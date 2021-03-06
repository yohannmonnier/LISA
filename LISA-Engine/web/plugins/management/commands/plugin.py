from django.core.management.base import BaseCommand, CommandError
from web.plugins.models import Plugin, Rule, Cron
from optparse import make_option
import os, json
import requests
try:
    from web.lisa.settings import LISA_PATH
except ImportError:
    from lisa.settings import LISA_PATH


class Command(BaseCommand):
    def __init__(self):
        super(Command, self).__init__()
        self.args = '<plugin_name>'
        self.help = 'Manage the plugins'

        self.plugins = []
        self.pluginPath = LISA_PATH + '/Plugins/'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.option_list = BaseCommand.option_list + (
            make_option('--list',
                action = 'store_true',
                help = 'List all plugins and show their status'),
            make_option('--create',
                action = 'store_true',
                help = 'Create a template plugin with a given name'),
            make_option('--enable',
                action = 'store_true',
                help = 'Enable a plugin'),
            make_option('--disable',
                action = 'store_true',
                help = 'Disable a plugin'),
            make_option('--install',
                action = 'store_true',
                help = 'Install a plugin'),
            make_option('--uninstall',
                action = 'store_true',
                help = 'Uninstall a plugin'),
            make_option('--upgrade',
                action = 'store_true',
                help = 'Upgrade a plugin'),
        )

    def handle(self, *args, **options):
        if args:
            self.arg_pluginName = args[0]
        if options.get('list'):
            self.list()

    def list(self):
        pluginLocalList = os.listdir(self.pluginPath)
        metareq = requests.get('https://raw.github.com/Seraf/LISA-Plugins/master/plugin_list.json')
        if(metareq.ok):
            for item in json.loads(metareq.text or metareq.content):
                pluginDB = Plugin.objects(name=item['name'])
                if pluginDB:
                    for plugin in pluginDB:
                        self.plugins.append({"name": item['name'], "installed": True, "enabled": plugin['enabled']})
                        if item['name'] in pluginLocalList:
                            pluginLocalList.remove(item['name'])
                else:
                    self.plugins.append({"name": item['name'], "installed": False, "enabled": False})
                    if item['name'] in pluginLocalList:
                        pluginLocalList.remove(item['name'])
        else:
            self.stdout.write(self.FAIL + "The plugin list on github seems to no be available" + self.ENDC)
        for pluginName in pluginLocalList:
            if os.path.isdir(os.path.join(self.pluginPath, pluginName)):
                pluginDB = Plugin.objects(name=pluginName)
                if pluginDB:
                    for plugin in pluginDB:
                        self.plugins.append({"name": plugin['name'], "installed": True, "enabled": plugin['enabled']})
                        if plugin['name'] in pluginLocalList:
                            pluginLocalList.remove(plugin['name'])
                else:
                    self.plugins.append({"name": pluginName, "installed": False, "enabled": False})
        for pluginDict in self.plugins:
            if pluginDict['installed']:
                installed = "["+ self.OKGREEN + "Installed" + self.ENDC + "]"
            else:
                installed = "["+ self.FAIL + "Not installed" + self.ENDC + "]"
            if pluginDict['enabled']:
                enabled = "["+ self.OKGREEN + "Enabled" + self.ENDC + "]"
            else:
                enabled = "["+ self.FAIL + "Not enabled" + self.ENDC + "]"

            self.stdout.write("%s => %s %s" % (pluginDict['name'], installed, enabled))