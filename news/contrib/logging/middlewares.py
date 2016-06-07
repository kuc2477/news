from functools import wraps, partial
from ...utils.logging import logger
from ...constants import LOG_URL_MAX_LENGTH


def logging_dispatch_middleware(reporter, dispatch):
    @wraps(dispatch)
    async def enhanced(*args, **kwargs):
        intel_count = len(getattr(reporter, '_intel', []))
        log = _log_factory(reporter)
        log('Dispatching reporter with {} intel'.format(intel_count))
        news_list = await dispatch(*args, **kwargs)
        log('Found {} news'.format(len(news_list)))
        return news_list
    return enhanced


def logging_fetch_middleware(reporter, fetch):
    @wraps(fetch)
    async def enhanced(*args, **kwargs):
        log = _log_factory(reporter)
        log('Fetch started')
        fetched = await fetch(*args, **kwargs)

        try:
            success_msg = 'Fetch successed'
            success_msg += ' [root status:{} ,{}]'.format(
                reporter.is_root,
                len(await reporter.get_visited())
            )
        except AttributeError:
            pass

        if fetched:
            log(success_msg)
        else:
            log('Fetch failed', tag='warning')
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
