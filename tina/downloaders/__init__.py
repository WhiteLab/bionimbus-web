from abc import ABCMeta, abstractmethod


class BaseDownloader(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def process(bundle_path):
        """
        This method should return a 2-tuple: (template_path, context_dict)
        """
        pass
