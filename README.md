# django-image-example
It's part of planengo.ru

Это django 2.0 приложение для хранения и обработки изображений на сайте.

- Модель для хранения файлов, которые потом подключаются как ManyToMany к другим Django приложениями
- Функции предварительного ресайза и ресайза по требованию

Подключение в файле settings.py
```python

INSTALLED_APPS = [
...
'image.apps.ImageConfig',
...
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

```

в urls.py
```python
urlpatterns += [...
    path('image/', include('image.urls', namespace='image')),
...]
```

В файловой системе по MEDIA_ROOT создаем каталог images и необходимые подкаталоги, 
в которые будут сохраняться файлы после ресайза. Например, s_100x100, w_800x300

Формат каталога важен и определяется по шаблону.
```python
def parse_path(path):
    match = re.search(r'/(\w+)/((a|s|w|h)_([0-9]+)?(x([0-9]+))?)/(.+?\.(jpg|jpeg|gif|png))$', path, re.IGNORECASE)
    if match:
        return {
            'path': match.group(0),
            'field': match.group(1),
            'sub_dir': match.group(2),
            'logic': match.group(3),
            'width': match.group(4),
            'height': match.group(6),
            'file_name': match.group(7),
            'ext': match.group(8)
        }
    return False
```

Первая буква - это алгоритм ресайза, затем подчеркивание, потом ширина и знак x и высота картинки.
Сейчас реализованы алгоритмы:
- а - произвольное сжатие по высоте или ширине до любой границы ширины или высоты
- s - строгое сжатие в квадрат. 
- w - сжатие до заданной ширины и обрезка по высоте 


Необходимо должным образом настроить ваш сервер, чтобы он отдавал сжатый файл или передавал запрос в приложение для его создания 

Например в Nginx:
```
server {
...
location /media  {
  alias YOUR-PATH/media;  
  if (!-f $request_filename) {
      rewrite (?i)^/media/((images|avatar)/(a|s|w|h)_([0-9]+)?(x[0-9]+)?/.+?\.(jpg|jpeg|gif|png))$ /image/resize/$1 last;
  }
}

...
}
```
Теперь в шаблонах Django можно указывать ссылки на файлы нужного размера через специальные теги 

```html
{% load static %}
{% load resize %}
...
<img src="{% get_media_prefix %}{{ user.avatar.name|resize:'s_36x36' }" alt="{{ user.name }}">
...
```

Сжатые файлы будут создаваться автоматически.

**Данный код реально работает на сайте https://planengo.ru/**
