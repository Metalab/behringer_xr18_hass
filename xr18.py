from typing import Optional
import logging

import pythonosc.udp_client as uc
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

_LOGGER = logging.getLogger(__name__)

class XR18Mixer:
    def __init__(self, ip_address: str, port: int = 10024):
        self.client = uc.SimpleUDPClient(ip_address, port)
        self.ip_address = ip_address

    async def get_fader_level(self, channel: Optional[int]):
        if channel == None:
            cmd = "/lr/mix/fader"
        else:
            cmd = f"/ch/{channel:02}/mix/fader"

        try:
            self.client.send(uc.OscMessageBuilder(cmd).build())
            res = uc.OscMessage(self.client._sock.recv(4096))
            _LOGGER.debug(f'Fader volume {channel} response {res.params}')
            return res.params[0]
        except BlockingIOError:
            return 0

    async def set_fader_level(self, channel: Optional[int], level: float):
        if channel == None:
            cmd = "/lr/mix/fader"
        else:
            cmd = f"/ch/{channel:02}/mix/fader"
        return await self.client.send_message(cmd, float(level))

    async def get_mute_channel(self, channel: Optional[int]):
        if channel == None:
            cmd = "/lr/mix/on"
        else:
            cmd = f"/ch/{channel:02}/mix/on"

        try:
            self.client.send(uc.OscMessageBuilder(cmd).build())
            res = uc.OscMessage(self.client._sock.recv(4096))
            _LOGGER.debug(f'Fader Mute {channel} response {res.params}')
            return not bool(res.params[0])
        except BlockingIOError:
            return None

    async def mute_channel(self, channel: Optional[int], mute: bool):
        if channel == None:
            cmd = "/lr/mix/on"
        else:
            cmd = f"/ch/{channel:02}/mix/on"
        return await self.client.send_message(cmd, int(not mute))
