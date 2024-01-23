from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from user.models import Account
from django.http import HttpResponseRedirect
from django.urls import reverse
from task.models import Task, Loop
from api.models import VDO
from django_celery_results.models import TaskResult
import requests
from api.views import VDOViewSet
import json
import os
from django.conf import settings
from django.http import HttpResponse
from celery import Celery
from django.http import JsonResponse

# Create your views here.

def index(request):
    user = request.user
    if user.is_anonymous:
        return HttpResponseRedirect(reverse("user:signin"))
    elif user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)


    return render(request, "task/index.html", {
        'tasks': Task.objects.all(),
        'account': account,
    })

def upload(request):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)
    return render(request, "task/upload.html", {
        'account': account,
    })

def new_task(request):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)

    name = request.POST.get('name')
    location = request.POST.get('location')
    date_collect = request.POST.get('date_collect')
    authority_need = request.POST.getlist('authority_need')
    description = request.POST.get('description')
    video = request.FILES.get('vdo')

    new_task = Task.objects.create(owner = request.user.username)
    new_task.name = name
    new_task.location = location
    new_task.date_collect = date_collect
    new_task.authority_need = authority_need
    new_task.description = description
    new_task.video = video
    new_task.save()

    loops = Loop.objects.filter(task = new_task)
    return render(request, 'task/task_details.html', {
        'task': new_task,
        'account': account,
        'loops': loops,
    })

def task_details(request, task_id):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)
    task = Task.objects.get(id = task_id)

    if user.username != task.owner and not user.is_superuser:
        return HttpResponseRedirect(reverse("task:index"))
    else:
        loops = Loop.objects.filter(task = task)
        return render(request, "task/task_details.html", {
            'task': task,
            'account': account,
            'loops': loops,
        })

def add_loop(request, task_id):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)
    task = Task.objects.get(id = task_id)

    if user.username != task.owner:
        return HttpResponseRedirect(reverse("task:index"))

    return render(request, "task/add_loop.html", {
        'task': task,
        'account': account,
    })


def new_loop(request, task_id):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)

    loop_name = request.POST.get('loop_name')
    x1 = request.POST.get('x1')
    y1 = request.POST.get('y1')
    x2 = request.POST.get('x2')
    y2 = request.POST.get('y2')
    x3 = request.POST.get('x3')
    y3 = request.POST.get('y3')
    x4 = request.POST.get('x4')
    y4 = request.POST.get('y4')
    orientation = request.POST.get('orientation')
    summary_location_x = request.POST.get('summary_location_x')
    summary_location_y = request.POST.get('summary_location_y')

    task = Task.objects.get(id = task_id)
    new_loop = Loop.objects.create(task = task)
    new_loop.loop_name = loop_name
    new_loop.x1 = x1
    new_loop.y1 = y1
    new_loop.x2 = x2
    new_loop.y2 = y2
    new_loop.x3 = x3
    new_loop.y3 = y3
    new_loop.x4 = x4
    new_loop.y4 = y4
    new_loop.orientation = orientation
    new_loop.summary_location_x = summary_location_x
    new_loop.summary_location_y = summary_location_y
    new_loop.save()

    loops = Loop.objects.filter(task = task)

    return render(request, 'task/task_details.html', {
        'task': task,
        'account': account,
        'loops': loops,
    })

def view_loop(request, loop_id):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)
    loop = Loop.objects.get(id = loop_id)

    return render(request, "task/edit_loop.html", {
        'loop': loop,
        'account': account,
    })

def edit_loop(request, loop_id):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)

    loop_name = request.POST.get('loop_name')
    x1 = request.POST.get('x1')
    y1 = request.POST.get('y1')
    x2 = request.POST.get('x2')
    y2 = request.POST.get('y2')
    x3 = request.POST.get('x3')
    y3 = request.POST.get('y3')
    x4 = request.POST.get('x4')
    y4 = request.POST.get('y4')
    orientation = request.POST.get('orientation')
    summary_location_x = request.POST.get('summary_location_x')
    summary_location_y = request.POST.get('summary_location_y')

    loop = Loop.objects.get(id = loop_id)
    loop.loop_name = loop_name
    loop.x1 = x1
    loop.y1 = y1
    loop.x2 = x2
    loop.y2 = y2
    loop.x3 = x3
    loop.y3 = y3
    loop.x4 = x4
    loop.y4 = y4
    loop.orientation = orientation
    loop.summary_location_x = summary_location_x
    loop.summary_location_y = summary_location_y
    loop.save()

    task = loop.task
    loops = Loop.objects.filter(task = task)

    return render(request, 'task/task_details.html', {
        'task': task,
        'account': account,
        'loops': loops,
    })


def delete_loop(request, loop_id, task_id):
    task = Task.objects.get(id = task_id)
    if request.user.username != task.owner:
        return HttpResponseRedirect(reverse("task:index"))
    else:
        loop = Loop.objects.get(id = loop_id)
        loop.delete()
            
        return HttpResponseRedirect(reverse('task:task_details', kwargs={'task_id': task_id}))

def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.user.username == task.owner or request.user.is_superuser:
        loops = Loop.objects.filter(task = task)
        for loop in loops:
            loop.delete()

        task.delete()

        return HttpResponseRedirect(reverse("task:index"))
    
    else:
        return HttpResponseRedirect(reverse("task:index"))

