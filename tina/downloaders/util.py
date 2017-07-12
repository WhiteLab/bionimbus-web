import os
import uuid
from datetime import datetime

from django.conf import settings

FIRST = 0


def create_bundle(libraries_to_bundle, for_windows=False):
    """
    What does libraries_to_download look like? Is it a list of actual Library models, or
    a list of strings of some sort?

    Does it return a path to where the compressed payload is? That seems best at first glance
    If so this location root should be configurable in settings.py or something

    :param libraries_to_download:
    :param on_windows:
    :return:
    """
    downloads_root = os.path.join(settings.MEDIA_ROOT, 'downloads')
    bundle_filename = '{username}_{date}_{project}_{short_uuid}.{extension}'.format(
        username='test_user',
        date=datetime.now().strftime('%d%b%Y'),
        project='testproject',
        short_uuid=str(uuid.uuid4())[:8],
        extension='zip' if for_windows else 'tar.gz'
    )

    if for_windows:
        import zipfile
        bundle_filehandle = zipfile.ZipFile(os.path.join(downloads_root, bundle_filename), mode='w')
    else:
        import tarfile
        bundle_filehandle = tarfile.open(os.path.join(downloads_root, bundle_filename), mode='w:gz')

    with bundle_filehandle as bundle:
        add_to_bundle = bundle.write if for_windows else bundle.add
        for lib_data_dir, lib_data_paths in _format_for_bundling(libraries_to_bundle):
            for lib_data_path in lib_data_paths:
                lib_data_arcname = os.path.join(lib_data_dir, os.path.basename(lib_data_path))
                add_to_bundle(lib_data_path, arcname=lib_data_arcname)

    return os.path.join(settings.MEDIA_URL, 'downloads', bundle_filename)


def _format_lineage_to_directories(entity_lineage):
    # If lineage is blank return empty string
    if len(entity_lineage) < 1:
        return ''
    # If lineage is return as strings, treat each as separate directory
    elif isinstance(entity_lineage[FIRST], unicode) or isinstance(entity_lineage[FIRST], str):
        return os.path.join(*entity_lineage).replace(' ', '_')

    # If model type information is available, group together common models as a single dir
    lineage_groups = [entity_lineage[FIRST].name]
    for i, entity in enumerate(entity_lineage[1:], start=1):
        if isinstance(entity, type(entity_lineage[i - 1])):
            lineage_groups[-1] = '__'.join((lineage_groups[-1], entity.name))
        else:
            lineage_groups.append(entity.name)
    return os.path.join(*lineage_groups).replace(' ', '_')


def _format_for_bundling(libraries_to_bundle):
    return [
        (
            _format_lineage_to_directories(library.lineage()),
            [ld.path for ld in library.librarydata_set.all()]
        )
        for library in libraries_to_bundle
    ]
