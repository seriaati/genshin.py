"""HoYoLAB badge login component."""

import asyncio
import contextlib
import typing

import aiohttp.typedefs

from genshin import errors, types, utility
from genshin.client import routes
from genshin.client.components import base
from genshin.utility import ds

__all__ = ("BadgeLoginClient",)

BADGE_TOKEN_COOKIES: typing.Mapping[types.Game, str] = {
    types.Game.ZZZ: "e_nap_token",
    types.Game.STARRAIL: "e_hkrpg_token",
}
"""Name of the cookie set by the badge login for each game."""


class BadgeLoginClient(base.BaseClient):
    """Component for HoYoLAB event tools that authenticate through the badge login.

    Tools such as the ZZZ agent upgrade guide and the HSR warp records require a
    game-scoped ``e_<game>_token`` cookie minted by the badge login endpoint.
    """

    _badge_login_lock: typing.Optional[asyncio.Lock] = None
    """Serializes badge token refreshes so concurrent recoveries don't race."""
    _badge_login_loop: typing.Optional[asyncio.AbstractEventLoop] = None
    """The event loop the login lock is bound to; the lock is recreated when it changes."""
    _device_id_suppressions: int = 0
    """Refcount of in-flight requests that have stripped ``x-rpc-device_id``."""
    _suppressed_device_id: typing.Optional[str] = None
    """The ``x-rpc-device_id`` removed while suppressed, restored once the refcount hits zero."""

    def _badge_headers(
        self,
        region: types.Region,
        *,
        lang: str,
        data: typing.Any = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    ) -> typing.Dict[str, str]:
        """Build headers for a badge-authenticated request (DS is only required for China)."""
        headers = {"x-rpc-lang": lang, "x-rpc-language": lang}
        if region is types.Region.CHINESE:
            headers.update(ds.get_ds_headers(region=region, data=data, params=params, lang=lang))
        return headers

    @contextlib.contextmanager
    def _suppress_device_id(self) -> typing.Generator[None, None, None]:
        """Temporarily remove the ``x-rpc-device_id`` header for the duration of the block.

        The badge login rejects tokens minted with an ``x-rpc-device_id`` header, and some
        tools (the ZZZ cultivate tool) reject data requests carrying it with a ``-100`` error,
        so it must be omitted even when the client was constructed with a device id. The
        removal is refcounted so that concurrent requests only restore the header once the
        last of them has finished. ``__enter__`` and ``__exit__`` run without awaiting, so
        the refcount stays consistent under asyncio concurrency.
        """
        if self._device_id_suppressions == 0:
            self._suppressed_device_id = self.custom_headers.pop("x-rpc-device_id", None)
        self._device_id_suppressions += 1
        try:
            yield
        finally:
            self._device_id_suppressions -= 1
            if self._device_id_suppressions == 0 and self._suppressed_device_id is not None:
                self.custom_headers["x-rpc-device_id"] = self._suppressed_device_id
                self._suppressed_device_id = None

    async def _badge_login(
        self,
        game: types.Game,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
        stale_token: typing.Optional[str] = None,
    ) -> None:
        """Obtain the badge token cookie for a game.

        The response sets a fresh token cookie which the cookie manager merges into the
        session automatically. Concurrent callers are serialized by a lock; if
        ``stale_token`` is given and another caller already refreshed the token while we
        waited, the login is skipped.
        """
        # Bind the lock to the running loop, recreating it if the loop changed. A single
        # Client may be reused across event loops (e.g. successive asyncio.run calls), and
        # an asyncio.Lock cannot be awaited from a loop other than the one that created it.
        loop = asyncio.get_running_loop()
        lock = self._badge_login_lock
        if lock is None or self._badge_login_loop is not loop:
            lock = self._badge_login_lock = asyncio.Lock()
            self._badge_login_loop = loop

        async with lock:
            # Drop stale session cookies so the fresh ones from the response are stored. The
            # cookie manager only merges cookie keys it doesn't already have, so the token,
            # its paired risk-control token (e_lrsag), and the load-balancer affinity cookies
            # must all be cleared to be refreshed together — a stale SERVERID otherwise routes
            # the new token to the wrong backend.
            cookies = getattr(self.cookie_manager, "cookies", None)
            if isinstance(cookies, dict):
                # Re-check under the lock: another coroutine may have logged in while we
                # waited. On the missing-token path (stale_token is None) any token will do;
                # on the retry path, skip only once the rejected token has been replaced.
                current_token = typing.cast("typing.Optional[str]", cookies.get(BADGE_TOKEN_COOKIES[game]))
                if current_token and current_token != stale_token:
                    return
                for key in (BADGE_TOKEN_COOKIES[game], "e_lrsag", "SERVERID", "SERVERCORSID"):
                    cookies.pop(key, None)

            await self._do_badge_login(game, uid, lang=lang)

    async def _do_badge_login(self, game: types.Game, uid: int, *, lang: typing.Optional[str] = None) -> None:
        """Perform the badge login request (must be called while holding the login lock).

        The badge login authenticates with the cookie token, which is invalidated whenever
        a newer one is minted for the account elsewhere while the other cookies stay valid.
        When the login is rejected and an stoken is available, a fresh cookie token is
        minted from it and the login is retried once.
        """
        lang = lang or self.lang
        region = utility.recognize_region(uid, game=game) or types.Region.OVERSEAS
        body = {
            "game_biz": utility.get_prod_game_biz(region, game),
            "lang": lang,
            "region": utility.recognize_server(uid, game),
            "uid": str(uid),
        }
        url = routes.BADGE_LOGIN_URL.get_url(region)
        headers = self._badge_headers(region, lang=lang, data=body)
        stale_tokens = self._get_cookie_tokens()
        with self._suppress_device_id():
            try:
                await self.request(url, method="POST", data=body, headers=headers)
            except errors.InvalidCookies:
                if not await self._refresh_cookie_token(stale_tokens, region=region):
                    raise

                await self.request(url, method="POST", data=body, headers=headers)

    async def _request_with_badge(
        self,
        game: types.Game,
        url: aiohttp.typedefs.StrOrURL,
        uid: int,
        *,
        lang: typing.Optional[str] = None,
        method: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        data: typing.Any = None,
        suppress_device_id: bool = False,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request authenticated by a badge token.

        The token cookie stays valid for a long time (~48 hours), so it is reused across
        requests. A fresh login is only performed when the token is missing, or when the
        server rejects it with an ``InvalidCookies`` (-100) error, after which the request
        is retried once. ``suppress_device_id`` strips the ``x-rpc-device_id`` header for
        tools that reject it.
        """
        cookies = getattr(self.cookie_manager, "cookies", None)
        if not (isinstance(cookies, dict) and cookies.get(BADGE_TOKEN_COOKIES[game])):
            await self._badge_login(game, uid, lang=lang)

        lang = lang or self.lang
        region = utility.recognize_region(uid, game=game) or types.Region.OVERSEAS
        headers = self._badge_headers(region, lang=lang, data=data, params=params)
        suppress = self._suppress_device_id if suppress_device_id else contextlib.nullcontext

        try:
            with suppress():
                return await self.request(url, method=method, params=params, data=data, headers=headers)
        except errors.InvalidCookies:
            stale_token = (
                typing.cast("typing.Optional[str]", cookies.get(BADGE_TOKEN_COOKIES[game]))
                if isinstance(cookies, dict)
                else None
            )
            await self._badge_login(game, uid, lang=lang, stale_token=stale_token)
            with suppress():
                return await self.request(url, method=method, params=params, data=data, headers=headers)
