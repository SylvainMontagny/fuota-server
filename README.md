# LoRaWAN FUOTA Server with Node-RED dashboards
Antoine AUGAGNEUR, USMB 2022

# What does LoRaWAN FUOTA mean ?
The FUOTA process allows a user to send a firmware image to an end-device (or a fleet) and update the current firmware remotely.
It needs dedicated layer messaging packages and prerequisites. To know more about FUOTA, check:
- the **_LoRaWAN Advanced Features_** book. Available here: [https://www.univ-smb.fr/lorawan/en/free-book/] 
- the video demonstrations. Available here: [https://www.youtube.com/playlist?list=PLZQkMBvJm9EIDVI_VpMRksb1GjXc08aiB]

# What are the different folders of this repo ?
To perform a FUOTA session, messaging package are needed. Each folder represents one of them and contains a Node-RED flow (json file) and its presentation (md file).
Here there are:
* clock-synchronization
To synchronize the time of an end-device with the time of the LoRaWAN server it is connected to.
* multicast
To send a single downlink frame to several end-devices at the same time.
* data-fragmentation
To send a large file over the LoRaWAN protocol
* fuota (that is actualy the firmware management package)
To manage the images the end-device owns and trigger the firmware update with the new image.

# Disclaimer
Please note that all of these tools are not intended to be used in an industrial context. They are dedicated to understanding and tests.

# Ressources
