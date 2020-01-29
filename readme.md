## Shippix

This uses an [RTL-SDR radio receiver](https://www.rtl-sdr.com/) and a Raspberry Pi Zero to monitor shipping traffic.

Larger ships at sea are supposed to continuously advertise their positions to aid marine navigation and prevent colissions. This is done by broadcasting radio messages according to the [AIS specification](https://en.wikipedia.org/wiki/Automatic_Identification_System). These signals can be picked up with an RTL-SDR radio receiver.

This project works by checking if the advertised location of a ship falls within a predefined geofence which is within the field of view of a mounted Raspberry Pi camera. The Raspberry Pi camera is then used to capture images of the ship and a Lambda stitches them together into a video.

Captures can be viewed at the [Shippix viewer](https://github.com/varunnaik/shippix-viewer).

[More information on this project](https://blog.vnaik.com/posts/photographing-ships.html).