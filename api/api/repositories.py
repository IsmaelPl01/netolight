"""This module provides the repositories."""

import datetime
from collections.abc import Sequence
from typing import Annotated, Self

import fastapi
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql
import sqlalchemy.sql.expression

import api.models
import api.postgres
import api.utils


def _window_pred(
    col: sa.orm.Mapped[datetime.datetime],
    t0: datetime.datetime | None,
    t1: datetime.datetime | None,
) -> sa.sql.expression.ColumnElement[bool] | sa.sql.expression.True_:
    if t0 is not None and t1 is not None:
        return sa.and_(col >= t0, col <= t1)
    if t0 is None and t1 is not None:
        return col <= t1
    if t0 is not None and t1 is None:
        return col >= t0
    return sa.true()


class UserRepository:
    """This class represents the user repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_by_id(self: Self, uid: int) -> api.models.User | None:
        """Find a user by ID."""
        s = sa.select(api.models.User).where(api.models.User.id == uid)
        return (await self.db.execute(s)).scalar()

    async def find_by_email(self: Self, email: str) -> api.models.User | None:
        """Find a user by email."""
        s = sa.select(api.models.User).where(api.models.User.email == email)
        return (await self.db.execute(s)).scalar()

    async def find_by_account_id(
        self: Self,
        aid: int,
        skip: int = 0,
        limit: int = 4,
    ) -> Sequence[api.models.User]:
        """Find a user by account ID."""
        s = (
            sa.select(api.models.User)
            .where(api.models.User.account_id == aid)
            .offset(skip)
            .limit(limit)
        )
        return (await self.db.execute(s)).scalars().all()

    async def find_all(
        self: Self, skip: int = 0, limit: int = 4
    ) -> Sequence[api.models.User]:
        """Find a sublist of the users."""
        s = sa.select(api.models.User).offset(skip).limit(limit)
        return (await self.db.execute(s)).scalars().all()

    async def count(self: Self) -> int:
        """Count all users."""
        s = sa.select(sa.func.count(api.models.User.id))
        return (await self.db.execute(s)).scalar() or 0

    async def insert(self: Self, u: api.models.User) -> int:
        """Insert a user."""
        s = sa.insert(api.models.User).values(
            account_id=u.account_id,
            first_name=u.first_name,
            last_name=u.last_name,
            email=u.email,
            role=u.role,
            hashed_password=u.hashed_password,
        )
        return (await self.db.execute(s)).rowcount


class AccountRepository:
    """This class represents the account repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_by_id(
        self: Self, account_id: int
    ) -> api.models.Account | None:
        """Find account by ID."""
        s = sa.select(api.models.Account).where(
            api.models.Account.id == account_id
        )
        return (await self.db.execute(s)).scalar()

    async def find_by_name(self: Self, name: str) -> api.models.Account | None:
        """Find account by name."""
        s = sa.select(api.models.Account).where(api.models.Account.name == name)
        return (await self.db.execute(s)).scalar()

    async def find_all(
        self: Self, skip: int = 0, limit: int = 4
    ) -> Sequence[api.models.Account]:
        """Find a sublist of accounts."""
        s = sa.select(api.models.Account).offset(skip).limit(limit)
        return (await self.db.execute(s)).scalars().all()

    async def count(self: Self) -> int:
        """Count all the accounts."""
        s = sa.select(sa.func.count(api.models.Account.id))
        return (await self.db.execute(s)).scalar() or 0

    async def insert(self: Self, a: api.models.Account) -> int | None:
        """Insert an account."""
        s = (
            sa.insert(api.models.Account)
            .values(
                name=a.name,
                cs_tenant_id=a.cs_tenant_id,
                cs_application_id=a.cs_application_id,
                cs_streetlamp_dp_id=a.cs_streetlamp_dp_id,
            )
            .returning(api.models.Account.id)
        )
        return (await self.db.execute(s)).scalar()

    async def update(self: Self, a: api.models.Account) -> int:
        """Update an account."""
        s = (
            sa.update(api.models.Account)
            .where(api.models.Account.id == a.id)
            .values(
                name=a.name,
                cs_tenant_id=a.cs_tenant_id,
                cs_application_id=a.cs_application_id,
                cs_streetlamp_dp_id=a.cs_streetlamp_dp_id,
            )
        )
        return (await self.db.execute(s)).rowcount


