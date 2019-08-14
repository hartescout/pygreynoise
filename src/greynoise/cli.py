"""GreyNoise command line Interface."""

import json
import os
import sys

from argparse import ArgumentParser
from datetime import datetime
from xml.dom.minidom import parseString

from dicttoxml import dicttoxml

from greynoise.client import GreyNoise
from greynoise.util import (
    CONFIG_FILE,
    load_config,
    save_config,
)


def main(argv=None):
    """Entry point for the greynoise CLI.

    :param argv: Command line arguments
    :type: list

    """
    if argv is None:
        argv = sys.argv[1:]

    args = parse_arguments(argv)
    result = args.func(args)

    if args.format == "json":
        output = json.dumps(result)
    elif args.format == "xml":
        output = parseString(dicttoxml(result)).toprettyxml()

    print(output)


def assert_api_key():
    """Get API key from environment or configuration."""
    prog = os.path.basename(sys.argv[0])
    print(
        "Error: API key not found.\n\n"
        "To fix this problem, please use any of the following methods:\n"
        "- Run {!r} to save it to the configuration file.\n"
        "- Pass it to {!r} using the -k/--api-key option.\n"
        "- Set it in the GREYNOISE_API_KEY environment variable.\n"
        .format(
            "{} setup".format(prog),
            "{} run".format(prog),
        )
    )


def setup(args):
    """Configure API key."""
    config = {"api_key": args.api_key}
    save_config(config)
    print("Configuration saved to {!r}".format(CONFIG_FILE))


def noise(args):
    """Get all noise IPs generated by internet scanners, search engines, and worms."""
    return args.api_client.get_noise(args.date)


def context(args):
    """Run IP context query."""
    return args.api_client.get_context(ip_address=args.ip_address)


def quick_check(args):
    """Run IP quick check query."""
    return args.api_client.get_noise_status(ip_address=args.ip_address)


def multi_quick_check(args):
    """Run IP multi quick check query."""
    return args.api_client.get_noise_status_bulk(ip_addresses=args.ip_address)


def actors(args):
    """Run actors query."""
    return args.api_client.get_actors()


def parse_arguments(argv):
    """Parse command line arguments."""
    parser = ArgumentParser(description=__doc__)
    parser.set_defaults(func=lambda args: parser.print_help())
    parser.add_argument(
        "-k",
        "--api-key",
        help="Key to include in API requests",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "xml"],
        default="json",
        help="Output format (%(default)s by default",
    )

    subparsers = parser.add_subparsers(help="Subcommands")

    setup_parser = subparsers.add_parser("setup", help=setup.__doc__.rstrip("."))
    setup_parser.add_argument(
        "-k",
        "--api-key",
        required=True,
        help="Key to include in API requests",
    )
    setup_parser.set_defaults(func=setup)

    noise_parser = subparsers.add_parser(
        "noise",
        help=noise.__doc__.rstrip("."),
    )
    noise_parser.add_argument(
        "-d",
        "--date",
        type=lambda date_str: datetime.strptime(date_str, "%Y-%m-%d"),
        help="Date to use as filter (format: YYYY-MM-DD)",
    )
    noise_parser.set_defaults(func=noise)

    context_parser = subparsers.add_parser(
        "context",
        help=context.__doc__.rstrip("."),
    )
    context_parser.add_argument("ip_address", help="IP address")
    context_parser.set_defaults(func=context)

    quick_check_parser = subparsers.add_parser(
        "quick_check",
        help=quick_check.__doc__.rstrip("."),
    )
    quick_check_parser.add_argument("ip_address", help="IP address")
    quick_check_parser.set_defaults(func=quick_check)

    multi_quick_check_parser = subparsers.add_parser(
        "multi_quick_check",
        help=multi_quick_check.__doc__.rstrip("."),
    )
    multi_quick_check_parser.add_argument("ip_address", nargs="+", help="IP address")
    multi_quick_check_parser.set_defaults(func=multi_quick_check)

    actors_parser = subparsers.add_parser(
        "actors",
        help=actors.__doc__.rstrip("."),
    )
    actors_parser.set_defaults(func=actors)

    args = parser.parse_args()
    if not args.api_key:
        config = load_config()
        args.api_key = config["api_key"]
        args.api_client = GreyNoise(args.api_key)

    return args
