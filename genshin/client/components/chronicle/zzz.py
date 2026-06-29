"""StarRail battle chronicle component."""

import asyncio
import functools
import typing

from genshin import errors, paginators, types, utility
from genshin.client import routes
from genshin.models import zzz as models
from genshin.models.genshin import gacha as gacha_models
from genshin.utility import ds

from . import base

__all__ = ("ZZZBattleChronicleClient",)


class ZZZBattleChronicleClient(base.BaseBattleChronicleClient):
    """ZZZ battle chronicle component."""

    async def _request_zzz_record(
        self,
        endpoint: str,
        uid: typing.Optional[int] = None,
        *,
        method: str = "GET",
        lang: typing.Optional[str] = None,
        payload: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        cache: bool = False,
        is_nap_ledger: bool = False,
        use_uid_in_payload: bool = False,
    ) -> typing.Mapping[str, typing.Any]:
        """Get an arbitrary ZZZ object."""
        payload = dict(payload or {})
        original_payload = payload.copy()

        uid = uid or await self._get_uid(types.Game.ZZZ)

        if is_nap_ledger or use_uid_in_payload:
            payload = {
                "uid": uid,
                "region": utility.recognize_zzz_server(uid),
                **payload,
            }
        else:
            payload = {
                "role_id": uid,
                "server": utility.recognize_zzz_server(uid),
                **payload,
            }

        data, params = None, None
        if method == "POST":
            data = payload
        else:
            params = payload

        cache_key: typing.Optional[base.ChronicleCacheKey] = None
        if cache:
            cache_key = base.ChronicleCacheKey(
                types.Game.ZZZ,
                endpoint,
                uid,
                lang=lang or self.lang,
                params=tuple(original_payload.values()),
            )

        return await self.request_game_record(
            endpoint,
            lang=lang,
            game=types.Game.ZZZ,
            region=utility.recognize_region(uid, game=types.Game.ZZZ),
            params=params,
            data=data,
            cache=cache_key,
            custom_route=routes.NAP_LEDGER_URL if is_nap_ledger else None,
        )

    @typing.overload
    async def get_zzz_notes(
        self,
        uid: typing.Optional[int] = ...,
        *,
        lang: typing.Optional[str] = ...,
        autoauth: bool = ...,
        return_raw_data: typing.Literal[False] = ...,
    ) -> models.ZZZNotes: ...
    @typing.overload
    async def get_zzz_notes(
        self,
        uid: typing.Optional[int] = ...,
        *,
        lang: typing.Optional[str] = ...,
        autoauth: bool = ...,
        return_raw_data: typing.Literal[True] = ...,
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_zzz_notes(
        self,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
        autoauth: bool = True,
        return_raw_data: bool = False,
    ) -> typing.Union[models.ZZZNotes, typing.Mapping[str, typing.Any]]:
        """Get ZZZ sticky notes (real-time notes)."""
        try:
            data = await self._request_zzz_record("note", uid, lang=lang)
        except errors.DataNotPublic as e:
            # error raised only when real-time notes are not enabled
            if uid and (await self._get_uid(types.Game.ZZZ)) != uid:
                raise errors.GenshinException(e.response, "Cannot view real-time notes of other users.") from e
            if not autoauth:
                raise errors.GenshinException(e.response, "Real-time notes are not enabled.") from e

            await self.update_settings(3, True, game=types.Game.ZZZ)
            data = await self._request_zzz_record("note", uid, lang=lang)

        if return_raw_data:
            return data
        return models.ZZZNotes(**data)

    async def get_zzz_diary(
        self,
        uid: typing.Optional[int] = None,
        *,
        month: typing.Optional[str] = None,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZDiary:
        """Get ZZZ inter-knot monthly earning data."""
        data = await self._request_zzz_record(
            "month_info", uid, lang=lang, payload={"month": month or ""}, is_nap_ledger=True
        )
        return models.ZZZDiary(**data)

    async def get_zzz_diary_detail(
        self,
        month: str,
        *,
        type: models.ZZZCurrencyType,
        page: int = 1,
        page_size: int = 20,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZDiaryDetail:
        """Get ZZZ inter-knot monthly earning data."""
        if not month:
            raise ValueError("month is required.")

        data = await self._request_zzz_record(
            "month_detail",
            uid,
            lang=lang,
            payload={"month": month, "current_page": page, "type": type.value, "page_size": page_size},
            is_nap_ledger=True,
        )
        return models.ZZZDiaryDetail(**data)

    async def get_zzz_user(
        self,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZUserStats:
        """Get ZZZ user stats."""
        data = await self._request_zzz_record("index", uid, lang=lang)
        return models.ZZZUserStats(**data)

    async def get_zzz_agents(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> typing.Sequence[models.ZZZPartialAgent]:
        """Get all owned ZZZ characters (only brief info)."""
        data = await self._request_zzz_record("avatar/basic", uid, lang=lang)
        return [models.ZZZPartialAgent(**item) for item in data["avatar_list"]]

    async def get_bangboos(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> typing.Sequence[models.ZZZBaseBangboo]:
        """Get all owned ZZZ bangboos."""
        data = await self._request_zzz_record("buddy/info", uid, lang=lang)
        return [models.ZZZBaseBangboo(**item) for item in data["list"]]

    @typing.overload
    async def get_zzz_agent_info(
        self,
        character_id: int,
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> models.ZZZFullAgent: ...
    @typing.overload
    async def get_zzz_agent_info(
        self,
        character_id: typing.Sequence[int],
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.ZZZFullAgent]: ...
    async def get_zzz_agent_info(
        self,
        character_id: typing.Union[int, typing.Sequence[int]],
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Union[models.ZZZFullAgent, typing.Sequence[models.ZZZFullAgent]]:
        """Get a ZZZ character's detailed info."""
        if isinstance(character_id, typing.Sequence):
            tasks = [
                self._request_zzz_record("avatar/info", uid, lang=lang, payload={"id_list[]": character_id_})
                for character_id_ in character_id
            ]
            results = await asyncio.gather(*tasks)
            return [models.ZZZFullAgent(**data["avatar_list"][0]) for data in results]

        data = await self._request_zzz_record("avatar/info", uid, lang=lang, payload={"id_list[]": character_id})
        return models.ZZZFullAgent(**data["avatar_list"][0])

    def _upgrade_guide_headers(
        self,
        region: types.Region,
        *,
        lang: str,
        data: typing.Any = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    ) -> typing.Dict[str, str]:
        """Build headers for an upgrade guide request (DS is only required for China)."""
        headers = {"x-rpc-lang": lang, "x-rpc-language": lang}
        if region is types.Region.CHINESE:
            headers.update(ds.get_ds_headers(region=region, data=data, params=params, lang=lang))
        return headers

    async def _login_upgrade_guide(self, uid: int, *, lang: typing.Optional[str] = None) -> None:
        """Obtain the ``e_nap_token`` cookie required by the ZZZ agent upgrade guide.

        The response sets a fresh ``e_nap_token`` cookie which the cookie manager
        merges into the session automatically.
        """
        # Drop stale session cookies so the fresh ones from the response are stored. The
        # cookie manager only merges cookie keys it doesn't already have, so the token
        # (e_nap_token), its paired risk-control token (e_lrsag), and the load-balancer
        # affinity cookies must all be cleared to be refreshed together — a stale
        # SERVERID otherwise routes the new token to the wrong backend.
        cookies = getattr(self.cookie_manager, "cookies", None)
        if isinstance(cookies, dict):
            for key in ("e_nap_token", "e_lrsag", "SERVERID", "SERVERCORSID"):
                cookies.pop(key, None)

        lang = lang or self.lang
        region = utility.recognize_region(uid, game=types.Game.ZZZ) or types.Region.OVERSEAS
        body = {
            "game_biz": "nap_cn" if region is types.Region.CHINESE else "nap_global",
            "lang": lang,
            "region": utility.recognize_zzz_server(uid),
            "uid": str(uid),
        }
        await self.request(
            routes.NAP_BADGE_LOGIN_URL.get_url(region),
            method="POST",
            data=body,
            headers=self._upgrade_guide_headers(region, lang=lang, data=body),
        )

    async def _request_upgrade_guide(
        self,
        endpoint: str,
        uid: typing.Optional[int] = None,
        *,
        lang: typing.Optional[str] = None,
        body: typing.Optional[typing.Mapping[str, typing.Any]] = None,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the ZZZ agent upgrade guide tool."""
        uid = uid or await self._get_uid(types.Game.ZZZ)
        await self._login_upgrade_guide(uid, lang=lang)

        lang = lang or self.lang
        region = utility.recognize_region(uid, game=types.Game.ZZZ) or types.Region.OVERSEAS
        params = {"uid": uid, "region": utility.recognize_zzz_server(uid)}
        return await self.request(
            routes.NAP_CULTIVATE_URL.get_url(region) / endpoint,
            method="POST" if body is not None else "GET",
            params=params,
            data=body,
            headers=self._upgrade_guide_headers(region, lang=lang, data=body, params=params),
        )

    async def get_zzz_upgrade_guide_agents(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> typing.Sequence[models.ZZZUpgradeGuideAgent]:
        """Get all agents available in the ZZZ agent upgrade guide tool."""
        data = await self._request_upgrade_guide("user/avatar_basic_list", uid, lang=lang)
        return [models.ZZZUpgradeGuideAgent(**item) for item in data["list"]]

    async def get_zzz_agent_upgrade_guide(
        self,
        character_id: typing.Union[int, typing.Sequence[int]],
        *,
        uid: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[models.ZZZAgentUpgradeGuide]:
        """Get detailed builds and recommended upgrade guides for ZZZ agents."""
        if isinstance(character_id, int):
            character_id = [character_id]

        avatar_list = [
            {"avatar_id": id_, "is_teaser": False, "teaser_need_weapon": False, "teaser_sp_skill": False}
            for id_ in character_id
        ]
        data = await self._request_upgrade_guide(
            "user/batch_avatar_detail_v2", uid, lang=lang, body={"avatar_list": avatar_list}
        )
        return [models.ZZZAgentUpgradeGuide(**item) for item in data["list"]]

    @typing.overload
    async def get_shiyu_defense(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[False] = ...,
    ) -> typing.Union[models.ShiyuDefenseV1, models.ShiyuDefenseV2]: ...
    @typing.overload
    async def get_shiyu_defense(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[True] = ...,
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_shiyu_defense(
        self,
        uid: typing.Optional[int] = None,
        *,
        previous: bool = False,
        lang: typing.Optional[str] = None,
        raw: bool = False,
    ) -> typing.Union[models.ShiyuDefenseV1, models.ShiyuDefenseV2, typing.Mapping[str, typing.Any]]:
        """Get ZZZ Shiyu defense stats."""
        payload = {"schedule_type": 2 if previous else 1}
        data = await self._request_zzz_record("hadal_info_v2", uid, lang=lang, payload=payload)
        version = data["hadal_ver"]  # v1 or v2
        key = f"hadal_info_{version}"

        if version == "v1":
            data = data[key]
        elif version == "v2":
            nickname = data["nick_name"]
            icon = data["icon"]
            data = data[key]
            data["nick_name"] = nickname
            data["icon"] = icon
        else:
            msg = f"Unknown Shiyu Defense version: {version!r}"
            raise ValueError(msg)

        self._add_timezone_to_data(data, ("hadal_begin_time", "hadal_end_time"), game=types.Game.ZZZ, uid=uid)

        if raw:
            return data
        if version == "v2":
            return models.ShiyuDefenseV2(**data)
        return models.ShiyuDefenseV1(**data)

    @typing.overload
    async def get_deadly_assault(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[False] = ...,
    ) -> models.DeadlyAssault: ...
    @typing.overload
    async def get_deadly_assault(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[True] = ...,
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_deadly_assault(
        self,
        uid: typing.Optional[int] = None,
        *,
        previous: bool = False,
        lang: typing.Optional[str] = None,
        raw: bool = False,
    ) -> typing.Union[models.DeadlyAssault, typing.Mapping[str, typing.Any]]:
        """Get ZZZ Shiyu defense stats."""
        payload = {"schedule_type": 2 if previous else 1}
        data = await self._request_zzz_record("mem_detail", uid, lang=lang, payload=payload, use_uid_in_payload=True)

        self._add_timezone_to_data(data, ("hadal_begin_time", "hadal_end_time"), game=types.Game.ZZZ, uid=uid)

        if raw:
            return data
        return models.DeadlyAssault(**data)

    @typing.overload
    async def get_annihilation_simulacrum(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[False] = ...,
    ) -> models.AnnihilationSimulacrum: ...
    @typing.overload
    async def get_annihilation_simulacrum(
        self,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[True] = ...,
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_annihilation_simulacrum(
        self,
        uid: typing.Optional[int] = None,
        *,
        previous: bool = False,
        lang: typing.Optional[str] = None,
        raw: bool = False,
    ) -> typing.Union[models.AnnihilationSimulacrum, typing.Mapping[str, typing.Any]]:
        """Get ZZZ Annihilation Simulacrum stats."""
        payload = {"schedule_type": 2 if previous else 1}
        data = await self._request_zzz_record(
            "holo_boss_detail", uid, lang=lang, payload=payload, use_uid_in_payload=True
        )

        data = self._add_timezone_to_data(data, ("start_time", "end_time"), game=types.Game.ZZZ, uid=uid)

        if raw:
            return data
        return models.AnnihilationSimulacrum(**data)

    async def get_lost_void_summary(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> models.LostVoidSummary:
        """Get ZZZ Lost Void summary."""
        data = await self._request_zzz_record("abysss2_abstract", uid, lang=lang, use_uid_in_payload=True)
        return models.LostVoidSummary(**data)

    async def get_threshold_simulation_brief(
        self, uid: typing.Optional[int] = None, *, previous: bool = False, lang: typing.Optional[str] = None
    ) -> models.ThresholdSimulationInfo:
        """Get ZZZ Threshold Simulation brief info."""
        schedule_type = 2 if previous else 1
        payload = {"schedule_type": schedule_type}
        data = await self._request_zzz_record(
            "void_front_battle_period_abstract_info", uid, lang=lang, use_uid_in_payload=True, payload=payload
        )
        return models.ThresholdSimulationInfo(**data["void_front_battle_abstract_info_brief"])

    @typing.overload
    async def get_threshold_simulation(
        self,
        id: typing.Optional[int] = ...,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[False] = ...,
    ) -> models.ThresholdSimulation: ...
    @typing.overload
    async def get_threshold_simulation(
        self,
        id: typing.Optional[int] = ...,
        uid: typing.Optional[int] = ...,
        *,
        previous: bool = ...,
        lang: typing.Optional[str] = ...,
        raw: typing.Literal[True] = ...,
    ) -> typing.Mapping[str, typing.Any]: ...
    async def get_threshold_simulation(
        self,
        id: typing.Optional[int] = None,
        uid: typing.Optional[int] = None,
        *,
        previous: bool = False,
        lang: typing.Optional[str] = None,
        raw: bool = False,
    ) -> typing.Union[models.ThresholdSimulation, typing.Mapping[str, typing.Any]]:
        """Get ZZZ Threshold Simulation stats.

        If no ID is given, the latest run will be fetched.
        """
        schedule_type = 2 if previous else 1
        if id is None:
            brief = await self.get_threshold_simulation_brief(uid, lang=lang, previous=previous)
            id = brief.id

        data = await self._request_zzz_record(
            "void_front_battle_period_detail",
            uid,
            lang=lang,
            payload={"void_front_id": id, "schedule_type": schedule_type},
            use_uid_in_payload=True,
        )
        data = data["void_front_battle_detail"]
        if raw:
            return data
        return models.ThresholdSimulation(**data)

    async def _get_chronicle_signal_page(
        self,
        end_id: int,
        banner_type: gacha_models.ZZZBannerType,
        *,
        lang: typing.Optional[str] = None,
        uid: typing.Optional[int] = None,
    ) -> typing.Sequence[gacha_models.SignalSearch]:
        """Get a single page of battle chronicle signal searches."""
        uid = uid or await self._get_uid(types.Game.ZZZ)
        timezone = self.get_account_timezone(game=types.Game.ZZZ, uid=uid)
        if timezone is None:
            msg = "Cannot find account timezone."
            raise ValueError(msg)

        data = await self._request_zzz_record(
            "gacha_record",
            uid,
            lang=lang,
            payload={"gacha_type": banner_type.to_chronicle_type(), "end_id": end_id},
            use_uid_in_payload=True,
        )
        records = data.get("gacha_item_list", [])
        return [
            gacha_models.SignalSearch.from_chronicle_data(i, uid=uid, banner_type=banner_type, tz_offset=timezone - 8)
            for i in records
        ]

    def chronicle_signal_history(
        self,
        banner_type: typing.Optional[typing.Union[int, typing.Sequence[int]]] = None,
        *,
        limit: typing.Optional[int] = None,
        lang: typing.Optional[str] = None,
        uid: typing.Optional[int] = None,
        end_id: int = 0,
    ) -> paginators.Paginator[gacha_models.SignalSearch]:
        """Get the signal search history of a user."""
        banner_types = banner_type or list(gacha_models.ZZZBannerType)

        if not isinstance(banner_types, typing.Sequence):
            banner_types = [banner_types]

        iterators: list[paginators.Paginator[gacha_models.SignalSearch]] = []
        for banner in banner_types:
            iterators.append(
                paginators.CursorPaginator(
                    functools.partial(
                        self._get_chronicle_signal_page,
                        banner_type=gacha_models.ZZZBannerType(banner),
                        lang=lang,
                        uid=uid,
                    ),
                    limit=limit,
                    end_id=end_id,
                )
            )

        if len(iterators) == 1:
            return iterators[0]

        return paginators.MergedPaginator(iterators, key=lambda wish: wish.time.timestamp())

    async def get_zzz_event_calendar(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> typing.Sequence[models.ZZZEvent]:
        """Get ZZZ event calendar."""
        data = await self._request_zzz_record("activity_calendar", uid, lang=lang, use_uid_in_payload=True)
        return [models.ZZZEvent(**item) for item in data["activity_list"]]

    async def get_zzz_gacha_calendar(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> models.ZZZGachaCalendar:
        """Get ZZZ gacha calendar."""
        data = await self._request_zzz_record("gacha_calendar", uid, lang=lang, use_uid_in_payload=True)
        return models.ZZZGachaCalendar(**data)

    async def get_zzz_gacha_info(
        self, uid: typing.Optional[int] = None, *, lang: typing.Optional[str] = None
    ) -> models.ZZZGachaInfo:
        """Get ZZZ gacha info."""
        data = await self._request_zzz_record("cur_gacha_detail", uid, lang=lang, use_uid_in_payload=True)
        return models.ZZZGachaInfo(**data)
