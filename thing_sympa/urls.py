from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url('^sympa/settings/$', 'thing_sympa.views.sympa_config'),
    url('^sympa/$', 'thing_sympa.views.sympa_index'),
    )
