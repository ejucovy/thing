from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'thing.views',

    url(r'^$', 'home', name="home"),
    url(r'^theme.html/$', 'theme', name="theme"),
    # @@TODO: xinha config

    url(r'^people/$', 'people', name="people"), 
    url(r'^new-people/$', 'people_recently_created'), #check

    url(r'^people/(?P<username>[\d\w\-_]+)/$', 'people_person',
        name='people_person'), #check
    url(r'^people/(?P<username>[\d\w\-_]+)/profile/$', 'people_person_profile',
        name="people_person_profile"),
#    url(r'^people/(?P<username>[\d\w\-_]+)/profile-edit/$', 'people_person_profile_edit'),
    url(r'^people/(?P<username>[\d\w\-_]+)/account/$', 'people_person_account',
        name="people_person_account"),

    url(r'^projects/$', 'projects', name="projects"),
    url(r'^create-project/$', 'projects_create', name="projects_create"),
    url(r'^recently-updated-projects/$', 'projects_recently_updated'), #check
    url(r'^recently-created-projects/$', 'projects_recently_created'), #check

    url(r'^projects/(?P<slug>[\d\w\-_]+)/$', 'projects_project',
        name='projects_project'), # check

    url(r'^projects/(?P<slug>[\d\w\-_]+)/members.xml$',
        'projects_project_members_xml',
        name='projects_project_members_xml'), 
    url(r'^projects/(?P<slug>[\d\w\-_]+)/info.xml$',
        'projects_project_info_xml',
        name='projects_project_info_xml'), 
    url(r'^projects/(?P<slug>[\d\w\-_]+)/theme/$', 'projects_project_theme',
        name="projects_project_theme"), #check

    url(r'^projects/(?P<slug>[\d\w\-_]+)/summary/$', 'projects_project_summary',
        name="projects_project_summary"),

#    url(r'^projects/(?P<slug>[\d\w\-_]+)/contents/$', 'projects_project_contents'),
    url(r'^projects/(?P<slug>[\d\w\-_]+)/team/$', 'projects_project_team',
        name="projects_project_team"), #check

    url(r'^projects/(?P<slug>[\d\w\-_]+)/manage-team/$', 'projects_project_manage_team',
        name="projects_project_manage_team"),
    url(r'^projects/(?P<slug>[\d\w\-_]+)/preferences/$', 'projects_project_preferences',
        name="projects_project_preferences"),
#    url(r'^projects/(?P<slug>[\d\w\-_]+)/export/$', 'projects_project_export'),
#    url(r'^projects/(?P<slug>[\d\w\-_]+)/delete/$', 'projects_project_delete'),

#    url(r'^projects/(?P<slug>[\d\w\-_]+)/contact-team/$', 'projects_project_contact_team'),

#    url(r'^projects/(?P<slug>[\d\w\-_]+)/request-membership/$', 'projects_project_request_membership'),
#    url(r'^projects/(?P<slug>[\d\w\-_]+)/invite/$', 'projects_project_invite'),

    url(r'^projects/(?P<slug>[\d\w\-_]+)/(?P<path_info>.*)$',
        'projects_project_dispatch'),

#    url(r'^search/$', 'search'),
#    url(r'^search/people/$', 'search_people'),
#    url(r'^search/people/location/$', 'search_people_location'),
#    url(r'^search/projects/$', 'search_projects'),
    url(r'^search/everything$', 'search_everything', name="search_everything"),
    )

from django.contrib.auth import views as auth_views

urlpatterns += patterns(
    '',

    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html'},
        name='login'),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html'},
        name='logout'),
    url(r'^join/$',
        'registration_workflow.views.register',
        name='join'),

    url(r'^forgot/$', 'forgot', name='forgot'),

    (r'^accounts/contact/', include('contact_manager.urls')),
    (r'^accounts/', include('registration_workflow.urls')),
    
    #url(r'^accounts/resend-confirmation/$',
    #    'inactive_user_workflow.views.resend_confirmation_email',
    #    name='resend-user-confirmation'),
    #url(r'^accounts/login/$',
    #    'inactive_user_workflow.views.login.login',
    #    {'template_name': 'registration/login.html'},
    #    name='auth_login'),



    
    url(r'^admin/', include(admin.site.urls)),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
    )

