import datetime

from django import forms
from django.conf import settings

from django_countries import Countries
from django_countries.fields import LazyTypedChoiceField
from django_countries.widgets import CountrySelectWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout


class OptionalCountries(Countries):
    first = ('--',)
    override = {'--': 'Decline to state'}


FOOD_LINK = '<a href="https://wiki.debconf.org/wiki/DebConf17/Catering" target="blank">More information</a>'
ACCOM_LINK = '<a href="https://wiki.debconf.org/wiki/DebConf17/Accomodation" target="blank">More information</a>'
BURSARIES_LINK = '<a href="https://debconf17.debconf.org/about/bursaries" target="blank">DebConf bursary instructions</a>'

# TODO: remove options for 2017-08-13 lunch and dinner
def meals(orga=False):
    day = datetime.date(2016, 7, 31)
    if orga:
        day = datetime.date(2016, 7, 28)
    while day <= datetime.date(2016, 8, 13):
        date = day.isoformat()
        yield 'breakfast_%s' % date, 'Breakfast %s' % date
        yield 'lunch_%s' % date, 'Lunch %s' % date
        yield 'dinner_%s' % date, 'Dinner %s' % date
        day += datetime.timedelta(days=1)

# TODO: fix the table
def nights(orga=False):
    day = datetime.date(2016, 7, 31)
    if orga:
        day = datetime.date(2016, 7, 28)
    while day <= datetime.date(2016, 8, 13):
        date = day.isoformat()
        yield 'night_%s' % date, 'Night %s' % date
        day += datetime.timedelta(days=1)


class RegistrationFormStep(forms.Form):
    def __init__(self, *args, wizard=None, **kwargs):
        super(RegistrationFormStep, self).__init__(*args, **kwargs)
        self.wizard = wizard
        self.helper = FormHelper()
        self.helper.form_tag = False


