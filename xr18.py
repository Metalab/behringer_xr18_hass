from typing import Callable, Optional
import logging
import asyncio
import re

from homeassistant.core import HomeAssistant

import pythonosc.udp_client as uc
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.osc_message_builder import ArgValue
from pythonosc.osc_packet import OscPacket

_LOGGER = logging.getLogger(__name__)

fader_channel_parser = re.compile(r'^/ch/(\d{2})/mix/fader$')
mute_channel_parser = re.compile(r'^/ch/(\d{2})/mix/on$')


class XR18EventReceiver:
    def __init__(self, fader_dispatcher: dict[int, Callable[[float], None]], mute_dispatcher: dict[int, Callable[[bool], None]]):
        super().__init__()
        self.transport = None
        self.fader_dispatcher = fader_dispatcher
        self.mute_dispatcher = mute_dispatcher

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, _addr):
        try:
            packet = OscPacket(data)
            for timed_message in packet.messages:
                message = timed_message.message
                _LOGGER.debug(f'set {message.address} = {message.params}')
                match message.address:
                    case "/lr/mix/fader":
                        if 0 in self.fader_dispatcher:
                            self.fader_dispatcher[0](message.params[0])
                    case "/lr/mix/on":
                        if 0 in self.mute_dispatcher:
                            self.mute_dispatcher[0](not message.params[0])
                    case "/rtn/aux/mix/fader":
                        if 0 in self.fader_dispatcher[17]:
                            self.fader_dispatcher[17](message.params[0])
                    case "/rtn/aux/mix/on":
                        if 17 in self.mute_dispatcher[17]:
                            self.mute_dispatcher[17](not message.params[0])
                    case _:
                        parsed = fader_channel_parser.match(message.address)
                        if parsed:
                            channel = int(parsed.group(1))
                            if channel in self.fader_dispatcher:
                                self.fader_dispatcher[channel](
                                    message.params[0])
                        else:
                            parsed = mute_channel_parser.match(message.address)
                            if parsed:
                                channel = int(parsed.group(1))
                                if channel in self.mute_dispatcher:
                                    self.mute_dispatcher[channel](
                                        not message.params[0])
        except Exception as e:
            _LOGGER.error(f'Handling UDP packet failed: {e}')


class XR18Mixer:
    def __init__(self, hass: HomeAssistant, ip_address: str, port: int = 10024):
        self.hass = hass
        self.fader_dispatcher = {}
        self.mute_dispatcher = {}
        self.client = uc.SimpleUDPClient(ip_address, port)
        self.ip_address = ip_address
        self.periodic_task = None
        self.transport = None

    @property
    def sock(self):
        return self.client._sock

    def subscribe_fader(self, channel: int, callback: Callable[[float], None]):
        self.fader_dispatcher[channel] = callback

    def unsubscribe_fader(self, channel: int):
        self.fader_dispatcher.pop(channel)

    def subscribe_mute(self, channel: int, callback: Callable[[bool], None]):
        self.mute_dispatcher[channel] = callback

    def unsubscribe_mute(self, channel: int):
        self.mute_dispatcher.pop(channel)

    def refresh_fader_level(self, channel: int):
        match channel:
            case 0:
                cmd = "/lr/mix/fader"
            case 17:
                cmd = "/rtn/aux/mix/fader"
            case _:
                cmd = f"/ch/{channel:02}/mix/fader"

        _LOGGER.debug(f'send message "{cmd}"')

        self.client.send_message(cmd, None)

    def set_fader_level(self, channel: int, level: float):
        match channel:
            case 0:
                cmd = "/lr/mix/fader"
            case 17:
                cmd = "/rtn/aux/mix/fader"
            case _:
                cmd = f"/ch/{channel:02}/mix/fader"

        _LOGGER.debug(f'send message "{cmd}" [{level}]')

        self.client.send_message(cmd, float(level))

    def refresh_mute_channel(self, channel: int):
        match channel:
            case 0:
                cmd = "/lr/mix/on"
            case 17:
                cmd = "/rtn/aux/mix/on"
            case _:
                cmd = f"/ch/{channel:02}/mix/on"

        _LOGGER.debug(f'send message "{cmd}"')

        self.client.send_message(cmd, None)

    def mute_channel(self, channel: int, mute: bool):
        match channel:
            case 0:
                cmd = "/lr/mix/on"
            case 17:
                cmd = "/rtn/aux/mix/on"
            case _:
                cmd = f"/ch/{channel:02}/mix/on"

        _LOGGER.debug(f'send message "{cmd}" [{not mute}]')

        self.client.send_message(cmd, int(not mute))

    async def start_listener(self):
        _LOGGER.debug('Starting listener for events')
        # Listen for incoming events
        transport, _protocol = await self.hass.loop.create_datagram_endpoint(lambda: XR18EventReceiver(self.fader_dispatcher, self.mute_dispatcher), sock=self.sock)
        self.transport = transport

        # Start the periodic task
        self.periodic_task = asyncio.create_task(
            self.send_periodic_message("/xremotenfb", ''))

        # Fetch initial state
        _LOGGER.debug('Fetch initial state')
        self.client.send_message("/xremotenfb", '')
        for i in range(18):
            self.refresh_fader_level(i)
            self.refresh_mute_channel(i)

    def set_helper_state(self, state: bool):
        _LOGGER.debug(f'helper state = {state}')
        if state and self.periodic_task is None:
            self.hass.async_create_task(self.start_listener())
        elif not state and self.periodic_task is not None:
            # Cancel the periodic task
            self.periodic_task.cancel()
            self.periodic_task = None
            self.transport.close()
            self.transport = None

    async def send_periodic_message(self, message: str, value: ArgValue):
        while True:
            for _ in range(9):  # 9 seconds
                await asyncio.sleep(1)
                if self.periodic_task.cancelled():
                    _LOGGER.debug('Periodic task terminating')
                    return
            _LOGGER.debug(f'XR18 refresh ticker')
            self.client.send_message(message, value)
