#!/usr/bin/env python
""":mod:`news.cli` --- News cli

Provides command line based interface to news scheduling.

"""
import os
import importlib

import click

from .utils import logger
from .backends.json import (
    STORE_PATH,
    JSONBackend,
)
from .site import Site
from .schedule import Schedule


# =================
# Option decorators
# =================

def required_url(f):
    return click.argument('url')(f)


def optional_cycle(f):
    return click.option(
        '-c', '--cycle', type=int, default=180,
        help='cycle in seconds for updating site pages'
    )(f)


def optional_brother(f):
    return click.option(
        '-b', '--brother', multiple=True,
        help='brother url of the site'
    )(f)


def optional_pipe(f):
    return click.option(
        '-p', '--pipe', multiple=True,
        help='path to page pipeline function'
    )(f)


def optional_on_start(f):
    return click.option(
        '--on-start', default=None,
        help='path to schedule fetch start callback'
    )(f)


def optional_on_complete(f):
    return click.option(
        '--on-complete', default=None,
        help='path to schedule update complete callback'
    )(f)


def optional_fetch_callback(f):
    return click.option(
        '--fetch-callback', multiple=True,
        help='path to fetch callback function'
    )(f)


def optional_add_callback(f):
    return click.option(
        '--add-callback', multiple=True,
        help='path to update callback function'
    )(f)


def optional_maxdepth(f):
    return click.option(
        '--max-depth', type=int, default=None,
        help='maximum depth to allow from the site to pages'
    )(f)


def optional_maxdist(f):
    return click.option(
        '--max-distance', type=int, default=None,
        help='maximum distance to allow from the site to pages'
    )(f)


def optional_backend_type(f):
    return click.option(
        '--backend-type', type=click.Choice(['json', 'django']),
        default='json', help='backend type to use'
    )(f)


def optional_backend_path(f):
    return click.option(
        '--backend-path', type=str, default=STORE_PATH,
        help='path to news store backend'
    )(f)


def optional_logging(f):
    return click.option(
        '-s', '--silent', is_flag=True, help='make logger silent'
    )(f)


# ===========
# Aux methods
# ===========

def get_backend(backend_type, path=STORE_PATH):
    if backend_type == 'json':
        return JSONBackend(path)

    elif backend_type == 'django':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', path)
        # Do lazy import after django settings module path set to avoid
        # `~django.core.exceptions.ImproperlyConfigured` error on import time.
        from .backends.django import DjangoBackend
        return DjangoBackend()


def get_function(path):
    if path is None:
        return None

    callback_name = path.split('.')[-1]
    module_path = path.replace(callback_name, '').rstrip('.')
    module = importlib.import_module(module_path)

    return getattr(module, callback_name)


# ========
# Commands
# ========

@click.group(help='Schedulable web scrapper automated')
def main():
    pass


@click.command('show', help='Show list of stored urls')
@optional_backend_type
@optional_backend_path
def show(backend_type, backend_path):
    backend_type = get_backend(backend_type, backend_path)
    for url in backend_type.get_urls():
        print(url)


@click.command('schedule', help='Run news schedule')
@required_url
@optional_backend_path
@optional_backend_type
@optional_maxdepth
@optional_maxdist
@optional_brother
@optional_on_start
@optional_on_complete
@optional_pipe
@optional_fetch_callback
@optional_add_callback
@optional_cycle
@optional_logging
def schedule(
        url, backend_path, backend_type, max_depth, max_distance, brother,
        on_start, on_complete, pipe, fetch_callback, add_callback,
        cycle, silent):
    site = Site(url)
    backend = get_backend(backend_type, backend_path)

    pipes = [get_function(p) for p in pipe]
    on_start = get_function(on_start)
    on_complete = get_function(on_complete)
    fetch_callbacks = [get_function(c) for c in fetch_callback]
    add_callbacks = [get_function(c) for c in add_callback]

    logger.set_mode(silent)
    schedule = Schedule(
        site, backend, cycle=cycle,
        maxdepth=max_depth, maxdist=max_distance,
        brothers=list(brother),
        on_start=on_start, on_complete=on_complete,
        fetch_callbacks=fetch_callbacks, add_callbacks=add_callbacks,
        pipes=pipes
    )
    schedule.run()


@click.command('update', help='Update news')
@required_url
@optional_backend_type
@optional_backend_path
@optional_maxdepth
@optional_maxdist
@optional_brother
@optional_on_start
@optional_on_complete
@optional_pipe
@optional_fetch_callback
@optional_add_callback
@optional_logging
def update(url, backend_type, backend_path, max_depth, max_distance, brother,
           on_start, on_complete, pipe, fetch_callback, add_callback, silent):
    site = Site(url)
    backend = get_backend(backend_type, backend_path)

    pipes = [get_function(p) for p in pipe]
    on_start = get_function(on_start)
    on_complete = get_function(on_complete)
    fetch_callbacks = [get_function(c) for c in fetch_callback]
    add_callbacks = [get_function(c) for c in add_callback]

    logger.set_mode(silent)
    schedule = Schedule(
        site, backend,
        maxdepth=max_depth, maxdist=max_distance,
        brothers=list(brother),
        on_start=on_start, on_complete=on_complete,
        fetch_callbacks=fetch_callbacks, add_callbacks=add_callbacks,
        pipes=pipes
    )
    schedule.run_once()


@click.command('delete', help='Delete news')
@required_url
@optional_backend_type
@optional_backend_path
def delete(url, backend_type, backend_path):
    backend = get_backend(backend_type, backend_path)
    backend.delete_pages(*backend.get_pages(url))


main.add_command(show)
main.add_command(schedule)
main.add_command(update)
main.add_command(delete)
