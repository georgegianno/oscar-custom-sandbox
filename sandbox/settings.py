import os
import environ
import oscar
import pathlib
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

env = environ.Env()

# Path helper
location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

EMAIL_SUBJECT_PREFIX = '[Oscar sandbox] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use a Sqlite database by default
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': os.path.join(BASE_DIR, 'sandbox', 'db.sqlite'),
        # 'ATOMIC_REQUESTS': True,
    }
}

CACHES = {
    'default': env.cache(default='locmemcache://'),
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SELECT2_CACHE_BACKEND = 'select2'
CACHE_PREFIX= 'select2_'
JS= '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js'
SELECT2_JS = 'assets/js/select2.min.js'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
USE_TZ = True
TIME_ZONE = 'Europe/London'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

# Includes all languages that have >50% coverage in Transifex
# Taken from Django's default setting for LANGUAGES
gettext_noop = lambda s: s
LANGUAGES = (
    ('ar', gettext_noop('Arabic')),
    ('ca', gettext_noop('Catalan')),
    ('cs', gettext_noop('Czech')),
    ('da', gettext_noop('Danish')),
    ('de', gettext_noop('German')),
    ('en-gb', gettext_noop('British English')),
    ('el', gettext_noop('Greek')),
    ('es', gettext_noop('Spanish')),
    ('fi', gettext_noop('Finnish')),
    ('fr', gettext_noop('French')),
    ('it', gettext_noop('Italian')),
    ('ko', gettext_noop('Korean')),
    ('nl', gettext_noop('Dutch')),
    ('pl', gettext_noop('Polish')),
    ('pt', gettext_noop('Portuguese')),
    ('pt-br', gettext_noop('Brazilian Portuguese')),
    ('ro', gettext_noop('Romanian')),
    ('ru', gettext_noop('Russian')),
    ('sk', gettext_noop('Slovak')),
    ('uk', gettext_noop('Ukrainian')),
    ('zh-cn', gettext_noop('Simplified Chinese')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = location("public/media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATIC_ROOT = location('public/static')
STATICFILES_DIRS = (
    location('static/'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/dev/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Make this unique, and don't share it with anybody.
SECRET_KEY = env.str('SECRET_KEY', default='UajFCuyjDKmWHe29neauXzHi9eZoRXr6RMbT5JyAdPiACBP6Cra2')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            location('templates'),
        ],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',

                # Oscar specific
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.communication.notifications.context_processors.notifications',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.core.context_processors.metadata',
            ],
            'debug': DEBUG,
        }
    }
]

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',

    # Allow languages to be selected
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.common.CommonMiddleware',

    # Ensure a valid basket is added to the request instance for every request
    'oscar.apps.basket.middleware.BasketMiddleware',
    'oscar.apps.promo.middleware.PromoMiddleware',

]

ROOT_URLCONF = 'urls'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        },
        'simple': {
            'format': '[%(asctime)s] %(message)s'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'oscar': {
            'level': 'DEBUG',
            'propagate': True,
        },
        'oscar.catalogue.import': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'oscar.alerts': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': False,
        },

        # Django loggers
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'WARNING',
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },

        # Third party
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sorl.thumbnail': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',

    'oscar.apps.promo',
    'oscar.apps.promo.promo_dashboard',
    'oscar.config.Shop',
    'oscar.apps.analytics.apps.AnalyticsConfig',
    'oscar.apps.checkout.apps.CheckoutConfig',
    'oscar.apps.address.apps.AddressConfig',
    'oscar.apps.shipping.apps.ShippingConfig',
    'oscar.apps.catalogue.apps.CatalogueConfig',
    'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
    'oscar.apps.communication.apps.CommunicationConfig',
    'oscar.apps.partner.apps.PartnerConfig',
    'oscar.apps.basket.apps.BasketConfig',
    'oscar.apps.payment.apps.PaymentConfig',
    'oscar.apps.offer.apps.OfferConfig',
    'oscar.apps.order.apps.OrderConfig',
    'oscar.apps.customer.apps.CustomerConfig',
    'oscar.apps.search.apps.SearchConfig',
    'oscar.apps.voucher.apps.VoucherConfig',
    'oscar.apps.wishlists.apps.WishlistsConfig',
    'oscar.apps.dashboard.apps.DashboardConfig',
    'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
    'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
    'oscar.apps.dashboard.orders.apps.OrdersDashboardConfig',
    'oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',

    # 3rd-party apps that Oscar depends on
    'widget_tweaks',
    'haystack',
    'treebeard',
    'sorl.thumbnail',
    'easy_thumbnails',
    'django_tables2',

    # Django apps that the sandbox depends on
    'django.contrib.sitemaps',
    'django_select2',


    # 3rd-party apps that the sandbox depends on
    'django_extensions',
    'debug_toolbar',
]

# Add Oscar's custom auth backend so users can sign in using their email
# address.
AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = '/'
APPEND_SLASH = True

# ====================
# Messages contrib app
# ====================

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Woosh settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': location('whoosh_index'),
        'INCLUDE_SPELLING': True,
    },
}

