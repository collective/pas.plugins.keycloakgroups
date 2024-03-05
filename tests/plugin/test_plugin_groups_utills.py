from pas.plugins.keycloakgroups import PLUGIN_ID
from pas.plugins.keycloakgroups.plugins import utils

import logging
import pytest


class TestGroupsPluginUtils:
    @pytest.fixture(autouse=True)
    def _initialize(self, portal):
        self.pas = portal.acl_users
        self.plugin = getattr(self.pas, PLUGIN_ID)
        self.plugin_id = self.plugin.getId()
        self.client = utils.get_keycloak_client()
        self.allowed_roles = utils.list_available_roles()

    def test__config(self):
        func = utils._config
        assert func("enabled") is True

    def test_is_plugin_enabled(self):
        func = utils.is_plugin_enabled
        assert func() is True

    @pytest.mark.parametrize(
        "key,expected",
        [
            ["realm_name", "plone-test"],
            ["client_id", "plone-admin"],
            ["client_secret_key", "12345678"],  # nosec B105
        ],
    )
    def test__connection_settings(self, key, expected):
        func = utils._connection_settings
        result = func()
        assert isinstance(result, dict)
        assert result[key] == expected

    @pytest.mark.parametrize(
        "role",
        [
            "Manager",
            "Site Administrator",
            "Editor",
            "Contributor",
            "Reviewer",
        ],
    )
    def test_list_available_roles(self, role):
        result = utils.list_available_roles()
        assert role in result

    def test_get_keycloak_client(self):
        from keycloak import KeycloakAdmin

        func = utils.get_keycloak_client
        result = func()
        assert isinstance(result, KeycloakAdmin)

    def test_get_all_keycloak_groups(self):
        func = utils.get_all_keycloak_groups
        result = func(
            plugin_id=self.plugin_id,
            client=self.client,
            allowed_roles=self.allowed_roles,
        )
        assert isinstance(result, dict)

    def test_get_groups_for_principal_success(self):
        func = utils.get_groups_for_principal
        result = func(self.client, principal_id="adf05305-9b27-4fad-b633-23d21ef32431")
        assert isinstance(result, tuple)
        assert len(result) == 1

    def test_get_groups_for_principal_fail(self, caplog):
        func = utils.get_groups_for_principal
        with caplog.at_level(logging.DEBUG):
            result = func(self.client, principal_id="bad-id")
            assert isinstance(result, tuple)
            assert len(result) == 0
        assert "Error 404 looking groups for bad-id" in caplog.text

    def test_get_group_members_success(self):
        func = utils.get_group_members
        result = func(self.client, group_id="5d5116a4-e6a0-4ec5-aa6e-84d038c8ac18")
        assert isinstance(result, tuple)
        assert len(result) == 1

    def test_get_group_members_fail(self, caplog):
        func = utils.get_group_members
        with caplog.at_level(logging.DEBUG):
            result = func(self.client, group_id="bad-id")
            assert isinstance(result, tuple)
            assert len(result) == 0
        assert "Error 404 looking up members for bad-id" in caplog.text
