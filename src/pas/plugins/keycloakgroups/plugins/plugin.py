from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from keycloak import KeycloakAdmin
from pas.plugins.keycloakgroups import logger
from pas.plugins.keycloakgroups.plugins import group
from pas.plugins.keycloakgroups.plugins import utils
from plone.memoize.ram import cache
from Products.PlonePAS.interfaces.group import IGroupIntrospection
from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.permissions import ManageGroups
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from typing import List
from typing import Optional
from typing import Tuple
from zope.interface import implementer
from zope.interface import Interface


class IKeycloakGroupsPlugin(Interface):
    """Interface for PAS plugin for using groups in Keycloak"""


@implementer(IKeycloakGroupsPlugin)
class KeycloakGroupsPlugin(BasePlugin):
    """PAS Plugin Providing Group information from Keycloak."""

    meta_type = "Keycloak Groups Plugin"
    security = ClassSecurityInfo()

    @property
    @cache(utils._cache_5_minutes)
    def _available_roles(self) -> List[str]:
        """Return available roles in Portal."""
        return utils.list_available_roles()

    @property
    def _keycloak_client(self) -> KeycloakAdmin:
        """Return an instance of KeycloakAdmin."""
        return utils.get_keycloak_client()

    @security.private
    def is_plugin_active(self, iface) -> bool:
        """Check if Plugin is active for given interface."""
        if not utils.is_plugin_enabled():
            logger.info(f"Group Plugin ({self.getId()}): Plugin is not active.")
            return False
        pas = self._getPAS()
        ids = pas.plugins.listPluginIds(iface)
        return self.getId() in ids

    @property
    @cache(utils._cache_5_minutes)
    def _keycloak_groups(self) -> dict:
        """Return a dictionary with all keycloak groups.

        This will be cached in memory for 5 minutes.
        """
        plugin_id = self.getId()
        client = self._keycloak_client
        allowed_roles = self._available_roles
        logger.info(f"Group Plugin ({plugin_id}): Get all Keycloak groups")
        return utils.get_all_keycloak_groups(plugin_id, client, allowed_roles)

    @cache(utils._cache_principal_info)
    def _keycloak_groups_for_principal(self, principal_id: str) -> Tuple[str]:
        """Return a tuple with all group ids for a given principal.

        This will be cached in memory for 5 minutes (for each principal).
        """
        client = self._keycloak_client
        logger.info(
            f"Group Plugin ({self.getId()}): Get all Keycloak groups for principal {principal_id}"
        )
        return utils.get_groups_for_principal(client=client, principal_id=principal_id)

    @cache(utils._cache_group_info)
    def _keycloak_group_members(self, group_id: str) -> Tuple[str]:
        client = self._keycloak_client
        logger.info(
            f"Group Plugin ({self.getId()}): Get all Keycloak members for group {group_id}"
        )
        return utils.get_group_members(client=client, group_id=group_id)

    @cache(utils._cache_group_info)
    def _get_group_info(self, group_id: str) -> dict:
        """Return group information, including members, for a given group_id."""
        default = {}
        group_info = self._keycloak_groups.get(group_id, default)
        if group_info:
            # Get Members
            group_info["_members"] = self._keycloak_group_members(group_id=group_id)
        return group_info

    def enumerateGroups(
        self,
        id=None,
        title=None,
        exact_match=False,
        sort_by=None,
        max_results=None,
        **kw,
    ):
        """Enumerate Groups.
        -> ( group_info_1, ... group_info_N )

        o Return mappings for groups matching the given criteria.

        o 'id' in combination with 'exact_match' true, will
          return at most one mapping per supplied ID ('id' and 'login'
          may be sequences).

        o If 'exact_match' is False, then 'id' may be treated by
          the plugin as "contains" searches (more complicated searches
          may be supported by some plugins using other keyword arguments).

        o If 'sort_by' is passed, the results will be sorted accordingly.
          known valid values are 'id' (some plugins may support others).

        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all groups satisfying the
          criteria.

        o Minimal keys in the returned mappings:

          'id' -- (required) the group ID

          'pluginid' -- (required) the plugin ID (as returned by getId())

          'properties_url' -- (optional) the URL to a page for updating the
                              group's properties.

          'members_url' -- (optional) the URL to a page for updating the
                           principals who belong to the group.

        o Plugin *must* ignore unknown criteria.

        o Plugin may raise ValueError for invalid criteria.

        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """
        default = ()
        if not self.is_plugin_active(plugins.IGroupEnumerationPlugin):
            return default
        groups = self._keycloak_groups
        if not groups:
            return default
        matches = []
        key = None
        if id or title:
            key = "id" if id else "title"
            value = id if id else title
        if key:
            matches = (
                [g for g in groups.values() if g[key] == value]
                if exact_match
                else [g for g in groups.values() if value in g[key]]
            )
        else:  # show all
            matches = list(groups.values())
        if sort_by == "id":
            matches = sorted(matches)
        ret = []
        for item in matches:
            ret.append(item)
        if max_results and len(ret) > max_results:
            ret = ret[:max_results]
        return tuple(ret)

    #
    #   IGroupsPlugin implementation
    #
    @security.private
    def getGroupsForPrincipal(self, principal, request=None) -> Tuple[str]:
        """See IGroupsPlugin."""
        if not self.is_plugin_active(plugins.IGroupsPlugin):
            return tuple()
        principal_id = principal.getId()
        return self._keycloak_groups_for_principal(principal_id=principal_id)

    #
    #   (notional)IZODBGroupManager interface
    #
    @security.protected(ManageGroups)
    def listGroupIds(self) -> Tuple[str]:
        """-> (group_id_1, ... group_id_n)"""
        if not self.is_plugin_active(plugins.IGroupsPlugin):
            return tuple()
        return tuple(group_id for group_id in self._keycloak_groups.keys())

    @security.protected(ManageGroups)
    def listGroupInfo(self) -> Tuple[dict]:
        """-> (dict, ...dict)

        o Return one mapping per group, with the following keys:

          - 'id'
        """
        if not self.is_plugin_active(plugins.IGroupsPlugin):
            return tuple()
        return tuple(group_info for group_info in self._keycloak_groups.values())

    @security.protected(ManageGroups)
    def getGroupInfo(self, group_id: str) -> Optional[dict]:
        """group_id -> dict"""
        if not self.is_plugin_active(plugins.IGroupsPlugin):
            return None
        return self._get_group_info(group_id=group_id)

    def getGroupById(self, group_id: str) -> group.MaybeKeycloakGroup:
        """Return the portal_groupdata object for a group corresponding to this id."""
        if not self.is_plugin_active(plugins.IGroupsPlugin):
            return None
        group_info = self.getGroupInfo(group_id)
        return group.wrap_group(group_info) if group_info else None

    def getGroups(self) -> List[group.KeycloakGroup]:
        """Return an iterator of the available groups."""
        if not self.is_plugin_active(plugins.IGroupsPlugin):
            return []
        return [self.getGroupById(group_id) for group_id in self.getGroupIds()]

    def getGroupIds(self) -> List[str]:
        """Return a list of the available groups."""
        if not self.is_plugin_active(plugins.IGroupsPlugin):
            return []
        return [group_id for group_id in self._keycloak_groups.keys()]

    def getGroupMembers(self, group_id: str) -> Tuple[str]:
        """Return the members of a group with the given group_id.

        We only care about groups defined in this plugin.
        """
        default = tuple()
        if (
            self.is_plugin_active(plugins.IGroupsPlugin)
            and group_id in self._keycloak_groups
        ):
            return self._keycloak_group_members(group_id=group_id)
        return default

    def _get_roles_for_group(self, group_id: str) -> list:
        """Return a list of roles for a given group."""
        group_info = self._get_group_info(group_id=group_id)
        return group_info.get("_roles", []) if group_info else []

    #
    #   IRolesPlugin implementation
    #
    @security.private
    def getRolesForPrincipal(self, principal, request=None) -> Tuple[str]:
        """Return roles for a given principal (See IRolesPlugin).

        We only care about principals(groups) defined in this plugin.
        """
        roles = []
        if self.is_plugin_active(plugins.IRolesPlugin):
            keycloak_groups_ids = [group_id for group_id in self._keycloak_groups]
            principal_id = principal.getId()
            if principal_id in keycloak_groups_ids:
                # Direct roles
                roles.extend(self._get_roles_for_group(principal_id))
            # Inherited roles
            all_group_ids = (
                principal.getGroupIds() if hasattr(principal, "getGroupIds") else []
            )
            our_group_ids = [gid for gid in all_group_ids if gid in keycloak_groups_ids]
            for group_id in our_group_ids:
                roles.extend(self._get_roles_for_group(group_id))
        return tuple(roles)


InitializeClass(KeycloakGroupsPlugin)


classImplements(
    KeycloakGroupsPlugin,
    IKeycloakGroupsPlugin,
    IGroupIntrospection,
    plugins.IGroupsPlugin,
    plugins.IGroupEnumerationPlugin,
    plugins.IRolesPlugin,
)
