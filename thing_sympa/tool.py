from django.conf import settings

from thing_sympa.models import ProjectSympaTool

class ToolProvider(object):

    _SYMPA_BASE_URL = settings.THING_SYMPA_BASE_URL
    _SYMPA_TOOL_PATH = 'lists'
    _DELIVERANCE_RULES = """
<ruleset>
  <rule class="default">
    <drop content="div#Menus .MenuBlock:first-child" />
    <drop content="div#Menus" />
    <replace theme="children://div[@id='oc-content-container']"
                   content="div#Menus" collapse-sources="1" />
    <append theme="children://div[@id='oc-content-container']"
             content="//div[@id='Stretcher']"
             collapse-sources="1"
             />
  </rule>

</ruleset>
"""

    def __init__(self, project):
        self._project = project
        try:
            self._tool = ProjectSympaTool.objects.get(project=project)
        except ProjectSympaTool.DoesNotExist:
            self._tool = None
        
    def nav_entries(self):
        if self._tool is None:
            return None
        return [(self._project.homepage_url()
                 + self._SYMPA_TOOL_PATH
                 + '/arc/%s' % self._tool.list_path,
                 self._tool.list_name)]

    def nav_management_entries(self):
        return None
    
    def match_request(self, path_info):
        if self._tool is None:
            return None
        path_info = path_info.lstrip("/").split("/")
        if path_info[0] == self._SYMPA_TOOL_PATH:
            return '/'.join(path_info[1:])

    def bind_request(self, path_info):
        self.script_name = self._project.homepage_url().rstrip("/") + "/%s/" % (
            self._SYMPA_TOOL_PATH)
        self.path_info = path_info
        self.url = self._SYMPA_BASE_URL
        self.deliverance_rules = self._DELIVERANCE_RULES
        return self