class RegistrationForm0(RegistrationFormStep):
    #
    # Contact informations
    #
    name = forms.CharField(
        label='My name is',
        help_text='This will appear on your name tag, and in public areas of '
                  'this site, e.g. if you submit a talk.',
    )
    # TODO: Consider storing the "wallet name" here, and having a separate
    # public name
    nametag_2 = forms.CharField(
        label='Nametag line 2',
        help_text="This could be your company, project, or anything you'd "
                  "like to say.",
        required=False,
    )
    nametag_3 = forms.CharField(
        label='Nametag line 3',
        help_text="This could be your nick, username, or something "
                  "suitably silly.",
        required=False,
    )
    email = forms.EmailField(
        label='My e-mail address is',
        help_text="This won't be listed publicly.",
    )
    phone = forms.CharField(
        label='My contact number',
        help_text="The full number, including international dialing codes, "
                  "please. This won't be listed publicly.",
        required=False,
    )
    # TODO: Find a way to make it easier to hint towards international numbers
    # e.g. drop-down list.
    emergency_contact = forms.CharField(
        label='My emergency contact',
        help_text='Please include the name, phone number, and language spoken '
                  '(if not English).',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    # Purposefully left unchecked by default to make this opt-in.
    announce_me = forms.BooleanField(
        label='Announce my arrival',
        help_text='If checked your name will be announced in the IRC channel when '
                  'you check in during conference',
        required=False,
    )


class RegistrationForm1(RegistrationFormStep):
    debcamp = forms.BooleanField(
        label='I plan to attend DebCamp (31 July to 4 August)',
        required=False,
    )
    open_day = forms.BooleanField(
        label='I plan to attend Open Day (5 August)',
        required=False,
    )
    debconf = forms.BooleanField(
        label='I plan to attend DebConf (6 August to 12 August)',
        initial=True,
        required=False,
    )
    fee = forms.ChoiceField(
        label='My registration fee',
        choices=(
            ('', 'Regular - Free'),
            ('pro', 'Professional - $200'),
            ('corp', 'Corporate - $500'),
        ),
        help_text='Prices in CAD. We encourage attendees to pay for their '
                  'attendance if they can afford to do so.',
        widget=forms.RadioSelect,
        initial='pro',
        required=False,
    )
    arrival = forms.DateTimeField(
        label='I arrive at the venue at',
        help_text="Please estimate, if you haven't booked tickets, yet, "
                  'and update it when you have final dates.',
        required=False,
    )
    departure = forms.DateTimeField(
        label='I depart from the venue at',
        required=False,
    )
    final_dates = forms.ChoiceField(
        label='My dates are',
        choices=(
            ('estimate', "Estimated, I haven't booked travel yet."),
            ('final', 'Final, I have booked my travel.'),
        ),
        initial='estimate',
        help_text="We'd like a rough indication of dates, even if you aren't "
                  'sure about the details yet. It helps us to plan.',
        required=False,
    )
    if settings.RECONFIRMATION:
        reconfirm = forms.BooleanField(
            label='I reconfirm my attendance',
            help_text="If you do not select this by July, we'll assume you "
                      "aren't coming",
            required=False,
        )

    def clean(self):
        cleaned_data = super(RegistrationForm1, self).clean()
        paid = bool(cleaned_data.get('fee'))

        if paid and not (cleaned_data.get('debcamp') or
                         cleaned_data.get('debian_day') or
                         cleaned_data.get('debconf')):
            self.add_error(
                'fee',
                "We can't collect a conference fee, if you aren't registering "
                "attendance at the conference")

        if cleaned_data.get('final_dates') == 'final':
            for field in ('arrival', 'departure'):
                if not cleaned_data.get(field):
                    self.add_error(
                        field, 'If your dates are final, pleas provide them')


class RegistrationForm2(RegistrationFormStep):
    #
    # Personnal information
    #
    t_shirt_cut = forms.ChoiceField(
        label='My T-shirt cut',
        choices=(
            ('n', "I don't want a t-shirt"),
            ('s', 'Straight cut'),
            ('w', "Women's fitted cut"),
        ),
        required=False,
    )
    t_shirt_size = forms.ChoiceField(
        label='My T-shirt size',
        choices=(
            ('n', ''),
            ('xs', 'Extra small'),
            ('s', 'Small'),
            ('m', 'Medium'),
            ('l', 'Large'),
            ('xl', 'Extra large'),
            ('2xl', '2X Large'),
            ('3xl', '3X Large'),
            ('4xl', '4X Large'),
            ('5xl', '5X Large'),
        ),
        required=False,
    )
    gender = forms.ChoiceField(
        label='My gender',
        choices=(
            ('', 'Decline to state'),
            ('m', 'Male'),
            ('f', 'Female'),
            ('o', 'Other'),
        ),
        help_text='For diversity statistics',
        required=False,
    )
    country = LazyTypedChoiceField(
        label='Country I call home',
        help_text='For diversity statistics',
        choices=OptionalCountries(),
        required=False,
        widget=CountrySelectWidget(),
    )
    languages = forms.CharField(
        label='Languages I speak',
        help_text='We will list these on your nametag',
        initial='en',
        required=False,
    )

#    def __init__(self, *args, **kwargs):
#        super(RegistrationForm2, self).__init__(*args, **kwargs)
#        self.helper.layout = Layout(
#            Field('t_shirt_cut'),
#            Fieldset(
#                '',
#                't_shirt_size',
#                css_id='tshirt-details',
#                # We do the collapsing in JS, so we can be sure that it'll
#                # expand, when necessary
#                css_class='collapse in',
#            ),
#            Field('gender'),
#            Field('country'),
#            Field('languages'),
#        )
#
#
#           TODO: add cleaned form


class RegistrationForm3(RegistrationFormStep):
    #
    # Bursaries
    #
    bursary = forms.BooleanField(
        label='I want to apply for a bursary',
        required=False,
    )

    bursary_type = forms.ChoiceField(
        label='What type of bursary do you need?',
        choices=(
            ('f', 'Food and accommodation only'),
            ('t', 'Food, accommodation *and travel*'),
        ),
        required=False,
    )

    bursary_reason = forms.CharField(
        label='Details of my bursary request',
        help_text='This is where you explain your needs, and involvement in '
                  'Debian, that justify a bursary. See the ' + BURSARIES_LINK,
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
    )
    bursary_need = forms.ChoiceField(
        label='My level of need',
        choices=(
            ('', 'N/A (not requesting a bursary)'),
            ('unable', 'Without this funding I will be absolutely '
                       'unable to attend'),
            ('sacrifice', 'Without the requested funding I will have to '
                          'make financial sacrifices, to attend'),
            ('inconvenient', 'Without the requested funding attending will '
                             'be inconvenient for me'),
            ('non-financial', 'I am not applying based on financial need'),
        ),
        required=False,
    )

    travel_bursary = forms.IntegerField(
        label='My travel expense claim',
        help_text='Estimated amount required. ' + BURSARIES_LINK,
        min_value=0,
        max_value=10000,
        required=False,
    )
    travel_bursary_from = forms.CharField(
        label='I\'m traveling from',
        help_text='Knowing where you travel from helps us estimate your travel '
                  'needs',
        widget=forms.Textarea(attrs={'rows': 1}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm3, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('bursary'),
            Fieldset(
                '',
                'bursary_type',
                'bursary_reason',
                'bursary_need',
                'travel_bursary',
                'travel_bursary_from',
                css_id='bursary-details',
                # We do the collapsing in JS, so we can be sure that it'll
                # expand, when necessary
                css_class='collapse in',
            )
        )

    def clean(self):
        cleaned_data = super(RegistrationForm3, self).clean()

        if cleaned_data.get('travel_bursary') == 0:
            cleaned_data['travel_bursary'] = None

        if not cleaned_data.get('bursary'):
            for field in ('bursary_reason', 'travel_bursary', 'bursary_need'):
                if cleaned_data.get(field):
                    self.add_error(
                        field,
                        'You have not applied for a bursary')
        else:
            if not cleaned_data.get('bursary_reason'):
                self.add_error(
                    'bursary_reason',
                    'A bursary has been requested, '
                    'please explain why it is needed')
            if not cleaned_data.get('bursary_need'):
                self.add_error(
                    'bursary_need',
                    'A bursary has been requested, '
                    'please explain the level of need')


class RegistrationForm4(RegistrationFormStep):
    #
    # Accommodation & Food
    #

    buy_food = forms.BooleanField(
        label='I want to buy meal tickets for onsite catering',
        required=False,
    )

    food_selection = forms.MultipleChoiceField(
        label='I want to eat catered food for these meals:',
        choices=meals(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='If you don\'t have a food bursaries, meal prices are: '
                  'Breakfast X CAD$, Lunch Y CAD$, Dinner Z CAD$',
    )

    diet = forms.ChoiceField(
        label='My diet',
        choices=(
            ('', 'I will be happy to eat whatever is provided'),
            ('vegetarian', "I am lacto-ovo vegetarian, don't provide "
                           "meat/fish for me"),
            ('vegan', "I am strict vegatarian (vegan), don't provide any "
                      "animal products for me"),
            ('other', 'Other, described below'),
        ),
        required=False,
    )
    venue_accom = forms.ChoiceField(
        label='I want to stay on premise',
        choices=(
            ('no', 'No, I will find accommodation by myself'),
            ('yes', 'Yes, I want to stay at the venue in classroom dorms'
                    '(30 CAD$/night)'),
        ),
        required=False,
    )

    night_selection = forms.MultipleChoiceField(
        label='I want to stay in classroom dorms these nights:',
        choices=nights(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    alt_accom = forms.BooleanField(
        label='I would like to request alternative accomodation',
        required=False,
    )
    alt_accom_choice = forms.ChoiceField(
        label='Select the accommodation you prefer during DebConf',
        choices=(
            ('rvc', 'McGill residences accommodation'
                    '(30min by public transit)'),
            ('hotel','Hotel Universel (reserved for families and people with',
                     'disabilities only'),
        ),
    )

    special_needs = forms.CharField(
        label='My special needs',
        help_text='Wheelchair access, food allergies, other diets, etc.',
        required=False,
    )

    family_usernames = forms.CharField(
        label='Usernames of my family members, '
              'who have registered separately',
        help_text="One per line. This isn't validated",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def clean(self):
        cleaned_data = super(RegistrationForm4, self).clean()

        if (cleaned_data.get('diet') == 'other' and
                not cleaned_data.get('special_needs')):
            self.add_error('special_needs', 'Required when diet is "other"')


class RegistrationForm5(RegistrationFormStep):
    #
    # Billing information
    #
    billing_address = forms.CharField(
        label='My billing address',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    notes = forms.CharField(
        label='Notes for the registration team',
        help_text='Anything else you need to describe. '
                  'The registration team will see this. '
                  'The bursaries team will not.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def clean(self):
        cleaned_data = super(RegistrationForm5, self).clean()
        step1_cleaned = self.wizard.get_cleaned_data_for_step(1) or {}
        paid = bool(step1_cleaned.get('fee'))

        if paid and not cleaned_data.get('billing_address'):
            self.add_error('billing_address',
                           'Paid attendees need to provide a billing address')
