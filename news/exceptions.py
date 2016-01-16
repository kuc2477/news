""":mod:`news.exceptions` --- Errors and warnings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module maps generates exceptions and warnings.

"""


class NewsException(Exception):
    """All News-related exceptions are derived from this class."""


class NewsWarning(NewsException, Warning):
    """Base class for News-related warnings."""


class NewsError(NewsException):
    """Base class for News-related errors."""


class NewsFetalError(NewsException):
    """Base class for News-related fetal errors."""


#: (:class:`list`) A List of error/warning domains. The form of each elements
#: is follows (domain name, description, bases)
DOMAIN_MAP = [
    ('StoreDoesNotExist', 'Store doesn\'t exist in given configurations',
     (), [300, 400, 700]),
    ('InvalidStoreSchema', 'Store scheme is not valid',
     (), [305, 405, 705])
]


#: (:class:`list`) A list of (base_class, suffix) pairs (for each code).
#: It would be zipped with :const:`DOMAIN_MAP` pair's last element.
CODE_MAP = [
    (NewsWarning, 'Warning'),
    (NewsError, 'Error'),
    (NewsFetalError, 'FetalError')
]


#: (:class:`dict`) The dictionary of (code, exc_type).
TYPE_MAP = {}


for domain, description, bases, codes in DOMAIN_MAP:
    for code, (base, suffix) in zip(codes, CODE_MAP):
        name = domain + suffix
        locals()[name] = TYPE_MAP[code] = type(name, (base,) + bases, {
            '__doc__': description,
            'news_error_code': code
        })
