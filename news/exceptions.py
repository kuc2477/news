""":mod:`news.exceptions` --- Domain specific exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides domain specific news exceptions.

"""


class NewsException(Exception):
    """Base exception for all news domain specific errors."""


class HeterogenuousEngineError(NewsException):
    """Engine error that will be raised when either given sqlalchemy models
    doesn't share common engine"""
