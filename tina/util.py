import json
from copy import copy
from collections import deque, defaultdict, namedtuple

import couchdb
from PIL import Image
from resizeimage import resizeimage

from ua_parser import user_agent_parser
from django.conf import settings
from django.apps import apps

import tina.models

THUMBNAIL_SIZE = (265, 265)
FIRST, LAST = 0, -1


def find_is_windows(request):
    ua_string = request.META['HTTP_USER_AGENT']
    print user_agent_parser.Parse(ua_string)
    request.session['is_windows'] = 'windows' in user_agent_parser.Parse(ua_string)['os']['family'].lower()
    return request.session['is_windows']


def resize_project_thumbnail(fullpath, size=THUMBNAIL_SIZE):
    # If a single int is given, assume a square of that size
    if type(size) == int:
        size = (size, size)

    # Resize and replace the given image
    with open(fullpath, 'r+b') as original_image:
        with Image.open(original_image) as img:
            thumbnail = resizeimage.resize_thumbnail(img, size)
            thumbnail.save(fullpath, img.format)


def generate_html(tag, attrs=None, self_closing=False, content=''):
    """
    Generates a literal HTML tag. If the tag argument is a dictionary, it must be of the form:
        {
            'tag': 'Name of the tag',
            'attrs': {'key1': 'val1', 'key2': 'val2'},
            'self_closing': False,
            'content': 'Hello World!'
        }
    Only 'tag' is required; omission of the other keys will result in their argument defaults

    :param tag: str|dict Name of the tag, or a dictionary containing all required elements
    :param attrs: dict Key-value mappings of attribute names to values
    :param self_closing: bool Whether the tag should be self closing
    :param content: str Content between tags; ignored if self_closing=True
    :return: str The literal HTML tag
    """
    self_closing_template = '<{tag} {attrs} />'
    content_template = '<{tag} {attrs}>{content}</{tag}>'

    # Check if the tag argument is a dict
    if type(tag) == dict:
        # If the 'tag' key doesn't exist or isn't a string, throw an exception
        if type(tag['tag']) != str:
            raise TypeError('Tag must be a string')
        tag_tag = tag['tag']  # Will throw KeyError if 'tag' is not present

        # Get other keys, or fall back to argument defaults
        tag_attrs = tag.get('attrs', None)
        tag_self_closing = tag.get('self_closing', False)
        tag_content = tag.get('content', '')

    # Check if the tag argument is a string
    elif type(tag) == str:
        tag_tag = tag
        tag_attrs = attrs
        tag_self_closing = self_closing
        tag_content = content

    # If the tag argument isn't a dict or str, throw an exception
    else:
        raise TypeError('\'tag\' argument must be either str or dict')

    # Build the tag and return
    attrs = (' '.join([
                '{key}="{val}"'.format(key=k, val=v)
                for k, v in tag_attrs.iteritems()
            ]) if tag_attrs else '')
    tag_template = self_closing_template if tag_self_closing else content_template

    tag_dict = dict(
        [('tag', tag_tag), ('attrs', attrs)] +
        ([('content', tag_content)] if not tag_self_closing else [])
    )

    return tag_template.format(**tag_dict)


class TinaCouchDB(object):
    """
    Utility methods are dealing with the documents in the Tina CouchDB database.
    """
    @staticmethod
    def format_handson_data(json_str):
        """
        Converts a JSON string to a Python dictionary. This JSON object will a bunch of 
        key-value pairs. If the key field is blank, that entry is discarded.
        """
        return dict([m for m in json.loads(json_str) if m[0]])

    @staticmethod
    def _get_tina_db():
        """
        Returns the Tina CouchDB database as configured in settings.py.
        """
        return couchdb.Server(settings.COUCH_SERVER)[settings.COUCH_TINA_DB]

    @staticmethod
    def get_tina_doc(doc_id, include_meta=True):
        """
        Retrieves the document with _id corresponding to doc_id. If include_meta is 
        False, the _rev and _id fields will be removed, leaving only the document body.
        """
        tina_db = TinaCouchDB._get_tina_db()
        if include_meta:
            return tina_db.get(doc_id)
        doc = tina_db.get(doc_id)
        doc.pop('_rev')
        doc.pop('_id')
        return doc

    @staticmethod
    def save_tina_doc(doc_body):
        """
        Given a Python dictionary object or something similar, will save the document to 
        the Tina CouchDB database as configured in settings.py.
        """
        return TinaCouchDB._get_tina_db().save(doc_body)

    @staticmethod
    def update_tina_doc(doc_id, update_doc_body):
        """
        Updates the document with _id corresponding to doc_id. Any keys not present will be 
        added, any keys present will have values overwritten, and keys that aren't in the 
        updated dictionary will be removed from the document.
        """
        tina_db = TinaCouchDB._get_tina_db()
        old_doc = TinaCouchDB.get_tina_doc(doc_id)
        new_doc = couchdb.Document({'_id': old_doc['_id'], '_rev': old_doc['_rev']})
        new_doc.update(update_doc_body)
        tina_db.save(new_doc)

    @staticmethod
    def delete_tina_doc(doc_id):
        """
        Deletes the document with _id corresponding to doc_id.
        """
        tina_db = TinaCouchDB._get_tina_db()
        try:
            tina_db.delete(TinaCouchDB.get_tina_doc(doc_id))
        except couchdb.ResourceConflict:
            raise


