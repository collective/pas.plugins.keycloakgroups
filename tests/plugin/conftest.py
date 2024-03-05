from plone import api
from zope.component.hooks import setSite

import pytest


@pytest.fixture()
def portal(integration, keycloak, keycloak_api):
    portal = integration["portal"]
    setSite(portal)
    with api.env.adopt_roles(["Manager", "Member"]):
        for key, value in keycloak_api.items():
            name = f"keycloak_groups.{key}"
            api.portal.set_registry_record(name, value)
    return portal
