import pytest


@pytest.fixture()
def user_information():
    def func(session_factory, user) -> dict:
        user_id = user["id"]
        username = user["username"]
        password = user["password"]
        session = session_factory(username, password)
        response = session.get(f"/@users/{user_id}").json()
        return response

    return func


class TestAuthenticationGroups:

    @pytest.fixture(autouse=True)
    def _initialize(self, api_authenticated_session_factory):
        self.api_session_factory = api_authenticated_session_factory

    @pytest.mark.parametrize(
        "group_id,expected",
        [
            ["AuthenticatedUsers", True],
            ["d04a8479-e830-47ab-a2be-9271bcb32f69", True],
            ["5d5116a4-e6a0-4ec5-aa6e-84d038c8ac18", False],
        ],
    )
    def test_user_editor_groups(
        self, user_editor, user_information, group_id: str, expected: bool
    ):
        response = user_information(self.api_session_factory, user_editor)
        group_ids = [i["id"] for i in response["groups"]["items"]]
        assert (group_id in group_ids) is expected

    @pytest.mark.parametrize(
        "group_id,expected",
        [
            ["AuthenticatedUsers", True],
            ["d04a8479-e830-47ab-a2be-9271bcb32f69", False],
            ["5d5116a4-e6a0-4ec5-aa6e-84d038c8ac18", True],
        ],
    )
    def test_user_member_groups(
        self, user_member, user_information, group_id: str, expected: bool
    ):
        response = user_information(self.api_session_factory, user_member)
        group_ids = [i["id"] for i in response["groups"]["items"]]
        assert (group_id in group_ids) is expected


class TestAuthenticationRoles:

    @pytest.fixture(autouse=True)
    def _initialize(self, api_authenticated_session_factory):
        self.api_session_factory = api_authenticated_session_factory

    @pytest.mark.parametrize(
        "role,expected",
        [
            ["Editor", True],
            ["Manager", True],
            ["Member", True],
        ],
    )
    def test_user_editor_roles(
        self, user_editor, user_information, role: str, expected: bool
    ):
        """Authenticate editor user, check if roles are applied."""
        response = user_information(self.api_session_factory, user_editor)
        roles = response["roles"]
        assert (role in roles) is expected

    @pytest.mark.parametrize(
        "role,expected",
        [
            ["Editor", False],
            ["Manager", False],
            ["Member", True],
        ],
    )
    def test_user_member_roles(
        self, user_member, user_information, role: str, expected: bool
    ):
        """Authenticate test user, check if roles are applied."""
        response = user_information(self.api_session_factory, user_member)
        roles = response["roles"]
        assert (role in roles) is expected
