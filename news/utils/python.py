import importlib


def importpath(path):
    module_path = '.'.join(path.split('.')[:-1])
    name = path.split('.')[-1:][0]
    attr = getattr(importlib.import_module(module_path), name)
    return attr
