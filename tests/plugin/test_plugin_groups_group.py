from pas.plugins.keycloakgroups.plugins import group as keycloak_group
from plone import api

import logging
import pytest


class TestGroupsPluginOidcGroup:
    @pytest.fixture(autouse=True)
    def _initialize(self, portal):
        self.pas = portal.acl_users
        self.group_id = "5d5116a4-e6a0-4ec5-aa6e-84d038c8ac18"
        self.group = api.group.get(groupname=self.group_id).getGroup()

    def test_instance(self):
        group_data = api.group.get(groupname=self.group_id)
        group = group_data.getGroup()
        assert isinstance(group, keycloak_group.KeycloakGroup)

    def test_addMember(self, caplog):
        group = self.group
        with caplog.at_level(logging.INFO):
            group.addMember("new-user")
        assert f"{self.group_id} does not support user assignment" in caplog.text

    def test_removeMember(self, caplog):
        group = self.group
        with caplog.at_level(logging.INFO):
            group.removeMember("new-user")
        assert f"{self.group_id} does not support user removal" in caplog.text
