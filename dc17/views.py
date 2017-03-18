from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django_countries import countries

from formtools.wizard.views import SessionWizardView
from wafer.utils import LoginRequiredMixin

from dc17.forms import REGISTRATION_FORMS


class RegistrationWizard(LoginRequiredMixin, SessionWizardView):
    form_list = REGISTRATION_FORMS

    def get_template_names(self):
        if self.steps.step1 == self.steps.count:
            return 'dc17/confirmation_form.html'
        else:
            return 'dc17/registration_form.html'

    def get_context_data(self, form, **kwargs):
        context = super(RegistrationWizard, self).get_context_data(
            form=form,
            **kwargs)
        if self.steps.step1 == self.steps.count:
            all_cleaned_data = self.get_all_cleaned_data()
            country = all_cleaned_data.get('country')

            context.update({
                'nametag': '{}\n{}\n{}'.format(
                    all_cleaned_data.get('name'),
                    all_cleaned_data.get('nametag_2'),
                    all_cleaned_data.get('nametag_3')
                ),
                'email': all_cleaned_data.get('email'),
                'phone': all_cleaned_data.get('phone'),
                'emergency_contact': all_cleaned_data.get('emergency_contact'),
                'announce_me': all_cleaned_data.get('announce_me'),
                'register_announce': all_cleaned_data.get('register_announce'),
                'register_discuss': all_cleaned_data.get('register_discuss'),

                'debcamp': all_cleaned_data.get('debcamp'),
                'open_day': all_cleaned_data.get('open_day'),
                'debconf': all_cleaned_data.get('debconf'),
                'fee': all_cleaned_data.get('fee'),
                'arrival': all_cleaned_data.get('arrival'),
                'departure': all_cleaned_data.get('departure'),
                'final_dates': all_cleaned_data.get('final_dates'),

                't_shirt_cut': all_cleaned_data.get('t_shirt_cut'),
                't_shirt_size': all_cleaned_data.get('t_shirt_size'),
                'genders': {
                    'm': 'Male',
                    'f': 'Female',
                },
                'gender': all_cleaned_data.get('gender'),
                'country': country,
                'country_name': dict(countries).get(country, None),
                'languages': all_cleaned_data.get('languages'),

                'bursary': all_cleaned_data.get('bursary'),
                'bursary_reason_contribution': all_cleaned_data.get(
                    'bursary_reason_contribution'),
                'bursary_reason_plans': all_cleaned_data.get(
                    'bursary_reason_plans'),
                'bursary_reason_diversity': all_cleaned_data.get(
                    'bursary_reason_diversity'),
                'bursary_need': all_cleaned_data.get(
                    'bursary_need'),
                'travel_bursary': all_cleaned_data.get(
                    'travel_bursary'),
                'travel_from': all_cleaned_data.get(
                    'travel_from'),

                'accomm_nights': ', '.join(
                    [n[6:] for n in all_cleaned_data.get('accomm_nights')]
                ),
                'accomm_special_requirements': all_cleaned_data.get(
                    'accomm_special_requirements'),
                'alt_accomm': all_cleaned_data.get('alt_accomm'),
                'alt_accomm_choice': all_cleaned_data.get(
                    'alt_accomm_choice'),
                'childcare_needs': all_cleaned_data.get(
                    'childcare_needs'),
                'childcare_details': all_cleaned_data.get(
                    'childcare_details'),
                'special_needs': all_cleaned_data.get('special_needs'),
                'family_usernames': all_cleaned_data.get('family_usernames'),

                'billing_address': all_cleaned_data.get('billing_address'),
                'notes': all_cleaned_data.get('notes'),
            })

        return context

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        user = self.request.user
        form = self.form_list[step]
        initial.update(form.get_initial(user))
        return initial

    def get_form_kwargs(self, step):
        kwargs = super().get_form_kwargs(step)
        kwargs['wizard'] = self
        return kwargs

    def done(self, form_list, **kwargs):
        return HttpResponseRedirect(
            reverse('wafer_user_profile', args=(self.request.user.username,)))
