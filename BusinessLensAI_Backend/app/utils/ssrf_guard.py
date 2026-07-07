"""
BusinessLens AI — SSRF Guard

Validates user-supplied hostnames/IPs before opening outbound connections.
Blocks requests to private IP ranges, loopback, link-local, and cloud metadata endpoints.

Called by ConnectionService BEFORE creating any connector.
"""

from __future__ import annotations

import ipaddress
import socket

from app.core.exceptions import SSRFError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Private, loopback, link-local, and cloud metadata IP ranges
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),         # RFC1918 private
    ipaddress.ip_network("172.16.0.0/12"),       # RFC1918 private
    ipaddress.ip_network("192.168.0.0/16"),      # RFC1918 private
    ipaddress.ip_network("127.0.0.0/8"),         # Loopback
    ipaddress.ip_network("::1/128"),             # IPv6 loopback
    ipaddress.ip_network("169.254.0.0/16"),      # Link-local (AWS metadata)
    ipaddress.ip_network("fe80::/10"),           # IPv6 link-local
    ipaddress.ip_network("100.64.0.0/10"),       # Carrier-grade NAT
    ipaddress.ip_network("0.0.0.0/8"),           # "This" network
    ipaddress.ip_network("::ffff:0:0/96"),       # IPv4-mapped IPv6
]

# Blocked hostnames regardless of IP resolution
_BLOCKED_HOSTNAMES: frozenset[str] = frozenset({
    "localhost",
    "metadata.google.internal",         # GCP metadata
    "169.254.169.254",                  # AWS/Azure metadata (also caught by IP check)
})


def validate_host(host: str, port: int | None = None) -> None:
    """
    Validate that a host is safe to connect to.
    Raises SSRFError if the host resolves to a private/internal IP.

    Must be called before ConnectorFactory.create_from_params() / create_from_model().
    """
    host_lower = host.lower().strip()

    # Block by hostname
    if host_lower in _BLOCKED_HOSTNAMES:
        raise SSRFError(host=host)

    # Resolve hostname to IP(s)
    try:
        addr_infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise SSRFError(host=host) from exc

    for _, _, _, _, sockaddr in addr_infos:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue

        for network in _BLOCKED_NETWORKS:
            if ip in network:
                logger.warning(
                    "SSRF blocked: host=%s resolved to private IP=%s (network=%s)",
                    host, ip_str, network,
                )
                raise SSRFError(host=host)

    logger.debug("SSRF check passed: host=%s", host)
