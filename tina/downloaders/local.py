from . import BaseDownloader


class LocalDownloader(BaseDownloader):
    @staticmethod
    def process(bundle_path):
        context = {
            'download_path': bundle_path
        }
        return 'tina/downloaders/local.html', context