class DimmingEventRepository:
    """This class represents the dimming event repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_by_id(
        self: Self, deid: int
    ) -> api.models.DimmingEvent | None:
        """Find a dimming event by ID."""
        s = sa.select(api.models.DimmingEvent).where(
            api.models.DimmingEvent.id == deid
        )
        return (await self.db.execute(s)).scalar()

    async def find_by_pid(
        self: Self, dpid: int
    ) -> Sequence[api.models.DimmingEvent]:
        """Find all dimming events of a given dimming profile."""
        s = sa.select(api.models.DimmingEvent).where(
            api.models.DimmingEvent.dimming_profile_id == dpid
        )
        return (await self.db.execute(s)).scalars().all()

    async def find_all(
        self: Self, skip: int = 0, limit: int | None = None
    ) -> Sequence[api.models.DimmingEvent]:
        """Find a sublist of dimming events."""
        if limit is not None:
            s = sa.select(api.models.DimmingEvent).offset(skip).limit(limit)
        else:
            s = sa.select(api.models.DimmingEvent).offset(skip)
        return (await self.db.execute(s)).scalars().all()

    async def count(self: Self) -> int:
        """Count all dimming events."""
        s = sa.select(sa.func.count(api.models.DimmingEvent.id))
        return (await self.db.execute(s)).scalar() or 0

    async def insert(self: Self, de: api.models.DimmingEvent) -> int | None:
        """Insert a dimming event."""
        s = (
            sa.insert(api.models.DimmingEvent)
            .values(
                account_id=de.account_id,
                dimming_profile_id=de.dimming_profile_id,
                target_id=de.target_id,
                target_type=de.target_type,
                job_id=de.job_id,
                command=de.command,
                start=de.start,
                end=de.end,
                color=de.color,
                text_color=de.text_color,
            )
            .returning(api.models.DimmingEvent.id)
        )
        return (await self.db.execute(s)).scalar()

    async def update(self: Self, de: api.models.DimmingEvent) -> bool:
        """Update a dimming event."""
        s = (
            sa.update(api.models.DimmingEvent)
            .where(api.models.DimmingEvent.id == de.id)
            .values(
                account_id=de.account_id,
                dimming_profile_id=de.dimming_profile_id,
                target_id=de.target_id,
                target_type=de.target_type,
                job_id=de.job_id,
                command=de.command,
                start=de.start,
                end=de.end,
                color=de.color,
                text_color=de.text_color,
            )
        )
        return (await self.db.execute(s)).rowcount == 1

    async def delete_by_id(self: Self, deid: int) -> bool:
        """Update a dimming event by ID."""
        s = sa.delete(api.models.DimmingEvent).where(
            api.models.DimmingEvent.id == deid
        )
        return (await self.db.execute(s)).rowcount == 1

    async def delete_by_dpid(self: Self, dpid: int) -> int:
        """Update a dimming event by ID."""
        s = sa.delete(api.models.DimmingEvent).where(
            api.models.DimmingEvent.dimming_profile_id == dpid
        )
        return (await self.db.execute(s)).rowcount


class DimmingProfileRepository:
    """This class represents a dimming profile repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_by_id(
        self: Self, dpid: int
    ) -> api.models.DimmingProfile | None:
        """Find a dimming profile by ID."""
        s = sa.select(api.models.DimmingProfile).where(
            api.models.DimmingProfile.id == dpid
        )
        return (await self.db.execute(s)).scalar()

    async def find_by_name(
        self: Self, name: str
    ) -> api.models.DimmingProfile | None:
        """Find a dimming profile by name."""
        s = sa.select(api.models.DimmingProfile).where(
            api.models.DimmingProfile.name == name
        )
        return (await self.db.execute(s)).scalar()

    async def find_all(
        self: Self, skip: int = 0, limit: int = 4
    ) -> Sequence[api.models.DimmingProfile]:
        """Find a sublist of dimming profiles."""
        s = sa.select(api.models.DimmingProfile).offset(skip).limit(limit)
        return (await self.db.execute(s)).scalars().all()

    async def count(self: Self) -> int:
        """Count all dimming profiles."""
        s = sa.select(sa.func.count(api.models.DimmingProfile.id))
        return (await self.db.execute(s)).scalar() or 0

    async def insert(self: Self, dp: api.models.DimmingProfile) -> int | None:
        """Insert a dimming profile."""
        s = (
            sa.insert(api.models.DimmingProfile)
            .values(
                account_id=dp.account_id,
                multicast_group_id=dp.multicast_group_id,
                active=dp.active,
                name=dp.name,
                description=dp.description,
                color=dp.color,
                sunset_dim_cmd0=dp.sunset_dim_cmd0,
                sunset_dim_cmd1=dp.sunset_dim_cmd1,
                h2000_dim_cmd=dp.h2000_dim_cmd,
                h2200_dim_cmd=dp.h2200_dim_cmd,
                h0000_dim_cmd=dp.h0000_dim_cmd,
                h0200_dim_cmd=dp.h0200_dim_cmd,
                h0400_dim_cmd=dp.h0400_dim_cmd,
                sunrise_dim_cmd0=dp.sunrise_dim_cmd0,
                sunrise_dim_cmd1=dp.sunrise_dim_cmd1,
            )
            .returning(api.models.DimmingProfile.id)
        )
        return (await self.db.execute(s)).scalar()

    async def update(
        self: Self,
        dpid: int,
        dp: api.models.DimmingProfile,
    ) -> bool:
        """Update a dimming profile."""
        s = (
            sa.update(api.models.DimmingProfile)
            .where(api.models.DimmingProfile.id == dpid)
            .values(
                account_id=dp.account_id,
                multicast_group_id=dp.multicast_group_id,
                active=dp.active,
                name=dp.name,
                description=dp.description,
                color=dp.color,
                sunset_dim_cmd0=dp.sunset_dim_cmd0,
                sunset_dim_cmd1=dp.sunset_dim_cmd1,
                h2000_dim_cmd=dp.h2000_dim_cmd,
                h2200_dim_cmd=dp.h2200_dim_cmd,
                h0000_dim_cmd=dp.h0000_dim_cmd,
                h0200_dim_cmd=dp.h0200_dim_cmd,
                h0400_dim_cmd=dp.h0400_dim_cmd,
                sunrise_dim_cmd0=dp.sunrise_dim_cmd0,
                sunrise_dim_cmd1=dp.sunrise_dim_cmd1,
            )
        )
        return (await self.db.execute(s)).rowcount == 1

    async def delete_by_id(self: Self, dpid: int) -> bool:
        """Delete a dimming profile by ID."""
        s = sa.delete(api.models.DimmingProfile).where(
            api.models.DimmingProfile.id == dpid
        )
        return (await self.db.execute(s)).rowcount == 1


