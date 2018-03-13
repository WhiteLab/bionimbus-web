def urljoin(*args):
    return '/'.join([u.strip('/') for u in args if u]) + ('/' if any(args) else '')