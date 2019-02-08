# Examples

This folder contains an example of library usage with the Emulator as a VIM.
You need `pytest` library to execute this test.

### Service configuration

```
+--------+     +----------+         +-------+     +--------+
| Client | <-> | Firewall | <-----> | Snort | <-> | Server |
+--------+     +----------+    ^    +-------+     +--------+
                               |
                          +---------+
                          | Sniffer |
                          +---------+
```

Snort is configured to detect HTTP requests to `http://server_ip/restricted/` and log them. This log is retrieved and analyzed in the test script.

Firewall does nothing by default. It is configured to block all traffic by the test script. Then Sniffer is used to check whether there is still some traffic between Client and Server after Firewall configuration.

