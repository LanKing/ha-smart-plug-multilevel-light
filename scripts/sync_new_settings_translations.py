#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "translations"

EN_LABEL = "Recent current readings"
EN_HELP = (
    "Number of latest current readings used to determine the mode. Readings that do not "
    "exactly match a configured mode value are ignored; among the remaining readings, "
    "the most frequent value wins. Default is 5."
)
RU_LABEL = "Последние показания тока"
RU_HELP = (
    "Количество последних показаний тока, используемых для определения режима. "
    "Показания, которые точно не совпадают с настроенным значением режима, отбрасываются; "
    "среди оставшихся выбирается значение, встретившееся чаще всего. По умолчанию — 5."
)


def patch_step(step: dict, locale: str) -> None:
    data = step.setdefault("data", {})
    descriptions = step.setdefault("data_description", {})

    data.pop("off_current_threshold", None)
    descriptions.pop("off_current_threshold", None)
    data.pop("current_stability_samples", None)
    descriptions.pop("current_stability_samples", None)

    label = RU_LABEL if locale == "ru" else EN_LABEL
    helper = RU_HELP if locale == "ru" else EN_HELP
    data["current_history_samples"] = label
    descriptions["current_history_samples"] = helper


def main() -> None:
    files = sorted(TRANSLATIONS.glob("*.json"))
    if len(files) != 64:
        raise SystemExit(f"Expected 64 translation files, found {len(files)}")

    for path in files:
        locale = path.stem
        doc = json.loads(path.read_text(encoding="utf-8"))
        patch_step(doc["config"]["step"]["settings"], locale)
        patch_step(doc["options"]["step"]["init"], locale)
        path.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
