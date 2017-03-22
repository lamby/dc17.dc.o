from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django_countries import countries

from formtools.wizard.views import SessionWizardView
from wafer.utils import LoginRequiredMixin

from dc17.forms import REGISTRATION_FORMS

FEES = {
    '': 0,
    'pro':  200,
    'corp': 500
}


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

            food_selection_by_day = {}
            food_selection_by_type = {
                'breakfast': 0,
                'dinner': 0,
                'lunch': 0,
            }

            for selection in context_update.get('food_selection'):
                (meal, day) = tuple(selection.split('_', 2))

                if food_selection_by_day.get(day, None) is None:
                    food_selection_by_day[day] = []
                food_selection_by_day[day] += [meal]
                food_selection_by_type[meal] += 1

            food_selection_summary = sorted([
                day + ': ' + (', '.join(meals))
                for day, meals in food_selection_by_day.items()
            ])

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
                'food_selection_by_type': food_selection_by_type,
                'food_price_by_type': {
                    'breakfast': '{} breakfast(s) * 3 CAD$ = {:.2f}'
                    ' CAD$'.format(
                        food_selection_by_type.get('breakfast'),
                        food_selection_by_type.get('breakfast') * 3
                    ),
                    'lunch': '{} lunch(es) * 7.50 CAD$ = {:.2f} CAD$'.format(
                        food_selection_by_type.get('lunch'),
                        food_selection_by_type.get('lunch') * 7.5
                    ),
                    'dinner': '{} dinner(s) * 7.50 CAD$ = {:.2f} CAD$'.format(
                        food_selection_by_type.get('dinner'),
                        food_selection_by_type.get('dinner') * 7.5
                    )
                },

                'accomm_nights_summary': ', '.join(
                    [n[6:] for n in context_update.get('accomm_nights')]
                ),
                'accomm_total': "{} night(s) * 30 CAD$ = {:.2f} CAD$".format(
                    len(context_update.get('accomm_nights')),
                    len(context_update.get('accomm_nights')) * 30
                ),

                'fee_value': '{:.2f}'.format(FEES[context_update.get('fee')]),

                'total_due': len(context_update.get('accomm_nights')) * 30 +
                food_selection_by_type.get('breakfast') * 3 +
                food_selection_by_type.get('lunch') * 7.5 +
                food_selection_by_type.get('dinner') * 7.5 +
                FEES[context_update.get('fee')]

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
