from pas.plugins.keycloakgroups.utils import setup
from Products.CMFPlone.interfaces import INonInstallable
from Products.GenericSetup.tool import SetupTool
from typing import List
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self) -> List[str]:
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "pas.plugins.keycloakgroups:uninstall",
        ]


def post_install(setup_tool: SetupTool):
    """Post install script"""
    for klass, plugin_id, title, *_ in setup.PLUGINS:
        setup.add_pas_plugin(klass, plugin_id, title)


def uninstall(setup_tool: SetupTool):
    """Uninstall script"""
    for klass, plugin_id, *_ in setup.PLUGINS:
        setup.remove_pas_plugin(klass, plugin_id)
