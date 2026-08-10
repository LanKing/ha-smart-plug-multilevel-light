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

    text = text.replace("version-0.8.0-blue", "version-0.9.3-blue")
    text = text.replace("Version 0.8.0", "Version 0.9.3")
    text = text.replace("?v=0.8.0", "?v=0.9.3")

    text = text.replace(
        "* Автоматически определяет текущий режим работы светильника по фактически измеренной мощности;",
        "* Переключает определённый режим только после нескольких последовательных показаний мощности, соответствующих одному и тому же новому режиму;",
    )
    text = text.replace(
        "* Использует нелинейную шкалу яркости с округлением до 5%, лучше отражающую различия между режимами;",
        "* Использует нелинейную шкалу яркости; округление рассчитанной яркости до 5% можно включать и отключать;",
    )

    text = text.replace(
        "   - **Power cycle delay** — пауза между отключением и повторной подачей питания; по умолчанию `0.7 s`;",
        "   - **Power cycle delay** — пауза между отключением и повторной подачей питания; по умолчанию `0.7 s`;\n"
        "   - **Consecutive readings to switch** — сколько последовательных показаний должны соответствовать одному новому режиму для переключения; по умолчанию `3`;\n"
        "   - **Round brightness to 5%** — округление рассчитанной яркости до 5%; по умолчанию включено;",
    )

    marker = "| **Power cycle delay** | пауза между выключением и повторным включением розетки | `0.7 s` |"
    if marker in text and "| **Consecutive readings to switch**" not in text:
        text = text.replace(
            marker,
            marker + "\n| **Consecutive readings to switch** | сколько последовательных показаний одного нового режима требуется для переключения | `3` |\n"
            "| **Round brightness to 5%** | округление рассчитанной яркости до ближайших 5% | включено |",
        )

    text = re.sub(
        r"Режим выбирается по правилу: используется максимальный настроенный порог, который меньше или равен измеренной мощности\..*?(?=\n## 🔌 Как определяется состояние)",
        "Каждое новое показание мощности отдельно сопоставляется с обычной пороговой логикой: используется максимальный настроенный порог, который меньше или равен этому показанию. Первый определённый режим принимается сразу. После этого интеграция сохраняет текущий режим и переключает его только тогда, когда последние **N** последовательных показаний все соответствуют одному и тому же другому режиму. **N** задаётся параметром **Consecutive readings to switch** и по умолчанию равно `3`. Если последовательность прерывается показанием другого режима, переключения не происходит.\n",
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"### Определяется неправильный режим\n\n.*?(?=\n### )",
        "### Определяется неправильный режим\n\nПроверьте атрибуты `power_history`, `power_history_modes` и `selected_power_mode`. `power_history` показывает последние показания мощности, `power_history_modes` — режим для каждого из них по настроенным порогам, а `selected_power_mode` — текущий зафиксированный режим. Для переключения последние N значений в `power_history_modes` должны быть одинаковыми и отличаться от текущего режима.\n",
        text,
        flags=re.DOTALL,
    )

    PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
