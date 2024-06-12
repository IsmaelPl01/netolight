import asyncio

import httpx
import pytest
import pytest_asyncio

import api.main
import api.repositories
import api.services


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def api_client():
    return httpx.AsyncClient(app=api.main.app, base_url='http://test')


@pytest_asyncio.fixture()
async def db():
    async with api.postgres.get_session().begin() as db:
        yield db


@pytest_asyncio.fixture()
async def streetlamp_repo(db):
    return api.repositories.StreetlampRepository(db)


@pytest_asyncio.fixture()
async def sstate_repo(db):
    return api.repositories.StreetlampStateRepository(db)


@pytest_asyncio.fixture()
async def salarm_repo(db):
    return api.repositories.StreetlampAlarmRepository(db)


@pytest_asyncio.fixture()
async def streamst_repo(db):
    return api.repositories.StreamStateRepository(db)


@pytest_asyncio.fixture()
async def hourly_state_repo(db):
    return api.repositories.HourlyStreetlampStateRepository(db)


@pytest_asyncio.fixture()
async def daily_state_repo(db):
    return api.repositories.DailyStreetlampStateRepository(db)


@pytest_asyncio.fixture()
async def weekly_state_repo(db):
    return api.repositories.WeeklyStreetlampStateRepository(db)


@pytest_asyncio.fixture()
async def monthly_state_repo(db):
    return api.repositories.MonthlyStreetlampStateRepository(db)


@pytest_asyncio.fixture()
async def streetlamp_state_serv(db, sstate_repo, salarm_repo, streamst_repo):
    serv = api.services.StreetlampStateService(
        sstate_repo=sstate_repo,
        stream_repo=streamst_repo,
        salarm_repo=salarm_repo,
    )

    await sstate_repo.delete_all()
    await streamst_repo.delete_all()

    yield serv


@pytest_asyncio.fixture()
async def streetlamp_hourly_agg_serv(
    streetlamp_repo,
    sstate_repo,
    streamst_repo,
    hourly_state_repo,
):
    serv = api.services.StreetlampHourlyAggregationService(
        streetlamp_repo=streetlamp_repo,
        sstate_repo=sstate_repo,
        streamst_repo=streamst_repo,
        hourly_state_repo=hourly_state_repo,
    )

    await sstate_repo.delete_all()
    await streamst_repo.delete_all()
    await hourly_state_repo.delete_all()

    yield serv


@pytest_asyncio.fixture()
async def streetlamp_daily_agg_serv(
    streetlamp_repo,
    streamst_repo,
    hourly_state_repo,
    daily_state_repo,
):
    serv = api.services.StreetlampDailyAggregationService(
        streetlamp_repo=streetlamp_repo,
        streamst_repo=streamst_repo,
        hourly_state_repo=hourly_state_repo,
        daily_state_repo=daily_state_repo,
    )

    await streamst_repo.delete_all()
    await hourly_state_repo.delete_all()
    await daily_state_repo.delete_all()

    yield serv


@pytest_asyncio.fixture()
async def streetlamp_weekly_agg_serv(
    streetlamp_repo,
    streamst_repo,
    daily_state_repo,
    weekly_state_repo,
):
    serv = api.services.StreetlampWeeklyAggregationService(
        streetlamp_repo=streetlamp_repo,
        streamst_repo=streamst_repo,
        daily_state_repo=daily_state_repo,
        weekly_state_repo=weekly_state_repo,
    )

    await streamst_repo.delete_all()
    await daily_state_repo.delete_all()
    await weekly_state_repo.delete_all()

    yield serv


@pytest_asyncio.fixture()
async def streetlamp_monthly_agg_serv(
    streetlamp_repo,
    streamst_repo,
    daily_state_repo,
    monthly_state_repo,
):
    serv = api.services.StreetlampMonthlyAggregationService(
        streetlamp_repo=streetlamp_repo,
        streamst_repo=streamst_repo,
        daily_state_repo=daily_state_repo,
        monthly_state_repo=monthly_state_repo,
    )

    await streamst_repo.delete_all()
    await daily_state_repo.delete_all()
    await monthly_state_repo.delete_all()

    yield serv


@pytest_asyncio.fixture()
async def dashboard_serv(
    streetlamp_repo,
    salarm_repo,
    hourly_state_repo,
    daily_state_repo,
    weekly_state_repo,
    monthly_state_repo,
):
    serv = api.services.DashboardService(
        streetlamp_repo=streetlamp_repo,
        salarm_repo=salarm_repo,
        hourly_state_repo=hourly_state_repo,
        daily_state_repo=daily_state_repo,
        weekly_state_repo=weekly_state_repo,
        monthly_state_repo=monthly_state_repo,
    )

    await streetlamp_repo.delete_all()
    await salarm_repo.delete_all()
    await daily_state_repo.delete_all()
    await weekly_state_repo.delete_all()
    await monthly_state_repo.delete_all()

    yield serv
