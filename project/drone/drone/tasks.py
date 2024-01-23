
# from celery import shared_task
# from arial_car_track.engine import *


# @shared_task
# def run_detect(loopfile, vdofile):
#     saved_result = mymain(loopfile,vdofile)
    
#     return saved_result

# from celery import Celery
# app = Celery('tasks', broker='pyamqp://guest@localhost//')

# @app.task
# def add(x, y):
#     print("x+y=",x+y)
#     return x + y


from celery import shared_task
from detect_and_track import mymain


@shared_task
def run_detect(loopfile, vdofile):
    saved_result = mymain(cmd=False,custom_arg=['--loop',loopfile,'--source',vdofile])
    
    return saved_result
"""
from celery import Celery
app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    print("x+y=",x+y)
    return x + y
"""
