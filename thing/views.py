import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from djangohelpers.lib import allow_http, rendered_with
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

@allow_http("GET")
def projects_create(request):
    return HttpResponse("OK")

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
@rendered_with("thing/projects/summary.html")
def projects_project_summary(request, slug):
    sources = request.project.feed_sources.all()
    return {'project': request.project, 'sources': sources, 'request': request}

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
@as_json
@project_view
def projects_project_team(request, slug):
    members = ProjectMember.objects.select_related("user").filter(
        project=request.project)
    return {'members': [unicode(member) for member in members]}

@allow_http("GET")
@as_json
def people_person(request, username):
    profile = UserProfile.objects.get(user__username=username)
    return {'profile': profile.to_json(include_projects=True)}
