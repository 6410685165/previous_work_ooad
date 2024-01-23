from django.urls import path, include
from rest_framework import routers
from api.views import *

from .views import StatusViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'upload', VDOViewSet, basename="upload")
router.register(r'status', StatusViewSet, basename="status")

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]