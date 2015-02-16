### Django runs on this
web: bin/start-pgbouncer-stunnel newrelic-admin run-program gunicorn --config=lily/settings/gunicorn.py lily.wsgi:application

### Celery workers

## beat: Trigger tasks for all queues, and processes the ones in queue 'celery'
beat: bin/start-pgbouncer-stunnel newrelic-admin run-program celery worker -B --app=lily.celery --loglevel=info -Q celery -n beat.%h

## worker: Execute tasks in queue 'queue1'
worker1: bin/start-pgbouncer-stunnel newrelic-admin run-program celery worker --loglevel=info --app=lily.celery -Q queue1 -n worker1.%h -c 12 -P eventlet
