import datetime
import re

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django_countries import Countries
from django_countries.fields import LazyTypedChoiceField
from django_countries.widgets import CountrySelectWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, HTML

from dc17.dates import meal_choices, night_choices
from dc17.models import Accomm, AccommNight, Bursary, Food, Meal


FOOD_LINK = (
    '<a href="https://wiki.debconf.org/wiki/DebConf17/Catering" '
    'target="blank">More information</a>')
ACCOM_LINK = (
    '<a href="https://wiki.debconf.org/wiki/DebConf17/Accomodation" '
    'target="blank">More information</a>')
BURSARIES_LINK = (
    '<a href="/about/bursaries/" target="blank">DebConf bursary instructions.'
    '</a>')
TSHIRT_CHART_LINK = (
    '<a href="https://wiki.debconf.org/wiki/DebConf17/TshirtSizes" '
    'target="blank">t-shirt sizes chart</a>')
PREAMBLE = (
    '<p>Thank you for your interest in attending DebConf17!</p>'
    '<p>Please read the following instructions carefully:</p>'
    '<ol>'
    '<noscript>'
    "<li>This registration form uses JavaScript. Without it, you'll have to "
    "navigate the validation dragons without any help. And you won't be able "
    "to make payments through Stripe.</li>"
    '</noscript>'
    '<li>Nothing will be saved until the last page of the form, so be sure to '
    'work all the way through it.</li>'
    '<li>All registration, accommodation and catering fees must be paid '
    'either trough the Stripe platform or in person at the front desk upon '
    'arrival.</li>'
    '<li>Please keep your registration information up to date. You can make '
    'changes at any time through this form.</li>'
    '<li>Registrations will need to be confirmed before July 1st. '
    'We cannot guarantee availability of accommodation, catering or swag for '
    'unconfirmed registrations.</li>'
    '<li>Badges will be available for pick-up at the front desk.</li>'
    '<li>The deadline to apply for a bursary is May 10th. After this date, '
    "new bursary applications won't be considered.</li>"
    '</ol>'
)

PLAN_DEBCAMP_LABEL = 'I plan to attend DebCamp (31 July to 4 August)'
PLAN_OPENDAY_LABEL = 'I plan to attend Open Day (5 August)'
PLAN_DEBCONF_LABEL = 'I plan to attend DebConf (6 August to 12 August)'

FEES_LABELS = {
    'regular': 'Regular - Free',
    'pro': 'Professional - 200 CAD',
    'corp': 'Corporate - 500 CAD',
}

FINAL_DATES_ESTIMATE_LABEL = "Estimated, I haven't booked travel yet."
FINAL_DATES_FINAL_LABEL = 'Final, I have booked my travel.'

NO_T_SHIRT_LABEL = "I don't want a t-shirt"
STRAIGHT_CUT_LABEL = 'Straight cut'
WOMENS_FITTED_CUT_LABEL = "Women's fitted cut"

T_SHIRT_SIZES = {
    'xs': 'Extra Small',
    's': 'Small',
    'm': 'Medium',
    'l': 'Large',
    'xl': 'Extra Large',
    '2xl': '2X Large',
    '3xl': '3X Large',
    '4xl': '4X Large',
    '5xl': '5X Large',
}

FOOD_ACCOMM_BURSARY_LABEL = 'Food and accommodation only'
TRAVEL_FOOD_ACCOMM_BURSARY_LABEL = 'Travel, food and accommodation'

BURSARY_NEED_LABELS = {
    'unable': 'Without this funding, I will be absolutely '
              'unable to attend',
    'sacrifice': 'Without the requested funding, I will have to '
                 'make financial sacrifices to attend',
    'inconvenient': 'Without the requested funding, attending will '
                    'be inconvenient for me',
    'non-financial': 'I am not applying based on financial need',
}

ACCOMM_CHOICE_LABELS = {
    'rvc_single': 'Single room at McGill residences accommodation '
                  '(30min by public transit)',
    'rvc_double': 'Double room at McGill residences accommodation '
                  '- for couples only - (30min by public transit)',
    'hotel': 'Hotel Universel (reserved for families and people with '
             'disabilities only',
}

DIET_LABELS = {
    '': 'I will be happy to eat whatever is provided',
    'vegetarian': "I am lacto-ovo vegetarian, don't provide "
                  "meat/fish for me",
    'vegan': "I am strict vegetarian (vegan), don't provide any "
             "animal products for me",
    'other': 'Other, described below',
}


def parse_date(date):
    return datetime.date(*(int(part) for part in date.split('-')))


class OptionalCountries(Countries):
    first = ('__',)
    override = {'__': 'Decline to state'}


