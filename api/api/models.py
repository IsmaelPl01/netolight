"""This module provides domain model."""

import datetime
import enum

import sqlalchemy as sa
from sqlalchemy.orm import (  # type: ignore[attr-defined]
    Mapped,
    mapped_column,
    relationship,
)

import api.postgres


class Account(api.postgres.Base):
    """This class represents the table accounts."""

    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    cs_tenant_id: Mapped[str] = mapped_column(nullable=False)
    cs_application_id: Mapped[str] = mapped_column(nullable=False)
    cs_streetlamp_dp_id: Mapped[str] = mapped_column(nullable=False)


class User(api.postgres.Base):
    """This class represents the table users."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('accounts.id')
    )
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    role: Mapped[str]

    account = relationship('Account', foreign_keys=[account_id])


DimmingCommand = enum.StrEnum(  # type: ignore[misc]
    'DimmingCommand',
    ['TURN_ON', 'TURN_OFF'] + [f'DIM_{n:02}' for n in range(101)],
)


class DimmingProfile(api.postgres.Base):
    """This class represents the table dimming profiles."""

    __tablename__ = 'dimming_profiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('accounts.id')
    )
    multicast_group_id: Mapped[str]
    active: Mapped[bool]
    name: Mapped[str]
    description: Mapped[str]
    color: Mapped[str]
    sunset_dim_cmd0: Mapped[DimmingCommand]
    sunset_dim_cmd1: Mapped[DimmingCommand]
    h2000_dim_cmd: Mapped[DimmingCommand]
    h2200_dim_cmd: Mapped[DimmingCommand]
    h0000_dim_cmd: Mapped[DimmingCommand]
    h0200_dim_cmd: Mapped[DimmingCommand]
    h0400_dim_cmd: Mapped[DimmingCommand]
    sunrise_dim_cmd0: Mapped[DimmingCommand]
    sunrise_dim_cmd1: Mapped[DimmingCommand]

    account = relationship('Account', foreign_keys=[account_id])


TargetType = enum.StrEnum('TargetType', ['DEVICE', 'DEVICE_GROUP'])


class DimmingEvent(api.postgres.Base):
    """This class represents the table dimming events."""

    __tablename__ = 'dimming_events'

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('accounts.id')
    )
    dimming_profile_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('dimming_profiles.id')
    )
    job_id: Mapped[str]
    target_id: Mapped[str]
    target_type: Mapped[TargetType]
    command: Mapped[DimmingCommand]
    start: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))
    end: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))
    color: Mapped[str]
    text_color: Mapped[str]

    account = relationship('Account', foreign_keys=[account_id])


class Streetlamp(api.postgres.Base):
    """This class represents the table streetlamps."""

    __tablename__ = 'streetlamps'

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey('accounts.id')
    )
    device_eui: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    lon: Mapped[float | None]
    lat: Mapped[float | None]

    account = relationship('Account', foreign_keys=[account_id])


class StreetlampState(api.postgres.Base):
    """This class represents the table streetlamp_states."""

    __tablename__ = 'streetlamp_states'
    id: Mapped[int] = mapped_column(primary_key=True)
    deduplication_id: Mapped[str]
    time: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), index=True
    )
    tenant_id: Mapped[str]
    tenant_name: Mapped[str]
    application_id: Mapped[str]
    application_name: Mapped[str]
    device_profile_id: Mapped[str]
    device_profile_name: Mapped[str]
    device_name: Mapped[str]
    dev_eui: Mapped[str]
    dev_addr: Mapped[str]
    dev_voltage: Mapped[float]
    dev_current: Mapped[float]
    dev_energy_out: Mapped[float]
    dev_energy_in: Mapped[float]
    dev_power: Mapped[float]
    dev_frequency: Mapped[float]
    dev_status_on: Mapped[bool]


AlarmType = enum.StrEnum(
    'AlarmType',
    [
        'INVALID_VALUE',
        'OVER_VOLTAGE',
        'OVER_CURRENT',
        'OVER_POWER',
        'OVER_ENERGY',
        'OVER_FREQUENCY',
    ],
)
AlarmSeverity = enum.StrEnum('AlarmSeverity', ['CRITICAL', 'MAJOR', 'MINOR'])


class StreetlampAlarm(api.postgres.Base):
    """This class represents the table streetlamp_alarms."""

    __tablename__ = 'streetlamp_alarms'
    id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), index=True
    )
    atype: Mapped[AlarmType]
    severity: Mapped[AlarmSeverity]
    cleared: Mapped[bool]
    dev_eui: Mapped[str]
    dev_voltage: Mapped[float]
    dev_current: Mapped[float]
    dev_energy_out: Mapped[float]
    dev_energy_in: Mapped[float]
    dev_power: Mapped[float]
    dev_frequency: Mapped[float]
    dev_status_on: Mapped[bool]


class StreamState(api.postgres.Base):
    """This class represents the table stream_states."""

    __tablename__ = 'stream_states'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    producer_ts: Mapped[datetime.datetime | None] = mapped_column(
        sa.DateTime(timezone=True)
    )
    consumer_ts: Mapped[datetime.datetime | None] = mapped_column(
        sa.DateTime(timezone=True)
    )


class HourlyStreetlampState(api.postgres.Base):
    """This class represents the table hourly_streetlamp_state."""

    __tablename__ = 'hourly_streetlamp_states'

    id: Mapped[int] = mapped_column(primary_key=True)
    hour: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), index=True
    )
    dev_eui: Mapped[str] = mapped_column(index=True)
    voltage: Mapped[float]
    current: Mapped[float]
    energy_out: Mapped[float]
    energy_in: Mapped[float]
    power: Mapped[float]
    frequency: Mapped[float]
    on_time: Mapped[float]

    __table_args__ = (
        sa.schema.UniqueConstraint(hour, dev_eui, name='uix_hour_dev_eui'),
    )


class DailyStreetlampState(api.postgres.Base):
    """This class represents the table daily_streetlamp_state."""

    __tablename__ = 'daily_streetlamp_states'

    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), index=True
    )
    dev_eui: Mapped[str] = mapped_column(index=True)
    voltage: Mapped[float]
    current: Mapped[float]
    energy_out: Mapped[float]
    energy_in: Mapped[float]
    power: Mapped[float]
    frequency: Mapped[float]
    on_time: Mapped[float]

    __table_args__ = (
        sa.schema.UniqueConstraint(day, dev_eui, name='uix_day_dev_eui'),
    )


class WeeklyStreetlampState(api.postgres.Base):
    """This class represents the table weekly_streetlamp_state."""

    __tablename__ = 'weekly_streetlamp_states'

    id: Mapped[int] = mapped_column(primary_key=True)
    week: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), index=True
    )
    dev_eui: Mapped[str] = mapped_column(index=True)
    voltage: Mapped[float]
    current: Mapped[float]
    energy_out: Mapped[float]
    energy_in: Mapped[float]
    power: Mapped[float]
    frequency: Mapped[float]
    on_time: Mapped[float]

    __table_args__ = (
        sa.schema.UniqueConstraint(week, dev_eui, name='uix_week_dev_eui'),
    )


class MonthlyStreetlampState(api.postgres.Base):
    """This class represents the table monthly_streetlamp_state."""

    __tablename__ = 'monthly_streetlamp_states'

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), index=True
    )
    dev_eui: Mapped[str] = mapped_column(index=True)
    voltage: Mapped[float]
    current: Mapped[float]
    energy_out: Mapped[float]
    energy_in: Mapped[float]
    power: Mapped[float]
    frequency: Mapped[float]
    on_time: Mapped[float]

    __table_args__ = (
        sa.schema.UniqueConstraint(month, dev_eui, name='uix_month_dev_eui'),
    )
