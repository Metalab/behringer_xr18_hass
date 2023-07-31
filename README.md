# Behringer XR18 Integration for Home Assistant

## Overview

This project consists of a Home Assistant component that creates and manages several entities related to audio volume control for the Behringer XR18 (probably also works with the X18):

* A number entity for the left and right (LR) volume, with a range from 0 to 100.
* Number entities for the volumes of 16 different channels, each with a range from 0 to 100.
* A number entity for an auxiliary (AUX) volume, also with a range from 0 to 100.
* Switch entities for the mute settings of all volumes mentioned above.

The component appears as an integration within Home Assistant and can be configured via the user interface. Configuration includes setting the IP address, port, and the switch entity name that enables or disables polling.

The idea with the switch entity is that the mixer can be turned on and off via this entity. This could be a Sonoff for example. Polling the mixer is only active while the mixer has power in order to reduce chatter on the network (although it's only a single UDP packet every 9 seconds).

Enabling the switch also triggers fetching the full configuration of the mixer.

## Installation

The integration can be added to Home Assistant using the following steps:

1. Copy the content of this repository to `custom_components/behringer_xr18` in your Home Assistant configuration directory.
2. Restart Home Assistant
3. Navigate to the Home Assistant Integrations page.
4. Click on the "+ ADD INTEGRATION" button.
5. Search for "Behringer XR18".
6. Follow the setup wizard, providing the required information (IP, port, and switch entity name).

## Contributing

Contributions to this project are welcome. Please create a fork of the repository, make your changes, and then submit a pull request. Please adhere to the existing coding style and conventions.

## Support and Contact

You can contact @anlumo:monitzer.com on Matrix if you have any questions.

## Disclaimer

This component is provided as is, without warranty of any kind. Use of this software is at your own risk. Please ensure you understand and agree with the license terms before using this software.

# License

This project is licensed under the GNU General Public License v3.0. For more information, see [https://choosealicense.com/licenses/gpl-3.0/](https://choosealicense.com/licenses/gpl-3.0/).

The license is also provided in the LICENSE file in this repository.
