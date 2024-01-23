from rest_framework.serializers import ModelSerializer
from rest_framework import exceptions
from api.models import VDO
from django_celery_results.models import TaskResult
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets

# Serializers define the API representation.
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['url', 'username', 'email', 'is_staff']


class VDOSerializer(ModelSerializer):

    def create(self, validated_data):
        newvdo_record = self.Meta.model.objects.create(**validated_data)
        return newvdo_record

    class Meta:
        model = VDO
        fields = '__all__'

class StatusSerializer(ModelSerializer):

    def create(self, validated_data):
        newvdo_record = self.Meta.model.objects.create(**validated_data)
        return newvdo_record

    class Meta:
        model = TaskResult
        fields = 'task_id','status','result'
