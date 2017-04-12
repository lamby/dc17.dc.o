import json
import logging

from django.core.mail import EmailMultiAlternatives
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from django_countries import countries

from formtools.wizard.views import SessionWizardView
from wafer.utils import LoginRequiredMixin

from dc17.forms import REGISTRATION_FORMS
from dc17.models import Attendee, Bursary

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

            meals_by_day = {}
            meals_by_type = {
                'breakfast': 0,
                'dinner': 0,
                'lunch': 0,
            }

            for selection in context_update.get('meals'):
                (meal, day) = tuple(selection.split('_', 2))

                if meals_by_day.get(day, None) is None:
                    meals_by_day[day] = []
                meals_by_day[day] += [meal]
                meals_by_type[meal] += 1

            meals_summary = sorted([
                day + ': ' + (', '.join(meals))
                for day, meals in meals_by_day.items()
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

                'meals_summary': meals_summary,
                'meals_by_type': meals_by_type,
                'food_price_by_type': {
                    'breakfast': '{} breakfast(s) * 3 CAD$ = {:.2f}'
                    ' CAD$'.format(
                        meals_by_type.get('breakfast'),
                        meals_by_type.get('breakfast') * 3
                    ),
                    'lunch': '{} lunch(es) * 7.50 CAD$ = {:.2f} CAD$'.format(
                        meals_by_type.get('lunch'),
                        meals_by_type.get('lunch') * 7.5
                    ),
                    'dinner': '{} dinner(s) * 7.50 CAD$ = {:.2f} CAD$'.format(
                        meals_by_type.get('dinner'),
                        meals_by_type.get('dinner') * 7.5
                    )
                },

                'accomm_nights_summary': ', '.join(
                    [n[6:] for n in context_update.get('nights')]
                ),
                'accomm_total': "{} night(s) * 30 CAD$ = {:.2f} CAD$".format(
                    len(context_update.get('nights')),
                    len(context_update.get('nights')) * 30
                ),

                'fee_value': '{:.2f}'.format(FEES[context_update.get('fee')]),

                'total_due': len(context_update.get('nights')) * 30 +
                meals_by_type.get('breakfast') * 3 +
                meals_by_type.get('lunch') * 7.5 +
                meals_by_type.get('dinner') * 7.5 +
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
        user = self.request.user
        attendee_data = {}
        for form in form_list:
            attendee_data.update(form.get_attendee_data())

        attendee, fresh_registration = Attendee.objects.update_or_create(
            user=user, defaults=attendee_data)

        for form in form_list:
            form.save(user, attendee)

        self.log_registration(user, fresh_registration)

        context = {
            'fresh_registration': fresh_registration,
        }
        self.send_confirmation_email(user, context)
        return render(self.request, 'dc17/registration_confirmation.html',
                      context)

    def send_confirmation_email(self, user, context):
        txt = render_to_string('dc17/registration_confirmation_email.txt',
                               context)
        to = user.email
        if context['fresh_registration']:
            subject = '[DebConf 17] Registration confirmation'
        else:
            subject = '[DebConf 17] Registration updated'
        email_message = EmailMultiAlternatives(subject, txt, to=[to])
        email_message.send()

    def log_registration(self, user, fresh_registration):
        log = logging.getLogger('dc17.registration')
        form_data = json.dumps(self.get_all_cleaned_data(),
                               cls=DjangoJSONEncoder)
        log.info('User registered: user=%s updated=%s data=%s',
                 user.username, not fresh_registration, form_data)


class UnregisterView(TemplateView):
    template_name = 'dc17/unregister.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'registered': Attendee.objects.filter(user=self.request.user)
                                  .exists(),
            'bursary': Bursary.objects.filter(user=self.request.user).exists(),
        })
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user.attendee:
            user.attendee.delete()
        if user.bursary:
            user.bursary.request = None
            user.bursary.save()

        context = self.get_context_data()
        return self.render_to_response(context)
