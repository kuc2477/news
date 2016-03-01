import importlib


def importattr(path):
    module_path = '.'.join(path.split('.')[:-1])
    middleware_name = path.split('.')[-1:][0]
    middleware = getattr(
        importlib.import_module(module_path),
        middleware_name
    )
    return middleware
