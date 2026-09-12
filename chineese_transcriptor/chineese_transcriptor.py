import re
import unicodedata


# --------------------------------------------------
# ИНИЦИАЛИ
# --------------------------------------------------

INITIALS = {
    "zh": "дж",
    "ch": "ч", # с выдыхом, тч
    "sh": "ш",

    "b": "б",
    "p": "п",
    "m": "м",
    "f": "ф",

    "d": "д",
    "t": "т", # с выдыхом, очень легкое т
    "n": "н",
    "l": "л",

    "g": "г",
    "k": "к",
    "h": "х",

    "j": "ть",
    "q": "чь",
    "x": "шь",

    "r": "ж",

    "z": "дз",
    "c": "ц", # с выдыхом, тс
    "s": "с",

    "y": "j",
    "w": "у"
}

SPECIAL_I = {
    "zh", "ch", "sh",
    "r",
    "z", "c", "s"
}

INITIALS_BEFORE_I = {
    "j": "ть",
    "q": "тсь",
    "x": "сь",
}

INITIAL_KEYS = sorted(INITIALS.keys(), key=len, reverse=True)

# --------------------------------------------------
# ФИНАЛИ
# --------------------------------------------------

FINALS = {

    "iang": "иаң", 
    "iong": "иоң",
    "uang": "уаң",
    "ueng": "уэң",

    "iao": "иау",
    "ian": "иэн",
    "ing": "иң",

    "uan": "уан",
    "ong": "оң",

    "ang": "аң",
    "eng": "(ыэ)ң", # (ыэ) звук между ы и э

    "iu": "иу",
    "ie": "иэ",
    "ia": "иа",

    "ua": "уа",
    "uo": "уо",
    "ui": "уэj",
    "uai": "уаj",

    "üe": "ӱэ",
    "üan": "ӱэн",
    "ün": "ӱин",

    # После j, q, x буква ü записывается без точек: ju, jue, juan, jun.
    "ue": "юэ",

    "ai": "аj",
    "ei": "эj",
    "ao": "ао",
    "ou": "оу",

    "an": "ан",
    "en": "эн",
    "in": "ин",
    "un": "уэн",

    "er": "ӭ", # как er в слове teacher

    "a": "а",
    "o": "о",
    "e": "(ыэ)", # звук между ы и э
    "i": "и",
    "u": "у",
    "ü": "ю",
}

FINAL_KEYS = sorted(FINALS.keys(), key=len, reverse=True)

# --------------------------------------------------
# ТОНЫ
# --------------------------------------------------

TONE_MAP = {
    "ā": ("a", 1), "á": ("a", 2), "ǎ": ("a", 3), "à": ("a", 4),
    "ē": ("e", 1), "é": ("e", 2), "ě": ("e", 3), "è": ("e", 4),
    "ī": ("i", 1), "í": ("i", 2), "ǐ": ("i", 3), "ì": ("i", 4),
    "ō": ("o", 1), "ó": ("o", 2), "ǒ": ("o", 3), "ò": ("o", 4),
    "ū": ("u", 1), "ú": ("u", 2), "ǔ": ("u", 3), "ù": ("u", 4),
    "ǖ": ("ü", 1), "ǘ": ("ü", 2), "ǚ": ("ü", 3), "ǜ": ("ü", 4),
}

COMBINING = {
    1: "\u0304",
    2: "\u0301",
    3: "\u030C",
    4: "\u0300",
}

VOWELS = "аеёиоуыэюя"

# --------------------------------------------------
# ОСОБЫЕ Y/W
# --------------------------------------------------

SPECIAL = {

    "yi": "и",
    "ya": "jа",
    "yao": "jау",
    "ye": "jэ",
    "you": "jоу",
    "yan": "jен",
    "yang": "jаң",
    "yin": "jин",
    "ying": "jң",
    "yong": "jоң",

    "wu": "у",
    "wa": "уа",
    "wo": "уо",
    "wei": "уэj",
    "wai": "уаj",
    "wan": "уан",
    "wen": "уэн",
    "wang": "уаң",
    "weng": "уэң",

    "yu": "ӱ",
    "yue": "ӱэ",
    "yuan": "ӱэн",
    "yun": "ӱин"
}

# --------------------------------------------------
# ПРЕОБРАЗОВАНИЕ ОДНОГО СЛОГА
# --------------------------------------------------

def remove_tone(word):
    tone = 0
    result = ""

    for ch in word:
        if ch in TONE_MAP:
            base, tone = TONE_MAP[ch]
            result += base
        else:
            result += ch

    return result, tone


def apply_tone(word, tone):
    if tone == 0:
        return word

    chars = list(word)

    for i, ch in enumerate(chars):
        if ch in VOWELS:
            chars[i] += COMBINING[tone]
            break

    return unicodedata.normalize("NFC", "".join(chars))


def split_initial(word):
    for ini in INITIAL_KEYS:
        if word.startswith(ini):
            return ini, word[len(ini):]

    return "", word


def apply_special_i(initial, final):
    if initial in SPECIAL_I and final == "i":
        return "ы"

    return FINALS.get(final, final)


def convert_syllable(word):
    word, tone = remove_tone(word)

    if word in SPECIAL:
        return apply_tone(SPECIAL[word], tone)

    initial, final = split_initial(word)
    if initial in INITIALS_BEFORE_I and final.startswith("i"):
        ru_initial = INITIALS_BEFORE_I[initial]
    else:
        ru_initial = INITIALS.get(initial, "")

    ru_final = apply_special_i(initial, final)
    result = ru_initial + ru_final

    return apply_tone(result, tone)


# Непрерывная последовательность пиньиня может содержать несколько слогов
# (duibuqi, xiexie, zaijian). Набор покрывает все сочетания инициалей и
# финалей из таблицы; динамическое разбиение предпочитает длинные слоги.
VALID_SYLLABLES = set(SPECIAL)
VALID_SYLLABLES.update(FINALS)
VALID_SYLLABLES.update(
    initial + final
    for initial in INITIALS
    for final in FINALS
)
MAX_SYLLABLE_LENGTH = max(map(len, VALID_SYLLABLES))


def split_into_syllables(word):
    plain_word, _ = remove_tone(word.lower())
    paths = {len(word): []}

    for start in range(len(word) - 1, -1, -1):
        max_end = min(len(word), start + MAX_SYLLABLE_LENGTH)

        for end in range(max_end, start, -1):
            if plain_word[start:end] in VALID_SYLLABLES and end in paths:
                paths[start] = [word[start:end], *paths[end]]
                break

    return paths.get(0, [word])


def convert_word(word):
    return " ".join(convert_syllable(part) for part in split_into_syllables(word))


# --------------------------------------------------
# ЧТЕНИЕ TXT
# --------------------------------------------------

PINYIN_PATTERN = re.compile(
    r"[A-Za-züÜāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+"
)

transcribed_lines = []
transcribed_count = 0

with open("pinyin.txt", "r", encoding="utf-8") as f:
    for line in f:
        def replace_syllable(match):
            global transcribed_count
            syllables = split_into_syllables(match.group())
            transcribed_count += len(syllables)
            return " ".join(
                convert_syllable(syllable.lower()) for syllable in syllables
            )

        transcribed_lines.append(PINYIN_PATTERN.sub(replace_syllable, line))

# --------------------------------------------------
# ЗАПИСЬ В TXT
# --------------------------------------------------

with open("pinyin_to_ru.txt", "w", encoding="utf-8") as f:
    f.writelines(transcribed_lines)

print(f"Готово. Транскрибировано {transcribed_count} слогов.")
