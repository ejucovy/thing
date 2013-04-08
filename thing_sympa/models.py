from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from thing.models import Project

class ProjectSympaTool(models.Model):
    project = models.ForeignKey(Project, verbose_name=_("project"))

    list_path = models.CharField(_('sympa list path'), max_length=80)
    list_name = models.CharField(_('sympa list name'), max_length=200)

from django.contrib import admin
admin.site.register(ProjectSympaTool)
