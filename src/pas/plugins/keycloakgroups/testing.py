from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing.zope import WSGI_SERVER_FIXTURE

import pas.plugins.keycloakgroups  # noQA


class Layer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import pas.plugins.oidc
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=pas.plugins.oidc)
        self.loadZCML(package=pas.plugins.keycloakgroups)

    def setUpPloneSite(self, portal):
        # Install plone.restapi
        applyProfile(portal, "plone.restapi:default")
        # Install pas.plugins.oidc
        applyProfile(portal, "pas.plugins.oidc:default")
        applyProfile(portal, "pas.plugins.keycloakgroups:default")


FIXTURE = Layer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="pas.plugins.keycloakgroupsLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="pas.plugins.keycloakgroupsLayer:FunctionalTesting",
)

RESTAPI_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="pas.plugins.keycloakgroupsLayer:RestAPITesting",
)
