#!/usr/bin/env python3
"""Generate localized README files from the protected Russian source.

This script is intended for the dedicated GitHub Actions workflow. It never writes
or stages docs/README_ru.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from difflib import SequenceMatcher
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
    ("gsw", "de", "Swiss German"),
    ("he", "iw", "Hebrew"),
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
    ("nn", "no", "Norwegian Nynorsk"),
    ("pl", "pl", "Polish"),
    ("pt", "pt", "Portuguese"),
    ("pt-BR", "pt", "Brazilian Portuguese"),
    ("ro", "ro", "Romanian"),
    ("sk", "sk", "Slovak"),
    ("sl", "sl", "Slovenian"),
    ("sq", "sq", "Albanian"),
    ("sr", "sr", "Serbian"),
    ("sr-Latn", "sr", "Serbian Latin"),
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
HASH_RE = re.compile(r"^<!-- markdown-translator:[a-f0-9]{64} -->\\n")

PROTECTED_LITERALS = (
    "[!TIP]",
    "Smart Plug Multi-Level Light",
    "Home Assistant",
    "Zigbee2MQTT",
    "HACS",
    "Z2M",
    "MIT",
    "MDI",
)


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
    index = 1
    for source, target in localized_ui(locale).items():
        token = f"XQZUI{index:03d}XQZ"
        protected = f"`{token}`"
        text = text.replace(source, protected)
        placeholders[protected] = target
        index += 1

    for literal in PROTECTED_LITERALS:
        token = f"XQZTECH{index:03d}XQZ"
        protected = f"`{token}`"
        text = text.replace(literal, protected)
        placeholders[protected] = literal
        index += 1

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

    text = text.replace("\\&", "&")
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



def plain_for_qa(text: str) -> str:
    """Reduce Markdown to comparable prose for round-trip quality checks."""
    text = HASH_RE.sub("", text)
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[#*_>\u0060~|=-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def qa_chunks(text: str, limit: int = 3500) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    length = 0
    for word in words:
        extra = len(word) + (1 if current else 0)
        if current and length + extra > limit:
            chunks.append(" ".join(current))
            current = []
            length = 0
        current.append(word)
        length += extra
    if current:
        chunks.append(" ".join(current))
    return chunks


def protected_signature(text: str) -> dict[str, object]:
    text = HASH_RE.sub("", text).replace("\\&", "&")
    number_text = re.sub(r"https?://[^\s)>\"\']+", "", text)
    numbers = sorted(
        value.replace(",", ".")
        for value in re.findall(r"(?<!\w)\d+(?:[.,]\d+)?%?", number_text)
    )
    return {
        "URLs": sorted(re.findall(r"https?://[^\s)>\"']+", text)),
        "inline code": sorted(re.findall(r"\u0060([^\u0060\n]+)\u0060", text)),
        "numbers": numbers,
        "code fences": text.count("```"),
        "headings": len(re.findall(r"^#{1,6}\s", text, re.MULTILINE)),
        "details blocks": text.count("<details>"),
    }


def record_round_trip_quality(
    locale: str,
    source: str,
    translated: str,
    back_translated: str,
) -> None:
    source_plain = plain_for_qa(source)
    back_plain = plain_for_qa(back_translated)
    similarity = SequenceMatcher(None, source_plain, back_plain).ratio()

    source_signature = protected_signature(source)
    translated_signature = protected_signature(translated)
    critical = [
        label
        for label in source_signature
        if source_signature[label] != translated_signature[label]
    ]
    severity = "critical" if critical else ("review" if similarity < 0.30 else "passed")
    message = (
        f"README translation QA {locale}: {severity}; "
        f"round-trip similarity {similarity:.1%}"
    )
    if critical:
        message += f"; protected content differs: {', '.join(critical)}"
    print(message)
    if severity != "passed":
        print(f"::warning title=README translation QA ({locale})::{message}")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        path = Path(summary_path)
        if not path.exists() or path.stat().st_size == 0:
            path.write_text(
                "## README round-trip translation QA\n\n"
                "| Locale | Result | Similarity | Protected differences |\n"
                "|---|---:|---:|---|\n",
                encoding="utf-8",
            )
        with path.open("a", encoding="utf-8") as summary:
            summary.write(
                f"| {locale} | {severity} | {similarity:.1%} | "
                f"{', '.join(critical) if critical else '—'} |\n"
            )


def run_round_trip_qa(
    locale: str,
    source: str,
    translated: str,
    translator_dir: Path,
) -> None:
    qa_source = translator_dir / "readme-backtranslation-source.md"
    qa_source.write_text(
        "\n\n".join(qa_chunks(plain_for_qa(translated))) + "\n",
        encoding="utf-8",
    )
    qa_result = translator_dir / "readme-backtranslation-source.ru.md"
    qa_result.unlink(missing_ok=True)
    run(
        "npm",
        "start",
        "--",
        "--lang=ru",
        "--files=readme-backtranslation-source.md",
        "--incremental=false",
        "--commit=false",
        "--push=false",
        cwd=translator_dir,
    )
    if not qa_result.exists():
        raise RuntimeError(f"Back translator did not create {qa_result}")
    back_translated = HASH_RE.sub("", qa_result.read_text(encoding="utf-8"))
    record_round_trip_quality(locale, source, translated, back_translated)
    qa_result.unlink(missing_ok=True)


BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*")
LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\([^)]+\)")


def validate_inline_spacing(text: str, locale: str) -> None:
    """Reject Markdown nodes glued to surrounding prose."""
    issues: list[str] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("<sub>"):
            continue
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for match in BOLD_RE.finditer(line):
            before = line[match.start() - 1] if match.start() else ""
            after = line[match.end()] if match.end() < len(line) else ""
            if before and before.isalnum():
                issues.append(f"line {number}: missing space before bold text")
            if after and after.isalnum():
                issues.append(f"line {number}: missing space after bold text")

        for match in LINK_RE.finditer(line):
            before = line[match.start() - 1] if match.start() else ""
            if before and not before.isspace() and before not in "([{<":
                issues.append(f"line {number}: missing space before link")

    if "[!TIP]" not in text or "> [!TIP]" not in text:
        issues.append("TIP callout marker was changed")
    if "[MIT](https://github.com/LanKing/ha-smart-plug-multilevel-light/blob/main/LICENSE)" not in text:
        issues.append("MIT license label or link was changed")
    for literal in ("Home Assistant", "HACS", "Zigbee2MQTT", "Smart Plug Multi-Level Light"):
        if literal not in text:
            issues.append(f"protected name is missing: {literal}")

    if issues:
        preview = "; ".join(issues[:10])
        raise RuntimeError(f"Translated README validation failed for {locale}: {preview}")

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
        "--commit=false",
        "--push=false",
        cwd=translator_dir,
    )
    if not translated_path.exists():
        raise RuntimeError(f"Translator did not create {translated_path}")

    translated = translated_path.read_text(encoding="utf-8")
    run_round_trip_qa(locale, source_text, translated, translator_dir)
    finalized = finalize(translated, locale, placeholders, switchers)
    validate_inline_spacing(finalized, locale)
    target.write_text(finalized, encoding="utf-8")

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
    parser.add_argument("--locale", action="append", dest="locales")
    args = parser.parse_args()

    switchers = load_switcher_module()
    run("git", "config", "user.name", "github-actions[bot]")
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )

    selected = set(args.locales or [])
    known = {locale for locale, _, _ in LANGUAGES}
    unknown = selected - known
    if unknown:
        raise SystemExit(f"Unknown README locales: {sorted(unknown)}")

    for locale, provider_locale, language_name in LANGUAGES:
        if selected and locale not in selected:
            continue
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
