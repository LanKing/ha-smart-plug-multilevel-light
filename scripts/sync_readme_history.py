#!/usr/bin/env python3
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "README_RU.md"
POWER_BASELINE = "0d32c707f3d5ec45fa9009a07a98ab7d2cd8964c"
BASE_URL = f"https://raw.githubusercontent.com/LanKing/ha-smart-plug-multilevel-light/{POWER_BASELINE}/README_RU.md"


def main() -> None:
    with urllib.request.urlopen(BASE_URL) as response:
        text = response.read().decode("utf-8")

    text = text.replace("version-0.6.4-blue", "version-0.9.2-blue")
    text = text.replace("Version 0.6.4", "Version 0.9.2")
    text = text.replace("?v=0.6.4", "?v=0.9.2")

    text = text.replace(
        "* Автоматически определяет текущий режим работы светильника по фактически измеренной мощности;",
        "* Фиксирует последние показания мощности, сопоставляет каждое с порогом режима и выбирает режим, который встречался в окне чаще всего;",
    )
    text = text.replace(
        "* Использует нелинейную шкалу яркости с округлением до 5%, лучше отражающую различия между режимами;",
        "* Использует нелинейную шкалу яркости; округление рассчитанной яркости до 5% можно включать и отключать;",
    )

    text = text.replace(
        "   - **Power cycle delay** — пауза между отключением и повторной подачей питания; по умолчанию `0.7 s`;",
        "   - **Power cycle delay** — пауза между отключением и повторной подачей питания; по умолчанию `0.7 s`;\n"
        "   - **Recent power readings** — количество последних показаний мощности, используемых для выбора режима; по умолчанию `5`;\n"
        "   - **Round brightness to 5%** — округление рассчитанной яркости до 5%; по умолчанию включено;",
    )

    marker = "| **Power cycle delay** | пауза между выключением и повторным включением розетки | `0.7 s` |"
    if marker in text and "| **Recent power readings**" not in text:
        text = text.replace(
            marker,
            marker + "\n| **Recent power readings** | количество последних показаний мощности для выбора режима | `5` |\n"
            "| **Round brightness to 5%** | округление рассчитанной яркости до ближайших 5% | включено |",
        )

    text = re.sub(
        r"Режим выбирается по правилу: используется максимальный настроенный порог, который меньше или равен измеренной мощности\..*?(?=\n## 🔌 Как определяется состояние)",
        "Для определения режима интеграция хранит последние **N** показаний мощности, где **N** задаётся параметром **Recent power readings** и по умолчанию равно `5`. Каждое показание отдельно сопоставляется с обычной пороговой логикой: используется максимальный настроенный порог, который меньше или равен этому показанию. Затем выбирается режим, встретившийся в окне чаще всего. Если несколько режимов встречались одинаковое количество раз, используется режим самого свежего из этих показаний. Поэтому колебания мощности внутри диапазона одного режима не дробят голоса между отдельными значениями мощности.\n",
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"### Определяется неправильный режим\n\n.*?(?=\n### )",
        "### Определяется неправильный режим\n\nПроверьте атрибуты `power_history`, `power_history_modes` и `selected_power_mode`. В `power_history` находятся последние показания мощности, в `power_history_modes` — режим, полученный для каждого показания по настроенным порогам, а `selected_power_mode` показывает победивший режим.\n",
        text,
        flags=re.DOTALL,
    )

    PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
