"""This module provides the routers."""

import datetime
from typing import Annotated

import fastapi
import fastapi.security
import sqlalchemy.exc

import api.log
import api.schemas
import api.services 

tokens = fastapi.APIRouter(
    prefix='/token',
    tags=['auth'],
    responses={404: {'description': 'Not found'}},
)


@tokens.post('')
async def token(
    form_data: Annotated[
        fastapi.security.OAuth2PasswordRequestForm, fastapi.Depends()
    ],
    auth_serv: Annotated[
        api.services.AuthService, fastapi.Depends(api.services.AuthService)
    ],
    settings: Annotated[
        api.config.Settings, fastapi.Depends(api.config.get_settings)
    ],
) -> api.schemas.Token:
    """Get token."""
    user = await auth_serv.authenticate(form_data.username, form_data.password)
    if user is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = auth_serv.create_access_token(
        data={'sub': user.email},
        expires_delta=datetime.timedelta(
            minutes=settings.NL_API_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )
    return api.schemas.Token(access_token=access_token, token_type='bearer')  # noqa: S106


users = fastapi.APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {'description': 'User not found'}},
)


@users.get('/me')
async def me(
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
) -> api.schemas.User | None:
    """Get current user."""
    return current_user


@users.post('')
async def create_user(
    user: api.schemas.UserCreate,
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    user_serv: Annotated[
        api.services.UserService, fastapi.Depends(api.services.UserService)
    ],
    account_serv: Annotated[
        api.services.AccountService, fastapi.Depends(api.services.AccountService)
    ]
) -> int | None:
    """Create a new user."""
    if current_user.role != 'super-admin' and current_user.role != 'admin':
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    # Verificar que el account_id existe
    account = await account_serv.get(user.account_id)
    if account is None:
        raise fastapi.HTTPException(
            status_code=400,
            detail="Invalid account_id"
        )

    return await user_serv.create(current_user, user)

accounts = fastapi.APIRouter(
    prefix='/accounts',
    tags=['accounts'],
    responses={404: {'description': 'Account not found'}},
)


@accounts.get('/mine')
async def mine(
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    account_serv: Annotated[
        api.services.AccountService,
        fastapi.Depends(api.services.AccountService),
    ],
) -> api.schemas.Account | None:
    """Get my account."""
    if a := await account_serv.get(current_user.account_id):
        return a
    raise fastapi.HTTPException(
        status_code=404, detail=f'Account {current_user.account_id} not found'
    )


devices = fastapi.APIRouter(
    prefix='/devices',
    tags=['devices'],
    responses={404: {'description': 'Device not found'}},
)


@devices.get('')
async def get_devices(
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    account_serv: Annotated[
        api.services.AccountService,
        fastapi.Depends(api.services.AccountService),
    ],
    streetlamp_device_serv: Annotated[
        api.services.StreetlampDeviceService,
        fastapi.Depends(api.services.StreetlampDeviceService),
    ],
    skip: int | None = 0,
    limit: int | None = 4,
) -> dict:
    """Get a sublist of devices."""
    if a := await account_serv.get(current_user.account_id):
        return await streetlamp_device_serv.get_sublist(
            a.cs_application_id, skip or 0, limit or 4
        )
    return {'total': 0, 'result': []}


@devices.get('/available')
async def get_devices_available(
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    account_serv: Annotated[
        api.services.AccountService,
        fastapi.Depends(api.services.AccountService),
    ],
    streetlamp_device_serv: Annotated[
        api.services.StreetlampDeviceService,
        fastapi.Depends(api.services.StreetlampDeviceService),
    ],
) -> list[str]:
    """Get the EUI of the available devices."""
    if a := await account_serv.get(current_user.account_id):
        return await streetlamp_device_serv.get_available(a.cs_application_id)
    return []


