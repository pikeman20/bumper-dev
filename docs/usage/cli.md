# Command-Line Usage

**Bumper** supports several command-line arguments, which you can view by using the `-h` flag.

> **Note:** For more detailed configuration, use environment variables. See [Environment Variables](../configuration/environment.md).

```sh
usage: bumper [-h] [--listen LISTEN] [--announce ANNOUNCE] [--debug_level DEBUG_LEVEL] [--debug_verbose DEBUG_VERBOSE]

options:
  -h, --help                    Show this help message and exit
  --listen LISTEN               Start serving on address (default: from socket)
  --announce ANNOUNCE           Announce address to bots on check-in (default: from --listen)
  --debug_level DEBUG_LEVEL     Set debug log level (default: "INFO")
  --debug_verbose DEBUG_VERBOSE Enable verbose debug logs (default: 1)
```
