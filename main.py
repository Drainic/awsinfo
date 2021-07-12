import argparse
import sys
parser = argparse.ArgumentParser()
# Global options
parser.add_argument(
    "-c", "--config-file",
    help="specify the configuration file to read (default: argtest.cfg)",
    default="argtest.cfg",
)
subparsers = parser.add_subparsers(dest="command")
# Command: update-device
parser_update_device = subparsers.add_parser(
    "update-device",
    help="update device data",
)
parser_update_device.add_argument(
    "-I", "--ip",
    help="device IP address",
    required=True,
)
parser_update_device.add_argument(
    "-S", "--site-name",
    help="new site name",
)
# Command: add-vlan
parser_add_vlan = subparsers.add_parser(
    "add-vlan",
    help="add a VLAN",
)
parser_add_vlan.add_argument(
    "--vlan-id",
    help="new VLAN ID",
    required=True,
)
args = parser.parse_args()
if not args.command:
    parser.parse_args(["--help"])
    sys.exit(0)
# Do the stuff here
print(args)