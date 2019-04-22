from celery import Celery
import os

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

#app = Celery('tasks',backend='rpc://', broker='amqp://guest@localhost:5672//')

app = Celery('tasks')
app.config_from_object('celeryconfig')

@app.task
def sum(x,y):
  return x + y + 1
