from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from zope.dottedname.resolve import resolve

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

    @models.permalink
    def team_url(self):
        return ('projects_project_team', [self.slug])

    @models.permalink
    def summary_url(self):
        return ('projects_project_summary', [self.slug])

    @models.permalink
    def theme_url(self):
        return ('projects_project_theme', [self.slug])

    @models.permalink
    def manage_team_url(self):
        return ('projects_project_manage_team', [self.slug])

    @models.permalink
    def preferences_url(self):
        return ('projects_project_preferences', [self.slug])

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

    def nav_entries(self):
        nav = [
            (self.summary_url(), _("Summary")),
            (self.team_url(), _("Team")),
            ]
        for tool in self.project_tools():
            tool_nav = tool.nav_entries()
            if tool_nav:
                nav.extend(tool_nav)
        return nav

    def project_tools(self):
        tools = list(self.tools.all())
        return [tool.get_tool() for tool in tools]

    def nav_management_entries(self):
        nav = [
            (self.manage_team_url(), _("Team")),
            (self.preferences_url(), _("Preferences")),
            ]
        for tool in self.project_tools():
            tool_nav = tool.nav_management_entries()
            if tool_nav:
                nav.extend(tool_nav)
        return nav

    def dispatch(self, path_info):
        """
        @@TODO unit test this!

        need to handle:

        /trac/first-env/
        /trac/first-env/query
        /trac/first-env/query/

        /blog/
        /blog/2010/07/25/opencore-0181-released/

        /project-home
        /project-home/
        /project-home/edit/
        /project-home/history

        /wikis/second-wiki/wiki-home

        /dotnyc/

        Also how to handle proxying to a downstream site whose root 
        lives exclusively at "/" (not /index.php)?
        """

        components = path_info.lstrip("/").split("/")

        tools = self.tools.all()
        paths = {}
        for tool in tools:
            tool = tool.get_tool()
            for path in tool.proxy_paths():
                paths[path] = tool

        remaining = []
        while components:
            prefix = '/'.join([''] + components)
            print prefix
            if prefix in paths:
                tool = paths[prefix]
                tool.consume_request(self.homepage_url().rstrip("/") + "/",
                                     prefix.lstrip("/"),
                                     '/'.join([''] + remaining))
                return tool
            remaining.insert(0, components.pop(-1))
        return None

class ProjectFeedSource(models.Model):
    
    class Meta:
        verbose_name = _('project feed source')
        verbose_name_plural = _('project feed sources')
    
    project = models.ForeignKey(
        Project, verbose_name=_('project'), related_name="feed_sources")
    feed_source = models.URLField(_('feed source'), max_length=255, null=True, blank=True)
    title = models.CharField(_('feed title'), max_length=255)

    feed_data_cache = models.TextField(null=True, blank=True)
    feed_data_cached_on = models.DateTimeField(null=True, blank=True)

    def logo_url(self):
        # @@TODO
        import random
        return random.choice(["/static/blog.gif", "/static/mailinglist.gif",
                              "/static/tasks.gif", "/static/wiki.gif"])

    def bind_data(self, feed_data):
        from django.utils import timezone
        self.feed_data_cache = feed_data
        self.feed_data_cached_on = timezone.now()

    def cache_expired(self):
        import datetime
        from django.utils import timezone
        if not self.feed_data_cache:
            return True
        if not self.feed_data_cached_on:
            return True
        if self.feed_data_cached_on < timezone.now() - datetime.timedelta(1):
            return True
        return False

    def get_feed(self):
        import feedparser
        feed = feedparser.parse(self.feed_data_cache or self.feed_source)
        from thing.utils import FeedEntry
        for entry in feed.entries[:5]:
            try:
                description = entry.description
            except AttributeError:
                description = ''
            yield FeedEntry(entry.link, entry.title, description, 
                            item_data=[entry.published])

class ProjectNavigationEntry(models.Model):

    class Meta:
        verbose_name = _('project navigation entry')
        verbose_name_plural = _('project navigation entries')
    
    project = models.ForeignKey(Project, verbose_name=_('project'),
#                                related_name="nav_entries"
                                )

    title = models.CharField('title', max_length=255)
    url = models.CharField('url', max_length=255)

        
class ProjectInstalledTool(models.Model):

    class Meta:
        verbose_name = _('project tool')
        verbose_name_plural = _('project tools')

    project = models.ForeignKey(Project, verbose_name=_('project'),
                                related_name="tools")
    tool_dottedname = models.CharField(_('project tool dotted name'),
                                       max_length=50)
    configuration = models.TextField(_('project tool configuration'),
                                     null=True, blank=True)

    def get_tool(self):
        return resolve(self.tool_dottedname)(self)

class ProjectTool(models.Model):
    
    class Meta:
        verbose_name = _('project tool')
        verbose_name_plural = _('project tools')
        unique_together = [('project', 'app')]
    
    project = models.ForeignKey(Project, verbose_name=_('project'),
                                related_name="toolss")

    app = models.CharField(_('app path'), max_length=50)

    homepage = models.CharField(_('app homepage'), max_length=150)

    title = models.CharField(_('app title'), max_length=30)
    
    deliverance_rules = models.TextField(_('app deliverance rules'))

    url = models.CharField(_('app url'), max_length=200)

    def match_request(self, path_info):
        path_info = path_info.lstrip("/")

        if '/' in path_info:
            app, path = path_info.split("/", 1)
        else:
            app = path_info
            path = '/'
        if self.app == app:
            return path
        
    def bind_request(self, path_info):
        self.script_name = self.project.homepage_url().rstrip("/") + "/%s/" % (
            self.app.strip("/"))
        self.path_info = path_info
        return self

    def relative_path(self):
        path = "/".join((
                self.app.strip("/"), self.homepage.strip("/")))
        return "%s%s" % (self.project.homepage_url(),
                         path.strip("/"))

    def nav_entries(self):
        return [
            (self.relative_path(), self.title),
            ]

    def nav_management_entries(self):
        return None

class ProjectMember(models.Model):
    
    class Meta:
        verbose_name = _('project member')
        verbose_name_plural = _('project members')
        unique_together = [('project', 'user')]
    
    project = models.ForeignKey(Project, verbose_name=_('project'),
                                related_name='memberships')
    user = models.ForeignKey('auth.User', verbose_name=_('user'),
                             related_name='memberships')

    def homepage_url(self):
        if self.anonymous:
            return self.project.homepage_url()
        return self.user.profile.homepage_url()

    def logo_url(self):
        if self.anonymous:
            return self.project.logo_url()
        return self.user.profile.logo_url()

    @property
    def location(self):
        if self.anonymous:
            return None
        return self.user.profile.location

    @property
    def projects(self):
        if self.anonymous:
            return [self.project]
        return self.user.profile.projects()

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

    def is_admin(self):
        return self.role == "admin"

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
                'homepage_url': membership.project.homepage_url(),
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
