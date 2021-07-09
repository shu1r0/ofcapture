# OpenFlow Proxy (ofcapture)

This program monitors the communication between switches and controller, 
and reproduces the flow table from the messages.
This is designed to separate the application from proxy.
Now, The proxy only mediates the TCP communication, but does not filter or send packets.
It supports only OpenFlow 1.3.