class StreetlampRepository:
    """This class represents a streetlamp repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_by_id(self: Self, sid: int) -> api.models.Streetlamp | None:
        """Find a streetlamp by ID."""
        s = sa.select(api.models.Streetlamp).where(
            api.models.Streetlamp.id == sid
        )
        return (await self.db.execute(s)).scalar()

    async def find_by_name(
        self: Self, name: str
    ) -> api.models.Streetlamp | None:
        """Find a streetlamp by name."""
        s = sa.select(api.models.Streetlamp).where(
            api.models.Streetlamp.name == name
        )
        return (await self.db.execute(s)).scalar()

    async def find_all(
        self: Self, skip: int = 0, limit: int | None = None
    ) -> Sequence[api.models.Streetlamp]:
        """Find a sublist of streetlamps."""
        if limit is None:
            s = sa.select(api.models.Streetlamp).offset(skip)
        else:
            s = sa.select(api.models.Streetlamp).offset(skip).limit(limit)
        return (await self.db.execute(s)).scalars().all()

    async def count(self: Self) -> int:
        """Count all streetlamps."""
        s = sa.select(sa.func.count(api.models.Streetlamp.id))
        return (await self.db.execute(s)).scalar() or 0

    async def insert(self: Self, s: api.models.Streetlamp) -> int | None:
        """Insert a streetlamp."""
        stmt = (
            sa.insert(api.models.Streetlamp)
            .values(
                account_id=s.account_id,
                device_eui=s.device_eui,
                name=s.name,
                lon=s.lon,
                lat=s.lat,
            )
            .returning(api.models.Streetlamp.id)
        )
        return (await self.db.execute(stmt)).scalar()

    async def update(self: Self, sid: int, s: api.models.Streetlamp) -> bool:
        """Update a streetlamp."""
        stmt = (
            sa.update(api.models.Streetlamp)
            .values(
                account_id=s.account_id,
                device_eui=s.device_eui,
                name=s.name,
                lon=s.lon,
                lat=s.lat,
            )
            .where(api.models.Streetlamp.id == sid)
        )
        return (await self.db.execute(stmt)).rowcount == 1

    async def delete_by_id(self: Self, sid: int) -> bool:
        """Delete a streetlamp."""
        s = sa.delete(api.models.Streetlamp).where(
            api.models.Streetlamp.id == sid
        )
        return (await self.db.execute(s)).rowcount == 1

    async def delete_all(self: Self) -> int:
        """Delete all streetlamps."""
        s = sa.delete(api.models.Streetlamp)
        return (await self.db.execute(s)).rowcount


class StreetlampStateRepository:
    """This class represents a streetlamp state repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_oldest_by_dev_eui(
        self: Self, dev_eui: str
    ) -> api.models.StreetlampState | None:
        """Find oldest streetlamp state."""
        s = sa.select(api.models.StreetlampState).where(
            api.models.StreetlampState.time
            == (
                sa.select(sa.func.min(api.models.StreetlampState.time))
                .where(api.models.StreetlampState.dev_eui == dev_eui)
                .scalar_subquery()
            ),
            api.models.StreetlampState.dev_eui == dev_eui,
        )
        return (await self.db.execute(s)).scalar_one_or_none()

    async def find_latest_by_dev_eui(
        self: Self, dev_eui: str
    ) -> api.models.StreetlampState | None:
        """Find latest streetlamp state."""
        s = sa.select(api.models.StreetlampState).where(
            api.models.StreetlampState.time
            == (
                sa.select(sa.func.max(api.models.StreetlampState.time))
                .where(
                    api.models.StreetlampState.dev_eui == dev_eui,
                )
                .scalar_subquery()
            ),
            api.models.StreetlampState.dev_eui == dev_eui,
        )
        return (await self.db.execute(s)).scalar_one_or_none()

    async def find_by_id(
        self: Self, ssid: int
    ) -> api.models.StreetlampState | None:
        """Find a streetlamp state by ID."""
        s = sa.select(api.models.StreetlampState).where(
            api.models.StreetlampState.id == ssid
        )
        return (await self.db.execute(s)).scalar()

    async def find_all(
        self: Self, skip: int = 0, limit: int | None = None
    ) -> Sequence[api.models.StreetlampState]:
        """Find a sublist streetlamp states."""
        if limit is None:
            s = sa.select(api.models.StreetlampState).offset(skip)
        else:
            s = sa.select(api.models.StreetlampState).offset(skip).limit(limit)
        return (await self.db.execute(s)).scalars().all()

    async def count(self: Self) -> int:
        """Count all streetlamp states."""
        s = sa.select(sa.func.count(api.models.StreetlampState.id))
        return (await self.db.execute(s)).scalar() or 0

    async def insert(self: Self, ss: api.models.StreetlampState) -> int | None:
        """Insert a streetlamp state."""
        s = (
            sa.insert(api.models.StreetlampState)
            .values(
                deduplication_id=ss.deduplication_id,
                time=ss.time,
                tenant_id=ss.tenant_id,
                tenant_name=ss.tenant_name,
                application_id=ss.application_id,
                application_name=ss.application_name,
                device_profile_id=ss.device_profile_id,
                device_profile_name=ss.device_profile_name,
                device_name=ss.device_name,
                dev_eui=ss.dev_eui,
                dev_addr=ss.dev_addr,
                dev_voltage=ss.dev_voltage,
                dev_current=ss.dev_current,
                dev_energy_out=ss.dev_energy_out,
                dev_energy_in=ss.dev_energy_in,
                dev_power=ss.dev_power,
                dev_frequency=ss.dev_frequency,
                dev_status_on=ss.dev_status_on,
            )
            .returning(api.models.StreetlampState.id)
        )
        return (await self.db.execute(s)).scalar()

    async def delete_by_id(self: Self, sid: int) -> bool:
        """Delete a streetlamp by ID."""
        s = sa.delete(api.models.StreetlampState).where(
            api.models.StreetlampState.id == sid
        )
        return (await self.db.execute(s)).rowcount == 1

    async def delete_all(self: Self) -> int:
        """Delete all streetlamp states."""
        s = sa.delete(api.models.StreetlampState)
        return (await self.db.execute(s)).rowcount


