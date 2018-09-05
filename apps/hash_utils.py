# coding: utf-8
import copy
import json


def make_hash(o):
    """
    FROM: https://stackoverflow.com/a/8714242
    """
    if isinstance(o, (set, tuple, list)):
        return tuple([make_hash(e) for e in o])    

    elif not isinstance(o, dict):
        return hash(o)

    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)

    return hash(tuple(frozenset(sorted(new_o.items()))))


def make_hash_from_cartitem(attrs, extra_products):
    hash = 0
    if extra_products:
        x = copy.deepcopy(attrs)
        x.update(extra_products)
        hash = make_hash(x)
    else:
        hash = make_hash(attrs)
    return hash


def json_make_hash(d):
    """
    FROM: https://stackoverflow.com/a/22003440
    """
    return json.dumps(d, sort_keys=True)
