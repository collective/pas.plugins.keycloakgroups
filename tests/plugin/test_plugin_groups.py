from pas.plugins.keycloakgroups import PLUGIN_ID
from plone import api

import pytest


class TestGroupsPlugin:
    @pytest.fixture(autouse=True)
    def _initialize(self, portal, http_request):
        self.pas = api.portal.get_tool("acl_users")
        self.plugin = getattr(self.pas, PLUGIN_ID)
        self.http_request = http_request
        self.http_response = http_request.response

    def test_plugin_instance(self):
        from pas.plugins.keycloakgroups.plugins import KeycloakGroupsPlugin

        assert isinstance(self.plugin, KeycloakGroupsPlugin)

    def test_plugin_enumerateGroups(self):
        groups = self.plugin.enumerateGroups()
        assert isinstance(groups, tuple)
        assert len(groups) == 3

    @pytest.mark.parametrize(
        "query,items",
        [
            ({}, 3),
            ({"id": "5d5116a4-e6a0-4ec5-aa6e-84d038c8ac18", "exact_match": True}, 1),
            ({"title": "Management", "exact_match": True}, 1),
        ],
    )
    def test_plugin_enumerateGroups_filter_id(self, query: dict, items: int):
        groups = self.plugin.enumerateGroups(**query)
        assert isinstance(groups, tuple)
        assert len(groups) == items

    @pytest.mark.parametrize(
        "group_id,title",
        [
            ("5d5116a4-e6a0-4ec5-aa6e-84d038c8ac18", "Developers"),
        ],
    )
    def test_plugin_getGroupInfo(self, group_id: str, title: str):
        group_info = self.plugin.getGroupInfo(group_id)
        assert isinstance(group_info, dict)
        assert group_info["title"] == title

    def test_plugin_getGroupIds(self):
        group_ids = self.plugin.getGroupIds()
        assert isinstance(group_ids, list)
        assert len(group_ids) == 3

    def test_plugin_listGroupIds(self):
        group_ids = self.plugin.listGroupIds()
        assert isinstance(group_ids, tuple)
        assert len(group_ids) == 3

    @pytest.mark.parametrize(
        "group_id,expected",
        [
            ("5d5116a4-e6a0-4ec5-aa6e-84d038c8ac18", ("Member",)),
            ("a266d9ab-f63c-4e12-8598-500bb4966e74", ("Member",)),
            ("d04a8479-e830-47ab-a2be-9271bcb32f69", ("Manager", "Editor", "Member")),
        ],
    )
    def test_plugin_getRolesForPrincipal(self, group_id, expected):
        group = api.group.get(groupname=group_id)
        roles = self.plugin.getRolesForPrincipal(group)
        assert len(roles) == len(expected)
        assert roles == expected
