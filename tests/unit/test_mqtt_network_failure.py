"""Network outages must not abort the device polling loop."""
import errno
import socket
from unittest.mock import patch

import pytest

from powermon.mqttbroker import MqttBroker


@pytest.mark.parametrize("failure", [
    socket.gaierror(socket.EAI_AGAIN, "Temporary failure in name resolution"),
    OSError(errno.ENETUNREACH, "Network is unreachable"),
    TimeoutError("connection timed out"),
    ConnectionRefusedError(errno.ECONNREFUSED, "Connection refused"),
])
def test_publish_can_retry_after_network_failure(failure):
    broker = MqttBroker("broker.local", 1883)
    # Exercise the real Paho connection path, failing only at the socket boundary.
    with patch("socket.create_connection", side_effect=failure), \
            patch("powermon.mqttbroker.mqttbroker.sleep"):
        broker.publish("battery/voltage", "13.2")
    assert not broker.is_connected

    # The next reading should still attempt to connect and publish.
    def connected(*args, **kwargs):
        broker.on_connect(broker.mqttc, None, {}, 0)

    with patch.object(broker.mqttc, "connect", side_effect=connected) as connect, \
            patch.object(broker.mqttc, "loop_start"), \
            patch.object(broker.mqttc, "publish") as publish, \
            patch("powermon.mqttbroker.mqttbroker.sleep"):
        broker.publish("battery/voltage", "13.3")
        connect.assert_called_once()
        publish.assert_called_once_with("battery/voltage", "13.3")
        publish.return_value.wait_for_publish.assert_called_once_with(5)


def test_invalid_connection_configuration_still_raises():
    broker = MqttBroker("broker.local", -1)
    with pytest.raises(ValueError):
        broker.connect()
