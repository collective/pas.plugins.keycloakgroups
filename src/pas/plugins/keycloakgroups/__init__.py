"""Init and utils."""

from Products.PluggableAuthService import PluggableAuthService as PAS
from Products.PluggableAuthService.permissions import ManageGroups
from zope.i18nmessageid import MessageFactory

import logging


PACKAGE_NAME = "pas.plugins.keycloakgroups"
PLUGIN_ID = "groups_keycloak"

_ = MessageFactory(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)


def initialize(context):  # pragma: no cover
    """Initializer called when used as a Zope2 product."""
    from pas.plugins.keycloakgroups import plugins

    PAS.registerMultiPlugin(plugins.KeycloakGroupsPlugin.meta_type)
    context.registerClass(
        plugins.KeycloakGroupsPlugin,
        permission=ManageGroups,
        constructors=(plugins.add_keycloak_plugin,),
    )
