from pas.plugins.keycloakgroups.interfaces import IKeycloakSettings
from pas.plugins.keycloakgroups.utils import setup
from plone import api
from plone.registry.events import RecordModifiedEvent


def keycloak_settings_modified(_: IKeycloakSettings, event: RecordModifiedEvent):
    """A setting in the keycloak group was modified."""
    field_name = event.record.fieldName
    if field_name == "enabled":
        # Enable or Disable the plugin
        pas = api.portal.get_tool("acl_users")
        plugin_id = setup.PLUGIN_GROUP[1]
        plugin = getattr(pas, plugin_id, None)
        value = event.record.value
        if plugin:
            interfaces = setup.interfaces_for_plugin(pas, plugin_id)
            move_to_top = setup.PLUGIN_GROUP[-1]
            func = setup.activate_plugin if value else setup.deactivate_plugin
            for interface_name in interfaces:
                args = [pas, plugin_id, interface_name]
                if value:
                    args.append(interface_name in move_to_top)
                func(*args)
