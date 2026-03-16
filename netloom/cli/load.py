from __future__ import annotations

from netloom.core.config import describe_profile_state, set_active_plugin
from netloom.core.plugin import list_plugins


def handle_load_command(args: dict) -> bool:
    service = args.get("service")
    action = args.get("action")

    if service in (None, "") and action in (None, ""):
        print("Usage: netloom load <plugin>")
        return True

    if service == "list" and not action:
        print("Available plugins:")
        for plugin in list_plugins():
            print(f"- {plugin}")
        return True

    if service == "show" and not action:
        state = describe_profile_state()
        print(f"Active plugin: {state.active_plugin or '<unset>'}")
        return True

    if action:
        print("Usage: netloom load <plugin>")
        return True

    plugin = str(service)
    available = list_plugins()
    if plugin not in available:
        print(f"Unknown plugin '{plugin}'. Available plugins: {', '.join(available)}")
        return True

    set_active_plugin(plugin)
    print(f"Active plugin set to {plugin}.")
    return True