# Here's a sample Haystack config for Solr 6.x (which is recommended)
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
#         'URL': 'http://127.0.0.1:8983/solr/sandbox',
#         'ADMIN_URL': 'http://127.0.0.1:8983/solr/admin/cores',
#         'INCLUDE_SPELLING': True,
#     }
# }

# =============
# Debug Toolbar
# =============

INTERNAL_IPS = ['127.0.0.1', '::1']

# ==============
# Oscar settings
# ==============

from oscar.defaults import *

# Meta
# ====

OSCAR_SHOP_TAGLINE = 'Sandbox'

OSCAR_RECENTLY_VIEWED_PRODUCTS = 20
OSCAR_ALLOW_ANON_CHECKOUT = True


# Order processing
# ================

# Sample order/line status settings. This is quite simplistic. It's like you'll
# want to override the set_status method on the order object to do more
# sophisticated things.
OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'

# This dict defines the new order statuses than an order can move to
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled',),
    'Being processed': ('Complete', 'Cancelled',),
    'Cancelled': (),
    'Complete': (),
}

# This dict defines the line statuses that will be set when an order's status
# is changed
OSCAR_ORDER_STATUS_CASCADE = {
    'Being processed': 'Being processed',
    'Cancelled': 'Cancelled',
    'Complete': 'Shipped',
}

# Sorl
# ====

THUMBNAIL_DEBUG = DEBUG
THUMBNAIL_KEY_PREFIX = 'oscar-sandbox'
THUMBNAIL_KVSTORE = env(
    'THUMBNAIL_KVSTORE',
    default='sorl.thumbnail.kvstores.cached_db_kvstore.KVStore')
THUMBNAIL_REDIS_URL = env('THUMBNAIL_REDIS_URL', default=None)

# easy-thumbnail. See https://github.com/SmileyChris/easy-thumbnails/issues/641#issuecomment-2291098096
THUMBNAIL_DEFAULT_STORAGE_ALIAS = "default"

# Django 1.6 has switched to JSON serializing for security reasons, but it does not
# serialize Models. We should resolve this by extending the
# django/core/serializers/json.Serializer to have the `dumps` function. Also
# in tests/config.py
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Security
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True


OSCAR_DASHBOARD_NAVIGATION = [
    {
        "label": _("Dashboard"),
        "icon": "fas fa-list",
        "url_name": "dashboard:index",
    },
    {
        "label": _("Catalogue"),
        "icon": "fas fa-sitemap",
        "children": [
            {
                "label": _("Products"),
                "url_name": "dashboard:catalogue-product-list",
            },
            {
                "label": _("Product Types"),
                "url_name": "dashboard:catalogue-class-list",
            },
            {
                "label": _("Categories"),
                "url_name": "dashboard:catalogue-category-list",
            },
            {
                "label": _("Ranges"),
                "url_name": "dashboard:range-list",
            },
            {
                "label": _("Low stock alerts"),
                "url_name": "dashboard:stock-alert-list",
            },
            {
                "label": _("Options"),
                "url_name": "dashboard:catalogue-option-list",
            },
            {
                "label": _("Attribute Option Groups"),
                "url_name": "dashboard:catalogue-attribute-option-group-list",
            },
        ],
    },
    {
        "label": _("Fulfilment"),
        "icon": "fas fa-shopping-cart",
        "children": [
            {
                "label": _("Orders"),
                "url_name": "dashboard:order-list",
            },
            {
                "label": _("Statistics"),
                "url_name": "dashboard:order-stats",
            },
            {
                "label": _("Partners"),
                "url_name": "dashboard:partner-list",
            },
            # The shipping method dashboard is disabled by default as it might
            # be confusing. Weight-based shipping methods aren't hooked into
            # the shipping repository by default (as it would make
            # customising the repository slightly more difficult).
            # {
            #     'label': _('Shipping charges'),
            #     'url_name': 'dashboard:shipping-method-list',
            # },
        ],
    },
    {
        "label": _("Customers"),
        "icon": "fas fa-users",
        "children": [
            {
                "label": _("Customers"),
                "url_name": "dashboard:users-index",
            },
            {
                "label": _("Stock alert requests"),
                "url_name": "dashboard:user-alert-list",
            },
        ],
    },
    {
        "label": _("Offers"),
        "icon": "fas fa-bullhorn",
        "children": [
            {
                "label": _("Offers"),
                "url_name": "dashboard:offer-list",
            },
            {
                'label': _('Promo offers'),
                'url_name': 'promo-dashboard:dashboard-promo-list',
                'access_fn': lambda user, url_name, url_args, url_kwargs: user.is_staff,
            },
            {
                "label": _("Vouchers"),
                "url_name": "dashboard:voucher-list",
            },
            {
                "label": _("Voucher Sets"),
                "url_name": "dashboard:voucher-set-list",
            },
        ],
    },
    {
        "label": _("Content"),
        "icon": "fas fa-folder",
        "children": [
            {
                "label": _("Pages"),
                "url_name": "dashboard:page-list",
            },
            {
                "label": _("Email templates"),
                "url_name": "dashboard:comms-list",
            },
            {
                "label": _("Reviews"),
                "url_name": "dashboard:reviews-list",
            },
        ],
    },
    {
        "label": _("Reports"),
        "icon": "fas fa-chart-bar",
        "url_name": "dashboard:reports-index",
    },
]
