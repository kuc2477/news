#!/usr/bin/env python
""":mod:`news.cli` --- News cli

Provides command line based interface to news scheduling.

"""
import click

from .backends import (
    STORE_TABLE_NAME,
    STORE_PATH
)
from .utils import logger
from .backends.json import JSONBackend
from .site import Site
from .schedule import Schedule


def require_url(f):
    return click.argument('url')(f)

def optional_term(f):
    return click.option(
        '-t', '--term', type=int, default=180,
        help='cycle term in seconds for scrapping site'
    )(f)

def optional_backend_type(f):
    return click.option(
        '-b', '--backend', type=click.Choice(['json', 'django']),
        default='json', help='backend type to use'
    )(f)

def optional_path(f):
    return click.option(
        '--path', type=str, default=STORE_PATH,
        help='path to news store backend'
    )(f)

def optional_table(f):
    return click.option(
        '--table', type=str, default=STORE_TABLE_NAME,
        help='table name of page in news store backend database'
    )(f)

def optional_username(f):
    return click.option(
        '-u', '--username', type=str, default=None,
        help='news store backend database username'
    )(f)

def optional_password(f):
    return click.option(
        '-p', '--password', type=str, default=None,
        help='news store backend database password'
    )(f)

def optional_logging(f):
    return click.option('-s', '--silent', is_flag=True)(f)

def get_backend(backend_type, username=None, password=None,
                table=STORE_TABLE_NAME, path=STORE_PATH):
    if backend_type == 'json':
        return JSONBackend(path)
    else:
        raise click.BadOptionUsage

@click.group(help='Scheduled web post scrapper automated')
def main():
    pass

@click.command('schedule', help='Make news schedule')
@require_url
@optional_backend_type
@optional_username
@optional_password
@optional_table
@optional_path
@optional_term
@optional_logging
def schedule(url, backend, username, password, table, path, term, silent):
    backend = get_backend(backend, username, password, table, path)
    site = Site(url, backend)

    if not silent:
        logger.enable()
    else:
        logger.disable()

    schedule = Schedule(site, term)
    schedule.run()

@click.command('update', help='Update news')
@require_url
@optional_backend_type
@optional_username
@optional_password
@optional_table
@optional_path
@optional_logging
def update(url, backend, username, password, table, path, silent):
    backend = get_backend(backend, username, password, table, path)
    site = Site(url, backend)

    if not silent:
        logger.enable()
    else:
        logger.disable()

    schedule = Schedule(site)
    schedule.run_once()

@click.command('delete', help='Delete site pages from the store')
@require_url
@optional_backend_type
@optional_username
@optional_password
@optional_table
@optional_path
def delete(url, backend, username, password, table, path):
    backend = get_backend(backend, username, password, table, path)
    backend.delete_pages(*backend.get_pages(url))


main.add_command(schedule)
main.add_command(update)
main.add_command(delete)
