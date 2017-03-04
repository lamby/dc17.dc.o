import datetime

from django import forms
from django.conf import settings

from django_countries import Countries
from django_countries.fields import LazyTypedChoiceField
from django_countries.widgets import CountrySelectWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout


FOOD_LINK = (
    '<a href="https://wiki.debconf.org/wiki/DebConf17/Catering" '
    'target="blank">More information</a>')
ACCOM_LINK = (
    '<a href="https://wiki.debconf.org/wiki/DebConf17/Accomodation" '
    'target="blank">More information</a>')
BURSARIES_LINK = (
    '<a href="https://debconf17.debconf.org/about/bursaries" target="blank">'
    'DebConf bursary instructions</a>')


class OptionalCountries(Countries):
    first = ('__',)
    override = {'__': 'Decline to state'}


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


class ContactInformationForm(RegistrationFormStep):
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
        help_text='If checked your name will be announced in the IRC channel '
                  'when you check in during conference',
        required=False,
    )


class ConferenceRegistrationForm(RegistrationFormStep):
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
            ('pro', 'Professional - 200 CAD$'),
            ('corp', 'Corporate - 500 CAD$'),
        ),
        help_text='We encourage attendees to pay for their attendance if they '
                  'can afford to do so.',
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
        cleaned_data = super(ConferenceRegistrationForm, self).clean()
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


class PersonalInformationForm(RegistrationFormStep):
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
            ('', 'N/A'),
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
        label='The country I call home',
        help_text='For diversity statistics',
        choices=OptionalCountries(),
        required=False,
        widget=CountrySelectWidget(),
    )
    languages = forms.CharField(
        label='The languages I speak',
        help_text='We will list these on your nametag',
        initial='en',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(PersonalInformationForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('t_shirt_cut'),
            Fieldset(
                '',
                't_shirt_size',
                css_id='tshirt-details',
                # We do the collapsing in JS, so we can be sure that it'll
                # expand, when necessary
                css_class='collapse in',
            ),
            Field('gender'),
            Field('country'),
            Field('languages'),
        )


#           TODO: add cleaned form


class BursaryForm(RegistrationFormStep):
    bursary = forms.ChoiceField(
        label='I want to apply for a bursary',
        choices=(
            ('', "No, I'm not requesting a bursary"),
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
    travel_from = forms.CharField(
        label="I'm traveling from",
        help_text='Knowing where you need to travel from helps us evaluate '
                  'the amount you are claiming.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(BursaryForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('bursary'),
            Fieldset(
                '',
                'bursary_reason',
                'bursary_need',
                css_id='bursary-details',
                # We do the collapsing in JS, so we can be sure that it'll
                # expand, when necessary
                css_class='collapse in',
            ),
            Fieldset(
                '',
                'travel_bursary',
                'travel_from',
                css_id='travel-details',
                # We do the collapsing in JS, so we can be sure that it'll
                # expand, when necessary
                css_class='collapse in',
            )
        )

    def clean(self):
        cleaned_data = super(BursaryForm, self).clean()

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


class FoodForm(RegistrationFormStep):
    food_selection = forms.MultipleChoiceField(
        label='I want to eat catered food for these meals:',
        choices=meals(),
        widget=forms.CheckboxSelectMultiple,
        help_text="If you don't have a food bursary, meal prices are: "
                  "Breakfast 3 CAD$, Lunch 7.50 CAD$, Dinner 7.50 CAD$",
        required=False,
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
    special_diet = forms.CharField(
        label='Details of my special dietary needs',
        required=False,
    )

    def clean(self):
        cleaned_data = super(FoodForm, self).clean()

        if (cleaned_data.get('diet') == 'other' and
                not cleaned_data.get('special_diet')):
            self.add_error('special_diet', 'Required when diet is "other"')


class AccommForm(RegistrationFormStep):
    venue_accom = forms.ChoiceField(
        label='Do you need accommodation?',
        choices=(
            ('no', 'No, I will find my own accommodation'),
            ('yes', 'Yes, I need accommodation'),
        ),
    )
    night_selection = forms.MultipleChoiceField(
        label="I'm requesting accommodation for these nights:",
        choices=nights(),
        widget=forms.CheckboxSelectMultiple,
        help_text='By defautl, the accommodation provided is in shared '
                  'classroom dorms on premises. The cost is 30 CAD$/night for '
                  ' self-paying attendees',
        required=False,
    )
    alt_accom = forms.BooleanField(
        label='I would like to request alternative accommodation',
        required=False,
    )
    alt_accom_choice = forms.ChoiceField(
        label='Select the accommodation you prefer during DebConf',
        choices=(
            ('rvc', 'McGill residences accommodation '
                    '(30min by public transit)'),
            ('hotel', 'Hotel Universel (reserved for families and people with '
                      'disabilities only'),
        ),
        required=False,
    )
    childcare = forms.ChoiceField(
        label='Do you need childcare?',
        choices=(
            ('no', 'No, I do not need childcare'),
            ('yes', 'Yes, I would like childcare for my kid(s)'),
        ),
    )
    childcare_needs = forms.CharField(
        label='Please specify what type of childcare services you need',
        help_text='How many hours a day? All the conference or only part of '
                  'it? etc.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    childcare_details = forms.CharField(
        label='Please specify all important informations about you kid(s)',
        help_text='Number, age, language spoken, special needs, etc.',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
    )
    special_needs = forms.CharField(
        label='My special needs',
        help_text='Wheelchair access or other any other needs we should be '
                  'aware of',
        required=False,
    )
    family_usernames = forms.CharField(
        label='Usernames of my family members, '
              'who have registered separately',
        help_text="One per line. This isn't validated",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(AccommForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('venue_accom'),
            Fieldset(
                '',
                'night_selection',
                'alt_accom',
                css_id='night-details',
                # We do the collapsing in JS, so we can be sure that it'll
                # expand, when necessary
                css_class='collapse in',
            ),
            Fieldset(
                '',
                'alt_accom_choice',
                css_id='accom-details',
                # We do the collapsing in JS, so we can be sure that it'll
                # expand, when necessary
                css_class='collapse in',
            ),
            Field('childcare'),
            Fieldset(
                '',
                'childcare_needs',
                'childcare_details',
                css_id='childcare-details',
                # We do the collapsing in JS, so we can be sure that it'll
                # expand, when necessary
                css_class='collapse in',
            ),
            Field('special_needs'),
            Field('family_usernames'),
        )


#           TODO: add cleaned form


class BillingForm(RegistrationFormStep):
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
        cleaned_data = super(BillingForm, self).clean()
        step1_cleaned = self.wizard.get_cleaned_data_for_step(1) or {}
        paid = bool(step1_cleaned.get('fee'))

        if paid and not cleaned_data.get('billing_address'):
            self.add_error('billing_address',
                           'Paid attendees need to provide a billing address')


REGISTRATION_FORMS = [
    ContactInformationForm,
    ConferenceRegistrationForm,
    PersonalInformationForm,
    BursaryForm,
    FoodForm,
    AccommForm,
    BillingForm,
]