class HierarchyEntity(object):
    @staticmethod
    def get_hierarchy(as_strings=True, include_terminal=False):
        """
        Returns the entity hierarchy from the top down.

        :param as_strings: bool If True, will return entities by their string name
        :param include_terminal: bool If True, will include the terminal entity
        :return: list The entity hierarchy from the top down
        """
        hierarchy = [e for e in apps.get_models() if getattr(e, '_initial_entity', False)]

        # Loop through children until the terminal entity is reached
        curr_entity = hierarchy[FIRST].child_class()
        while not getattr(curr_entity, '_terminal_entity', False):
            hierarchy.append(curr_entity)
            curr_entity = curr_entity.child_class()

        # If include_terminal is True, add the terminal entity to hierarchy
        if include_terminal:
            hierarchy.append(curr_entity)

        if as_strings:
            return [e.__name__ for e in hierarchy]
        return hierarchy


class LibraryTable(object):
    """
    Utility methods related to render the display table for viewing Libraries
    """
    TableRow = namedtuple('TableRow', 'library_inst row_content')

    def __init__(self, libraries, columns):
        self.table = defaultdict(list)

        # Get all Libraries grouped by it's immediate superior model
        for library in libraries.order_by('parent_model'):
            row_content = [str(getattr(library, col, '')) for col in columns]
            self.table[library.parent_model.lineage(to_root=False)].append(
                LibraryTable.TableRow(library_inst=library, row_content=row_content)
            )
        self.table = dict(self.table)

    def groupby(self, groupby_entity):
        # If the user requests a higher level model, do that here until it's satisfied
        while not isinstance(next(self.table.iterkeys())[LAST], groupby_entity):
            _table = dict()
            for grouping, table_rows in self.table.iteritems():
                new_grouping, moving_entity = grouping[:LAST], grouping[LAST]
                for table_row in table_rows:
                    table_row.row_content.append(moving_entity.name)
                _table[new_grouping] = table_rows
            self.table = _table

        return self

    def groups_to_str(self):
        # Convert tuple keys to string keys
        _table = dict()
        for grouping, table_rows in self.table.iteritems():
            header_str = ' > '.join([e.name for e in grouping])
            _table[header_str] = table_rows
        self.table = _table

        return self

    def to_json(self):
        json_obj = list()
        for grouping, table_rows in self.table.iteritems():
            json_obj.append({
                'groupData': [table_row.row_content for table_row in table_rows],
                'header': grouping
            })
        return json.dumps(json_obj)

    def render(self):
        import random
        import string
        for grouping, table_rows in self.table.iteritems():
            for table_row in table_rows:
                table_row.row_content.extend([''.join([string.ascii_letters[random.randint(0,51)] for i in range(random.randint(1,100))]) for s in range(4)])
        return self.table

    # @staticmethod
    # def _groupby(groupby_entity):
    #     library_display_table = defaultdict(list)
    #     # TODO Filter on Projects the User is assigned to
    #     # Get all Libraries grouped by it's immediate superior model
    #     for library in tina.models.Library.objects.all().order_by('parent_model'):
    #         library_display_table[library.parent_model.lineage(to_root=False)].append(
    #             deque([library])
    #         )
    #
    #     # If the user requests a higher level model, do that here until it's satisfied
    #     while not isinstance(next(library_display_table.iterkeys())[LAST], groupby_entity):
    #         _table = dict()
    #         for grouping, table_rows in library_display_table.iteritems():
    #             new_grouping, moving_entity = grouping[:LAST], grouping[LAST]
    #             for table_row in table_rows:
    #                 table_row.appendleft(moving_entity.name)
    #             _table[new_grouping] = table_rows
    #         library_display_table = _table
    #
    #     # Convert tuple keys to string keys
    #     _table = dict()
    #     for grouping, table_rows in library_display_table.iteritems():
    #         header_str = ' > '.join([e.name for e in grouping])
    #         _table[header_str] = table_rows
    #
    #     return _table
