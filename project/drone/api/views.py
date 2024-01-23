import os
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from api.serializer import VDOSerializer,StatusSerializer
from django.http import JsonResponse
from drone.tasks import run_detect
from drone.settings import MEDIA_ROOT

from api.models import VDO
from django_celery_results.models import TaskResult
from task.models import Task, Loop
from django.http import FileResponse
    
from django.shortcuts import get_object_or_404
import requests

from celery import current_app
from celery.signals import task_success, task_prerun, task_postrun, task_failure

from rest_framework.decorators import api_view
from rest_framework.response import Response
from user.models import Account
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse



# Create your views here.

# ViewSets define the view behavior.  
    
class VDOViewSet(ModelViewSet):
    queryset = VDO.objects.all()
    serializer_class = VDOSerializer
    # permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'get']

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            account = None
        else:
            account = Account.objects.get(user = user)

        task_id = request.POST.get('task_id')
        task = Task.objects.get(id = task_id)
        video = task.video
        loop = create_loop_file(task_id)
        
        if len(loop)> 0 and len(video)>0:
            fileobject = VDO.objects.create(loop=loop,vdo=video)
            loopname,vdoname =  os.path.join(MEDIA_ROOT,fileobject.loop.name),os.path.join(MEDIA_ROOT,fileobject.vdo.name)
            print(loopname,vdoname)
            res = run_detect.apply_async((loopname,vdoname))
            #convert task_id to pk
            response = Response(data=f"/status/{res.id}", status=status.HTTP_201_CREATED)  # NOQA
            ts = TaskResult.objects.get_task(res.id)
            ts.save()
            task.result = ts
            task.save()
            return HttpResponseRedirect(reverse('task:results', kwargs={'task_id': task_id}))
        else:
            return Response(data='Bad request.', status=status.HTTP_400_BAD_REQUEST)  
    

# @task_success.connect
# def handle_task_success(sender, result, **kwargs):

#     task_result = TaskResult.objects.get(task_id=sender.request.id)
#     task = Task.objects.get(result = task_result)
#     user = User.objects.get(username = task.owner)
    
#     print("success view")
#     return HttpResponseRedirect(reverse("task:noti"))


class StatusViewSet(ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = StatusSerializer
    # permission_classes = (IsAuthenticated,)
    http_method_names = ['post','get']
    def retrieve(self, request,pk=None):
        ts = TaskResult.objects.get_task(pk)
        sts = StatusSerializer(ts)
        return Response(sts.data)

def create_loop_file(task_id):
    task = Task.objects.get(id = task_id)
    loops = Loop.objects.filter(task = task)

    base_dir = settings.BASE_DIR
    
    data = []
    i = -1
    for loop in loops:
        data.append({
            "name":loop.loop_name,
            "id":str(i+1),
            "points":[
                {"x":loop.x1,"y":loop.y1},
                {"x":loop.x2,"y":loop.y2},
                {"x":loop.x3,"y":loop.y3},
                {"x":loop.x4,"y":loop.y4}
            ],
            "orientation":loop.orientation,
            "summary_location":{"x":loop.summary_location_x,"y":str(loop.summary_location_x)}
        })
    
    data = {
        "loops":data
    }
 
    if len(loops) == 0:
        file_path = str(base_dir)+"\\media/loops/loop.json"
        with open(file_path, 'r') as file:
            read_data = file.read()
        data = json.loads(read_data)
        for loop in data['loops']:
            name = loop['name']
            x1 = loop['points'][0]['x']
            y1 = loop['points'][0]['y']
            x2 = loop['points'][1]['x']
            y2 = loop['points'][1]['y']
            x3 = loop['points'][2]['x']
            y3 = loop['points'][2]['y']
            x4 = loop['points'][3]['x']
            y4 = loop['points'][3]['y']
            orientation = loop['orientation']
            sumX = loop['summary_location']['x']
            sumY = loop['summary_location']['y']
            loop = Loop.objects.create(task=task, loop_name=name, x1=x1, y1=y1, x2=x2, y2=y2,x3=x3, y3=y3, x4=x4, y4=y4,
                                       orientation=orientation, summary_location_x=sumX, summary_location_y=sumY)


    directory = str(base_dir)+"\\media/loops/"
    file_path = os.path.join(directory, f"loop{task_id}.json")
    os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist

    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
            print("JSON file created successfully.")
    except IOError:
        print("An error occurred while creating the JSON file.")

    return file_path

