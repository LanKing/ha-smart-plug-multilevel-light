#!/usr/bin/env python3
"""Generate localized README files from the protected Russian source.

This script is intended for the dedicated GitHub Actions workflow. It never writes
or stages docs/README_ru.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "README_ru.md"
TRANSLATIONS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "translations"
FRONTEND_LOCALES = (
    ROOT
    / "custom_components"
    / "smart_plug_multilevel_light"
    / "static"
    / "smart-plug-multilevel-light-locales.js"
)

LANGUAGES = [
    ("uk", "uk", "Ukrainian"),
    ("af", "af", "Afrikaans"),
    ("ar", "ar", "Arabic"),
    ("bg", "bg", "Bulgarian"),
    ("bn", "bn", "Bengali"),
    ("bs", "bs", "Bosnian"),
    ("ca", "ca", "Catalan"),
    ("cs", "cs", "Czech"),
    ("cy", "cy", "Welsh"),
    ("da", "da", "Danish"),
    ("de", "de", "German"),
    ("el", "el", "Greek"),
    ("eo", "eo", "Esperanto"),
    ("es", "es", "Spanish"),
    ("et", "et", "Estonian"),
    ("eu", "eu", "Basque"),
    ("fa", "fa", "Persian"),
    ("fi", "fi", "Finnish"),
    ("fy", "fy", "Frisian"),
    ("fr", "fr", "French"),
    ("ga", "ga", "Irish"),
    ("gl", "gl", "Galician"),
    ("gsw", "gsw", "Swiss German"),
    ("he", "he", "Hebrew"),
    ("hi", "hi", "Hindi"),
    ("hr", "hr", "Croatian"),
    ("hu", "hu", "Hungarian"),
    ("hy", "hy", "Armenian"),
    ("id", "id", "Indonesian"),
    ("is", "is", "Icelandic"),
    ("it", "it", "Italian"),
    ("ja", "ja", "Japanese"),
    ("ka", "ka", "Georgian"),
    ("ko", "ko", "Korean"),
    ("lb", "lb", "Luxembourgish"),
    ("lt", "lt", "Lithuanian"),
    ("lv", "lv", "Latvian"),
    ("mk", "mk", "Macedonian"),
    ("ml", "ml", "Malayalam"),
    ("nb", "no", "Norwegian Bokmål"),
    ("nl", "nl", "Dutch"),
    ("nn", "nn", "Norwegian Nynorsk"),
    ("pl", "pl", "Polish"),
    ("pt", "pt", "Portuguese"),
    ("pt-BR", "pt", "Brazilian Portuguese"),
    ("ro", "ro", "Romanian"),
    ("sk", "sk", "Slovak"),
    ("sl", "sl", "Slovenian"),
    ("sq", "sq", "Albanian"),
    ("sr", "sr", "Serbian"),
    ("sr-Latn", "sr-Latn", "Serbian Latin"),
    ("sv", "sv", "Swedish"),
    ("ta", "ta", "Tamil"),
    ("te", "te", "Telugu"),
    ("th", "th", "Thai"),
    ("tr", "tr", "Turkish"),
    ("ur", "ur", "Urdu"),
    ("vi", "vi", "Vietnamese"),
    ("zh-Hans", "zh-CN", "Simplified Chinese"),
    ("zh-Hant", "zh-TW", "Traditional Chinese"),
]

CONFIG_UI = {
    "Название светильника": ("name", "Light name"),
    "Датчик мощности": ("power_sensor", "Power sensor"),
    "🔅 Режимы яркости": ("modes", "🔅 Brightness modes"),
    "Округлять яркость до 5% (может выглядеть аккуратнее)": (
        "round_brightness_to_5",
        "Round brightness to 5% (may look nicer)",
    ),
    "Показаний подряд для переключения": (
        "power_history_samples",
        "Consecutive readings to switch",
    ),
}

FRONTEND_UI = {
    "Проверить стабильную мощность": ("test_stable_power", "Test stable power"),
    "🐞 Последние измерения": ("last_measures_debug", "🐞 Last measures"),
    "Содержимое": ("content", "Content"),
    "Взаимодействия": ("interactions", "Interactions"),
    "Показывать название режима": ("show_mode", "Show mode name"),
    "Показывать процент": ("show_percentage", "Show percentage"),
    "Всегда показывать фон иконки": (
        "always_icon_bg",
        "Always show icon background",
    ),
}

SUMMARY_RE = re.compile(r"^<summary><b>(.*?)</b></summary>$", re.MULTILINE)
HASH_RE = re.compile(r"^<!-- markdown-translator:[a-f0-9]{64} -->\n")


def run(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd or ROOT, check=True)


def load_switcher_module():
    path = ROOT / "scripts" / "sync_readme_language_switchers.py"
    spec = importlib.util.spec_from_file_location("readme_switchers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load language switcher module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frontend_values(locale: str) -> dict[str, str]:
    text = FRONTEND_LOCALES.read_text(encoding="utf-8")
    candidates = (f"{locale}:{{", f'"{locale}":{{')
    start = next((text.find(marker) for marker in candidates if text.find(marker) >= 0), -1)
    if start < 0:
        raise RuntimeError(f"Frontend locale not found: {locale}")
    end = text.find("},", start)
    block = text[start:end]
    values: dict[str, str] = {}
    for key, encoded in re.findall(r'(\w+):("(?:\\.|[^"])*")', block):
        values[key] = json.loads(encoded)
    return values


def localized_ui(locale: str) -> dict[str, str]:
    config = json.loads((TRANSLATIONS / f"{locale}.json").read_text(encoding="utf-8"))
    data = config["config"]["step"]["settings"]["data"]
    frontend = frontend_values(locale)
    replacements: dict[str, str] = {}

    for source, (key, english) in CONFIG_UI.items():
        value = str(data[key])
        replacements[source] = english if value == english else f"{value} ({english})"

    for source, (key, english) in FRONTEND_UI.items():
        value = frontend[key]
        replacements[source] = english if value == english else f"{value} ({english})"

    return replacements


def prepare_source(locale: str) -> tuple[str, dict[str, str]]:
    text = SOURCE.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].startswith("<sub>"):
        lines = lines[2:]
    text = "\n".join(lines).rstrip() + "\n"

    # Raw HTML summary text is not visited by the Markdown translator.
    text = SUMMARY_RE.sub(lambda match: f"### {match.group(1)}", text)

    placeholders: dict[str, str] = {}
    for index, (source, target) in enumerate(localized_ui(locale).items(), start=1):
        token = f"XQZUI{index:03d}XQZ"
        text = text.replace(source, token)
        placeholders[token] = target

    return text, placeholders


def finalize(
    translated: str,
    locale: str,
    placeholders: dict[str, str],
    switchers,
) -> str:
    text = HASH_RE.sub("", translated)
    for token, value in placeholders.items():
        text = text.replace(token, value)

    text = re.sub(
        r"^### (❓.*?)$",
        lambda match: f"<summary><b>{match.group(1)}</b></summary>",
        text,
        flags=re.MULTILINE,
    )
    text = text.replace(
        "/docs/README_ru.md",
        f"/docs/README_{locale}.md",
    )
    text = text.replace("README_RU.md", f"README_{locale}.md")
    text = switchers.switcher(locale) + "\n\n" + text.lstrip()
    if "&#8288;" in text:
        raise RuntimeError(f"HTML WORD JOINER entity found in {locale}")
    if f"README_{locale}.md\">" in text.splitlines()[0]:
        raise RuntimeError(f"Current language remains in switcher: {locale}")
    return text.rstrip() + "\n"


def translate_one(
    locale: str,
    provider_locale: str,
    language_name: str,
    translator_dir: Path,
    overwrite: bool,
    switchers,
) -> None:
    target = ROOT / "docs" / f"README_{locale}.md"
    if target.exists() and not overwrite:
        print(f"Skipping existing {target.relative_to(ROOT)}")
        return

    source_text, placeholders = prepare_source(locale)
    translator_source = translator_dir / "readme-translation-source.md"
    translator_source.write_text(source_text, encoding="utf-8")
    translated_path = translator_dir / f"readme-translation-source.{provider_locale}.md"
    translated_path.unlink(missing_ok=True)

    run(
        "npm",
        "start",
        "--",
        f"--lang={provider_locale}",
        "--files=readme-translation-source.md",
        "--incremental=false",
        cwd=translator_dir,
    )
    if not translated_path.exists():
        raise RuntimeError(f"Translator did not create {translated_path}")

    translated = translated_path.read_text(encoding="utf-8")
    target.write_text(
        finalize(translated, locale, placeholders, switchers),
        encoding="utf-8",
    )

    run("git", "add", str(target.relative_to(ROOT)))
    run("git", "commit", "-m", f"Add {language_name} README translation")
    run("git", "pull", "--rebase", "origin", "main")
    run("git", "push", "origin", "HEAD:main")
    translated_path.unlink(missing_ok=True)
    time.sleep(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--translator-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    switchers = load_switcher_module()
    run("git", "config", "user.name", "github-actions[bot]")
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )

    for locale, provider_locale, language_name in LANGUAGES:
        translate_one(
            locale,
            provider_locale,
            language_name,
            args.translator_dir.resolve(),
            args.overwrite,
            switchers,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
