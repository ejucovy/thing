import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from djangohelpers.lib import allow_http, rendered_with
import grequests
import json
from thing.models import Project, UserProfile, ProjectMember
from thing import utils
from topp.utils.pretty_date import prettyDate

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
def as_json(view):
    def inner(*args, **kw):
        data = view(*args, **kw)
        if not isinstance(data, dict):
            return data
        return HttpResponse(json.dumps(data, default=dthandler),
                            content_type="application/json")
    return inner

@allow_http("GET")
@rendered_with("thing/theme.html")
def theme(request):
    return {}

@allow_http("GET")
@rendered_with("thing/home.html")
def home(request):
    chrome = {}

    recently_created_projects = utils.projects_recently_created()
    chrome.update({
            'news': [
                utils.FeedEntry()
                for news in utils.recent_news_items()
                ],
            'newest_projects': [
                utils.FeedEntry(project['url'], project['name'], 
                                project['description'],
                                item_data=[
                        _("created %(date)s by %(user_link)s") % {
                            'date': prettyDate(project['created']),
                            'user_link': project['creator']['user_link'],
                            },
                        ],
                                image_url=project['logo'],
                                image_class="oc-project-logo",
                                )
                for project in recently_created_projects
                ],
            'updated_projects': [
                utils.FeedEntry(project['url'], project['name'], 
                                project['description'],
                                item_data=[
                        _("%(num_members)s members") % {
                            'num_members': project['num_members']},
                        _("last updated %(date)s") % {
                            'date': prettyDate(project['updated'])},
                        ],
                                image_url=project['logo'],
                                image_class="oc-project-logo",
                                )
                for project in utils.projects_recently_updated(exclude=[
                        project['slug'] for project in recently_created_projects])
                ],
            })
    return chrome


@allow_http("GET")
@rendered_with("thing/people.html")
def people(request):
    chrome = {}
    chrome.update({
            'recent_members': [
                utils.FeedEntry(person['url'], person['fullname'], 
                                person['about'],
                                item_data=[
                        person['location'],
                        _("Member since %(date)s") % {'date': prettyDate(person['created'])},
                        ],
                                image_url=person['logo'],
                                image_class="photo",
                                )
                for person in utils.people_recently_created()],
            })
    return chrome

@allow_http("GET")
def people_person_profile(request, username):
    return HttpResponse("OK")
@allow_http("GET")
def people_person_account(request, username):
    return HttpResponse("OK")

@allow_http("GET")
def search_everything(request):
    return HttpResponse("OK")

@allow_http("GET")
def login(request):
    return HttpResponse("OK")
logout = join = login

@allow_http("GET")
@rendered_with("thing/projects.html")
def projects(request):
    chrome = {}
    chrome.update({
            'updated_projects': [
                utils.FeedEntry(project['url'], project['name'], 
                                project['description'],
                                item_data=[
                        _("%(num_members)s members, last updated %(date)s") % {
                            'num_members': project['num_members'],
                            'date': prettyDate(project['updated'])},
                        ],
                                image_url=project['logo'],
                                image_class="oc-project-logo",
                                )
                for project in utils.projects_recently_updated(limit=10)],
            })
    return chrome

#@@TODO: POST to create project
@allow_http("GET")
@rendered_with("thing/projects_create.html")
def projects_create(request):
    return {}

@allow_http("GET")
@as_json
def people_recently_created(request):
    return {'profiles': utils.people_recently_created()}

@allow_http("GET")
@as_json
def projects_recently_created(request):
    return {'projects': utils.projects_recently_created()}

@allow_http("GET")
@as_json
def projects_recently_updated(request):
    return {'projects': utils.projects_recently_updated()}

def project_view(view):
    def inner(request, slug, *args, **kw):
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            return HttpResponseNotFound()
        try:
            member = project.get_membership(request.user)
        except ProjectMember.DoesNotExist:
            if project.policy == "closed":
                return HttpResponseForbidden()
            member = None
        request.project = project
        request.member = member
        return view(request, slug, *args, **kw)
    inner.__name__ = view.__name__
    return inner

@allow_http("GET")
@project_view
def projects_project(request, slug):
    url = request.project.homepage_url()
    url = '/'.join((url.rstrip("/"), request.project.homepage.lstrip("/"))
                   ).rstrip("/") + "/"
    return redirect(url)

@allow_http("GET")
@project_view
def projects_project_theme(request, slug):
    return theme(request)

@allow_http("GET")
@project_view
def projects_project_manage_team(request, slug):
    return theme(request)

@allow_http("GET")
@project_view
def projects_project_preferences(request, slug):
    return theme(request)

from libopencore.deliverance_middleware import CustomDeliveranceMiddleware

class UseProxy(Exception):
    def __init__(self, base_url, path_info):
        self.base_url = base_url
        self.path_info = path_info

