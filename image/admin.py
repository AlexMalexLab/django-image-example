
from .models import Image
from django.contrib import admin
from django.utils.html import mark_safe

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'small_shot', 'file_name']
    readonly_fields = ["original_shot"]
    search_fields = ['id', 'file']
    raw_id_fields = ['user']

    def file_name(self, obj):
        return obj.file.name if obj.file else '-'

    def small_shot(self, obj):
        if obj.file:
            return mark_safe(
                '<img src="{url}" width="200" alt="Image {id}"/>'
                    .format(url=obj.file.url, id=obj.id))
        else:
            return '-'

    def original_shot(self, obj):
        if obj.file:
            w = obj.file.width
            return mark_safe(
                '<img src="{url}" width="{width}"/>'
                    .format(url=obj.file.url, width=(w if w <= 400 else 400)))
        else:
            return '-'