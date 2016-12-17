# -*- encoding: utf-8 -*-
from pathlib import Path

from django.core.urlresolvers import reverse_lazy

from wafer.settings import *

TIME_ZONE = 'America/Montreal'

WAFER_TALKS_OPEN = False
WAFER_REGISTRATION_OPEN = False

try:
    from localsettings import *
except ImportError:
    pass

root = Path(__file__).parent

INSTALLED_APPS = (
    'dc17',
    'news',
#    'volunteers'
) + INSTALLED_APPS

STATIC_ROOT = str(root / 'localstatic/')

STATICFILES_DIRS = (
    str(root / 'static'),
)

STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.ManifestStaticFilesStorage')

TEMPLATES[0]['DIRS'] = TEMPLATES[0]['DIRS'] + (
    str(root / 'templates'),
)


# Menu system 101:
# Anything in the database with "Appear on menu" set will be appended to the
# end of the menu we define here. So, to control the ordering of items, set
# them here
WAFER_MENUS += (
    {
        'menu': 'about',
        'label': 'About',
        'items': [
            {
                'menu': 'debconf',
                'label': 'About DebConf',
                'url': reverse_lazy('wafer_page', args=('about/debconf',))
            },
            {
                'menu': 'debian',
                'label': 'About Debian',
                'url': reverse_lazy('wafer_page', args=('about/debian',))
            },
            {
                'menu': 'dates',
                'label': 'Dates',
                'url': reverse_lazy('wafer_page', args=('about/dates',))
            },
            {
                'menu': 'registration_information',
                'label': 'Registration Information',
                'url': reverse_lazy('wafer_page', args=('about/registration',))
            },
            {
                'menu': 'bursaries',
                'label': 'Bursaries',
                'url': reverse_lazy('wafer_page', args=('about/bursaries',))
            },
            {
                'menu': 'visiting_canada',
                'label': 'Visiting Canada',
                'url': reverse_lazy(
                    'wafer_page', args=('about/visiting-canada',))
            },
        ],
    },
    {
        'menu': 'sponsors',
        'label': 'Sponsors',
        'url': reverse_lazy('wafer_sponsors')
    },
    {
        'menu': 'schedule_index',
        'label': 'Schedule',
        'items': [
            {
                'menu': 'schedule',
                'label': 'Schedule',
                'url': reverse_lazy('wafer_full_schedule')
            },
            {
                'menu': 'talks',
                'label': 'Talks',
                'url': reverse_lazy('wafer_users_talks')
            },
            {
                'menu': 'mobile_friendly_schedule',
                'label': 'Mobile-friendly Schedule',
                'url': reverse_lazy(
                    'wafer_page',
                    args=('mobile-friendly-schedule',))
            },
            {
                'menu': 'open-weekend',
                'label': 'Open Weekend',
                'url': reverse_lazy('wafer_page', args=('open-weekend',))
            },
            {
                'menu': 'debcamp-sprints',
                'label': 'DebCamp Sprints',
                'url': reverse_lazy('wafer_page', args=('debcamp-sprints',))
            }
        ]
    }
)

ROOT_URLCONF = 'urls'

CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG

MARKITUP_FILTER = ('markdown.markdown', {
    'safe_mode': False,
    'extensions': [
        'markdown.extensions.tables',
    ],
})
MARKITUP_SET = 'markitup/sets/markdown/'

DEFAULT_FROM_EMAIL = 'registration@debconf.org'

WAFER_REGISTRATION_MODE = 'form'
#WAFER_REGISTRATION_FORM = 'dc16.registration.RegistrationForm'

#WAFER_TALK_FORM = 'dc16.talks.TalkForm'

WAFER_PUBLIC_ATTENDEE_LIST = False

PAGE_DIR = '%s/' % (root / 'pages')
NEWS_DIR = '%s/' % (root / 'news' / 'stories')
