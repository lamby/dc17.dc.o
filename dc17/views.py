from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


from formtools.wizard.views import SessionWizardView

from dc17.forms import (
    RegistrationForm0,
    RegistrationForm1,
    RegistrationForm2,
    RegistrationForm3,
    RegistrationForm4,
    RegistrationForm5,
)


class RegistrationWizard(SessionWizardView):
    template_name = 'dc17/registration_form.html'
    form_list = [
        RegistrationForm0,
        RegistrationForm1,
        RegistrationForm2,
        RegistrationForm3,
        RegistrationForm4,
        RegistrationForm5,
    ]

    def get_form_initial(self, step):
        initial = super(RegistrationWizard, self).get_form_initial(step)
        user = self.request.user
        if step == '0':
            initial.update({
                'name': user.get_full_name(),
                'nametag_3': user.username,
                'email': user.email,
            })
        return initial

    def get_form_kwargs(self, step):
        kwargs = super(RegistrationWizard, self).get_form_kwargs(step)
        kwargs['wizard'] = self
        return kwargs

    def done(self, form_list, **kwargs):
        return HttpResponseRedirect(
            reverse('wafer_user_profile', args=(self.request.user.username,)))
