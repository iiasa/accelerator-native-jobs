from acc_worker.configs.Environment import get_environment_variables
from celery.schedules import crontab

env = get_environment_variables()

broker_url = env.CELERY_BROKER_URL

beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    'periodic_pvc_cleanup': {
        'task': 'acc_native_jobs.clean_unused_pvcs_task',
        'schedule': crontab(
            minute='*/15'
        ),
        'args': [],
    },
}