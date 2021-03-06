from django.conf.urls import patterns, include, url
from tastypie.api import Api
from plugins.api import PluginResource
from interface.api import WidgetResource, WorkspaceResource, WidgetByUserResource
from api import LisaResource, UserResource
from twisted.python.reflect import namedAny
import tastypie_swagger

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(PluginResource())
v1_api.register(WorkspaceResource())
v1_api.register(WidgetResource())
v1_api.register(WidgetByUserResource())
v1_api.register(LisaResource())

from libs.Server import enabled_plugins
for plugin in enabled_plugins:
    try:
        metapluginResource = namedAny(plugin+'.web.api.'+plugin+'Resource')
        v1_api.register(metapluginResource())
    except:
        pass
urlpatterns = patterns('',
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/docs/', include('tastypie_swagger.urls', namespace='tastypie_swagger')),
    url(r'^speech/', include('googlespeech.urls')),
    url(r'^plugins/', include('plugins.urls')),
    url(r'', include('interface.urls')),
)
