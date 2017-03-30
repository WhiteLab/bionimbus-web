from PIL import Image
from resizeimage import resizeimage

THUMBNAIL_SIZE = (265, 265)


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
