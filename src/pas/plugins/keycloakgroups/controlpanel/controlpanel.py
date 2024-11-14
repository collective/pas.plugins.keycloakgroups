from pas.plugins.keycloakgroups import _
from pas.plugins.keycloakgroups.interfaces import IBrowserLayer
from pas.plugins.keycloakgroups.interfaces import IKeycloakSettings
from plone.app.registry.browser import controlpanel
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface


class KeycloakGroupsSettingsForm(controlpanel.RegistryEditForm):
    schema = IKeycloakSettings
    schema_prefix = "keycloak_groups"
    label = _("Keycloak Groups Plugin Settings")
    description = ""


class KeycloakGroupsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = KeycloakGroupsSettingsForm


@adapter(Interface, IBrowserLayer)
class KeycloakGroupsSettingsConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = IKeycloakSettings
    configlet_id = "keycloak_groups"
    configlet_category_id = "plone-users"
    title = _("Keycloak Groups settings")
    group = ""
    schema_prefix = "keycloak_groups"
