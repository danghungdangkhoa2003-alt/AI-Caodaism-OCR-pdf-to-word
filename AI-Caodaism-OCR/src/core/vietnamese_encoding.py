"""Detection and conversion of legacy VNI-Windows Vietnamese text."""

from __future__ import annotations

import unicodedata

# Parallel VNI-Windows and Unicode tables.  Long source sequences are replaced
# through temporary tokens, preventing a replacement from corrupting the next.
_VNI = """AØ|AÙ|AÂ|AÕ|EØ|EÙ|EÂ|Ì|Í|OØ|OÙ|OÂ|OÕ|UØ|UÙ|YÙ|aø|aù|aâ|aõ|eø|eù|eâ|ì|í|oø|où|oâ|oõ|uø|uù|yù|AÊ|aê|Ñ|ñ|Ó|ó|UÕ|uõ|Ô|ô|Ö|ö|AÏ|aï|AÛ|aû|AÁ|aá|AÀ|aà|AÅ|aå|AÃ|aã|AÄ|aä|AÉ|aé|AÈ|aè|AÚ|aú|AÜ|aü|AË|aë|EÏ|eï|EÛ|eû|EÕ|eõ|EÁ|eá|EÀ|eà|EÅ|eå|EÃ|eã|EÄ|eä|Æ|æ|Ò|ò|OÏ|oï|OÛ|oû|OÁ|oá|OÀ|oà|OÅ|oå|OÃ|oã|OÄ|oä|ÔÙ|ôù|ÔØ|ôø|ÔÛ|ôû|ÔÕ|ôõ|ÔÏ|ôï|UÏ|uï|UÛ|uû|ÖÙ|öù|ÖØ|öø|ÖÛ|öû|ÖÕ|öõ|ÖÏ|öï|YØ|yø|Î|î|YÛ|yû|YÕ|yõ""".split("|")
_UNICODE = """À|Á|Â|Ã|È|É|Ê|Ì|Í|Ò|Ó|Ô|Õ|Ù|Ú|Ý|à|á|â|ã|è|é|ê|ì|í|ò|ó|ô|õ|ù|ú|ý|Ă|ă|Đ|đ|Ĩ|ĩ|Ũ|ũ|Ơ|ơ|Ư|ư|Ạ|ạ|Ả|ả|Ấ|ấ|Ầ|ầ|Ẩ|ẩ|Ẫ|ẫ|Ậ|ậ|Ắ|ắ|Ằ|ằ|Ẳ|ẳ|Ẵ|ẵ|Ặ|ặ|Ẹ|ẹ|Ẻ|ẻ|Ẽ|ẽ|Ế|ế|Ề|ề|Ể|ể|Ễ|ễ|Ệ|ệ|Ỉ|ỉ|Ị|ị|Ọ|ọ|Ỏ|ỏ|Ố|ố|Ồ|ồ|Ổ|ổ|Ỗ|ỗ|Ộ|ộ|Ớ|ớ|Ờ|ờ|Ở|ở|Ỡ|ỡ|Ợ|ợ|Ụ|ụ|Ủ|ủ|Ứ|ứ|Ừ|ừ|Ử|ử|Ữ|ữ|Ự|ự|Ỳ|ỳ|Ỵ|ỵ|Ỷ|ỷ|Ỹ|ỹ""".split("|")
_TABLE = tuple(zip(_VNI, _UNICODE, strict=True))
_MULTI_CHARACTER_MARKERS = tuple(source for source, _ in _TABLE if len(source) > 1)


def is_vni_windows(text: str) -> bool:
    """Return true only for strong multi-character VNI evidence.

    Single characters such as ``ô`` occur in valid Unicode too, so converting
    them without a VNI marker would damage already-correct text.
    """
    return any(marker in text for marker in _MULTI_CHARACTER_MARKERS)


def to_unicode(text: str) -> str:
    """Convert a VNI-Windows block to NFC Unicode; leave Unicode blocks intact."""
    if not is_vni_windows(text):
        return unicodedata.normalize("NFC", text)
    for index, (source, _) in enumerate(_TABLE):
        text = text.replace(source, f"\uFFF0{index}\uFFF1")
    for index, (_, target) in enumerate(_TABLE):
        text = text.replace(f"\uFFF0{index}\uFFF1", target)
    # VNI represents horn vowels plus tones with separate sequences.
    final_replacements = {
        "ơø": "ờ", "ơù": "ớ", "ơû": "ở", "ơï": "ợ", "ơõ": "ỡ",
        "ưù": "ứ", "ưø": "ừ", "ưû": "ử", "ưõ": "ữ", "ưï": "ự",
        "ƠÏ": "Ợ", "ƯÙ": "Ứ",
    }
    for source, target in final_replacements.items():
        text = text.replace(source, target)
    return unicodedata.normalize("NFC", text)
