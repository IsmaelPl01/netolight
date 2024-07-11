"""This module provides the schemas."""

import datetime
from typing import Literal

import pydantic
import pydantic.alias_generators

import api.models


class AccountCreate(pydantic.BaseModel):
    """This class represents a request to create an account."""

    name: str
    nl_api_url: str


class AccountUpdate(pydantic.BaseModel):
    """This class represents a request to update an account."""

    name: str
    cs_tenant_id: str | None
    cs_application_id: str | None
    cs_streetlamp_dp_id: str | None


class Account(pydantic.BaseModel):
    """This class represents an account."""

    id: int
    name: str
    is_active: bool
    cs_tenant_id: str
    cs_application_id: str
    cs_streetlamp_dp_id: str

    model_config = pydantic.ConfigDict(from_attributes=True)


class AccountList(pydantic.BaseModel):
    """This class represents a sublist of the accounts."""

    total: int
    data: list[Account]


class UserBase(pydantic.BaseModel):
    """Base class for users."""

    account_id: int
    first_name: str
    last_name: str
    email: pydantic.EmailStr
    role: Literal['super-admin', 'admin', 'user'] = 'user'


class UserCreate(UserBase):
    """This class represents a request to create an user."""

    password: str


class UserUpdate(UserBase):
    """This class represents a request to update an user."""


class User(UserBase):
    """This class represents an user."""

    id: int
    is_active: bool


class UserList(pydantic.BaseModel):
    """This class represents a sublist of users."""

    total: int
    data: list[User]


class Token(pydantic.BaseModel):
    """This class represents a session token."""

    access_token: str
    token_type: str


class ChirpStackEntityCreated(pydantic.BaseModel):
    """This class represents a ChirpStackEntityCreated event."""

    id: int


class ChirpStackError(pydantic.BaseModel):
    """This class represents a ChirpStack error."""

    error: str
    code: int
    message: str
    details: list[str]


class ChirpStackTenantCreate(pydantic.BaseModel):
    """This class represents a request to create ChirpStack tenant."""

    name: str
    display_name: str


class ChirpStackTenant(pydantic.BaseModel):
    """This class represents a ChirpStack tenant."""

    id: int
    name: str
    display_name: str


class ChirpStackTenantSearchResult(pydantic.BaseModel):
    """This class represents the result of a ChirpStack tenant search."""

    total_count: int
    result: list[ChirpStackTenant]


class DimmingEventBase(pydantic.BaseModel):
    """Base class for dimming events."""

    account_id: int
    dimming_profile_id: int
    target_id: str
    target_type: api.models.TargetType
    command: api.models.DimmingCommand
    start: datetime.datetime
    end: datetime.datetime
    color: str
    text_color: str


class DimmingEventCreate(DimmingEventBase):
    """This class represents a request to create a dimming event."""


class DimmingEventUpdate(DimmingEventBase):
    """This class represents a request to update a dimming event."""


class DimmingEvent(DimmingEventBase):
    """This class represents a dimming event."""

    id: int

    model_config = pydantic.ConfigDict(from_attributes=True)


class DimmingEventList(pydantic.BaseModel):
    """This class represents a sublist of dimming events."""

    total: int
    data: list[DimmingEvent]


class DimmingProfileBase(pydantic.BaseModel):
    """Base class for dimming profiles."""

    account_id: int
    multicast_group_id: str
    active: bool
    name: str
    description: str
    color: str
    sunset_dim_cmd0: api.models.DimmingCommand
    sunset_dim_cmd1: api.models.DimmingCommand
    h2000_dim_cmd: api.models.DimmingCommand
    h2200_dim_cmd: api.models.DimmingCommand
    h0000_dim_cmd: api.models.DimmingCommand
    h0200_dim_cmd: api.models.DimmingCommand
    h0400_dim_cmd: api.models.DimmingCommand
    sunrise_dim_cmd0: api.models.DimmingCommand
    sunrise_dim_cmd1: api.models.DimmingCommand


class DimmingProfileCreate(DimmingProfileBase):
    """This class represents a request to create a dimming profile."""


class DimmingProfileUpdate(DimmingProfileBase):
    """This class represents a request to update a dimming profile."""


class DimmingProfile(DimmingProfileBase):
    """This class represents a dimming profile."""

    id: int

    model_config = pydantic.ConfigDict(from_attributes=True)


class DimmingProfileList(pydantic.BaseModel):
    """This class represents a sublist of dimming profiles."""

    total: int
    data: list[DimmingProfile]


class GatewayBase(pydantic.BaseModel):
    """Base class for gateways."""

    id: str
    name: str
    description: str | None
    region_id: str | None = None
    region_common_name: str | None = None


class GatewayCreate(GatewayBase):
    """This class represents a request to create a gateway."""


class GatewayUpdate(GatewayBase):
    """This class represents a request to update a gateway."""
    name: str
    description: str | None = None


class Gateway(GatewayBase):
    """This class represents a gateway."""

    last_seen: datetime.datetime | None
    state: str


class GatewayList(pydantic.BaseModel):
    """This class represents a sublist of gateways."""

    total: int
    data: list[Gateway]


class StreamState(pydantic.BaseModel):
    """This class represents the state of a stream."""

    id: int
    name: str
    producer_ts: datetime.datetime | None
    consumer_ts: datetime.datetime | None

    model_config = pydantic.ConfigDict(from_attributes=True)


