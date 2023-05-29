import logging
import sys
from xr18 import XR18Mixer
import asyncio
from pythonosc.osc_packet import OscPacket

_LOGGER = logging.getLogger(__name__)


class MockHass:
    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_running_loop()

    def async_create_task(self, task):
        self.loop.create_task(task)


async def main(ip: str, port: int):
    xr18_mixer = XR18Mixer(MockHass(), ip, port)
    _LOGGER.debug('Startup!')

    def log_fader(value: float):
        _LOGGER.debug(f'fader = {value}')

    def log_mute(value: bool):
        _LOGGER.debug(f'mute = {value}')

    for i in range(18):
        xr18_mixer.subscribe_fader(i, log_fader)
        xr18_mixer.subscribe_mute(i, log_mute)

    xr18_mixer.set_helper_state(True)

    try:
        while True:
            await asyncio.sleep(3600)  # Serve for 1 hour.
    except KeyboardInterrupt:
        _LOGGER.info('Terminating.')
        xr18_mixer.set_helper_state(False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _LOGGER.debug(f'args: {sys.argv}')
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} IP PORT')
    else:
        asyncio.run(main(sys.argv[1], int(sys.argv[2])))
