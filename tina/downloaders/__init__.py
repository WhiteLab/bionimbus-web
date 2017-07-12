from abc import ABCMeta, abstractmethod


class BaseDownloader(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def process(payload_file):
        """
        This method should return a 2-tuple: (template_path, context_dict)
        """
        pass
