#!/usr/bin/env python

import os.path


class Atter(object):
    pass


def upper_dir(path, level):
    for _ in range(level):
        path = os.path.dirname(path)
    return path


def module_to_class_name(name):
    return "".join(i.title() for i in name.split("_"))


def class_to_module_name(name):
    return_value = name[0].lower()
    for i in name[1:]:
        return_value += "_%s" % (i.lower(),) if "A" <= i <= "Z" else i
    return return_value