class StreetlampAlarmRepository:
    """This class represents a streetlamp alarm repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_by_id(
        self: Self, said: int
    ) -> api.models.StreetlampAlarm | None:
        """Find a streetlamp alarm by ID."""
        s = sa.select(api.models.StreetlampAlarm).where(
            api.models.StreetlampAlarm.id == said
        )
        return (await self.db.execute(s)).scalar()

    async def find_all(
        self: Self, skip: int = 0, limit: int | None = None
    ) -> Sequence[api.models.StreetlampAlarm]:
        """Find a sublist streetlamp alarms."""
        if limit is None:
            s = sa.select(api.models.StreetlampAlarm).offset(skip)
        else:
            s = sa.select(api.models.StreetlampAlarm).offset(skip).limit(limit)
        return (await self.db.execute(s)).scalars().all()

    async def count(self: Self) -> int:
        """Count all streetlamp alarms."""
        s = sa.select(sa.func.count(api.models.StreetlampAlarm.id))
        return (await self.db.execute(s)).scalar() or 0

    async def insert(self: Self, sal: api.models.StreetlampAlarm) -> int | None:
        """Insert a streetlamp alarm."""
        s = (
            sa.insert(api.models.StreetlampAlarm)
            .values(
                time=sal.time,
                atype=sal.atype,
                severity=sal.severity,
                cleared=sal.cleared,
                dev_eui=sal.dev_eui,
                dev_voltage=sal.dev_voltage,
                dev_current=sal.dev_current,
                dev_energy_out=sal.dev_energy_out,
                dev_energy_in=sal.dev_energy_in,
                dev_power=sal.dev_power,
                dev_frequency=sal.dev_frequency,
                dev_status_on=sal.dev_status_on,
            )
            .returning(api.models.StreetlampAlarm.id)
        )
        return (await self.db.execute(s)).scalar()

    async def delete_by_id(self: Self, said: int) -> bool:
        """Delete a streetlamp by ID."""
        s = sa.delete(api.models.StreetlampAlarm).where(
            api.models.StreetlampAlarm.id == said
        )
        return (await self.db.execute(s)).rowcount == 1

    async def delete_all(self: Self) -> int:
        """Delete all streetlamp alarms."""
        s = sa.delete(api.models.StreetlampAlarm)
        return (await self.db.execute(s)).rowcount

    async def summary(self: Self):  # noqa: ANN201
        """Make summary alarms not yet cleared."""
        t = api.models.StreetlampAlarm
        s = sa.select(
            sa.select(sa.func.count(t.dev_eui))
            .where(
                sa.not_(t.cleared),
                t.severity == api.models.AlarmSeverity.CRITICAL,
            )
            .label('critical'),
            sa.select(sa.func.count(t.dev_eui))
            .where(
                sa.not_(t.cleared), t.severity == api.models.AlarmSeverity.MAJOR
            )
            .label('major'),
            sa.select(sa.func.count(t.dev_eui))
            .where(
                sa.not_(t.cleared), t.severity == api.models.AlarmSeverity.MINOR
            )
            .label('minor'),
        )

        return (await self.db.execute(s)).one()


class HourlyStreetlampStateRepository:
    """This class represents a hourly streetlamp energy repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_oldest_by_dev_eui(
        self: Self, dev_eui: str
    ) -> api.models.HourlyStreetlampState | None:
        """Find oldest hourly streetlamp energy row."""
        s = sa.select(api.models.HourlyStreetlampState).where(
            api.models.HourlyStreetlampState.hour
            == (
                sa.select(sa.func.min(api.models.HourlyStreetlampState.hour))
                .where(api.models.HourlyStreetlampState.dev_eui == dev_eui)
                .scalar_subquery()
            ),
            api.models.HourlyStreetlampState.dev_eui == dev_eui,
        )
        return (await self.db.execute(s)).scalar_one_or_none()

    async def find_latest_by_dev_eui(
        self: Self, dev_eui: str
    ) -> api.models.HourlyStreetlampState | None:
        """Find latest hourly streetlamp energy entry."""
        s = sa.select(api.models.HourlyStreetlampState).where(
            api.models.HourlyStreetlampState.hour
            == (
                sa.select(sa.func.max(api.models.HourlyStreetlampState.hour))
                .where(
                    api.models.HourlyStreetlampState.dev_eui == dev_eui,
                )
                .scalar_subquery()
            ),
            api.models.HourlyStreetlampState.dev_eui == dev_eui,
        )
        return (await self.db.execute(s)).scalar_one_or_none()

    async def find_by_id(
        self: Self, hseid: int
    ) -> api.models.HourlyStreetlampState | None:
        """Find an hourly streetlamp energy row."""
        s = sa.select(api.models.HourlyStreetlampState).where(
            api.models.HourlyStreetlampState.id == hseid
        )
        return (await self.db.execute(s)).scalar()

    async def find_by_hour(
        self: Self, hour: datetime.datetime
    ) -> api.models.HourlyStreetlampState | None:
        """Find all hourly streetlamp energy rows of a given hour."""
        s = sa.select(api.models.HourlyStreetlampState).where(
            api.models.HourlyStreetlampState.hour == hour
        )
        return (await self.db.execute(s)).scalar()

    async def delete(
        self: Self, t0: datetime.datetime | None, t1: datetime.datetime | None
    ) -> int:
        """Delete all hourly streetlamp energy rows between t0 and t1."""
        s = sa.delete(api.models.HourlyStreetlampState).where(
            _window_pred(api.models.HourlyStreetlampState.hour, t0, t1)
        )
        return (await self.db.execute(s)).rowcount

    async def delete_all(self: Self) -> int:
        """Delete all hourly streetlamp energy rows."""
        s = sa.delete(api.models.HourlyStreetlampState)
        return (await self.db.execute(s)).rowcount

    async def pull(
        self: Self,
        dev_eui: str,
        t0: datetime.datetime,
        t1: datetime.datetime,
    ) -> int:
        """Pull energy information from table streetlamp_states."""
        src = api.models.StreetlampState
        tgt = api.models.HourlyStreetlampState
        s = sa.dialects.postgresql.insert(tgt).from_select(
            [
                tgt.hour,
                tgt.dev_eui,
                tgt.voltage,
                tgt.current,
                tgt.energy_out,
                tgt.energy_in,
                tgt.power,
                tgt.frequency,
                tgt.on_time,
            ],
            sa.select(
                (sa.func.date_trunc('hour', sa.func.min(src.time))).label(
                    'hour'
                ),
                src.dev_eui.label('dev_eui'),
                sa.func.avg(src.dev_voltage).label('voltage'),
                sa.func.avg(src.dev_current).label('current'),
                (
                    (
                        sa.func.max(src.dev_energy_out)
                        - sa.func.min(src.dev_energy_out)
                    )
                    / 100.0
                ).label('energy_out'),
                (
                    (
                        sa.func.max(src.dev_energy_in)
                        - sa.func.min(src.dev_energy_in)
                    )
                    / 100.0
                ).label('energy_in'),
                sa.func.avg(src.dev_power).label('power'),
                sa.func.avg(src.dev_frequency).label('frequency'),
                (
                    sa.func.avg(sa.func.cast(src.dev_status_on, sa.Integer))
                    * sa.func.extract(
                        'epoch', sa.func.max(src.time) - sa.func.min(src.time)
                    )
                ).label('on_time'),
            )
            .where(
                src.time.between(t0, t1),
                src.dev_eui == dev_eui,
            )
            .group_by(src.dev_eui, sa.func.date_trunc('hour', src.time))
            .order_by('hour'),
        )

        us = s.on_conflict_do_update(
            index_elements=['hour', 'dev_eui'],
            set_={
                'voltage': s.excluded.voltage,
                'current': s.excluded.current,
                'energy_out': s.excluded.energy_out,
                'energy_in': s.excluded.energy_in,
                'power': s.excluded.power,
                'frequency': s.excluded.frequency,
                'on_time': s.excluded.on_time,
            },
        )

        return (await self.db.execute(us)).rowcount

    async def day_summary(self: Self, day: datetime.datetime):  # noqa: ANN201
        """Make summary of given day."""
        t = api.models.HourlyStreetlampState
        s = sa.select(
            sa.func.count(sa.func.distinct(t.dev_eui)).label('ndevices'),
            sa.func.coalesce(sa.func.avg(t.voltage), 0).label('voltage'),
            sa.func.coalesce(sa.func.avg(t.current), 0).label('current'),
            sa.func.coalesce(sa.func.sum(t.energy_out), 0).label('energy_out'),
            sa.func.coalesce(sa.func.sum(t.energy_in), 0).label('energy_in'),
            sa.func.coalesce(sa.func.avg(t.power), 0).label('power'),
            sa.func.coalesce(sa.func.avg(t.frequency), 0).label('frequency'),
            sa.func.coalesce(sa.func.sum(t.on_time), 0).label('on_time'),
        ).where(
            sa.func.date_trunc('day', t.hour) == sa.func.date_trunc('day', day),
        )

        return (await self.db.execute(s)).one()


