# -*- encoding: utf-8 -*-
from pathlib import Path

from django.core.urlresolvers import reverse_lazy

from wafer.settings import *

TIME_ZONE = 'America/Montreal'

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
                'menu': 'visiting_montreal',
                'label': 'Visiting Montreal',
                'url': reverse_lazy(
                    'wafer_page', args=('about/visiting-montreal',))
            },
        ],
    },
    {
        'menu': 'sponsors_index',
        'label': 'Sponsors',
        'items': [
            {
                'menu': 'sponsors',
                'label': 'Our Sponsors',
                'url': reverse_lazy('wafer_sponsors')
            },
            {
                'menu': 'become_sponsor',
                'label': 'Become a Sponsor',
                'url': reverse_lazy('wafer_page', args=('sponsors/become-a-sponsor',))
            }
        ],
    },
    {
        'menu': 'schedule_index',
        'label': 'Schedule',
        'items': [
            {
                'menu': 'important-dates',
                'label': 'Important Dates',
                'url': reverse_lazy('wafer_page', args=('schedule/important-dates',))
            },
            {
                'menu': 'confirmed_talks',
                'label': 'Confirmed Talks',
                'url': reverse_lazy('wafer_users_talks')
            },
            {
                'menu': 'debian-day',
                'label': 'Debian Day',
                'url': reverse_lazy('wafer_page', args=('schedule/debian-day',))
            },

        ]
    }
)

ROOT_URLCONF = 'urls'

CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG

MARKITUP_FILTER = ('markdown.markdown', {
    'extensions': [
        'markdown.extensions.smarty',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'dc17.markdown',
    ],
    'output_format': 'html5',
    'safe_mode': False,
})
MARKITUP_SET = 'markitup/sets/markdown/'

DEFAULT_FROM_EMAIL = 'registration@debconf.org'

WAFER_REGISTRATION_MODE = 'form'
#WAFER_REGISTRATION_FORM = 'dc16.registration.RegistrationForm'

#WAFER_TALK_FORM = 'dc16.talks.TalkForm'

WAFER_PUBLIC_ATTENDEE_LIST = False

PAGE_DIR = '%s/' % (root / 'pages')
NEWS_DIR = '%s/' % (root / 'news' / 'stories')
SPONSORS_DIR = '%s/' % (root / 'sponsors')
