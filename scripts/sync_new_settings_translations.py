#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "translations"
LOCALES_JS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "static" / "smart-plug-multilevel-light-locales.js"
POWER_BASELINE = "0d32c707f3d5ec45fa9009a07a98ab7d2cd8964c"
RAW_BASE = f"https://raw.githubusercontent.com/LanKing/ha-smart-plug-multilevel-light/{POWER_BASELINE}"

EN_LABEL = "Consecutive readings to switch"
EN_HELP = (
    "Number of consecutive one-second power samples that must map to the same new mode "
    "before the integration switches modes. State changes are sampled immediately as "
    "well. Until confirmation, the current mode is kept unchanged. Default is 5."
)
RU_LABEL = "Показаний подряд для переключения"
RU_HELP = (
    "Количество последовательных секундных замеров мощности, которые должны "
    "соответствовать одному и тому же новому режиму, прежде чем интеграция переключит "
    "режим. Изменения состояния также фиксируются сразу. До подтверждения текущий режим "
    "сохраняется без изменений. По умолчанию — 5."
)

EN_ROUND_LABEL = "Round brightness to 5% (may look nicer)"
EN_ROUND_HELP = (
    "Rounds calculated brightness to the nearest 5%. This can make displayed percentages "
    "look cleaner. Disabled by default."
)
RU_ROUND_LABEL = "Округлять яркость до 5% (может выглядеть аккуратнее)"
RU_ROUND_HELP = (
    "Округляет рассчитанную яркость до ближайших 5%. Это может сделать отображаемые "
    "проценты аккуратнее. По умолчанию выключено."
)

EN_MODES_HELP = (
    "For a new lamp, first teach the integration its brightness modes. Add a mode, enable "
    "that preset on the light fixture, and use the stable power test in the mode editor to "
    "measure and apply its power threshold."
)
RU_MODES_HELP = (
    "Для нового светильника сначала задайте режимы яркости. Добавьте режим, включите "
    "соответствующий пресет на светильнике и используйте тест стабильной мощности в "
    "редакторе режима, чтобы измерить и применить его порог мощности."
)

EN_FRONTEND = {
    "stable_power_prompt": "Please enable the preset on your light fixture and press",
    "test_stable_power": "Test stable power",
    "testing_wait": "Testing, wait",
    "measured_result": "Measured",
    "repeat_test": "Repeat test",
    "current_moment_power": "Current moment power",
    "last_measures_debug": "Last measures (debug)",
    "power_test_unavailable": "Power measurement is unavailable. Check the light and repeat the test.",
}
RU_FRONTEND = {
    "stable_power_prompt": "Включите нужный режим на светильнике и нажмите",
    "test_stable_power": "Проверить стабильную мощность",
    "testing_wait": "Проверка, подождите",
    "measured_result": "Измерено",
    "repeat_test": "Повторить тест",
    "current_moment_power": "Текущая мощность",
    "last_measures_debug": "Последние измерения (отладка)",
    "power_test_unavailable": "Не удалось измерить мощность. Проверьте светильник и повторите тест.",
}


def fetch_baseline(path: str) -> str:
    with urllib.request.urlopen(f"{RAW_BASE}/{path}") as response:
        return response.read().decode("utf-8")


def patch_step(step: dict, locale: str) -> None:
    data = step.setdefault("data", {})
    descriptions = step.setdefault("data_description", {})
    data["power_history_samples"] = RU_LABEL if locale == "ru" else EN_LABEL
    descriptions["power_history_samples"] = RU_HELP if locale == "ru" else EN_HELP
    data["round_brightness_to_5"] = RU_ROUND_LABEL if locale == "ru" else EN_ROUND_LABEL
    descriptions["round_brightness_to_5"] = RU_ROUND_HELP if locale == "ru" else EN_ROUND_HELP
    descriptions["modes"] = RU_MODES_HELP if locale == "ru" else EN_MODES_HELP


def js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def patch_frontend_locales(text: str, locales: list[str]) -> str:
    for locale in locales:
        values = RU_FRONTEND if locale == "ru" else EN_FRONTEND
        additions = "".join(f"{key}:{js_string(value)}," for key, value in values.items())
        pattern = re.compile(rf'(^\s*(?:"{re.escape(locale)}"|{re.escape(locale)}):\{{)', re.MULTILINE)
        text, count = pattern.subn(lambda match: match.group(1) + additions, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not patch frontend locale {locale}")
    return text


def main() -> None:
    files = sorted(TRANSLATIONS.glob("*.json"))
    if len(files) != 64:
        raise SystemExit(f"Expected 64 translation files, found {len(files)}")

    locales = [path.stem for path in files]
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
    locales_text = fetch_baseline(locales_relative)
    LOCALES_JS.write_text(
        patch_frontend_locales(locales_text, locales),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
