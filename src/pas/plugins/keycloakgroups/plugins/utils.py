from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from keycloak.exceptions import KeycloakGetError
from pas.plugins.keycloakgroups import logger
from plone import api
from time import time
from typing import Any
from typing import List
from typing import Tuple
from typing import Union


# Plone Registry
def _config(key: str) -> Any:
    """Get registry configuration for a given key."""
    name = f"keycloak_groups.{key}"
    return api.portal.get_registry_record(name=name)


def is_plugin_enabled() -> bool:
    """Check if plugin is enabled in the configuration registry."""
    return _config("enabled")


def _connection_settings() -> dict:
    return (
        {
            "server_url": _config("server_url"),
            "realm_name": _config("realm_name"),
            "client_id": _config("client_id"),
            "client_secret_key": _config("client_secret"),
            "verify": _config("verify"),
        }
        if is_plugin_enabled()
        else {}
    )


# Keycloak
def get_keycloak_client() -> Union[KeycloakAdmin | None]:
    """Return an instance of KeycloakAdmin."""
    settings = _connection_settings()
    if settings:
        keycloak_connection = KeycloakOpenIDConnection(**settings)
        keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
        return keycloak_admin


def _filter_group_roles(realm_roles: List[str], allowed_roles: List[str]) -> List[str]:
    """Filter group roles, coming from keycloak, and only keep the ones in the allowed_roles list."""
    return [r for r in realm_roles if r in allowed_roles]


def _keycloak_group_to_plone_group(group: dict, plugin_id: str) -> dict:
    """Convert a keycloak group information to the format used by PAS."""
    return {
        "id": group["id"],
        "title": group["name"],
        "description": group["path"],
        "pluginid": plugin_id,
        "groupid": group["id"],
        "principal_type": "group",
    }


def get_all_keycloak_groups(
    plugin_id: str, client: KeycloakAdmin, allowed_roles: List[str]
) -> dict:
    """Query keycloak for groups and return group information.

    This function:
    - Get all groups from keycloak realm
    - Convert keycloak group representation to PAS group representation
    - Filter group roles to match those available in the Plone site
    """
    groups = {}
    groups_info = client.get_groups({"briefRepresentation": False})
    for item in groups_info:
        # Transform keycloak group info into PAS group information
        group_info = _keycloak_group_to_plone_group(group=item, plugin_id=plugin_id)
        # Annotate roles
        realm_roles = item.get("realmRoles", [])
        group_info["_roles"] = _filter_group_roles(realm_roles, allowed_roles)
        # Add to dict with all groups
        groups[item["id"]] = group_info
    return groups


def get_groups_for_principal(client: KeycloakAdmin, principal_id: str) -> Tuple[str]:
    """Query keycloak for all group ids for a given principal."""
    try:
        groups = client.get_user_groups(user_id=principal_id)
    except KeycloakGetError as exc:
        logger.debug(f"Error {exc.response_code} looking groups for {principal_id}")
        return tuple()
    return tuple([x.get("id") for x in groups])


def get_group_members(client: KeycloakAdmin, group_id: str) -> Tuple[str]:
    """Query keycloak for all members for a given group_id."""
    try:
        members = client.get_group_members(group_id=group_id)
    except KeycloakGetError as exc:
        logger.debug(f"Error {exc.response_code} looking up members for {group_id}")
        members = []
    return tuple([member["id"] for member in members])


# Roles
def list_available_roles() -> List[str]:
    """Return available roles in Portal."""
    member_tool = api.portal.get_tool("portal_membership")
    return [r for r in member_tool.getPortalRoles() if r != "Owner"]


# Cache keys
def _cache_5_minutes(*args, **kwargs):
    """Cache key to keep information in cache for 5 minutes."""
    time_key = time() // (60 * 5)
    return time_key


def _cache_group_info(*args, **kwargs):
    """Cache key to keep Group information cached for 5 minutes."""
    time_key = time() // (60 * 5)
    principal_id = kwargs["group_id"]
    return f"{principal_id}-{time_key}"


def _cache_principal_info(*args, **kwargs):
    """Cache key to keep Principal information cached for 5 minutes."""
    time_key = time() // (60 * 5)
    principal_id = kwargs["principal_id"]
    return f"{principal_id}-{time_key}"
