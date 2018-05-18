from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

from django.conf import settings

app = Celery('main')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# app.conf.update(
#     CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
# )


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# # celerybeat

# from celery.schedules import crontab

# app.conf.CELERYBEAT_SCHEDULE = {
#     'feed-aggregation-every-day': {
#         'task': 'ony_proj.tasks.feed_aggregation',
#         'schedule': crontab(minute=0, hour=2),  # 05:00 msk
#     },
#     #'test-every-day': {
#     #    'task': 'ony_proj.tasks.periodic_test',
#     #    'schedule': crontab(minute=0, hour=1),
#     #},
# }
# app.conf.CELERY_TIMEZONE = 'Europe/Moscow'
