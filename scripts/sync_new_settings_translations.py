#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "translations"
LOCALES_JS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "static" / "smart-plug-multilevel-light-locales.js"
POWER_BASELINE = "0d32c707f3d5ec45fa9009a07a98ab7d2cd8964c"
RAW_BASE = f"https://raw.githubusercontent.com/LanKing/ha-smart-plug-multilevel-light/{POWER_BASELINE}"

EN_LABEL = "Consecutive readings to switch"
EN_HELP = (
    "Number of consecutive power readings that must map to the same new mode before "
    "the integration switches modes. Until then, the current mode is kept unchanged. "
    "Default is 3."
)
RU_LABEL = "Показаний подряд для переключения"
RU_HELP = (
    "Количество последовательных показаний мощности, которые должны соответствовать "
    "одному и тому же новому режиму, прежде чем интеграция переключит режим. До этого "
    "текущий режим сохраняется без изменений. По умолчанию — 3."
)


def fetch_baseline(path: str) -> str:
    with urllib.request.urlopen(f"{RAW_BASE}/{path}") as response:
        return response.read().decode("utf-8")


def patch_step(step: dict, locale: str) -> None:
    data = step.setdefault("data", {})
    descriptions = step.setdefault("data_description", {})
    data["power_history_samples"] = RU_LABEL if locale == "ru" else EN_LABEL
    descriptions["power_history_samples"] = RU_HELP if locale == "ru" else EN_HELP


def main() -> None:
    files = sorted(TRANSLATIONS.glob("*.json"))
    if len(files) != 64:
        raise SystemExit(f"Expected 64 translation files, found {len(files)}")

    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        doc = json.loads(fetch_baseline(relative))
        locale = path.stem
        patch_step(doc["config"]["step"]["settings"], locale)
        patch_step(doc["options"]["step"]["init"], locale)
        path.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    locales_relative = LOCALES_JS.relative_to(ROOT).as_posix()
    LOCALES_JS.write_text(fetch_baseline(locales_relative), encoding="utf-8")


if __name__ == "__main__":
    main()
