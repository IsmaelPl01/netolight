import calendar
import datetime
import math
import uuid
import zoneinfo

import api.repositories
import api.schemas
import api.services
import api.utils
import pytest


def gen_ss_sample(
    *,
    time: datetime.datetime,
    dev_eui: str,
    energy_in: float,
    power: float = 90.0,
    status_on: bool,
):
    deduplication_id = str(uuid.uuid4())
    tenant_id = '52f14cd4-c6f1-4fbd-8f87-4025e1d49242'
    tenant_name = 'NetoLight'
    application_id = 'c828e0b5-f1b7-4490-9678-59b3304070ef'
    application_name = 'NetoLight App'
    device_profile_id = '77efb5fd-d36a-4eeb-b2c8-ad1a22256771'
    device_profile_name = 'NetoLight Default Profile'
    device_name = f'NLPY{dev_eui}'
    dev_addr = '006fdf37'

    sds = api.schemas.StreetlampDeviceState(
        voltage=239.6,
        current=0.10,
        energy_out=0.0,
        energy_in=energy_in,
        power=power,
        frequency=60.0,
        status_on=status_on,
    )

    return (
        api.schemas.StreetlampStateCreate(
            deduplicationId=deduplication_id,
            time=time,
            deviceInfo=api.schemas.StreetlampInfo(
                tenantId=tenant_id,
                tenantName=tenant_name,
                applicationId=application_id,
                applicationName=application_name,
                deviceProfileId=device_profile_id,
                deviceProfileName=device_profile_name,
                deviceName=device_name,
                devEui=dev_eui,
            ),
            devAddr=dev_addr,
            data=api.services.encode_state_data(sds),
        ),
        lambda ssid: api.schemas.StreetlampState(
            id=ssid,
            time=time,
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            application_id=application_id,
            application_name=application_name,
            device_profile_id=device_profile_id,
            device_profile_name=device_profile_name,
            device_name=device_name,
            dev_eui=dev_eui,
            dev_addr=dev_addr,
            dev_voltage=sds.voltage,
            dev_current=sds.current,
            dev_energy_out=sds.energy_out,
            dev_energy_in=sds.energy_in,
            dev_power=sds.power,
            dev_frequency=sds.frequency,
            dev_status_on=sds.status_on,
        ),
    )


def test_encode_decode_state_data():
    sds = api.schemas.StreetlampDeviceState(
        voltage=239.6380566060543,
        current=0.10395040735602379,
        energy_out=0.0,
        energy_in=22267,
        power=14.328086748719215,
        frequency=60.04456432508503,
        status_on=True,
    )

    assert (
        api.services.decode_state_data(api.services.encode_state_data(sds))
        == sds
    )


@pytest.mark.asyncio()
async def test_create_streetlamp_state(
    streetlamp_state_serv: api.services.StreetlampStateService,
):
    ssc, ssf = gen_ss_sample(
        time=api.utils.utcnow(),
        dev_eui='5058000000000001',
        energy_in=22267,
        status_on=True,
    )
    ssid = await streetlamp_state_serv.create(ssc)
    ss = await streetlamp_state_serv.find_by_id(ssid)

    assert ss == ssf(ssid)


