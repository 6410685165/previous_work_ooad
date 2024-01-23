from django.db import models

# Create your models here.
class VDO(models.Model):
    loop = models.FileField(upload_to='vdo/%Y/%m/%d/%H/%M')
    vdo =  models.FileField(upload_to='vdo/%Y/%m/%d/%H/%M')

