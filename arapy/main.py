#!/usr/bin/env python3
# ======================================================================
# title             :ClearPass API
# description       :
# author            :Mathias Granlund [mathias.granlund@aranya.se]
# date              :2026-02-20
# script version    :0.8.0
# clearpass version :6.11.13
# python_version    :3.10.12
# ======================================================================

#---- standard libs
import sys
import urllib3

#---- custom libs start

from .api_endpoints import API_ENDPOINTS as APIPath
from .clearpass import ClearPassClient
from . import config
from . import commands
from . import get_version
from .gui import run_gui

#---- globals start
if not config.VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def print_help(args=None):
    """
    Context-aware help, driven by commands.DISPATCH.

    Examples:
      arapy --help
      arapy identities --help
      arapy identities endpoint --help
      arapy identities endpoint add --help
    """
    if args is None:
        args = {}

    module = args.get("module")
    service = args.get("service")
    action = args.get("action")

    dispatch = commands.DISPATCH

    def list_keys(d):
        return sorted(d.keys())

    def indent(lines, n=2):
        pad = " " * n
        return "\n".join(pad + line if line else "" for line in lines.splitlines())

    header = f"ClearPass API tool v{get_version()}\n"

    usage = (
        "Usage:\n"
        "  arapy <module> <service> <action> [--key=value] [-vvv]\n"
        "  arapy --help | --version\n"
        "\n"
        "Notes:\n"
        "  - Use -vvv / --verbose to also print output to console (otherwise logs to file only).\n"
        "  - Use --out=FILE to override default log output path.\n"
    )

    # ---- TOP LEVEL HELP ----
    if not module:
        modules = "\n".join(f"- {m}" for m in list_keys(dispatch))
        examples = (
            "Examples:\n"
            "  arapy policy-elements network-device list\n"
            "  arapy identities endpoint list --limit=5\n"
            "  arapy identities endpoint get --id=1234\n"
        )
        print(header + usage + "\nAvailable modules:\n" + indent(modules) + "\n\n" + examples)
        return

    # ---- MODULE HELP ----
    if module not in dispatch:
        available = ", ".join(list_keys(dispatch))
        print(header + f"Unknown module '{module}'. Available modules: {available}")
        return

    services_dict = dispatch[module]
    if not service:
        services = "\n".join(f"- {s}" for s in list_keys(services_dict))
        examples = (
            "Examples:\n"
            f"  arapy {module} {list_keys(services_dict)[0]} list\n"
            f"  arapy {module} {list_keys(services_dict)[0]} --help\n"
        )
        print(header + usage + f"\nModule: {module}\nAvailable services:\n" + indent(services) + "\n\n" + examples)
        return

    # ---- SERVICE HELP ----
    if service not in services_dict:
        available = ", ".join(list_keys(services_dict))
        print(header + f"Unknown service '{service}' under module '{module}'. Available services: {available}")
        return

    actions_dict = services_dict[service]
    if not action:
        actions = "\n".join(f"- {a}" for a in list_keys(actions_dict))
        examples = (
            "Examples:\n"
            f"  arapy {module} {service} list\n"
            f"  arapy {module} {service} add --help\n"
        )
        print(
            header
            + usage
            + f"\nModule: {module}\nService: {service}\nAvailable actions:\n"
            + indent(actions)
            + "\n\n"
            + examples
        )
        return

    # ---- ACTION HELP ----
    if action not in actions_dict:
        available = ", ".join(list_keys(actions_dict))
        print(header + f"Unknown action '{action}' for {module} {service}. Available actions: {available}")
        return

    # Action-specific help (hand-written “best” docs per action)
    # You can expand this incrementally.
    action_help = ""

    if (module, service, action) == ("policy-elements", "network-device", "list"):
        action_help = (
            "Network Device (NAD) list\n"
            "Usage:\n"
            "  arapy policy-elements network-device list [--limit=N] [--offset=N] [--sort=+id] [--out=FILE] [-vvv]\n"
            "  Optional: --csv_fieldnames=id,name,ip_address\n"
        )

    elif (module, service, action) == ("policy-elements", "network-device", "add"):
        action_help = (
            "Network Device (NAD) add\n"
            "Usage:\n"
            "  arapy policy-elements network-device add --name=NAME --ip_address=IP --vendor_name=VENDOR "
            "[--radius_secret=SECRET] [--out=FILE] [-vvv]\n"
            "  Or from file:\n"
            "  arapy policy-elements network-device add --file=devices.csv [--out=FILE] [-vvv]\n"
            "  arapy policy-elements network-device add --file=devices.json [--out=FILE] [-vvv]\n"
        )

    elif (module, service, action) == ("policy-elements", "network-device", "delete"):
        action_help = (
            "Network Device (NAD) delete\n"
            "Usage:\n"
            "  arapy policy-elements network-device delete --id=1234 [--out=FILE] [-vvv]\n"
        )

    elif (module, service, action) == ("identities", "endpoint", "list"):
        action_help = (
            "Endpoint list\n"
            "Usage:\n"
            "  arapy identities endpoint list [--limit=N] [--offset=N] [--sort=+id] [--out=FILE] [-vvv]\n"
            "  Optional: --csv_fieldnames=id,mac_address,description,status,device_insight_tags\n"
        )

    elif (module, service, action) == ("identities", "endpoint", "get"):
        action_help = (
            "Endpoint get\n"
            "Usage:\n"
            "  arapy identities endpoint get --id=1234 [--out=FILE] [-vvv]\n"
            "  arapy identities endpoint get --mac_address=aa:bb:cc:dd:ee:ff [--out=FILE] [-vvv]\n"
        )

    elif (module, service, action) == ("identities", "endpoint", "add"):
        action_help = (
            "Endpoint add\n"
            "Usage:\n"
            "  arapy identities endpoint add --mac_address=aa:bb:cc:dd:ee:ff --status=Known "
            "[--description=TEXT] [--device_insight_tags=...] [--out=FILE] [-vvv]\n"
            "  Or from file:\n"
            "  arapy identities endpoint add --file=endpoints.csv [--out=FILE] [-vvv]\n"
            "  arapy identities endpoint add --file=endpoints.json [--out=FILE] [-vvv]\n"
            "\n"
            "Notes:\n"
            "  status must be one of: Known, Unknown, Disabled\n"
        )

    elif (module, service, action) == ("identities", "endpoint", "delete"):
        action_help = (
            "Endpoint delete\n"
            "Usage:\n"
            "  arapy identities endpoint delete --id=1234 [--out=FILE] [-vvv]\n"
            "  arapy identities endpoint delete --mac_address=aa:bb:cc:dd:ee:ff [--out=FILE] [-vvv]\n"
        )

    else:
        action_help = (
            f"Help for: {module} {service} {action}\n"
            "No detailed help is defined yet for this action.\n"
            "Tip: run with -vvv to see console output while logging.\n"
        )

    print(header + action_help)


