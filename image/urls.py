from django.urls import path, re_path

from rest_framework import routers
from .views import ImageViewSet, resize_image

app_name = 'image'

router = routers.SimpleRouter()
router.register(r'api', ImageViewSet)

urlpatterns = [
    re_path(r'^resize/', resize_image),
]
urlpatterns += router.urls


