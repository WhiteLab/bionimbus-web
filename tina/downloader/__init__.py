import os
import uuid
from datetime import datetime
from abc import ABCMeta, abstractmethod
from django.conf import settings

from tina.models import Project


class BaseDownloader(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def process(payload_file):
        """
        This method should return a 2-tuple: (template_path, context_dict)
        """
        pass


def create_compressed_payload(paths_to_compress, for_windows=False):
    """
    What does libraries_to_download look like? Is it a list of actual Library models, or
    a list of strings of some sort?

    Does it return a path to where the compressed payload is? That seems best at first glance
    If so this location root should be configurable in settings.py or something

    :param libraries_to_download:
    :param on_windows:
    :return:
    """
    if for_windows:
        import zipfile
        pass
    else:
        import tarfile
        downloads_root = os.path.join(settings.MEDIA_ROOT, 'downloads')
        compressed_filename = '{username}_{date}_{project}_{short_uuid}.tar.gz'.format(
            username='test_user',
            date=datetime.now().strftime('%d%b%Y'),
            project='testproject',
            short_uuid=str(uuid.uuid4())[:8]
        )
        # compressed_filepath = os.path.join(settings.MEDIA_ROOT, 'downloads', 'test_samples.tar.gz')
        # compressed_filepath = '/home/dfitzgerald/workspace/PycharmProjects/tina/media/downloads/test_samples.tar.gz'
        with tarfile.open(os.path.join(downloads_root, compressed_filename), mode='w:gz') as compressed_file:
            for path in paths_to_compress:
                compressed_file.add(path, recursive=False)

        return os.path.join(settings.MEDIA_URL, 'downloads', compressed_filename)
