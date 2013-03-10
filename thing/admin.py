from django.contrib import admin
from djangohelpers.lib import register_admin
from thing.models import Project, ProjectMember, UserProfile, ProjectFeedSource

register_admin(Project)
register_admin(ProjectMember)
register_admin(UserProfile)
register_admin(ProjectFeedSource)
