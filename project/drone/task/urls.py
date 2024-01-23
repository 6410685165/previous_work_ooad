from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'task'

urlpatterns = [
    path('',views.index,name='index'),
    path('upload/',views.upload,name='upload'),
    path('new_task/',views.new_task,name='new_task'),
    path('task_details/<int:task_id>/', views.task_details, name='task_details'),
    path('add_loop/<int:task_id>/', views.add_loop, name='add_loop'),
    path('new_loop/<int:task_id>/', views.new_loop, name='new_loop'),
    path('view_loop/<int:loop_id>/', views.view_loop, name='view_loop'),
    path('edit_loop/<int:loop_id>/', views.edit_loop, name='edit_loop'),
    path('delete_loop/<int:loop_id>/<int:task_id>/', views.delete_loop, name='delete_loop'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('search/', views.search, name='search'),
    path('result/<int:task_id>', views.results, name='results'),
    path('download_json/<str:summary>', views.download_json, name='download_json'),
] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