@pytest.mark.asyncio()
async def test_aggregates(
    mocker,
    streetlamp_state_serv: api.services.StreetlampStateService,
    streetlamp_hourly_agg_serv: api.services.StreetlampHourlyAggregationService,
    streetlamp_daily_agg_serv: api.services.StreetlampDailyAggregationService,
    streetlamp_weekly_agg_serv: api.services.StreetlampWeeklyAggregationService,
    streetlamp_monthly_agg_serv: api.services.StreetlampMonthlyAggregationService,
    dashboard_serv: api.services.DashboardService,
):
    nl = 3
    ss = [
        api.models.Streetlamp(
            id=i,
            account_id=1,
            name=f'NLPY505800000000000{i+1}',
            device_eui=f'505800000000000{i+1}',
        )
        for i in range(nl)
    ]
    mocker.patch.object(
        streetlamp_hourly_agg_serv.streetlamp_repo,
        'find_all',
        return_value=ss,
    )
    mocker.patch.object(
        streetlamp_hourly_agg_serv.streetlamp_repo,
        'count',
        return_value=nl,
    )
    mocker.patch.object(
        dashboard_serv.streetlamp_repo,
        'find_all',
        return_value=ss,
    )
    connectivity = api.schemas.StreetlampsConnectivity(
        active=nl,
        inactive=0,
        never_seen=0,
    )
    mocker.patch.object(
        dashboard_serv,
        '_get_connectivity_summary',
        return_value=connectivity,
    )

    r = api.utils.now()
    cal = calendar.Calendar()
    imd = list(cal.itermonthdates(r.year, r.month - 1))
    nd = len(imd) + r.day
    t0 = datetime.datetime.combine(imd[0], datetime.datetime.min.time())
    energy_in = 0
    status_on = False

    for i in range(24 * nd):
        for s in ss:
            t1 = t0 + datetime.timedelta(hours=i)
            status_on = t1.hour < 6 or t1.hour >= 18
            energy_in = energy_in + 7500 if status_on else energy_in
            ssc0, _ = gen_ss_sample(
                time=t1.astimezone(zoneinfo.ZoneInfo('UTC')),
                dev_eui=s.device_eui,
                energy_in=energy_in,
                status_on=status_on,
            )
            if (i + 1) % 24 == 0:
                ssc00, _ = gen_ss_sample(
                    time=ssc0.time + datetime.timedelta(seconds=60),
                    dev_eui=s.device_eui,
                    energy_in=energy_in,
                    power=100.0,
                    status_on=status_on,
                )
            status_on = t1.hour < 6 or t1.hour >= 18
            energy_in = energy_in + 7500 if status_on else energy_in
            t2 = t1 + datetime.timedelta(
                minutes=59, seconds=59, microseconds=999999
            )
            ssc1, _ = gen_ss_sample(
                time=t2.astimezone(zoneinfo.ZoneInfo('UTC')),
                dev_eui=s.device_eui,
                energy_in=energy_in,
                status_on=status_on,
            )
            await streetlamp_state_serv.create(ssc0)
            if (i + 1) % 24 == 0:
                await streetlamp_state_serv.create(ssc00)
            await streetlamp_hourly_agg_serv.aggregate()
            await streetlamp_state_serv.create(ssc1)

        if nd == (24 * nd) - 1:
            await streetlamp_state_serv.create(
                ssc1.copy(
                    update={
                        'time': ssc1.time + datetime.timedelta(microseconds=1)
                    }
                )
            )

        await streetlamp_daily_agg_serv.aggregate()
        await streetlamp_weekly_agg_serv.aggregate()
        await streetlamp_monthly_agg_serv.aggregate()

    d = await dashboard_serv.get(1, 1)

    assert d.connectivity == connectivity

    assert d.alarms == api.schemas.StreetlampsAlarms(
        critical=3 * nd,
        major=0,
        minor=0,
    )

    assert (
        d.today_energy.consumption
        == api.schemas.StreetlampsEnergyConsumption(
            total_in_kw=(12 * 75 * nl) / 1000,
            avg_in_watts=12 * 75,
        )
    )

    assert d.today_energy.savings == api.schemas.StreetlampsEnergySavings(
        percentage=100 * (250 - 75) / 250,
        avg_in_watts=12 * (250 - 75),
    )

    assert (
        d.today_energy.dimming_savings
        == api.schemas.StreetlampsDimmingSavings(
            percentage=round(100 * (90 - 75) / 90, 1),
            avg_in_watts=12 * (90 - 75),
        )
    )

    assert d.today_energy.co2_savings == api.schemas.StreetlampsCo2Savings(
        total_in_ton=api.services.energy_to_co2(12 * (250 - 75)),
        avg_in_ton=api.services.energy_to_co2(12 * (250 - 75)),
    )

    assert (
        d.yesterday_energy.consumption
        == api.schemas.StreetlampsEnergyConsumption(
            total_in_kw=(12 * 75 * nl) / 1000,
            avg_in_watts=12 * 75,
        )
    )

    assert d.yesterday_energy.savings == api.schemas.StreetlampsEnergySavings(
        percentage=100 * (250 - 75) / 250,
        avg_in_watts=12 * (250 - 75),
    )

    assert (
        d.yesterday_energy.dimming_savings
        == api.schemas.StreetlampsDimmingSavings(
            percentage=round(100 * (90 - 75) / 90, 1),
            avg_in_watts=12 * (90 - 75),
        )
    )

    assert d.yesterday_energy.co2_savings == api.schemas.StreetlampsCo2Savings(
        total_in_ton=api.services.energy_to_co2(12 * (250 - 75)),
        avg_in_ton=api.services.energy_to_co2(12 * (250 - 75)),
    )

    assert (
        d.last_week_energy.consumption
        == api.schemas.StreetlampsEnergyConsumption(
            total_in_kw=(7 * (12 * 75) * nl) / 1000,
            avg_in_watts=7 * (12 * 75),
        )
    )

    assert d.last_week_energy.savings == api.schemas.StreetlampsEnergySavings(
        percentage=100 * (250 - 75) / 250,
        avg_in_watts=7 * 12 * (250 - 75),
    )

    assert (
        d.last_week_energy.dimming_savings
        == api.schemas.StreetlampsDimmingSavings(
            percentage=round(100 * (90 - 75) / 90, 1),
            avg_in_watts=7 * 12 * (90 - 75),
        )
    )

    assert d.last_week_energy.co2_savings == api.schemas.StreetlampsCo2Savings(
        total_in_ton=api.services.energy_to_co2(7 * 12 * (250 - 75)),
        avg_in_ton=api.services.energy_to_co2(7 * 12 * (250 - 75)),
    )

    assert (
        d.last_month_energy.consumption
        == api.schemas.StreetlampsEnergyConsumption(
            total_in_kw=round((31 * 12 * 75 * nl) / 1000, 1),
            avg_in_watts=31 * 12 * 75,
        )
    )

    assert d.last_month_energy.savings == api.schemas.StreetlampsEnergySavings(
        percentage=100 * (250 - 75) / 250,
        avg_in_watts=31 * 12 * (250 - 75),
    )

    assert (
        d.last_month_energy.dimming_savings
        == api.schemas.StreetlampsDimmingSavings(
            percentage=round(100 * (90 - 75) / 90, 1),
            avg_in_watts=31 * 12 * (90 - 75),
        )
    )

    assert d.last_month_energy.co2_savings == api.schemas.StreetlampsCo2Savings(
        total_in_ton=api.services.energy_to_co2(31 * 12 * (250 - 75) * nl),
        avg_in_ton=api.services.energy_to_co2(31 * 12 * (250 - 75)),
    )

    assert d.geo_states == [
        api.schemas.StreetlampGeoState(
            name=s.name, dev_eui=s.device_eui, lon=s.lon, lat=s.lat
        )
        for s in ss
    ]
