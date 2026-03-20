import json
import re
import types
from pathlib import Path

import pytest
import requests

import netloom.cli.copy as copymod
import netloom.cli.diff as diffmod
from netloom.core.config import AppPaths, Settings


def _make_settings(tmp_path, profile: str):
    paths = AppPaths(
        cache_dir=tmp_path / profile / "cache",
        state_dir=tmp_path / profile / "state",
        response_dir=tmp_path / profile / "responses",
        app_log_dir=tmp_path / profile / "logs",
    ).ensure()
    return Settings(
        server=profile,
        https_prefix="https://",
        verify_ssl=False,
        timeout=1,
        client_id=f"{profile}-client",
        client_secret=f"{profile}-secret",
        active_profile=profile,
        paths=paths,
    )


def _catalog():
    return {
        "modules": {
            "policyelements": {
                "role": {
                    "actions": {
                        "list": {
                            "method": "GET",
                            "paths": ["/api/role"],
                            "params": [
                                "filter",
                                "sort",
                                "offset",
                                "limit",
                                "calculate_count",
                            ],
                        },
                        "get": {
                            "method": "GET",
                            "paths": ["/api/role/{id}", "/api/role/name/{name}"],
                            "params": ["id", "name"],
                        },
                    }
                }
            }
        }
    }


def _plugin(build_client, catalog):
    def get_api_catalog(
        cp, token, settings, force_refresh=False, catalog_view="visible"
    ):
        del cp, token, settings, force_refresh, catalog_view
        return catalog

    def normalize_diff_item(module, service, item):
        del module, service
        if isinstance(item, dict):
            return {
                key: normalize_diff_item("", "", value)
                for key, value in item.items()
                if key not in {"id", "_links", "updated_at"}
            }
        if isinstance(item, list):
            return [normalize_diff_item("", "", value) for value in item]
        return item

    return types.SimpleNamespace(
        build_client=build_client,
        resolve_auth_token=lambda cp, settings: f"{settings.server}-token",
        get_api_catalog=get_api_catalog,
        normalize_diff_item=normalize_diff_item,
    )


class _CollectionCP:
    last_response_meta = None

    def __init__(self, catalog, items):
        self.catalog = catalog
        self.items = items

    def get_action_definition(self, api_catalog, module, service, action):
        return self.catalog["modules"][module][service]["actions"][action]

    def list(self, api_catalog, token, args, *, params=None):
        del api_catalog, token, params
        items = list(self.items)
        raw_filter = args.get("filter")
        if raw_filter:
            parsed = json.loads(raw_filter)
            if isinstance(parsed, dict) and isinstance(parsed.get("name"), str):
                items = [item for item in items if item.get("name") == parsed["name"]]
        return {"_embedded": {"items": items}, "count": len(items)}

    def get(self, api_catalog, token, args, *, params=None):
        del api_catalog, token, params
        if args.get("id") not in (None, ""):
            for item in self.items:
                if str(item.get("id")) == str(args["id"]):
                    return item
        if args.get("name") not in (None, ""):
            for item in self.items:
                if item.get("name") == args["name"]:
                    return item
        response = types.SimpleNamespace(status_code=404)
        raise requests.HTTPError("item not found", response=response)


def test_handle_diff_command_all_is_symmetric_and_normalized(
    monkeypatch, tmp_path, capsys
):
    catalog = _catalog()
    source_cp = _CollectionCP(
        catalog,
        [
            {"id": 1, "name": "alpha", "description": "same", "_links": {"self": "a"}},
            {"id": 2, "name": "beta", "description": "source-only"},
            {"id": 3, "name": "gamma", "description": "old"},
        ],
    )
    target_cp = _CollectionCP(
        catalog,
        [
            {"id": 99, "name": "alpha", "description": "same", "updated_at": "now"},
            {"id": 5, "name": "gamma", "description": "new"},
            {"id": 6, "name": "delta", "description": "target-only"},
        ],
    )

    monkeypatch.setattr(copymod, "list_profiles", lambda: ["lab", "prod"])
    monkeypatch.setattr(
        diffmod,
        "load_settings_for_profile",
        lambda profile: _make_settings(tmp_path, profile),
    )

    def build_client(settings, *, mask_secrets=True):
        del mask_secrets
        return source_cp if settings.server == "lab" else target_cp

    settings = _make_settings(tmp_path, "prod")
    report = diffmod.handle_diff_command(
        {
            "module": "policyelements",
            "service": "role",
            "action": "diff",
            "from": "lab",
            "to": "prod",
            "all": True,
        },
        settings=settings,
        plugin=_plugin(build_client, catalog),
    )

    assert report["summary"] == {
        "compared": 2,
        "only_in_source": 1,
        "only_in_target": 1,
        "different": 1,
        "same": 1,
    }
    different = next(item for item in report["items"] if item["status"] == "different")
    assert different["label"] == "gamma"
    assert different["changed_fields"] == ["description"]
    assert different["source"]["description"] == "old"
    assert different["target"]["description"] == "new"
    same = next(item for item in report["items"] if item["status"] == "same")
    assert same["label"] == "alpha"

    out = capsys.readouterr().out
    assert "Only in target: 1" in out
    assert "Differences:" in out

    report_path = Path(report["artifacts"]["report"])
    assert report_path.parent == settings.paths.response_dir
    assert re.fullmatch(
        r"policyelements_role_lab_to_prod_\d{8}-\d{6}-\d{6}_diff\.json",
        report_path.name,
    )
    saved = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved["summary"]["different"] == 1


