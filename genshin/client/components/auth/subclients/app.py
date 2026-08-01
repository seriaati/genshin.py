"""App sub client for AuthClient.

Covers HoYoLAB and Miyoushe app auth endpoints.
"""

import json
import random
import string
import typing
from http.cookies import SimpleCookie

from genshin import errors
from genshin.client import routes
from genshin.client.components import base
from genshin.models.auth.cookie import AppLoginResult
from genshin.models.auth.geetest import SessionMMT, SessionMMTResult, SessionMMTv4, SessionMMTv4Result
from genshin.models.auth.qrcode import QRCodeCreationResult, QRCodeStatus
from genshin.models.auth.verification import ActionTicket
from genshin.types import AppGeetestResult, AppGeetestSession
from genshin.utility import auth as auth_utility
from genshin.utility import ds as ds_utility

__all__ = ["AppAuthClient"]


class AppAuthClient(base.BaseClient):
    """App sub client for AuthClient."""

    @staticmethod
    def generate_app_device_id() -> str:
        """Generate a random device ID for app login."""
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=16))

    @typing.overload
    async def _app_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        device_name: typing.Optional[str] = ...,
        device_model: typing.Optional[str] = ...,
        encrypted: bool = ...,
        mmt_result: SessionMMTResult,
        ticket: None = ...,
    ) -> typing.Union[AppLoginResult, ActionTicket]: ...

    @typing.overload
    async def _app_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        device_name: typing.Optional[str] = ...,
        device_model: typing.Optional[str] = ...,
        encrypted: bool = ...,
        mmt_result: SessionMMTv4Result,
        ticket: None = ...,
    ) -> typing.Union[AppLoginResult, ActionTicket]: ...

    @typing.overload
    async def _app_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        device_name: typing.Optional[str] = ...,
        device_model: typing.Optional[str] = ...,
        encrypted: bool = ...,
        mmt_result: None = ...,
        ticket: ActionTicket,
    ) -> AppLoginResult: ...

    @typing.overload
    async def _app_login(  # noqa: D102 missing docstring in overload?
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        device_name: typing.Optional[str] = ...,
        device_model: typing.Optional[str] = ...,
        encrypted: bool = ...,
        mmt_result: None = ...,
        ticket: None = ...,
    ) -> typing.Union[AppLoginResult, SessionMMT, ActionTicket]: ...

    async def _app_login(
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        device_name: typing.Optional[str] = None,
        device_model: typing.Optional[str] = None,
        encrypted: bool = False,
        mmt_result: typing.Optional[AppGeetestResult] = None,
        ticket: typing.Optional[ActionTicket] = None,
    ) -> typing.Union[AppLoginResult, AppGeetestSession, ActionTicket]:
        """Login with a password using HoYoLab app endpoint.

        Returns
        -------
        - AppLoginResult if login is successful.
        - AppGeetestSession if captcha is triggered.
        - ActionTicket if email verification is required.
        """
        headers = {
            **auth_utility.APP_LOGIN_HEADERS,
            # Passing "x-rpc-device_id" header will trigger email verification
            # (unless the device_id is already verified).
            # For some reason, without this header, email verification is not triggered.
            #
            # 2025/07/18: Hoyo found this issue and fixed it, we now have to provide this header.
            # This value needs to be consistent across all requests, else it will trigger email
            # verification repeatedly.
            "x-rpc-device_id": device_id,
        }
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        if ticket:
            headers["x-rpc-verify"] = ticket.to_rpc_verify_header()

        if device_name:
            headers["x-rpc-device_name"] = device_name
        if device_model:
            headers["x-rpc-device_model"] = device_model

        payload = {
            "account": account if encrypted else auth_utility.encrypt_credentials(account, 1),
            "password": password if encrypted else auth_utility.encrypt_credentials(password, 1),
        }

        headers["ds"] = ds_utility.generate_app_login_ds(payload)

        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.APP_LOGIN_URL.get_url(),
            json=payload,
            headers=headers,
        )

        if resp.data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(resp.headers["x-rpc-aigis"])

            if isinstance(aigis["data"], str):
                aigis["data"] = json.loads(aigis["data"])

            if aigis["data"].get("use_v4"):
                return SessionMMTv4(
                    **aigis["data"],
                    session_id=aigis["session_id"],
                )

            return SessionMMT(**aigis)

        if resp.data["retcode"] == -3239:
            # Email verification required
            action_ticket = json.loads(resp.headers["x-rpc-verify"])
            return ActionTicket(**action_ticket)

        if not resp.data["data"]:
            errors.raise_for_retcode(resp.data)

        cookies = {
            "stoken": resp.data["data"]["token"]["token"],
            "ltuid_v2": resp.data["data"]["user_info"]["aid"],
            "ltmid_v2": resp.data["data"]["user_info"]["mid"],
            "account_id_v2": resp.data["data"]["user_info"]["aid"],
            "account_mid_v2": resp.data["data"]["user_info"]["mid"],
        }
        self.set_cookies(cookies)

        return AppLoginResult(**cookies)

    async def _send_verification_email(
        self,
        ticket: ActionTicket,
        *,
        mmt_result: typing.Optional[SessionMMTResult] = None,
    ) -> typing.Union[None, SessionMMT]:
        """Send verification email.

        Returns None if success, SessionMMT data if geetest triggered.
        """
        headers = {**auth_utility.EMAIL_SEND_HEADERS}
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.SEND_VERIFICATION_CODE_URL.get_url(),
            json={
                "action_type": "verify_for_component",
                "action_ticket": ticket.verify_str.ticket,
            },
            headers=headers,
        )

        if resp.data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(resp.headers["x-rpc-aigis"])
            return SessionMMT(**aigis)

        if resp.data["retcode"] != 0:
            errors.raise_for_retcode(resp.data)

        return None

    async def _verify_email(self, code: str, ticket: ActionTicket) -> None:
        """Verify email."""
        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.VERIFY_EMAIL_URL.get_url(),
            json={
                "action_type": "verify_for_component",
                "action_ticket": ticket.verify_str.ticket,
                "email_captcha": code,
                "verify_method": 2,
            },
            headers=auth_utility.EMAIL_VERIFY_HEADERS,
        )

        if resp.data["retcode"] != 0:
            errors.raise_for_retcode(resp.data)

        return None

    async def _create_qrcode(self) -> QRCodeCreationResult:
        """Create a QR code for login."""
        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.CREATE_QRCODE_URL.get_url(),
            headers=auth_utility.QRCODE_HEADERS,
        )

        if not resp.data["data"]:
            errors.raise_for_retcode(resp.data)

        return QRCodeCreationResult(
            ticket=resp.data["data"]["ticket"],
            url=resp.data["data"]["url"],
        )

    async def _check_qrcode(self, ticket: str) -> tuple[QRCodeStatus, SimpleCookie]:
        """Check the status of a QR code login."""
        payload = {"ticket": ticket}

        resp = await self.cookie_manager._raw_request(
            "POST",
            routes.CHECK_QRCODE_URL.get_url(),
            json=payload,
            headers=auth_utility.QRCODE_HEADERS,
        )

        if not resp.data["data"]:
            errors.raise_for_retcode(resp.data)

        return QRCodeStatus(resp.data["data"]["status"]), resp.cookies
