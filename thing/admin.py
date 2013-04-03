from django.contrib import admin
from djangohelpers.lib import register_admin
from thing.models import Project, ProjectMember, UserProfile, ProjectFeedSource, ProjectTool, ProjectInstalledTool

register_admin(Project)
register_admin(ProjectMember)
register_admin(UserProfile)
register_admin(ProjectFeedSource)
register_admin(ProjectTool)
register_admin(ProjectInstalledTool)
