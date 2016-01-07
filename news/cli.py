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

def get_site(url, brothers):
    return Site(url, brothers=[Site(u) for u in brothers])


# ========
# Commands
# ========

@click.group(help='Schedulable web scrapper automated')
def main():
    pass

@click.command('show', help='Show list of stored urls')
@optional_backend_type
@optional_path
def show(backend, path):
    backend = get_backend(backend, path)
    for url in backend.get_urls():
        print(url)

@click.command('schedule', help='Run news schedule')
@required_url
@optional_path
@optional_backend_type
@optional_maxdepth
@optional_maxdist
@optional_brother
@optional_cycle
@optional_logging
def schedule(
        url, path, backend, max_depth, max_distance,
        brother, cycle, silent):
    site = get_site(url, brother)
    backend = get_backend(backend, path)

    logger.set_mode(silent)
    schedule = Schedule(
        site, backend, cycle=cycle,
        maxdepth=max_depth, maxdist=max_dist
    )
    schedule.run()

@click.command('update', help='Update news')
@required_url
@optional_path
@optional_backend_type
@optional_maxdepth
@optional_maxdist
@optional_brother
@optional_logging
def update(url, path, backend, max_depth, max_distance, brother, silent):
    site = get_site(url, brother)
    backend = get_backend(backend, path)

    logger.set_mode(silent)
    schedule = Schedule(site, backend, maxdepth=max_depth, maxdist=max_distance)
    schedule.run_once()

@click.command('delete', help='Delete news')
@required_url
@optional_backend_type
@optional_path
def delete(url, backend, path):
    backend = get_backend(backend, path)
    backend.delete_pages(*backend.get_pages(url))


main.add_command(show)
main.add_command(schedule)
main.add_command(update)
main.add_command(delete)
