from AccessControl import ClassSecurityInfo
from pas.plugins.keycloakgroups import logger
from Products.PlonePAS.plugins.group import PloneGroup
from typing import Union


_ATTRS_NOT_WRAPPED = [
    "id",
    "_members",
    "_roles",
]


class KeycloakGroup(PloneGroup):
    security = ClassSecurityInfo()

    @security.public
    def addMember(self, id: str) -> None:
        logger.info(f"{self._id} does not support user assignment")

    @security.public
    def removeMember(self, id: str) -> None:
        logger.info(f"{self._id} does not support user removal")


MaybeKeycloakGroup = Union[KeycloakGroup, None]


def wrap_group(group_info: dict) -> MaybeKeycloakGroup:
    """Given a dictionary with group information, return a KeycloakGroup."""
    group = KeycloakGroup(group_info["id"], group_info["title"])
    # Add title, description properties to the group object
    data = {k: v for k, v in group_info.items() if k not in _ATTRS_NOT_WRAPPED}
    group.addPropertysheet("temp", data)
    return group
