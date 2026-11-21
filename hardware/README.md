# hardware/

Optional (task SAT-07, SAT-08): an **ESP32 satellite-module emulator** used for Level B simulation.

**What it emulates.** The device-side hardware module of a satellite service: the phone talks to it over BLE or USB with the same framing a real module would use; the ESP32 applies simulated latency, loss and message-size limits and forwards the message to the cloud over its own network connection. The radio, the satellite and the provider's ground segment remain simulated.

**Why.** The phone can run in real airplane mode while the hardware interface is real, which prepares the replacement of the emulator with a real module later.

**Status.** Nothing is implemented yet. The phone↔module protocol is specified first (SAT-08); the firmware language is an open decision (O7). Do not describe this folder as a working satellite link.