@devices.put('/{dev_eui}/send_command')
async def send_command(
    dev_eui: str,
    command: api.schemas.DeviceCommand,
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    streetlamp_device_serv: Annotated[
        api.services.StreetlampDeviceService,
        fastapi.Depends(api.services.StreetlampDeviceService),
    ],
) -> None:
    """Send command."""
    if current_user.role == 'super-admin':
        match command.command.lower().split('_'):
            case ['turn', 'on']:
                streetlamp_device_serv.turn_on(dev_eui)
            case ['turn', 'off']:
                streetlamp_device_serv.turn_off(dev_eui)
            case ['dim', val]:
                streetlamp_device_serv.dim(dev_eui, int(val))
    else:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN
        )


@devices.put('/{dev_eui}/send_raw_command')
async def send_raw_command(
    dev_eui: str,
    command: api.schemas.DeviceCommand,
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    streetlamp_device_serv: Annotated[
        api.services.StreetlampDeviceService,
        fastapi.Depends(api.services.StreetlampDeviceService),
    ],
) -> None:
    """Send raw command."""
    if current_user.role == 'super-admin':
        streetlamp_device_serv.enqueue_command(
            dev_eui, command.command.encode('utf-8')
        )
    else:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN
        )


dimming_events = fastapi.APIRouter(
    prefix='/dimming_events',
    tags=['dimming events'],
    responses={404: {'description': 'DimmingEvent not found'}},
)


@dimming_events.get('/')
async def get_dimming_events(
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.DimmingEventService,
        fastapi.Depends(api.services.DimmingEventService),
    ],
    skip: int | None = 0,
    limit: int | None = None,
) -> api.schemas.DimmingEventList:
    """Get a sublist of dimming events."""
    return await serv.get_sublist(skip or 0, limit)


@dimming_events.get('/{deid}')
async def get_dimming_event(
    deid: int,
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.DimmingEventService,
        fastapi.Depends(api.services.DimmingEventService),
    ],
) -> api.schemas.DimmingEvent | None:
    """Get a dimming event by ID."""
    return await serv.get_one(deid)


dimming_profiles = fastapi.APIRouter(
    prefix='/dimming_profiles',
    tags=['dimming profiles'],
    responses={404: {'description': 'DimmingProfile not found'}},
)


@dimming_profiles.get('/')
async def get_dimming_profiles(
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.DimmingProfileService,
        fastapi.Depends(api.services.DimmingProfileService),
    ],
    skip: int | None = 0,
    limit: int | None = 4,
) -> api.schemas.DimmingProfileList:
    """Get a sublist of dimming profiles."""
    return await serv.get_sublist(skip or 0, limit or 4)


@dimming_profiles.post('/')
async def create_dimming_profile(
    dpc: api.schemas.DimmingProfileCreate,
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.DimmingProfileService,
        fastapi.Depends(api.services.DimmingProfileService),
    ],
) -> dict:
    """Create a dimming profile."""
    try:
        return {'id': await serv.create(dpc)}
    except sqlalchemy.exc.IntegrityError as e:
        raise fastapi.HTTPException(
            status_code=422,
            detail=[
                {
                    'loc': ['name'],
                    'msg': f'DimmingProfile `{dpc.name}` already exist',
                }
            ],
        ) from e


@dimming_profiles.get('/{dpid}')
async def get_dimming_profile(
    dpid: int,
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.DimmingProfileService,
        fastapi.Depends(api.services.DimmingProfileService),
    ],
) -> api.schemas.DimmingProfile | None:
    """Get a dimming profile by ID."""
    return await serv.get_one(dpid)


@dimming_profiles.put('/{dpid}')
async def update_dimming_profile(
    dpid: int,
    dpu: api.schemas.DimmingProfileUpdate,
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.DimmingProfileService,
        fastapi.Depends(api.services.DimmingProfileService),
    ],
) -> dict:
    """Delete a dimming profile by ID."""
    try:
        return {'updated': await serv.update(dpid, dpu)}
    except sqlalchemy.exc.IntegrityError as e:
        raise fastapi.HTTPException(
            status_code=422,
            detail=[
                {
                    'loc': ['name'],
                    'msg': f'DimmingProfile `{dpu.name}` already exist',
                }
            ],
        ) from e


