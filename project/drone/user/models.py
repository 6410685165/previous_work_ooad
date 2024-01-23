
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	profile_pics = models.FileField(default='profile_pics/default.jpg', upload_to='profile_pics/', null=True)
	authorityType = [('ตำรวจจราจร', 'จร'),
					('ตํารวจส่วนท้องถิ่น', 'ตท'),
					('กรมทางหลวง+', 'ทล')]
	authority = models.CharField(blank=True, choices=authorityType, max_length=30)