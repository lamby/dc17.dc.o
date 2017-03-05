from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from formtools.wizard.views import SessionWizardView
from wafer.utils import LoginRequiredMixin

from dc17.forms import REGISTRATION_FORMS


class RegistrationWizard(LoginRequiredMixin, SessionWizardView):
    template_name = 'dc17/registration_form.html'
    form_list = REGISTRATION_FORMS

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
