"""Web sub client for AuthClient.

Covers HoYoLAB and Miyoushe web auth endpoints.
"""

import json
import typing
import uuid

from genshin import constants, errors, types
from genshin.client import routes
from genshin.client.components import base
from genshin.models.auth.cookie import CNWebLoginResult, MobileLoginResult, WebLoginResult
from genshin.models.auth.geetest import SessionMMT, SessionMMTResult, SessionMMTv4
from genshin.utility import auth as auth_utility
from genshin.utility import ds as ds_utility

__all__ = ["WebAuthClient"]


class WebAuthClient(base.BaseClient):
    """Web sub client for AuthClient."""

    @staticmethod
    def generate_web_device_id() -> str:
        """Generate a random device ID for web login."""
        return str(uuid.uuid4())

    @typing.overload
    async def _os_web_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        encrypted: bool = ...,
        token_type: typing.Optional[int] = ...,
        mmt_result: SessionMMTResult,
    ) -> WebLoginResult: ...

    @typing.overload
    async def _os_web_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        encrypted: bool = ...,
        token_type: typing.Optional[int] = ...,
        mmt_result: None = ...,
    ) -> typing.Union[SessionMMT, WebLoginResult]: ...

    @base.region_specific(types.Region.OVERSEAS)
    async def _os_web_login(
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        encrypted: bool = False,
        token_type: typing.Optional[int] = 6,
        mmt_result: typing.Optional[SessionMMTResult] = None,
    ) -> typing.Union[SessionMMT, WebLoginResult]:
        """Login with a password using web endpoint.

        Returns either data from aigis header or cookies.
        """
        headers = {**auth_utility.WEB_LOGIN_HEADERS}
        # If not provided, [-3104] is returned, see #272
        headers["x-rpc-device_id"] = device_id

        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        payload = {
            "account": account if encrypted else auth_utility.encrypt_credentials(account, 1),
            "password": password if encrypted else auth_utility.encrypt_credentials(password, 1),
            "token_type": token_type,
        }

        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.WEB_LOGIN_URL.get_url(),
            json=payload,
            headers=headers,
        )
        cookies = {cookie.key: cookie.value for cookie in resp.cookies.values()}

        if resp.data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(resp.headers["x-rpc-aigis"])
            return SessionMMT(**aigis)

        if not resp.data["data"]:
            errors.raise_for_retcode(resp.data)

        if resp.data["data"].get("stoken"):
            cookies["stoken"] = resp.data["data"]["stoken"]

        self.set_cookies(cookies)
        return WebLoginResult(**cookies)

    @typing.overload
    async def _cn_web_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = ...,
        mmt_result: SessionMMTResult,
    ) -> CNWebLoginResult: ...

    @typing.overload
    async def _cn_web_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = ...,
        mmt_result: None = ...,
    ) -> typing.Union[SessionMMT, CNWebLoginResult]: ...

    @base.region_specific(types.Region.CHINESE)
    async def _cn_web_login(
        self,
        account: str,
        password: str,
        *,
        encrypted: bool = False,
        mmt_result: typing.Optional[SessionMMTResult] = None,
    ) -> typing.Union[SessionMMT, CNWebLoginResult]:
        """
        Login with account and password using Miyoushe loginByPassword endpoint.

        Returns data from aigis header or cookies.
        """
        headers = {
            **auth_utility.CN_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["cn_signin"]),
        }
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        payload = {
            "account": account if encrypted else auth_utility.encrypt_credentials(account, 2),
            "password": password if encrypted else auth_utility.encrypt_credentials(password, 2),
        }

        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.CN_WEB_LOGIN_URL.get_url(),
            json=payload,
            headers=headers,
        )

        if resp.data["retcode"] == -3102:
            # Captcha triggered
            aigis = json.loads(resp.headers["x-rpc-aigis"])
            return SessionMMT(**aigis)

        if not resp.data["data"]:
            errors.raise_for_retcode(resp.data)

        cookies = {cookie.key: cookie.value for cookie in resp.cookies.values()}
        self.set_cookies(cookies)

        return CNWebLoginResult(**cookies)

    async def _send_mobile_otp(
        self,
        mobile: str,
        *,
        encrypted: bool = False,
        mmt_result: typing.Optional[SessionMMTResult] = None,
    ) -> typing.Union[None, SessionMMTv4]:
        """Attempt to send OTP to the provided mobile number.

        May return aigis headers if captcha is triggered, None otherwise.
        """
        headers = {
            **auth_utility.CN_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["cn_signin"]),
        }
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        payload = {
            "mobile": mobile if encrypted else auth_utility.encrypt_credentials(mobile, 2),
            "area_code": auth_utility.encrypt_credentials("+86", 2),
        }

        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.MOBILE_OTP_URL.get_url(),
            json=payload,
            headers=headers,
        )

        if resp.data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(resp.headers["x-rpc-aigis"])
            return SessionMMTv4(**aigis)

        if not resp.data["data"]:
            errors.raise_for_retcode(resp.data)

        return None

    async def _login_with_mobile_otp(self, mobile: str, otp: str, *, encrypted: bool = False) -> MobileLoginResult:
        """Login with OTP and mobile number.

        Returns cookies if OTP matches the one sent, raises an error otherwise.
        """
        headers = {
            **auth_utility.CN_LOGIN_HEADERS,
            "ds": ds_utility.generate_dynamic_secret(constants.DS_SALT["cn_signin"]),
        }

        payload = {
            "mobile": mobile if encrypted else auth_utility.encrypt_credentials(mobile, 2),
            "area_code": auth_utility.encrypt_credentials("+86", 2),
            "captcha": otp,
        }

        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.MOBILE_LOGIN_URL.get_url(),
            json=payload,
            headers=headers,
        )

        if not resp.data["data"]:
            errors.raise_for_retcode(resp.data)

        cookies = {cookie.key: cookie.value for cookie in resp.cookies.values()}
        self.set_cookies(cookies)

        return MobileLoginResult(**cookies)
