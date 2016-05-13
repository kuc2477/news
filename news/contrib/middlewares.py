from bs4 import BeautifulSoup
from functools import wraps, partial
from ..utils.logging import logger
from ..constants import LOG_URL_MAX_LENGTH


def textifying_fetch_middleware(reporter, fetch):
    @wraps(fetch)
    def enhanced(r, *args, **kwargs):
        fetched = fetch(*args, **kwargs)

        soup = BeautifulSoup(fetched.content)
        for script in soup(['script', 'style']):
            script.extract()

        # get text from the response body
        plain_text = soup.get_text()
        lines = (l.strip() for l in plain_text.splitlines())
        chunks = (p.strip() for l in lines for p in l.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        fetched.content = text
        return fetched
    return enhanced


def logging_dispatch_middleware(reporter, dispatch):
    @wraps(dispatch)
    def enhanced(r, *args, **kwargs):
        log = _log_factory(r)
        log('Dispatching reporter with {} intel'.format(len(r.meta.intel)))
        news_list = dispatch(*args, **kwargs)
        log('Found {} news'.format(len(news_list)))
        return news_list
    return enhanced


def logging_fetch_middleware(reporter, fetch):
    @wraps(fetch)
    def enhanced(r, *args, **kwargs):
        log = _log_factory(r)
        log(r, 'Fetch started')
        fetched = fetch(*args, **kwargs)
        if fetched:
            log(r, 'Fetch successed')
        else:
            log(r, 'Fetch failed', tag='warning')
        return fetched
    return enhanced


def _log_reporter(reporter, message, tag='info'):
    id = reporter.schedule.id
    url = reporter.url[:LOG_URL_MAX_LENGTH] + '...' \
        if len(reporter.url) > LOG_URL_MAX_LENGTH else reporter.url

    title = '[Reporter of schedule {} for {}]'.format(id, url)
    logging_method = getattr(logger, tag)
    logging_method('{}: {}'.format(title, message))


def _log_factory(reporter):
    return partial(_log_reporter, reporter)
