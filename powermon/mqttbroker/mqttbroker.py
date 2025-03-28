"""mqtt broker 

   - provides MqttBroker class

"""
import logging
from time import sleep
from typing import Self, Callable

import paho.mqtt.client as mqtt_client

from powermon.libs.config import safe_config

# Set-up logger
log = logging.getLogger("mqttbroker")


class MqttBroker:
    """MqttBroker class - wraps connecting, subscribing and publishing to a mqtt broker
    """
    def __str__(self):
        if self.disabled:
            return "MqttBroker DISABLED"
        else:
            return f"MqttBroker name: {self.name}, port: {self.port}, user: {self.username}"

    @classmethod
    def from_config(cls, config: dict=None) -> Self:
        """builds the mqtt broker object from a config dict

        Args:
            - config (dict, optional): Defaults to None which will disable class.
                - name: broker network name or ip address
                - port (optional): broker port. Defaults to 1883
                - username (optional): required if broker authentication wanted
                - password (optional): required if broker authentication wanted
                - adhoc_topic: (optional): topic to monitor for adhoc commands
                - adhoc_result_topic (optional): topic to publish adhoc command results

        Returns:
            Self: configured (or disabled if config is None) MqttBroker class
        """

        log.debug("mqttbroker config: %s", safe_config(config))

        if config:
            name = config.get("name")
            port = config.get("port", 1883)
            username = config.get("username")
            password = config.get("password")
            mqtt_broker = cls(name=name, port=port, username=username, password=password)
            mqtt_broker.adhoc_topic = config.get("adhoc_topic")
            mqtt_broker.adhoc_result_topic = config.get("adhoc_result_topic")
            return mqtt_broker
        else:
            return cls(name=None)

    def __init__(self, name, port=None, username=None, password=None):
        self.name = name
        self.port = port
        self.username = username
        self.password = password
        self.is_connected = False

        if self.name is None:
            self.disabled = True
        else:
            self.disabled = False
            self.mqttc = mqtt_client.Client()

    @property
    def adhoc_topic(self) -> str:
        """the topic to listen for any adhoc command"""
        return getattr(self, "_adhoc_topic", None)

    @adhoc_topic.setter
    def adhoc_topic(self, value):
        log.debug("setting adhoc topic to: %s", value)
        self._adhoc_topic = value

    @property
    def adhoc_result_topic(self) -> str:
        """the topic to publish adhoc results to"""
        return getattr(self, "_adhoc_result_topic", None)

    @adhoc_result_topic.setter
    def adhoc_result_topic(self, value):
        log.debug("setting adhoc result topic to: %s", value)
        self._adhoc_result_topic = value

    def on_connect(self, client, userdata, flags, rc):
        """callback for connect"""
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised
        # 6-255: Currently unused.
        log.debug("on_connect called - client: %s, userdata: %s, flags: %s", client, userdata, flags)
        connection_result = [
            "Connection successful",
            "Connection refused - incorrect protocol version",
            "Connection refused - invalid client identifier",
            "Connection refused - server unavailable",
            "Connection refused - bad username or password",
            "Connection refused - not authorised",
            "Connection failed"
        ]
        log.debug("MqttBroker connection returned result: %s %s", rc, connection_result[rc if rc <= 6 else 6])
        if rc == 0:
            self.is_connected = True
            return
        self.is_connected = False

    def on_disconnect(self, client, userdata, rc):
        """ callback for disconnect """
        log.debug("on_disconnect called - client: %s, userdata: %s, rc: %s", client, userdata, rc)
        self.is_connected = False

    def connect(self) -> None:
        """ connect to mqtt broker """
        if self.disabled:
            log.info("MQTT broker not enabled, was a broker name defined? '%s'", self.name)
            return
        if not self.name:
            log.info("MQTT could not connect as no broker name")
            return
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect
        # if name is screen just return without connecting
        if self.name == "screen":
            # allows checking of message formats
            return
        try:
            log.debug("Connecting to %s on port %s", self.name, self.port)
            if self.username:
                # auth = {"username": mqtt_user, "password": mqtt_pass}
                _password = "********" if self.password is not None else "None"
                log.info("Using mqtt authentication, username: %s, password: %s", self.username, _password)
                self.mqttc.username_pw_set(self.username, password=self.password)
            else:
                log.debug("No mqtt authentication used")
                # auth = None
            self.mqttc.connect(self.name, port=self.port, keepalive=60)
            self.mqttc.loop_start()
            sleep(1)
        except ConnectionRefusedError as ex:
            log.warning("%s refused connection with error: '%s'", self.name, ex)

    def start(self) -> None:
        """start the mqtt broker """
        if self.disabled:
            return
        if self.is_connected:
            self.mqttc.loop_start()

    def stop(self) -> None:
        """stop the mqtt broker"""
        log.debug("Stopping mqttbroker connection")
        if self.disabled:
            return
        self.mqttc.loop_stop()

    # def set(self, variable, value):
    #     setattr(self, variable, value)

    # def update(self, variable, value):
    #     # only override if value is not None
    #     if value is None:
    #         return
    #     setattr(self, variable, value)

    def subscribe(self, topic: str, callback: Callable) -> None:
        """subscribe to a topic on the mqtt broker

        Args:
            topic (str): topic to subscribe to
            callback (Callable): function to call when a message is received
        """
        if not self.name:
            return
        if self.disabled:
            return
        # check if connected, connect if not
        if not self.is_connected:
            log.debug("Not connected, connecting")
            self.connect()
        # Register callback
        self.mqttc.on_message = callback
        if self.is_connected:
            # Subscribe to command topic
            log.debug("Subscribing to topic: %s", topic)
            self.mqttc.subscribe(topic, qos=0)
        else:
            log.warning("Did not subscribe to topic: %s as not connected to broker", topic)

    def post_adhoc_command(self, command_code: str) -> None:
        """ shortcut function to publish an adhoc command """
        self.publish(topic=self.adhoc_topic, payload=command_code)

    def post_adhoc_result(self, payload: str) -> None:
        """ shortcut function to publish the results of an adhoc command """
        self.publish(topic=self.adhoc_result_topic, payload=payload)


    def publish(self, topic: str, payload: str) -> None:
        """ publish messages to the defined mqtt broker
            - if broker name is 'screen' will write to stdout instead

        Args:
            topic (str): topic to publish to.
            payload (str): content to publish.
        """
        if self.disabled:
            log.debug("Cannot publish msg as mqttbroker disabled")
            return
        # log.debug("Publishing '%s' to '%s'", payload, topic)
        if self.name == "screen":
            print(f"mqtt debug - topic: '{topic}', payload: '{payload}'")
            return
        # check if connected, connect if not
        if not self.is_connected:
            log.debug("Not connected, connecting")
            self.connect()
            sleep(1)
            if not self.is_connected:
                log.warning("mqtt broker did not connect")
                return
        if topic is None:
            log.warning('no topic supplied to publish to')
            return
        if isinstance(topic, bytes):
            topic = topic.decode('utf-8')
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8')
        try:
            infot = self.mqttc.publish(topic, payload)
            infot.wait_for_publish(5)
        except Exception as e:
            log.warning(str(e))

    # def setAdhocCommands(self, config={}, callback=None):
    #     if not config:
    #         return
    #     if self.disabled:
    #         log.debug("Cannot setAdhocCommands as mqttbroker disabled")
    #         return

    #     adhoc_commands = config.get("adhoc_commands")
    #     # sub to command topic if defined
    #     adhoc_commands_topic = adhoc_commands.get("topic")
    #     if adhoc_commands_topic is not None:
    #         log.info("Setting adhoc commands topic to %s", adhoc_commands_topic)
    #         self.subscribe(adhoc_commands_topic, callback)
