from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kabukit.sources.edinet.client import AuthKey, EdinetClient

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit


def test_set_api_key() -> None:
    client = EdinetClient("abc")
    assert client.client.params["Subscription-Key"] == "abc"


def test_set_api_key_none_and_no_config(mocker: MockerFixture) -> None:
    mock_get_config_value = mocker.patch(
        "kabukit.sources.edinet.client.get_config_value",
        return_value=None,
    )
    client = EdinetClient()
    assert "Subscription-Key" not in client.client.params
    mock_get_config_value.assert_called_once_with(AuthKey.API_KEY)


def test_set_api_key_directly(mocker: MockerFixture) -> None:
    mock_get_config_value = mocker.patch(
        "kabukit.sources.edinet.client.get_config_value",
        return_value="should_not_be_called",
    )
    client = EdinetClient("initial_key")
    client.set_api_key("new_key")
    assert client.client.params["Subscription-Key"] == "new_key"
    mock_get_config_value.assert_not_called()