@csrf_exempt
@project_view
def projects_project_dispatch(request, slug, path_info):
    for t in request.project.tools.all():
        t = t.get_tool()
        from django.core.urlresolvers import resolve, Resolver404
        if not hasattr(t, 'urlconf'):
            continue
        try:
            view = resolve('/%s' % path_info.lstrip('/'), t.urlconf)
        except Resolver404:
            continue
        if not isinstance(view, Resolver404):
            return view[0](request)

    tool = request.project.dispatch(path_info)
    if tool is None:
        return HttpResponse("404") # @@todo

    data = tool.request_data(tool.path_info)

    return HttpResponse(json.dumps({
                "base_url": data['url'],
                "script_name": tool.script_name,
                "path_info": tool.path_info,
                "deliverance_rules": data['deliverance_rules'],

                "theme": request.project.theme_url(),
                "project": request.project.to_json(),

                "user": request.user.username,
                "cookie_blacklist": [
                    "__ac",
                    settings.SESSION_COOKIE_NAME,
                    settings.CSRF_COOKIE_NAME,
                    ],
                }, default=dthandler), status=305)


from thing.models import ProjectInstalledTool
from thing.forms import ProjectToolForm
import requests
@allow_http("GET", "POST")
@project_view
@rendered_with("thing/projects/create_tool.html")
def projects_project_create_tool(request, slug):
    if request.method == "GET":
        form = ProjectToolForm()
        return {'form': form}

    form = ProjectToolForm(data=request.POST)
    if not form.is_valid():
        return {'form': form}

    member_permissions = set()
    other_permissions = set()
    for permission in form.PERMISSION_CHOICES[1:]:
        member_permissions.add(form.PERMISSION_MAP[permission[0]])
        if permission[0] == form.cleaned_data['member_level']:
            break
    for permission in form.PERMISSION_CHOICES[1:]:
        other_permissions.add(form.PERMISSION_MAP[permission[0]])
        if permission[0] == form.cleaned_data['other_level']:
            break

    project_parts = []
    i = 0
    while i <= len(request.project.slug):
        project_parts.append(request.project.slug[i:i+10])
        i += 10

    data = json.dumps({
            'roles': {
                'ProjectMember': list(member_permissions),
                'Authenticated': list(other_permissions),
                },
            'wiki': '/tmp/%s/%s/' % ('/'.join(project_parts), form.cleaned_data['slug']),
            })
    try:
        resp = requests.post('http://localhost:8080/_create/',
                             data=data, headers={'Content-Type': "application/json"})
    except Exception, e:
        return HttpResponse("didn't work: " + str(e))
    tool = ProjectInstalledTool(project=request.project, 
                                tool_dottedname='thing_gitwiki.tool.ToolProvider',
                                configuration=json.dumps(dict(slug=form.cleaned_data['slug'],
                                                              title=form.cleaned_data['name'])
                                                         ))
    tool.save()
    return redirect("..")

@allow_http("GET")
@project_view
@rendered_with("thing/projects/summary.html")
def projects_project_summary(request, slug):
    sources = request.project.feed_sources.all()
    
    source_data = [
        source.feed_source for source in sources
        if source.cache_expired()
        ]
    source_data = (grequests.get(u) for u in source_data)
    results = grequests.map(source_data)

    for source, result in zip(sources, results):
        source.bind_data(result.text)
        source.save()

    team = request.project.memberships.select_related(
        "user", "user__profile", "project").all()
    num_members = len(team)
    return {
        'project': request.project, 'sources': sources, 'request': request,
        'team': team, 'num_members': num_members,
        }

@csrf_exempt
@allow_http("GET", "POST")
@project_view
@rendered_with("thing/projects/members.xml", mimetype="application/xml")
def projects_project_members_xml(request, slug):
    members = ProjectMember.objects.select_related("user").filter(
        project=request.project)
    return {'members': members}

@csrf_exempt
@allow_http("GET", "POST")
@project_view
@rendered_with("thing/projects/info.xml", mimetype="application/xml")
def projects_project_info_xml(request, slug):
    return {'project': request.project}

@allow_http("GET")
@rendered_with("thing/projects/team.html")
@project_view
def projects_project_team(request, slug):
    members = ProjectMember.objects.select_related(
        "user", "user__profile", "project").filter(
        project=request.project).exclude(anonymous=True)
    sort_options = [
        {"value": "username", "title": _("sorted by user name"), 
         "selected": request.GET.get("sort_by") == "username"},
        {"value": "membership_date", "title": _("sorted by membership date"), 
         "selected": request.GET.get("sort_by") == "membership_date"},
        {"value": "location", "title": _("sorted by location"), 
         "selected": request.GET.get("sort_by") == "location"},
        ]
    ## @@TODO: clean this up
    if sort_options[0]['selected']:
        members = members.order_by("user__username")
    elif sort_options[1]['selected']:
        members = members.order_by("-created")
    elif sort_options[2]['selected']:
        members = members.order_by("user__profile__location")

    paginator = Paginator(members, 10)
    page = request.GET.get("page", 1)
    try:
        page = int(page)
        page = paginator.page(page)
    except (TypeError, ValueError, EmptyPage):
        # @@TODO: utility function
        resp = redirect(".") 
        qs = request.GET.copy()
        qs['page'] = 1
        resp['Location'] += "?" + qs.urlencode()
        return resp

    return {'members': [unicode(member) for member in members],
            'num_members': len(members),
            'sort_options': sort_options,
            'page_start': page.start_index(),
            'page_end': page.end_index(),
            'page': page,
            }

@allow_http("GET")
@as_json
def people_person(request, username):
    profile = UserProfile.objects.get(user__username=username)
    return {'profile': profile.to_json(include_projects=True)}
