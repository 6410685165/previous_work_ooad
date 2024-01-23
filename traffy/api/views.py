import os
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.serializer import VDOSerializer,StatusSerializer

from traffy.tasks import run_detect
from traffy.settings import BASE_DIR

from api.models import VDO
from django_celery_results.models import TaskResult

class VDOViewSet(ModelViewSet):
    #queryset = VDO.objects.all()
    serializer_class = VDOSerializer
    #permission_classes = (IsAuthenticated,)
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):
        lp = request.FILES.getlist('loop', None)
        vdo = request.FILES.getlist('vdo', None)
        if len(lp)> 0 and len(vdo)>0:
            fileobject = VDO.objects.create(loop=lp[0],vdo=vdo[0])
            loopname,vdoname =  os.path.join(BASE_DIR,fileobject.loop.name),os.path.join(BASE_DIR,fileobject.vdo.name)
            print(loopname,vdoname)
            res = run_detect.apply_async((loopname,vdoname))
            #convert task_id to pk
            return Response(data=f"/status/{res.id}", status=status.HTTP_201_CREATED)  # NOQA
        else:
            return Response(data='Bad request.', status=status.HTTP_400_BAD_REQUEST)  

class StatusViewSet(ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = StatusSerializer
    #permission_classes = (IsAuthenticated,)
    http_method_names = ['post','get']
    def retrieve(self, request,pk=None):
        ts = TaskResult.objects.get_task(pk)
        sts = StatusSerializer(ts)
        return Response(sts.data)

'''
@api_view(['GET'])
def get_download_txt(request, job_id):
    # check if job exists and retrieve its status from the databas

    # return the status in the response
    return Response({'status': 'txt'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_download_vid(request, job_id):
    # check if job exists and retrieve its status from the database
    

    # return the status in the response
    return Response({'status': 'vid'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_job_status(request, job_id):
    # check if job exists and retrieve its status from the database
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    status = job.status

    # return the status in the response
    return Response({'status': status}, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_file(request):
    # Get the JSON payload from the request
    data = request.data.get('json_data')
    if not data:
        return Response({'error': 'JSON data is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the file upload from the request
    file = request.data.get('file')
    if not file:
        return Response({'error': 'File upload is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Save the JSON payload to a file
    with open(os.path.join('path/to/folder', 'data.json'), 'w') as f:
        f.write(data)

    # Save the file upload to a file
    with open(os.path.join('path/to/folder', file.name), 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    #call the job scheduler 
    res = add.delay(2,2)
    return Response({'success': f'JSON payload and file upload saved successfully. {res.id}'}, status=status.HTTP_201_CREATED)
'''
