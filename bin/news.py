#!/usr/bin/env python
import click

from news.backends import STORE_TABLE_NAME
from news.backends.json import JSONBackend
from news.site import Site
from news.schedule import Schedule


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
        '--path', type=str, default=None,
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


@click.group()
def main():
    pass

@click.command()
@require_url
@optional_backend_type
@optional_username
@optional_password
@optional_table
@optional_path
@optional_term
def schedule(url, backend, username, password, path, term):
    pass

@click.command()
@require_url
@optional_backend_type
@optional_username
@optional_password
@optional_table
@optional_path
def update(url, backend, username, password, path):
    pass

@click.command()
@require_url
@optional_backend_type
@optional_username
@optional_password
@optional_table
@optional_path
def delete(url, backend, username, password):
    pass


main.add_command(schedule)
main.add_command(update)
main.add_command(delete)


if __name__ == "__main__":
    main()
