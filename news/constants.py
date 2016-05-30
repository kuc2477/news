# ===============
# Option defaults
# ===============

DEFAULT_MAX_VISIT = 200
DEFAULT_EXT_BLACKLIST = ['png', 'jpg', 'gif', 'pdf', 'svg', 'zip']
DEFAULT_OPTIONS = {
    'max_dist': None,
    'max_visit': DEFAULT_MAX_VISIT,
    'ext_blacklist': DEFAULT_EXT_BLACKLIST,
    'url_whitelist': [],
    'url_blacklist': [],
}


# ==============
# Model defaults
# ==============

DEFAULT_SCHEDULE_TYPE = 'url'
DEFAULT_SCHEDULE_CYCLE = 300
SCHEDULE_TYPE_MAX_LENGTH = 30
AUTHOR_MAX_LENGTH = 100
TITLE_MAX_LENGTH = 300


# =========
# Scheduler
# =========

COVER_PUSHER_CYCLE = 5


# =========
# Persister
# =========

REDIS_PUBSUB_SLEEP_TIME = 0.001
REDIS_SCHEDULE_CREATE_CHANNEL = 'NEWS_SCHEDULE_CREATED'
REDIS_SCHEDULE_UPDATE_CHANNEL = 'NEWS_SCHEDULE_UPDATED'
REDIS_SCHEDULE_DELETE_CHANNEL = 'NEWS_SCHEDULE_DELETED'


# =======
# Logging
# =======

LOG_URL_MAX_LENGTH = 40
