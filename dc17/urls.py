from django.conf.urls import url

from dc17.views import RegistrationWizard, UnregisterView


urlpatterns = [
    url(r'^register/$', RegistrationWizard.as_view(), name='register'),
    url(r'^unregister/$', UnregisterView.as_view(), name='unregister'),
]
