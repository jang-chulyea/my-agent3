import re


PARTICLE_SUFFIXES = [
    "\uc73c\ub85c",
    "\uc5d0\uc11c",
    "\uc5d0\uac8c",
    "\uae4c\uc9c0",
    "\ubd80\ud130",
    "\ucc98\ub7fc",
    "\ubcf4\ub2e4",
    "\ud558\uace0",
    "\uc774\uba70",
    "\uc774\ub2e4",
    "\uc774",
    "\uac00",
    "\uc740",
    "\ub294",
    "\uc744",
    "\ub97c",
    "\uc758",
    "\uc640",
    "\uacfc",
    "\ub3c4",
    "\ub85c",
    "\ub9cc",
]


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    return re.sub(r"\s+", " ", lowered)


def normalize_token(token: str) -> str:
    normalized = normalize_text(token)
    for suffix in PARTICLE_SUFFIXES:
        if normalized.endswith(suffix) and len(normalized) > len(suffix):
            return normalized[: -len(suffix)]
    return normalized
