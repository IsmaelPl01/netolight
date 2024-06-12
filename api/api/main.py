"""This module provides the main entry point."""

import asyncio
import contextlib
import time
from collections.abc import AsyncGenerator

import fastapi
import redis.asyncio as redis

import api.config
import api.log
import api.postgres
import api.routers
import api.rs
import api.services
import api.utils

settings = api.config.get_settings()
background_tasks = set()


async def run_agg_process() -> None:
    """Run aggregation process."""
    try:
        api.log.logger.info('Started running the aggregation process')

        async with api.postgres.get_session().begin() as db:
            streetlamp_repo = api.repositories.StreetlampRepository(db)
            sstate_repo = api.repositories.StreetlampStateRepository(db)
            streamst_repo = api.repositories.StreamStateRepository(db)
            hourly_state_repo = (
                api.repositories.HourlyStreetlampStateRepository(db)
            )
            daily_state_repo = api.repositories.DailyStreetlampStateRepository(
                db
            )
            weekly_state_repo = (
                api.repositories.WeeklyStreetlampStateRepository(db)
            )
            monthly_state_repo = (
                api.repositories.MonthlyStreetlampStateRepository(db)
            )

            hourly_agg_serv = api.services.StreetlampHourlyAggregationService(
                streetlamp_repo=streetlamp_repo,
                sstate_repo=sstate_repo,
                streamst_repo=streamst_repo,
                hourly_state_repo=hourly_state_repo,
            )

            await hourly_agg_serv.aggregate()

            daily_agg_serv = api.services.StreetlampDailyAggregationService(
                streetlamp_repo=streetlamp_repo,
                streamst_repo=streamst_repo,
                hourly_state_repo=hourly_state_repo,
                daily_state_repo=daily_state_repo,
            )

            await daily_agg_serv.aggregate()

            weekly_agg_serv = api.services.StreetlampWeeklyAggregationService(
                streetlamp_repo=streetlamp_repo,
                streamst_repo=streamst_repo,
                daily_state_repo=daily_state_repo,
                weekly_state_repo=weekly_state_repo,
            )

            await weekly_agg_serv.aggregate()

            monthly_agg_serv = api.services.StreetlampMonthlyAggregationService(
                streetlamp_repo=streetlamp_repo,
                streamst_repo=streamst_repo,
                daily_state_repo=daily_state_repo,
                monthly_state_repo=monthly_state_repo,
            )

            await monthly_agg_serv.aggregate()

        api.log.logger.info('Finished running the aggregation process')

    except Exception as e:  # noqa: BLE001
        api.log.logger.exception(
            'Failed to finish running the aggregation process', e
        )


async def proc_streetlamp_state_batch(
    last_id_seen: str, batch_size: int
) -> None:
    """Process streetlamp state batch."""
    try:
        async with api.postgres.get_session().begin() as db:
            sstate_repo = api.repositories.StreetlampStateRepository(db)
            streamst_repo = api.repositories.StreamStateRepository(db)
            salarm_repo = api.repositories.StreetlampAlarmRepository(db)
            serv = api.services.StreetlampStateService(
                sstate_repo=sstate_repo,
                stream_repo=streamst_repo,
                salarm_repo=salarm_repo,
            )

            entries = await api.rs.db.xread(
                streams={'nl:streetlamp_states': last_id_seen}, count=batch_size
            )
            n = 0
            for _, items in entries:
                for item_id, item in items:
                    ssc = api.schemas.StreetlampStateCreate.parse_raw(
                        item['value']
                    )
                    try:
                        if ssc.data:
                            ssid = await serv.create(ssc)
                            if ssid is not None:
                                n += 1
                        await api.rs.db.xdel('nl:streetlamp_states', item_id)
                    except redis.RedisError as e:
                        api.log.logger.error(
                            'Failed creating streetlamp states: %s, %s',
                            ssc,
                            e,
                        )
                    finally:
                        last_id_seen = item_id

            api.log.logger.debug('%s streetlamp state created', n)
    except Exception as e:  # noqa: BLE001
        api.log.logger.exception('Failed processing streetlamp states', e)


async def proc_streetlamp_states() -> None:
    """Process streetlamp states."""
    last_id_seen = '0-0'
    t = 0.0
    while True:
        await proc_streetlamp_state_batch(
            last_id_seen=last_id_seen, batch_size=1000
        )
        if (time.time() - t) > 15 * 60:
            await run_agg_process()
            t = time.time()
        else:
            await asyncio.sleep(30)


async def _start() -> None:
    api.log.logger.info('api %s started', settings.NL_VERSION)

    async with api.postgres.get_session().begin() as db:
        seed_serv = api.services.SeedService(
            settings=settings,
            account_repo=api.repositories.AccountRepository(db),
            user_repo=api.repositories.UserRepository(db),
            dimming_profile_repo=api.repositories.DimmingProfileRepository(db),
            dimming_event_repo=api.repositories.DimmingEventRepository(db),
        )
        await seed_serv.sow()

    task = asyncio.create_task(proc_streetlamp_states())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)


async def _stop() -> None:
    await api.postgres.get_engine().dispose()
    api.log.logger.info('api %s stopped', settings.NL_VERSION)


@contextlib.asynccontextmanager
async def _lifespan(app: fastapi.FastAPI) -> AsyncGenerator:  # noqa: ARG001
    await _start()
    yield
    await _stop()


app = fastapi.FastAPI(
    lifespan=_lifespan,
    title='NetoLight',
    description='NetoLight API',
    version=settings.NL_VERSION,
)

router = fastapi.APIRouter(prefix='/api')

router.include_router(api.routers.tokens)
router.include_router(api.routers.users)
router.include_router(api.routers.accounts)
router.include_router(api.routers.devices)
router.include_router(api.routers.dimming_events)
router.include_router(api.routers.dimming_profiles)
router.include_router(api.routers.gateways)
router.include_router(api.routers.streetlamp_states)
router.include_router(api.routers.streetlamps)
router.include_router(api.routers.dashboards)

app.include_router(router)
