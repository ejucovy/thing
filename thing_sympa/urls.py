from django.conf.urls import patterns, include, url
from thing.urlconf import project_url as purl

urlpatterns = patterns('',
    url('^sympa_config/$', 'thing_sympa.views.sympa_config'),
    )
