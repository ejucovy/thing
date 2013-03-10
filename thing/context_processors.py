from django.conf import settings
from thing.models import ProjectMember, UserProfile, Project

def thing_chrome(request):
    chrome = {
        'request': request,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'SITE_BIRTHDATE': settings.SITE_BIRTHDATE,
        'NUM_PEOPLE': UserProfile.objects.all().count(),
        'NUM_PROJECTS': Project.objects.all().count(),
        }
    if request.user.is_authenticated():
        chrome.update({
                'num_user_updates': 0,
                'user_projects': [membership.project for membership in
                                  ProjectMember.objects.select_related("project").filter(
                        user=request.user).order_by("project__name")],
                })
    if hasattr(request, 'project'):
        chrome['project'] = request.project
    return chrome
