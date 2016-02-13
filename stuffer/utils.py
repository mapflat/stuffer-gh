"""Unsorted utility classes and routines."""


def natural_repr(obj):
    if isinstance(obj, list) or isinstance(obj, tuple):
        return repr(map(natural_repr, obj))
    if isinstance(obj, dict):
        return repr(dict([map(natural_repr, kv) for kv in obj.items()]))
    return repr(obj)


def natural_object_repr(obj):
    return "{}({})".format(obj.__class__.__name__, ". ".join(
            ["{}={}".format(member, natural_repr(getattr(obj, member))) for member in dir(obj)
             if member[0] != '_' and not callable(getattr(obj, member))]))


class NaturalReprMixin(object):
    def __repr__(self):
        return natural_object_repr(self)