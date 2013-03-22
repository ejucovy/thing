from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',

    url(r'^register/$',
        'registration_workflow.views.register',
        name='registration_register'),

    url(r'^inactive/$',
        'registration_workflow.views.inactive',
        name='registration_inactive'),
    
    (r'', include('registration_workflow.auth_urls')),
    )
