from functools import partial
from ...utils.logging import logger
from ...constants import LOG_URL_MAX_LENGTH


async def request_log_middleware(reporter, client_session):
    log = _log_factory(reporter)
    log('Fetch start')
    return client_session


async def response_log_middleware(reporter, response):
    log = _log_factory(reporter)
    if response.status == 200:
        log('Fetch success')
    else:
        log('Fetch failure', tag='warning')
    return response


def report_log_middleware(cover, news):
    log = _log_factory(cover.reporter)
    log('Reporting {} news'.format(len(news)))
    return news


def _log_reporter(reporter, message, tag='info'):
    id = reporter.schedule.id
    url = reporter.url[:LOG_URL_MAX_LENGTH] + '...' \
        if len(reporter.url) > LOG_URL_MAX_LENGTH else reporter.url

    title = '[Reporter of schedule {} for {}]'.format(id, url)
    logging_method = getattr(logger, tag)
    logging_method('{}: {}'.format(title, message))


def _log_factory(reporter):
    return partial(_log_reporter, reporter)
