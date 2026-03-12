from __future__ import annotations

from arapy.cli.help import service_cli_actions
from arapy.core.config import list_profiles


def completion_candidates(words: list[str], catalog: dict | None) -> list[str]:
    modules = (catalog or {}).get("modules") or {}

    current = ""
    for word in words:
        if word.startswith("--_cur="):
            current = word.split("=", 1)[1]

    positionals = [word for word in words if not word.startswith("-")]

    if len(positionals) == 0:
        return ["cache", "server", *sorted(modules.keys())]

    module = positionals[0]
    if module == "cache":
        if len(positionals) == 1:
            return ["clear", "update"]
        return []

    if module == "server":
        if len(positionals) == 1:
            return ["list", "show", "use"]
        service = positionals[1]
        if service == "use" and len(positionals) == 2:
            return list_profiles()
        if service in {"list", "show"}:
            return []
        return ["list", "show", "use"]

    if module not in modules:
        return ["cache", "server", *sorted(modules.keys())]

    services = modules[module]
    if len(positionals) == 1 or (len(positionals) == 2 and current != ""):
        return sorted(services.keys())

    service = positionals[1]
    if service not in services:
        return sorted(services.keys())

    if len(positionals) == 2:
        return service_cli_actions(services[service])

    return []


def print_completions(words: list[str], catalog: dict | None) -> None:
    print("\n".join(completion_candidates(words, catalog)))
