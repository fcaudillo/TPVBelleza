from kombu import Queue
task_default_queueE = 'celeryx'
task_default_exchange = 'celeryx'
task_default_exchange_type = 'direct'



## Broker settings.
broker_url = 'amqp://guest@rabbitmq:5672//'

# List of modules to import when the Celery worker starts.
imports = ('tasks',)

## Using the database to store task state and results.
#result_backend = 'db+sqlite:///results.db'
result_backend = 'rpc://'

#result_backend = 'amqp://' deprecated
result_persistent = False

