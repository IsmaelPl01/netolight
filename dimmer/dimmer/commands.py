import base64
import os
import grpc

from chirpstack_api import api
from google.protobuf.json_format import MessageToDict

from .log import logger


def enqueue_device_command(dev_eui: str, data: bytes, f_port: int = 2):
    """Enqueue a command to a device."""
    channel = grpc.insecure_channel(os.getenv("CHIRPSTACK_SERVER_URL"))
    token = [ ('authorization', f'Bearer {os.getenv("CHIRPSTACK_SERVER_JWT_TOKEN")}') ]
    client = api.DeviceServiceStub(channel)
    req = api.EnqueueDeviceQueueItemRequest()
    req.queue_item.confirmed = False
    req.queue_item.dev_eui = dev_eui
    req.queue_item.data = data
    req.queue_item.f_port = f_port
    resp = client.Enqueue(req, metadata=token)
    return MessageToDict(resp)


def enqueue_group_command(mgid: str, data: bytes, f_port: int = 2) -> dict:
    """Enqueue a message to a group of devices."""
    channel = grpc.insecure_channel(os.getenv("CHIRPSTACK_SERVER_URL"))
    token = [ ('authorization', f'Bearer {os.getenv("CHIRPSTACK_SERVER_JWT_TOKEN")}') ]
    client = api.MulticastGroupServiceStub(channel)
    req = api.EnqueueMulticastGroupQueueItemRequest()
    req.queue_item.multicast_group_id = mgid
    req.queue_item.data = data
    req.queue_item.f_port = f_port
    resp = client.Enqueue(req, metadata=token)
    return MessageToDict(resp)


def turn_on(dev_eui: str):
    logger.debug(f'Sending command TURN_ON to device {dev_eui}')
    return enqueue_device_command(dev_eui, b'9529-ON')


def turn_off(dev_eui: str):
    logger.debug(f'Sending command TURN_OFF to device {dev_eui}')
    return enqueue_device_command(dev_eui, b'9529-OF')


def dim(dev_eui: str, val: int):
    logger.debug(f'Sending command DIM_{val} to device {dev_eui}')
    return enqueue_device_command(dev_eui, bytes(f'9529-DM{val}', 'utf-8'))


def turn_on_group(mgid: str):
    logger.debug(f'Sending command TURN_ON to group {mgid}')
    return enqueue_group_command(mgid, b'9529-ON')


def turn_off_group(mgid: str):
    logger.debug(f'Sending command TURN_OFF to group {mgid}')
    return enqueue_group_command(mgid, b'9529-OF')


def dim_group(mgid: str, val: int):
    logger.debug(f'Sending command DIM_{val} to group {mgid}')
    return enqueue_group_command(mgid, bytes(f'9529-DM{str(val).zfill(3)}', 'utf-8'))
