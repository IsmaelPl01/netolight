"""This module provides the services."""

import asyncio
import base64
import csv
import dataclasses
import datetime
import enum
import io
import math
import struct
import zoneinfo
from collections.abc import Sequence
from typing import Annotated, Any, Self

import chirpstack_api.api  # type: ignore[import-untyped]
import dateutil.parser
import fastapi.security
import google.protobuf.json_format
import grpc  # type: ignore[import-untyped]
import jose.jwt
import passlib.context
import pytz
import rpyc  # type: ignore[import-untyped]
import sqlalchemy.exc

import api.config
import api.log
import api.repositories
import api.rs
import api.schemas


class _TenantService:
    """This class provides functions for managing tenants."""

    def __init__(
        self: Self, channel: grpc.Channel, token: list[tuple[str, str]]
    ) -> None:
        """Initialize channel and token properties."""
        self.channel = channel
        self.token = token

    def reads(self: Self, offset: int = 0, limit: int = 10) -> dict[str, Any]:
        """Read a sublist of tenants."""
        client = chirpstack_api.api.TenantServiceStub(self.channel)
        req = chirpstack_api.api.ListTenantsRequest()
        req.offset = offset
        req.limit = limit
        resp = client.List(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def read(self: Self, tenant_id: str) -> dict | None:
        """Read a tenants."""
        client = chirpstack_api.api.TenantServiceStub(self.channel)
        req = chirpstack_api.api.GetTenantRequest()
        req.id = tenant_id
        try:
            resp = client.Get(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)['tenant']
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def create(self: Self, name: str, description: str) -> dict:
        """Create a tenant."""
        client = chirpstack_api.api.TenantServiceStub(self.channel)
        req = chirpstack_api.api.CreateTenantRequest()
        req.tenant.name = name
        req.tenant.description = description
        req.tenant.can_have_gateways = True
        req.tenant.max_device_count = 0
        resp = client.Create(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)


class _ApplicationService:
    """This class provides functions for managing applications."""

    def __init__(
        self: Self, channel: grpc.Channel, token: list[tuple[str, str]]
    ) -> None:
        """Initialize channel and token properties."""
        self.channel = channel
        self.token = token

    def reads(self: Self, offset: int = 0, limit: int = 10) -> dict[str, Any]:
        """Read a sublist of applications."""
        client = chirpstack_api.api.ApplicationServiceStub(self.channel)
        req = chirpstack_api.api.ListApplicationsRequest()
        req.offset = offset
        req.limit = limit
        resp = client.List(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def read(self: Self, application_id: str) -> dict | None:
        """Read an application."""
        client = chirpstack_api.api.ApplicationServiceStub(self.channel)
        req = chirpstack_api.api.GetApplicationRequest()
        req.id = application_id
        try:
            resp = client.Get(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)[
                'application'
            ]
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def create(self: Self, tenant_id: str, name: str, description: str) -> dict:
        """Create an application."""
        client = chirpstack_api.api.ApplicationServiceStub(self.channel)
        req = chirpstack_api.api.CreateApplicationRequest()
        req.application.name = name
        req.application.description = description
        req.application.tenant_id = tenant_id
        resp = client.Create(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def get_http_integration(self: Self, app_id: str) -> dict | None:
        """Get a HTTP application."""
        client = chirpstack_api.api.ApplicationServiceStub(self.channel)
        req = chirpstack_api.api.GetHttpIntegrationRequest()
        req.application_id = app_id
        try:
            resp = client.GetHttpIntegration(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)[
                'integration'
            ]
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def create_http_integration(
        self: Self, app_id: str, encoding: int, event_endpoint_url: str
    ) -> dict:
        """Create a HTTP application."""
        client = chirpstack_api.api.ApplicationServiceStub(self.channel)
        req = chirpstack_api.api.CreateHttpIntegrationRequest()
        req.integration.application_id = app_id
        req.integration.encoding = encoding
        req.integration.event_endpoint_url = event_endpoint_url
        resp = client.CreateHttpIntegration(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)


class _GatewayService:
    """This class provides functions for managing gateways."""

    def __init__(
        self: Self, channel: grpc.Channel, token: list[tuple[str, str]]
    ) -> None:
        """Initialize channel and token properties."""
        self.channel = channel
        self.token = token

    def reads(self: Self, offset: int = 0, limit: int = 10) -> dict[str, Any]:
        """Read a sublist of gateways."""
        client = chirpstack_api.api.GatewayServiceStub(self.channel)
        req = chirpstack_api.api.ListGatewaysRequest()
        req.offset = offset
        req.limit = limit
        resp = client.List(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def read(self: Self, gateway_id: str) -> dict | None:
        """Read a gateway."""
        client = chirpstack_api.api.GatewayServiceStub(self.channel)
        req = chirpstack_api.api.GetGatewayRequest()
        req.gateway_id = gateway_id
        try:
            resp = client.Get(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def create(
        self: Self,
        tenant_id: str,
        gateway_id: str,
        name: str,
        description: str | None,
    ) -> dict:
        """Create a gateway."""
        client = chirpstack_api.api.GatewayServiceStub(self.channel)
        req = chirpstack_api.api.CreateGatewayRequest()
        req.gateway.gateway_id = gateway_id
        req.gateway.name = name
        if description is not None:
            req.gateway.description = description
        req.gateway.tenant_id = tenant_id
        req.gateway.stats_interval = 3600
        resp = client.Create(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def update(
        self: Self, tenant_id: str, gateway_id: str, name: str, description: str
    ) -> dict:
        """Create a gateway."""
        client = chirpstack_api.api.GatewayServiceStub(self.channel)
        req = chirpstack_api.api.UpdateGatewayRequest()
        req.gateway.gateway_id = gateway_id
        req.gateway.name = name
        req.gateway.description = description
        req.gateway.tenant_id = tenant_id
        resp = client.Create(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def delete(self: Self, gateway_id: str) -> dict:
        """Delete a gateway."""
        client = chirpstack_api.api.GatewayServiceStub(self.channel)
        req = chirpstack_api.api.DeleteGatewayRequest()
        req.gateway_id = gateway_id
        resp = client.Delete(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)


class _DeviceService:
    """This class provides functions for managing devices."""

    def __init__(
        self: Self, channel: grpc.Channel, token: list[tuple[str, str]]
    ) -> None:
        """Initialize channel and token properties."""
        self.channel = channel
        self.token = token

    def reads(
        self: Self, app_id: str, offset: int = 0, limit: int = 10
    ) -> dict[str, Any]:
        """Read a sublist of devices."""
        client = chirpstack_api.api.DeviceServiceStub(self.channel)
        req = chirpstack_api.api.ListDevicesRequest()
        req.application_id = app_id
        req.offset = offset
        req.limit = limit
        resp = client.List(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def count(self: Self, app_id: str) -> int:
        """Count devices."""
        r = self.reads(app_id, 0, 1)
        return r.get('totalCount', 0) if len(r) > 0 else 0

    def read(self: Self, device_id: str) -> dict | None:
        """Read a device by ID."""
        client = chirpstack_api.api.DeviceServiceStub(self.channel)
        req = chirpstack_api.api.GetDeviceRequest()
        req.id = device_id
        try:
            resp = client.Get(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def read_by_eui(self: Self, app_id: str, dev_eui: str) -> dict | None:
        """Read a device by EUI."""
        client = chirpstack_api.api.DeviceServiceStub(self.channel)
        req = chirpstack_api.api.ListDevicesRequest()
        req.offset = 0
        req.limit = 1
        req.search = dev_eui
        req.application_id = app_id
        try:
            resp = client.List(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def delete(self: Self, dev_eui: str) -> dict | None:
        """Delete a device by EUI."""
        client = chirpstack_api.api.DeviceServiceStub(self.channel)
        req = chirpstack_api.api.DeleteDeviceRequest()
        req.dev_eui = dev_eui
        try:
            resp = client.Delete(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def create(  # noqa: PLR0913
        self: Self,
        name: str,
        description: str,
        app_id: str,
        dev_eui: str,
        dev_prof_id: str,
    ) -> dict:
        """Create a device."""
        client = chirpstack_api.api.DeviceServiceStub(self.channel)
        req = chirpstack_api.api.CreateDeviceRequest()
        req.device.dev_eui = dev_eui
        req.device.name = name
        req.device.description = description
        req.device.application_id = app_id
        req.device.device_profile_id = dev_prof_id
        resp = client.Create(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def read_keys(self: Self, dev_eui: str) -> dict:
        """Read device keys."""
        client = chirpstack_api.api.DeviceServiceStub(self.channel)
        req = chirpstack_api.api.GetDeviceKeysRequest()
        req.dev_eui = dev_eui
        resp = client.GetKeys(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def create_keys(
        self: Self, dev_eui: str, nwk_key: str, app_key: str
    ) -> dict:
        """Create device keys."""
        client = chirpstack_api.api.DeviceServiceStub(self.channel)
        req = chirpstack_api.api.CreateDeviceKeysRequest()
        req.device_keys.dev_eui = dev_eui
        req.device_keys.nwk_key = nwk_key
        req.device_keys.app_key = app_key
        resp = client.CreateKeys(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)


class _DeviceProfileService:
    """This class represents device profile."""

    def __init__(
        self: Self, channel: grpc.Channel, token: list[tuple[str, str]]
    ) -> None:
        """Initialize channel and token properties."""
        self.channel = channel
        self.token = token

    def reads(
        self: Self, tenant_id: str, offset: int = 0, limit: int = 10
    ) -> dict[str, Any]:
        """Read a sublist of device profiles."""
        client = chirpstack_api.api.DeviceProfileServiceStub(self.channel)
        req = chirpstack_api.api.ListDeviceProfilesRequest()
        req.tenant_id = tenant_id
        req.offset = offset
        req.limit = limit
        resp = client.List(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def read(self: Self, device_profile_id: str) -> dict | None:
        """Read a device profile."""
        client = chirpstack_api.api.DeviceProfileServiceStub(self.channel)
        req = chirpstack_api.api.GetDeviceProfileRequest()
        req.id = device_profile_id
        try:
            resp = client.Get(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)[
                'deviceProfile'
            ]
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def create(  # noqa: PLR0913
        self: Self,
        tenant_id: str,
        name: str,
        description: str,
        region: int | str,
        mac_version: int | str,
        reg_params_revision: int | str,
        adr_algorithm_id: str,
    ) -> dict:
        """Create a device profile."""
        client = chirpstack_api.api.DeviceProfileServiceStub(self.channel)
        req = chirpstack_api.api.CreateDeviceProfileRequest()
        req.device_profile.name = name
        req.device_profile.description = name
        req.device_profile.tenant_id = tenant_id
        req.device_profile.name = name
        req.device_profile.description = description
        req.device_profile.region = region
        req.device_profile.mac_version = mac_version
        req.device_profile.reg_params_revision = reg_params_revision
        req.device_profile.adr_algorithm_id = adr_algorithm_id
        req.device_profile.supports_otaa = True
        req.device_profile.supports_class_b = True
        req.device_profile.supports_class_c = True
        req.device_profile.uplink_interval = 3600
        resp = client.Create(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)


class _DeviceQueueService:
    """This class represents device queue."""

    def __init__(
        self: Self, channel: grpc.Channel, token: list[tuple[str, str]]
    ) -> None:
        """Initialize channel and token properties."""
        self.channel = channel
        self.token = token

    def enqueue(self: Self, dev_eui: str, data: bytes, f_port: int = 2) -> dict:
        """Enqueue a message."""
        client = chirpstack_api.api.DeviceServiceStub(self.channel)
        req = chirpstack_api.api.EnqueueDeviceQueueItemRequest()
        req.queue_item.confirmed = False
        req.queue_item.dev_eui = dev_eui
        req.queue_item.data = data
        req.queue_item.f_port = f_port
        resp = client.Enqueue(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)


class _MulticastGroupService:
    """This class provides functions for managing multicast groups."""

    def __init__(
        self: Self, channel: grpc.Channel, token: list[tuple[str, str]]
    ) -> None:
        """Initialize channel and token properties."""
        self.channel = channel
        self.token = token

    def read_by_name(self: Self, app_id: str, name: str) -> dict | None:
        """Read a multicast group by name."""
        client = chirpstack_api.api.MulticastGroupServiceStub(self.channel)
        req = chirpstack_api.api.ListMulticastGroupsRequest()
        req.offset = 0
        req.limit = 1
        req.search = name
        req.application_id = app_id
        try:
            resp = google.protobuf.json_format.MessageToDict(
                client.List(req, metadata=self.token)
            )
            return (
                resp['result'][0]
                if (
                    resp is not None
                    and resp.get('totalCount', 0) == 1
                    and len(resp.get('result', [])) > 0
                )
                else None
            )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def reads(
        self: Self, app_id: str, offset: int = 0, limit: int = 10
    ) -> dict[str, Any]:
        """Read a sublist of multicast groups."""
        client = chirpstack_api.api.MulticastGroupServiceStub(self.channel)
        req = chirpstack_api.api.ListMulticastGroupsRequest()
        req.application_id = app_id
        req.offset = offset
        req.limit = limit
        resp = client.List(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def count(self: Self, app_id: str) -> int:
        """Count multicastGroups."""
        r = self.reads(app_id, 0, 1)
        return r.get('totalCount', 0) if len(r) > 0 else 0

    def read(self: Self, mgid: str) -> dict | None:
        """Read a multicast group by ID."""
        client = chirpstack_api.api.MulticastGroupServiceStub(self.channel)
        req = chirpstack_api.api.GetMulticastGroupRequest()
        req.id = mgid
        try:
            resp = google.protobuf.json_format.MessageToDict(
                client.Get(req, metadata=self.token)
            )
            return resp['multicastGroup']
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def delete(self: Self, mgid: str) -> dict | None:
        """Delete a multicast group by ID."""
        client = chirpstack_api.api.MulticastGroupServiceStub(self.channel)
        req = chirpstack_api.api.DeleteMulticastGroupRequest()
        req.id = mgid
        try:
            resp = client.Delete(req, metadata=self.token)
            return google.protobuf.json_format.MessageToDict(resp)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    def create(self: Self, app_id: str, name: str) -> dict:
        """Create a multicast group."""
        client = chirpstack_api.api.MulticastGroupServiceStub(self.channel)
        req = chirpstack_api.api.CreateMulticastGroupRequest()
        req.multicast_group.name = name
        req.multicast_group.application_id = app_id
        req.multicast_group.region = 2
        req.multicast_group.mc_addr = '0023f440'
        req.multicast_group.mc_nwk_s_key = '7396500101ed7ca0247ac8f7b46ab269'
        req.multicast_group.mc_app_s_key = '3b923538df3fa39443fb4e19502320d5'
        req.multicast_group.f_cnt = 0
        req.multicast_group.group_type = 0
        req.multicast_group.dr = 0
        req.multicast_group.frequency = 0
        resp = client.Create(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def enqueue(self: Self, mgid: str, data: bytes, f_port: int = 2) -> dict:
        """Enqueue a message to a multicast group."""
        client = chirpstack_api.api.MulticastGroupServiceStub(self.channel)
        req = chirpstack_api.api.EnqueueMulticastGroupQueueItemRequest()
        req.queue_item.multicast_group_id = mgid
        req.queue_item.data = data
        req.queue_item.f_port = f_port
        resp = client.Enqueue(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def add_device(self: Self, mgid: str, dev_eui: str) -> dict:
        """Add a device to a multicast group."""
        client = chirpstack_api.api.MulticastGroupServiceStub(self.channel)
        req = chirpstack_api.api.AddDeviceToMulticastGroupRequest()
        req.multicast_group_id = mgid
        req.dev_eui = dev_eui
        resp = client.AddDevice(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)

    def remove_device(self: Self, mgid: str, dev_eui: str) -> dict:
        """Add a device to a multicast group."""
        client = chirpstack_api.api.MulticastGroupServiceStub(self.channel)
        req = chirpstack_api.api.RemoveDeviceFromMulticastGroupRequest()
        req.multicast_group_id = mgid
        req.dev_eui = dev_eui
        resp = client.RemoveDevice(req, metadata=self.token)
        return google.protobuf.json_format.MessageToDict(resp)


class ChirpStackState(enum.Enum):
    """This class represents the ChirpStack state."""

    UNKNOWN = 0
    UNAVAILABLE = 1
    UNAUTHENTICATED = 2
    READY = 3


class _ChirpStackService:
    """This class represents ChirpStack."""

    def __init__(
        self: Self,
        settings: Annotated[
            api.config.Settings, fastapi.Depends(api.config.get_settings)
        ],
    ) -> None:
        """Initialize all ChirpStack related subservices."""
        channel = grpc.insecure_channel(settings.CHIRPSTACK_SERVER_URL)
        token = [
            ('authorization', f'Bearer {settings.CHIRPSTACK_SERVER_JWT_TOKEN}')
        ]

        self.settings = settings
        self.tenant = _TenantService(channel, token)
        self.application = _ApplicationService(channel, token)
        self.gateway = _GatewayService(channel, token)
        self.device = _DeviceService(channel, token)
        self.device_queue = _DeviceQueueService(channel, token)
        self.device_profile = _DeviceProfileService(channel, token)
        self.multicast_group = _MulticastGroupService(channel, token)

    def get_current_state(self: Self) -> ChirpStackState:
        """Determine if ChirpStack is ready."""
        channel = grpc.insecure_channel(self.settings.CHIRPSTACK_SERVER_URL)
        token = [
            (
                'authorization',
                f'Bearer {self.settings.CHIRPSTACK_SERVER_JWT_TOKEN}',
            )
        ]
        tenant = _TenantService(channel, token)
        try:
            tenant.reads()
        except grpc.RpcError as e:
            match e.code():
                case grpc.StatusCode.UNAUTHENTICATED:
                    return ChirpStackState.UNAUTHENTICATED
                case grpc.StatusCode.UNAVAILABLE:
                    return ChirpStackState.UNAVAILABLE
                case _:
                    return ChirpStackState.UNKNOWN
        else:
            return ChirpStackState.READY


_chirpstack_serv = _ChirpStackService(api.config.get_settings())

OAUTH2_SCHEME = fastapi.security.OAuth2PasswordBearer(tokenUrl='api/token')
_pwd_context = passlib.context.CryptContext(
    schemes=['bcrypt'], deprecated='auto'
)


class AuthService:
    """This class provides functions for authentication."""

    def __init__(
        self: Self,
        settings: Annotated[
            api.config.Settings, fastapi.Depends(api.config.get_settings)
        ],
        user_repo: Annotated[
            api.repositories.UserRepository,
            fastapi.Depends(api.repositories.UserRepository),
        ],
    ) -> None:
        """Initialize settings, user_repo, and pwd_context properties."""
        self.settings = settings
        self.user_repo = user_repo

    def verify_password(
        self: Self, plain_password: str, hashed_password: str
    ) -> bool:
        """Verify password."""
        return _pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self: Self, password: str) -> str:
        """Get password hash."""
        return _pwd_context.hash(password)

    async def authenticate(
        self: Self, email: str, password: str
    ) -> api.models.User | None:
        """Return user if pass otherwise false."""
        user = await self.user_repo.find_by_email(email)
        if user is not None and _pwd_context.verify(
            password, user.hashed_password
        ):
            return user
        return None

    def create_access_token(
        self: Self, data: dict, expires_delta: datetime.timedelta | None = None
    ) -> str:
        """Return an encoded JWT token."""
        to_encode = data.copy()
        if expires_delta:
            expire = (
                datetime.datetime.now(tz=datetime.timezone.utc) + expires_delta
            )
        else:
            expire = datetime.datetime.now(
                tz=datetime.timezone.utc
            ) + datetime.timedelta(minutes=15)
        to_encode.update({'exp': expire})
        return jose.jwt.encode(
            to_encode,
            self.settings.NL_API_SECRET_KEY,
            algorithm=self.settings.NL_API_ALGORITHM,
        )

    @staticmethod
    async def get_current_user(
        settings: Annotated[
            api.config.Settings, fastapi.Depends(api.config.get_settings)
        ],
        user_repo: Annotated[
            api.repositories.UserRepository,
            fastapi.Depends(api.repositories.UserRepository),
        ],
        token: Annotated[str, fastapi.Depends(OAUTH2_SCHEME)],
    ) -> api.models.User:
        """Get current user."""
        credentials_exception = fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jose.jwt.decode(
                token,
                settings.NL_API_SECRET_KEY,
                algorithms=[settings.NL_API_ALGORITHM],
            )
            username = payload.get('sub')
            if username is None:
                raise credentials_exception
        except jose.JWTError:
            raise credentials_exception  # noqa: B904
        user = await user_repo.find_by_email(username)
        if user is None:
            raise credentials_exception
        return user


class UserService:
    """This class provides functions for managing users."""

    def __init__(
        self: Self,
        user_repo: Annotated[
            api.repositories.UserRepository,
            fastapi.Depends(api.repositories.UserRepository),
        ],
    ) -> None:
        """Initialize user_repo and auth_serv properties."""
        self.user_repo = user_repo

    async def _create_user(self: Self, uc: api.schemas.UserCreate) -> int:
        """Create user."""
        u = api.models.User(
            account_id=uc.account_id,
            email=uc.email,
            hashed_password=_pwd_context.hash(uc.password),
            first_name=uc.first_name,
            last_name=uc.last_name,
            role=uc.role,
        )
        return await self.user_repo.insert(u)

    async def create(
        self: Self, current_user: api.schemas.User, user: api.schemas.UserCreate
    ) -> int | None:
        """Create user."""
        match current_user.role:
            case 'super-admin':
                return await self._create_user(user)
            case 'admin':
                if user.account_id == current_user.account_id:
                    return await self._create_user(user)
                return None
            case _:
                return None

    async def read_users(
        self: Self,
        current_user: api.schemas.User,
        skip: int = 0,
        limit: int = 4,
    ) -> Sequence[api.schemas.User]:
        """Read a sublist of users."""

        def to_schema_user(
            us: Sequence[api.models.User],
        ) -> Sequence[api.schemas.User]:
            return [api.schemas.User.from_orm(u) for u in us]

        match current_user.role:
            case 'super-admin':
                return to_schema_user(
                    await self.user_repo.find_all(skip, limit)
                )
            case 'admin':
                return to_schema_user(
                    await self.user_repo.find_by_account_id(
                        current_user.account_id
                    )
                )
            case _:
                return [current_user]


class DimmingEventService:
    """This class provides functions for managing dimming events."""

    def __init__(
        self: Self,
        settings: Annotated[
            api.config.Settings, fastapi.Depends(api.config.get_settings)
        ],
        repo: Annotated[
            api.repositories.DimmingEventRepository,
            fastapi.Depends(api.repositories.DimmingEventRepository),
        ],
    ) -> None:
        """Initialize repo, dimmer_host, and dimmer_port properties."""
        self.repo = repo
        self.dimmer_host = settings.NL_DIMMER_HOST
        self.dimmer_port = settings.NL_DIMMER_PORT

    async def get_one(self: Self, deid: int) -> api.schemas.DimmingEvent | None:
        """Get a dimming event by ID."""
        if de := await self.repo.find_by_id(deid):
            return api.schemas.DimmingEvent.from_orm(de)
        return None

    async def get_sublist(
        self: Self, skip: int, limit: int | None
    ) -> api.schemas.DimmingEventList:
        """Get a sublist of dimming events."""
        return api.schemas.DimmingEventList(
            total=await self.repo.count(),
            data=[
                api.schemas.DimmingEvent.from_orm(x)
                for x in await self.repo.find_all(skip, limit)
            ],
        )

    async def create(
        self: Self, dec: api.schemas.DimmingEventCreate
    ) -> int | None:
        """Create a dimming event."""
        cmd = dec.command.value
        if cmd.startswith('dim'):
            val = int(cmd.split('_')[1])
            args = [dec.target_id, val]
        else:
            args = [dec.target_id]

        conn = rpyc.connect(self.dimmer_host, self.dimmer_port)
        job = conn.root.add_job(
            f'dimmer:commands.{cmd}',
            'cron',
            args=args,
            hour=dec.start.time().hour,
            minute=dec.start.time().minute,
        )
        de = api.models.DimmingEvent(**(dec.model_dump() | {'job_id': job.id}))

        return await self.repo.insert(de)

    async def update(
        self: Self,
        deid: int,
        deu: api.schemas.DimmingEventUpdate,
    ) -> int:
        """Update dimming event by ID."""
        de = await self.repo.find_by_id(deid)
        if de is None:
            return 0
        conn = rpyc.connect(self.dimmer_host, self.dimmer_port)
        conn.root.remove_job(de.job_id)

        cmd = deu.command.value
        if cmd.startswith('dim'):
            val = int(cmd.split('_')[1])
            args = [deu.target_id, val]
        else:
            args = [deu.target_id]

        job = conn.root.add_job(
            f'dimmer:commands.{cmd}',
            'cron',
            args=args,
            hour=deu.start.time().hour,
            minute=deu.start.time().minute,
        )

        ude = api.models.DimmingEvent(
            id=de.id,
            account_id=de.account_id,
            job_id=job.id,
            target_id=de.target_id,
            command=de.command,
            start=de.start,
            end=de.end,
            color=de.color,
            text_color=de.text_color,
        )

        return await self.repo.update(ude)

    async def delete_by_id(self: Self, deid: int) -> int:
        """Delete dimming event by ID."""
        de = await self.repo.find_by_id(deid)
        if de is None:
            return 0
        conn = rpyc.connect(self.dimmer_host, self.dimmer_port)
        conn.root.remove_job(de.job_id)
        return await self.repo.delete_by_id(deid)


class DimmingProfileService:
    """This class provides functions for managing dimming profiles."""

    def __init__(
        self: Self,
        settings: Annotated[
            api.config.Settings, fastapi.Depends(api.config.get_settings)
        ],
        dprof_repo: Annotated[
            api.repositories.DimmingProfileRepository,
            fastapi.Depends(api.repositories.DimmingProfileRepository),
        ],
        de_repo: Annotated[
            api.repositories.DimmingEventRepository,
            fastapi.Depends(api.repositories.DimmingEventRepository),
        ],
    ) -> None:
        """Initialize the repo property."""
        self.dprof_repo = dprof_repo
        self.devent_repo = de_repo
        self.dimmer_host = settings.NL_DIMMER_HOST
        self.dimmer_port = settings.NL_DIMMER_PORT

    async def _add_command_job(  # noqa: ANN202
        self: Self,
        cmd: api.models.DimmingCommand,
        date: datetime.datetime,
        target_id: str,
    ):
        if cmd.value.startswith('dim'):
            val = int(cmd.value.split('_')[1])
            cmd_str = 'dimmer:commands.dim_group'
            args = [target_id, val]
        else:
            cmd_str = f'dimmer:commands.{cmd.value}_group'
            args = [target_id]

        conn = rpyc.connect(self.dimmer_host, self.dimmer_port)
        return conn.root.add_job(
            cmd_str,
            'cron',
            args=args,
            hour=date.time().hour,
            minute=date.time().minute,
        )

    async def _create_events(
        self: Self, dpid: int, dpc: api.schemas.DimmingProfileBase
    ) -> None:
        for hour, cmd in [
            (18, dpc.sunset_dim_cmd0),
            (18, dpc.sunset_dim_cmd1),
            (20, dpc.h2000_dim_cmd),
            (22, dpc.h2200_dim_cmd),
            (0, dpc.h0000_dim_cmd),
            (2, dpc.h0200_dim_cmd),
            (4, dpc.h0400_dim_cmd),
            (6, dpc.sunrise_dim_cmd0),
            (6, dpc.sunrise_dim_cmd1),
        ]:
            date = api.utils.today_hour(hour)
            dec = api.schemas.DimmingEventCreate(
                account_id=dpc.account_id,
                dimming_profile_id=dpid,
                target_id=dpc.multicast_group_id,
                target_type=api.models.TargetType.DEVICE_GROUP,
                command=cmd,
                start=date,
                end=date,
                color=dpc.color,
                text_color='#ffffff',
            )
            job = await self._add_command_job(cmd, date, dpc.multicast_group_id)
            de = api.models.DimmingEvent(
                **(dec.model_dump() | {'job_id': job.id})
            )
            await self.devent_repo.insert(de)

    async def create(
        self: Self, dpc: api.schemas.DimmingProfileCreate
    ) -> int | None:
        """Create a dimming profile."""
        dp = api.models.DimmingProfile(
            account_id=dpc.account_id,
            multicast_group_id=dpc.multicast_group_id,
            active=dpc.active,
            name=dpc.name,
            description=dpc.description,
            color=dpc.color,
            sunset_dim_cmd0=dpc.sunset_dim_cmd0,
            sunset_dim_cmd1=dpc.sunset_dim_cmd1,
            h2000_dim_cmd=dpc.h2000_dim_cmd,
            h2200_dim_cmd=dpc.h2200_dim_cmd,
            h0000_dim_cmd=dpc.h0000_dim_cmd,
            h0200_dim_cmd=dpc.h0200_dim_cmd,
            h0400_dim_cmd=dpc.h0400_dim_cmd,
            sunrise_dim_cmd0=dpc.sunrise_dim_cmd0,
            sunrise_dim_cmd1=dpc.sunrise_dim_cmd1,
        )
        dpid = await self.dprof_repo.insert(dp)
        if dpid is not None:
            await self._create_events(dpid, dpc)
        return dpid

    async def update(
        self: Self, dpid: int, dpu: api.schemas.DimmingProfileUpdate
    ) -> int | None:
        """Update a dimming profile by ID."""
        if dp := await self.dprof_repo.find_by_id(dpid):
            dp.account_id = dpu.account_id
            dp.multicast_group_id = dpu.multicast_group_id
            dp.active = dpu.active
            dp.name = dpu.name
            dp.description = dpu.description
            dp.color = dpu.color
            dp.sunset_dim_cmd0 = dpu.sunset_dim_cmd0
            dp.sunset_dim_cmd1 = dpu.sunset_dim_cmd1
            dp.h2000_dim_cmd = dpu.h2000_dim_cmd
            dp.h2200_dim_cmd = dpu.h2200_dim_cmd
            dp.h0000_dim_cmd = dpu.h0000_dim_cmd
            dp.h0200_dim_cmd = dpu.h0200_dim_cmd
            dp.h0400_dim_cmd = dpu.h0400_dim_cmd
            dp.sunrise_dim_cmd0 = dpu.sunrise_dim_cmd0
            dp.sunrise_dim_cmd1 = dpu.sunrise_dim_cmd1
            if await self.dprof_repo.update(dpid, dp):
                conn = rpyc.connect(self.dimmer_host, self.dimmer_port)
                for de in await self.devent_repo.find_by_pid(dpid):
                    conn.root.remove_job(de.job_id)
                await self.devent_repo.delete_by_dpid(dpid)
                await self._create_events(dpid, dpu)
        return None

    async def get_one(
        self: Self, dpid: int
    ) -> api.schemas.DimmingProfile | None:
        """Get a dimming profile by ID."""
        if dp := await self.dprof_repo.find_by_id(dpid):
            return api.schemas.DimmingProfile.from_orm(dp)
        return None

    async def get_sublist(
        self: Self, skip: int, limit: int
    ) -> api.schemas.DimmingProfileList:
        """Get a sublist of dimming profiles."""
        return api.schemas.DimmingProfileList(
            total=await self.dprof_repo.count(),
            data=[
                api.schemas.DimmingProfile.from_orm(dp)
                for dp in await self.dprof_repo.find_all(skip, limit)
            ],
        )

    async def delete_one(self: Self, dpid: int) -> int:
        """Delete dimming profile by ID."""
        conn = rpyc.connect(self.dimmer_host, self.dimmer_port)
        for de in await self.devent_repo.find_by_pid(dpid):
            conn.root.remove_job(de.job_id)
        await self.devent_repo.delete_by_dpid(dpid)
        return await self.dprof_repo.delete_by_id(dpid)


class GatewayService:
    """This class provides functions for managing gateways."""

    def __init__(self: Self) -> None:
        """Initialize classes properties."""
        self.chirpstack_serv = _chirpstack_serv

    def reads(self: Self, offset: int = 0, limit: int = 10) -> dict[str, Any]:
        """Read a sublist of gateways."""
        return self.chirpstack_serv.gateway.reads(offset, limit)

    def read(self: Self, gid: str) -> dict | None:
        """Read a gateway."""
        return self.chirpstack_serv.gateway.read(gid)

    def create(
        self: Self, tid: str, gid: str, name: str, description: str | None
    ) -> dict:
        """Create a gateway."""
        return self.chirpstack_serv.gateway.create(tid, gid, name, description)

    def update(
        self: Self, tid: str, gid: str, name: str, description: str
    ) -> dict:
        """Update a gateway."""
        return self.chirpstack_serv.gateway.update(tid, gid, name, description)

    def delete(self: Self, gid: str) -> dict:
        """Delete a gateway."""
        return self.chirpstack_serv.gateway.delete(gid)


class StreetlampService:
    """This class provides functions for managing streetlamps."""

    def __init__(
        self: Self,
        streetlamp_repo: Annotated[
            api.repositories.StreetlampRepository,
            fastapi.Depends(api.repositories.StreetlampRepository),
        ],
    ) -> None:
        """Initialize streetlamp_repo and chirpstack_serv properties."""
        self.streetlamp_repo = streetlamp_repo
        self.chirpstack_serv = _chirpstack_serv

    async def get_sublist(
        self: Self, skip: int, limit: int
    ) -> api.schemas.StreetlampList:
        """Get a sublist of devices."""
        return api.schemas.StreetlampList(
            data=[
                api.schemas.Streetlamp.from_orm(s)
                for s in await self.streetlamp_repo.find_all(skip, limit)
            ],
            total=await self.streetlamp_repo.count(),
        )

    async def _create_or_read_device(
        self: Self, name: str, app_id: str, dev_eui: str, dev_prof_id: str
    ) -> str:
        r = self.chirpstack_serv.device.read_by_eui(app_id, dev_eui)
        if (
            r is not None
            and 'totalCount' in r
            and r.get('totalCount', 0) == 1
            and len(r['result']) > 0
        ):
            return dev_eui
        r = self.chirpstack_serv.device.create(
            name=name,
            description='',
            app_id=app_id,
            dev_eui=dev_eui,
            dev_prof_id=dev_prof_id,
        )
        return dev_eui

    async def _create_device_keys(
        self: Self, dev_eui: str, app_key: str
    ) -> None:
        self.chirpstack_serv.device.create_keys(
            dev_eui=dev_eui, nwk_key=app_key, app_key=app_key
        )

    async def create(
        self: Self,
        sc: api.schemas.StreetlampCreate,
        cs_app_id: str,
        cs_streetlamp_dp_id: str,
    ) -> int | None:
        """Create streetlamp."""
        dp = self.chirpstack_serv.device_profile.read(cs_streetlamp_dp_id)
        if dp is not None:
            await self._create_or_read_device(
                name=sc.name,
                app_id=cs_app_id,
                dev_eui=sc.device_eui.lower(),
                dev_prof_id=dp['id'],
            )
            await self._create_device_keys(
                dev_eui=sc.device_eui.lower(), app_key=sc.app_key
            )
            s = api.models.Streetlamp(
                **sc.model_dump(exclude={'app_key': True})
            )
            return await self.streetlamp_repo.insert(s)
        return None

    async def creates(
        self: Self,
        file: fastapi.UploadFile,
        aid: int,
        cs_app_id: str,
        cs_streetlamp_dp_id: str,
    ) -> list[dict]:
        """Create streetlamps from file."""
        s = await file.read()
        es = []
        for x in csv.DictReader(io.StringIO(s.decode('utf-8'))):
            try:
                async with self.streetlamp_repo.db.begin_nested():
                    await self.create(
                        sc=api.schemas.StreetlampCreate(
                            account_id=aid,
                            device_eui=x['name'].lower(),
                            name='NLPY' + x['name'].lower(),
                            app_key=x['app_key'],
                            lon=float(x['lon']),
                            lat=float(x['lat']),
                        ),
                        cs_app_id=cs_app_id,
                        cs_streetlamp_dp_id=cs_streetlamp_dp_id,
                    )
            except sqlalchemy.exc.IntegrityError as e:  # noqa: PERF203
                es.append({'loc': 'name', 'msg': str(e)})
            except grpc.RpcError as e:
                es.append({'loc': 'name', 'msg': str(e)})
        return es

    async def update(
        self: Self, sid: int, su: api.schemas.StreetlampUpdate
    ) -> bool:
        """Update a streetlamp."""
        if await self.streetlamp_repo.find_by_id(sid):
            return await self.streetlamp_repo.update(
                sid,
                api.models.Streetlamp(
                    account_id=su.account_id,
                    device_eui=su.device_eui,
                    name=su.name,
                    lon=su.lon,
                    lat=su.lat,
                ),
            )
        return False

    async def delete_by_id(self: Self, sid: int) -> bool:
        """Delete a streetlamp."""
        if (
            s := await self.streetlamp_repo.find_by_id(sid)
        ) and self.chirpstack_serv.device.delete(s.device_eui) is not None:
            return await self.streetlamp_repo.delete_by_id(sid)
        return False


class StreetlampDeviceService:
    """This class provides functions for managing streetlamp devices."""

    def __init__(
        self: Self,
        streetlamp_repo: Annotated[
            api.repositories.StreetlampRepository,
            fastapi.Depends(api.repositories.StreetlampRepository),
        ],
    ) -> None:
        """Initialize class properties."""
        self.streetlamp_repo = streetlamp_repo
        self.chirpstack_serv = _chirpstack_serv

    async def get_sublist(
        self: Self, cs_application_id: str, skip: int, limit: int
    ) -> dict:
        """Get a sublist of devices."""
        return self.chirpstack_serv.device.reads(cs_application_id, skip, limit)

    async def get_available(self: Self, cs_application_id: str) -> list[str]:
        """Get the EUI of the available streetlamps."""
        dc = self.chirpstack_serv.device.count(cs_application_id)
        dr = self.chirpstack_serv.device.reads(cs_application_id, 0, dc)
        dev_euis = [d['devEui'] for d in dr['result']]
        sc = await self.streetlamp_repo.count()
        if sc is not None:
            ss = await self.streetlamp_repo.find_all(limit=sc)
            return list(filter(lambda x: x not in ss, dev_euis))
        return []

    def enqueue_command(self: Self, dev_eui: str, cmd: bytes) -> dict:
        """Turn on a FMC device."""
        return self.chirpstack_serv.device_queue.enqueue(dev_eui, cmd)

    def turn_on(self: Self, dev_eui: str) -> dict:
        """Turn on a FMC device."""
        return self.chirpstack_serv.device_queue.enqueue(dev_eui, b'9529-ON')

    def turn_off(self: Self, dev_eui: str) -> dict:
        """Turn off a FMC device."""
        return self.chirpstack_serv.device_queue.enqueue(dev_eui, b'9529-OF')

    def dim(self: Self, dev_eui: str, val: int) -> dict:
        """Dim a FMC device."""
        return self.chirpstack_serv.device_queue.enqueue(
            dev_eui, bytes(f'9529-DM{str(val).zfill(3)}', 'utf-8')
        )


STREETLAMP_STATES_STR = 'streetlamp_states'


def encode_state_data(sds: api.schemas.StreetlampDeviceState) -> str:
    """Encode FMC device state data."""

    def encode_float(h: str, val: float) -> bytes:
        return h.encode() + struct.pack('<d', val)

    return base64.b64encode(
        encode_float('V', sds.voltage)
        + encode_float('I', sds.current)
        + encode_float('M', sds.energy_out)
        + encode_float('E', sds.energy_in)
        + encode_float('W', sds.power)
        + encode_float('F', sds.frequency)
        + b'S'
        + (b'\x01' if sds.status_on else b'\x00')
        + b'\xff\xff\xff\xff\xff\xff\xff\xff'
    ).decode()


def decode_state_data(s: str) -> api.schemas.StreetlampDeviceState:
    """Decode FMC device state data."""
    ndouble = 6
    vals = [
        struct.unpack('<d', x) if j < ndouble else (bool(x[0]),)
        for j, x in enumerate(
            [base64.b64decode(s)[i + 1 + 8 * i : 9 * (i + 1)] for i in range(7)]
        )
    ]
    return api.schemas.StreetlampDeviceState(
        voltage=vals[0][0],
        current=vals[1][0],
        energy_out=vals[2][0],
        energy_in=vals[3][0],
        power=vals[4][0],
        frequency=vals[5][0],
        status_on=vals[6][0],
    )


def _make_alarm(
    ss: api.models.StreetlampState,
    atype: api.models.AlarmType,
    severity: api.models.AlarmSeverity,
) -> api.models.StreetlampAlarm:
    return api.models.StreetlampAlarm(
        time=ss.time,
        atype=atype,
        severity=severity,
        cleared=False,
        dev_eui=ss.dev_eui,
        dev_voltage=ss.dev_voltage,
        dev_current=ss.dev_current,
        dev_energy_out=ss.dev_energy_out,
        dev_energy_in=ss.dev_energy_in,
        dev_power=ss.dev_power,
        dev_frequency=ss.dev_frequency,
        dev_status_on=ss.dev_status_on,
    )


class StreetlampStateService:
    """This class provides functions for managing streetlamp states."""

    def __init__(
        self: Self,
        sstate_repo: Annotated[
            api.repositories.StreetlampStateRepository,
            fastapi.Depends(api.repositories.StreetlampStateRepository),
        ],
        stream_repo: Annotated[
            api.repositories.StreamStateRepository,
            fastapi.Depends(api.repositories.StreamStateRepository),
        ],
        salarm_repo: Annotated[
            api.repositories.StreetlampAlarmRepository,
            fastapi.Depends(api.repositories.StreetlampAlarmRepository),
        ],
    ) -> None:
        """Initialize slstate_repo and stream_repo properties."""
        self.sstate_repo = sstate_repo
        self.stream_repo = stream_repo
        self.salarm_repo = salarm_repo

    async def find_latest(
        self: Self, dev_eui: str
    ) -> api.schemas.StreetlampState | None:
        """Find latest streetlamp state."""
        if ss := await self.sstate_repo.find_latest_by_dev_eui(dev_eui):
            return api.schemas.StreetlampState.model_validate(
                ss, from_attributes=True
            )
        return None

    async def find_by_id(
        self: Self, ssid: int
    ) -> api.schemas.StreetlampState | None:
        """Find a streetlamp state by ID."""
        if ss := await self.sstate_repo.find_by_id(ssid):
            return api.schemas.StreetlampState.model_validate(
                ss, from_attributes=True
            )
        return None

    async def enqueue_create(self: Self, state: bytes) -> None:
        """Enqueue create streetlamp state."""
        await api.rs.db.xadd(
            name='nl:streetlamp_states', fields={'value': state}
        )

    async def create(
        self: Self, ssc: api.schemas.StreetlampStateCreate
    ) -> int | None:
        """Create streetlamp state."""
        sds = decode_state_data(ssc.data)
        time = ssc.time.astimezone(zoneinfo.ZoneInfo('America/Santo_Domingo'))
        ss = api.models.StreetlampState(
            deduplication_id=ssc.deduplication_id,
            time=time,
            tenant_id=ssc.device_info.tenant_id,
            tenant_name=ssc.device_info.tenant_name,
            application_id=ssc.device_info.application_id,
            application_name=ssc.device_info.application_name,
            device_profile_id=ssc.device_info.device_profile_id,
            device_profile_name=ssc.device_info.device_profile_name,
            device_name=ssc.device_info.device_name,
            dev_eui=ssc.device_info.dev_eui,
            dev_addr=ssc.dev_addr,
            dev_voltage=sds.voltage,
            dev_current=sds.current,
            dev_energy_out=sds.energy_out,
            dev_energy_in=sds.energy_in,
            dev_power=sds.power,
            dev_frequency=sds.frequency,
            dev_status_on=sds.status_on,
        )

        min_valid_value = 0.0001
        max_valid_value = 1000.0

        if (
            math.isnan(ss.dev_voltage)
            or ss.dev_voltage < min_valid_value
            or ss.dev_voltage > max_valid_value
            or math.isnan(ss.dev_current)
            or ss.dev_current < min_valid_value
            or ss.dev_current > max_valid_value
            or math.isnan(ss.dev_power)
            or ss.dev_power < min_valid_value
            or ss.dev_power > max_valid_value
            or math.isnan(ss.dev_frequency)
            or ss.dev_frequency < min_valid_value
            or ss.dev_frequency > max_valid_value
        ):
            await self.salarm_repo.insert(
                _make_alarm(
                    ss,
                    api.models.AlarmType.INVALID_VALUE,
                    api.models.AlarmSeverity.MINOR,
                )
            )
            return None

        max_power = 95.0
        if ss.dev_power > max_power:
            await self.salarm_repo.insert(
                _make_alarm(
                    ss,
                    api.models.AlarmType.OVER_POWER,
                    api.models.AlarmSeverity.CRITICAL,
                )
            )
            return None

        max_frequency = 65
        if ss.dev_frequency > max_frequency:
            await self.salarm_repo.insert(
                _make_alarm(
                    ss,
                    api.models.AlarmType.OVER_FREQUENCY,
                    api.models.AlarmSeverity.CRITICAL,
                )
            )
            return None

        max_ecr = 100000
        ls = await self.sstate_repo.find_latest_by_dev_eui(ss.dev_eui)
        if ls is not None:
            t = (ss.time - ls.time).total_seconds() // 3600
            t = 1 if t == 0 else t
            if (ss.dev_energy_in - ls.dev_energy_in) / t > max_ecr:
                await self.salarm_repo.insert(
                    _make_alarm(
                        ss,
                        api.models.AlarmType.OVER_ENERGY,
                        api.models.AlarmSeverity.MAJOR,
                    )
                )
                return None

        if (ssid := await self.sstate_repo.insert(ss)) is not None:
            await self.stream_repo.update_producer(
                f'streetlamp:state:hourly:{ssc.device_info.dev_eui}',
                api.utils.round_to_hour(time),
            )
        return ssid


@dataclasses.dataclass
class _StreamDataRange:
    """This class represents a stream data range."""

    t0: datetime.datetime
    t1: datetime.datetime


class StreetlampHourlyAggregationService:
    """This class provides functions for consolidating energy data."""

    def __init__(
        self: Self,
        streetlamp_repo: Annotated[
            api.repositories.StreetlampRepository,
            fastapi.Depends(api.repositories.StreetlampRepository),
        ],
        sstate_repo: Annotated[
            api.repositories.StreetlampStateRepository,
            fastapi.Depends(api.repositories.StreetlampStateRepository),
        ],
        streamst_repo: Annotated[
            api.repositories.StreamStateRepository,
            fastapi.Depends(api.repositories.StreamStateRepository),
        ],
        hourly_state_repo: Annotated[
            api.repositories.HourlyStreetlampStateRepository,
            fastapi.Depends(api.repositories.HourlyStreetlampStateRepository),
        ],
    ) -> None:
        """Initialize class properties."""
        self.streetlamp_repo = streetlamp_repo
        self.sstate_repo = sstate_repo
        self.streamst_repo = streamst_repo
        self.hourly_state_repo = hourly_state_repo

    async def _get_hourly_range(
        self: Self,
        strname: str,
        dev_eui: str,
    ) -> _StreamDataRange | None:
        ss_str = await self.streamst_repo.find_by_name(strname)

        if ss_str is None or ss_str.producer_ts is None:
            return None

        if ss_str.consumer_ts is None:
            if oss := await self.sstate_repo.find_oldest_by_dev_eui(dev_eui):
                t0 = api.utils.round_to_hour(oss.time)
            else:
                return None
        else:
            t0 = ss_str.consumer_ts
        t1 = ss_str.producer_ts

        if t0 == t1:
            return None

        return _StreamDataRange(
            api.utils.convert_to_default_tz(t0),
            api.utils.convert_to_default_tz(t1),
        )

    async def aggregate(self: Self) -> int:
        """Run hourly aggregation process."""
        tnr = 0
        for s in await self.streetlamp_repo.find_all():
            strname = f'streetlamp:state:hourly:{s.device_eui}'
            match await self._get_hourly_range(strname, s.device_eui):
                case None:
                    pass

                case _StreamDataRange(t0=t0, t1=t1):
                    nr = await self.hourly_state_repo.pull(s.device_eui, t0, t1)
                    api.log.logger.info(
                        'Stream [%s][%s -- %s]: %s rows(s) inserted',
                        strname,
                        t0,
                        t1,
                        nr,
                    )

                    await self.streamst_repo.update_consumer(strname, t1)
                    await self.streamst_repo.update_producer(
                        f'streetlamp:state:daily:{s.device_eui}',
                        api.utils.round_to_day(t1),
                    )
                    tnr += nr
        return tnr


class StreetlampDailyAggregationService:
    """This class provides functions for consolidating energy data."""

    def __init__(
        self: Self,
        streetlamp_repo: Annotated[
            api.repositories.StreetlampRepository,
            fastapi.Depends(api.repositories.StreetlampRepository),
        ],
        streamst_repo: Annotated[
            api.repositories.StreamStateRepository,
            fastapi.Depends(api.repositories.StreamStateRepository),
        ],
        hourly_state_repo: Annotated[
            api.repositories.HourlyStreetlampStateRepository,
            fastapi.Depends(api.repositories.HourlyStreetlampStateRepository),
        ],
        daily_state_repo: Annotated[
            api.repositories.DailyStreetlampStateRepository,
            fastapi.Depends(api.repositories.DailyStreetlampStateRepository),
        ],
    ) -> None:
        """Initialize class properties."""
        self.streetlamp_repo = streetlamp_repo
        self.streamst_repo = streamst_repo
        self.hourly_state_repo = hourly_state_repo
        self.daily_state_repo = daily_state_repo

    async def _get_daily_range(
        self: Self, strname: str, dev_eui: str
    ) -> _StreamDataRange | None:
        ss_str = await self.streamst_repo.find_by_name(strname)

        if ss_str is None or ss_str.producer_ts is None:
            return None

        if ss_str.consumer_ts is None:
            if ohse := await self.hourly_state_repo.find_oldest_by_dev_eui(
                dev_eui
            ):
                t0 = ohse.hour
            else:
                return None
        else:
            t0 = ss_str.consumer_ts
        t1 = ss_str.producer_ts

        if t0 == t1:
            return None

        return _StreamDataRange(
            api.utils.convert_to_default_tz(t0),
            api.utils.convert_to_default_tz(t1),
        )

    async def aggregate(self: Self) -> int:
        """Run daily aggregation process."""
        tnd = 0
        for s in await self.streetlamp_repo.find_all():
            strname = f'streetlamp:state:daily:{s.device_eui}'
            match await self._get_daily_range(strname, s.device_eui):
                case None:
                    pass

                case _StreamDataRange(t0=t0, t1=t1):
                    nd = await self.daily_state_repo.pull(s.device_eui, t0, t1)
                    api.log.logger.info(
                        'Stream [%s][%s -- %s]: %s rows(s) inserted',
                        strname,
                        t0,
                        t1,
                        nd,
                    )

                    await self.streamst_repo.update_consumer(strname, t1)
                    await self.streamst_repo.update_producer(
                        f'streetlamp:state:weekly:{s.device_eui}',
                        api.utils.round_to_week(t1),
                    )
                    await self.streamst_repo.update_producer(
                        f'streetlamp:state:monthly:{s.device_eui}',
                        api.utils.round_to_month(t1),
                    )
                    tnd += nd
        return tnd


class StreetlampWeeklyAggregationService:
    """This class provides functions for consolidating energy data."""

    def __init__(
        self: Self,
        streetlamp_repo: Annotated[
            api.repositories.StreetlampRepository,
            fastapi.Depends(api.repositories.StreetlampRepository),
        ],
        streamst_repo: Annotated[
            api.repositories.StreamStateRepository,
            fastapi.Depends(api.repositories.StreamStateRepository),
        ],
        daily_state_repo: Annotated[
            api.repositories.DailyStreetlampStateRepository,
            fastapi.Depends(api.repositories.DailyStreetlampStateRepository),
        ],
        weekly_state_repo: Annotated[
            api.repositories.WeeklyStreetlampStateRepository,
            fastapi.Depends(api.repositories.WeeklyStreetlampStateRepository),
        ],
    ) -> None:
        """Initialize class properties."""
        self.streetlamp_repo = streetlamp_repo
        self.streamst_repo = streamst_repo
        self.daily_state_repo = daily_state_repo
        self.weekly_state_repo = weekly_state_repo

    async def _get_weekly_range(
        self: Self, strname: str, dev_eui: str
    ) -> _StreamDataRange | None:
        ss_str = await self.streamst_repo.find_by_name(strname)

        if ss_str is None or ss_str.producer_ts is None:
            return None

        if ss_str.consumer_ts is None:
            if odse := await self.daily_state_repo.find_oldest_by_dev_eui(
                dev_eui
            ):
                t0 = odse.day
            else:
                return None
        else:
            t0 = ss_str.consumer_ts
        t1 = ss_str.producer_ts

        if t0 == t1:
            return None

        return _StreamDataRange(
            api.utils.convert_to_default_tz(t0),
            api.utils.convert_to_default_tz(t1),
        )

    async def aggregate(self: Self) -> int:
        """Run weekly aggregation process."""
        tnw = 0
        for s in await self.streetlamp_repo.find_all():
            strname = f'streetlamp:state:weekly:{s.device_eui}'
            match await self._get_weekly_range(strname, s.device_eui):
                case None:
                    pass

                case _StreamDataRange(t0=t0, t1=t1):
                    nw = await self.weekly_state_repo.pull(s.device_eui, t0, t1)
                    api.log.logger.info(
                        'Stream [%s][%s -- %s]: %s rows(s) inserted',
                        strname,
                        t0,
                        t1,
                        nw,
                    )

                    await self.streamst_repo.update_consumer(strname, t1)
                    tnw += nw
        return tnw


class StreetlampMonthlyAggregationService:
    """This class provides functions for consolidating energy data."""

    def __init__(
        self: Self,
        streetlamp_repo: Annotated[
            api.repositories.StreetlampRepository,
            fastapi.Depends(api.repositories.StreetlampRepository),
        ],
        streamst_repo: Annotated[
            api.repositories.StreamStateRepository,
            fastapi.Depends(api.repositories.StreamStateRepository),
        ],
        daily_state_repo: Annotated[
            api.repositories.DailyStreetlampStateRepository,
            fastapi.Depends(api.repositories.DailyStreetlampStateRepository),
        ],
        monthly_state_repo: Annotated[
            api.repositories.MonthlyStreetlampStateRepository,
            fastapi.Depends(api.repositories.MonthlyStreetlampStateRepository),
        ],
    ) -> None:
        """Initialize class properties."""
        self.streetlamp_repo = streetlamp_repo
        self.streamst_repo = streamst_repo
        self.daily_state_repo = daily_state_repo
        self.monthly_state_repo = monthly_state_repo

    async def _get_monthly_range(
        self: Self, strname: str, dev_eui: str
    ) -> _StreamDataRange | None:
        ss_str = await self.streamst_repo.find_by_name(strname)

        if ss_str is None or ss_str.producer_ts is None:
            return None

        if ss_str.consumer_ts is None:
            if odse := await self.daily_state_repo.find_oldest_by_dev_eui(
                dev_eui
            ):
                t0 = odse.day
            else:
                return None
        else:
            t0 = ss_str.consumer_ts
        t1 = ss_str.producer_ts

        if t0 == t1:
            return None

        return _StreamDataRange(
            api.utils.convert_to_default_tz(t0),
            api.utils.convert_to_default_tz(t1),
        )

    async def aggregate(self: Self) -> int:
        """Run monthly aggregation process."""
        tnm = 0
        for s in await self.streetlamp_repo.find_all():
            strname = f'streetlamp:state:monthly:{s.device_eui}'
            match await self._get_monthly_range(strname, s.device_eui):
                case None:
                    pass

                case _StreamDataRange(t0=t0, t1=t1):
                    nm = await self.monthly_state_repo.pull(
                        s.device_eui, t0, t1
                    )
                    api.log.logger.info(
                        'Stream [%s][%s -- %s]: %s rows(s) inserted',
                        strname,
                        t0,
                        t1,
                        nm,
                    )

                    await self.streamst_repo.update_consumer(strname, t1)
                    tnm += nm
        return tnm


class AccountService:
    """This class provides functions for managing accounts."""

    def __init__(
        self: Self,
        account_repo: Annotated[
            api.repositories.AccountRepository,
            fastapi.Depends(api.repositories.AccountRepository),
        ],
    ) -> None:
        """Initialize class properties."""
        self.account_repo = account_repo

    async def get(self: Self, aid: int) -> api.schemas.Account | None:
        """Get an account by ID."""
        a = await self.account_repo.find_by_id(aid)
        return api.schemas.Account.from_orm(a)


def energy_to_co2(energy: float) -> float:
    """Convert energy to CO2 metric tons."""
    etco2 = 6.99e-4
    return round(etco2 * (energy / 1000.0), 1)


class DashboardService:
    """This class provides functions for managing dashboards."""

    def __init__(  # noqa: PLR0913
        self: Self,
        streetlamp_repo: Annotated[
            api.repositories.StreetlampRepository,
            fastapi.Depends(api.repositories.StreetlampRepository),
        ],
        salarm_repo: Annotated[
            api.repositories.StreetlampAlarmRepository,
            fastapi.Depends(api.repositories.StreetlampAlarmRepository),
        ],
        hourly_state_repo: Annotated[
            api.repositories.HourlyStreetlampStateRepository,
            fastapi.Depends(api.repositories.HourlyStreetlampStateRepository),
        ],
        daily_state_repo: Annotated[
            api.repositories.DailyStreetlampStateRepository,
            fastapi.Depends(api.repositories.DailyStreetlampStateRepository),
        ],
        weekly_state_repo: Annotated[
            api.repositories.WeeklyStreetlampStateRepository,
            fastapi.Depends(api.repositories.WeeklyStreetlampStateRepository),
        ],
        monthly_state_repo: Annotated[
            api.repositories.MonthlyStreetlampStateRepository,
            fastapi.Depends(api.repositories.MonthlyStreetlampStateRepository),
        ],
    ) -> None:
        """Initialize class properties."""
        self.chirpstack_serv = _chirpstack_serv
        self.streetlamp_repo = streetlamp_repo
        self.salarm_repo = salarm_repo
        self.hourly_state_repo = hourly_state_repo
        self.daily_state_repo = daily_state_repo
        self.weekly_state_repo = weekly_state_repo
        self.monthly_state_repo = monthly_state_repo

    async def get(
        self: Self,
        cs_app_id: str,
        cs_streetlamp_dp_id: str,
    ) -> api.schemas.Dashboard:
        """Get dashboard."""
        today_summ = (
            api.schemas.StreetlampStateSummary.from_orm(today_summ_)
            if (
                today_summ_ := await self.hourly_state_repo.day_summary(
                    api.utils.today_midnight()
                )
            )
            is not None
            else None
        )

        yesterday_summ = (
            api.schemas.StreetlampStateSummary.from_orm(yesterday_summ_)
            if (
                yesterday_summ_ := await self.daily_state_repo.summary(
                    api.utils.yesterday_midnight()
                )
            )
            is not None
            else None
        )

        last_week_summ = (
            api.schemas.StreetlampStateSummary.from_orm(last_week_summ_)
            if (
                last_week_summ_ := await self.weekly_state_repo.summary(
                    api.utils.last_week()
                )
            )
            is not None
            else None
        )

        last_month_summ = (
            api.schemas.StreetlampStateSummary.from_orm(last_month_summ_)
            if (
                last_month_summ_ := await self.monthly_state_repo.summary(
                    api.utils.last_month()
                )
            )
            is not None
            else None
        )

        mtd_daily_summs = [
            api.schemas.StreetlampStatePointwiseSummary.from_orm(ss)
            for ss in await self.daily_state_repo.pointwise_summary(
                from_=api.utils.current_month(),
                to=api.utils.yesterday_midnight(),
            )
        ] + (
            []
            if today_summ is None
            else [
                api.schemas.StreetlampStatePointwiseSummary(
                    **(
                        today_summ.model_dump()
                        | {'ts': api.utils.today_midnight()}
                    )
                )
            ]
        )

        mtd_weekly_summs = [
            api.schemas.StreetlampStatePointwiseSummary.from_orm(ss)
            for ss in await self.weekly_state_repo.pointwise_summary(
                from_=api.utils.current_month(), to=api.utils.now()
            )
        ]

        ytd_montly_summs = [
            api.schemas.StreetlampStatePointwiseSummary.from_orm(ss)
            for ss in await self.monthly_state_repo.pointwise_summary(
                from_=api.utils.current_year(), to=api.utils.now()
            )
        ]

        return api.schemas.Dashboard(
            connectivity=await self._get_connectivity_summary(
                cs_app_id, cs_streetlamp_dp_id
            ),
            alarms=await self._get_alarms_summary(),
            life_span=await self._get_life_span_summary(),
            today_energy=await self._get_energy_summary(today_summ),
            yesterday_energy=await self._get_energy_summary(yesterday_summ),
            last_week_energy=await self._get_energy_summary(last_week_summ),
            last_month_energy=await self._get_energy_summary(last_month_summ),
            mtd_daily_energy=self._get_energy_to_date_summary(mtd_daily_summs),
            mtd_weekly_energy=self._get_energy_to_date_summary(
                mtd_weekly_summs
            ),
            ytd_monthly_energy=self._get_energy_to_date_summary(
                ytd_montly_summs
            ),
            geo_states=await self._get_geo_states(),
        )

    async def _get_connectivity_summary(
        self: Self, cs_app_id: str, cs_streetlamp_dp_id: str
    ) -> api.schemas.StreetlampsConnectivity:
        dp = self.chirpstack_serv.device_profile.read(cs_streetlamp_dp_id)
        if dp is None:
            return api.schemas.StreetlampsConnectivity(
                active=0,
                inactive=0,
                never_seen=0,
            )
        uli = dp.get('uplinkInterval', 0)
        dlr = self.chirpstack_serv.device.reads(cs_app_id, 0, 0)
        n = dlr.get('totalCount', 0)
        active = 0
        never_seen = 0
        inactive = 0
        for m in range(0, n, 100):
            dlr = self.chirpstack_serv.device.reads(cs_app_id, m, 100)
            for x in dlr['result']:
                if 'lastSeenAt' not in x:
                    never_seen += 1
                elif uli > 0:
                    lsa = dateutil.parser.parse(x['lastSeenAt']).astimezone(
                        pytz.UTC
                    )
                    t0 = lsa + datetime.timedelta(seconds=uli)
                    t1 = datetime.datetime.now(tz=pytz.UTC)
                    if t0 > t1:
                        active += 1
                    else:
                        inactive += 1
                else:
                    inactive += 1

        return api.schemas.StreetlampsConnectivity(
            active=active,
            inactive=inactive,
            never_seen=never_seen,
        )

    async def _get_alarms_summary(self: Self) -> api.schemas.StreetlampsAlarms:
        sas = await self.salarm_repo.summary()
        return api.schemas.StreetlampsAlarms(
            critical=sas.critical,
            major=sas.major,
            minor=sas.minor,
        )

    async def _get_life_span_summary(
        self: Self,
    ) -> api.schemas.StreetlampsLifeSpan:
        return api.schemas.StreetlampsLifeSpan(
            zero_ten=await self.streetlamp_repo.count(),
            fifty_seventy=0,
            seventy_ninety=0,
            ninety_one_hundred=0,
        )

    async def _get_geo_states(
        self: Self,
    ) -> list[api.schemas.StreetlampGeoState]:
        return [
            api.schemas.StreetlampGeoState(
                name=s.name, dev_eui=s.device_eui, lon=s.lon, lat=s.lat
            )
            for s in await self.streetlamp_repo.find_all(limit=None)
        ]

    async def _get_energy_summary(
        self: Self,
        summ: api.schemas.StreetlampStateSummary | None,
    ) -> api.schemas.StreetlampEnergySummary:
        return api.schemas.StreetlampEnergySummary(
            consumption=await self._get_energy_consumption_summary(summ),
            savings=await self._get_energy_savings_summary(summ),
            dimming_savings=await self._get_energy_dimming_savings_summary(
                summ
            ),
            co2_savings=await self._get_energy_co2_savings_summary(summ),
        )

    async def _get_energy_consumption_summary(
        self: Self,
        summ: api.schemas.StreetlampStateSummary | None,
    ) -> api.schemas.StreetlampsEnergyConsumption:
        if summ is None:
            return api.schemas.StreetlampsEnergyConsumption(
                total_in_kw=0.0,
                avg_in_watts=0.0,
            )
        total_in_kw = round(summ.energy_in / 1000, 2)
        avg_in_watts = round(
            summ.energy_in / summ.ndevices if summ.ndevices != 0 else 0.0, 2
        )
        return api.schemas.StreetlampsEnergyConsumption(
            total_in_kw=total_in_kw,
            avg_in_watts=avg_in_watts,
        )

    async def _get_energy_savings_summary(
        self: Self,
        summ: api.schemas.StreetlampStateSummary | None,
    ) -> api.schemas.StreetlampsEnergySavings:
        if summ is None:
            return api.schemas.StreetlampsEnergySavings(
                percentage=0.0,
                avg_in_watts=0.0,
            )
        total = 250 * (summ.on_time / 3600.0)
        savings = total - summ.energy_in
        percentage = round(100 * savings / total if total != 0 else 0.0, 1)
        avg_in_watts = round(
            savings / summ.ndevices if summ.ndevices != 0 else 0.0, 2
        )
        return api.schemas.StreetlampsEnergySavings(
            percentage=percentage,
            avg_in_watts=avg_in_watts,
        )

    async def _get_energy_dimming_savings_summary(
        self: Self,
        summ: api.schemas.StreetlampStateSummary | None,
    ) -> api.schemas.StreetlampsDimmingSavings:
        if summ is None:
            return api.schemas.StreetlampsDimmingSavings(
                percentage=0.0,
                avg_in_watts=0.0,
            )
        total = 90 * (summ.on_time / 3600.0)
        savings = total - summ.energy_in
        percentage = round(100 * savings / total if total != 0 else 0.0, 1)
        avg_in_watts = round(
            savings / summ.ndevices if summ.ndevices != 0 else 0.0, 2
        )
        return api.schemas.StreetlampsDimmingSavings(
            percentage=percentage,
            avg_in_watts=avg_in_watts,
        )

    async def _get_energy_co2_savings_summary(
        self: Self,
        summ: api.schemas.StreetlampStateSummary | None,
    ) -> api.schemas.StreetlampsCo2Savings:
        if summ is None:
            return api.schemas.StreetlampsCo2Savings(
                total_in_ton=0.0,
                avg_in_ton=0.0,
            )
        savings = 250 * (summ.on_time / 3600.0) - summ.energy_in
        return api.schemas.StreetlampsCo2Savings(
            total_in_ton=energy_to_co2(savings),
            avg_in_ton=energy_to_co2(
                savings / summ.ndevices if summ.ndevices != 0 else 0.0
            ),
        )

    def _get_energy_to_date_summary(
        self: Self,
        summs: list[api.schemas.StreetlampStatePointwiseSummary],
    ) -> list[api.schemas.StreetlampEnergyPoint]:
        return [
            api.schemas.StreetlampEnergyPoint(
                ts=summ.ts,
                consumption=round(summ.energy_in / 1000, 2),
                savings=round(
                    (250 * (summ.on_time / 3600.0) - summ.energy_in) / 1000, 2
                ),
                dimming_savings=round(
                    (90 * (summ.on_time / 3600.0) - summ.energy_in) / 1000, 2
                ),
                co2_savings=energy_to_co2(
                    round(
                        (250 * (summ.on_time / 3600.0) - summ.energy_in) / 1000,
                        2,
                    )
                ),
            )
            for summ in summs
        ]


class SeedService:
    """This class provides functions for creating the initial DB state."""

    def __init__(  # noqa: PLR0913
        self: Self,
        settings: api.config.Settings,
        account_repo: api.repositories.AccountRepository,
        user_repo: api.repositories.UserRepository,
        dimming_profile_repo: api.repositories.DimmingProfileRepository,
        dimming_event_repo: api.repositories.DimmingEventRepository,
    ) -> None:
        """Initialize class properties."""
        self.settings = settings
        self.chirpstack_serv = _chirpstack_serv
        self.account_repo = account_repo
        self.user_repo = user_repo
        self.dimming_profile_repo = dimming_profile_repo
        self.dimming_event_repo = dimming_event_repo

    async def sow(self: Self) -> None:
        """Create initial entities."""
        cs = self.chirpstack_serv.get_current_state()
        while cs != ChirpStackState.READY:
            api.log.logger.error(f'Invalid ChirpStack state : {cs}')
            await asyncio.sleep(30)
            cs = self.chirpstack_serv.get_current_state()

        if a := await self._create_netolight_account():
            await self._create_netolight_admin_user(a.id)
            await self._create_default_dprofile(a.cs_application_id, a.id)

    async def _read_or_create_tenant(
        self: Self, tenant_id: str | None = None
    ) -> dict | None:
        if (
            tenant_id
            and (t := self.chirpstack_serv.tenant.read(tenant_id)) is not None
        ):
            return t

        r = self.chirpstack_serv.tenant.create(
            name='NetoLight', description='NetoLight default tenant'
        )
        return self.chirpstack_serv.tenant.read(r['id'])

    async def _read_or_create_app(
        self: Self, tenant_id: str, app_id: str | None = None
    ) -> dict | None:
        if (
            app_id
            and (a := self.chirpstack_serv.application.read(app_id)) is not None
        ):
            return a

        r = self.chirpstack_serv.application.create(
            tenant_id=tenant_id,
            name='NetoLight',
            description='NetoLight default app',
        )
        return self.chirpstack_serv.application.read(r['id'])

    async def _read_or_create_streetlamp_dp(
        self: Self, tenant_id: str, dev_prof_id: str | None = None
    ) -> dict | None:
        if dev_prof_id and (
            d := self.chirpstack_serv.device_profile.read(dev_prof_id)
        ):
            return d

        r = self.chirpstack_serv.device_profile.create(
            tenant_id=tenant_id,
            name='NetoLightLamp',
            description='NetoLight default streetlamp device profile',
            region=2,
            mac_version=3,
            reg_params_revision=1,
            adr_algorithm_id='Default ADR algorithm (LoRa only)',
        )
        return self.chirpstack_serv.device_profile.read(r['id'])

    async def _read_or_create_streetlamp_multicast_group(
        self: Self, app_id: str
    ) -> dict | None:
        name = 'Default'
        if mg := self.chirpstack_serv.multicast_group.read_by_name(
            app_id, name
        ):
            return mg

        r = self.chirpstack_serv.multicast_group.create(
            app_id=app_id,
            name=name,
        )
        return self.chirpstack_serv.multicast_group.read(r['id'])

    async def _read_or_create_http_integration(
        self: Self, app_id: str, event_endpoint_url: str
    ) -> dict:
        i = self.chirpstack_serv.application.get_http_integration(app_id)
        if i is None:
            return self.chirpstack_serv.application.create_http_integration(
                app_id=app_id, encoding=0, event_endpoint_url=event_endpoint_url
            )
        return i

    async def _create_netolight_account(
        self: Self,
    ) -> api.models.Account | None:
        """Create the NetoLight account."""
        url = f'{self.settings.NL_API_URL}/api/streetlamp_states'
        if (
            (acc := await self.account_repo.find_by_name('NetoLight'))
            and acc.id is not None
            and (
                (tenant := await self._read_or_create_tenant(acc.cs_tenant_id))
                and (
                    app := await self._read_or_create_app(
                        tenant['id'], acc.cs_application_id
                    )
                )
                and (
                    dev_prof := await self._read_or_create_streetlamp_dp(
                        tenant['id'], acc.cs_streetlamp_dp_id
                    )
                )
            )
        ):
            await self._read_or_create_http_integration(app['id'], url)
            await self.account_repo.update(
                api.models.Account(
                    name=acc.name,
                    cs_tenant_id=tenant['id'],
                    cs_application_id=app['id'],
                    cs_streetlamp_dp_id=dev_prof['id'],
                ),
            )
            return await self.account_repo.find_by_id(acc.id)
        if (
            (tenant := await self._read_or_create_tenant())
            and (app := await self._read_or_create_app(tenant['id']))
            and (
                dev_prof := await self._read_or_create_streetlamp_dp(
                    tenant['id']
                )
            )
        ):
            await self._read_or_create_http_integration(app['id'], url)
            a = api.models.Account(
                name='NetoLight',
                cs_tenant_id=tenant['id'],
                cs_application_id=app['id'],
                cs_streetlamp_dp_id=dev_prof['id'],
            )
            if aid := await self.account_repo.insert(a):
                return await self.account_repo.find_by_id(aid)
        return None

    async def _create_netolight_admin_user(self: Self, aid: int) -> None:
        """Create an admin user."""
        user = await self.user_repo.find_by_email('admin@netolight.com')
        if user is None:
            u = api.models.User(
                account_id=aid,
                email='admin@netolight.com',
                hashed_password=_pwd_context.hash('1234'),
                first_name='Admin',
                last_name='Admin',
                role='super-admin',
            )
            await self.user_repo.insert(u)

    async def _create_default_dprofile(
        self: Self, cs_app_id: str, aid: int
    ) -> None:
        """Create default dimming profile."""
        dp = await self.dimming_profile_repo.find_by_name('Default')
        if dp is not None:
            return

        mg = await self._read_or_create_streetlamp_multicast_group(cs_app_id)
        if mg is None:
            errmsg = 'Failed to create multicast group'
            raise ValueError(errmsg)

        dp_serv = DimmingProfileService(
            self.settings, self.dimming_profile_repo, self.dimming_event_repo
        )
        await dp_serv.create(
            api.schemas.DimmingProfileCreate(
                account_id=aid,
                multicast_group_id=mg['id'],
                active=True,
                name='Default',
                description='NetoLight default dimming profile',
                color='#00bfff',
                sunset_dim_cmd0=api.models.DimmingCommand.TURN_ON,  # type: ignore[attr-defined]
                sunset_dim_cmd1=api.models.DimmingCommand.DIM_100,  # type: ignore[attr-defined]
                h2000_dim_cmd=api.models.DimmingCommand.DIM_80,  # type: ignore[attr-defined]
                h2200_dim_cmd=api.models.DimmingCommand.DIM_70,  # type: ignore[attr-defined]
                h0000_dim_cmd=api.models.DimmingCommand.DIM_60,  # type: ignore[attr-defined]
                h0200_dim_cmd=api.models.DimmingCommand.DIM_50,  # type: ignore[attr-defined]
                h0400_dim_cmd=api.models.DimmingCommand.DIM_40,  # type: ignore[attr-defined]
                sunrise_dim_cmd0=api.models.DimmingCommand.DIM_00,  # type: ignore[attr-defined]
                sunrise_dim_cmd1=api.models.DimmingCommand.TURN_OFF,  # type: ignore[attr-defined]
            )
        )
