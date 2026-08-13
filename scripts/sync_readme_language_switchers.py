#!/usr/bin/env python3
"""Synchronize README language switchers without changing document bodies."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPOSITORY_URL = "https://github.com/LanKing/ha-smart-plug-multilevel-light"
DEFAULT_BRANCH = "main"

LANGUAGES = [
    "en", "uk", "ru", "af", "ar", "bg", "bn", "bs", "ca", "cs", "cy",
    "da", "de", "el", "eo", "es", "et", "eu", "fa", "fi", "fy", "fr",
    "ga", "gl", "gsw", "he", "hi", "hr", "hu", "hy", "id", "is", "it",
    "ja", "ka", "ko", "lb", "lt", "lv", "mk", "ml", "nb", "nl", "nn",
    "pl", "pt", "pt-BR", "ro", "sk", "sl", "sq", "sr", "sr-Latn", "sv",
    "ta", "te", "th", "tr", "ur", "vi", "zh-Hans", "zh-Hant",
]

PREFIXES = {
    "en": "🇺🇸", "uk": "🇺🇦", "ru": "ru", "af": "🇿🇦", "ar": "🇸🇦",
    "bg": "🇧🇬", "bn": "🇧🇩", "bs": "🇧🇦", "ca": "ca", "cs": "🇨🇿",
    "cy": "cy", "da": "🇩🇰", "de": "🇩🇪", "el": "🇬🇷", "eo": "eo",
    "es": "🇪🇸", "et": "🇪🇪", "eu": "eu", "fa": "🇮🇷", "fi": "🇫🇮",
    "fy": "fy", "fr": "🇫🇷", "ga": "🇮🇪", "gl": "gl", "gsw": "🇨🇭",
    "he": "🇮🇱", "hi": "🇮🇳", "hr": "🇭🇷", "hu": "🇭🇺", "hy": "🇦🇲",
    "id": "🇮🇩", "is": "🇮🇸", "it": "🇮🇹", "ja": "🇯🇵", "ka": "🇬🇪",
    "ko": "🇰🇷", "lb": "🇱🇺", "lt": "🇱🇹", "lv": "🇱🇻", "mk": "🇲🇰",
    "ml": "🇮🇳", "nb": "🇳🇴", "nl": "🇳🇱", "nn": "🇳🇴", "pl": "🇵🇱",
    "pt": "🇵🇹", "pt-BR": "🇧🇷", "ro": "🇷🇴", "sk": "🇸🇰",
    "sl": "🇸🇮", "sq": "🇦🇱", "sr": "🇷🇸", "sr-Latn": "🇷🇸",
    "sv": "🇸🇪", "ta": "🇮🇳", "te": "🇮🇳", "th": "🇹🇭", "tr": "🇹🇷",
    "ur": "🇵🇰", "vi": "🇻🇳", "zh-Hans": "🇨🇳", "zh-Hant": "🇹🇼",
}

LABELS = {
    "en": "E⁠n⁠g⁠l⁠i⁠s⁠h",
    "uk": "У⁠к⁠р⁠а⁠ї⁠н⁠с⁠ь⁠к⁠а",
    "ru": "Р⁠у⁠с⁠с⁠к⁠и⁠й",
    "af": "A⁠f⁠r⁠i⁠k⁠a⁠a⁠n⁠s",
    "ar": "ا⁠ل⁠ع⁠ر⁠ب⁠ي⁠ة",
    "bg": "Б⁠ъ⁠л⁠г⁠а⁠р⁠с⁠к⁠и",
    "bn": "বাং⁠লা",
    "bs": "B⁠o⁠s⁠a⁠n⁠s⁠k⁠i",
    "ca": "C⁠a⁠t⁠a⁠l⁠à",
    "cs": "Č⁠e⁠š⁠t⁠i⁠n⁠a",
    "cy": "C⁠y⁠m⁠r⁠a⁠e⁠g",
    "da": "D⁠a⁠n⁠s⁠k",
    "de": "D⁠e⁠u⁠t⁠s⁠c⁠h",
    "el": "Ε⁠λ⁠λ⁠η⁠ν⁠ι⁠κ⁠ά",
    "eo": "E⁠s⁠p⁠e⁠r⁠a⁠n⁠t⁠o",
    "es": "E⁠s⁠p⁠a⁠ñ⁠o⁠l",
    "et": "E⁠e⁠s⁠t⁠i",
    "eu": "E⁠u⁠s⁠k⁠a⁠r⁠a",
    "fa": "ف⁠ا⁠ر⁠س⁠ی",
    "fi": "S⁠u⁠o⁠m⁠i",
    "fy": "F⁠r⁠y⁠s⁠k",
    "fr": "F⁠r⁠a⁠n⁠ç⁠a⁠i⁠s",
    "ga": "G⁠a⁠e⁠i⁠l⁠g⁠e",
    "gl": "G⁠a⁠l⁠e⁠g⁠o",
    "gsw": "S⁠c⁠h⁠w⁠i⁠i⁠z⁠e⁠r⁠d⁠ü⁠t⁠s⁠c⁠h",
    "he": "ע⁠ב⁠ר⁠י⁠ת",
    "hi": "हि⁠न्दी",
    "hr": "H⁠r⁠v⁠a⁠t⁠s⁠k⁠i",
    "hu": "M⁠a⁠g⁠y⁠a⁠r",
    "hy": "Հ⁠ա⁠յ⁠ե⁠ր⁠ե⁠ն",
    "id": "I⁠n⁠d⁠o⁠n⁠e⁠s⁠i⁠a",
    "is": "Í⁠s⁠l⁠e⁠n⁠s⁠k⁠a",
    "it": "I⁠t⁠a⁠l⁠i⁠a⁠n⁠o",
    "ja": "日⁠本⁠語",
    "ka": "K⁠a⁠r⁠t⁠u⁠l⁠i",
    "ko": "한⁠국⁠어",
    "lb": "L⁠ë⁠t⁠z⁠e⁠b⁠u⁠e⁠r⁠g⁠e⁠s⁠c⁠h",
    "lt": "L⁠i⁠e⁠t⁠u⁠v⁠i⁠ų",
    "lv": "L⁠a⁠t⁠v⁠i⁠e⁠š⁠u",
    "mk": "М⁠а⁠к⁠е⁠д⁠о⁠н⁠с⁠к⁠и",
    "ml": "മ⁠ല⁠യാ⁠ളം",
    "nb": "N⁠o⁠r⁠s⁠k⁠&nbsp;⁠B⁠o⁠k⁠m⁠å⁠l",
    "nl": "N⁠e⁠d⁠e⁠r⁠l⁠a⁠n⁠d⁠s",
    "nn": "N⁠o⁠r⁠s⁠k⁠&nbsp;⁠N⁠y⁠n⁠o⁠r⁠s⁠k",
    "pl": "P⁠o⁠l⁠s⁠k⁠i",
    "pt": "P⁠o⁠r⁠t⁠u⁠g⁠u⁠ê⁠s",
    "pt-BR": "P⁠o⁠r⁠t⁠u⁠g⁠u⁠ê⁠s⁠&nbsp;⁠(⁠B⁠R⁠)",
    "ro": "R⁠o⁠m⁠â⁠n⁠ă",
    "sk": "S⁠l⁠o⁠v⁠e⁠n⁠č⁠i⁠n⁠a",
    "sl": "S⁠l⁠o⁠v⁠e⁠n⁠š⁠č⁠i⁠n⁠a",
    "sq": "S⁠h⁠q⁠i⁠p",
    "sr": "С⁠р⁠п⁠с⁠к⁠и",
    "sr-Latn": "S⁠r⁠p⁠s⁠k⁠i",
    "sv": "S⁠v⁠e⁠n⁠s⁠k⁠a",
    "ta": "த⁠மி⁠ழ்",
    "te": "తె⁠లు⁠గు",
    "th": "ภ⁠า⁠ษ⁠า⁠ไ⁠ท⁠ย",
    "tr": "T⁠ü⁠r⁠k⁠ç⁠e",
    "ur": "اُ⁠ر⁠دُ⁠و",
    "vi": "T⁠i⁠ế⁠n⁠g⁠&nbsp;⁠V⁠i⁠ệ⁠t",
    "zh-Hans": "简⁠体⁠中⁠文",
    "zh-Hant": "繁⁠體⁠中⁠文",
}

SWITCHER_RE = re.compile(r"^<sub>.*README.*</sub>$")


def href(current: str, target: str) -> str:
    if current == "en":
        return (
            f"{REPOSITORY_URL}/blob/{DEFAULT_BRANCH}/docs/"
            f"README_{target}.md"
        )
    if target == "en":
        return "../README.md"
    return f"README_{target}.md"


def switcher(current: str) -> str:
    items = []
    targets = [code for code in LANGUAGES if code != current]
    for index, target in enumerate(targets):
        suffix = "&nbsp;|" if index < len(targets) - 1 else ""
        items.append(
            f'<sub>{PREFIXES[target]}&nbsp;<a href="{href(current, target)}">'
            f"{LABELS[target]}</a>{suffix}</sub>"
        )
    return " ".join(items)


def current_language(path: Path) -> str:
    if path == ROOT / "README.md":
        return "en"
    match = re.fullmatch(r"README_(.+)\.md", path.name)
    if not match or match.group(1) not in LANGUAGES:
        raise ValueError(f"Unexpected README translation path: {path}")
    return match.group(1)


def update_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    lines = [line for line in lines if not SWITCHER_RE.fullmatch(line)]
    while lines and not lines[0].strip():
        lines.pop(0)
    updated = switcher(current_language(path)) + "\n\n" + "\n".join(lines).rstrip() + "\n"
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    paths = [ROOT / "README.md", *sorted(DOCS.glob("README_*.md"))]
    changed = [path for path in paths if update_file(path)]
    for path in changed:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
