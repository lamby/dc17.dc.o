from django.conf.urls import url

from dc17.views import RegistrationWizard


urlpatterns = [
    url(r'^register/$', RegistrationWizard.as_view()),
]
