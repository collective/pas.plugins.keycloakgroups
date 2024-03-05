from pas.plugins.keycloakgroups.plugins import KeycloakGroupsPlugin
from pas.plugins.keycloakgroups.utils import setup as utils
from plone import api

import pytest


class TestUtilsSetup:
    @pytest.fixture(autouse=True)
    def _initialize(self, portal, http_request):
        self.portal = portal
        self.http_request = http_request

    @pytest.mark.parametrize(
        "plugin_id,klass,expected",
        [
            [
                "groups_keycloak",
                KeycloakGroupsPlugin,
                KeycloakGroupsPlugin,
            ],
            [
                "oidc",
                KeycloakGroupsPlugin,
                None,
            ],
        ],
    )
    def test_get_plugin(self, plugin_id: str, klass, expected):
        func = utils.get_plugin
        result = func(plugin_id, klass)
        assert isinstance(result, expected) if expected else result is expected

    @pytest.mark.parametrize(
        "plugin_id,interfaces",
        [
            ["invalid_plugin", []],
            [
                "groups_keycloak",
                [
                    "IGroupEnumerationPlugin",
                    "IGroupIntrospection",
                    "IGroupsPlugin",
                    "IRolesPlugin",
                ],
            ],
        ],
    )
    def test_interfaces_for_plugin(self, plugin_id: str, interfaces: list):
        pas = api.portal.get_tool("acl_users")
        func = utils.interfaces_for_plugin
        results = func(pas, plugin_id)
        assert len(results) == len(interfaces)
        for name in interfaces:
            assert name in results

    @pytest.mark.parametrize(
        "plugin_id,interface,move_to_top",
        [
            ["groups_keycloak", "IGroupEnumerationPlugin", True],
            ["groups_keycloak", "IGroupIntrospection", True],
            ["groups_keycloak", "IGroupsPlugin", True],
            ["groups_keycloak", "IRolesPlugin", True],
        ],
    )
    def test_activate_plugin(self, plugin_id: str, interface: str, move_to_top: bool):
        pas = api.portal.get_tool("acl_users")
        func = utils.activate_plugin
        result = func(pas, plugin_id, interface, move_to_top)
        assert result is None

    @pytest.mark.parametrize(
        "plugin_id,interface,move_to_top",
        [
            ["invalid_plugin", "IGroupEnumerationPlugin", True],
        ],
    )
    def test_activate_plugin_error(
        self, plugin_id: str, interface: str, move_to_top: bool
    ):
        pas = api.portal.get_tool("acl_users")
        func = utils.activate_plugin
        with pytest.raises(ValueError) as exc:
            func(pas, plugin_id, interface, move_to_top)
        assert f"acl_users has no plugin {plugin_id}." in str(exc)

    @pytest.mark.parametrize(
        "plugin_id,interface",
        [
            ["groups_keycloak", "IGroupEnumerationPlugin"],
            ["groups_keycloak", "IGroupIntrospection"],
            ["groups_keycloak", "IGroupsPlugin"],
            ["groups_keycloak", "IRolesPlugin"],
        ],
    )
    def test_deactivate_plugin(self, plugin_id: str, interface: str):
        pas = api.portal.get_tool("acl_users")
        # First activate plugin
        utils.activate_plugin(pas, plugin_id, interface)
        # Now deactivate
        func = utils.deactivate_plugin
        result = func(pas, plugin_id, interface)
        assert result is None

    @pytest.mark.parametrize(
        "plugin_id,interface",
        [
            ["invalid_plugin", "IGroupEnumerationPlugin"],
        ],
    )
    def test_deactivate_plugin_error(self, plugin_id: str, interface: str):
        pas = api.portal.get_tool("acl_users")
        func = utils.activate_plugin
        with pytest.raises(ValueError) as exc:
            func(pas, plugin_id, interface)
        assert f"acl_users has no plugin {plugin_id}." in str(exc)