def parse_cli(argv):
    args = {}
    positionals = []

    for item in argv[1:]:
        if item in ("-h", "--help"):
            args["help"] = True
        elif item in ("-v", "--version"):
            args["version"] = True
        elif item in ("-vvv", "--verbose"):
            args["verbose"] = True
        elif item.startswith("--") and "=" in item:
            key, value = item[2:].split("=", 1)
            args[key] = value
        elif item.startswith("-"):
            raise ValueError(f"Unknown flag: {item}")
        else:
            # bare word => positional
            positionals.append(item)

    if len(positionals) >= 1:
        args["module"] = positionals[0]
    if len(positionals) >= 2:
        args["service"] = positionals[1]
    if len(positionals) >= 3:
        args["action"] = positionals[2]

    return args

def main():
    args = parse_cli(sys.argv)

    # ---- VERSION FIRST ----
    if args.get("version"):
        print(get_version())  # or config.VERSION
        return

    # ---- HELP ----
    if args.get("help"):
        print_help(args)
        return

    # ---- No module provided → show top-level help ----
    if not args.get("module"):
        print_help({})
        return

    if args.get("module") == "gui":
        run_gui()
        return

    module = args.get("module")
    service = args.get("service")
    action = args.get("action")

    if not (module and service and action):
        print_help(args)   # contextual help
        return

    cp = ClearPassClient(
        config.SERVER,
        https_prefix=config.HTTPS,
        verify_ssl=config.VERIFY_SSL,
        timeout=config.DEFAULT_TIMEOUT,
    )
    token = cp.login(APIPath, config.CREDENTIALS)["access_token"]

    try:
        command = commands.DISPATCH[module][service][action]
    except KeyError:
        print_help(args)
        print(f"\nUnknown command: {module} {service} {action}")
        return

    command(cp, token, APIPath, args)

if __name__ == "__main__":
    main()