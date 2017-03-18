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
            context_update = {}
            for form, step in self.form_list.items():
                cleaned_data = self.get_cleaned_data_for_step(form)

                if cleaned_data is None:
                    continue

                for key, value in cleaned_data.items():
                    context_update[key] = value

            context.update(context_update)

            food_selection_summary = {}
            for selection in context_update.get('food_selection'):
                (meal, day) = tuple(selection.split('_', 2))

                if food_selection_summary.get(day, None) is None:
                    food_selection_summary[day] = []
                food_selection_summary[day] = [meal]

            for day, meals in food_selection_summary.items():
                food_selection_summary[day] = ', '.join(meals)

            context.update({
                'nametag': '{}\n{}\n{}'.format(
                    context_update.get('name'),
                    context_update.get('nametag_2'),
                    context_update.get('nametag_3')
                ),

                'genders': {
                    'm': 'Male',
                    'f': 'Female',
                },
                'country_name': dict(countries).get(
                    context_update.get('country'), None
                ),

                'food_selection_summary': food_selection_summary,

                'accomm_nights_summary': ', '.join(
                    [n[6:] for n in context_update.get('accomm_nights')]
                ),
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
