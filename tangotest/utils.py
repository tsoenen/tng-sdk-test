import socket


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


SNORT_TIME_FORMAT = '%Y/%m/%d-%H:%M:%S.%f'
SNIFFER_TIME_FORMAT = '%b %d, %Y %H:%M:%S.%f'
