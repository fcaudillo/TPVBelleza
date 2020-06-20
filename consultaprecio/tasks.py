#fdcp from celery import Celery
import os

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

#app = Celery('tasks',backend='rpc://', broker='amqp://guest@localhost:5672//')

#fdcp app = Celery('tasks')
#fdcp app.config_from_object('celeryconfig')
#fdcp app.conf.broker_heartbeat = 0


#@app.task
def sum(x,y):
  return x + y + 1

#fdcp @app.task
def recarga(compania,plan,numero,monto):
  return "llamadalocalnosirve"

#fdcp @app.task
def consultaSaldo():
  return "LLamadadummynosirve"
