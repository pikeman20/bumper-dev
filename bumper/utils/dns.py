"""Dns module."""

from aiohttp import AsyncResolver

from bumper.utils.settings import config as bumper_isc


def get_resolver_with_public_nameserver() -> AsyncResolver:
    """Get resolver."""
    # requires aiodns
    return AsyncResolver(nameservers=bumper_isc.PROXY_NAMESERVER)


async def resolve(host: str) -> str:
    """Resolve host."""
    hosts = await get_resolver_with_public_nameserver().resolve(host)
    return str(hosts[0]["host"])
