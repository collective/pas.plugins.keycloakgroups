from pas.plugins.keycloakgroups import PACKAGE_NAME
from pas.plugins.keycloakgroups import PLUGIN_ID
from pas.plugins.keycloakgroups import plugins
from plone import api

import pytest


class TestSetupInstall:

    @pytest.fixture(autouse=True)
    def _initialize(self, portal):
        self.portal = portal

    def test_addon_installed(self, installer):
        """Test if pas.plugins.keycloakgroups is installed."""
        assert installer.is_product_installed(PACKAGE_NAME) is True

    def test_browserlayer(self, browser_layers):
        """Test that IBrowserLayer is registered."""
        from pas.plugins.keycloakgroups.interfaces import IBrowserLayer

        assert IBrowserLayer in browser_layers

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(f"{PACKAGE_NAME}:default") == "1000"

    @pytest.mark.parametrize(
        "plugin_id",
        [
            PLUGIN_ID,
        ],
    )
    def test_plugin_added(self, plugin_id):
        """Test if plugin is added to acl_users."""
        pas = api.portal.get_tool("acl_users")
        assert plugin_id in pas.objectIds()

    @pytest.mark.parametrize(
        "plugin_id,klass",
        [
            (PLUGIN_ID, plugins.KeycloakGroupsPlugin),
        ],
    )
    def test_plugin_is_correct(self, plugin_id, klass):
        """Test if we have the correct plugin."""
        pas = api.portal.get_tool("acl_users")
        plugin = getattr(pas, plugin_id)
        assert isinstance(plugin, klass)

    @pytest.mark.parametrize("configlet_id", ["keycloak_groups"])
    def test_controlpanel_installed(self, configlet_id):
        """Test if we registered the control panel."""
        control_panels = api.portal.get_tool("portal_controlpanel")
        actions_ids = [configlet.id for configlet in control_panels.listActions()]
        assert configlet_id in actions_ids
