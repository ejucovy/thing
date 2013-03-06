from thing.models import Project, UserProfile, ProjectMember
from django.db import models

def recent_news_items():
    """
    {% blocktrans with user_link=feed_entry.author_html entry_date=feed_entry.created %}by {{ user_link }}, {{ entry_date }}{% endblocktrans %}
    """
    return []

def people_recently_created():
    profiles = UserProfile.objects.select_related("user").order_by("-created")[:5]
    profiles = [profile.to_json() for profile in profiles]
    return profiles

def projects_recently_created():
    projects = Project.objects.all().exclude(policy="closed").order_by("-created")[:5]
    projects = [project.to_json(include_members=False) for project in projects]
    return projects

def projects_recently_updated(limit=5, exclude=None):
    projects = Project.objects.all().exclude(policy="closed")
    if exclude is not None:
        projects = projects.exclude(slug__in=exclude)
    projects = projects.order_by("-updated").annotate(
        num_members=models.Count('memberships'))[:limit]
    projects = [project.to_json(include_members=True) for project in projects]
    return projects

class FeedEntry(object):
    def __init__(self, url, title, content, 
                 item_data=None,
                 image_url=None, image_class=None):
        self.get_absolute_url = url
        self.title = title

        if item_data is not None and not isinstance(item_data, list):
            raise TypeError("item_data must be a list, got %s" % item_data)
        self.item_data = item_data or []

        self.content = content

        self.image_prefix = None
        if image_url is not None:
            self.image_prefix = {
                'html_class': image_class or '',
                'image_url': image_url,
                }
