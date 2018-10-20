import wand.image
import os
import re
from django.conf import settings
from django.db import models
from .service import resize, remove_resized_images
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import FieldError


class Image(models.Model):
    #blank=True TEMP
    file = models.ImageField(upload_to='images', blank=False, verbose_name=_('Файл'))
    old_file_name = models.CharField(max_length=200, default='')
    priority = models.IntegerField(default=0, blank=True, db_index=True, verbose_name=_('Приоритет'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Пользователь'))

    class Meta:
        ordering = ['pk']
        verbose_name = _('Картинка')
        verbose_name_plural = _('Картинки')

    def save(self, *args, **kwargs):
        is_new = False if self.pk else True

        super().save(*args, **kwargs)

        if is_new: # if self.file
            full_name = os.path.join(settings.MEDIA_ROOT, self.file.name)
            os.chmod(full_name, 0o664)

            try:
                with wand.image.Image(filename=full_name) as img:
                    w, h = img.size

                resize(full_name, 'a', width=850, height=850, replace=True)

            except Exception as exp:
                self.file.delete()
                raise ValueError(_('Это не картинка') )

        if is_new:
            if not self.priority:
                self.priority = self.pk
                super().save(force_update=True)


    def rotate(self, degree=90):
        image_name = self.file.name
        full_name = os.path.join(settings.MEDIA_ROOT, image_name)
        with wand.image.Image(filename=full_name) as img:
            img.rotate(degree)
            img.save(filename=full_name)
            remove_resized_images(image_name)

    def delete(self, *args, **kwargs):
        image_name = self.file.name
        full_name = os.path.join(settings.MEDIA_ROOT, image_name)
        res = super().delete(*args, **kwargs)
        if os.path.exists(full_name):
            os.remove(full_name)
            remove_resized_images(image_name)

        return res

    def __str__(self):
        return self.file.name