def search(request):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)

    text = request.POST.get('search')
    all_task = Task.objects.all()
    tasks = []
    if text != "":
        for task in all_task:
            if text.lower() in task.name.lower():
                tasks.append(task)
        return render(request, "task/index.html", {
            "tasks": tasks,
            'account': account,
        })
    else:
        return HttpResponseRedirect(reverse('task:index'))


def results(request, task_id):
    user = request.user
    if user.is_superuser:
        account = None
    else:
        account = Account.objects.get(user = user)

    task = Task.objects.get(id = task_id)
    if task.result.status == "SUCCESS":
        loop_path, video_path = get_result_path(task_id)
        if os.path.exists(str(settings.BASE_DIR)+loop_path):
            summary_path = create_summary(task_id, loop_path)
        else:
            summary_path = create_summary(task_id, None)

        with open(summary_path, 'r') as file:
            json_data = file.read()
            summary = json.loads(json_data)
    else:
        video_path = task.video.url
        summary = None

    return render(request, "task/results.html", {
        'task': task,
        'account': account,
        'video': video_path,
        'summary': summary,
    })

def get_result_path(task_id):
    task = Task.objects.get(id = task_id)
    
    result_data = task.result.result
    result_data = result_data.strip("[]")
    file_paths = result_data.split(', ')

    loop = file_paths[0]
    loop_path = loop.replace('"', '')
    video = file_paths[1]
    video_path = video.replace('"', '')
    return loop_path, video_path

def create_summary(task_id, loop_path=None):
    task = Task.objects.get(id = task_id)
    loops = Loop.objects.filter(task = task)

    base_dir = settings.BASE_DIR

    data = []

    for i in range(len(loops)):
        lcar = 0
        ltruck = 0
        lbike = 0

        rcar = 0
        rtruck = 0
        rbike = 0

        scar = 0
        struck = 0
        sbike = 0

        if loop_path != None:
            loop_path_full = str(base_dir)+loop_path

            with open(loop_path_full, 'r') as file:
                read_data = file.read()

            read_data = read_data.split("\n")

            for j in read_data[:-1]:
                j = j.split(',')
                direction = j[-1]
                type = j[2]

                if int(j[0]) == i:
                    if direction == "LEFT":
                        if type == "car":
                            lcar += 1
                        elif type == "truck":
                            ltruck += 1
                        else:
                            lbike += 1
                    elif direction == "RIGHT":
                        if type == "car":
                            rcar += 1
                        elif type == "truck":
                            rtruck += 1
                        else:
                            rbike += 1
                    elif direction == "STRAIGHT":
                        if type == "car":
                            scar += 1
                        elif type == "truck":
                            struck += 1
                        else:
                            sbike += 1
        
        tcar = lcar+rcar+scar
        ttruck = ltruck+rtruck+struck
        tbike = lbike+rbike+sbike
        tall = tcar+ttruck+tbike
                    
        data.append({
            "name": loops[i].loop_name,
            "direction": ["", "Left", "Right", "Straight", "Total"],
            "type": [
                ["Car", lcar, rcar, scar, tcar],
                ["Truck", ltruck, rtruck, struck, ttruck],
                ["Bike", lbike, rbike, sbike, tbike],
                ["Total", lbike, rbike, sbike, tall],
            ]
        })

    sum_lcar = 0
    sum_ltruck = 0
    sum_lbike = 0

    sum_rcar = 0
    sum_rtruck = 0
    sum_rbike = 0

    sum_scar = 0
    sum_struck = 0
    sum_sbike = 0

    if loop_path != None:
        for d in data:
            sum_lcar += d['type'][0][1]
            sum_ltruck += d['type'][1][1]
            sum_lbike += d['type'][2][1]

            sum_rcar += d['type'][0][2]
            sum_rtruck += d['type'][1][2]
            sum_rbike += d['type'][2][2]

            sum_scar += d['type'][0][3]
            sum_struck += d['type'][1][3]
            sum_sbike += d['type'][2][3]

    sum_tcar = sum_lcar+sum_rcar+sum_scar
    sum_ttruck = sum_ltruck+sum_rtruck+sum_struck
    sum_tbike = sum_lbike+sum_rbike+sum_sbike
    sum_all = sum_tcar+sum_ttruck+sum_tbike
    summary = [{
        "type": [
            ["Car", sum_lcar, sum_rcar, sum_scar, sum_tcar],
            ["Truck", sum_ltruck, sum_rtruck, sum_struck, sum_ttruck],
            ["Bike", sum_lbike, sum_rbike, sum_sbike, sum_tbike],
            ["Total", sum_lbike, sum_rbike, sum_sbike, sum_all],
        ]}
    ]
    data = {
        "loops":data,
        "summary":summary
    }
    
    directory = str(base_dir)+"\\media/summary/"
    file_path = os.path.join(directory, f"data{task_id}.json")
    os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
 
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            print(f"JSON file {task_id} created successfully.")
    except IOError:
        print("An error occurred while creating the JSON file.")

    return file_path

def download_json(request, summary):

    response = HttpResponse(summary, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="summary.json"'
    return response

