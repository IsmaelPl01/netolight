import logging
import os
import rpyc

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from rpyc.utils.server import ThreadedServer

from .log import logger


SQLALCHEMY_URL = os.getenv('NL_DIMMER_POSTGRES_URI')


class SchedulerService(rpyc.Service):

    def exposed_add_job(self, func, *args, **kwargs):
        return scheduler.add_job(func, *args, **kwargs)

    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        return scheduler.modify_job(job_id, jobstore, **changes)

    def exposed_reschedule_job(self, job_id, jobstore=None, trigger=None, **trigger_args):
        return scheduler.reschedule_job(job_id, jobstore, trigger, **trigger_args)

    def exposed_pause_job(self, job_id, jobstore=None):
        return scheduler.pause_job(job_id, jobstore)

    def exposed_resume_job(self, job_id, jobstore=None):
        return scheduler.resume_job(job_id, jobstore)

    def exposed_remove_job(self, job_id, jobstore=None):
        scheduler.remove_job(job_id, jobstore)

    def exposed_get_job(self, job_id):
        return scheduler.get_job(job_id)

    def exposed_get_jobs(self, jobstore=None):
        return scheduler.get_jobs(jobstore)


if __name__ == '__main__':

    scheduler = BackgroundScheduler(jobstores={
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_URL)
    })
    scheduler.start()

    proto_cfg = { 'allow_public_attrs': True }
    server = ThreadedServer(SchedulerService,
                            port=os.getenv('NL_DIMMER_PORT'),
                            protocol_config=proto_cfg)

    logger.info('dimmer started')

    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()

    logger.info('dimmer stopped')