def test_handle_diff_command_name_is_source_scoped(monkeypatch, tmp_path):
    catalog = _catalog()
    source_cp = _CollectionCP(catalog, [{"id": 2, "name": "beta", "description": "x"}])
    target_cp = _CollectionCP(catalog, [{"id": 6, "name": "delta", "description": "y"}])

    monkeypatch.setattr(copymod, "list_profiles", lambda: ["lab", "prod"])
    monkeypatch.setattr(
        diffmod,
        "load_settings_for_profile",
        lambda profile: _make_settings(tmp_path, profile),
    )

    def build_client(settings, *, mask_secrets=True):
        del mask_secrets
        return source_cp if settings.server == "lab" else target_cp

    report = diffmod.handle_diff_command(
        {
            "module": "policyelements",
            "service": "role",
            "action": "diff",
            "from": "lab",
            "to": "prod",
            "name": "beta",
        },
        settings=_make_settings(tmp_path, "prod"),
        plugin=_plugin(build_client, catalog),
    )

    assert report["summary"]["only_in_source"] == 1
    assert report["summary"]["only_in_target"] == 0
    assert report["items"][0]["status"] == "only_in_source"


def test_handle_diff_command_filter_is_symmetric_with_filtered_target(
    monkeypatch, tmp_path
):
    catalog = _catalog()
    source_cp = _CollectionCP(
        catalog,
        [
            {"id": 1, "name": "Guest", "description": "same"},
            {"id": 2, "name": "Admin", "description": "skip"},
        ],
    )
    target_cp = _CollectionCP(
        catalog,
        [
            {"id": 9, "name": "Guest", "description": "same"},
            {"id": 8, "name": "TargetOnly", "description": "skip"},
        ],
    )

    monkeypatch.setattr(copymod, "list_profiles", lambda: ["lab", "prod"])
    monkeypatch.setattr(
        diffmod,
        "load_settings_for_profile",
        lambda profile: _make_settings(tmp_path, profile),
    )

    def build_client(settings, *, mask_secrets=True):
        del mask_secrets
        return source_cp if settings.server == "lab" else target_cp

    report = diffmod.handle_diff_command(
        {
            "module": "policyelements",
            "service": "role",
            "action": "diff",
            "from": "lab",
            "to": "prod",
            "filter": json.dumps({"name": "Guest"}),
        },
        settings=_make_settings(tmp_path, "prod"),
        plugin=_plugin(build_client, catalog),
    )

    assert report["summary"] == {
        "compared": 1,
        "only_in_source": 0,
        "only_in_target": 0,
        "different": 0,
        "same": 1,
    }


def test_handle_diff_command_match_by_id_uses_id_resolution(monkeypatch, tmp_path):
    catalog = _catalog()
    source_cp = _CollectionCP(
        catalog, [{"id": 7, "name": "old-name", "description": "x"}]
    )
    target_cp = _CollectionCP(
        catalog, [{"id": 7, "name": "new-name", "description": "x"}]
    )

    monkeypatch.setattr(copymod, "list_profiles", lambda: ["lab", "prod"])
    monkeypatch.setattr(
        diffmod,
        "load_settings_for_profile",
        lambda profile: _make_settings(tmp_path, profile),
    )

    def build_client(settings, *, mask_secrets=True):
        del mask_secrets
        return source_cp if settings.server == "lab" else target_cp

    report = diffmod.handle_diff_command(
        {
            "module": "policyelements",
            "service": "role",
            "action": "diff",
            "from": "lab",
            "to": "prod",
            "id": "7",
            "match_by": "id",
        },
        settings=_make_settings(tmp_path, "prod"),
        plugin=_plugin(build_client, catalog),
    )

    assert report["summary"]["different"] == 1
    assert report["items"][0]["match_by"] == "id"
    assert report["items"][0]["changed_fields"] == ["name"]


def test_handle_diff_command_rejects_missing_selector(monkeypatch, tmp_path):
    monkeypatch.setattr(copymod, "list_profiles", lambda: ["lab", "prod"])
    monkeypatch.setattr(
        diffmod,
        "load_settings_for_profile",
        lambda profile: _make_settings(tmp_path, profile),
    )

    with pytest.raises(ValueError, match="Use exactly one selector"):
        diffmod.handle_diff_command(
            {
                "module": "policyelements",
                "service": "role",
                "action": "diff",
                "from": "lab",
                "to": "prod",
            },
            settings=_make_settings(tmp_path, "prod"),
            plugin=types.SimpleNamespace(),
        )
