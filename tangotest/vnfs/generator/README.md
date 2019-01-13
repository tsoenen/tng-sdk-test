# Sniffer VNF

VNF that bridges two network interfaces of a container (L2) and forwards all traffic from the input interface to the output interface. It starts tshark to monitor all traffic on this bridge.

### Configuration

```
    +------------------------------------------+
    |                   VNF                    |
    |                                          |
    |                +--------+                |
    |                | tshark |                |
    |                +---^----+                |
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
