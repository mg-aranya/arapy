from __future__ import annotations

from typing import Any

from netloom.cli.copy import (
    VALID_MATCH_MODES,
    _copy_item_label,
    _default_artifact_path,
    _fetch_source_items,
    _load_catalog,
    _resolve_match,
    _validate_compare_args,
)
from netloom.core.config import Settings, load_settings_for_profile
from netloom.io.output import should_mask_secrets, write_value_to_file


def _normalize_diff_item(plugin, module: str, service: str, item: Any) -> Any:
    normalizer = getattr(plugin, "normalize_diff_item", None)
    if callable(normalizer):
        return normalizer(module, service, item)
    return item


def _changed_fields(source: Any, target: Any) -> list[str]:
    if isinstance(source, dict) and isinstance(target, dict):
        return sorted(
            key
            for key in set(source.keys()) | set(target.keys())
            if source.get(key) != target.get(key)
        )
    return ["value"] if source != target else []


def _match_key(
    item: dict[str, Any],
    match_mode: str,
) -> tuple[tuple[str, str] | None, str | None]:
    if match_mode not in VALID_MATCH_MODES:
        raise ValueError("--match-by must be one of: auto, name, id")

    if match_mode in {"auto", "name"} and item.get("name") not in (None, ""):
        return ("name", str(item["name"])), "name"

    if match_mode in {"auto", "id"} and item.get("id") not in (None, ""):
        return ("id", str(item["id"])), "id"

    return None, None


