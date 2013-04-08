from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url('^sympa_config/$', 'thing_sympa.views.sympa_config'),
    )
