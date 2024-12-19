import pytest

from bumper.utils import db


@pytest.mark.usefixtures("clean_database")
def test_client_db() -> None:
    db.client_add("user_123", "realm_123", "resource_123")
    assert db.client_get("resource_123")  # Test client was added

    db.client_set_mqtt("resource_123", True)
    assert db.client_get("resource_123").get("mqtt_connection")  # Test that mqtt was set True for client

    db.client_set_xmpp("resource_123", False)
    assert db.client_get("resource_123").get("xmpp_connection") is False  # Test that xmpp was set False for client
    assert len(db.get_disconnected_xmpp_clients()) > 0  # Test len of connected xmpp clients is 1

    db.client_reset_connection_status()
    assert db.client_get("resource_123").get("mqtt_connection") is False  # Test that mqtt was reset False for client
    assert db.client_get("resource_123").get("xmpp_connection") is False  # Test that xmpp was reset False for client

    db.client_remove("resource_123")
    assert db.client_get("resource_123") is None


@pytest.mark.usefixtures("clean_database")
def test_client_add_no_existing() -> None:
    # Add a new client
    db.client_add("user_456", "realm_456", "resource_456")

    # Verify that the new client was added successfully
    assert db.client_get("resource_456") is not None


@pytest.mark.usefixtures("clean_database")
def test_client_add_existing() -> None:
    # Add an initial client
    db.client_add("user_789", "realm_789", "resource_789")

    # Try to add a new client with the same resource
    db.client_add("user_789", "realm_789", "resource_789")

    # Verify that the existing client is not overwritten
    client = db.client_get("resource_789")
    assert client is not None
    assert client.get("userid") == "user_789"


@pytest.mark.usefixtures("clean_database")
def test_client_remove() -> None:
    # Add a client
    db.client_add("user_remove", "realm_remove", "resource_remove")

    # Remove the added client
    db.client_remove("resource_remove")

    # Verify that the client was removed
    assert db.client_get("resource_remove") is None


@pytest.mark.usefixtures("clean_database")
def test_client_set_status() -> None:
    # Add a client
    db.client_add("user_status", "realm_status", "resource_status")

    # Set MQTT and XMPP status for the client
    db.client_set_mqtt("resource_status", True)
    db.client_set_xmpp("resource_status", True)

    # Verify that the status was set correctly
    client = db.client_get("resource_status")
    assert client is not None
    assert client.get("mqtt_connection") is True
    assert client.get("xmpp_connection") is True


@pytest.mark.usefixtures("clean_database")
def test_client_reset_connection_status() -> None:
    # Add multiple clients
    db.client_add("user_reset_1", "realm_reset_1", "resource_reset_1")
    db.client_add("user_reset_2", "realm_reset_2", "resource_reset_2")

    # Set MQTT and XMPP status for the clients
    db.client_set_mqtt("resource_reset_1", True)
    db.client_set_xmpp("resource_reset_2", True)

    # Reset connection status for all clients
    db.client_reset_connection_status()

    # Verify that connection status was reset for all clients
    client_1 = db.client_get("resource_reset_1")
    client_2 = db.client_get("resource_reset_2")
    assert client_1.get("mqtt_connection") is False
    assert client_2.get("xmpp_connection") is False


@pytest.mark.usefixtures("clean_database")
def test_client_get_all() -> None:
    # Add multiple clients
    db.client_add("user_all_1", "realm_all_1", "resource_all_1")
    db.client_add("user_all_2", "realm_all_2", "resource_all_2")

    # Get all clients
    all_clients = db.client_get_all()

    # Verify that all clients were retrieved
    assert len(all_clients) == 2

    # Verify that each client has the expected resource
    resources = {client.get("resource") for client in all_clients}
    assert "resource_all_1" in resources
    assert "resource_all_2" in resources
