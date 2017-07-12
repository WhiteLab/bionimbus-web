from . import BaseDownloader


class LocalDownloader(BaseDownloader):
    @staticmethod
    def process(payload_file):
        context = {
            'download_path': payload_file
        }
        return 'tina/downloader/local.html', context
