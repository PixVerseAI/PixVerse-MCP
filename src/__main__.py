"""
Entry point for Pixverse MCP server.
"""

import asyncio
from .server import cli_main


def main():
    """Main entry point for uvx."""
    asyncio.run(cli_main())


if __name__ == "__main__":
    main()