@dimming_profiles.delete('/{dpid}')
async def delete_dimming_profile(
    dpid: int,
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.DimmingProfileService,
        fastapi.Depends(api.services.DimmingProfileService),
    ],
) -> dict:
    """Delete a dimming profile by ID."""
    return {'deleted': await serv.delete_one(dpid)}


gateways = fastapi.APIRouter(
    prefix='/gateways',
    tags=['gateways'],
    responses={404: {'description': 'Gateway not found'}},
)


@gateways.get('')
async def get_gateways(
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    gateway_serv: Annotated[
        api.services.GatewayService,
        fastapi.Depends(api.services.GatewayService),
    ],
    skip: int | None = 0,
    limit: int | None = 4,
) -> api.schemas.GatewayList:
    """Get a sublist of gateways."""
    r = gateway_serv.reads(skip or 0, limit or 4)
    gs = [_gateway_from_cs(g) for g in r.get('result', [])]
    return api.schemas.GatewayList(total=r.get('totalCount', 0), data=gs)


@gateways.post('')
async def create_gateway(
    gateway: api.schemas.GatewayCreate,
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    account_serv: Annotated[
        api.services.AccountService,
        fastapi.Depends(api.services.AccountService),
    ],
    gateway_serv: Annotated[
        api.services.GatewayService,
        fastapi.Depends(api.services.GatewayService),
    ],
) -> dict:
    """Create a gateway."""
    if a := await account_serv.get(current_user.account_id):
        return {
            'id': gateway_serv.create(
                a.cs_tenant_id, gateway.id, gateway.name, gateway.description
            )
        }
    return {'id': None}


@gateways.get('/{gid}')
async def get_gateway(
    gid: str,
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    gateway_serv: Annotated[
        api.services.GatewayService,
        fastapi.Depends(api.services.GatewayService),
    ],
) -> api.schemas.Gateway | None:
    """Get a gateway by ID."""
    r = gateway_serv.read(gid)
    if r is not None and 'gateway' in r and r['gateway'] is not None:
        return _gateway_from_cs(r['gateway'])
    return None




def _gateway_from_cs(g: dict) -> api.schemas.Gateway:
    return api.schemas.Gateway(
        last_seen=g.get('lastSeenAt'),
        state=g.get('state', ''),
        id=g['gatewayId'],
        name=g['name'],
        description=g.get('description'),
        region_id=g.get('regionId'),
        region_common_name=g.get('regionCommonName'),
    )

@gateways.put('/{gid}')
async def update_gateway(
    gid: str,
    gateway: api.schemas.GatewayUpdate,
    current_user: Annotated[
        api.schemas.User, fastapi.Depends(api.services.AuthService.get_current_user)
    ],
    account_serv: Annotated[
        api.services.AccountService, fastapi.Depends(api.services.AccountService)
    ],
    gateway_serv: Annotated[
        api.services.GatewayService, fastapi.Depends(api.services.GatewayService)
    ],
) -> dict:
    """Update a gateway."""
    if a := await account_serv.get(current_user.account_id):
        return {
            'id': gateway_serv.update(
                a.cs_tenant_id, gid, gateway.name, gateway.description
            )
        }
    return {'id': None} 

@gateways.delete('/{gid}')
async def delete_gateway(
    gid: str,
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    gateway_serv: Annotated[
        api.services.GatewayService,
        fastapi.Depends(api.services.GatewayService),
    ],
) -> dict:
    """Delete a gateway."""
    gateway_serv.delete(gid)
    return {'deleted': gid}


streetlamp_states = fastapi.APIRouter(
    prefix='/streetlamp_states', tags=['streetlamp states']
)