class DailyStreetlampStateRepository:
    """This class represents a daily streetlamp energy repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_oldest_by_dev_eui(
        self: Self, dev_eui: str
    ) -> api.models.DailyStreetlampState | None:
        """Find oldest daily streetlamp energy row."""
        s = sa.select(api.models.DailyStreetlampState).where(
            api.models.DailyStreetlampState.day
            == (
                sa.select(sa.func.min(api.models.DailyStreetlampState.day))
                .where(api.models.DailyStreetlampState.dev_eui == dev_eui)
                .scalar_subquery()
            ),
            api.models.DailyStreetlampState.dev_eui == dev_eui,
        )
        return (await self.db.execute(s)).scalar_one_or_none()

    async def find_by_id(
        self: Self, dseid: int
    ) -> api.models.DailyStreetlampState | None:
        """Find a daily streetlamp energy row by ID."""
        s = sa.select(api.models.DailyStreetlampState).where(
            api.models.DailyStreetlampState.id == dseid
        )
        return (await self.db.execute(s)).scalar()

    async def find_by_day(
        self: Self, day: datetime.datetime
    ) -> api.models.DailyStreetlampState | None:
        """Find all daily streetlamp energy rows of a given day."""
        s = sa.select(api.models.DailyStreetlampState).where(
            api.models.DailyStreetlampState.day == day
        )
        return (await self.db.execute(s)).scalar()

    async def delete(
        self: Self, t0: datetime.datetime | None, t1: datetime.datetime | None
    ) -> int:
        """Delete all daily streetlamp energy rows between t0 and t1."""
        s = sa.delete(api.models.DailyStreetlampState).where(
            _window_pred(api.models.DailyStreetlampState.day, t0, t1)
        )
        return (await self.db.execute(s)).rowcount

    async def delete_all(self: Self) -> int:
        """Delete all daily streetlamp energy rows."""
        s = sa.delete(api.models.DailyStreetlampState)
        return (await self.db.execute(s)).rowcount

    async def pull(
        self: Self,
        dev_eui: str,
        t0: datetime.datetime,
        t1: datetime.datetime,
    ) -> int:
        """Pull energy information from table hourly_streetlamp_energy."""
        src = api.models.HourlyStreetlampState
        tgt = api.models.DailyStreetlampState
        s = sa.dialects.postgresql.insert(tgt).from_select(
            [
                tgt.day,
                tgt.dev_eui,
                tgt.voltage,
                tgt.current,
                tgt.energy_out,
                tgt.energy_in,
                tgt.power,
                tgt.frequency,
                tgt.on_time,
            ],
            sa.select(
                (sa.func.date_trunc('day', sa.func.min(src.hour))).label('day'),
                src.dev_eui.label('dev_eui'),
                sa.func.avg(src.voltage).label('voltage'),
                sa.func.avg(src.current).label('current'),
                sa.func.sum(src.energy_out).label('energy_out'),
                sa.func.sum(src.energy_in).label('energy_in'),
                sa.func.avg(src.power).label('power'),
                sa.func.avg(src.frequency).label('frequency'),
                sa.func.sum(src.on_time).label('on_time'),
            )
            .where(src.hour.between(t0, t1), src.dev_eui == dev_eui)
            .group_by(src.dev_eui, sa.func.date_trunc('day', src.hour))
            .order_by('day'),
        )

        us = s.on_conflict_do_update(
            index_elements=['day', 'dev_eui'],
            set_={
                'voltage': s.excluded.voltage,
                'current': s.excluded.current,
                'energy_out': s.excluded.energy_out,
                'energy_in': s.excluded.energy_in,
                'power': s.excluded.power,
                'frequency': s.excluded.frequency,
                'on_time': s.excluded.on_time,
            },
        )

        return (await self.db.execute(us)).rowcount

    async def summary(self: Self, day: datetime.datetime):  # noqa: ANN201
        """Make summary of given day."""
        t = api.models.DailyStreetlampState
        s = sa.select(
            sa.func.count(t.dev_eui).label('ndevices'),
            sa.func.coalesce(sa.func.avg(t.voltage), 0).label('voltage'),
            sa.func.coalesce(sa.func.avg(t.current), 0).label('current'),
            sa.func.coalesce(sa.func.sum(t.energy_out), 0).label('energy_out'),
            sa.func.coalesce(sa.func.sum(t.energy_in), 0).label('energy_in'),
            sa.func.coalesce(sa.func.avg(t.power), 0).label('power'),
            sa.func.coalesce(sa.func.avg(t.frequency), 0).label('frequency'),
            sa.func.coalesce(sa.func.sum(t.on_time), 0).label('on_time'),
        ).where(
            sa.func.date_trunc('day', t.day) == sa.func.date_trunc('day', day),
        )

        return (await self.db.execute(s)).one()

    async def pointwise_summary(  # noqa: ANN201
        self: Self, from_: datetime.datetime, to: datetime.datetime
    ):
        """Make summary of given interval."""
        t = api.models.DailyStreetlampState
        s = (
            sa.select(
                t.day.label('ts'),
                sa.func.count(t.dev_eui).label('ndevices'),
                sa.func.coalesce(sa.func.avg(t.voltage), 0).label('voltage'),
                sa.func.coalesce(sa.func.avg(t.current), 0).label('current'),
                sa.func.coalesce(sa.func.sum(t.energy_out), 0).label(
                    'energy_out'
                ),
                sa.func.coalesce(sa.func.sum(t.energy_in), 0).label(
                    'energy_in'
                ),
                sa.func.coalesce(sa.func.avg(t.power), 0).label('power'),
                sa.func.coalesce(sa.func.avg(t.frequency), 0).label(
                    'frequency'
                ),
                sa.func.coalesce(sa.func.sum(t.on_time), 0).label('on_time'),
            )
            .where(
                sa.func.date_trunc('day', t.day)
                >= sa.func.date_trunc('day', from_),
                sa.func.date_trunc('day', t.day)
                <= sa.func.date_trunc('day', to),
            )
            .group_by(t.day)
            .order_by(t.day)
        )

        return (await self.db.execute(s)).all()


class WeeklyStreetlampStateRepository:
    """This class represents a weekly streetlamp energy repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_oldest_by_dev_eui(
        self: Self, dev_eui: str
    ) -> api.models.WeeklyStreetlampState | None:
        """Find oldest weekly streetlamp energy row."""
        s = sa.select(api.models.WeeklyStreetlampState).where(
            api.models.WeeklyStreetlampState.week
            == (
                sa.select(sa.func.min(api.models.WeeklyStreetlampState.week))
                .where(api.models.WeeklyStreetlampState.dev_eui == dev_eui)
                .scalar_subquery()
            ),
            api.models.WeeklyStreetlampState.dev_eui == dev_eui,
        )
        return (await self.db.execute(s)).scalar_one_or_none()

    async def find_by_id(
        self: Self, wseid: int
    ) -> api.models.WeeklyStreetlampState | None:
        """Find a weekly streetlamp energy row by ID."""
        s = sa.select(api.models.WeeklyStreetlampState).where(
            api.models.WeeklyStreetlampState.id == wseid
        )
        return (await self.db.execute(s)).scalar()

    async def delete(
        self: Self, t0: datetime.datetime | None, t1: datetime.datetime | None
    ) -> int:
        """Delete all weekly streetlamp energy rows between t0 and t1."""
        s = sa.delete(api.models.WeeklyStreetlampState).where(
            _window_pred(api.models.WeeklyStreetlampState.week, t0, t1)
        )
        return (await self.db.execute(s)).rowcount

    async def delete_all(self: Self) -> int:
        """Delete all weekly streetlamp energy rows."""
        s = sa.delete(api.models.WeeklyStreetlampState)
        return (await self.db.execute(s)).rowcount

    async def pull(
        self: Self,
        dev_eui: str,
        t0: datetime.datetime,
        t1: datetime.datetime,
    ) -> int:
        """Pull state information from table hourly_streetlamp_state."""
        src = api.models.DailyStreetlampState
        tgt = api.models.WeeklyStreetlampState
        s = sa.dialects.postgresql.insert(tgt).from_select(
            [
                tgt.week,
                tgt.dev_eui,
                tgt.voltage,
                tgt.current,
                tgt.energy_out,
                tgt.energy_in,
                tgt.power,
                tgt.frequency,
                tgt.on_time,
            ],
            sa.select(
                (sa.func.date_trunc('week', sa.func.min(src.day))).label(
                    'week'
                ),
                src.dev_eui.label('dev_eui'),
                sa.func.avg(src.voltage).label('voltage'),
                sa.func.avg(src.current).label('current'),
                sa.func.sum(src.energy_out).label('energy_out'),
                sa.func.sum(src.energy_in).label('energy_in'),
                sa.func.avg(src.power).label('power'),
                sa.func.avg(src.frequency).label('frequency'),
                sa.func.sum(src.on_time).label('on_time'),
            )
            .where(src.day.between(t0, t1), src.dev_eui == dev_eui)
            .group_by(src.dev_eui, sa.func.date_trunc('week', src.day))
            .order_by('week'),
        )

        us = s.on_conflict_do_update(
            index_elements=['week', 'dev_eui'],
            set_={
                'voltage': s.excluded.voltage,
                'current': s.excluded.current,
                'energy_out': s.excluded.energy_out,
                'energy_in': s.excluded.energy_in,
                'power': s.excluded.power,
                'frequency': s.excluded.frequency,
                'on_time': s.excluded.on_time,
            },
        )

        return (await self.db.execute(us)).rowcount

    async def summary(self: Self, week: datetime.datetime):  # noqa: ANN201
        """Make summary of given week."""
        t = api.models.WeeklyStreetlampState
        s = sa.select(
            sa.func.count(t.dev_eui).label('ndevices'),
            sa.func.coalesce(sa.func.avg(t.voltage), 0).label('voltage'),
            sa.func.coalesce(sa.func.avg(t.current), 0).label('current'),
            sa.func.coalesce(sa.func.sum(t.energy_out), 0).label('energy_out'),
            sa.func.coalesce(sa.func.sum(t.energy_in), 0).label('energy_in'),
            sa.func.coalesce(sa.func.avg(t.power), 0).label('power'),
            sa.func.coalesce(sa.func.avg(t.frequency), 0).label('frequency'),
            sa.func.coalesce(sa.func.sum(t.on_time), 0).label('on_time'),
        ).where(
            sa.func.date_trunc('week', t.week)
            == sa.func.date_trunc('week', week),
        )

        return (await self.db.execute(s)).one()

    async def pointwise_summary(  # noqa: ANN201
        self: Self, from_: datetime.datetime, to: datetime.datetime
    ):
        """Make summary of given interval."""
        t = api.models.WeeklyStreetlampState
        s = (
            sa.select(
                t.week.label('ts'),
                sa.func.count(t.dev_eui).label('ndevices'),
                sa.func.coalesce(sa.func.avg(t.voltage), 0).label('voltage'),
                sa.func.coalesce(sa.func.avg(t.current), 0).label('current'),
                sa.func.coalesce(sa.func.sum(t.energy_out), 0).label(
                    'energy_out'
                ),
                sa.func.coalesce(sa.func.sum(t.energy_in), 0).label(
                    'energy_in'
                ),
                sa.func.coalesce(sa.func.avg(t.power), 0).label('power'),
                sa.func.coalesce(sa.func.avg(t.frequency), 0).label(
                    'frequency'
                ),
                sa.func.coalesce(sa.func.sum(t.on_time), 0).label('on_time'),
            )
            .where(
                sa.func.date_trunc('week', t.week)
                >= sa.func.date_trunc('week', from_),
                sa.func.date_trunc('week', t.week)
                <= sa.func.date_trunc('week', to),
            )
            .group_by(t.week)
            .order_by(t.week)
        )

        return (await self.db.execute(s)).all()


