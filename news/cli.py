#!/usr/bin/env python
""":mod:`news.cli` --- News cli

Provides command line based interface to news scheduling.

"""
import os

import click

from .utils import logger
from .backends.json import (
    STORE_PATH,
    JSONBackend,
)
from .site import Site
from .schedule import Schedule


def require_url(f):
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

def optional_backend_type(f):
    return click.option(
        '--backend', type=click.Choice(['json', 'django']),
        default='json', help='backend type to use'
    )(f)

def optional_path(f):
    return click.option(
        '-p', '--path', type=str, default=STORE_PATH,
        help='path to news store backend'
    )(f)

def optional_logging(f):
    return click.option(
        '-s', '--silent', is_flag=True, help='make logging silent'
    )(f)

def get_backend(backend_type, path=STORE_PATH):
    if backend_type == 'json':
        return JSONBackend(path)

    elif backend_type == 'django':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', path)
        # Do lazy import after django settings module path set to avoid
        # `~django.core.exceptions.ImproperlyConfigured` error on import time.
        from .backends.django import DjangoBackend
        return DjangoBackend()


@click.group(help='Schedulable web scrapper automated')
def main():
    pass

@click.command('show', help='show list of urls of stored news in the backend')
@optional_backend_type
@optional_path
def show(backend, path):
    backend = get_backend(backend, path)
    for url in backend.get_urls():
        print(url)

@click.command('schedule', help='Register and run news schedule')
@require_url
@optional_brother
@optional_backend_type
@optional_path
@optional_cycle
@optional_logging
def schedule(url, brother, backend, path, cycle, silent):
    backend = get_backend(backend, path)
    site = Site(url, backend, brothers=list(brother))

    if not silent:
        logger.enable()
    else:
        logger.disable()

    schedule = Schedule(site, cycle)
    schedule.run()

@click.command('update', help='Update news')
@require_url
@optional_brother
@optional_backend_type
@optional_path
@optional_logging
def update(url, brother, backend, path, silent):
    print(url)
    print(brother)
    print(backend)
    backend = get_backend(backend, path)
    site = Site(url, backend, brothers=list(brother))

    if not silent:
        logger.enable()
    else:
        logger.disable()

    schedule = Schedule(site)
    schedule.run_once()

@click.command('delete', help='Delete news from the store')
@require_url
@optional_backend_type
@optional_path
def delete(url, backend, path):
    backend = get_backend(backend, path)
    backend.delete_pages(*backend.get_pages(url))


main.add_command(show)
main.add_command(schedule)
main.add_command(update)
main.add_command(delete)