class StreetlampBase(pydantic.BaseModel):
    """This class represents the common properties of a streetlamp."""

    account_id: int
    device_eui: str
    name: str
    lon: float | None = None
    lat: float | None = None


class StreetlampCreate(StreetlampBase):
    """This class represents a request to create a streetlamp."""

    app_key: str


class StreetlampUpdate(StreetlampBase):
    """This class represents a request to update a streetlamp."""


class Streetlamp(StreetlampBase):
    """This class represents a streetlamp."""

    id: int

    model_config = pydantic.ConfigDict(from_attributes=True)


class StreetlampList(pydantic.BaseModel):
    """This class represents a sublist of streetlamps."""

    total: int
    data: list[Streetlamp]


class StreetlampInfo(pydantic.BaseModel):
    """This class represents the ChirpStack-related info of a streetlamp."""

    tenant_id: str
    tenant_name: str
    application_id: str
    application_name: str
    device_profile_id: str
    device_profile_name: str
    device_name: str
    dev_eui: str

    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.AliasGenerator(
            validation_alias=pydantic.alias_generators.to_camel
        )
    )


class StreetlampStateCreate(pydantic.BaseModel):
    """This class represents a request to create streetlamp state."""

    deduplication_id: str
    time: datetime.datetime
    device_info: StreetlampInfo
    dev_addr: str
    data: str

    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.AliasGenerator(
            validation_alias=pydantic.alias_generators.to_camel
        )
    )


class StreetlampDeviceState(pydantic.BaseModel):
    """This class represents a streetlamp device state."""

    voltage: float
    current: float
    energy_out: float
    energy_in: float
    power: float
    frequency: float
    status_on: bool


class StreetlampState(pydantic.BaseModel):
    """This class represents a streetlamp state."""

    id: int
    time: datetime.datetime
    tenant_id: str
    tenant_name: str
    application_id: str
    application_name: str
    device_profile_id: str
    device_profile_name: str
    device_name: str
    dev_eui: str
    dev_addr: str
    dev_voltage: float
    dev_current: float
    dev_energy_out: float
    dev_energy_in: float
    dev_power: float
    dev_frequency: float
    dev_status_on: bool


class StreetlampStateList(pydantic.BaseModel):
    """This class represents a sublist of streetlamp states."""

    total: int
    data: list[StreetlampState]


class StreetlampStateSummary(pydantic.BaseModel):
    """This class represents a streetlamp state."""

    ndevices: int
    voltage: float
    current: float
    energy_out: float
    energy_in: float
    power: float
    frequency: float
    on_time: float

    model_config = pydantic.ConfigDict(from_attributes=True)


class StreetlampStatePointwiseSummary(StreetlampStateSummary):
    """This class represents a streetlamp state worth a day."""

    ts: datetime.datetime


class StreetlampsConnectivity(pydantic.BaseModel):
    """This class represents the connectivity summary."""

    active: int
    inactive: int
    never_seen: int


class StreetlampsAlarms(pydantic.BaseModel):
    """This class represents the alarms summary ."""

    critical: int
    major: int
    minor: int


class StreetlampsLifeSpan(pydantic.BaseModel):
    """This class represents the alarms summary ."""

    zero_ten: int
    fifty_seventy: int
    seventy_ninety: int
    ninety_one_hundred: int


class StreetlampsEnergyConsumption(pydantic.BaseModel):
    """This class represents the energy consumption summary ."""

    total_in_kw: float
    avg_in_watts: float


class StreetlampsEnergySavings(pydantic.BaseModel):
    """This class represents the energy savings summary ."""

    percentage: float
    avg_in_watts: float


class StreetlampsDimmingSavings(pydantic.BaseModel):
    """This class represents the dimming savings summary ."""

    percentage: float
    avg_in_watts: float


class StreetlampsCo2Savings(pydantic.BaseModel):
    """This class represents the dimming savings summary ."""

    total_in_ton: float
    avg_in_ton: float


class StreetlampEnergySummary(pydantic.BaseModel):
    """This class represents the state summary ."""

    consumption: StreetlampsEnergyConsumption
    savings: StreetlampsEnergySavings
    dimming_savings: StreetlampsDimmingSavings
    co2_savings: StreetlampsCo2Savings


class StreetlampEnergyPoint(pydantic.BaseModel):
    """This class represents the state summary ."""

    ts: datetime.datetime
    consumption: float
    savings: float
    dimming_savings: float
    co2_savings: float


class StreetlampGeoState(pydantic.BaseModel):
    """This class represents the state summary ."""

    name: str
    dev_eui: str
    lon: float | None
    lat: float | None


class DeviceCommand(pydantic.BaseModel):
    """This class represents a device command."""

    command: str


class Dashboard(pydantic.BaseModel):
    """This class represents a dashboard."""

    connectivity: StreetlampsConnectivity
    alarms: StreetlampsAlarms
    life_span: StreetlampsLifeSpan
    today_energy: StreetlampEnergySummary
    yesterday_energy: StreetlampEnergySummary
    last_week_energy: StreetlampEnergySummary
    last_month_energy: StreetlampEnergySummary
    mtd_daily_energy: list[StreetlampEnergyPoint]
    mtd_weekly_energy: list[StreetlampEnergyPoint]
    ytd_monthly_energy: list[StreetlampEnergyPoint]
    geo_states: list[StreetlampGeoState]
