from django.conf import settings
import json

class ToolProvider(object):

    _BASE_URL = "http://localhost:8080"
    _DELIVERANCE_RULES = """
<ruleset>
  <rule class="default">
    <drop content="div#Menus .MenuBlock:first-child" />
    <replace theme="children://div[@id='oc-content-container']"
             content="children://body" />
  </rule>

</ruleset>
"""

    def __init__(self, project_tool):
        self._project = project = project_tool.project
        self.urlconf = 'thing_sympa.urls'
        self.config = json.loads(project_tool.configuration)

    def nav_entries(self):
        entries = [(self._project.homepage_url() + "wikis/%s/" % self.config['slug'],
                    self.config['title'])]
        return entries

    def nav_management_entries(self):
        return []
    
    def proxy_paths(self):
        return ['/wikis/%s' % self.config['slug']]

    def consume_request(self, script_name, matched_prefix, path_info):
        assert matched_prefix.startswith("wikis/")
        self.script_name = script_name + matched_prefix
        self.path_info = path_info

    def request_data(self, path_info):
        return {'url': self._BASE_URL,
                'deliverance_rules': self._DELIVERANCE_RULES}


