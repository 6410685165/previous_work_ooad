from django.db import models
import datetime
from api.models import VDO
from django_celery_results.models import TaskResult

# Create your models here.
class Task(models.Model):
    owner = models.CharField(max_length=1000, blank=True)
    name = models.CharField(max_length=1000, blank=True)
    location = models.CharField(max_length=1000, blank=True)
    authority_need = models.CharField(max_length=1000, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    date_collect = models.DateField(default=datetime.date.today)
    date_modify = models.DateTimeField(default=datetime.datetime.now)
    date_upload = models.DateTimeField(default=datetime.datetime.now)
    video = models.FileField(upload_to='videos/', null=True, verbose_name="")
    result = models.ForeignKey(TaskResult,on_delete=models.CASCADE, null=True)

class Loop(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, default=None)
    loop_name = models.CharField(max_length=1000, blank=True)
    x1 = models.IntegerField(null=True)
    y1 = models.IntegerField(null=True)
    x2 = models.IntegerField(null=True)
    y2 = models.IntegerField(null=True)
    x3 = models.IntegerField(null=True)
    y3 = models.IntegerField(null=True)
    x4 = models.IntegerField(null=True)
    y4 = models.IntegerField(null=True)
    orientation = models.CharField(choices=[("cw", "clockwise"), ("ctcw", "counterclockwise")], default="cw", max_length=100)
    summary_location_x = models.IntegerField(null=True)
    summary_location_y = models.IntegerField(null=True)