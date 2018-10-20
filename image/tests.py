import os
import io
from django.test import TestCase
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import Group
from account.models import ExtUser
from .models import Image


class ImageTestClass(TestCase):
    test_file_name = 'special_test_file_name.png'
    usr_data = { 'login': 'test-img@test.ru', 'password': '123'}

    @classmethod
    def setUpTestData(cls):
        Group.objects.get_or_create(name='User')
        cls.usr = ExtUser.objects.create_user(**cls.usr_data)

        super().setUpTestData()

    def media_file_exist(self, fname):
        return os.path.isfile( os.path.join(settings.MEDIA_ROOT, 'images', fname))

    def test_img(self):
        # Normal image file
        test_full_fname = settings.STATIC_ROOT+'/images/avatar_def.png'
        with open(test_full_fname, 'rb') as f:
            img = Image(user=self.usr)
            img.file.save(self.test_file_name, File(f))
            img.save()
            self.assertTrue(self.media_file_exist(self.test_file_name))

            img.delete()
            self.assertFalse(self.media_file_exist(self.test_file_name))



        # Bad image file
        def load_bad_file():
            f_text = io.StringIO("some initial text data")
            img = Image(user=self.usr)
            img.file.save(self.test_file_name, File(f_text))
            img.save()

        self.assertRaises(ValueError, load_bad_file)
        self.assertFalse(self.media_file_exist(self.test_file_name))