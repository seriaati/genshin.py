"""App sub client for AuthClient.

Covers HoYoLAB and Miyoushe app auth endpoints.
"""

from __future__ import annotations

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
        mmt_result: typing.Union[SessionMMTResult, SessionMMTv4Result],
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
    ) -> typing.Union[AppLoginResult, SessionMMT, SessionMMTv4, ActionTicket]: ...

    async def _app_login(
        self,
        account: str,
        password: str,
        *,
        device_id: str,
        device_name: typing.Optional[str] = None,
        device_model: typing.Optional[str] = None,
        encrypted: bool = False,
        mmt_result: typing.Optional[typing.Union[SessionMMTResult, SessionMMTv4Result]] = None,
        ticket: typing.Optional[ActionTicket] = None,
    ) -> typing.Union[AppLoginResult, SessionMMT, SessionMMTv4, ActionTicket]:
        """Login with a password using HoYoLab app endpoint.

        Returns
        -------
        - Cookies if login is successful.
        - SessionMMT if GeeTest v3 captcha is triggered.
        - SessionMMTv4 if GeeTest v4 captcha is triggered.
        - ActionTicket if new-device email verification is required.
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

        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.APP_LOGIN_URL.get_url(),
                json=payload,
                headers=headers,
            ) as r:
                data = await r.json()

        print("_app_login headers", headers)
        print("_app_login payload", payload)
        print("_app_login", data)

        if data["retcode"] == -3101:
            # Captcha triggered, detect v3 vs v4 from the aigis data
            aigis = json.loads(r.headers["x-rpc-aigis"])
            inner_data = aigis.get("data", "{}")
            print("_app_login aigis", aigis)
            if isinstance(inner_data, str):
                inner_data = json.loads(inner_data)
            if inner_data.get("use_v4"):
                return SessionMMTv4(**aigis)
            return SessionMMT(**aigis)

        if data["retcode"] == -3239:
            # New device, email verification required
            action_ticket = json.loads(r.headers["x-rpc-verify"])
            print("_app_login action_ticket", action_ticket)
            return ActionTicket(**action_ticket)

        if not data["data"]:
            errors.raise_for_retcode(data)

        cookies = {
            "stoken": data["data"]["token"]["token"],
            "ltuid_v2": data["data"]["user_info"]["aid"],
            "ltmid_v2": data["data"]["user_info"]["mid"],
            "account_id_v2": data["data"]["user_info"]["aid"],
            "account_mid_v2": data["data"]["user_info"]["mid"],
        }
        self.set_cookies(cookies)

        return AppLoginResult(**cookies)

    async def _send_verification_email(
        self,
        ticket: ActionTicket,
        *,
        mmt_result: typing.Optional[typing.Union[SessionMMTResult, SessionMMTv4Result]] = None,
    ) -> typing.Union[None, SessionMMT, SessionMMTv4]:
        """Send verification email.

        Returns None if success, SessionMMT or SessionMMTv4 data if geetest triggered.
        """
        headers = {**auth_utility.EMAIL_SEND_HEADERS}
        if mmt_result:
            headers["x-rpc-aigis"] = mmt_result.to_aigis_header()

        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.SEND_VERIFICATION_CODE_URL.get_url(),
                json={
                    "action_type": "verify_for_component",
                    "action_ticket": ticket.verify_str.ticket,
                },
                headers=headers,
            ) as r:
                data = await r.json()

        print("_send_verification_email headers", headers)
        print(
            "_send_verification_email payload",
            {"action_type": "verify_for_component", "action_ticket": ticket.verify_str.ticket},
        )
        print("_send_verification_email", data)

        if data["retcode"] == -3101:
            # Captcha triggered
            aigis = json.loads(r.headers["x-rpc-aigis"])
            inner_data = aigis.get("data", "{}")
            print("_send_verification_email aigis", aigis)
            if isinstance(inner_data, str):
                inner_data = json.loads(inner_data)
            if inner_data.get("use_v4"):
                return SessionMMTv4(**aigis)
            return SessionMMT(**aigis)

        if data["retcode"] != 0:
            errors.raise_for_retcode(data)

        return None

    async def _verify_email(self, code: str, ticket: ActionTicket) -> None:
        """Verify email."""
        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.VERIFY_EMAIL_URL.get_url(),
                json={
                    "action_type": "verify_for_component",
                    "action_ticket": ticket.verify_str.ticket,
                    "email_captcha": code,
                    "verify_method": 2,
                },
                headers=auth_utility.EMAIL_VERIFY_HEADERS,
            ) as r:
                data = await r.json()

        print("_verify_email headers", auth_utility.EMAIL_VERIFY_HEADERS)
        print(
            "_verify_email payload",
            {
                "action_type": "verify_for_component",
                "action_ticket": ticket.verify_str.ticket,
                "email_captcha": code,
                "verify_method": 2,
            },
        )
        print("_verify_email", data)

        if data["retcode"] != 0:
            errors.raise_for_retcode(data)

        return None

    async def _create_qrcode(self) -> QRCodeCreationResult:
        """Create a QR code for login."""
        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.CREATE_QRCODE_URL.get_url(),
                headers=auth_utility.QRCODE_HEADERS,
            ) as r:
                data = await r.json()

        if not data["data"]:
            errors.raise_for_retcode(data)

        return QRCodeCreationResult(
            ticket=data["data"]["ticket"],
            url=data["data"]["url"],
        )

    async def _check_qrcode(self, ticket: str) -> tuple[QRCodeStatus, SimpleCookie]:
        """Check the status of a QR code login."""
        payload = {"ticket": ticket}

        async with self.cookie_manager.create_session() as session:
            async with session.post(
                routes.CHECK_QRCODE_URL.get_url(),
                json=payload,
                headers=auth_utility.QRCODE_HEADERS,
            ) as r:
                data = await r.json()

                if not data["data"]:
                    errors.raise_for_retcode(data)

                return QRCodeStatus(data["data"]["status"]), r.cookies