@streetlamp_states.post('')
async def create_streetlamp_state(
    req: fastapi.Request,
    event: str,
    serv: Annotated[
        api.services.StreetlampStateService,
        fastapi.Depends(api.services.StreetlampStateService),
    ],
) -> None:
    """Create a streetlamp state."""
    if event == 'up':
        await serv.enqueue_create(await req.body())


@streetlamp_states.get('/latest')
async def get_latest_streetlamp_state(
    dev_eui: str,
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.StreetlampStateService,
        fastapi.Depends(api.services.StreetlampStateService),
    ],
) -> api.schemas.StreetlampState | None:
    """Get latest streetlamp state."""
    if current_user.role == 'super-admin':
        return await serv.find_latest(dev_eui)
    raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN)


streetlamps = fastapi.APIRouter(
    prefix='/streetlamps',
    tags=['streetlamps'],
)


@streetlamps.post('')
async def create_streetlamp(
    sc: api.schemas.StreetlampCreate,
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    account_serv: Annotated[
        api.services.AccountService,
        fastapi.Depends(api.services.AccountService),
    ],
    serv: Annotated[
        api.services.StreetlampService,
        fastapi.Depends(api.services.StreetlampService),
    ],
) -> int | None:
    """Create streetlamp."""
    if a := await account_serv.get(current_user.account_id):
        return await serv.create(sc, a.cs_application_id, a.cs_streetlamp_dp_id)
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Account not found',
    )


@streetlamps.put('/{sid}')
async def update_streetlamp(
    sid: int,
    su: api.schemas.StreetlampUpdate,
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.StreetlampService,
        fastapi.Depends(api.services.StreetlampService),
    ],
) -> dict:
    """Create streetlamp."""
    if current_user.role == 'super-admin':
        return {'updated': await serv.update(sid, su)}
    raise fastapi.HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN)


@streetlamps.post('/file')
async def create_streetlamps(
    file: fastapi.UploadFile,
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    account_serv: Annotated[
        api.services.AccountService,
        fastapi.Depends(api.services.AccountService),
    ],
    serv: Annotated[
        api.services.StreetlampService,
        fastapi.Depends(api.services.StreetlampService),
    ],
) -> dict:
    """Create streetlamps from a CSV file."""
    if a := await account_serv.get(current_user.account_id):
        es = await serv.creates(
            file, a.id, a.cs_application_id, a.cs_streetlamp_dp_id
        )
        return {'errors': es}
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Account not found',
    )


@streetlamps.delete('/{sid}')
async def delete_streetlamp(
    sid: int,
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.StreetlampService,
        fastapi.Depends(api.services.StreetlampService),
    ],
) -> dict:
    """Delete a streetlamp by ID."""
    return {'deleted': await serv.delete_by_id(sid)}


@streetlamps.get('')
async def get_streetlamps(
    current_user: Annotated[  # noqa: ARG001
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    serv: Annotated[
        api.services.StreetlampService,
        fastapi.Depends(api.services.StreetlampService),
    ],
    skip: int | None = 0,
    limit: int | None = 4,
) -> api.schemas.StreetlampList:
    """Get streetlamps."""
    return await serv.get_sublist(skip or 0, limit or 4)


dashboards = fastapi.APIRouter(
    prefix='/dashboards',
    tags=['dashboards'],
)


@dashboards.get('/me')
async def get_dashboards(
    current_user: Annotated[
        api.schemas.User,
        fastapi.Depends(api.services.AuthService.get_current_user),
    ],
    account_serv: Annotated[
        api.services.AccountService,
        fastapi.Depends(api.services.AccountService),
    ],
    dashboard_serv: Annotated[
        api.services.DashboardService,
        fastapi.Depends(api.services.DashboardService),
    ],
) -> api.schemas.Dashboard | None:
    """Get dashboard."""
    if a := await account_serv.get(current_user.account_id):
        return await dashboard_serv.get(
            a.cs_application_id, a.cs_streetlamp_dp_id
        )
    return None
