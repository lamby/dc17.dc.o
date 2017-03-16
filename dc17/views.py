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
        context = super(RegistrationWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.step1 == self.steps.count:
            all_cleaned_data = self.get_all_cleaned_data()
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
                'country': all_cleaned_data.get('country'),
                'country_name': dict(countries)[all_cleaned_data.get('country')],
                'languages': all_cleaned_data.get('languages'),
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
