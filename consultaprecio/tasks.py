from celery import Celery
import os

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

#app = Celery('tasks',backend='rpc://', broker='amqp://guest@localhost:5672//')

app = Celery('tasks')
app.config_from_object('celeryconfig')
app.conf.broker_heartbeat = 0


#@app.task
def sum(x,y):
  return x + y + 1

@app.task
def recarga(compania,plan,numero,monto):
  return "llamadalocalnosirve"