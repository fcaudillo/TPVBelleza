from kombu import Queue
import os
task_default_queueE = 'celeryx'
task_default_exchange = 'celeryx'
task_default_exchange_type = 'direct'



## Broker settings.
#broker_url = 'amqp://guest@rabbitmq:5672//'

broker_url = 'amqp://%s:%s@rabbitmq:5672//' % (os.environ['USUARIO_MQ'],os.environ['PASSWORD_MQ'])

broker_heartbeat = 10
# List of modules to import when the Celery worker starts.
imports = ('tasks',)

## Using the database to store task state and results.
#result_backend = 'db+sqlite:///results.db'
result_backend = 'rpc://'

#result_backend = 'amqp://' deprecated
result_persistent = False

