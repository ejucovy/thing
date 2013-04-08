from django.conf import settings

from thing_sympa.models import ProjectSympaTool

class ToolProvider(object):

    _SYMPA_BASE_URL = settings.THING_SYMPA_BASE_URL
    _DELIVERANCE_RULES = """
<ruleset>
  <rule class="default">
    <drop content="div#Menus .MenuBlock:first-child" />
    <replace theme="children://div[@id='oc-content-container']"
             content="div#Menus" collapse-sources="1" />
    <append theme="children://div[@id='oc-content-container']"
             content="//div[@id='Stretcher']"
             collapse-sources="1"
             />
  </rule>

</ruleset>
"""

    def __init__(self, project_tool):
        self._project = project = project_tool.project
        self._lists = list(ProjectSympaTool.objects.filter(project=project))
        self.urlconf = 'thing_sympa.urls'

    def nav_entries(self):
        entries = [(self._project.homepage_url() + "sympa/", "Sympa Lists")]
        for list in self._lists:
            entries.append((self._project.homepage_url() + "sympa/%s/arc/%s/" % (
                        list.list_path, list.list_path),
                            list.list_name))
        return entries

    def nav_management_entries(self):
        return [(self._project.homepage_url() + 'sympa/settings/',
                 "Sympa Lists")]
    
    def proxy_paths(self):
        return ['/sympa/%s' % list.list_path for list in self._lists]

    def consume_request(self, script_name, matched_prefix, path_info):
        assert matched_prefix.startswith("sympa/")
        self.script_name = script_name + matched_prefix
        self.path_info = path_info

    def request_data(self, path_info):
        return {'url': self._SYMPA_BASE_URL,
                'deliverance_rules': self._DELIVERANCE_RULES}


