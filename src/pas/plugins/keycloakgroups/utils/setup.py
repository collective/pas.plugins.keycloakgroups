from pas.plugins.keycloakgroups import logger
from pas.plugins.keycloakgroups import PLUGIN_ID
from pas.plugins.keycloakgroups.plugins import KeycloakGroupsPlugin
from plone import api
from Products.PluggableAuthService.PluggableAuthService import PluggableAuthService
from typing import List
from typing import Type
from typing import Union


PLUGIN_GROUP = (
    KeycloakGroupsPlugin,
    PLUGIN_ID,
    "Keycloak Groups",
    [
        "IGroupsPlugin",
        "IGroupIntrospection",
        "IGroupEnumerationPlugin",
        "IRolesPlugin",
    ],
)


PLUGINS = [PLUGIN_GROUP]


def get_plugin(plugin_id: str, klass: Type) -> Union[KeycloakGroupsPlugin]:
    """Check if plugin has the correct class."""
    pas = api.portal.get_tool("acl_users")
    plugin = getattr(pas, plugin_id, None)
    if not (plugin and isinstance(plugin, klass)):
        logger.warning(f"PAS plugin {plugin_id} is not a {klass.__name__}.")
        return None
    return plugin


def interfaces_for_plugin(pas: PluggableAuthService, plugin_id: str) -> List[str]:
    """Given a plugin, return a list of interface names."""
    plugin = getattr(pas, plugin_id, None)
    if not plugin:
        return []
    plugins = pas.plugins
    interfaces = []
    for info in plugins.listPluginTypeInfo():
        interface = info["interface"]
        interface_name = info["id"]
        if plugin.testImplements(interface):
            interfaces.append(interface_name)
    return interfaces


def activate_plugin(
    pas: PluggableAuthService,
    plugin_id: str,
    interface_name: str,
    move_to_top: bool = False,
):
    if plugin_id not in pas.objectIds():
        raise ValueError(f"acl_users has no plugin {plugin_id}.")

    # This would activate one interface and deactivate all others:
    # plugin.manage_activateInterfaces([interface_name])
    # So only take over the necessary code from manage_activateInterfaces.
    plugins = pas.plugins
    iface = plugins._getInterfaceFromName(interface_name)
    if plugin_id not in plugins.listPluginIds(iface):
        plugins.activatePlugin(iface, plugin_id)
        logger.info(f"Activated interface {interface_name} for plugin {plugin_id}")

    if move_to_top:
        # Order some plugins to make sure our plugin is at the top.
        # This is not needed for all plugin interfaces.
        plugins.movePluginsTop(iface, [plugin_id])
        logger.info(f"Moved {plugin_id} to top of {interface_name}.")


def deactivate_plugin(pas: PluggableAuthService, plugin_id: str, interface_name: str):
    if plugin_id in pas.objectIds():
        plugins = pas.plugins
        iface = plugins._getInterfaceFromName(interface_name)
        plugins.deactivatePlugin(iface, plugin_id)
        logger.info(f"Deactivated interface {interface_name} for plugin {plugin_id}")


def add_pas_plugin(
    klass: Type,
    plugin_id: str,
    title: str,
) -> Union[KeycloakGroupsPlugin]:
    """Add a new plugin to acl_users."""
    pas = api.portal.get_tool("acl_users")
    plugin = get_plugin(plugin_id, klass)
    if not plugin:
        plugin = klass(title=title)
        plugin.id = plugin_id
        pas._setObject(plugin_id, plugin)
        logger.info(f"Added {plugin_id} to acl_users.")

    return plugin


def remove_pas_plugin(klass: Type, plugin_id: str) -> bool:
    """Remove pas plugin from acl_users."""
    status = False
    pas = api.portal.get_tool("acl_users")
    # Remove plugin if it exists.
    plugin = get_plugin(plugin_id, klass)
    if plugin:
        pas._delObject(plugin_id)
        logger.info(f"Removed {klass.__name__} {plugin_id} from acl_users.")
        status = True
    return status