def _build_symmetric_index(
    items: list[dict[str, Any]], match_mode: str
) -> tuple[dict[tuple[str, str], dict[str, Any]], list[dict[str, Any]]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    unmatched: list[dict[str, Any]] = []
    for item in items:
        key, _ = _match_key(item, match_mode)
        if key is None or key in indexed:
            unmatched.append(item)
            continue
        indexed[key] = item
    return indexed, unmatched


def _diff_entry(
    *,
    label: str,
    match_by: str | None,
    status: str,
    source_item: dict[str, Any] | None,
    target_item: dict[str, Any] | None,
    source_normalized: Any | None = None,
    target_normalized: Any | None = None,
) -> dict[str, Any]:
    entry = {
        "label": label,
        "status": status,
        "match_by": match_by,
        "source_id": source_item.get("id") if isinstance(source_item, dict) else None,
        "source_name": (
            source_item.get("name") if isinstance(source_item, dict) else None
        ),
        "target_id": target_item.get("id") if isinstance(target_item, dict) else None,
        "target_name": (
            target_item.get("name") if isinstance(target_item, dict) else None
        ),
    }
    if status == "different":
        entry["changed_fields"] = _changed_fields(source_normalized, target_normalized)
        entry["source"] = source_normalized
        entry["target"] = target_normalized
    elif status == "only_in_source":
        entry["source"] = source_normalized
    elif status == "only_in_target":
        entry["target"] = target_normalized
    return entry


def _emit_diff_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("Diff completed")
    print(f"Source profile: {report['source_profile']}")
    print(f"Target profile: {report['target_profile']}")
    print(f"Service: {report['module']} {report['service']}")
    print(f"Match by: {report['match_by']}")
    print(f"Compared: {summary['compared']}")
    print(f"Only in source: {summary['only_in_source']}")
    print(f"Only in target: {summary['only_in_target']}")
    print(f"Different: {summary['different']}")
    print(f"Same: {summary['same']}")

    different = [item for item in report["items"] if item["status"] == "different"]
    if different:
        print("Differences:")
        for item in different[:10]:
            fields = ", ".join(item.get("changed_fields") or ["value"])
            print(f"- {item['label']}: {fields}")

    only_in_source = [
        item for item in report["items"] if item["status"] == "only_in_source"
    ]
    if only_in_source:
        print("Only in source:")
        for item in only_in_source[:10]:
            print(f"- {item['label']}")

    only_in_target = [
        item for item in report["items"] if item["status"] == "only_in_target"
    ]
    if only_in_target:
        print("Only in target:")
        for item in only_in_target[:10]:
            print(f"- {item['label']}")

    print(f"Report: {report['artifacts']['report']}")


def handle_diff_command(
    args: dict[str, Any],
    *,
    settings: Settings | None,
    plugin,
) -> dict[str, Any]:
    _validate_compare_args(
        args,
        module_key="module",
        service_key="service",
        operation_name="diff",
    )

    module = str(args["module"])
    service = str(args["service"])
    source_profile = str(args["from"])
    target_profile = str(args["to"])
    match_by = str(args.get("match_by", "auto"))

    source_settings = load_settings_for_profile(source_profile)
    target_settings = load_settings_for_profile(target_profile)
    active_settings = settings or target_settings
    mask_secrets = should_mask_secrets(args, active_settings)
    catalog_view = str(args.get("catalog_view") or "visible").strip().lower()
    if catalog_view not in {"visible", "full"}:
        catalog_view = "visible"

    source_cp = plugin.build_client(source_settings, mask_secrets=mask_secrets)
    source_token = plugin.resolve_auth_token(source_cp, source_settings)
    source_catalog = _load_catalog(
        plugin,
        source_cp,
        source_token,
        source_settings,
        catalog_view=catalog_view,
    )

    target_cp = plugin.build_client(target_settings, mask_secrets=mask_secrets)
    target_token = plugin.resolve_auth_token(target_cp, target_settings)
    target_catalog = _load_catalog(
        plugin,
        target_cp,
        target_token,
        target_settings,
        catalog_view=catalog_view,
    )

    source_items = _fetch_source_items(
        source_cp, source_token, source_catalog, module, service, args
    )
    if not source_items:
        raise ValueError("No source objects matched the requested selector")

    diff_items: list[dict[str, Any]] = []
    symmetric_scope = bool(args.get("all")) or bool(args.get("filter"))

    if symmetric_scope:
        target_items = _fetch_source_items(
            target_cp, target_token, target_catalog, module, service, args
        )
        target_index, target_unmatched = _build_symmetric_index(target_items, match_by)

        for source_item in source_items:
            label = _copy_item_label(source_item)
            key, resolved_match = _match_key(source_item, match_by)
            source_normalized = _normalize_diff_item(
                plugin, module, service, source_item
            )

            if key is None:
                diff_items.append(
                    _diff_entry(
                        label=label,
                        match_by=resolved_match,
                        status="only_in_source",
                        source_item=source_item,
                        target_item=None,
                        source_normalized=source_normalized,
                    )
                )
                continue

            target_item = target_index.pop(key, None)
            if target_item is None:
                diff_items.append(
                    _diff_entry(
                        label=label,
                        match_by=resolved_match,
                        status="only_in_source",
                        source_item=source_item,
                        target_item=None,
                        source_normalized=source_normalized,
                    )
                )
                continue

            target_normalized = _normalize_diff_item(
                plugin, module, service, target_item
            )
            status = "same" if source_normalized == target_normalized else "different"
            diff_items.append(
                _diff_entry(
                    label=label,
                    match_by=resolved_match,
                    status=status,
                    source_item=source_item,
                    target_item=target_item,
                    source_normalized=source_normalized,
                    target_normalized=target_normalized,
                )
            )

        for target_item in [*target_unmatched, *target_index.values()]:
            label = _copy_item_label(target_item)
            _, resolved_match = _match_key(target_item, match_by)
            target_normalized = _normalize_diff_item(
                plugin, module, service, target_item
            )
            diff_items.append(
                _diff_entry(
                    label=label,
                    match_by=resolved_match,
                    status="only_in_target",
                    source_item=None,
                    target_item=target_item,
                    target_normalized=target_normalized,
                )
            )
    else:
        for source_item in source_items:
            label = _copy_item_label(source_item)
            target_match, resolved_match = _resolve_match(
                target_cp,
                target_token,
                target_catalog,
                module,
                service,
                source_item,
                match_by,
            )
            source_normalized = _normalize_diff_item(
                plugin, module, service, source_item
            )
            if target_match is None:
                diff_items.append(
                    _diff_entry(
                        label=label,
                        match_by=resolved_match,
                        status="only_in_source",
                        source_item=source_item,
                        target_item=None,
                        source_normalized=source_normalized,
                    )
                )
                continue

            target_normalized = _normalize_diff_item(
                plugin, module, service, target_match
            )
            status = "same" if source_normalized == target_normalized else "different"
            diff_items.append(
                _diff_entry(
                    label=label,
                    match_by=resolved_match,
                    status=status,
                    source_item=source_item,
                    target_item=target_match,
                    source_normalized=source_normalized,
                    target_normalized=target_normalized,
                )
            )

    summary = {
        "compared": sum(
            1 for item in diff_items if item["status"] in {"same", "different"}
        ),
        "only_in_source": sum(
            1 for item in diff_items if item["status"] == "only_in_source"
        ),
        "only_in_target": sum(
            1 for item in diff_items if item["status"] == "only_in_target"
        ),
        "different": sum(1 for item in diff_items if item["status"] == "different"),
        "same": sum(1 for item in diff_items if item["status"] == "same"),
    }

    artifact_timestamp = None
    out_path = str(args.get("out") or "").strip() or _default_artifact_path(
        active_settings,
        module,
        service,
        source_profile,
        target_profile,
        "diff",
        timestamp=artifact_timestamp,
    )
    report = {
        "mode": "diff",
        "module": module,
        "service": service,
        "source_profile": source_profile,
        "target_profile": target_profile,
        "match_by": match_by,
        "summary": summary,
        "items": diff_items,
        "artifacts": {"report": out_path},
    }

    write_value_to_file(
        report,
        out_path,
        data_format="json",
        mask_secrets=mask_secrets,
    )
    _emit_diff_summary(report)
    return report


__all__ = ["handle_diff_command"]
