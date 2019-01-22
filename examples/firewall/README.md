# Firewall VNF

VNF that bridges two network interfaces of a container (L2) and forwards all traffic from the input interface to the output interface.

### Configuration

```
    +------------------------------------------+
    |                   VNF                    |
    |                                          |
    |              +-----------+               |
    |              | iptables  |               |
    |              +-----^-----+               |
    |                    |                     |
    | +-----------+    +-+-+    +------------+ |
+-----> eth:input +---->br0+----> eth:output +------->
    | +-----------+    +---+    +------------+ |
    |                                          |
    +------------------------------------------+

```

### Entry point:

```
./start.sh
```
