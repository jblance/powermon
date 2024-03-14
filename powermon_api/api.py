""" powermon_api / api.py """
import json
import logging
from argparse import ArgumentParser

import paho.mqtt.client as mqttClient

try:
    import uvicorn
except ImportError:
    print("You are missing a python library - 'uvicorn'")
    print("To install it, use the below command:")
    print("    python -m pip install 'powermon[api]'")
    print("or:")
    print("    python -m pip install uvicorn")
    exit(1)
try:
    from fastapi import FastAPI, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
except ImportError:
    print("You are missing a python library - 'fastapi'")
    print("To install it, use the below command:")
    print("    python -m pip install 'powermon[api]'")
    print("or:")
    print("    python -m pip install fastapi")
    exit(1)

from powermon import read_yaml_file
from powermon.libs.version import __version__  # noqa: F401

# from fastapi_mqtt import FastMQTT, MQTTConfig


# Set-up logger
log = logging.getLogger("")
log.setLevel(logging.INFO)

# Initialize some variables
templates = Jinja2Templates(directory="powermon_api/templates")
config = None
mqtt = None
announce = None
results = []


def on_mqtt_message_cb(client, userdata, msg):
    global announce, results
    print(f"mqtt message received on topic: {msg.topic=}\n")
    match msg.topic:
        case 'powermon/api/announce':
            announce = json.loads(msg.payload)
        case _:
            results.append((msg.topic, msg.payload))
    #print(data)


# Create FastAPI app instance
app = FastAPI()
app.mount("/static", StaticFiles(directory="powermon_api/static"), name="static")
@app.get("/")
def read_root(request: Request):
    global config, announce, results
    log.info("config: %s", config)
    return templates.TemplateResponse("home.html.j2", {"request": request, "config": config, "announce": announce, "results": results})

@app.get("/commandList")
def command_list(request: Request):
    return {"command_list": "list of commands"}



def main():
    """main entry point for powermon api"""
    global config, mqtt
    description = f"Power Device Monitoring Api, version: {__version__}"
    parser = ArgumentParser(description=description)

    parser.add_argument(
        "-C",
        "--configFile",
        type=str,
        help="Full location of yaml config file",
        default="./powermon-api.yaml",
    )
    args = parser.parse_args()

    # Build configuration from config file etc
    log.info("Using config file: %s", args.configFile)
    config = {"configFile": args.configFile}
    # build config with details from config file
    config.update(read_yaml_file(args.configFile))

    log.info("config: %s", config)
    if "mqttbroker" in config:
        hostname=config["mqttbroker"].get("name")
        port=config["mqttbroker"].get("port")
        keepalive=60
        username=config["mqttbroker"].get("username")
        password=config["mqttbroker"].get("password")
    try:
        mqtt = mqttClient.Client()
        mqtt.connect(host=hostname, port=port, keepalive=keepalive)
        mqtt.subscribe('powermon/#')
        mqtt.on_message = on_mqtt_message_cb
        mqtt.loop_start()
    except Exception as exc:
        print("Unable to connect to mqttbroker: %s", exc)
        mqtt = None
        raise Exception('unable to connect to mqttbroker') from exc

    uvicorn_config = uvicorn.Config(
        "powermon_api.api:app",
        host=config["api"].get("host", "0.0.0.0"),
        port=config["api"].get("port", 5000),
        log_level=config["api"].get("log_level", "info"),
        reload=True,
    )
    server = uvicorn.Server(uvicorn_config)
    server.run()
