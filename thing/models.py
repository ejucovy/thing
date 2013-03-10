from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

class Project(models.Model):

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    name = models.CharField(_('project name'), max_length=255)
    slug = models.SlugField(_('project slug'), unique=True)

    description = models.TextField(_('project description'), null=True, blank=True)

    logo = models.CharField(_('project logo'), max_length=100, null=True, blank=True)

    POLICY_CHOICES = (
        ('open', _('open security policy')),
        ('medium', _('medium security policy')),
        ('closed', _('closed security policy')),
        )
    policy = models.CharField(_('security policy'), max_length=10, 
                              choices=POLICY_CHOICES,
                              db_index=True)

    def policy_token(self):
        return "%s_policy" % self.policy

    homepage = models.CharField(_('project homepage'), max_length=30, default='summary')

    created = models.DateTimeField(_('project created'), auto_now_add=True)
    updated = models.DateTimeField(_('project updated'), auto_now=True)

    creator = models.ForeignKey('auth.User', verbose_name=_('project creator'))

    @models.permalink
    def homepage_url(self):
        return ('projects_project', [self.slug])

    def logo_url(self):
        if self.logo:
            return self.logo
        return '/static/img/default_project_logo.png'

    def to_json(self, include_members=False):
        data = {
            'slug': self.slug,
            'name': self.name,
            'url': self.homepage_url(),
            'description': self.description,
            'created': self.created,
            'updated': self.updated,

            'creator': self.creator.profile.to_json(),
            'logo': self.logo_url(),

            '__obj': self,
            }
        if include_members:
            data['num_members'] = self.num_members
        return data

    def get_membership(self, user):
        if user.is_anonymous():
            raise ProjectMember.DoesNotExist
        return ProjectMember.objects.get(project=self, user=user)

    def __unicode__(self):
        return self.name

class ProjectTool(models.Model):
    
    class Meta:
        verbose_name = _('project tool')
        verbose_name_plural = _('project tools')
        unique_together = [('project', 'tool')]
    
    project = models.ForeignKey(Project, verbose_name=_('project'))

    TOOL_CHOICES = (
        ('blogs', _('blog tool')),
        ('wikis', _('wiki tool')),
        ('tasks', _('task tracker tool')),
        ('lists', _('mailing list tool')),
        )
    tool = models.CharField(_('tool'), max_length=10, choices=TOOL_CHOICES)

class ProjectMember(models.Model):
    
    class Meta:
        verbose_name = _('project member')
        verbose_name_plural = _('project members')
        unique_together = [('project', 'user')]
    
    project = models.ForeignKey(Project, verbose_name=_('project'),
                                related_name='memberships')
    user = models.ForeignKey('auth.User', verbose_name=_('user'),
                             related_name='memberships')

    ROLE_CHOICES = (
        ('member', _('project role: member')),
        ('admin', _('project role: admin')),
        )
    role = models.CharField(max_length=25, db_index=True, choices=ROLE_CHOICES)

    def role_token(self):
        if self.role == "member":
            return "ProjectMember"
        if self.role == "admin":
            return "ProjectAdmin"

    anonymous = models.BooleanField(default=False, verbose_name=_('project member anonymous flag'))
    pseudonym = models.CharField(max_length=300, null=True, blank=True, unique=True)

    def __unicode__(self):
        if self.anonymous:
            return self.pseudonym
        return unicode(self.user)
    
    created = models.DateTimeField(_('project member created'), auto_now_add=True)
    updated = models.DateTimeField(_('project member updated'), auto_now=True)
    
class UserProfile(models.Model):
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    user = models.OneToOneField('auth.User', verbose_name=_('user'), 
                                related_name="profile")

    location = models.CharField(_('user location'), max_length=255, null=True, blank=True)
    website = models.URLField(_('user website'), null=True, blank=True)

    about = models.TextField(_('user about'), null=True, blank=True)
    interests = models.TextField(_('user interests'), null=True, blank=True)

    created = models.DateTimeField(_('user profile created'), auto_now_add=True)
    updated = models.DateTimeField(_('user profile updated'), auto_now=True)

    def memoize_projects(self, memberships):
        self._projects = [{
                'name': membership.project.name,
                'url': membership.project.homepage_url(),
                } for membership in memberships]
        return self._projects

    def projects(self):
        if hasattr(self, '_projects'):
            return self._projects
        memberships = ProjectMember.objects.select_related("project").filter(
            user=self.user, anonymous=False).exclude(project__policy="closed")
        return self.memoize_projects(memberships)
    
    @models.permalink
    def homepage_url(self):
        return ('people_person', [self.user.username])

    def logo_url(self):
        return '/static/img/default_person_logo.png'

    def to_json(self, include_projects=False):
        data = {
            'username': self.user.username,
            'fullname': self.user.get_full_name() or self.user.username,
            'created': self.created,
            'last_login': self.user.last_login,

            'logo': self.logo_url(),
            
            'url': self.homepage_url(),
            'user_link': self.render_html(),

            'location': self.location,
            'website': self.website,
            'about': self.about,
            'interests': self.interests,

            '__obj': self,
            }
        if include_projects:
            data['projects'] = self.projects()
        return data

    def render_html(self):
        return mark_safe(u'<a href="%s">%s</a>' % (self.homepage_url(), unicode(self.user)))

from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
import libopencore.auth
def set_cookie(sender, request, user, **kwargs):
    secret = libopencore.auth.get_secret(settings.OPENCORE_SECRET_FILENAME)
    val = libopencore.auth.generate_cookie_value(user.username, secret)
    request.set_cookie("__ac", val)
user_logged_in.connect(set_cookie)

def unset_cookie(sender, request, user, **kwargs):
    request.delete_cookie("__ac")
user_logged_out.connect(unset_cookie)
