import re
import os
import wand.image
from django.conf import settings


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


def build_path(logic, width=None, height=None):
    return '{}_{}{}'.format(logic, width or '', 'x{}'.format(height) if height else '')


def remove_resized_images(file_name=None):
    p = re.compile(r'(a|s|w|h)_([0-9]+)?(x[0-9]+)?')
    uploads_dir = os.path.join(settings.MEDIA_ROOT, os.path.dirname(file_name or ''))
    dirs = [img_dir for img_dir in os.walk(uploads_dir).__next__()[1] if re.match(p, img_dir)]
    for img_dir in dirs:
        if file_name:
            full_name = os.path.join(uploads_dir, img_dir, os.path.basename(file_name))
            if os.path.exists(full_name) and os.path.isfile(full_name):
                os.remove(full_name)
        else:
            for one_file in os.listdir(os.path.join(uploads_dir, img_dir)):
                full_name = os.path.join(uploads_dir, img_dir, os.path.basename(one_file))
                if os.path.isfile(full_name):
                    os.remove(full_name)


def resize(src_file_name, logic, width=None, height=None, replace=False):
    assert os.path.exists(src_file_name), ' '.join([src_file_name, 'not found'])

    with wand.image.Image(filename=src_file_name) as img:
        if logic not in ['a', 's', 'w', 'h']:
            raise Exception('logic.resize')

        if logic == 'a' and (width or height):
            if width and height:
                img.transform(resize='{0}x{1}'.format(width, height))
            elif width:
                img.transform(resize=str(width))
            elif height:
                img.transform(resize='x{}'.format(height))
            else:
                raise Exception('logic.resize')
        elif logic == 's' and width:
            size = int(width)
            if img.height > img.width:
                img.transform(resize=str(size))
            else:
                img.transform(resize='x{}'.format(size))
            img.crop(width=size, height=size, gravity='center')
        elif logic == 'w' and width and height:
            img.transform(resize=str(width))
            img.crop(width=int(width), height=int(height), gravity='center')
        else:
            raise Exception('logic.resize')

        orientation = img.metadata.get('exif:Orientation')
        if orientation:
            img.auto_orient()

        # img.reresolution = 72
        # img.compression_quality = 60

        if replace:
            out_filename = src_file_name
        else:
            sub_dir = build_path(logic, width, height)
            out_filename = os.path.join(os.path.dirname(src_file_name), sub_dir, os.path.basename(src_file_name))

        img.save(filename=out_filename)

        extension = os.path.splitext(src_file_name)[1][1:]
        if extension.lower() in ['jpeg', 'jpg']:
            os.system('jpegtran -copy none -optimize -outfile "{}" "{}"'.format(out_filename, out_filename))

        return out_filename, img.mimetype