class MonthlyStreetlampStateRepository:
    """This class represents a monthly streetlamp energy repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_by_id(
        self: Self, mseid: int
    ) -> api.models.MonthlyStreetlampState | None:
        """Find a monthly streetlamp energy row by ID."""
        s = sa.select(api.models.MonthlyStreetlampState).where(
            api.models.MonthlyStreetlampState.id == mseid
        )
        return (await self.db.execute(s)).scalar()

    async def delete(
        self: Self, t0: datetime.datetime | None, t1: datetime.datetime | None
    ) -> int:
        """Delete all monthly streetlamp energy rows between t0 and t1."""
        s = sa.delete(api.models.MonthlyStreetlampState).where(
            _window_pred(api.models.MonthlyStreetlampState.month, t0, t1)
        )
        return (await self.db.execute(s)).rowcount

    async def delete_all(self: Self) -> int:
        """Delete all monthly streetlamp energy rows."""
        s = sa.delete(api.models.MonthlyStreetlampState)
        return (await self.db.execute(s)).rowcount

    async def pull(
        self: Self,
        dev_eui: str,
        t0: datetime.datetime,
        t1: datetime.datetime,
    ) -> int:
        """Pull state information from table hourly_streetlamp_state."""
        src = api.models.DailyStreetlampState
        tgt = api.models.MonthlyStreetlampState
        s = sa.dialects.postgresql.insert(tgt).from_select(
            [
                tgt.month,
                tgt.dev_eui,
                tgt.voltage,
                tgt.current,
                tgt.energy_out,
                tgt.energy_in,
                tgt.power,
                tgt.frequency,
                tgt.on_time,
            ],
            sa.select(
                (sa.func.date_trunc('month', sa.func.min(src.day))).label(
                    'month'
                ),
                src.dev_eui.label('dev_eui'),
                sa.func.avg(src.voltage).label('voltage'),
                sa.func.avg(src.current).label('current'),
                sa.func.sum(src.energy_out).label('energy_out'),
                sa.func.sum(src.energy_in).label('energy_in'),
                sa.func.avg(src.power).label('power'),
                sa.func.avg(src.frequency).label('frequency'),
                sa.func.sum(src.on_time).label('on_time'),
            )
            .where(src.day.between(t0, t1), src.dev_eui == dev_eui)
            .group_by(src.dev_eui, sa.func.date_trunc('month', src.day))
            .order_by('month'),
        )
        us = s.on_conflict_do_update(
            index_elements=['month', 'dev_eui'],
            set_={
                'voltage': s.excluded.voltage,
                'current': s.excluded.current,
                'energy_out': s.excluded.energy_out,
                'energy_in': s.excluded.energy_in,
                'power': s.excluded.power,
                'frequency': s.excluded.frequency,
                'on_time': s.excluded.on_time,
            },
        )

        return (await self.db.execute(us)).rowcount

    async def summary(self: Self, month: datetime.datetime):  # noqa: ANN201
        """Make summary of given month."""
        t = api.models.MonthlyStreetlampState
        s = sa.select(
            sa.func.count(sa.func.distinct(t.dev_eui)).label('ndevices'),
            sa.func.coalesce(sa.func.avg(t.voltage), 0).label('voltage'),
            sa.func.coalesce(sa.func.avg(t.current), 0).label('current'),
            sa.func.coalesce(sa.func.sum(t.energy_out), 0).label('energy_out'),
            sa.func.coalesce(sa.func.sum(t.energy_in), 0).label('energy_in'),
            sa.func.coalesce(sa.func.avg(t.power), 0).label('power'),
            sa.func.coalesce(sa.func.avg(t.frequency), 0).label('frequency'),
            sa.func.coalesce(sa.func.sum(t.on_time), 0).label('on_time'),
        ).where(
            sa.func.date_trunc('month', t.month)
            == sa.func.date_trunc('month', month),
        )

        return (await self.db.execute(s)).one()

    async def pointwise_summary(  # noqa: ANN201
        self: Self, from_: datetime.datetime, to: datetime.datetime
    ):
        """Make summary of given interval."""
        t = api.models.MonthlyStreetlampState
        s = (
            sa.select(
                t.month.label('ts'),
                sa.func.count(t.dev_eui).label('ndevices'),
                sa.func.coalesce(sa.func.avg(t.voltage), 0).label('voltage'),
                sa.func.coalesce(sa.func.avg(t.current), 0).label('current'),
                sa.func.coalesce(sa.func.sum(t.energy_out), 0).label(
                    'energy_out'
                ),
                sa.func.coalesce(sa.func.sum(t.energy_in), 0).label(
                    'energy_in'
                ),
                sa.func.coalesce(sa.func.avg(t.power), 0).label('power'),
                sa.func.coalesce(sa.func.avg(t.frequency), 0).label(
                    'frequency'
                ),
                sa.func.coalesce(sa.func.sum(t.on_time), 0).label('on_time'),
            )
            .where(
                sa.func.date_trunc('month', t.month)
                >= sa.func.date_trunc('month', from_),
                sa.func.date_trunc('month', t.month)
                <= sa.func.date_trunc('month', to),
            )
            .group_by(t.month)
            .order_by(t.month)
        )

        return (await self.db.execute(s)).all()


class StreamStateRepository:
    """This class represents the stream state repository."""

    def __init__(
        self: Self,
        db: Annotated[api.postgres.Db, fastapi.Depends(api.postgres.get_db)],
    ) -> None:
        """Initialize the db property."""
        self.db = db

    async def find_by_name(
        self: Self, name: str
    ) -> api.models.StreamState | None:
        """Find a stream state by name."""
        s = sa.select(api.models.StreamState).where(
            sa.func.lower(api.models.StreamState.name) == sa.func.lower(name)
        )
        return (await self.db.execute(s)).scalar()

    async def delete_by_name(self: Self, name: str) -> int:
        """Delete a stream state by name."""
        s = sa.delete(api.models.StreamState).where(
            api.models.StreamState.name == name
        )
        return (await self.db.execute(s)).rowcount

    async def delete_all(self: Self) -> int:
        """Delete all stream states."""
        s = sa.delete(api.models.StreamState)
        return (await self.db.execute(s)).rowcount

    async def insert(
        self: Self,
        name: str,
        producer_ts: datetime.datetime | None = None,
        consumer_ts: datetime.datetime | None = None,
    ) -> int | None:
        """Insert a stream state."""
        s = (
            sa.insert(api.models.StreamState)
            .values(name=name, producer_ts=producer_ts, consumer_ts=consumer_ts)
            .returning(api.models.StreamState.id)
        )
        return (await self.db.execute(s)).scalar()

    async def update_producer(
        self: Self, name: str, producer_ts: datetime.datetime
    ) -> int:
        """Update a stream state producer timestamp."""
        s = (
            sqlalchemy.dialects.postgresql.insert(api.models.StreamState)
            .values(name=name, producer_ts=producer_ts)
            .on_conflict_do_update(
                index_elements=['name'], set_={'producer_ts': producer_ts}
            )
        )
        return (await self.db.execute(s)).rowcount

    async def update_consumer(
        self: Self,
        name: str,
        consumer_ts: datetime.datetime | None,
    ) -> int:
        """Update a stream state consumer timestamp."""
        s = (
            sa.update(api.models.StreamState)
            .values(consumer_ts=consumer_ts)
            .where(api.models.StreamState.name == name)
        )
        return (await self.db.execute(s)).rowcount