class RegistrationFormStep(forms.Form):
    attendee_fields = ()

    def __init__(self, *args, wizard=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.wizard = wizard
        self.helper = FormHelper()
        self.helper.form_tag = False

    @classmethod
    def get_initial(cls, user):
        return cls.get_initial_attendee_data(user)

    @classmethod
    def get_initial_attendee_data(cls, user):
        # Hack to allow overriding get_initial while still being a classmethod
        try:
            return {field: getattr(user.attendee, field)
                    for field in cls.attendee_fields}
        except ObjectDoesNotExist:
            return {}

    def get_attendee_data(self):
        return {field: self.cleaned_data[field]
                for field in self.attendee_fields}

    def save(self, user, attendee):
        pass

    def get_cleaned_data_for_form(self, form):
        for step, found_form in self.wizard.form_list.items():
            if form == found_form:
                return self.wizard.get_cleaned_data_for_step(step)
        return {}


class PreambleForm(RegistrationFormStep):
    title = 'Preamble'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            HTML(PREAMBLE),
        )


class ContactInformationForm(RegistrationFormStep):
    title = 'Contact Information'

    name = forms.CharField(
        label='My name is',
        help_text='This will appear on your name tag, and in public areas of '
                  'this site, e.g. if you submit a talk.',
        max_length=50,
    )
    # TODO: Consider storing the "wallet name" here, and having a separate
    # public name
    nametag_2 = forms.CharField(
        label='Nametag line 2',
        help_text="This could be your company, project, preferred pronoun or "
                  "anything you'd like to say.",
        max_length=50,
        required=False,
    )
    nametag_3 = forms.CharField(
        label='Nametag line 3',
        help_text="This could be your nick, username, or something "
                  "suitably silly.",
        max_length=50,
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
        max_length=16,
        required=False,
    )
    emergency_contact = forms.CharField(
        label='My emergency contact',
        help_text='Please include the name, full international phone number, '
                  'and language spoken (if not English).',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    # Purposefully left unchecked by default to make this opt-in.
    announce_me = forms.BooleanField(
        label='Announce my arrival',
        help_text='If checked, your name will be announced in the IRC channel '
                  'when you check in to the conference.',
        required=False,
    )
    register_announce = forms.BooleanField(
        label="Subscribe me to the DebConf-announce mailing list",
        help_text='This low-volume mailing list is the primary way for us to '
                  'reach attendees about important conference news and '
                  'information.',
        required=False,
        initial=True,
    )
    register_discuss = forms.BooleanField(
        label='Subscribe me to the DebConf-discuss mailing list',
        help_text='This mailing list is used by attendees and interested '
                  'people for general discussions about the conference.',
        required=False,
    )

    attendee_fields = (
        'nametag_2',
        'nametag_3',
        'emergency_contact',
        'announce_me',
        'register_announce',
        'register_discuss',
    )

    @classmethod
    def get_initial(cls, user):
        initial = {
            'name': user.get_full_name(),
            'nametag_3': user.username,
            'email': user.email,
            'phone': user.userprofile.contact_number,
        }
        initial.update(cls.get_initial_attendee_data(user))
        return initial

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+', phone):
            raise forms.ValidationError(
                "If provide a phone number, please make sure it's in "
                "international dialing format. e.g. +1 234 567 8999")
        return phone

    def clean_emergency_contact(self):
        emergency_contact = self.cleaned_data.get('emergency_contact')
        if emergency_contact:
            m = re.search(r'(?<![0-9+ ]) *\(?\d{2,4}[).-]? ?\d{2,4}',
                          emergency_contact)
            if m:
                raise forms.ValidationError(
                    "If you include a phone number, please make sure it's in "
                    "intarnational dialing format. e.g. +1 234 5678")
        return emergency_contact

    def save(self, user, attendee):
        data = self.cleaned_data
        if user.get_full_name() != self.cleaned_data['name']:
            user.first_name, user.last_name = data['name'].split(None, 1)
        user.email = data['email']
        user.save()
        user.userprofile.contact_number = data['phone']
        user.userprofile.save()


class ConferenceRegistrationForm(RegistrationFormStep):
    title = 'Conference Registration'

    coc_ack = forms.BooleanField(
        label='I have read and promise to abide by the '
              '<a href="http://debconf.org/codeofconduct.shtml" '
              'target="_blank">'
              'DebConf Code of Conduct</a>',
        required=True,
    )
    debcamp = forms.BooleanField(
        label=PLAN_DEBCAMP_LABEL,
        required=False,
    )
    open_day = forms.BooleanField(
        label=PLAN_OPENDAY_LABEL,
        required=False,
    )
    debconf = forms.BooleanField(
        label=PLAN_DEBCONF_LABEL,
        initial=True,
        required=False,
    )
    fee = forms.ChoiceField(
        label='My registration fee',
        choices=(
            ('', FEES_LABELS['regular']),
            ('pro', FEES_LABELS['pro']),
            ('corp', FEES_LABELS['corp']),
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
    final_dates = forms.BooleanField(
        label='My dates are',
        widget=forms.Select(choices=(
                (False, FINAL_DATES_ESTIMATE_LABEL),
                (True, FINAL_DATES_FINAL_LABEL),
        )),
        initial=False,
        help_text="We'd like a rough indication of dates, even if you aren't "
                  'sure about the details yet. It helps us to plan.',
        required=False,
    )
    reconfirm = forms.BooleanField(
        label='I reconfirm my attendance',
        help_text="If you do not select this by July, we'll assume you "
                  "aren't coming.",
        required=False,
    )

    attendee_fields = (
        'debcamp',
        'open_day',
        'debconf',
        'fee',
        'arrival',
        'departure',
        'final_dates',
        'reconfirm',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'coc_ack',
            'debcamp',
            'open_day',
            'debconf',
            'fee',
            Field('arrival', id='arrival'),
            Field('departure', id='departure'),
            'final_dates',
        )
        if settings.RECONFIRMATION:
            self.helper.layout.append('reconfirm')

    @classmethod
    def get_initial(cls, user):
        initial = cls.get_initial_attendee_data(user)
        try:
            user.attendee
            initial['coc_ack'] = True
        except ObjectDoesNotExist:
            pass
        return initial

    def clean(self):
        cleaned_data = super().clean()

        if not (cleaned_data.get('debcamp') or
                cleaned_data.get('open_day') or
                cleaned_data.get('debconf')):
            for field in ('debcamp', 'open_day', 'debconf'):
                # TODO: Add link to unregister
                self.add_error(
                    field,
                    'You need to register for at least one section of the '
                    'conference.')

        if cleaned_data.get('final_dates'):
            for field in ('arrival', 'departure'):
                if not cleaned_data.get(field):
                    self.add_error(
                        field, 'If your dates are final, pleas provide them')

        else:
            if cleaned_data.get('reconfirm'):
                self.add_error(
                    'final_dates', 'Dates need to be final, to reconfirm')


class PersonalInformationForm(RegistrationFormStep):
    title = 'Personal Information'

    t_shirt_cut = forms.ChoiceField(
        label='My t-shirt cut',
        choices=(
            ('', NO_T_SHIRT_LABEL),
            ('s', STRAIGHT_CUT_LABEL),
            ('w', WOMENS_FITTED_CUT_LABEL),
        ),
        required=False,
    )
    t_shirt_size = forms.ChoiceField(
        label='My t-shirt size',
        choices=(
            ('', 'N/A'),
            ('xs', T_SHIRT_SIZES['xs']),
            ('s', T_SHIRT_SIZES['s']),
            ('m', T_SHIRT_SIZES['m']),
            ('l', T_SHIRT_SIZES['l']),
            ('xl', T_SHIRT_SIZES['xl']),
            ('2xl', T_SHIRT_SIZES['2xl']),
            ('3xl', T_SHIRT_SIZES['3xl']),
            ('4xl', T_SHIRT_SIZES['4xl']),
            ('5xl', T_SHIRT_SIZES['5xl']),
        ),
        help_text='Refer to the ' + TSHIRT_CHART_LINK + '.',
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
        help_text='For diversity statistics.',
        required=False,
    )
    country = LazyTypedChoiceField(
        label='The country I call home',
        help_text='For diversity statistics.',
        choices=OptionalCountries(),
        required=False,
        widget=CountrySelectWidget(),
    )
    languages = forms.CharField(
        label='The languages I speak',
        help_text='We will list these on your nametag.',
        initial='en',
        max_length=50,
        required=False,
    )

    attendee_fields = (
        't_shirt_cut',
        't_shirt_size',
        'gender',
        'country',
        'languages',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                'T-shirt',
                Field('t_shirt_cut', id='tshirt-cut'),
                Field('t_shirt_size', id='tshirt-size'),
            ),
            Field('gender'),
            Field('country'),
            Field('languages'),
        )

    def clean_t_shirt_size(self):
        if not self.cleaned_data.get('t_shirt_cut'):
            return ''
        return self.cleaned_data.get('t_shirt_size')

    def clean(self):
        cleaned_data = super().clean()
        t_shirt_cut = cleaned_data.get('t_shirt_cut')
        t_shirt_size = cleaned_data.get('t_shirt_size')
        if t_shirt_cut and not t_shirt_size:
            self.add_error('t_shirt_size', "Select a size, please")


class BursaryForm(RegistrationFormStep):
    title = 'Bursary'

    request = forms.ChoiceField(
        label='I want to apply for a bursary',
        choices=(
            ('', "No, I'm not requesting a bursary"),
            ('food+accomm', FOOD_ACCOMM_BURSARY_LABEL),
            ('travel+food+accomm', TRAVEL_FOOD_ACCOMM_BURSARY_LABEL),
        ),
        required=False,
    )
    reason_contribution = forms.CharField(
        label='My contributions to Debian',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        help_text='To help us evaluate your eligibility for a Debian bursary.',
    )
    reason_plans = forms.CharField(
        label='My plans for DebCamp or DebConf',
        help_text='To help us evaluate your eligibility for a Debian bursary.',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
    )
    reason_diversity = forms.CharField(
        label='My eligibility for a diversity bursary',
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Diversity bursary applications only. Please consult the '
                  '<a href="/about/bursaries/#diversity-bursaries" '
                  'target="blank">diversity bursary instructions</a>.',
        required=False,
    )
    need = forms.ChoiceField(
        label='My level of need',
        choices=(
            ('', 'N/A (not requesting a bursary)'),
            ('unable', BURSARY_NEED_LABELS['unable']),
            ('sacrifice', BURSARY_NEED_LABELS['sacrifice']),
            ('inconvenient', BURSARY_NEED_LABELS['inconvenient']),
            ('non-financial', BURSARY_NEED_LABELS['non-financial']),
        ),
        required=False,
    )
    travel_bursary = forms.IntegerField(
        label='My travel expense claim (in USD)',
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
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('request', id='bursary-request'),
            Fieldset(
                'Bursary Details',
                HTML('<p>This is where you explain your needs, and '
                     'involvement in Debian, that justify a bursary. See the '
                     + BURSARIES_LINK + '.</p>'),
                'reason_contribution',
                'reason_plans',
                'reason_diversity',
                'need',
                css_id='bursary-details',
            ),
            Fieldset(
                'Travel Bursary Details',
                'travel_bursary',
                'travel_from',
                css_id='travel-details',
            )
        )

    @classmethod
    def get_initial(cls, user):
        try:
            bursary = user.bursary
        except ObjectDoesNotExist:
            return {}
        return {field: getattr(bursary, field) for field in (
            'request',
            'reason_contribution',
            'reason_plans',
            'reason_diversity',
            'need',
            'travel_bursary',
            'travel_from',
        )}

    def clean_travel_bursary(self):
        travel_bursary = self.cleaned_data.get('travel_bursary')
        if travel_bursary == 0:
            return None
        return travel_bursary

    def clean(self):
        cleaned_data = super().clean()

        request = cleaned_data.get('request')
        if not request:
            cleaned_data['request'] = None
            return cleaned_data

        if not cleaned_data.get('reason_plans'):
            self.add_error(
                'reason_plans',
                'Please share your plans for the conference, when appyling '
                'for a bursary.')

        if (not cleaned_data.get('reason_contribution')
                and not cleaned_data.get('reason_diversity')):
            for field in ('reason_contribution', 'reason_diversity'):
                self.add_error(
                    field,
                    'Please describe your contributions and/or the diversity '
                    'of your background, when applying for a bursary.')

        if not cleaned_data.get('need'):
            self.add_error(
                'need',
                'Please share your level of need, when appyling for a bursary.'
            )

        if 'travel' in request:
            for field in ('travel_bursary', 'travel_from'):
                if not cleaned_data.get(field):
                    self.add_error(
                        field,
                        'Please share your travel details, when appyling for '
                        'a travel bursary.'
                    )

    def save(self, user, attendee):
        data = self.cleaned_data
        bursary_data = {field: data[field] for field in (
            'request',
            'reason_contribution',
            'reason_plans',
            'reason_diversity',
            'need',
            'travel_bursary',
            'travel_from',
        )}

        if data['request']:
            Bursary.objects.update_or_create(user=user, defaults=bursary_data)
        else:
            Bursary.objects.filter(user=user).update(**bursary_data)


class FoodForm(RegistrationFormStep):
    title = 'Food'

    meals = forms.MultipleChoiceField(
        label='I want to eat catered food for these meals:',
        choices=meal_choices(),
        widget=forms.CheckboxSelectMultiple,
        help_text="If you don't have a food bursary, meal prices are: "
                  "Breakfast 3 CAD, Lunch 7.50 CAD, Dinner 7.50 CAD.",
        required=False,
    )
    diet = forms.ChoiceField(
        label='My diet',
        choices=(
            ('', DIET_LABELS['']),
            ('vegetarian', DIET_LABELS['vegetarian']),
            ('vegan', DIET_LABELS['vegan']),
            ('other', DIET_LABELS['other']),
        ),
        required=False,
    )
    special_diet = forms.CharField(
        label='Details of my special dietary needs',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('meals', id='meals'),
            Field('diet', id='diet'),
            Field('special_diet', id='special_diet'),
        )

    @classmethod
    def get_initial(cls, user):
        try:
            food = user.attendee.food
        except ObjectDoesNotExist:
            return {}
        return {
            'meals': [meal.form_name for meal in food.meals.all()],
            'diet': food.diet,
            'special_diet': food.special_diet,
        }

    def clean(self):
        cleaned_data = super().clean()

        if (cleaned_data.get('diet') == 'other' and
                not cleaned_data.get('special_diet')):
            self.add_error('special_diet', 'Required when diet is "other"')

    def save(self, user, attendee):
        data = self.cleaned_data

        if not data['meals']:
            Food.objects.filter(attendee=attendee).delete()
            return

        food, created = Food.objects.update_or_create(
            attendee=attendee,
            defaults={field: data[field]
                      for field in ('diet', 'special_diet')})

        stored_meals = set(food.meals.all())
        requested_meals = set()
        for meal in data['meals']:
            meal, date = meal.split('_')
            date = parse_date(date)
            requested_meals.add(Meal.objects.get(meal=meal, date=date))

        food.meals.remove(*(stored_meals - requested_meals))
        food.meals.add(*(requested_meals - stored_meals))


class AccommForm(RegistrationFormStep):
    title = 'Accommodation'

    accomm = forms.BooleanField(
        label='I need conference-organised accommodation',
        widget=forms.Select(choices=(
            (False, 'No, I will find my own accommodation'),
            (True, 'Yes, I need accommodation'),
        )),
        required=False,
    )
    nights = forms.MultipleChoiceField(
        label="I'm requesting accommodation for these nights:",
        choices=night_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    requirements = forms.CharField(
        label='Do you have any particular accommodation requirements?',
        help_text='Anything that you want us to consider for room attribution '
                  'should be listed here (ex. "I want to be with Joe Hill", '
                  '"I snore", "I go to bed early")',
        required=False,
    )
    alt_accomm = forms.BooleanField(
        label='I would like to request alternative accommodation (only '
              'available if you receive a bursary)',
        required=False,
    )
    alt_accomm_choice = forms.ChoiceField(
        label='Select the accommodation you prefer during DebConf (only '
              'available if you receive a bursary)',
        choices=(
            ('rvc_single', ACCOMM_CHOICE_LABELS['rvc_single']),
            ('rvc_double', ACCOMM_CHOICE_LABELS['rvc_double']),
            ('hotel', ACCOMM_CHOICE_LABELS['hotel']),
        ),
        required=False,
    )
    special_needs = forms.CharField(
        label='My special needs',
        help_text='Wheelchair access or other any other needs we should be '
                  'aware of.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    childcare = forms.BooleanField(
        label='I need childcare for my kid(s)',
        required=False,
    )
    childcare_needs = forms.CharField(
        label='The childcare services I need are',
        help_text='How many hours a day? All the conference or only part of '
                  'it? etc.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    childcare_details = forms.CharField(
        label='Important informations about my kid(s)',
        help_text='Number, ages, languages spoken, special needs, etc.',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
    )
    family_usernames = forms.CharField(
        label='Usernames of my family members, '
              'who have registered separately',
        help_text="One per line. This isn't validated.",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        bursary_cleaned = self.get_cleaned_data_for_form(
            BursaryForm)
        accomm_details = Fieldset(
            'Accommodation Details',
            'nights',
            'requirements',
            css_id='accomm-details',
        )
        if bursary_cleaned.get('request'):
            accomm_details.fields += [
                Field('alt_accomm', id='alt_accomm'),
                Field('alt_accomm_choice', id='alt_accomm_choice'),
            ]

        self.helper.layout = Layout(
            HTML(
                '<p>By default, the accommodation provided is in <a href="'
                'https://wiki.debconf.org/wiki/DebConf17/Accommodation#On-site'
                '" target="_blank">shared classroom dorms on premises</a>. '
                'The cost is 30 CAD/night for attendees who do not receive a '
                'bursary.</p>'),
            Field('accomm', id='accomm'),
            accomm_details,
            Field('childcare', id='childcare'),
            Fieldset(
                'Childcare Details',
                'childcare_needs',
                'childcare_details',
                css_id='childcare-details',
            ),
            Field('special_needs'),
            Field('family_usernames'),
        )

    @classmethod
    def get_initial(cls, user):
        try:
            accomm = user.attendee.accomm
        except ObjectDoesNotExist:
            return {}

        initial = {
            'accomm': True,
            'nights': [night.form_name for night in accomm.nights.all()],
            'alt_accomm': bool(accomm.alt_accomm_choice),
        }
        initial.update({field: getattr(accomm, field) for field in (
            'requirements',
            'alt_accomm_choice',
            'childcare',
            'childcare_needs',
            'childcare_details',
            'special_needs',
            'family_usernames',
        )})
        return initial

    def clean_alt_accomm_choice(self):
        if not self.cleaned_data.get('alt_accomm'):
            return None
        return self.cleaned_data.get('alt_accomm_choice')

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('childcare'):
            if not cleaned_data.get('childcare_needs'):
                self.add_error('childcare_needs',
                               'Please provide us with your needs.')
            if not cleaned_data.get('childcare_details'):
                self.add_error(
                    'childcare_details',
                    "Please provide us with your children's details.")

        if not cleaned_data.get('accomm'):
            return

        if not cleaned_data.get('nights'):
            self.add_error(
                'nights',
                'Please select the nights you require accommodation for.')

        alt_accomm = None
        if cleaned_data.get('alt_accomm'):
            alt_accomm = cleaned_data.get('alt_accomm_choice')
        else:
            cleaned_data['alt_accomm_choice'] = None

        if alt_accomm == 'rvc_double' and not cleaned_data.get(
                'family_usernames'):
            for field in ('alt_accomm_choice', 'family_usernames'):
                self.add_error(
                    field,
                    "Please provide the username of the person you want to "
                    "share a room with.")

        if alt_accomm == 'hotel' and not cleaned_data.get('special_needs'):
            for field in ('alt_accomm_choice', 'special_needs'):
                self.add_error(
                    field,
                    "Please provide the special needs that lead you to "
                    "request a hotel room.")

        return cleaned_data

    def save(self, user, attendee):
        data = self.cleaned_data

        if not data['accomm']:
            Accomm.objects.filter(attendee=attendee).delete()
            return

        accomm, created = Accomm.objects.update_or_create(
            attendee=attendee,
            defaults={field: data[field] for field in (
                'requirements',
                'alt_accomm_choice',
                'childcare',
                'childcare_needs',
                'childcare_details',
                'special_needs',
                'family_usernames',
        )})

        stored_nights = set(accomm.nights.all())
        requested_nights = set()
        for night in data['nights']:
            date = parse_date(night.split('_')[1])
            requested_nights.add(AccommNight.objects.get(date=date))

        accomm.nights.remove(*(stored_nights - requested_nights))
        accomm.nights.add(*(requested_nights - stored_nights))


class BillingForm(RegistrationFormStep):
    title = 'Billing'

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

    attendee_fields = (
        'billing_address',
        'notes',
    )

    def clean(self):
        cleaned_data = super().clean()
        conf_reg_cleaned = self.get_cleaned_data_for_form(
            ConferenceRegistrationForm)
        paid = bool(conf_reg_cleaned.get('fee'))

        if paid and not cleaned_data.get('billing_address'):
            self.add_error('billing_address',
                           'Paid attendees need to provide a billing address')


class ConfirmationForm(RegistrationFormStep):
    title = 'Review your registration'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fieldsets = []

        contact_information_fieldset = Fieldset(
            'Contact Information',
            HTML('<div>'
                 '<strong>Nametag:</strong>'
                 '<pre>{{ nametag }}</pre>'
                 '</div>'),
            HTML('<p><strong>Email:</strong> {{ email }}</p>'),
            HTML('{% if phone %}'
                 '<p><strong>Phone:</strong> {{ phone }}</p>'
                 '{% endif %}'),
            HTML('{% if emergency_contact %}'
                 '<div>'
                 '<strong>Emergency contact:</strong>'
                 '<pre>{{ emergency_contact }}</pre>'
                 '</div>'
                 '{% endif %}'),
            HTML('{% if announce_me %}'
                 '<p class="check">Announce my arrival in the IRC channel '
                 'when I check-in at the conference</p>'
                 '{% endif %}'),
            HTML('{% if register_announce %}'
                 '<p class="check">Subscribe me to the '
                 '<em>DebConf-announce</em> mailing list</p>'
                 '{% endif %}'),
            HTML('{% if register_discuss %}'
                 '<p class="check">Subscribe me to the '
                 '<em>DebConf-discuss</em> mailing list</p>'
                 '{% endif %}'),
        )
        fieldsets += [contact_information_fieldset]

        conference_registration_fieldset = Fieldset(
            'Conference Registration',
            HTML('{% if debcamp %}'
                 '<p class="check">' + PLAN_DEBCAMP_LABEL + '</p>'
                 '{% endif %}'),
            HTML('{% if open_day %}'
                 '<p class="check">' + PLAN_OPENDAY_LABEL + '</p>'
                 '{% endif %}'),
            HTML('{% if debconf %}'
                 '<p class="check">' + PLAN_DEBCONF_LABEL + '</p>'
                 '{% endif %}'),
            HTML('<p>'
                 '<strong>Fee:</strong> '
                 '{% if fee == "pro" %}' + FEES_LABELS['pro'] + '{% endif %}'
                 '{% if fee == "corp" %}'
                 '' + FEES_LABELS['corp'] + '{% endif %}'
                 '{% if fee == "" %}'
                 '' + FEES_LABELS['regular'] + '{% endif %}'
                 '</p>'),
            HTML('{% if arrival or departure %}'
                 '<p><strong>Will attend from</strong> '
                 '{% if arrival %}'
                 '{{ arrival }}'
                 '{% else %}'
                 '<em>Unspecified</em>'
                 '{% endif %}'
                 ' <strong>to</strong> '
                 '{% if departure %}'
                 '{{ departure }}'
                 '{% else %}'
                 '<em>Unspecified</em>'
                 '{% endif %}'
                 '{% endif %}'),
            HTML('{% if arrival or departure %}'
                 '<p><strong>Dates are:</strong> '
                 '{% if not final_dates %}'
                 '' + FINAL_DATES_ESTIMATE_LABEL + ''
                 '{% else %}'
                 '' + FINAL_DATES_FINAL_LABEL + ''
                 '{% endif %}</p>'
                 '{% endif %}'),
        )
        fieldsets += [conference_registration_fieldset]

        personal_information_fieldset = Fieldset(
            'Personal Information',
            HTML('{% if t_shirt_cut %}'
                 '<p><strong>My t-shirt:</strong> '
                 '{% if t_shirt_cut == "s" %}'
                 '' + STRAIGHT_CUT_LABEL + ''
                 '{% elif t_shirt_cut == "w" %}'
                 '' + WOMENS_FITTED_CUT_LABEL + ''
                 '{% endif %} , '
                 '{% if t_shirt_size == "xs" %}'
                 '' + T_SHIRT_SIZES['xs'] + ''
                 '{% elif t_shirt_size == "s" %}'
                 '' + T_SHIRT_SIZES['s'] + ''
                 '{% elif t_shirt_size == "m" %}'
                 '' + T_SHIRT_SIZES['m'] + ''
                 '{% elif t_shirt_size == "l" %}'
                 '' + T_SHIRT_SIZES['l'] + ''
                 '{% elif t_shirt_size == "xl" %}'
                 '' + T_SHIRT_SIZES['xl'] + ''
                 '{% elif t_shirt_size == "2xl" %}'
                 '' + T_SHIRT_SIZES['2xl'] + ''
                 '{% elif t_shirt_size == "3xl" %}'
                 '' + T_SHIRT_SIZES['3xl'] + ''
                 '{% elif t_shirt_size == "4xl" %}'
                 '' + T_SHIRT_SIZES['4xl'] + ''
                 '{% elif t_shirt_size == "5xl" %}'
                 '' + T_SHIRT_SIZES['5xl'] + ''
                 '{% endif %}'
                 '{% endif %}'),
            HTML('{% if gender %}'
                 '<p><strong>Gender:</strong> '
                 '{% if gender == "f" %}'
                 'Female'
                 '{% elif gender == "m" %}'
                 'Male'
                 '{% elif gender == "o" %}'
                 'Other'
                 '{% endif %}'
                 '</p>'
                 '{% endif %}'),
            HTML('{% if country != "__" %}'
                 '<p><strong>Country:</strong> '
                 '{{ country_name }}'
                 '</p>'
                 '{% endif %}'),
            HTML('<p><strong>Languages:</strong> '
                 '{{ languages }}'
                 '</p>'),
        )
        fieldsets += [personal_information_fieldset]

        bursary_request = self.get_cleaned_data_for_form(BursaryForm).get(
            'request')
        if bursary_request:
            bursary_fields = [
                HTML('<p><strong>Covering:</strong> '
                     '{% if request == "food+accomm" %}'
                     '' + FOOD_ACCOMM_BURSARY_LABEL + ''
                     '{% elif request == "travel+food+accomm" %}'
                     '' + TRAVEL_FOOD_ACCOMM_BURSARY_LABEL + ''
                     '{% endif %}'
                     '</p>'),
                HTML('<p><strong>My level of need:</strong> '
                     '{% if need == "unable" %}'
                     '' + BURSARY_NEED_LABELS['unable'] + ''
                     '{% elif need == "sacrifice" %}'
                     '' + BURSARY_NEED_LABELS['sacrifice'] + ''
                     '{% elif need == "inconvenient" %}'
                     '' + BURSARY_NEED_LABELS['inconvenient'] + ''
                     '{% elif need == "non-financial" %}'
                     '' + BURSARY_NEED_LABELS['non-financial'] + ''
                     '{% endif %}'
                     '</p>'),
                HTML('<div>'
                     '<strong>My contributions to Debian:</strong>'
                     '<pre>{{ reason_contribution }}</pre>'
                     '</div>'),
                HTML('<div>'
                     '<strong>My plans for DebCamp or DebConf:</strong>'
                     '<pre>{{ reason_plans }}</pre>'
                     '</div>'),
                HTML('<div>'
                     '<strong>My eligibility for a diversity bursary:</strong>'
                     '<pre>{{ reason_diversity }}</pre>'
                     '</div>'),
            ]

            if bursary_request == 'travel+food+accomm':
                bursary_fields += [
                    HTML('<p><strong>My travel expense claim '
                         '(in USD):</strong> '
                         '{{ travel_bursary }}</p>'),
                    HTML('<p><strong>Traveling from:</strong> '
                         '{{ travel_from }}'
                         '</p>'),
                ]

            bursary_fieldset = Fieldset(
                'Bursary',
                *bursary_fields
            )
            fieldsets += [bursary_fieldset]

        food_fields = []
        if len(self.get_cleaned_data_for_form(FoodForm).get('meals')) > 0:
            food_fields += [
                HTML('{% if meals_summary %}'
                     '<div>'
                     '<strong>I want to eat catered '
                     'food for these meals:</strong>'
                     '<ul>'
                     '{% for day_summary in meals_summary %}'
                     '<li>{{ day_summary }}</li>'
                     '{% endfor %}'
                     '</ul>'
                     '</div>'
                     '{% endif %}'),
            ]

        if self.get_cleaned_data_for_form(FoodForm).get('diet'):
            food_fields += [
                HTML('<p><strong>My diet:</strong> '
                     '{% if diet == "vegetarian" %}'
                     '' + DIET_LABELS['vegetarian'] + ''
                     '{% elif diet == "vegan" %}'
                     '' + DIET_LABELS['vegan'] + ''
                     '{% elif diet == "other" %}'
                     '' + DIET_LABELS['other'] + ''
                     '{% endif %}'),
                HTML('<p><strong>Details of my special'
                     ' dietary needs:</strong> '
                     '{{ special_diet }}</p>'),
            ]

        if len(food_fields) > 0:
            food_fieldset = Fieldset(
                'Food',
                *food_fields
            )
            fieldsets += [food_fieldset]

        accomm_fields = []

        if self.get_cleaned_data_for_form(AccommForm).get('accomm'):
            accomm_fields += [
                HTML('<p class="check">I need accomodation.</p>'),
                HTML('<p><strong>For the following nights:</strong> '
                     '{{ accomm_nights_summary }}</p>'),
                HTML('{% if requirements %}'
                     '<p><strong>Special accomodation requirements:</strong> '
                     '{{ requirements }}</p>'
                     '{% endif %}'),
                HTML('{% if alt_accomm %}'
                     '<p><strong>Preferred accommodation:</strong> '
                     '{% if alt_accomm_choice == "rvc_single" %}'
                     '' + ACCOMM_CHOICE_LABELS['rvc_single'] + ''
                     '{% elif alt_accomm_choice == "rvc_double" %}'
                     '' + ACCOMM_CHOICE_LABELS['rvc_double'] + ''
                     '{% elif alt_accomm_choice == "rvc_double" %}'
                     '' + ACCOMM_CHOICE_LABELS['hotel'] + ''
                     '{% endif %}'
                     '</p>'
                     '{% endif %}'),
            ]

        if self.get_cleaned_data_for_form(AccommForm).get('childcare'):
            accomm_fields += [
                HTML('<p class="check">I need childcare</p>'),
                HTML('<div>'
                     '<strong>Childcare services I need</strong>'
                     '<pre>{{ childcare_needs }}'
                     '</div>'),
                HTML('<div>'
                     '<strong>Information about my kid(s)</strong>'
                     '<pre>{{ childcare_details }}'
                     '</div>'),
            ]

        if self.get_cleaned_data_for_form(AccommForm).get('special_needs'):
            accomm_fields += [
                HTML('<div>'
                     '<strong>My special needs</strong>'
                     '<pre>{{ special_needs }}</pre>'
                     '</div>'),
            ]

        if self.get_cleaned_data_for_form(AccommForm).get('family_usernames'):
            accomm_fields += [
                HTML('<div>'
                     '<strong>Usernames of family members</strong>'
                     '<pre>{{ family_usernames }}</pre>'
                     '</div>'),
            ]

        if len(accomm_fields) > 0:
            accomm_fieldset = Fieldset(
                'Accommodotation',
                *accomm_fields
            )
            fieldsets += [accomm_fieldset]

        billing_fields = [
            HTML('<div>'
                 '<strong>My billing address</strong>'
                 '<pre>{{ billing_address }}'
                 '</div>'),
        ]
        if self.get_cleaned_data_for_form(BillingForm).get('notes'):
            billing_fields += [
                HTML('<div>'
                     '<strong>Notes</strong>'
                     '<pre>{{ notes }}</pre>'
                     '</div>'),
            ]

        billing_fields += [
            HTML('<div id="cost-summary">'),
            HTML('<strong>Total due</strong>'),
            HTML('{% if meals_summary %}'
                 '<div class="due">'
                 '{% if meals_by_type.breakfast %}'
                 '<em>Breakfast:</em> '
                 '{{ food_price_by_type.breakfast }}<br>'
                 '{% endif %}'
                 '{% if meals_by_type.lunch %}'
                 '<em>Lunch:</em> {{ food_price_by_type.lunch }}<br>'
                 '{% endif %}'
                 '{% if meals_by_type.dinner %}'
                 '<em>Dinner:</em> '
                 '{{ food_price_by_type.dinner }}'
                 '{% endif %}'
                 '</div>'
                 '{% endif %}'),
            HTML('{% if nights %}'
                 '<div class="due">'
                 '<em>Accommodation:</em> '
                 '{{ accomm_total }}'
                 '</div>'
                 '{% endif %}'),
            HTML('{% if fee != "" %}'
                 '<div class="due">'
                 '<em>Fee:</em> '
                 '{{ fee_value }}'
                 ' CAD'
                 '</div>'
                 '{% endif %}'),
            HTML('<div class="total due">'
                 '<strong>Total:</strong> '
                 '{{ total_due }} CAD'
                 '</div>'),
            HTML('<p class="alert alert-info">'
                 "We haven't implemented online payment collection yet, "
                 "we'll let you know when we're ready to receive payment."
                 '</p>'),
            HTML('</div>')
        ]

        billing_fieldset = Fieldset(
            'Billing',
            *billing_fields
        )
        fieldsets += [billing_fieldset]

        self.helper.layout = Layout(
            *fieldsets
        )


REGISTRATION_FORMS = [
    PreambleForm,
    ContactInformationForm,
    ConferenceRegistrationForm,
    PersonalInformationForm,
    BursaryForm,
    FoodForm,
    AccommForm,
    BillingForm,
    ConfirmationForm,
]
