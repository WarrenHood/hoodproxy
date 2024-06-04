# HoodProxy

A simple WIP TCP/UDP proxy. Only TCP is implemented currently.

## Usage

Install poetry, and ensure you have python 3.10+.

Run the script with `--help` to see the arguments.

```bash
poetry run hoodproxy --help
```

Add an entry to your hosts file or modify the target program to point to your listen ip (127.0.0.1 will probably be fine if running locally)
Then run hoodproxy, and start up the target program/game.