import os
from django.http import FileResponse
from django.conf import settings

from rest_framework.renderers import JSONRenderer
from rest_framework import status, permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django_filters import rest_framework as filters

from utils import IsOwnerPermission

from .models import Image
from .serializers import ImageSerializer
from .service import parse_path, resize


def resize_image(request):
    params = parse_path(request.path_info)
    if params:
        file_name = os.path.join(settings.MEDIA_ROOT, params['field'], params['file_name'])
        new_file, mimetype = resize(file_name, params['logic'], params['width'], params['height'])
        return FileResponse(open(new_file, 'rb'), content_type=mimetype)


class ImageFilter(filters.FilterSet):
    ids = filters.BaseInFilter(field_name='id')

    class Meta:
        model = Image
        fields = ['ids']

class ImageViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    renderer_classes = [JSONRenderer]
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ImageFilter

    def get_permissions(self):
        perm = [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            perm.append(IsOwnerPermission())
        return perm

    def perform_destroy(self, instance):
        instance.delete()

    def get_queryset(self):
        if self.action == 'list':
            data = self.request.query_params
            if not data.get('ids', None):
                return self.queryset.none()

        return self.queryset

    def create(self, request, *args, **kwargs):
        request.data.update({
            'user': request.user.pk,
        })
        return super().create(request, *args, **kwargs)

    @detail_route(methods=['post'])
    def rotate(self, request, pk):
        img = Image.objects.get(pk=pk)
        img.rotate()
        return Response(ImageSerializer(img).data, status=status.HTTP_200_OK)


    @detail_route(methods=['post'])
    def unrotate(self, request, pk):
        img = Image.objects.get(pk=pk)
        img.rotate(-90)
        return Response(ImageSerializer(img).data, status=status.HTTP_200_OK)
