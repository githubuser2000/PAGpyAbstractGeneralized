#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Angular Vector-Currency Economy / Winkelwährungswirtschaft
==========================================================

PyPy3-compatible simulation with colorful terminal output, random EU country selection by seed, multilingual script output, and a large UTF-8 art gallery at the end.

Core rule: EA, EB and EC are all Euro vectors with identical vector length.
They compete by angle, not by numerical exchange-rate length.
"""

import argparse
import csv
import math
import random
import shutil
import sys
import textwrap
import zipfile
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

# -----------------------------------------------------------------------------
# 1. Terminal colors and output helpers
# -----------------------------------------------------------------------------

class Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"

COLOR_ON = True
WRAP_WIDTH = 118


def strip_ansi(s: object) -> str:
    s = str(s)
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\033" and i + 1 < len(s) and s[i + 1] == "[":
            i += 2
            while i < len(s) and s[i] != "m":
                i += 1
            if i < len(s):
                i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def col(text: object, code: str) -> str:
    if not COLOR_ON:
        return str(text)
    return code + str(text) + Ansi.RESET


def bold(text: object) -> str:
    return col(text, Ansi.BOLD)


def dim(text: object) -> str:
    return col(text, Ansi.DIM)


def rainbow(text: str) -> str:
    if not COLOR_ON:
        return text
    palette = [Ansi.BRIGHT_RED, Ansi.BRIGHT_YELLOW, Ansi.BRIGHT_GREEN,
               Ansi.BRIGHT_CYAN, Ansi.BRIGHT_BLUE, Ansi.BRIGHT_MAGENTA]
    out = []
    j = 0
    for ch in text:
        if ch.isspace():
            out.append(ch)
        else:
            out.append(palette[j % len(palette)] + ch + Ansi.RESET)
            j += 1
    return "".join(out)


def hr(char: str = "─", width: Optional[int] = None) -> str:
    return char * (width or WRAP_WIDTH)


def _dense_utf_text(s: str) -> bool:
    # CJK, Korean, Japanese, Hebrew, Arabic/Persian and Devanagari text often
    # has fewer spaces. textwrap can become slow or visually awkward there, so
    # those paragraphs are chunked directly. German/Spanish accents are not affected.
    for ch in s:
        o = ord(ch)
        if (0x3040 <= o <= 0x30FF) or (0x3400 <= o <= 0x9FFF) or (0xAC00 <= o <= 0xD7AF):
            return True
        if (0x0590 <= o <= 0x06FF) or (0x0900 <= o <= 0x097F):
            return True
    return False

def _chunk_dense(p: str, width: int, prefix: str) -> str:
    step = max(12, width - len(prefix))
    chunks = [p[i:i+step] for i in range(0, len(p), step)]
    return "\n".join(prefix + c for c in chunks)

def wrap(text: str, width: Optional[int] = None, indent: int = 0) -> str:
    width = width or WRAP_WIDTH
    prefix = " " * indent
    paras = str(text).split("\n")
    out = []
    for p in paras:
        raw = p.strip()
        if not raw:
            out.append("")
        elif _dense_utf_text(raw) and len(raw) > width:
            out.append(_chunk_dense(raw, width, prefix))
        else:
            out.append(textwrap.fill(raw, width=width,
                                     initial_indent=prefix,
                                     subsequent_indent=prefix))
    return "\n".join(out)


def section(title: str, color: str = Ansi.BRIGHT_CYAN) -> None:
    print()
    print(col(hr("═"), color))
    print(col(title, color + Ansi.BOLD if COLOR_ON else ""))
    print(col(hr("═"), color))


def small_section(title: str, color: str = Ansi.CYAN) -> None:
    print()
    visible = len(strip_ansi(title))
    print(col("── " + title + " " + "─" * max(1, WRAP_WIDTH - visible - 4), color))


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def fmt(x: float, n: int = 2) -> str:
    return f"{x:.{n}f}"


def gauge(value: float, width: int = 22, lo: float = 0.0, hi: float = 100.0) -> str:
    if hi == lo:
        ratio = 0.0
    else:
        ratio = clamp((value - lo) / (hi - lo), 0.0, 1.0)
    filled = int(round(ratio * width))
    empty = width - filled
    bar = "█" * filled + "░" * empty
    if value >= 70:
        c = Ansi.BRIGHT_GREEN
    elif value >= 45:
        c = Ansi.BRIGHT_YELLOW
    else:
        c = Ansi.BRIGHT_RED
    return col(bar, c) + f" {value:5.1f}"


def tension_gauge(value: float, width: int = 22) -> str:
    ratio = clamp(value / 100.0, 0.0, 1.0)
    filled = int(round(ratio * width))
    empty = width - filled
    bar = "█" * filled + "░" * empty
    if value <= 30:
        c = Ansi.BRIGHT_GREEN
    elif value <= 60:
        c = Ansi.BRIGHT_YELLOW
    else:
        c = Ansi.BRIGHT_RED
    return col(bar, c) + f" {value:5.1f}"


def table(headers: List[str], rows: List[List[object]], colors: Optional[List[str]] = None) -> str:
    str_rows = [[str(x) for x in r] for r in rows]
    widths = [len(strip_ansi(h)) for h in headers]
    for r in str_rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(strip_ansi(cell)))

    def pad_cell(cell: str, w: int) -> str:
        visible = len(strip_ansi(cell))
        return cell + " " * max(0, w - visible)

    hline = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    end = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"
    out = [hline]
    out.append("│ " + " │ ".join(col(pad_cell(headers[i], widths[i]), Ansi.BOLD) for i in range(len(headers))) + " │")
    out.append(mid)
    for ri, r in enumerate(str_rows):
        line = "│ " + " │ ".join(pad_cell(cell, widths[i]) for i, cell in enumerate(r)) + " │"
        if colors and ri < len(colors) and colors[ri]:
            line = col(line, colors[ri])
        out.append(line)
    out.append(end)
    return "\n".join(out)


def spark(values: List[float], lo: Optional[float] = None, hi: Optional[float] = None) -> str:
    chars = "▁▂▃▄▅▆▇█"
    if not values:
        return ""
    if lo is None:
        lo = min(values)
    if hi is None:
        hi = max(values)
    if hi == lo:
        return chars[0] * len(values)
    return "".join(chars[int(clamp((v - lo) / (hi - lo), 0, 0.999) * len(chars))] for v in values)


def heat_block(value: float, lo: float = 0.0, hi: float = 100.0) -> str:
    ratio = clamp((value - lo) / max(1e-9, hi - lo), 0.0, 1.0)
    blocks = "▁▂▃▄▅▆▇█"
    ch = blocks[int(ratio * (len(blocks) - 1))]
    if ratio < 0.35:
        return col(ch, Ansi.BRIGHT_GREEN)
    if ratio < 0.65:
        return col(ch, Ansi.BRIGHT_YELLOW)
    return col(ch, Ansi.BRIGHT_RED)


# -----------------------------------------------------------------------------
# 2. Angle mathematics
# -----------------------------------------------------------------------------


def norm_angle(a: float) -> float:
    return a % 360.0


def signed_delta(a: float, b: float) -> float:
    return ((b - a + 180.0) % 360.0) - 180.0


def angle_distance(a: float, b: float) -> float:
    return abs(signed_delta(a, b))


def klang(a: float, b: float) -> float:
    # 1.0 = same direction, 0.0 = opposite direction. Not positive/negative.
    return (1.0 + math.cos(math.radians(angle_distance(a, b)))) / 2.0


def gegenklang(a: float, b: float) -> float:
    return 1.0 - klang(a, b)


def circular_mean(angles: Iterable[float], weights: Iterable[float]) -> float:
    sx = 0.0
    sy = 0.0
    total = 0.0
    for a, w in zip(angles, weights):
        r = math.radians(a)
        sx += math.cos(r) * w
        sy += math.sin(r) * w
        total += w
    if total == 0 or (abs(sx) < 1e-12 and abs(sy) < 1e-12):
        return 0.0
    return norm_angle(math.degrees(math.atan2(sy, sx)))


def rotate_towards(a: float, target: float, rate: float) -> float:
    return norm_angle(a + signed_delta(a, target) * clamp(rate, 0.0, 1.0))


def softmax01(scores: List[float], temperature: float = 6.0) -> List[float]:
    if not scores:
        return []
    m = max(scores)
    vals = [math.exp((s - m) * temperature) for s in scores]
    total = sum(vals)
    if total == 0:
        return [1.0 / len(scores)] * len(scores)
    return [v / total for v in vals]


def angle_arrow(angle: float) -> str:
    arrows = ["→", "↗", "↑", "↖", "←", "↙", "↓", "↘"]
    idx = int(((norm_angle(angle) + 22.5) % 360) // 45)
    return arrows[idx]


def angle_label(angle: float) -> str:
    return f"{angle_arrow(angle)} {norm_angle(angle):6.1f}°"


def circular_noise(rng: random.Random, span: float) -> float:
    return rng.uniform(-span, span)


# -----------------------------------------------------------------------------
# 3. Localized labels, EU country pool and language helpers
# -----------------------------------------------------------------------------

ACTIONS = ["BUY", "SELL", "WORK"]
ACTION_OFFSET = {"BUY": 0.0, "SELL": 32.0, "WORK": -42.0}

SCENARIOS = ["baseline", "resonance", "power", "wellbeing", "fragmented", "scarcity", "tradeboom"]

SUPPORTED_LANGS = ["en", "de", "ru", "es", "it", "zh", "ja", "ko", "hi", "he", "fa", "ar"]
LANG_ALIASES = {
    "en":"en", "english":"en", "englisch":"en",
    "de":"de", "deutsch":"de", "german":"de",
    "ru":"ru", "russian":"ru", "russisch":"ru", "русский":"ru",
    "es":"es", "spanish":"es", "spanisch":"es", "español":"es",
    "it":"it", "italian":"it", "italienisch":"it", "italiano":"it",
    "zh":"zh", "cn":"zh", "chinese":"zh", "chinesisch":"zh", "中文":"zh",
    "ja":"ja", "japanese":"ja", "japanisch":"ja", "日本語":"ja",
    "ko":"ko", "korean":"ko", "koreanisch":"ko", "한국어":"ko",
    "hi":"hi", "hindi":"hi", "indisch":"hi", "indian":"hi", "हिन्दी":"hi",
    "he":"he", "hebrew":"he", "hebräisch":"he", "hebraeisch":"he", "עברית":"he",
    "fa":"fa", "persian":"fa", "persisch":"fa", "farsi":"fa", "فارسی":"fa",
    "ar":"ar", "arabic":"ar", "arabisch":"ar", "العربية":"ar",
}
LANG_NAMES = {"en":"English", "de":"Deutsch", "ru":"Русский", "es":"Español", "it":"Italiano", "zh":"中文", "ja":"日本語", "ko":"한국어", "hi":"हिन्दी", "he":"עברית", "fa":"فارسی", "ar":"العربية"}
LANGUAGE_NAMES = LANG_NAMES

def normalize_lang(lang: str) -> str:
    key = (lang or "en").strip().lower()
    return LANG_ALIASES.get(key, key if key in SUPPORTED_LANGS else "en")

def _names(en, de, ru, es, it, zh, ja, ko, hi, he, fa, ar):
    return {"en":en,"de":de,"ru":ru,"es":es,"it":it,"zh":zh,"ja":ja,"ko":ko,"hi":hi,"he":he,"fa":fa,"ar":ar}

# EU member-state pool used for seed-stable random country choice.
EU_COUNTRIES = [
    {"code":"AUT","scale":0.88,"names":_names("Austria","Österreich","Австрия","Austria","Austria","奥地利","オーストリア","오스트리아","ऑस्ट्रिया","אוסטריה","اتریش","النمسا")},
    {"code":"BEL","scale":0.95,"names":_names("Belgium","Belgien","Бельгия","Bélgica","Belgio","比利时","ベルギー","벨기에","बेल्जियम","בלגיה","بلژیک","بلجيكا")},
    {"code":"BGR","scale":0.78,"names":_names("Bulgaria","Bulgarien","Болгария","Bulgaria","Bulgaria","保加利亚","ブルガリア","불가리아","बुल्गारिया","בולגריה","بلغارستان","بلغاريا")},
    {"code":"HRV","scale":0.72,"names":_names("Croatia","Kroatien","Хорватия","Croacia","Croazia","克罗地亚","クロアチア","크로아티아","क्रोएशिया","קרואטיה","کرواسی","كرواتيا")},
    {"code":"CYP","scale":0.55,"names":_names("Cyprus","Zypern","Кипр","Chipre","Cipro","塞浦路斯","キプロス","키프로스","साइप्रस","קפריסין","قبرس","قبرص")},
    {"code":"CZE","scale":0.94,"names":_names("Czechia","Tschechien","Чехия","Chequia","Cechia","捷克","チェコ","체코","चेकिया","צ'כיה","چک","التشيك")},
    {"code":"DNK","scale":0.82,"names":_names("Denmark","Dänemark","Дания","Dinamarca","Danimarca","丹麦","デンマーク","덴마크","डेनमार्क","דנמרק","دانمارک","الدنمارك")},
    {"code":"EST","scale":0.56,"names":_names("Estonia","Estland","Эстония","Estonia","Estonia","爱沙尼亚","エストニア","에스토니아","एस्टोनिया","אסטוניה","استونی","إستونيا")},
    {"code":"FIN","scale":0.80,"names":_names("Finland","Finnland","Финляндия","Finlandia","Finlandia","芬兰","フィンランド","핀란드","फ़िनलैंड","פינלנד","فنلاند","فنلندا")},
    {"code":"FRA","scale":1.28,"names":_names("France","Frankreich","Франция","Francia","Francia","法国","フランス","프랑스","फ्रांस","צרפת","فرانسه","فرنسا")},
    {"code":"DEU","scale":1.35,"names":_names("Germany","Deutschland","Германия","Alemania","Germania","德国","ドイツ","독일","जर्मनी","גרמניה","آلمان","ألمانيا")},
    {"code":"GRC","scale":0.91,"names":_names("Greece","Griechenland","Греция","Grecia","Grecia","希腊","ギリシャ","그리스","ग्रीस","יוון","یونان","اليونان")},
    {"code":"HUN","scale":0.89,"names":_names("Hungary","Ungarn","Венгрия","Hungría","Ungheria","匈牙利","ハンガリー","헝가리","हंगरी","הונגריה","مجارستان","المجر")},
    {"code":"IRL","scale":0.76,"names":_names("Ireland","Irland","Ирландия","Irlanda","Irlanda","爱尔兰","アイルランド","아일랜드","आयरलैंड","אירלנד","ایرلند","أيرلندا")},
    {"code":"ITA","scale":1.22,"names":_names("Italy","Italien","Италия","Italia","Italia","意大利","イタリア","이탈리아","इटली","איטליה","ایتالیا","إيطاليا")},
    {"code":"LVA","scale":0.60,"names":_names("Latvia","Lettland","Латвия","Letonia","Lettonia","拉脱维亚","ラトビア","라트비아","लातविया","לטביה","لتونی","لاتفيا")},
    {"code":"LTU","scale":0.64,"names":_names("Lithuania","Litauen","Литва","Lituania","Lituania","立陶宛","リトアニア","리투아니아","लिथुआनिया","ליטא","لیتوانی","ليتوانيا")},
    {"code":"LUX","scale":0.50,"names":_names("Luxembourg","Luxemburg","Люксембург","Luxemburgo","Lussemburgo","卢森堡","ルクセンブルク","룩셈부르크","लक्ज़मबर्ग","לוקסמבורג","لوکزامبورگ","لوكسمبورغ")},
    {"code":"MLT","scale":0.48,"names":_names("Malta","Malta","Мальта","Malta","Malta","马耳他","マルタ","몰타","माल्टा","מלטה","مالت","مالطا")},
    {"code":"NLD","scale":1.02,"names":_names("Netherlands","Niederlande","Нидерланды","Países Bajos","Paesi Bassi","荷兰","オランダ","네덜란드","नीदरलैंड","הולנד","هلند","هولندا")},
    {"code":"POL","scale":1.14,"names":_names("Poland","Polen","Польша","Polonia","Polonia","波兰","ポーランド","폴란드","पोलैंड","פולין","لهستان","بولندا")},
    {"code":"PRT","scale":0.90,"names":_names("Portugal","Portugal","Португалия","Portugal","Portogallo","葡萄牙","ポルトガル","포르투갈","पुर्तगाल","פורטוגל","پرتغال","البرتغال")},
    {"code":"ROU","scale":1.04,"names":_names("Romania","Rumänien","Румыния","Rumanía","Romania","罗马尼亚","ルーマニア","루마니아","रोमानिया","רומניה","رومانی","رومانيا")},
    {"code":"SVK","scale":0.77,"names":_names("Slovakia","Slowakei","Словакия","Eslovaquia","Slovacchia","斯洛伐克","スロバキア","슬로바키아","स्लोवाकिया","סלובקיה","اسلواکی","سلوفاكيا")},
    {"code":"SVN","scale":0.61,"names":_names("Slovenia","Slowenien","Словения","Eslovenia","Slovenia","斯洛文尼亚","スロベニア","슬로베니아","स्लोवेनिया","סלובניה","اسلوونی","سلوفينيا")},
    {"code":"ESP","scale":1.18,"names":_names("Spain","Spanien","Испания","España","Spagna","西班牙","スペイン","스페인","स्पेन","ספרד","اسپانیا","إسبانيا")},
    {"code":"SWE","scale":0.94,"names":_names("Sweden","Schweden","Швеция","Suecia","Svezia","瑞典","スウェーデン","스웨덴","स्वीडन","שוודיה","سوئد","السويد")},
]

EU_COUNTRY_BY_ISO3 = {str(c["code"]): c for c in EU_COUNTRIES}

def normalize_lang_code(value: str) -> str:
    return normalize_lang(value)

def local_dict(d: Dict[str, str], lang: str) -> str:
    lang = normalize_lang(lang)
    return str(d.get(lang, d.get("en", next(iter(d.values())) if d else "")))

SECTOR_NAMES = {
    "FOO": _names("food","Nahrung","пища","alimentos","alimentazione","食品","食料","식량","भोजन","מזון","غذا","الغذاء"),
    "ENE": _names("energy","Energie","энергия","energía","energia","能源","エネルギー","에너지","ऊर्जा","אנרגיה","انرژی","الطاقة"),
    "HOU": _names("housing","Wohnen","жильё","vivienda","abitazione","住房","住宅","주거","आवास","דיור","مسکن","السكن"),
    "HEA": _names("health","Gesundheit","здоровье","salud","salute","健康","医療","건강","स्वास्थ्य","בריאות","سلامت","الصحة"),
    "EDU": _names("education","Bildung","образование","educación","istruzione","教育","教育","교육","शिक्षा","חינוך","آموزش","التعليم"),
    "CUL": _names("culture","Kultur","культура","cultura","cultura","文化","文化","문화","संस्कृति","תרבות","فرهنگ","الثقافة"),
    "SEC": _names("security","Sicherheit","безопасность","seguridad","sicurezza","安全","安全","안보","सुरक्षा","ביטחון","امنیت","الأمن"),
    "DAT": _names("data","Daten","данные","datos","dati","数据","データ","데이터","डेटा","נתונים","داده","البيانات"),
    "MOB": _names("mobility","Mobilität","мобильность","movilidad","mobilità","交通","移動","이동성","गतिशीलता","ניידות","جابه‌جایی","التنقل"),
}

def sector_label(code: str, lang: str) -> str:
    return local_dict(SECTOR_NAMES.get(code, {"en": code}), lang)

ACTION_LABELS = {
    "BUY": _names("buy market","Kaufmarkt","рынок покупки","mercado de compra","mercato d'acquisto","购买市场","購入市場","구매 시장","खरीद बाज़ार","שוק קנייה","بازار خرید","سوق الشراء"),
    "SELL": _names("sell market","Verkaufsmarkt","рынок продажи","mercado de venta","mercato di vendita","销售市场","販売市場","판매 시장","बिक्री बाज़ार","שוק מכירה","بازار فروش","سوق البيع"),
    "WORK": _names("labor market","Arbeitsmarkt","рынок труда","mercado laboral","mercato del lavoro","劳动市场","労働市場","노동 시장","श्रम बाज़ार","שוק עבודה","بازار کار","سوق العمل"),
}

SCENARIO_LABELS = {
    "baseline": _names("baseline","Basislauf","базовый ход","base","base","基线","基準","기준","आधार","בסיס","پایه","الأساس"),
    "resonance": _names("resonance","Resonanz","резонанс","resonancia","risonanza","共振","共鳴","공명","अनुनाद","תהודה","تشدید","رنين"),
    "power": _names("power pursuit","Machtstreben","стремление к власти","búsqueda de poder","ricerca di potere","权力追求","権力志向","권력 추구","शक्ति-प्रयास","חתירה לעוצמה","پیگیری قدرت","السعي إلى القوة"),
    "wellbeing": _names("well-being pursuit","Wohlbefinden","стремление к благополучию","búsqueda de bienestar","ricerca del benessere","福祉追求","幸福志向","복지 추구","कल्याण-प्रयास","חתירה לרווחה","پیگیری رفاه","السعي إلى الرفاه"),
    "fragmented": _names("fragmented angles","zersplitterte Winkel","рассеянные углы","ángulos fragmentados","angoli frammentati","碎片化角度","分断された角度","분절된 각도","खंडित कोण","זוויות מפוצלות","زاویه‌های پراکنده","زوايا متشظية"),
    "scarcity": _names("scarcity pressure","Mangeldruck","давление дефицита","presión de escasez","pressione della scarsità","稀缺压力","不足圧力","부족 압력","अभाव-दबाव","לחץ מחסור","فشار کمبود","ضغط الندرة"),
    "tradeboom": _names("trade boom","Handelsboom","торговый бум","auge comercial","boom commerciale","贸易繁荣","貿易ブーム","무역 붐","व्यापार उछाल","פריחת מסחר","رونق تجارت","طفرة تجارية"),
}

PH = {
    "ru": {"title":"УГЛОВАЯ ВЕКТОРНО-ВАЛЮТНАЯ ЭКОНОМИКА — ЦВЕТНАЯ СИМУЛЯЦИЯ PYPY3", "run":"Параметры запуска:", "selected":"Выбранные страны ЕС:", "language":"Язык:", "how":"Как читать этот вывод", "result":"Результат", "explain":"Объяснение"},
    "es": {"title":"ECONOMÍA ANGULAR DE MONEDAS VECTORIALES — SIMULACIÓN PYPY3 COLORIDA", "run":"Parámetros de ejecución:", "selected":"Países de la UE seleccionados:", "language":"Idioma:", "how":"Cómo leer esta salida", "result":"Resultado", "explain":"Explicación"},
    "it": {"title":"ECONOMIA ANGOLARE DELLE VALUTE VETTORIALI — SIMULAZIONE PYPY3 COLORATA", "run":"Parametri di esecuzione:", "selected":"Paesi UE selezionati:", "language":"Lingua:", "how":"Come leggere questo output", "result":"Risultato", "explain":"Spiegazione"},
    "zh": {"title":"角度向量货币经济 — 彩色 PYPY3 模拟", "run":"运行参数：", "selected":"选中的欧盟国家：", "language":"语言：", "how":"如何阅读此输出", "result":"结果", "explain":"说明"},
    "ja": {"title":"角度ベクトル通貨経済 — カラフル PYPY3 シミュレーション", "run":"実行パラメータ：", "selected":"選ばれたEU諸国：", "language":"言語：", "how":"この出力の読み方", "result":"結果", "explain":"説明"},
    "ko": {"title":"각도 벡터 통화 경제 — 컬러 PYPY3 시뮬레이션", "run":"실행 매개변수:", "selected":"선택된 EU 국가:", "language":"언어:", "how":"이 출력 읽는 법", "result":"결과", "explain":"설명"},
    "hi": {"title":"कोणीय वेक्टर-मुद्रा अर्थव्यवस्था — रंगीन PYPY3 सिमुलेशन", "run":"चलाने के मानक:", "selected":"चुने गए ईयू देश:", "language":"भाषा:", "how":"इस आउटपुट को कैसे पढ़ें", "result":"परिणाम", "explain":"व्याख्या"},
    "he": {"title":"כלכלת מטבעות-וקטור זוויתית — סימולציית PYPY3 צבעונית", "run":"פרמטרי הרצה:", "selected":"מדינות האיחוד שנבחרו:", "language":"שפה:", "how":"איך לקרוא את הפלט", "result":"תוצאה", "explain":"הסבר"},
    "fa": {"title":"اقتصاد ارز-بردار زاویه‌ای — شبیه‌سازی رنگی PYPY3", "run":"پارامترهای اجرا:", "selected":"کشورهای اتحادیه اروپا انتخاب‌شده:", "language":"زبان:", "how":"چگونه این خروجی را بخوانیم", "result":"نتیجه", "explain":"توضیح"},
    "ar": {"title":"اقتصاد العملات المتجهية الزاوي — محاكاة PYPY3 ملوّنة", "run":"معلمات التشغيل:", "selected":"دول الاتحاد الأوروبي المختارة:", "language":"اللغة:", "how":"كيف تقرأ هذا الخرج", "result":"النتيجة", "explain":"تفسير"},
}

COMMON = {
    "Code": _names("Code","Kürzel","Код","Código","Codice","代码","コード","코드","कोड","קוד","کد","رمز"),
    "Unit": _names("Unit","Einheit","Единица","Unidad","Unità","单位","単位","단위","इकाई","יחידה","واحد","وحدة"),
    "Meaning only in this part": _names("Meaning only in this part","Bedeutung nur in diesem Teil","Значение только в этой части","Significado solo en esta parte","Significato solo in questa parte","仅本部分含义","この部分だけの意味","이 부분에서만의 의미","सिर्फ इस भाग में अर्थ","משמעות רק בחלק זה","معنا فقط در این بخش","المعنى في هذا الجزء فقط"),
    "currency code": _names("currency code","Währungscode","код валюты","código de moneda","codice valuta","货币代码","通貨コード","통화 코드","मुद्रा कोड","קוד מטבע","کد ارز","رمز العملة"),
    "degrees": _names("degrees","Grad","градусы","grados","gradi","度","度","도","डिग्री","מעלות","درجه","درجات"),
    "hours": _names("hours","Stunden","часы","horas","ore","小时","時間","시간","घंटे","שעות","ساعت","ساعات"),
    "goods units": _names("goods units","Gütereinheiten","единицы благ","unidades de bienes","unità di beni","商品单位","財単位","재화 단위","वस्तु इकाइयाँ","יחידות טובין","واحد کالا","وحدات سلع"),
    "Name": _names("Name","Name","Имя","Nombre","Nome","名称","名称","이름","नाम","שם","نام","الاسم"),
    "Home": _names("Home","Heimat","Дом","Origen","Casa","归属","帰属","소속","घर","בית","خانه","الموطن"),
    "Share": _names("Share","Anteil","Доля","Cuota","Quota","份额","比率","점유율","हिस्सा","חלק","سهم","الحصة"),
    "Power": _names("Power","Macht","Власть","Poder","Potere","权力","権力","권력","शक्ति","עוצמה","قدرت","القوة"),
    "Pair": _names("Pair","Paar","Пара","Par","Coppia","配对","ペア","쌍","जोड़ी","זוג","جفت","زوج"),
    "Sec": _names("Sec","Sek","Сек","Sec","Set","部","部門","부문","क्षेत्र","מגזר","بخش","قطاع"),
    "Need": _names("Need","Bedarf","Потребн.","Neces.","Bisogno","需求","需要","수요","ज़रूरत","צורך","نیاز","الحاجة"),
    "Supply": _names("Supply","Versorgung","Предлож.","Oferta","Offerta","供给","供給","공급","आपूर्ति","אספקה","عرضه","العرض"),
    "Sat": _names("Sat","Deckung","Покрытие","Cobert.","Copert.","满足","充足","충족","पूर्ति","כיסוי","پوشش","التغطية"),
    "Price": _names("Price","Preis","Цена","Precio","Prezzo","价格","価格","가격","मूल्य","מחיר","قیمت","السعر"),
    "Country": _names("Country","Land","Страна","País","Paese","国家","国","국가","देश","מדינה","کشور","الدولة"),
    "Currency": _names("Currency","Währung","Валюта","Moneda","Valuta","货币","通貨","통화","मुद्रा","מטבע","ارز","العملة"),
    "Length": _names("Length","Länge","Длина","Longitud","Lunghezza","长度","長さ","길이","लंबाई","אורך","طول","الطول"),
    "Scenario": _names("Scenario","Szenario","Сценарий","Escenario","Scenario","情景","シナリオ","시나리오","परिदृश्य","תרחיש","سناریو","السيناريو"),
    "Final": _names("Final","Final","Финал","Final","Finale","最终","最終","최종","अंतिम","סופי","نهایی","نهائي"),
    "trail": _names("trail","Spur","след","rastro","traccia","轨迹","軌跡","흔적","रास्ता","עקבה","رد","أثر"),
    "power": _names("power","Macht","власть","poder","potere","权力","権力","권력","शक्ति","עוצמה","قدرت","القوة"),
    "resonance": _names("resonance","Resonanz","резонанс","resonancia","risonanza","共振","共鳴","공명","अनुनाद","תהודה","تشدید","الرنين"),
    "weak": _names("weak","schwach","слабый","débil","debole","弱","弱い","약함","कमज़ोर","חלש","ضعیف","ضعيف"),
    "well-being": _names("well-being","Wohlbefinden","благополучие","bienestar","benessere","福祉","幸福","복지","कल्याण","רווחה","رفاه","الرفاه"),
    "Run parameters:": _names("Run parameters:","Startparameter:","Параметры запуска:","Parámetros de ejecución:","Parametri di esecuzione:","运行参数：","実行パラメータ：","실행 매개변수:","चलाने के मानक:","פרמטרי הרצה:","پارامترهای اجرا:","معلمات التشغيل:"),
    "Selected EU countries:": _names("Selected EU countries:","Ausgewählte EU-Länder:","Выбранные страны ЕС:","Países de la UE seleccionados:","Paesi UE selezionati:","选中的欧盟国家：","選ばれたEU諸国：","선택된 EU 국가:","चुने गए ईयू देश:","מדינות האיחוד שנבחרו:","کشورهای اتحادیه اروپا انتخاب‌شده:","دول الاتحاد الأوروبي المختارة:"),
    "Language:": _names("Language:","Sprache:","Язык:","Idioma:","Lingua:","语言：","言語：","언어:","भाषा:","שפה:","زبان:","اللغة:"),
    "ANGULAR VECTOR-CURRENCY ECONOMY — COLORFUL PYPY3 SIMULATION": _names("ANGULAR VECTOR-CURRENCY ECONOMY — COLORFUL PYPY3 SIMULATION","WINKELWÄHRUNGSWIRTSCHAFT — BUNTE PYPY3-SIMULATION", PH["ru"]["title"], PH["es"]["title"], PH["it"]["title"], PH["zh"]["title"], PH["ja"]["title"], PH["ko"]["title"], PH["hi"]["title"], PH["he"]["title"], PH["fa"]["title"], PH["ar"]["title"]),
    "How to read this output": _names("How to read this output","So liest du diese Ausgabe", PH["ru"]["how"], PH["es"]["how"], PH["it"]["how"], PH["zh"]["how"], PH["ja"]["how"], PH["ko"]["how"], PH["hi"]["how"], PH["he"]["how"], PH["fa"]["how"], PH["ar"]["how"]),
    "FINAL REPORT": _names("FINAL REPORT","ABSCHLUSSBERICHT","ФИНАЛЬНЫЙ ОТЧЁТ","INFORME FINAL","RAPPORTO FINALE","最终报告","最終報告","최종 보고서","अंतिम रिपोर्ट","דוח סופי","گزارش نهایی","التقرير النهائي"),
    "UTF-8 ART GALLERY OF THE ANGULAR ECONOMY": _names("UTF-8 ART GALLERY OF THE ANGULAR ECONOMY","UTF-8-ART-GALERIE DER WINKELWIRTSCHAFT","ГАЛЕРЕЯ UTF-8-АРТА УГЛОВОЙ ЭКОНОМИКИ","GALERÍA UTF-8 DE LA ECONOMÍA ANGULAR","GALLERIA UTF-8 DELL'ECONOMIA ANGOLARE","角度经济 UTF-8 艺术图库","角度経済 UTF-8 アートギャラリー","각도 경제 UTF-8 아트 갤러리","कोणीय अर्थव्यवस्था की UTF-8 कला गैलरी","גלריית UTF-8 של הכלכלה הזוויתית","گالری UTF-8 اقتصاد زاویه‌ای","معرض UTF-8 للاقتصاد الزاوي"),
}

SECTION_TITLES = {
    "A) Currency ring: three equally long Euro vectors": _names("A) Currency ring: three equally long Euro vectors","A) Währungsring: drei gleich lange Euro-Vektoren","A) Валютное кольцо: три равных евро-вектора","A) Anillo monetario: tres euro-vectores iguales","A) Anello valutario: tre euro-vettori uguali","A) 货币环：三个等长欧元向量","A) 通貨リング：同じ長さの三つのユーロ・ベクトル","A) 통화 고리: 같은 길이의 세 유로 벡터","A) मुद्रा वृत्त: समान लंबाई वाले तीन यूरो-वेक्टर","A) טבעת מטבעות: שלושה וקטורי אירו באורך שווה","A) حلقه ارز: سه بردار یوروی هم‌طول","A) حلقة العملات: ثلاثة متجهات يورو متساوية الطول"),
    "B) Labor market and production": _names("B) Labor market and production","B) Arbeitsmarkt und Produktion","B) Рынок труда и производство","B) Mercado laboral y producción","B) Mercato del lavoro e produzione","B) 劳动市场与生产","B) 労働市場と生産","B) 노동시장과 생산","B) श्रम बाज़ार और उत्पादन","B) שוק עבודה וייצור","B) بازار کار و تولید","B) سوق العمل والإنتاج"),
    "C) Goods market and vector-Euro prices": _names("C) Goods market and vector-Euro prices","C) Gütermarkt und Vektor-Euro-Preise","C) Рынок благ и цены вектор-евро","C) Mercado de bienes y precios vector-euro","C) Mercato dei beni e prezzi vettore-euro","C) 商品市场与向量欧元价格","C) 財市場とベクトル・ユーロ価格","C) 재화시장과 벡터-유로 가격","C) वस्तु बाज़ार और वेक्टर-यूरो मूल्य","C) שוק טובין ומחירי וקטור-אירו","C) بازار کالا و قیمت‌های بردار-یورو","C) سوق السلع وأسعار متجه-اليورو"),
    "D) Trade triangle and angular work": _names("D) Trade triangle and angular work","D) Handelsdreieck und Umlenkungsarbeit","D) Торговый треугольник и угловая работа","D) Triángulo comercial y trabajo angular","D) Triangolo commerciale e lavoro angolare","D) 贸易三角与角度功","D) 貿易三角形と角度仕事","D) 무역 삼각형과 각도 일","D) व्यापार त्रिकोण और कोणीय कार्य","D) משולש מסחר ועבודה זוויתית","D) مثلث تجارت و کار زاویه‌ای","D) مثلث التجارة والعمل الزاوي"),
    "E) Power, well-being and economic strength": _names("E) Power, well-being and economic strength","E) Macht, Wohlbefinden und Wirtschaftsstärke","E) Власть, благополучие и экономическая сила","E) Poder, bienestar y fuerza económica","E) Potere, benessere e forza economica","E) 权力、福祉与经济强度","E) 権力・幸福・経済強度","E) 권력, 복지, 경제 강도","E) शक्ति, कल्याण और आर्थिक बल","E) עוצמה, רווחה וחוסן כלכלי","E) قدرت، رفاه و توان اقتصادی","E) القوة والرفاه والقوة الاقتصادية"),
    "F) Angle drift and event notes": _names("F) Angle drift and event notes","F) Winkeldrift und Ereignisnotizen","F) Дрейф углов и заметки событий","F) Deriva angular y notas de eventos","F) Deriva degli angoli e note evento","F) 角度漂移与事件说明","F) 角度ドリフトとイベント記録","F) 각도 표류와 사건 메모","F) कोण बहाव और घटना नोट","F) סחיפת זוויות והערות אירוע","F) رانش زاویه و یادداشت رویداد","F) انجراف الزوايا وملاحظات الأحداث"),
}
COMMON.update(SECTION_TITLES)

# Translations for short focus labels used by scenario-reading paragraphs.
COMMON.update({
    "the currency compass": _names("the currency compass","den Währungskompass","валютного компаса","la brújula monetaria","la bussola valutaria","货币罗盘","通貨コンパス","통화 나침반","मुद्रा कम्पास","מצפן המטבע","قطب‌نمای ارز","بوصلة العملة"),
    "equal vector length": _names("equal vector length","gleiche Vektorlänge","равной длины вектора","longitud vectorial igual","lunghezza vettoriale uguale","等长向量","等しいベクトル長","같은 벡터 길이","समान वेक्टर लंबाई","אורך וקטור שווה","طول بردار برابر","طول متجه متساوٍ"),
    "orthogonal axes": _names("orthogonal axes","orthogonale Achsen","ортогональных осей","ejes ortogonales","assi ortogonali","正交轴","直交軸","직교 축","लंबवत अक्ष","צירים ניצבים","محورهای عمود","محاور متعامدة"),
    "the three market vectors": _names("the three market vectors","die drei Marktvektoren","трёх рыночных векторов","los tres vectores de mercado","i tre vettori di mercato","三个市场向量","三つの市場ベクトル","세 시장 벡터","तीन बाज़ार वेक्टर","שלושת וקטורי השוק","سه بردار بازار","متجهات السوق الثلاثة"),
    "power versus well-being": _names("power versus well-being","Macht gegen Wohlbefinden","власти против благополучия","poder frente a bienestar","potere contro benessere","权力与福祉","権力対幸福","권력 대 복지","शक्ति बनाम कल्याण","עוצמה מול רווחה","قدرت در برابر رفاه","القوة مقابل الرفاه"),
    "the tension carpet": _names("the tension carpet","den Spannungsteppich","ковра напряжения","la alfombra de tensión","il tappeto di tensione","紧张地毯","緊張絨毯","긴장 카펫","तनाव कालीन","שטיח המתח","فرش تنش","سجادة التوتر"),
    "the trade triangle": _names("the trade triangle","das Handelsdreieck","торгового треугольника","el triángulo comercial","il triangolo commerciale","贸易三角","貿易三角形","무역 삼각형","व्यापार त्रिकोण","משולש המסחר","مثلث تجارت","مثلث التجارة"),
    "currency drift": _names("currency drift","Währungsdrift","валютного дрейфа","deriva monetaria","deriva valutaria","货币漂移","通貨ドリフト","통화 표류","मुद्रा बहाव","סחיפת מטבע","رانش ارز","انجراف العملة"),
    "sector satisfaction": _names("sector satisfaction","Sektordeckung","удовлетворения секторов","satisfacción sectorial","soddisfazione settoriale","部门满足度","部門満足度","부문 충족","क्षेत्र पूर्ति","סיפוק מגזרי","رضایت بخش","إشباع القطاع"),
    "price waves": _names("price waves","Preiswellen","ценовых волн","olas de precio","onde di prezzo","价格波","価格波","가격 파동","मूल्य तरंगें","גלי מחיר","موج‌های قیمت","موجات السعر"),
    "scenario quadrants": _names("scenario quadrants","Szenario-Quadranten","сценарных квадрантов","cuadrantes de escenario","quadranti di scenario","情景象限","シナリオ象限","시나리오 사분면","परिदृश्य चतुर्थांश","רביעי תרחיש","چهارک‌های سناریو","أرباع السيناريو"),
})


# Extra semantic translations used by unit tables and repeated summaries.
EXTRA_TRANSLATIONS = {
    "The three competing Euro vectors.": _names("The three competing Euro vectors.","Die drei konkurrierenden Euro-Vektoren.","Три конкурирующих евро-вектора.","Los tres euro-vectores en competencia.","I tre euro-vettori concorrenti.","三个竞争的欧元向量。","競合する三つのユーロ・ベクトル。","경쟁하는 세 유로 벡터.","तीन प्रतिस्पर्धी यूरो-वेक्टर।","שלושת וקטורי האירו המתחרים.","سه بردار یوروی رقابتی.","متجهات اليورو الثلاثة المتنافسة."),
    "Vector length. It must remain 1.000 for all currencies.": _names("Vector length. It must remain 1.000 for all currencies.","Vektorlänge. Sie muss bei allen Währungen 1.000 bleiben.","Длина вектора; у всех валют она остаётся 1.000.","Longitud del vector; debe permanecer 1.000 en todas las monedas.","Lunghezza del vettore; resta 1.000 per tutte le valute.","向量长度；所有货币都必须保持 1.000。","ベクトル長。すべての通貨で 1.000 のまま。","벡터 길이. 모든 통화에서 1.000으로 유지된다.","वेक्टर लंबाई; सभी मुद्राओं में 1.000 रहती है।","אורך וקטור; נשאר 1.000 בכל המטבעות.","طول بردار؛ برای همه ارزها 1.000 می‌ماند.","طول المتجه؛ يبقى 1.000 في كل العملات."),
    "Current direction of a currency on the ring.": _names("Current direction of a currency on the ring.","Aktuelle Richtung einer Währung auf dem Ring.","Текущее направление валюты на кольце.","Dirección actual de la moneda en el anillo.","Direzione attuale della valuta sull'anello.","货币在环上的当前方向。","リング上の通貨の現在方向。","고리 위 통화의 현재 방향.","वृत्त पर मुद्रा की वर्तमान दिशा।","הכיוון הנוכחי של המטבע על הטבעת.","جهت کنونی ارز روی حلقه.","الاتجاه الحالي للعملة على الحلقة."),
    "Part of this tick's transaction flow captured by the currency angle.": _names("Part of this tick's transaction flow captured by the currency angle.","Anteil des Transaktionsflusses dieses Ticks, der vom Währungswinkel gebunden wird.","Доля потока сделок этого шага, захваченная углом валюты.","Parte del flujo de transacciones de este paso captada por el ángulo monetario.","Quota del flusso di transazioni di questo tick catturata dall'angolo valutario.","本轮交易流中被货币角度吸引的份额。","このティックの取引流のうち通貨角が取り込んだ部分。","이번 틱의 거래 흐름 중 통화 각도가 붙잡은 몫.","इस टिक के लेन-देन प्रवाह का वह हिस्सा जिसे मुद्रा कोण पकड़ता है।","חלק מזרם העסקאות שנתפס בידי זווית המטבע.","بخشی از جریان تراکنش این گام که زاویه ارز جذب می‌کند.","جزء من تدفق معاملات هذه الدورة تلتقطه زاوية العملة."),
    "Accumulated attachment of market action and home government to this vector.": _names("Accumulated attachment of market action and home government to this vector.","Aufgebaute Bindung von Markthandlung und Heimatregierung an diesen Vektor.","Накопленная привязка рыночного действия и домашнего правительства к вектору.","Vínculo acumulado de la acción de mercado y el gobierno local con este vector.","Attaccamento accumulato dell'azione di mercato e del governo locale a questo vettore.","市场行动和本国政府对该向量的累积绑定。","市場行動と母国政府がこのベクトルへ蓄積した結び付き。","시장 행동과 자국 정부가 이 벡터에 쌓은 결속.","बाज़ार क्रिया और घरेलू सरकार का इस वेक्टर से जमा हुआ बंधन।","היקשרות מצטברת של פעולת השוק והממשלה המקומית לווקטור הזה.","پیوند انباشته کنش بازار و دولت خانگی با این بردار.","ارتباط متراكم بين فعل السوق والحكومة المحلية بهذا المتجه."),
    "Angle distance between two currencies; not a money exchange rate.": _names("Angle distance between two currencies; not a money exchange rate.","Winkelabstand zwischen zwei Währungen; kein Geld-Wechselkurs.","Угловое расстояние между валютами; не денежный курс.","Distancia angular entre dos monedas; no es tipo de cambio.","Distanza angolare fra due valute; non è un cambio monetario.","两种货币之间的角距；不是汇率。","二つの通貨の角度距離。為替レートではない。","두 통화 사이의 각도 거리; 환율이 아니다.","दो मुद्राओं के बीच कोण दूरी; यह विनिमय दर नहीं है।","מרחק זוויתי בין שני מטבעות; לא שער חליפין.","فاصله زاویه‌ای دو ارز؛ نرخ تبدیل پولی نیست.","مسافة زاوية بين عملتين؛ ليست سعر صرف."),
    "Angular resonance. 1 means same direction, 0 means opposite direction.": _names("Angular resonance. 1 means same direction, 0 means opposite direction.","Winkelklang. 1 bedeutet gleiche Richtung, 0 bedeutet Gegenrichtung.","Угловой резонанс: 1 — одно направление, 0 — противоположность.","Resonancia angular: 1 misma dirección, 0 dirección opuesta.","Risonanza angolare: 1 stessa direzione, 0 direzione opposta.","角度共振：1 表示同向，0 表示反向。","角度共鳴。1 は同方向、0 は反対方向。","각도 공명. 1은 같은 방향, 0은 반대 방향.","कोणीय अनुनाद: 1 समान दिशा, 0 विपरीत दिशा।","תהודה זוויתית: 1 אותו כיוון, 0 כיוון נגדי.","تشدید زاویه‌ای: 1 هم‌جهت، 0 پادجهت.","رنين زاوي: 1 الاتجاه نفسه، 0 الاتجاه المعاكس."),
    "Action angle of labor in a sector.": _names("Action angle of labor in a sector.","Handlungswinkel der Arbeit in einem Sektor.","Угол трудового действия в секторе.","Ángulo de acción del trabajo en un sector.","Angolo dell'azione-lavoro in un settore.","部门中劳动行动的角度。","部門内の労働行動角。","부문 내 노동 행동 각도.","किसी क्षेत्र में श्रम-क्रिया का कोण।","זווית פעולת העבודה במגזר.","زاویه کنش کار در یک بخش.","زاوية فعل العمل في قطاع."),
    "Currency whose angle fits the labor action best.": _names("Currency whose angle fits the labor action best.","Währung, deren Winkel am besten zur Arbeitsentscheidung passt.","Валюта, угол которой лучше всего подходит к труду.","Moneda cuyo ángulo encaja mejor con la acción laboral.","Valuta il cui angolo si adatta meglio al lavoro.","角度最适合劳动行动的货币。","労働行動に最も合う角度の通貨。","노동 행동에 가장 잘 맞는 각도의 통화.","जिस मुद्रा का कोण श्रम-क्रिया से सबसे अच्छा मिलता है।","המטבע שזוויתו מתאימה ביותר לפעולת העבודה.","ارزی که زاویه‌اش بهترین تناسب را با کار دارد.","العملة التي تناسب زاويتها فعل العمل أكثر."),
    "Abstract labor hours allocated this tick.": _names("Abstract labor hours allocated this tick.","Abstrakte Arbeitsstunden dieses Ticks.","Абстрактные трудочасы этого шага.","Horas laborales abstractas asignadas en este paso.","Ore di lavoro astratte assegnate in questo tick.","本轮分配的抽象劳动小时。","このティックに割り当てた抽象労働時間。","이번 틱에 배정된 추상 노동시간.","इस टिक में बाँटे गए अमूर्त श्रम घंटे।","שעות עבודה מופשטות שהוקצו במחזור הזה.","ساعت‌های کار انتزاعی تخصیص‌یافته در این گام.","ساعات عمل مجردة مخصصة في هذه الدورة."),
    "Production created by labor and productivity.": _names("Production created by labor and productivity.","Produktion, die aus Arbeit und Produktivität entsteht.","Производство из труда и производительности.","Producción creada por trabajo y productividad.","Produzione creata da lavoro e produttività.","由劳动和生产率产生的产出。","労働と生産性が生む生産。","노동과 생산성이 만든 생산량.","श्रम और उत्पादकता से बना उत्पादन।","ייצור שנוצר מעבודה ופריון.","تولید حاصل از کار و بهره‌وری.","إنتاج ناتج من العمل والإنتاجية."),
    "Fatigue from labor close to the unpopular pole.": _names("Fatigue from labor close to the unpopular pole.","Ermüdung durch Arbeit nahe am Unbeliebt-Pol.","Усталость от труда рядом с непопулярным полюсом.","Fatiga por trabajo cerca del polo impopular.","Fatica da lavoro vicino al polo impopolare.","靠近不受欢迎极点的劳动疲劳。","不人気極に近い労働からの疲労。","비인기 극에 가까운 노동에서 생기는 피로.","अलोकप्रिय ध्रुव के पास काम से उत्पन्न थकान।","עייפות מעבודה קרובה לקוטב הלא-פופולרי.","خستگی کار نزدیک به قطب نامحبوب.","إجهاد من عمل قريب من قطب غير محبوب."),
    "Population demand in the sector.": _names("Population demand in the sector.","Bevölkerungsbedarf im Sektor.","Спрос населения в секторе.","Demanda de la población en el sector.","Domanda della popolazione nel settore.","该部门的人口需求。","その部門での住民需要。","해당 부문의 인구 수요.","क्षेत्र में जन-आवश्यकता।","ביקוש האוכלוסייה במגזר.","تقاضای جمعیت در بخش.","طلب السكان في القطاع."),
    "Production minus exports plus imports.": _names("Production minus exports plus imports.","Produktion minus Exporte plus Importe.","Производство минус экспорт плюс импорт.","Producción menos exportaciones más importaciones.","Produzione meno esportazioni più importazioni.","生产减出口加进口。","生産から輸出を引き輸入を足したもの。","생산에서 수출을 빼고 수입을 더한 값.","उत्पादन घटा निर्यात और जोड़ा आयात।","ייצור פחות יצוא ועוד יבוא.","تولید منهای صادرات به‌علاوه واردات.","الإنتاج ناقص الصادرات زائد الواردات."),
    "Need covered by final supply.": _names("Need covered by final supply.","Bedarf, der durch Endversorgung gedeckt wird.","Потребность, покрытая итоговым предложением.","Necesidad cubierta por la oferta final.","Bisogno coperto dall'offerta finale.","最终供给覆盖的需求。","最終供給で満たされた需要。","최종 공급으로 충족된 수요.","अंतिम आपूर्ति से पूरी हुई जरूरत।","צורך המכוסה באספקה הסופית.","نیاز پوشش‌یافته با عرضه نهایی.","الحاجة التي يغطيها العرض النهائي."),
    "Number of equal vector-Euro units per goods unit.": _names("Number of equal vector-Euro units per goods unit.","Anzahl gleich langer Vektor-Euro-Einheiten pro Gütereinheit.","Число равных вектор-евро на единицу блага.","Número de unidades vector-euro iguales por unidad de bien.","Numero di unità vettore-euro uguali per unità di bene.","每单位商品所需的等长向量欧元数量。","財単位あたりの同長ベクトル・ユーロ数。","재화 단위당 같은 길이의 벡터-유로 수.","प्रति वस्तु इकाई समान वेक्टर-यूरो इकाइयों की संख्या।","מספר יחידות וקטור-אירו שוות לכל יחידת טובין.","تعداد واحدهای بردار-یوروی هم‌طول به ازای هر واحد کالا.","عدد وحدات متجه-اليورو المتساوية لكل وحدة سلعة."),
    "Buy and sell action angles.": _names("Buy and sell action angles.","Kauf- und Verkaufs-Handlungswinkel.","Углы действий покупки и продажи.","Ángulos de acción de compra y venta.","Angoli di azione di acquisto e vendita.","购买和销售行动角。","購入と販売の行動角。","구매와 판매의 행동 각도.","खरीद और बिक्री क्रिया के कोण।","זוויות פעולת קנייה ומכירה.","زاویه‌های کنش خرید و فروش.","زوايا فعل الشراء والبيع."),
    "Best currency for buy/sell angle.": _names("Best currency for buy/sell angle.","Beste Währung für Kauf-/Verkaufswinkel.","Лучшая валюта для угла покупки/продажи.","Mejor moneda para el ángulo de compra/venta.","Valuta migliore per l'angolo acquisto/vendita.","最适合购买/销售角的货币。","購入/販売角に最も合う通貨。","구매/판매 각도에 가장 적합한 통화.","खरीद/बिक्री कोण के लिए सर्वोत्तम मुद्रा।","המטבע המתאים ביותר לזווית קנייה/מכירה.","بهترین ارز برای زاویه خرید/فروش.","أفضل عملة لزاوية الشراء/البيع."),
    "Average orthogonal deviation of good/evil versus popular/unpopular axes.": _names("Average orthogonal deviation of good/evil versus popular/unpopular axes.","Mittlere Orthogonalitätsabweichung der Gut/Böse- zur Beliebt/Unbeliebt-Achse.","Среднее отклонение от ортогональности между осями добро/зло и популярно/непопулярно.","Desviación ortogonal media entre ejes bueno/malo y popular/impopular.","Deviazione ortogonale media fra assi bene/male e popolare/impopolare.","好/恶轴与受欢迎/不受欢迎轴的平均正交偏差。","善/悪軸と人気/不人気軸の平均直交偏差。","선/악 축과 인기/비인기 축 사이의 평균 직교 편차.","अच्छा/बुरा और लोकप्रिय/अलोकप्रिय अक्षों की औसत लंबवत विचलन।","סטייה ניצבת ממוצעת בין צירי טוב/רע ופופולרי/לא פופולרי.","انحراف عمودیت میانگین بین محور خوب/بد و محبوب/نامحبوب.","متوسط انحراف التعامد بين محوري الخير/الشر والمحبوب/غير المحبوب."),
    "country→country": _names("country→country","Land→Land","страна→страна","país→país","paese→paese","国家→国家","国→国","국가→국가","देश→देश","מדינה→מדינה","کشور→کشور","دولة→دولة"),
    "Exporter to importer.": _names("Exporter to importer.","Exportland zu Importland.","От экспортёра к импортёру.","Del exportador al importador.","Da esportatore a importatore.","从出口方到进口方。","輸出国から輸入国へ。","수출국에서 수입국으로.","निर्यातक से आयातक तक।","מיצואן ליבואן.","از صادرکننده به واردکننده.","من المصدّر إلى المستورد."),
    "Traded quantity.": _names("Traded quantity.","Gehandelte Menge.","Торгованный объём.","Cantidad comerciada.","Quantità scambiata.","交易数量。","取引量。","거래 수량.","व्यापारित मात्रा।","כמות נסחרת.","مقدار معامله‌شده.","الكمية المتداولة."),
    "Currency angle used by the joint trade action.": _names("Currency angle used by the joint trade action.","Währungswinkel, der von der gemeinsamen Handelshandlung genutzt wird.","Валютный угол совместного торгового действия.","Ángulo monetario usado por la acción comercial conjunta.","Angolo valutario usato dall'azione commerciale comune.","共同贸易行动使用的货币角度。","共同貿易行動が使う通貨角。","공동 무역 행동이 사용하는 통화 각도.","संयुक्त व्यापार क्रिया द्वारा उपयोग किया गया मुद्रा कोण।","זווית המטבע שמשמשת את פעולת המסחר המשותפת.","زاویه ارزی که کنش تجاری مشترک به‌کار می‌برد.","زاوية العملة المستخدمة في فعل التجارة المشترك."),
    "Mean action angle between exporter sell angle and importer buy angle.": _names("Mean action angle between exporter sell angle and importer buy angle.","Mittlerer Handlungswinkel aus Verkaufswinkel des Exporteurs und Kaufwinkel des Importeurs.","Средний угол действия между продажей экспортёра и покупкой импортёра.","Ángulo medio entre venta del exportador y compra del importador.","Angolo medio tra vendita dell'esportatore e acquisto dell'importatore.","出口销售角与进口购买角之间的平均行动角。","輸出側販売角と輸入側購入角の平均行動角。","수출자 판매각과 수입자 구매각 사이의 평균 행동각.","निर्यातक बिक्री कोण और आयातक खरीद कोण का औसत क्रिया कोण।","זווית פעולה ממוצעת בין זווית מכירת היצואן וזווית קניית היבואן.","زاویه کنش میانگین میان فروش صادرکننده و خرید واردکننده.","زاوية الفعل المتوسطة بين زاوية بيع المصدّر وزاوية شراء المستورد."),
    "Angle distance between exporter's home currency and trade currency.": _names("Angle distance between exporter's home currency and trade currency.","Winkelabstand zwischen Heimatwährung des Exporteurs und Handelswährung.","Угловая дистанция между домашней валютой экспортёра и валютой сделки.","Distancia angular entre moneda local del exportador y moneda comercial.","Distanza angolare fra valuta locale dell'esportatore e valuta commerciale.","出口方本国货币与贸易货币之间的角距。","輸出国の自国通貨と貿易通貨の角距離。","수출국 자국 통화와 무역 통화 사이의 각도 거리.","निर्यातक की घरेलू मुद्रा और व्यापार मुद्रा के बीच कोण दूरी।","מרחק זוויתי בין מטבע הבית של היצואן ומטבע המסחר.","فاصله زاویه‌ای ارز خانگی صادرکننده و ارز تجارت.","المسافة الزاوية بين عملة المصدّر المحلية وعملة التجارة."),
    "Angular work: vector-Euro amount multiplied by rotation in radians.": _names("Angular work: vector-Euro amount multiplied by rotation in radians.","Umlenkungsarbeit: Vektor-Euro-Menge mal Drehung in Radiant.","Угловая работа: объём вектор-евро умножен на поворот в радианах.","Trabajo angular: cantidad vector-euro multiplicada por rotación en radianes.","Lavoro angolare: quantità vettore-euro moltiplicata per la rotazione in radianti.","角度功：向量欧元数量乘以弧度旋转。","角度仕事：ベクトル・ユーロ量×ラジアン回転。","각도 일: 벡터-유로 양에 라디안 회전을 곱한 값.","कोणीय कार्य: वेक्टर-यूरो मात्रा गुणा रेडियन घुमाव।","עבודה זוויתית: כמות וקטור-אירו כפול סיבוב ברדיאנים.","کار زاویه‌ای: مقدار بردار-یورو ضربدر چرخش بر حسب رادیان.","العمل الزاوي: مقدار متجه-اليورو مضروباً في الدوران بالراديان."),
    "Well-being index of the population.": _names("Well-being index of the population.","Wohlbefindenindex der Bevölkerung.","Индекс благополучия населения.","Índice de bienestar de la población.","Indice di benessere della popolazione.","人口福祉指数。","住民の幸福指数。","인구 복지 지수.","जनता का कल्याण सूचकांक।","מדד רווחת האוכלוסייה.","شاخص رفاه جمعیت.","مؤشر رفاه السكان."),
    "Power index of government/currency attachment.": _names("Power index of government/currency attachment.","Machtindex der Bindung von Regierung und Währung.","Индекс власти связи правительства и валюты.","Índice de poder del vínculo gobierno/moneda.","Indice di potere del legame governo/valuta.","政府/货币绑定的权力指数。","政府/通貨結合の権力指数。","정부/통화 결속의 권력 지수.","सरकार/मुद्रा बंधन का शक्ति सूचकांक।","מדד עוצמה של קשר ממשלה/מטבע.","شاخص قدرت پیوند دولت/ارز.","مؤشر قوة ارتباط الحكومة/العملة."),
    "Economic strength under angular competition.": _names("Economic strength under angular competition.","Wirtschaftsstärke unter Winkelkonkurrenz.","Экономическая сила при угловой конкуренции.","Fuerza económica bajo competencia angular.","Forza economica sotto competizione angolare.","角度竞争下的经济强度。","角度競争下の経済強度。","각도 경쟁 아래의 경제 강도.","कोणीय प्रतिस्पर्धा में आर्थिक बल।","חוסן כלכלי תחת תחרות זוויתית.","توان اقتصادی زیر رقابت زاویه‌ای.","القوة الاقتصادية تحت التنافس الزاوي."),
    "Tension degree. Lower is calmer.": _names("Tension degree. Lower is calmer.","Spannungsgrad. Niedriger ist ruhiger.","Степень напряжения; ниже значит спокойнее.","Grado de tensión; más bajo es más tranquilo.","Grado di tensione; più basso è più calmo.","张力程度；越低越平稳。","緊張度。低いほど穏やか。","긴장도. 낮을수록 안정적.","तनाव स्तर; कम होना अधिक शांत है।","דרגת מתח; נמוך יותר רגוע יותר.","درجه تنش؛ کمتر آرام‌تر است.","درجة التوتر؛ الأقل أهدأ."),
    "Domestic share of the home vector currency.": _names("Domestic share of the home vector currency.","Inlandsanteil der eigenen Vektorwährung.","Внутренняя доля домашней векторной валюты.","Cuota interna de la moneda vectorial propia.","Quota interna della valuta vettoriale domestica.","本国向量货币的国内份额。","自国ベクトル通貨の国内シェア。","자국 벡터 통화의 국내 점유율.","घरेलू वेक्टर मुद्रा की देशीय हिस्सेदारी।","החלק המקומי של מטבע הווקטור הביתי.","سهم داخلی ارز برداری خانگی.","الحصة المحلية للعملة المتجهية الوطنية."),
    "Dominant currency in local transaction flow.": _names("Dominant currency in local transaction flow.","Dominante Währung im lokalen Transaktionsfluss.","Доминирующая валюта в местном потоке сделок.","Moneda dominante en el flujo local de transacciones.","Valuta dominante nel flusso locale di transazioni.","本地交易流中的主导货币。","地域取引流で支配的な通貨。","지역 거래 흐름의 지배 통화.","स्थानीय लेन-देन प्रवाह की प्रमुख मुद्रा।","המטבע הדומיננטי בזרם העסקאות המקומי.","ارز غالب در جریان تراکنش محلی.","العملة المهيمنة في تدفق المعاملات المحلي."),
    "Direction toward which a currency is slowly rotating.": _names("Direction toward which a currency is slowly rotating.","Richtung, zu der sich eine Währung langsam dreht.","Направление, к которому валюта медленно вращается.","Dirección hacia la que la moneda gira lentamente.","Direzione verso cui la valuta ruota lentamente.","货币缓慢旋转的目标方向。","通貨がゆっくり回転していく方向。","통화가 천천히 회전하는 방향.","जिस दिशा में मुद्रा धीरे-धीरे घूम रही है।","הכיוון שאליו המטבע מסתובב לאט.","جهتی که ارز آهسته به سوی آن می‌چرخد.","الاتجاه الذي تدور نحوه العملة ببطء."),
    "Distance between current currency angle and its initial angle.": _names("Distance between current currency angle and its initial angle.","Abstand zwischen aktuellem Währungswinkel und Anfangswinkel.","Расстояние между текущим и начальным углом валюты.","Distancia entre el ángulo actual de la moneda y el inicial.","Distanza fra angolo valutario attuale e iniziale.","当前货币角与初始角之间的距离。","現在の通貨角と初期角の距離。","현재 통화 각도와 초기 각도의 거리.","वर्तमान मुद्रा कोण और शुरुआती कोण के बीच दूरी।","מרחק בין זווית המטבע הנוכחית והראשונית.","فاصله زاویه کنونی ارز از زاویه آغازین.","المسافة بين زاوية العملة الحالية وزاويتها الابتدائية."),
    "Government good/evil angle: direction of the good pole.": _names("Government good/evil angle: direction of the good pole.","Gut/Böse-Winkel der Regierung: Richtung des Gut-Pols.","Угол добро/зло правительства: направление полюса добра.","Ángulo bueno/malo del gobierno: dirección del polo bueno.","Angolo bene/male del governo: direzione del polo bene.","政府好/恶角：好极点的方向。","政府の善/悪角：善極の方向。","정부 선/악 각도: 선 극의 방향.","सरकार का अच्छा/बुरा कोण: अच्छे ध्रुव की दिशा।","זווית טוב/רע של הממשלה: כיוון קוטב הטוב.","زاویه خوب/بد دولت: جهت قطب خوب.","زاوية خير/شر الحكومة: اتجاه قطب الخير."),
    "Population popular/unpopular angle: direction of the popular pole.": _names("Population popular/unpopular angle: direction of the popular pole.","Beliebt/Unbeliebt-Winkel der Bevölkerung: Richtung des Beliebt-Pols.","Угол популярно/непопулярно населения: направление популярного полюса.","Ángulo popular/impopular de la población: dirección del polo popular.","Angolo popolare/impopolare della popolazione: direzione del polo popolare.","人口受欢迎/不受欢迎角：受欢迎极点的方向。","住民の人気/不人気角：人気極の方向。","인구 인기/비인기 각도: 인기 극의 방향.","जनता का लोकप्रिय/अलोकप्रिय कोण: लोकप्रिय ध्रुव की दिशा।","זווית פופולרי/לא פופולרי של האוכלוסייה: כיוון הקוטב הפופולרי.","زاویه محبوب/نامحبوب مردم: جهت قطب محبوب.","زاوية محبوب/غير محبوب للسكان: اتجاه قطب المحبوب."),
    "Deviation from ideal 90° orthogonality between the axes.": _names("Deviation from ideal 90° orthogonality between the axes.","Abweichung von idealer 90°-Orthogonalität der Achsen.","Отклонение от идеальной ортогональности 90° между осями.","Desviación respecto a la ortogonalidad ideal de 90° entre ejes.","Deviazione dall'ortogonalità ideale di 90° fra gli assi.","轴之间偏离理想 90° 正交的程度。","軸間の理想的な90°直交からのずれ。","축 사이의 이상적 90° 직교에서 벗어난 정도.","अक्षों के बीच आदर्श 90° लंबवतता से विचलन।","סטייה מאורתוגונליות אידאלית של 90° בין הצירים.","انحراف از عمودیت ایدئال 90 درجه میان محورها.","الانحراف عن تعامد مثالي 90° بين المحاور."),
    "UTF-8 mini chart": _names("UTF-8 mini chart","UTF-8-Minikurve","мини-график UTF-8","minigráfico UTF-8","mini-grafico UTF-8","UTF-8 迷你图","UTF-8 ミニチャート","UTF-8 미니 차트","UTF-8 लघु चार्ट","תרשים UTF-8 קטן","نمودار کوچک UTF-8","رسم مصغر UTF-8"),
    "Tiny history line from low ▁ to high █.": _names("Tiny history line from low ▁ to high █.","Kleine Verlaufslinie von niedrig ▁ bis hoch █.","Малая линия истории от низкого ▁ до высокого █.","Línea histórica pequeña de bajo ▁ a alto █.","Piccola linea storica da basso ▁ ad alto █.","从低 ▁ 到高 █ 的小历史线。","低い ▁ から高い █ への小さな履歴線。","낮음 ▁ 에서 높음 █ 까지의 작은 이력선.","निम्न ▁ से उच्च █ तक छोटी इतिहास रेखा।","קו היסטורי קטן מנמוך ▁ לגבוה █.","خط تاریخچه کوچک از کم ▁ تا زیاد █.","خط تاريخ صغير من منخفض ▁ إلى مرتفع █."),
    "Home vector currency share in the final tick.": _names("Home vector currency share in the final tick.","Anteil der eigenen Vektorwährung im letzten Tick.","Доля домашней векторной валюты в финальном шаге.","Cuota de la moneda vectorial propia en el paso final.","Quota della valuta vettoriale domestica nel tick finale.","最后一轮中本国向量货币的份额。","最終ティックでの自国ベクトル通貨シェア。","마지막 틱의 자국 벡터 통화 점유율.","अंतिम टिक में घरेलू वेक्टर मुद्रा का हिस्सा।","חלק מטבע הווקטור הביתי במחזור האחרון.","سهم ارز برداری خانگی در گام نهایی.","حصة العملة المتجهية المحلية في الدورة الأخيرة."),
    "arithmetic mean": _names("arithmetic mean","arithmetischer Mittelwert","арифметическое среднее","media aritmética","media aritmetica","算术平均","算術平均","산술 평균","अंकगणितीय औसत","ממוצע אריתמטי","میانگین حسابی","المتوسط الحسابي"),
    "Average across three countries or full scenario run.": _names("Average across three countries or full scenario run.","Durchschnitt über drei Länder oder den ganzen Szenariolauf.","Среднее по трём странам или полному сценарию.","Promedio de tres países o de toda la ejecución del escenario.","Media sui tre paesi o sull'intero scenario.","三个国家或完整情景运行的平均值。","三国またはシナリオ全体の平均。","세 국가 또는 전체 시나리오 실행의 평균.","तीन देशों या पूरे परिदृश्य रन का औसत।","ממוצע על פני שלוש מדינות או תרחיש מלא.","میانگین سه کشور یا اجرای کامل سناریو.","متوسط عبر ثلاث دول أو تشغيل السيناريو الكامل."),
    "Targetθ": _names("Targetθ","Zielθ","Цельθ","Objetivoθ","Bersaglioθ","目标θ","目標θ","목표θ","लक्ष्यθ","יעדθ","هدفθ","الهدفθ"),
    "Random seed was generated automatically; pass --seed N to reproduce exactly.": _names("Random seed was generated automatically; pass --seed N to reproduce exactly.","Der Zufalls-Seed wurde automatisch erzeugt; mit --seed N lässt sich der Lauf exakt reproduzieren.","Случайное зерно создано автоматически; --seed N воспроизводит запуск точно.","La semilla aleatoria se generó automáticamente; usa --seed N para reproducir exactamente.","Il seed casuale è stato generato automaticamente; usa --seed N per riprodurre esattamente.","随机种子已自动生成；使用 --seed N 可精确复现。","乱数シードは自動生成されました。--seed N で正確に再現できます。","난수 시드가 자동 생성되었습니다. --seed N으로 정확히 재현할 수 있습니다.","रैंडम सीड अपने-आप बना; ठीक वैसा चलाने के लिए --seed N दें।","זרע אקראי נוצר אוטומטית; --seed N ישחזר בדיוק.","بذر تصادفی خودکار ساخته شد؛ با --seed N دقیقاً بازتولید می‌شود.","تم توليد البذرة العشوائية تلقائياً؛ استخدم --seed N للإعادة الدقيقة."),
    "one simulated period": _names("one simulated period","ein simulierter Zeitabschnitt","один имитируемый период","un período simulado","un periodo simulato","一个模拟周期","一つの模擬期間","하나의 시뮬레이션 기간","एक सिमुलेटेड अवधि","תקופה מדומה אחת","یک دوره شبیه‌سازی‌شده","فترة محاكاة واحدة"),
    "How to use it: choose --scenario resonance to see cleaner angular coherence, --scenario power to see stronger state/currency attachment, --scenario wellbeing to privilege livability, --scenario fragmented for scattered axes, --scenario scarcity for high needs and low production, or --scenario tradeboom for strong export/import motion.": _names("How to use it: choose --scenario resonance to see cleaner angular coherence, --scenario power to see stronger state/currency attachment, --scenario wellbeing to privilege livability, --scenario fragmented for scattered axes, --scenario scarcity for high needs and low production, or --scenario tradeboom for strong export/import motion.","Nutzung: --scenario resonance zeigt sauberere Winkelkohärenz, --scenario power stärkere Staats-/Währungsbindung, --scenario wellbeing bevorzugt Lebbarkeit, --scenario fragmented streut Achsen, --scenario scarcity erzeugt hohen Bedarf und niedrige Produktion, --scenario tradeboom starke Export-/Importbewegung.","Как использовать: --scenario resonance показывает более чистую угловую согласованность; --scenario power усиливает связь государство/валюта; --scenario wellbeing отдаёт приоритет жизнеспособности; --scenario fragmented рассеивает оси; --scenario scarcity даёт высокий спрос и низкое производство; --scenario tradeboom усиливает экспорт/импорт.","Uso: --scenario resonance muestra mayor coherencia angular; --scenario power refuerza el vínculo Estado/moneda; --scenario wellbeing prioriza vivibilidad; --scenario fragmented dispersa ejes; --scenario scarcity crea alta necesidad y baja producción; --scenario tradeboom impulsa exportación/importación.","Uso: --scenario resonance mostra maggiore coerenza angolare; --scenario power rafforza il legame stato/valuta; --scenario wellbeing privilegia vivibilità; --scenario fragmented disperde assi; --scenario scarcity crea bisogni alti e produzione bassa; --scenario tradeboom spinge export/import.","用法：--scenario resonance 显示更干净的角度连贯；--scenario power 加强国家/货币绑定；--scenario wellbeing 优先生活性；--scenario fragmented 分散轴；--scenario scarcity 产生高需求低生产；--scenario tradeboom 强化进出口运动。","使い方：--scenario resonance は角度整合をより明確に、--scenario power は国家/通貨結合を強く、--scenario wellbeing は生活可能性を優先、--scenario fragmented は軸を散らし、--scenario scarcity は高需要・低生産、--scenario tradeboom は輸出入運動を強めます。","사용법: --scenario resonance는 더 깨끗한 각도 일관성을, --scenario power는 국가/통화 결속을, --scenario wellbeing은 살 만함을 우선합니다. --scenario fragmented는 축을 흩뜨리고, --scenario scarcity는 높은 필요와 낮은 생산을, --scenario tradeboom은 수출입 운동을 강화합니다.","उपयोग: --scenario resonance साफ कोणीय संगति दिखाता है; --scenario power राज्य/मुद्रा बंधन बढ़ाता है; --scenario wellbeing रहने योग्य स्थिति को प्राथमिकता देता है; --scenario fragmented अक्ष फैलाता है; --scenario scarcity जरूरत बढ़ाकर उत्पादन घटाता है; --scenario tradeboom निर्यात/आयात गति बढ़ाता है।","שימוש: --scenario resonance מציג קוהרנטיות זוויתית נקייה יותר; --scenario power מחזק קשר מדינה/מטבע; --scenario wellbeing מעדיף חיות; --scenario fragmented מפזר צירים; --scenario scarcity יוצר צורך גבוה וייצור נמוך; --scenario tradeboom מחזק יצוא/יבוא.","کاربرد: --scenario resonance انسجام زاویه‌ای پاک‌تر نشان می‌دهد؛ --scenario power پیوند دولت/ارز را قوی‌تر می‌کند؛ --scenario wellbeing زیست‌پذیری را مقدم می‌دارد؛ --scenario fragmented محورها را می‌پراکند؛ --scenario scarcity نیاز بالا و تولید پایین می‌سازد؛ --scenario tradeboom حرکت صادرات/واردات را تقویت می‌کند.","الاستخدام: --scenario resonance يوضح تماسكاً زاوياً أنظف؛ --scenario power يقوي ارتباط الدولة/العملة؛ --scenario wellbeing يفضل قابلية العيش؛ --scenario fragmented يبعثر المحاور؛ --scenario scarcity يخلق حاجة عالية وإنتاجاً منخفضاً؛ --scenario tradeboom يقوي حركة التصدير/الاستيراد."),
}
COMMON.update(EXTRA_TRANSLATIONS)

GENERIC_LONG = {
    "read": _names("Each simulation part explains only its own abbreviations and units: currency angles, labor hours, goods supply, trade work and indices.","Jeder Simulationsteil erklärt nur seine eigenen Kürzel und Einheiten: Währungswinkel, Arbeitsstunden, Güterversorgung, Handelsarbeit und Indizes.","Каждая часть объясняет только свои сокращения и единицы: валютные углы, трудочасы, предложение благ, торговую работу и индексы.","Cada parte explica solo sus abreviaturas y unidades: ángulos monetarios, horas laborales, oferta de bienes, trabajo comercial e índices.","Ogni parte spiega solo abbreviazioni e unità proprie: angoli valutari, ore di lavoro, offerta di beni, lavoro commerciale e indici.","每个模拟部分只解释本部分的缩写和单位：货币角、劳动小时、商品供给、贸易功和指数。","各部分はその部分の略語と単位だけを説明します：通貨角、労働時間、財供給、貿易仕事、指数。","각 부분은 그 부분의 약어와 단위만 설명합니다: 통화 각도, 노동시간, 재화 공급, 무역 일, 지수.","हर भाग केवल अपने संक्षेप और इकाइयाँ समझाता है: मुद्रा कोण, श्रम घंटे, वस्तु आपूर्ति, व्यापार कार्य और सूचकांक।","כל חלק מסביר רק את הקיצורים והיחידות שלו: זוויות מטבע, שעות עבודה, אספקת טובין, עבודת מסחר ומדדים.","هر بخش فقط اختصارها و واحدهای خودش را توضیح می‌دهد: زاویه ارز، ساعت کار، عرضه کالا، کار تجارت و شاخص‌ها.","كل جزء يشرح اختصاراته ووحداته فقط: زوايا العملات، ساعات العمل، عرض السلع، عمل التجارة والمؤشرات."),
    "currency": _names("This part simulates the three equal Euro-vector currencies as directions on one ring and asks which direction attracts action flow.","Dieser Teil simuliert die drei gleich langen Euro-Vektor-Währungen als Richtungen auf einem Ring und fragt, welche Richtung Handlungsfluss anzieht.","Эта часть моделирует три равных евро-вектора как направления на кольце и спрашивает, какое направление притягивает поток действий.","Esta parte simula las tres monedas euro-vector iguales como direcciones en un anillo y pregunta qué dirección atrae el flujo de acción.","Questa parte simula le tre valute euro-vettore uguali come direzioni su un anello e chiede quale direzione attira il flusso d'azione.","本部分把三个等长欧元向量货币模拟为同一环上的方向，并询问哪一方向吸引行动流。","この部分は同じ長さの三つのユーロ・ベクトル通貨を一つのリング上の方向として模擬し、どの方向が行動流を引き寄せるかを問います。","이 부분은 같은 길이의 세 유로 벡터 통화를 하나의 고리 위 방향으로 시뮬레이션하고 어떤 방향이 행동 흐름을 끌어오는지 묻습니다.","यह भाग तीन समान यूरो-वेक्टर मुद्राओं को एक वृत्त पर दिशाओं की तरह सिमुलेट करता है और पूछता है कि कौन-सी दिशा क्रिया प्रवाह खींचती है।","חלק זה מדמה שלושה מטבעות וקטור-אירו שווים ככיוונים על טבעת אחת ושואל איזה כיוון מושך זרם פעולה.","این بخش سه ارز بردار-یوروی برابر را مانند جهت‌هایی روی یک حلقه شبیه‌سازی می‌کند و می‌پرسد کدام جهت جریان کنش را جذب می‌کند.","يحاكي هذا الجزء العملات الثلاث المتجهية المتساوية كاتجاهات على حلقة واحدة ويسأل أي اتجاه يجذب تدفق الفعل."),
    "labor": _names("This part simulates labor as an angular action and shows where work creates production or fatigue.","Dieser Teil simuliert Arbeit als Winkelhandlung und zeigt, wo Arbeit Produktion oder Ermüdung erzeugt.","Эта часть моделирует труд как угловое действие и показывает, где работа создаёт производство или усталость.","Esta parte simula el trabajo como acción angular y muestra dónde crea producción o fatiga.","Questa parte simula il lavoro come azione angolare e mostra dove produce beni o fatica.","本部分把劳动模拟为角度行动，并显示劳动在哪里产生生产或疲劳。","この部分は労働を角度行動として模擬し、労働がどこで生産または疲労を生むかを示します。","이 부분은 노동을 각도 행동으로 시뮬레이션하고 어디서 생산 또는 피로가 생기는지 보여줍니다.","यह भाग श्रम को कोणीय क्रिया मानकर दिखाता है कि काम कहाँ उत्पादन या थकान बनाता है।","חלק זה מדמה עבודה כפעולה זוויתית ומראה היכן עבודה יוצרת ייצור או עייפות.","این بخش کار را به‌عنوان کنش زاویه‌ای شبیه‌سازی می‌کند و نشان می‌دهد کجا تولید یا خستگی می‌سازد.","يحاكي هذا الجزء العمل كفعل زاوي ويُظهر أين يخلق العمل إنتاجاً أو إجهاداً."),
    "goods": _names("This part simulates need, supply, satisfaction and vector-Euro price; price counts equal VE units and never lengthens a currency vector.","Dieser Teil simuliert Bedarf, Versorgung, Deckung und Vektor-Euro-Preis; der Preis zählt gleiche VE-Einheiten und verlängert nie einen Währungsvektor.","Эта часть моделирует потребность, предложение, покрытие и цену вектор-евро; цена считает равные VE и не удлиняет валютный вектор.","Esta parte simula necesidad, oferta, cobertura y precio vector-euro; el precio cuenta unidades VE iguales y nunca alarga un vector monetario.","Questa parte simula bisogno, offerta, copertura e prezzo vettore-euro; il prezzo conta unità VE uguali e non allunga mai un vettore valutario.","本部分模拟需求、供给、满足度和向量欧元价格；价格只是计数等长 VE 单位，不会拉长货币向量。","この部分は需要・供給・充足・ベクトルユーロ価格を模擬します。価格は同じ VE 単位を数えるだけで通貨ベクトルを伸ばしません。","이 부분은 필요, 공급, 충족, 벡터-유로 가격을 시뮬레이션합니다. 가격은 같은 VE 단위를 세며 통화 벡터를 늘리지 않습니다.","यह भाग जरूरत, आपूर्ति, पूर्ति और वेक्टर-यूरो मूल्य सिमुलेट करता है; मूल्य समान VE इकाइयाँ गिनता है, मुद्रा वेक्टर लंबा नहीं करता।","חלק זה מדמה צורך, אספקה, כיסוי ומחיר וקטור-אירו; המחיר סופר יחידות VE שוות ואינו מאריך וקטור מטבע.","این بخش نیاز، عرضه، پوشش و قیمت بردار-یورو را شبیه‌سازی می‌کند؛ قیمت فقط واحدهای VE برابر را می‌شمارد و بردار ارز را بلند نمی‌کند.","يحاكي هذا الجزء الحاجة والعرض والتغطية وسعر متجه-اليورو؛ السعر يعد وحدات VE متساوية ولا يطيل متجه العملة."),
    "trade": _names("This part simulates triangular trade and angular work between exporter, importer and trade currency.","Dieser Teil simuliert Dreieckshandel und Umlenkungsarbeit zwischen Exporteur, Importeur und Handelswährung.","Эта часть моделирует треугольную торговлю и угловую работу между экспортёром, импортёром и валютой сделки.","Esta parte simula comercio triangular y trabajo angular entre exportador, importador y moneda comercial.","Questa parte simula commercio triangolare e lavoro angolare fra esportatore, importatore e valuta commerciale.","本部分模拟出口方、进口方和贸易货币之间的三角贸易与角度功。","この部分は輸出国・輸入国・貿易通貨の間の三角貿易と角度仕事を模擬します。","이 부분은 수출국, 수입국, 무역 통화 사이의 삼각 무역과 각도 일을 시뮬레이션합니다.","यह भाग निर्यातक, आयातक और व्यापार मुद्रा के बीच त्रिकोणीय व्यापार और कोणीय कार्य सिमुलेट करता है।","חלק זה מדמה מסחר משולש ועבודה זוויתית בין יצואן, יבואן ומטבע מסחר.","این بخش تجارت مثلثی و کار زاویه‌ای میان صادرکننده، واردکننده و ارز تجارت را شبیه‌سازی می‌کند.","يحاكي هذا الجزء التجارة المثلثة والعمل الزاوي بين المصدّر والمستورد وعملة التجارة."),
    "goals": _names("This part simulates the goal system: well-being, power, economic strength and tension instead of wealth maximization.","Dieser Teil simuliert das Zielsystem: Wohlbefinden, Macht, Wirtschaftsstärke und Spannung statt Reichtumsmaximierung.","Эта часть моделирует систему целей: благополучие, власть, экономическую силу и напряжение вместо максимизации богатства.","Esta parte simula el sistema de objetivos: bienestar, poder, fuerza económica y tensión en vez de maximizar riqueza.","Questa parte simula il sistema degli obiettivi: benessere, potere, forza economica e tensione invece della massimizzazione della ricchezza.","本部分模拟目标系统：福祉、权力、经济强度和张力，而不是财富最大化。","この部分は目標体系を模擬します。富の最大化ではなく、幸福・権力・経済強度・緊張です。","이 부분은 목표 체계를 시뮬레이션합니다: 부의 극대화가 아니라 복지, 권력, 경제 강도, 긴장입니다.","यह भाग लक्ष्य प्रणाली सिमुलेट करता है: धन अधिकतम करने के बजाय कल्याण, शक्ति, आर्थिक बल और तनाव।","חלק זה מדמה מערכת מטרות: רווחה, עוצמה, חוסן כלכלי ומתח במקום מקסום עושר.","این بخش نظام هدف را شبیه‌سازی می‌کند: رفاه، قدرت، توان اقتصادی و تنش به‌جای بیشینه‌سازی ثروت.","يحاكي هذا الجزء نظام الأهداف: الرفاه والقوة والقوة الاقتصادية والتوتر بدلاً من تعظيم الثروة."),
    "drift": _names("This part simulates slow angular drift of governments, populations and currencies toward successful, powerful or livable actions.","Dieser Teil simuliert langsame Winkeldrift von Regierungen, Bevölkerungen und Währungen zu erfolgreichen, machtvollen oder lebbaren Handlungen.","Эта часть моделирует медленный дрейф углов правительств, населения и валют к успешным, властным или пригодным для жизни действиям.","Esta parte simula la deriva angular lenta de gobiernos, poblaciones y monedas hacia acciones exitosas, poderosas o vivibles.","Questa parte simula la lenta deriva angolare di governi, popolazioni e valute verso azioni riuscite, potenti o vivibili.","本部分模拟政府、人口和货币缓慢漂向成功、有权力或可生活的行动角。","この部分は政府・住民・通貨が成功・権力・生活可能性のある行動へゆっくり角度ドリフトする様子を模擬します。","이 부분은 정부, 인구, 통화가 성공적이거나 강력하거나 살기 좋은 행동으로 천천히 각도 표류하는 것을 시뮬레이션합니다.","यह भाग सरकारों, जनता और मुद्राओं का धीमा कोण बहाव सफल, शक्तिशाली या रहने योग्य क्रियाओं की ओर सिमुलेट करता है।","חלק זה מדמה סחיפה זוויתית איטית של ממשלות, אוכלוסיות ומטבעות אל פעולות מצליחות, עוצמתיות או ראויות לחיים.","این بخش رانش آهسته زاویه دولت‌ها، مردم و ارزها را به سوی کنش‌های موفق، قدرتمند یا زیست‌پذیر شبیه‌سازی می‌کند.","يحاكي هذا الجزء انجرافاً زاوياً بطيئاً للحكومات والسكان والعملات نحو أفعال ناجحة أو قوية أو قابلة للعيش."),
    "final": _names("This final part reads the whole run by comparing indices, mini-charts and angular weakness.","Dieser Abschlussteil liest den ganzen Lauf über Indizes, Minikurven und Winkelschwäche.","Финальная часть читает весь запуск через индексы, мини-графики и угловую слабость.","La parte final lee toda la ejecución comparando índices, minigráficos y debilidad angular.","La parte finale legge l'intera corsa confrontando indici, mini-grafici e debolezza angolare.","最终部分通过指数、迷你图和角度弱点解读整个运行。","最終部は指数・ミニチャート・角度の弱さを比較して全体を読みます。","최종 부분은 지수, 미니 차트, 각도 약점을 비교해 전체 실행을 읽습니다.","अंतिम भाग सूचकांक, लघु चार्ट और कोणीय कमजोरी से पूरे रन को पढ़ता है।","החלק הסופי קורא את כל ההרצה דרך מדדים, תרשימים קטנים וחולשה זוויתית.","بخش پایانی کل اجرا را با شاخص‌ها، نمودارهای کوچک و ضعف زاویه‌ای می‌خواند.","يقرأ الجزء النهائي التشغيل كله عبر المؤشرات والرسوم الصغيرة والضعف الزاوي."),
    "tick": _names("A tick can be read as a month, quarter or political-market cycle: currency, labor, goods, trade, indices and drift.","Ein Tick kann als Monat, Quartal oder politischer Marktzyklus gelesen werden: Währung, Arbeit, Güter, Handel, Indizes und Drift.","Шаг можно читать как месяц, квартал или политико-рыночный цикл: валюта, труд, блага, торговля, индексы и дрейф.","Un tick puede leerse como mes, trimestre o ciclo político-mercantil: moneda, trabajo, bienes, comercio, índices y deriva.","Un tick può essere letto come mese, trimestre o ciclo politico-mercato: valuta, lavoro, beni, commercio, indici e deriva.","一个 tick 可理解为月份、季度或政治市场周期：货币、劳动、商品、贸易、指数和漂移。","1ティックは月・四半期・政治市場サイクルとして読めます：通貨、労働、財、貿易、指数、ドリフト。","틱 하나는 월, 분기 또는 정치-시장 주기로 읽을 수 있습니다: 통화, 노동, 재화, 무역, 지수, 표류.","एक टिक को महीना, तिमाही या राजनीतिक-बाज़ार चक्र माना जा सकता है: मुद्रा, श्रम, वस्तु, व्यापार, सूचकांक और बहाव।","טיק יכול להיקרא כחודש, רבעון או מחזור שוק-פוליטי: מטבע, עבודה, טובין, מסחר, מדדים וסחיפה.","یک تیک می‌تواند ماه، فصل یا چرخه سیاسی-بازاری خوانده شود: ارز، کار، کالا، تجارت، شاخص‌ها و رانش.","يمكن قراءة الدورة كشهر أو ربع سنة أو دورة سياسية-سوقية: عملة، عمل، سلع، تجارة، مؤشرات وانجراف."),
    "final_report": _names("The final report asks which vector currency gained power, where well-being stayed livable and where angular tension weakened the economy.","Der Abschlussbericht fragt, welche Vektorwährung Macht gewann, wo Wohlbefinden lebbar blieb und wo Winkelspannung die Wirtschaft schwächte.","Финальный отчёт спрашивает, какая векторная валюта набрала власть, где благополучие осталось жизнеспособным и где угловое напряжение ослабило экономику.","El informe final pregunta qué moneda vectorial ganó poder, dónde el bienestar siguió vivible y dónde la tensión angular debilitó la economía.","Il rapporto finale chiede quale valuta vettoriale ha guadagnato potere, dove il benessere è rimasto vivibile e dove la tensione angolare ha indebolito l'economia.","最终报告询问哪种向量货币获得权力，哪里福祉仍可生活，哪里角度张力削弱经济。","最終報告は、どのベクトル通貨が権力を得たか、どこで幸福が生きられる水準に残ったか、どこで角度緊張が経済を弱めたかを問います。","최종 보고서는 어떤 벡터 통화가 권력을 얻었는지, 어디서 복지가 살 만하게 남았는지, 어디서 각도 긴장이 경제를 약화했는지 묻습니다.","अंतिम रिपोर्ट पूछती है कौन-सी वेक्टर मुद्रा ने शक्ति पाई, कहाँ कल्याण रहने योग्य रहा और कहाँ कोणीय तनाव ने अर्थव्यवस्था कमजोर की।","הדוח הסופי שואל איזה מטבע-וקטור צבר עוצמה, היכן הרווחה נשארה ראויה לחיים והיכן מתח זוויתי החליש את הכלכלה.","گزارش پایانی می‌پرسد کدام ارز برداری قدرت گرفت، کجا رفاه زیست‌پذیر ماند و کجا تنش زاویه‌ای اقتصاد را تضعیف کرد.","يسأل التقرير النهائي أي عملة متجهية اكتسبت قوة، وأين بقي الرفاه قابلاً للعيش، وأين أضعف التوتر الزاوي الاقتصاد."),
    "gallery": _names("The UTF-8 gallery turns the final state into colorful circles, vectors, heat carpets, trade arrows and scenario maps.","Die UTF-8-Galerie übersetzt den Endzustand in bunte Kreise, Vektoren, Wärmeteppiche, Handelspfeile und Szenariokarten.","Галерея UTF-8 переводит финальное состояние в цветные круги, векторы, тепловые ковры, торговые стрелки и карты сценариев.","La galería UTF-8 convierte el estado final en círculos, vectores, alfombras de calor, flechas comerciales y mapas de escenarios.","La galleria UTF-8 traduce lo stato finale in cerchi colorati, vettori, tappeti di calore, frecce commerciali e mappe di scenario.","UTF-8 图库把最终状态转成彩色圆、向量、热力地毯、贸易箭头和情景图。","UTF-8ギャラリーは最終状態を色付きの円、ベクトル、ヒートカーペット、貿易矢印、シナリオ地図に変換します。","UTF-8 갤러리는 최종 상태를 컬러 원, 벡터, 열 카펫, 무역 화살표, 시나리오 지도로 바꿉니다.","UTF-8 कला गैलरी अंतिम स्थिति को रंगीन वृत्त, वेक्टर, ताप-पट्टी, व्यापार तीर और परिदृश्य मानचित्र में बदलती है।","גלריית UTF-8 מתרגמת את המצב הסופי לעיגולים צבעוניים, וקטורים, שטיחי חום, חיצי מסחר ומפות תרחיש.","گالری UTF-8 حالت نهایی را به دایره‌های رنگی، بردارها، فرش حرارتی، پیکان‌های تجارت و نقشه‌های سناریو تبدیل می‌کند.","يحوّل معرض UTF-8 الحالة النهائية إلى دوائر ملوّنة ومتجهات وبسط حرارية وأسهم تجارة وخرائط سيناريو."),
}

RESULT_SUMMARIES = [
    ("Result: the picture shows only direction", _names("The picture shows directions only, not longer or shorter money. The three Euro vectors compete because their angles differ while every vector length remains 1 VE.","Das Bild zeigt nur Richtungen, keine längeren oder kürzeren Gelder. Die drei Euro-Vektoren konkurrieren über verschiedene Winkel, während jede Vektorlänge 1 VE bleibt.","Картинка показывает только направления, а не более длинные или короткие деньги. Три евро-вектора конкурируют углами, но длина каждого остаётся 1 VE.","La imagen muestra solo direcciones, no dinero más largo o más corto. Los tres euro-vectores compiten por ángulos distintos, con longitud fija de 1 VE.","L'immagine mostra solo direzioni, non denaro più lungo o più corto. I tre euro-vettori competono per angoli diversi, con lunghezza fissa di 1 VE.","图像只显示方向，不显示更长或更短的钱。三个欧元向量因角度不同而竞争，但长度都保持 1 VE。","図は方向だけを示し、長い/短いお金を示しません。三つのユーロ・ベクトルは角度で競合し、長さはすべて1 VEです。","그림은 방향만 보여주며 돈의 길고 짧음을 보여주지 않습니다. 세 유로 벡터는 각도로 경쟁하지만 길이는 모두 1 VE입니다.","चित्र केवल दिशाएँ दिखाता है, बड़ा या छोटा पैसा नहीं। तीन यूरो-वेक्टर कोणों से प्रतिस्पर्धा करते हैं, लंबाई हर बार 1 VE रहती है।","התמונה מציגה כיוונים בלבד, לא כסף ארוך או קצר יותר. שלושת וקטורי האירו מתחרים בזוויות, ואורך כל אחד נשאר 1 VE.","تصویر فقط جهت‌ها را نشان می‌دهد، نه پول بلندتر یا کوتاه‌تر. سه بردار یورو با زاویه رقابت می‌کنند و طول همه 1 VE می‌ماند.","تعرض الصورة الاتجاهات فقط، لا مالاً أطول أو أقصر. تتنافس متجهات اليورو الثلاثة بالزوايا، وطول كل منها يبقى 1 VE.")),
    ("Result: all three bars have identical length", _names("All three bars have identical length. Prices count how many equal vector-Euro units a good needs; scarcity raises this count, but no currency vector becomes longer.","Alle drei Balken haben identische Länge. Preise zählen, wie viele gleiche Vektor-Euro-Einheiten ein Gut braucht; Mangel erhöht diese Zahl, aber kein Währungsvektor wird länger.","Все три столбца имеют одинаковую длину. Цены считают число равных вектор-евро на благо; дефицит повышает счёт, но валюта не удлиняется.","Las tres barras tienen igual longitud. Los precios cuentan cuántas unidades vector-euro iguales necesita un bien; la escasez sube la cuenta, pero ninguna moneda se alarga.","Le tre barre hanno lunghezza uguale. I prezzi contano quante unità vettore-euro uguali servono a un bene; la scarsità aumenta il conteggio, ma nessun vettore si allunga.","三条柱长度相同。价格计算一种商品需要多少个等长向量欧元；稀缺会提高数量，但货币向量不会变长。","三本のバーは同じ長さです。価格は財に必要な同長ベクトル・ユーロ数を数えます。不足で数は増えても通貨ベクトルは伸びません。","세 막대의 길이는 같습니다. 가격은 재화에 필요한 같은 길이의 벡터-유로 수를 세며, 부족은 그 수를 올리지만 통화 벡터는 길어지지 않습니다.","तीनों पट्टियाँ समान लंबाई की हैं। मूल्य गिनता है कि वस्तु को कितनी समान वेक्टर-यूरो इकाइयाँ चाहिए; कमी गिनती बढ़ाती है, मुद्रा लंबी नहीं होती।","שלושת העמודים באותו אורך. המחיר סופר כמה יחידות וקטור-אירו שוות דרושות לטובין; מחסור מעלה את המספר אך המטבע לא מתארך.","هر سه میله هم‌طول‌اند. قیمت می‌شمارد یک کالا چند واحد بردار-یوروی برابر می‌خواهد؛ کمبود عدد را بالا می‌برد اما ارز بلندتر نمی‌شود.","الأشرطة الثلاثة متساوية الطول. السعر يعد عدد وحدات متجه-اليورو المتساوية اللازمة للسلعة؛ الندرة ترفع العدد لكن العملة لا تطول.")),
    ("Result: this is the strongest axis-pressure example", _names("This panel selects the strongest final axis-pressure example. It contrasts the government good/evil pole with the population popular/unpopular pole and shows how far the axes deviate from the ideal right angle.","Diese Tafel wählt den stärksten finalen Achsendruck. Sie stellt den Gut/Böse-Pol der Regierung dem Beliebt/Unbeliebt-Pol der Bevölkerung gegenüber und zeigt die Abweichung vom rechten Winkel.","Панель выбирает сильнейший пример финального давления осей. Она сопоставляет полюс добро/зло правительства с полюсом популярно/непопулярно населения и показывает отклонение от прямого угла.","El panel elige el ejemplo final más fuerte de presión de ejes. Contrasta el polo bueno/malo del gobierno con el polo popular/impopular de la población y muestra la desviación del ángulo recto.","Il pannello sceglie l'esempio finale più forte di pressione degli assi. Confronta il polo bene/male del governo con il polo popolare/impopolare della popolazione e mostra lo scarto dall'angolo retto.","此图选择最终状态中轴压力最强的例子，对比政府好/恶极点与人口受欢迎/不受欢迎极点，并显示其偏离直角的程度。","この図は最終状態で最も強い軸圧の例を選び、政府の善/悪極と住民の人気/不人気極を対比し、直角からのずれを示します。","이 패널은 최종 상태에서 가장 강한 축 압력 사례를 고르고 정부 선/악 극과 인구 인기/비인기 극을 대비해 직각에서 벗어난 정도를 보여줍니다.","यह पैनल अंतिम स्थिति का सबसे मजबूत अक्ष-दबाव उदाहरण चुनता है, सरकार के अच्छा/बुरा ध्रुव और जनता के लोकप्रिय/अलोकप्रिय ध्रुव को मिलाकर 90° से विचलन दिखाता है।","הלוח בוחר את דוגמת לחץ הצירים החזקה ביותר בסוף. הוא משווה בין קוטב טוב/רע של הממשלה וקוטב פופולרי/לא פופולרי של האוכלוסייה ומראה סטייה מזווית ישרה.","این پنل نیرومندترین نمونه فشار محور در پایان را برمی‌گزیند؛ قطب خوب/بد دولت را با محبوب/نامحبوب مردم می‌سنجد و فاصله از زاویه راست را نشان می‌دهد.","تختار اللوحة أقوى مثال نهائي لضغط المحاور، وتقارن قطب خير/شر الحكومة بقطب محبوب/غير محبوب للسكان وتعرض الانحراف عن الزاوية القائمة.")),
    ("Result: the three market actions", _names("Buy, sell and labor may point in different directions inside one sector. A weak sector is therefore not simply poor; it can be split between action angles and currencies.","Kauf, Verkauf und Arbeit können in einem Sektor in verschiedene Richtungen zeigen. Ein schwacher Sektor ist deshalb nicht einfach arm; er kann zwischen Handlungswinkeln und Währungen gespalten sein.","Покупка, продажа и труд могут указывать в разные стороны внутри одного сектора. Слабый сектор не просто беден; он может быть расколот между углами действий и валютами.","Compra, venta y trabajo pueden apuntar en direcciones distintas dentro de un sector. Un sector débil no es solo pobre; puede estar dividido entre ángulos de acción y monedas.","Acquisto, vendita e lavoro possono puntare in direzioni diverse in un settore. Un settore debole non è semplicemente povero; può essere diviso fra angoli d'azione e valute.","同一部门中购买、销售和劳动可指向不同方向。因此弱部门不只是贫穷，而可能在行动角和货币之间分裂。","一つの部門で購入・販売・労働が別方向を向くことがあります。弱い部門は単に貧しいのではなく、行動角と通貨の間で割れています。","한 부문 안에서 구매, 판매, 노동은 서로 다른 방향을 가리킬 수 있습니다. 약한 부문은 단순히 가난한 것이 아니라 행동 각도와 통화 사이에서 분열된 것입니다.","एक क्षेत्र में खरीद, बिक्री और श्रम अलग दिशाओं में हो सकते हैं। इसलिए कमजोर क्षेत्र केवल गरीब नहीं; वह क्रिया कोणों और मुद्राओं में बँटा हो सकता है।","קנייה, מכירה ועבודה עשויות להצביע לכיוונים שונים באותו מגזר. מגזר חלש אינו רק עני; הוא עשוי להיות מפוצל בין זוויות פעולה ומטבעות.","خرید، فروش و کار در یک بخش می‌توانند به جهت‌های مختلف بروند. بخش ضعیف فقط فقیر نیست؛ ممکن است میان زاویه‌های کنش و ارزها شکافته باشد.","قد تشير الشراء والبيع والعمل إلى اتجاهات مختلفة داخل قطاع واحد. القطاع الضعيف ليس فقيراً فقط؛ قد يكون منقسماً بين زوايا الفعل والعملات.")),
    ("Result: this diagram separates the two main goals", _names("The diagram separates the two goals: right means more well-being, upward means more power. The best corner is coherent power with livable well-being, not simple richness.","Das Diagramm trennt die zwei Ziele: rechts bedeutet mehr Wohlbefinden, oben mehr Macht. Die beste Ecke ist kohärente Macht mit lebbaren Wohlbefinden, nicht einfacher Reichtum.","Диаграмма разделяет две цели: вправо — больше благополучия, вверх — больше власти. Лучший угол — согласованная власть с жизнеспособным благополучием, а не простое богатство.","El diagrama separa dos objetivos: derecha es más bienestar, arriba es más poder. La mejor esquina es poder coherente con bienestar vivible, no simple riqueza.","Il diagramma separa due obiettivi: destra è più benessere, alto è più potere. L'angolo migliore è potere coerente con benessere vivibile, non semplice ricchezza.","图表分离两个目标：向右是更多福祉，向上是更强权力。最佳角落是权力与可生活福祉的连贯，而非简单富有。","図は二つの目標を分けます。右は幸福、上は権力。最良の角は単なる富ではなく、生活可能な幸福と整合した権力です。","그림은 두 목표를 나눕니다: 오른쪽은 복지, 위쪽은 권력. 가장 좋은 구석은 단순한 부가 아니라 살 만한 복지와 일관된 권력입니다.","चित्र दो लक्ष्यों को अलग करता है: दाएँ अधिक कल्याण, ऊपर अधिक शक्ति। अच्छा कोना सरल धन नहीं, बल्कि रहने योग्य कल्याण के साथ सुसंगत शक्ति है।","התרשים מפריד בין שתי מטרות: ימינה יותר רווחה, למעלה יותר עוצמה. הפינה הטובה היא עוצמה עקבית עם רווחה ראויה לחיים, לא עושר פשוט.","نمودار دو هدف را جدا می‌کند: راست یعنی رفاه بیشتر، بالا یعنی قدرت بیشتر. گوشه بهتر، قدرت منسجم با رفاه زیست‌پذیر است نه ثروت ساده.","يفصل الرسم هدفين: اليمين رفاه أكثر، والأعلى قوة أكثر. أفضل زاوية هي قوة متماسكة مع رفاه قابل للعيش، لا مجرد ثراء.")),
    ("Result: the carpet shows", _names("The heat carpet shows whether tension is temporary or structural. Long hot bands mean that government axes, population axes, currency directions and market actions keep missing each other.","Der Wärmeteppich zeigt, ob Spannung vorübergehend oder strukturell ist. Lange heiße Bänder bedeuten, dass Regierungsachsen, Bevölkerungsachsen, Währungsrichtungen und Markthandlungen dauerhaft aneinander vorbeilaufen.","Тепловой ковёр показывает, временно ли напряжение или структурно. Длинные горячие полосы означают, что оси правительства, населения, валют и действий постоянно не совпадают.","La alfombra de calor muestra si la tensión es temporal o estructural. Bandas calientes largas significan que ejes de gobierno, población, monedas y acciones de mercado no encajan.","Il tappeto termico mostra se la tensione è episodica o strutturale. Lunghe bande calde indicano che assi di governo, popolazione, valute e azioni di mercato non si incontrano.","热力地毯显示张力是暂时还是结构性的。长热带表示政府轴、人口轴、货币方向和市场行动持续错位。","ヒートカーペットは緊張が一時的か構造的かを示します。長い熱い帯は、政府軸・住民軸・通貨方向・市場行動が合わないことを意味します。","열 카펫은 긴장이 일시적인지 구조적인지 보여줍니다. 긴 뜨거운 띠는 정부축, 인구축, 통화 방향, 시장 행동이 계속 어긋남을 뜻합니다.","ताप-पट्टी दिखाती है तनाव अस्थायी है या संरचनात्मक। लंबी गर्म पट्टियाँ बताती हैं कि सरकार, जनता, मुद्रा दिशा और बाज़ार क्रिया बार-बार मेल नहीं खातीं।","שטיח החום מראה אם המתח זמני או מבני. רצועות חמות ארוכות פירושן שצירי ממשלה, אוכלוסייה, מטבע ופעולות שוק ממשיכים להחמיץ זה את זה.","فرش حرارتی نشان می‌دهد تنش گذراست یا ساختاری. نوارهای داغ بلند یعنی محورهای دولت، مردم، ارز و کنش بازار مدام نامنطبق‌اند.","تُظهر البسطة الحرارية هل التوتر مؤقت أم بنيوي. الأشرطة الحارة الطويلة تعني أن محاور الحكومة والسكان والعملات وأفعال السوق لا تتلاقى باستمرار.")),
    ("Result: each arrow lists", _names("Each arrow lists traded quantity and angular work. A route may move few goods but still be expensive when its trade currency is far from the exporter's home vector.","Jeder Pfeil zeigt Handelsmenge und Umlenkungsarbeit. Eine Route kann wenig Güter bewegen und trotzdem teuer sein, wenn ihre Handelswährung weit vom Heimatvektor des Exporteurs entfernt ist.","Каждая стрелка показывает объём торговли и угловую работу. Маршрут может вести мало благ, но быть дорогим, если валюта сделки далеко от домашнего вектора экспортёра.","Cada flecha muestra cantidad comerciada y trabajo angular. Una ruta puede mover pocos bienes y aun así ser costosa si su moneda comercial está lejos del vector local del exportador.","Ogni freccia mostra quantità scambiata e lavoro angolare. Una rotta può muovere pochi beni ed essere costosa se la valuta commerciale è lontana dal vettore domestico dell'esportatore.","每个箭头显示交易数量和角度功。若贸易货币远离出口方本国向量，即使货物流量小，路线也可能很昂贵。","各矢印は取引量と角度仕事を示します。貿易通貨が輸出国の自国ベクトルから遠いと、少量の財でも高コストになります。","각 화살표는 거래량과 각도 일을 보여줍니다. 무역 통화가 수출국 자국 벡터에서 멀면 적은 재화 흐름도 비싸질 수 있습니다.","हर तीर व्यापार मात्रा और कोणीय कार्य बताता है। व्यापार मुद्रा निर्यातक के घरेलू वेक्टर से दूर हो तो थोड़ी मात्रा भी महँगी हो सकती है।","כל חץ מציג כמות מסחר ועבודה זוויתית. נתיב יכול להזיז מעט טובין ועדיין להיות יקר אם מטבע המסחר רחוק מווקטור הבית של היצואן.","هر پیکان مقدار تجارت و کار زاویه‌ای را نشان می‌دهد. اگر ارز تجارت از بردار خانگی صادرکننده دور باشد، حتی جریان کم کالا هم پرهزینه است.","كل سهم يبيّن الكمية المتداولة والعمل الزاوي. قد ينقل المسار سلعاً قليلة لكنه يكون مكلفاً إذا ابتعدت عملة التجارة عن متجه المصدّر المحلي.")),
    ("Result: the trail is a history", _names("The trail records direction changes, not length changes. Stable trails keep a currency identity; turning trails show market and government pull into a new orbit.","Die Spur zeigt Richtungsänderungen, keine Längenänderungen. Stabile Spuren halten Währungsidentität; drehende Spuren zeigen Zug von Markt und Regierung in einen neuen Orbit.","След записывает изменения направления, а не длины. Стабильный след сохраняет идентичность валюты; поворотный след показывает тягу рынка и правительства к новой орбите.","El rastro registra cambios de dirección, no de longitud. Rastros estables conservan identidad monetaria; rastros giratorios muestran tracción de mercado y gobierno hacia una órbita nueva.","La traccia registra cambi di direzione, non di lunghezza. Tracce stabili conservano identità; tracce che girano mostrano la spinta di mercato e governo verso una nuova orbita.","轨迹记录方向变化，而非长度变化。稳定轨迹保持货币身份；转向轨迹显示市场和政府把它拉入新轨道。","軌跡は長さではなく方向の変化を記録します。安定した軌跡は通貨の同一性を保ち、曲がる軌跡は市場と政府の引力を示します。","흔적은 길이가 아니라 방향 변화를 기록합니다. 안정된 흔적은 통화 정체성을 유지하고, 도는 흔적은 시장과 정부가 새 궤도로 끄는 것을 보여줍니다.","रास्ता लंबाई नहीं, दिशा परिवर्तन दर्ज करता है। स्थिर रास्ता मुद्रा पहचान रखता है; मुड़ता रास्ता बाज़ार और सरकार के नए कक्ष में खिंचाव को दिखाता है।","העקבה מתעדת שינויי כיוון, לא שינויי אורך. עקבה יציבה שומרת זהות מטבע; עקבה מסתובבת מראה משיכה של שוק וממשלה למסלול חדש.","رد تغییر جهت را ثبت می‌کند نه تغییر طول. رد پایدار هویت ارز را حفظ می‌کند؛ رد چرخان کشش بازار و دولت به مدار تازه را نشان می‌دهد.","يسجل الأثر تغيّر الاتجاه لا تغيّر الطول. الأثر المستقر يحافظ على هوية العملة؛ والأثر الدوّار يبين جذب السوق والحكومة إلى مدار جديد.")),
    ("Result: the mosaic translates", _names("The mosaic turns final need coverage into blocks. Strong blocks mean a sector is materially covered and angularly usable; weak blocks show missing production, trade access or angle fit.","Das Mosaik übersetzt finale Bedarfsdeckung in Blöcke. Starke Blöcke bedeuten materielle Deckung und Winkelnutzbarkeit; schwache Blöcke zeigen fehlende Produktion, Handelszugang oder Winkelpassung.","Мозаика переводит финальное покрытие потребностей в блоки. Сильные блоки — материальное покрытие и угловая пригодность; слабые — нехватка производства, торговли или углового совпадения.","El mosaico convierte la cobertura final de necesidades en bloques. Bloques fuertes indican cobertura material y uso angular; débiles muestran falta de producción, acceso comercial o ajuste angular.","Il mosaico traduce la copertura finale in blocchi. Blocchi forti significano copertura materiale e uso angolare; blocchi deboli mostrano mancanza di produzione, commercio o adattamento angolare.","马赛克把最终需求覆盖转为方块。强方块表示物质覆盖且角度可用；弱方块显示生产、贸易通道或角度匹配不足。","モザイクは最終需要充足をブロック化します。強いブロックは物質充足と角度利用可能性、弱いブロックは生産・貿易アクセス・角度適合の不足を示します。","모자이크는 최종 필요 충족을 블록으로 바꿉니다. 강한 블록은 물질적 충족과 각도 사용 가능성을, 약한 블록은 생산·무역 접근·각도 적합 부족을 뜻합니다.","मोज़ेक अंतिम जरूरत पूर्ति को ब्लॉकों में बदलता है। मजबूत ब्लॉक सामग्री और कोणीय उपयोगिता दिखाते हैं; कमजोर ब्लॉक उत्पादन, व्यापार पहुँच या कोण मेल की कमी बताते हैं।","המוזאיקה מתרגמת כיסוי צרכים סופי לבלוקים. בלוקים חזקים מציינים כיסוי חומרי ושימוש זוויתי; חלשים מצביעים על חסר בייצור, מסחר או התאמת זווית.","موزاییک پوشش نیاز نهایی را به بلوک تبدیل می‌کند. بلوک قوی یعنی پوشش مادی و کاربرد زاویه‌ای؛ ضعیف یعنی کمبود تولید، دسترسی تجارت یا تناسب زاویه.","تحوّل الفسيفساء تغطية الحاجة النهائية إلى كتل. الكتل القوية تعني تغطية مادية وقابلية زاوية؛ والضعيفة تعني نقص إنتاج أو تجارة أو توافق زاوي.")),
    ("Result: each wave is", _names("Each wave is the vector-Euro count per unit across sectors. Peaks are not longer Euros; they mark scarcity, mismatch or currency-distance friction.","Jede Welle ist die Vektor-Euro-Zahl pro Einheit über Sektoren. Spitzen sind keine längeren Euros; sie markieren Mangel, Fehlpassung oder Währungsabstand.","Каждая волна — счёт вектор-евро на единицу по секторам. Пики не являются длинными евро; они отмечают дефицит, несовпадение или валютную дистанцию.","Cada ola es el conteo vector-euro por unidad en sectores. Los picos no son euros más largos; marcan escasez, desajuste o distancia monetaria.","Ogni onda è il conteggio vettore-euro per unità nei settori. I picchi non sono euro più lunghi; segnano scarsità, disadattamento o distanza valutaria.","每条波是各部门每单位的向量欧元计数。峰值不是更长欧元，而是稀缺、错配或货币距离摩擦。","各波は部門ごとの単位あたりベクトル・ユーロ数です。山は長いユーロではなく、不足・不一致・通貨距離の摩擦です。","각 파동은 부문별 단위당 벡터-유로 수입니다. 봉우리는 더 긴 유로가 아니라 부족, 불일치, 통화 거리 마찰을 뜻합니다.","हर लहर क्षेत्रों में प्रति इकाई वेक्टर-यूरो गिनती है। शिखर लंबे यूरो नहीं; वे कमी, असंगति या मुद्रा दूरी का घर्षण हैं।","כל גל הוא ספירת וקטור-אירו ליחידה לפי מגזרים. פסגות אינן אירו ארוך יותר; הן מציינות מחסור, אי-התאמה או חיכוך מרחק מטבע.","هر موج شمار بردار-یورو به ازای واحد در بخش‌هاست. قله‌ها یوروی بلندتر نیستند؛ کمبود، ناهماهنگی یا اصطکاک فاصله ارز را نشان می‌دهند.","كل موجة هي عدد متجه-اليورو لكل وحدة عبر القطاعات. القمم ليست يورو أطول؛ إنها ندرة أو عدم توافق أو احتكاك مسافة العملة.")),
    ("Result: the quadrant picture", _names("The quadrant gives a political-economic reading: resonance can join power and well-being; power lock dominates lived welfare; fracture means the angle system is unstable.","Der Quadrant liest politisch-ökonomisch: Resonanz kann Macht und Wohlbefinden verbinden; Machtverschluss dominiert gelebtes Wohl; Bruch bedeutet instabiles Winkelsystem.","Квадрант даёт политико-экономическое чтение: резонанс соединяет власть и благополучие; блок власти доминирует над жизненным благом; разлом — нестабильная угловая система.","El cuadrante da una lectura político-económica: la resonancia une poder y bienestar; el bloqueo de poder domina el bienestar vivido; la fractura indica sistema angular inestable.","Il quadrante dà una lettura politico-economica: la risonanza unisce potere e benessere; il blocco di potere domina il benessere vissuto; la frattura indica instabilità angolare.","象限给出政治经济解读：共振可结合权力与福祉；权力锁定压倒生活福祉；断裂表示角度系统不稳定。","象限は政治経済的読解です。共鳴は権力と幸福を結び、権力ロックは生活上の幸福を支配し、亀裂は角度システムの不安定を示します。","사분면은 정치경제적 해석입니다. 공명은 권력과 복지를 결합할 수 있고, 권력 잠금은 삶의 복지를 지배하며, 균열은 각도 체계 불안정을 뜻합니다.","चतुर्थांश राजनीतिक-आर्थिक पढ़ाई देता है: अनुनाद शक्ति और कल्याण जोड़ता है; शक्ति-लॉक जीवित कल्याण पर हावी होता है; टूटन अस्थिर कोण प्रणाली है।","הרביע נותן קריאה פוליטית-כלכלית: תהודה מחברת עוצמה ורווחה; נעילת עוצמה משתלטת על רווחה חיה; שבר מציין מערכת זוויות לא יציבה.","ربع نمودار خوانش سیاسی-اقتصادی می‌دهد: تشدید می‌تواند قدرت و رفاه را پیوند دهد؛ قفل قدرت رفاه زیسته را غالب می‌کند؛ شکست یعنی نظام زاویه‌ای ناپایدار.","يعطي الربع قراءة سياسية-اقتصادية: الرنين يجمع القوة والرفاه؛ قفل القوة يهيمن على الرفاه المعيش؛ والكسر يعني نظام زوايا غير مستقر.")),
    ("Result: this final table", _names("The final table silently runs several scenarios with the same rules. Differences are angle-system differences, not Euro-length differences.","Die Abschlusstabelle führt mehrere Szenarien still mit denselben Regeln aus. Unterschiede sind Winkelsystem-Unterschiede, keine Euro-Längen-Unterschiede.","Финальная таблица тихо запускает несколько сценариев по тем же правилам. Различия — различия угловой системы, а не длины евро.","La tabla final ejecuta varios escenarios con las mismas reglas. Las diferencias son del sistema angular, no de longitud del euro.","La tabella finale esegue vari scenari con le stesse regole. Le differenze sono del sistema angolare, non della lunghezza dell'euro.","最终表用相同规则静默运行多个情景。差异来自角度系统，而不是欧元长度。","最終表は同じ規則で複数シナリオを静かに実行します。違いはユーロ長ではなく角度システムの違いです。","최종 표는 같은 규칙으로 여러 시나리오를 조용히 실행합니다. 차이는 유로 길이가 아니라 각도 시스템의 차이입니다.","अंतिम तालिका समान नियमों से कई परिदृश्य चलाती है। अंतर कोण प्रणाली के हैं, यूरो लंबाई के नहीं।","הטבלה הסופית מריצה בשקט כמה תרחישים לפי אותם כללים. ההבדלים הם הבדלי מערכת זווית, לא הבדלי אורך אירו.","جدول نهایی چند سناریو را با همان قواعد بی‌صدا اجرا می‌کند. تفاوت‌ها تفاوت نظام زاویه‌ای‌اند، نه طول یورو.","يشغّل الجدول النهائي عدة سيناريوهات بالقواعد نفسها. الفروق هي فروق نظام الزوايا، لا فروق طول اليورو.")),
]

SCENARIO_MEANING_SUMMARIES = [
    ("Scenario meaning: resonance keeps", _names("Scenario reading: resonance keeps axes coherent; power pursuit pulls action to state/currency; well-being pursuit pulls action to the popular side; fragmented angles scatter the system.","Szenario-Lesart: Resonanz hält Achsen kohärent; Machtstreben zieht Handlung zu Staat/Währung; Wohlbefinden zieht zur Beliebt-Seite; Zersplitterung streut das System.","Чтение сценария: резонанс держит оси согласованными; власть тянет к государству/валюте; благополучие к популярной стороне; фрагментация рассыпает систему.","Lectura del escenario: la resonancia mantiene ejes coherentes; el poder tira hacia Estado/moneda; el bienestar hacia lo popular; la fragmentación dispersa el sistema.","Lettura dello scenario: la risonanza tiene coerenti gli assi; il potere tira verso stato/valuta; il benessere verso il lato popolare; la frammentazione disperde il sistema.","情景解读：共振保持轴的连贯；权力追求拉向国家/货币；福祉追求拉向受欢迎侧；碎片化会分散系统。","シナリオ読解：共鳴は軸を整合させ、権力志向は国家/通貨側へ、幸福志向は人気側へ引き、断片化は体系を散らします。","시나리오 해석: 공명은 축을 일관되게 유지하고, 권력 추구는 국가/통화 쪽으로, 복지 추구는 인기 쪽으로 끌며, 분열은 체계를 흩뜨립니다.","परिदृश्य पढ़ाई: अनुनाद अक्षों को सुसंगत रखता है; शक्ति राज्य/मुद्रा की ओर खींचती है; कल्याण लोकप्रिय ओर खींचता है; विखंडन प्रणाली फैलाता है।","קריאת תרחיש: תהודה שומרת צירים עקביים; חתירה לעוצמה מושכת למדינה/מטבע; רווחה לצד הפופולרי; פיצול מפזר את המערכת.","خوانش سناریو: تشدید محورها را منسجم نگه می‌دارد؛ قدرت کنش را به دولت/ارز می‌کشد؛ رفاه به سمت محبوب؛ پراکندگی سامانه را پخش می‌کند.","قراءة السيناريو: الرنين يحافظ على تماسك المحاور؛ السعي للقوة يجذب نحو الدولة/العملة؛ الرفاه نحو الجانب المحبوب؛ والتشتت يبعثر النظام.")),
    ("Scenario meaning: in resonance", _names("Scenario reading: resonance clusters actions; power may force work near state currency; scarcity raises buy counts; trade boom strengthens sell vectors.","Szenario-Lesart: Resonanz bündelt Handlungen; Macht kann Arbeit nahe an Staatswährung drücken; Mangel verteuert Kaufzahlen; Handelsboom stärkt Verkaufsvektoren.","Чтение сценария: резонанс группирует действия; власть может прижать труд к госвалюте; дефицит повышает счета покупки; торговый бум усиливает продажные векторы.","Lectura del escenario: la resonancia agrupa acciones; el poder puede forzar trabajo cerca de la moneda estatal; la escasez encarece compras; el auge comercial fortalece ventas.","Lettura dello scenario: la risonanza raggruppa azioni; il potere può spingere il lavoro vicino alla valuta statale; la scarsità alza i conteggi d'acquisto; il boom commerciale rafforza le vendite.","情景解读：共振聚合行动；权力会把劳动压向国家货币；稀缺提高购买计数；贸易繁荣增强销售向量。","シナリオ読解：共鳴は行動を集め、権力は労働を国家通貨近くへ押し、不足は購入数を上げ、貿易ブームは販売ベクトルを強めます。","시나리오 해석: 공명은 행동을 묶고, 권력은 노동을 국가 통화 근처로 몰 수 있으며, 부족은 구매 수를 올리고, 무역 붐은 판매 벡터를 강화합니다.","परिदृश्य पढ़ाई: अनुनाद क्रियाएँ जोड़ता है; शक्ति काम को राज्य-मुद्रा के पास धकेल सकती है; कमी खरीद गिनती बढ़ाती है; व्यापार-बूम बिक्री वेक्टर मजबूत करता है।","קריאת תרחיש: תהודה מקבצת פעולות; עוצמה עשויה לכפות עבודה ליד מטבע המדינה; מחסור מייקר ספירת קנייה; בום מסחר מחזק וקטורי מכירה.","خوانش سناریو: تشدید کنش‌ها را خوشه می‌کند؛ قدرت می‌تواند کار را نزدیک ارز دولت ببرد؛ کمبود شمار خرید را بالا می‌برد؛ رونق تجارت بردار فروش را نیرومند می‌کند.","قراءة السيناريو: الرنين يجمّع الأفعال؛ القوة قد تدفع العمل قرب عملة الدولة؛ الندرة ترفع عدّ الشراء؛ وازدهار التجارة يقوي متجهات البيع.")),
]

def translate_result_summary(lang: str, key: str, en: str) -> str:
    lang = normalize_lang(lang)
    label = _names("Scenario meaning","Szenario-Bedeutung","Смысл сценария","Sentido del escenario","Significato dello scenario","情景含义","シナリオの意味","시나리오 의미","परिदृश्य अर्थ","משמעות התרחיש","معنای سناریو","معنى السيناريو")[lang] if key == "scenario_meaning" or en.startswith("Scenario meaning:") else PH.get(lang, {}).get("result", "Result")
    sources = SCENARIO_MEANING_SUMMARIES if key == "scenario_meaning" or en.startswith("Scenario meaning:") else RESULT_SUMMARIES
    for prefix, mapping in sources:
        if en.startswith(prefix):
            return f"{label}: {mapping[lang]}"
    fallback = _names("The figure reads the final state in the angular system. It compares power, well-being, tension and vector direction while all Euro-vector lengths remain equal.","Die Abbildung liest den Endzustand im Winkelsystem. Sie vergleicht Macht, Wohlbefinden, Spannung und Vektorrichtung, während alle Euro-Vektorlängen gleich bleiben.","Фигура читает финальное состояние в угловой системе: власть, благополучие, напряжение и направление векторов при равной длине евро-векторов.","La figura lee el estado final en el sistema angular: poder, bienestar, tensión y dirección vectorial con longitudes euro-vector iguales.","La figura legge lo stato finale nel sistema angolare: potere, benessere, tensione e direzione vettoriale con lunghezze euro-vettore uguali.","图像在角度系统中解读最终状态，比较权力、福祉、张力和向量方向，同时所有欧元向量长度相等。","図は角度システムで最終状態を読み、権力・幸福・緊張・ベクトル方向を比較します。すべてのユーロ・ベクトル長は同じです。","그림은 각도 체계에서 최종 상태를 읽고 권력, 복지, 긴장, 벡터 방향을 비교합니다. 모든 유로 벡터 길이는 같습니다.","चित्र अंतिम स्थिति को कोणीय प्रणाली में पढ़ता है: शक्ति, कल्याण, तनाव और वेक्टर दिशा, जबकि सभी यूरो-वेक्टर लंबाई समान है।","האיור קורא את המצב הסופי במערכת הזוויתית ומשווה עוצמה, רווחה, מתח וכיוון וקטור, כשכל אורכי וקטור-אירו שווים.","شکل وضعیت نهایی را در نظام زاویه‌ای می‌خواند و قدرت، رفاه، تنش و جهت بردار را می‌سنجد، در حالی که همه طول‌های بردار-یورو برابرند.","يقرأ الشكل الحالة النهائية في النظام الزاوي ويقارن القوة والرفاه والتوتر واتجاه المتجه، مع بقاء أطوال متجهات اليورو متساوية.")[lang]
    return f"{label}: {fallback}"


# Compact semantic translations for recurring explanation rows.
COMMON.update({
    "0..100%": _names("0..100%","0..100%","0..100%","0..100%","0..100%","0..100%","0..100%","0..100%","0..100%","0..100%","0..100%","0..100%"),
    "country→country": _names("country→country","Land→Land","страна→страна","país→país","paese→paese","国家→国家","国→国","국가→국가","देश→देश","מדינה→מדינה","کشور→کشور","دولة→دولة"),
    "UTF-8 mini chart": _names("UTF-8 mini chart","UTF-8-Minikurve","мини-график UTF-8","minigráfico UTF-8","mini grafico UTF-8","UTF-8 迷你图","UTF-8 ミニチャート","UTF-8 미니 차트","UTF-8 लघु चार्ट","תרשים קטן UTF-8","نمودار کوچک UTF-8","رسم مصغر UTF-8"),
    "arithmetic mean": _names("arithmetic mean","arithmetischer Mittelwert","среднее арифметическое","media aritmética","media aritmetica","算术平均值","算術平均","산술 평균","अंकगणितीय औसत","ממוצע חשבוני","میانگین حسابی","متوسط حسابي"),
})

AUTO_PHRASES = [
    ("The three competing Euro vectors.", _names("The three competing Euro vectors.","Die drei konkurrierenden Euro-Vektoren.","Три конкурирующих евро-вектора.","Los tres euro-vectores competidores.","I tre euro-vettori concorrenti.","三个竞争的欧元向量。","競合する三つのユーロ・ベクトル。","경쟁하는 세 유로 벡터.","तीन प्रतिस्पर्धी यूरो-वेक्टर।","שלושת וקטורי האירו המתחרים.","سه بردار یوروی رقابتی.","متجهات اليورو الثلاثة المتنافسة.")),
    ("Vector length.", _names("Vector length: it remains 1.000 for every currency.","Vektorlänge: Sie bleibt bei jeder Währung 1.000.","Длина вектора: у каждой валюты остаётся 1.000.","Longitud vectorial: permanece 1.000 en cada moneda.","Lunghezza vettoriale: resta 1.000 per ogni valuta.","向量长度：每种货币都保持 1.000。","ベクトル長：各通貨で 1.000 のまま。","벡터 길이: 모든 통화에서 1.000 유지.","वेक्टर लंबाई: हर मुद्रा में 1.000 रहती है।","אורך וקטור: נשאר 1.000 בכל מטבע.","طول بردار: برای هر ارز 1.000 می‌ماند.","طول المتجه: يبقى 1.000 لكل عملة.")),
    ("Current direction", _names("Current direction of a currency on the ring.","Aktuelle Richtung einer Währung auf dem Ring.","Текущее направление валюты на кольце.","Dirección actual de la moneda en el anillo.","Direzione attuale della valuta sull'anello.","货币在圆环上的当前方向。","リング上の通貨の現在方向。","고리 위 통화의 현재 방향.","वृत्त पर मुद्रा की वर्तमान दिशा।","הכיוון הנוכחי של המטבע על הטבעת.","جهت کنونی ارز روی حلقه.","الاتجاه الحالي للعملة على الحلقة.")),
    ("Part of this tick", _names("Share of this tick's transaction flow captured by this angle.","Anteil des Transaktionsflusses dieses Ticks, der vom Winkel gebunden wird.","Доля потока транзакций этого тика, захваченная углом.","Parte del flujo de transacciones de este tick captada por el ángulo.","Quota del flusso di transazioni di questo tick catturata dall'angolo.","本周期交易流中被该角度吸引的份额。","このティックの取引流のうち角度が捕まえた割合。","이번 틱 거래 흐름 중 이 각도가 잡은 몫.","इस टिक के लेन-देन प्रवाह का वह हिस्सा जिसे यह कोण पकड़ता है।","חלק מזרם העסקאות של הטיק שהזווית קולטת.","سهم جریان تراکنش این تیک که زاویه جذب می‌کند.","حصة تدفق معاملات هذه الدورة التي تلتقطها الزاوية.")),
    ("Accumulated attachment", _names("Accumulated attachment of market action and home government to the vector.","Aufgebaute Bindung von Markthandlung und Heimatregierung an den Vektor.","Накопленная привязка рыночного действия и домашнего правительства к вектору.","Adhesión acumulada de la acción de mercado y del gobierno local al vector.","Legame accumulato di azione di mercato e governo interno al vettore.","市场行动和本国政府对该向量的累积绑定。","市場行動と自国政府のベクトルへの蓄積された結合。","시장 행동과 본국 정부가 벡터에 쌓은 결속.","बाज़ार क्रिया और घरेलू सरकार का वेक्टर से संचित बंधन।","היצמדות מצטברת של פעולת השוק והממשלה הביתית לווקטור.","وابستگی انباشته کنش بازار و دولت خانگی به بردار.","ارتباط متراكم لحركة السوق والحكومة المحلية بالمتجه.")),
    ("Angle distance", _names("Angle distance; this is not a money exchange rate.","Winkelabstand; das ist kein Geld-Wechselkurs.","Угловая дистанция; это не денежный курс.","Distancia angular; no es un tipo de cambio monetario.","Distanza angolare; non è un tasso di cambio monetario.","角度距离；这不是货币汇率。","角度距離。これは貨幣の為替レートではありません。","각도 거리; 돈의 환율이 아니다.","कोणीय दूरी; यह धन विनिमय दर नहीं है।","מרחק זוויתי; זה אינו שער חליפין כספי.","فاصله زاویه‌ای؛ نرخ تبدیل پولی نیست.","مسافة زاوية؛ ليست سعر صرف مالي.")),
    ("Angular resonance", _names("Angular resonance: 1 same direction, 0 opposite direction.","Winkelklang: 1 gleiche Richtung, 0 Gegenrichtung.","Угловой резонанс: 1 одно направление, 0 противоположное.","Resonancia angular: 1 misma dirección, 0 dirección opuesta.","Risonanza angolare: 1 stessa direzione, 0 direzione opposta.","角度共振：1 为同向，0 为反向。","角度共鳴：1 は同方向、0 は反対方向。","각도 공명: 1 같은 방향, 0 반대 방향.","कोणीय अनुनाद: 1 समान दिशा, 0 विपरीत दिशा।","תהודה זוויתית: 1 אותו כיוון, 0 כיוון נגדי.","تشدید زاویه‌ای: 1 هم‌جهت، 0 خلاف‌جهت.","رنين زاوي: 1 الاتجاه نفسه، 0 الاتجاه المعاكس.")),
    ("Action angle", _names("Action angle of labor in a sector.","Handlungswinkel der Arbeit in einem Sektor.","Угол трудового действия в секторе.","Ángulo de acción del trabajo en un sector.","Angolo d'azione del lavoro in un settore.","某部门劳动行动的角度。","部門内の労働行動角。","부문에서 노동 행동의 각도.","किसी क्षेत्र में श्रम क्रिया का कोण।","זווית פעולת העבודה במגזר.","زاویه کنش کار در یک بخش.","زاوية فعل العمل في قطاع.")),
    ("Currency whose angle", _names("Currency whose angle fits the labor action best.","Währung, deren Winkel am besten zur Arbeitsentscheidung passt.","Валюта, чей угол лучше всего подходит к труду.","Moneda cuyo ángulo encaja mejor con la acción laboral.","Valuta il cui angolo si adatta meglio al lavoro.","角度最适合劳动行动的货币。","労働行動に最も合う角度の通貨。","노동 행동에 각도가 가장 잘 맞는 통화.","जिस मुद्रा का कोण श्रम क्रिया से सबसे अच्छा मेल खाता है।","מטבע שהזווית שלו מתאימה ביותר לפעולת העבודה.","ارزی که زاویه‌اش با کنش کار بهتر می‌خواند.","العملة التي تلائم زاويتها فعل العمل أكثر.")),
    ("Abstract labor hours", _names("Abstract labor hours allocated in this tick.","Abstrakte Arbeitsstunden dieses Ticks.","Абстрактные трудовые часы в этом тике.","Horas laborales abstractas asignadas en este tick.","Ore di lavoro astratte assegnate in questo tick.","本周期分配的抽象劳动小时。","このティックに割り当てた抽象労働時間。","이번 틱에 배정된 추상 노동시간.","इस टिक में बाँटे गए अमूर्त श्रम-घंटे।","שעות עבודה מופשטות שהוקצו בטיק זה.","ساعت‌های کار انتزاعی تخصیص‌یافته در این تیک.","ساعات عمل مجردة مخصصة في هذه الدورة.")),
    ("Production created", _names("Production created by labor and productivity.","Produktion aus Arbeit und Produktivität.","Производство, созданное трудом и продуктивностью.","Producción creada por trabajo y productividad.","Produzione creata da lavoro e produttività.","由劳动和生产率产生的产量。","労働と生産性で生まれた生産。","노동과 생산성이 만든 생산량.","श्रम और उत्पादकता से बनी उत्पादन मात्रा।","ייצור שנוצר מעבודה ופריון.","تولید حاصل از کار و بهره‌وری.","إنتاج ناتج عن العمل والإنتاجية.")),
    ("Fatigue", _names("Fatigue from work near the unpopular pole.","Ermüdung durch Arbeit nahe am Unbeliebt-Pol.","Усталость от работы близко к непопулярному полюсу.","Fatiga por trabajo cerca del polo impopular.","Fatica da lavoro vicino al polo impopolare.","靠近不受欢迎极点的劳动疲劳。","不人気極の近くで働くことによる疲労。","비인기 극 가까운 노동에서 생기는 피로.","अलोकप्रिय ध्रुव के पास श्रम से थकान।","עייפות מעבודה ליד הקוטב הלא פופולרי.","خستگی از کار نزدیک قطب نامحبوب.","إرهاق من العمل قرب القطب غير المحبوب.")),
    ("Population demand", _names("Population demand in the sector.","Bevölkerungsbedarf im Sektor.","Потребность населения в секторе.","Demanda de la población en el sector.","Domanda della popolazione nel settore.","该部门的人口需求。","部門における住民需要。","부문의 인구 수요.","क्षेत्र में जन-आवश्यकता।","ביקוש האוכלוסייה במגזר.","تقاضای جمعیت در بخش.","طلب السكان في القطاع.")),
    ("Production minus", _names("Production minus exports plus imports.","Produktion minus Exporte plus Importe.","Производство минус экспорт плюс импорт.","Producción menos exportaciones más importaciones.","Produzione meno esportazioni più importazioni.","生产减出口加进口。","生産から輸出を引き、輸入を足す。","생산에서 수출을 빼고 수입을 더함.","उत्पादन minus निर्यात plus आयात।","ייצור פחות יצוא ועוד יבוא.","تولید منهای صادرات به‌علاوه واردات.","الإنتاج ناقص الصادرات زائد الواردات.")),
    ("Need covered", _names("Need covered by final supply.","Bedarf, der durch Endversorgung gedeckt wird.","Потребность, покрытая конечным снабжением.","Necesidad cubierta por la oferta final.","Bisogno coperto dall'offerta finale.","最终供给覆盖的需求。","最終供給で満たされた需要。","최종 공급이 충족한 수요.","अंतिम आपूर्ति से पूरी हुई ज़रूरत।","צורך שמכוסה באספקה הסופית.","نیازی که عرضه نهایی پوشش می‌دهد.","الحاجة التي يغطيها العرض النهائي.")),
    ("Number of equal", _names("Number of equal vector-Euro units per goods unit.","Anzahl gleich langer Vektor-Euro-Einheiten pro Gütereinheit.","Число равных единиц вектор-евро на единицу блага.","Número de unidades vector-euro iguales por unidad de bien.","Numero di unità vettore-euro uguali per unità di bene.","每单位商品所需的等长向量欧元数量。","財単位あたりの同長ベクトル・ユーロ数。","재화 단위당 같은 길이의 벡터-유로 수.","प्रति वस्तु इकाई समान वेक्टर-यूरो की संख्या।","מספר יחידות וקטור-אירו שוות לכל יחידת טובין.","تعداد واحدهای بردار-یوروی برابر برای هر واحد کالا.","عدد وحدات متجه-اليورو المتساوية لكل وحدة سلعة.")),
    ("Buy and sell", _names("Buy and sell action angles.","Kauf- und Verkaufs-Handlungswinkel.","Углы действий покупки и продажи.","Ángulos de acción de compra y venta.","Angoli d'azione di acquisto e vendita.","购买和销售行动角。","購入と販売の行動角。","구매와 판매 행동 각도.","खरीद और बिक्री क्रिया कोण।","זוויות פעולת קנייה ומכירה.","زاویه‌های کنش خرید و فروش.","زوايا فعل الشراء والبيع.")),
    ("Best currency", _names("Best currency for the buy or sell angle.","Beste Währung für Kauf- oder Verkaufswinkel.","Лучшая валюта для угла покупки или продажи.","Mejor moneda para el ángulo de compra o venta.","Migliore valuta per l'angolo di acquisto o vendita.","最适合买入或卖出角度的货币。","購入または販売角に最も合う通貨。","구매/판매 각도에 가장 맞는 통화.","खरीद या बिक्री कोण के लिए श्रेष्ठ मुद्रा।","המטבע הטוב ביותר לזווית קנייה או מכירה.","بهترین ارز برای زاویه خرید یا فروش.","أفضل عملة لزاوية الشراء أو البيع.")),
    ("Average orthogonal", _names("Average deviation between good/evil and popular/unpopular axes.","Mittlere Abweichung der Gut/Böse- zur Beliebt/Unbeliebt-Achse.","Среднее отклонение между осями добро/зло и популярно/непопулярно.","Desviación media entre ejes bueno/malo y popular/impopular.","Deviazione media tra assi bene/male e popolare/impopolare.","好/恶轴与受欢迎/不受欢迎轴的平均偏差。","善悪軸と人気/不人気軸の平均ずれ。","선/악 축과 인기/비인기 축의 평균 편차.","अच्छा/बुरा और लोकप्रिय/अलोकप्रिय अक्षों की औसत विचलन।","סטייה ממוצעת בין ציר טוב/רע לציר פופולרי/לא פופולרי.","انحراف میانگین میان محور خوب/بد و محبوب/نامحبوب.","الانحراف المتوسط بين محوري الخير/الشر والمحبوب/غير المحبوب.")),
    ("Exporter to importer", _names("Exporter to importer.","Exportland zu Importland.","Экспортёр к импортёру.","Exportador a importador.","Da esportatore a importatore.","出口国到进口国。","輸出国から輸入国へ。","수출국에서 수입국으로.","निर्यातक से आयातक।","מיצואן ליבואן.","از صادرکننده به واردکننده.","من المصدّر إلى المستورد.")),
    ("Traded quantity", _names("Traded quantity.","Gehandelte Menge.","Торгуемое количество.","Cantidad comerciada.","Quantità scambiata.","交易数量。","取引量。","거래 수량.","व्यापारित मात्रा।","כמות נסחרת.","مقدار معامله‌شده.","الكمية المتداولة.")),
    ("Currency angle used", _names("Currency angle used by the joint trade action.","Währungswinkel der gemeinsamen Handelshandlung.","Угол валюты, используемый совместным торговым действием.","Ángulo monetario usado por la acción comercial conjunta.","Angolo valutario usato dall'azione commerciale congiunta.","共同贸易行动使用的货币角度。","共同貿易行動が使う通貨角。","공동 무역 행동이 쓰는 통화 각도.","संयुक्त व्यापार क्रिया द्वारा उपयोग मुद्रा कोण।","זווית מטבע המשמשת את פעולת המסחר המשותפת.","زاویه ارزی که کنش تجاری مشترک به‌کار می‌برد.","زاوية العملة المستخدمة في فعل التجارة المشترك.")),
    ("Mean action angle", _names("Mean action angle between exporter sell and importer buy.","Mittlerer Handlungswinkel aus Export-Verkauf und Import-Kauf.","Средний угол между продажей экспортёра и покупкой импортёра.","Ángulo medio entre venta del exportador y compra del importador.","Angolo medio tra vendita dell'esportatore e acquisto dell'importatore.","出口方卖出与进口方买入之间的平均行动角。","輸出者の販売と輸入者の購入の平均行動角。","수출자의 판매와 수입자의 구매 사이 평균 행동 각.","निर्यातक बिक्री और आयातक खरीद के बीच औसत क्रिया कोण।","זווית פעולה ממוצעת בין מכירת יצואן לקניית יבואן.","زاویه کنش میانگین میان فروش صادرکننده و خرید واردکننده.","زاوية الفعل المتوسطة بين بيع المصدّر وشراء المستورد.")),
    ("Angular work", _names("Angular work: vector-Euro amount times rotation in radians.","Umlenkungsarbeit: Vektor-Euro-Menge mal Drehung in Radiant.","Угловая работа: сумма вектор-евро умноженная на поворот в радианах.","Trabajo angular: cantidad vector-euro multiplicada por giro en radianes.","Lavoro angolare: quantità vettore-euro per rotazione in radianti.","角度功：向量欧元数量乘以弧度旋转。","角度仕事：ベクトル・ユーロ量×ラジアン回転。","각도 일: 벡터-유로 양 × 라디안 회전.","कोणीय कार्य: वेक्टर-यूरो मात्रा × रेडियन घूर्णन।","עבודה זוויתית: כמות וקטור-אירו כפול סיבוב ברדיאנים.","کار زاویه‌ای: مقدار بردار-یورو ضربدر چرخش بر حسب رادیان.","عمل زاوي: مقدار متجه-اليورو مضروباً في الدوران بالراديان.")),
    ("Well-being index", _names("Well-being index of the population.","Wohlbefindenindex der Bevölkerung.","Индекс благополучия населения.","Índice de bienestar de la población.","Indice di benessere della popolazione.","人口福祉指数。","住民の幸福指数。","인구 복지 지수.","जनता का कल्याण सूचकांक।","מדד רווחת האוכלוסייה.","شاخص رفاه جمعیت.","مؤشر رفاه السكان.")),
    ("Power index", _names("Power index of government/currency attachment.","Machtindex der Bindung von Regierung und Währung.","Индекс власти связи правительства и валюты.","Índice de poder del vínculo gobierno/moneda.","Indice di potere del legame governo/valuta.","政府/货币绑定的权力指数。","政府/通貨結合の権力指数。","정부/통화 결속의 권력 지수.","सरकार/मुद्रा बंधन का शक्ति सूचकांक।","מדד עוצמה של קשר ממשלה/מטבע.","شاخص قدرت پیوند دولت/ارز.","مؤشر قوة ارتباط الحكومة/العملة.")),
    ("Economic strength", _names("Economic strength under angular competition.","Wirtschaftsstärke unter Winkelkonkurrenz.","Экономическая сила при угловой конкуренции.","Fuerza económica bajo competencia angular.","Forza economica sotto competizione angolare.","角度竞争下的经济强度。","角度競争下の経済強度。","각도 경쟁 아래 경제 강도.","कोणीय प्रतिस्पर्धा में आर्थिक बल।","חוסן כלכלי תחת תחרות זוויתית.","توان اقتصادی زیر رقابت زاویه‌ای.","القوة الاقتصادية تحت المنافسة الزاوية.")),
    ("Tension degree", _names("Tension degree; lower means calmer.","Spannungsgrad; niedriger ist ruhiger.","Степень напряжения; ниже значит спокойнее.","Grado de tensión; menor significa más calma.","Grado di tensione; più basso è più calmo.","紧张度；越低越平稳。","緊張度。低いほど穏やか。","긴장도; 낮을수록 차분함.","तनाव स्तर; कम मतलब अधिक शांत।","דרגת מתח; נמוך יותר רגוע יותר.","درجه تنش؛ کمتر یعنی آرام‌تر.","درجة التوتر؛ الأقل أكثر هدوءاً.")),
    ("Domestic share", _names("Domestic share of the home vector currency.","Inlandsanteil der eigenen Vektorwährung.","Внутренняя доля домашней вектор-валюты.","Cuota interna de la moneda vectorial propia.","Quota interna della propria valuta vettoriale.","本国向量货币的国内份额。","自国ベクトル通貨の国内比率。","자국 벡터 통화의 국내 점유율.","स्वदेशी वेक्टर-मुद्रा का घरेलू हिस्सा।","החלק המקומי של מטבע-הווקטור הביתי.","سهم داخلی ارز برداری خانگی.","الحصة المحلية للعملة المتجهية المنزلية.")),
    ("Dominant currency", _names("Dominant currency in local transaction flow.","Dominante Währung im lokalen Transaktionsfluss.","Доминирующая валюта в местном потоке транзакций.","Moneda dominante en el flujo local de transacciones.","Valuta dominante nel flusso locale delle transazioni.","本地交易流中的主导货币。","地域取引流で支配的な通貨。","지역 거래 흐름의 지배 통화.","स्थानीय लेन-देन प्रवाह की प्रमुख मुद्रा।","המטבע הדומיננטי בזרם העסקאות המקומי.","ارز غالب در جریان تراکنش محلی.","العملة المهيمنة في تدفق المعاملات المحلي.")),
    ("Direction toward", _names("Direction toward which a currency slowly rotates.","Richtung, zu der sich eine Währung langsam dreht.","Направление, к которому валюта медленно поворачивается.","Dirección hacia la que la moneda gira lentamente.","Direzione verso cui la valuta ruota lentamente.","货币缓慢旋转的目标方向。","通貨がゆっくり回転する方向。","통화가 천천히 도는 방향.","वह दिशा जिसकी ओर मुद्रा धीरे घूमती है।","הכיוון שאליו המטבע מסתובב לאט.","جهتی که ارز به‌آرامی به سوی آن می‌چرخد.","الاتجاه الذي تدور نحوه العملة ببطء.")),
    ("Distance between current", _names("Distance between current and initial currency angle.","Abstand zwischen aktuellem und anfänglichem Währungswinkel.","Дистанция между текущим и начальным углом валюты.","Distancia entre el ángulo monetario actual e inicial.","Distanza tra angolo valutario attuale e iniziale.","当前货币角与初始角之间的距离。","現在角と初期通貨角の距離。","현재 통화 각도와 초기 각도의 거리.","वर्तमान और प्रारंभिक मुद्रा कोण की दूरी।","המרחק בין זווית המטבע הנוכחית וההתחלתית.","فاصله میان زاویه کنونی و آغازین ارز.","المسافة بين زاوية العملة الحالية والابتدائية.")),
    ("Government good/evil", _names("Government good/evil angle: direction of the good pole.","Gut/Böse-Winkel der Regierung: Richtung des Gut-Pols.","Угол добро/зло правительства: направление полюса добра.","Ángulo bueno/malo del gobierno: dirección del polo bueno.","Angolo bene/male del governo: direzione del polo bene.","政府好/恶角：好极点的方向。","政府の善悪角：善極の方向。","정부 선/악 각도: 선 극의 방향.","सरकार का अच्छा/बुरा कोण: अच्छे ध्रुव की दिशा।","זווית טוב/רע של הממשלה: כיוון קוטב הטוב.","زاویه خوب/بد دولت: جهت قطب خوب.","زاوية الخير/الشر للحكومة: اتجاه قطب الخير.")),
    ("Population popular", _names("Population popular/unpopular angle: direction of the popular pole.","Beliebt/Unbeliebt-Winkel der Bevölkerung: Richtung des Beliebt-Pols.","Угол популярно/непопулярно населения: направление популярного полюса.","Ángulo popular/impopular de la población: dirección del polo popular.","Angolo popolare/impopolare della popolazione: direzione del polo popolare.","人口受欢迎/不受欢迎角：受欢迎极点的方向。","住民の人気/不人気角：人気極の方向。","인구 인기/비인기 각도: 인기 극의 방향.","जनता का लोकप्रिय/अलोकप्रिय कोण: लोकप्रिय ध्रुव की दिशा।","זווית פופולרי/לא פופולרי של האוכלוסייה: כיוון קוטב הפופולריות.","زاویه محبوب/نامحبوب مردم: جهت قطب محبوب.","زاوية محبوب/غير محبوب للسكان: اتجاه قطب المحبوب.")),
    ("Deviation from ideal", _names("Deviation from ideal 90° orthogonality of the axes.","Abweichung von idealer 90°-Orthogonalität der Achsen.","Отклонение от идеальной 90° ортогональности осей.","Desviación de la ortogonalidad ideal de 90° entre ejes.","Deviazione dall'ortogonalità ideale di 90° degli assi.","偏离轴之间理想 90° 正交的程度。","軸の理想的な90°直交からのずれ。","축의 이상적 90° 직교에서 벗어난 정도.","अक्षों की आदर्श 90° लंबवतता से विचलन।","סטייה מאורתוגונליות אידאלית של 90° בין הצירים.","انحراف از تعامد ایده‌آل ۹۰ درجه محور‌ها.","الانحراف عن التعامد المثالي 90° بين المحاور.")),
    ("Tiny history", _names("Tiny history line from low ▁ to high █.","Kleine Verlaufslinie von niedrig ▁ bis hoch █.","Мини-линия истории от низкого ▁ к высокому █.","Pequeña línea histórica de bajo ▁ a alto █.","Piccola linea storica da basso ▁ ad alto █.","从低 ▁ 到高 █ 的小历史线。","低 ▁ から高 █ への小さな履歴線。","낮음 ▁ 에서 높음 █ 까지의 작은 이력선.","निम्न ▁ से उच्च █ तक छोटी इतिहास रेखा।","קו היסטוריה קטן מנמוך ▁ לגבוה █.","خط کوچک تاریخ از کم ▁ تا زیاد █.","خط تاريخ صغير من منخفض ▁ إلى مرتفع █.")),
    ("Home vector currency", _names("Home vector-currency share in the final tick.","Anteil der eigenen Vektorwährung im letzten Tick.","Доля домашней вектор-валюты в финальном тике.","Cuota de la moneda-vector propia en el tick final.","Quota della valuta vettoriale propria nel tick finale.","最后周期中本国向量货币的份额。","最終ティックの自国ベクトル通貨比率。","마지막 틱의 자국 벡터 통화 점유율.","अंतिम टिक में घरेलू वेक्टर-मुद्रा का हिस्सा।","חלק מטבע-הווקטור הביתי בטיק האחרון.","سهم ارز برداری خانگی در تیک نهایی.","حصة العملة المتجهية المنزلية في الدورة النهائية.")),
    ("Average across", _names("Average across the three countries or a scenario run.","Durchschnitt über drei Länder oder einen Szenariolauf.","Среднее по трём странам или сценарию.","Promedio de los tres países o de una ejecución de escenario.","Media dei tre paesi o di una corsa di scenario.","三个国家或一次情景运行的平均值。","三国またはシナリオ実行の平均。","세 국가 또는 시나리오 실행 평균.","तीन देशों या परिदृश्य रन का औसत।","ממוצע על פני שלוש המדינות או ריצת תרחיש.","میانگین سه کشور یا اجرای سناریو.","متوسط عبر الدول الثلاث أو تشغيل سيناريو.")),
]

LONG_KEYWORDS = [
    ("The model simulates three governments", "intro"), ("The explanations are not collected", "read"),
    ("Important: good versus evil", "important"), ("This part simulates the three currencies", "currency"),
    ("This part simulates labor", "labor"), ("This part simulates need", "goods"),
    ("This part simulates the trade triangle", "trade"), ("This part simulates the goal system", "goals"),
    ("This part simulates angle drift", "drift"), ("This final part reads", "final"),
    ("A tick can be read", "tick"), ("The final report does not ask", "final_report"),
    ("The gallery comes after", "gallery"), ("Result:", "result"), ("Scenario meaning:", "scenario_meaning"),
]

LONG_BASE = {
    "intro": _names(
        "The model simulates three governments, three markets and three competing Euro vectors. EA, EB and EC all have equal length |€⃗|=1 VE; competition comes from angle, direction, resonance, power attachment and well-being, not from numerical exchange rates.",
        "Das Modell simuliert drei Regierungen, drei Märkte und drei konkurrierende Euro-Vektoren. EA, EB und EC haben gleiche Länge |€⃗|=1 VE; Konkurrenz entsteht durch Winkel, Richtung, Resonanz, Machtbindung und Wohlbefinden, nicht durch Zahlen-Wechselkurse.",
        "Модель имитирует три правительства, три рынка и три конкурирующих евро-вектора. EA, EB и EC имеют равную длину |€⃗|=1 VE; конкуренция идёт через угол, направление, резонанс, власть и благополучие, а не через численный курс.",
        "El modelo simula tres gobiernos, tres mercados y tres euro-vectores en competencia. EA, EB y EC tienen longitud igual |€⃗|=1 VE; la competencia nace del ángulo, dirección, resonancia, poder y bienestar, no del tipo de cambio numérico.",
        "Il modello simula tre governi, tre mercati e tre euro-vettori concorrenti. EA, EB ed EC hanno lunghezza uguale |€⃗|=1 VE; la competizione nasce da angolo, direzione, risonanza, potere e benessere, non dal cambio numerico.",
        "模型模拟三个政府、三个市场和三个竞争的欧元向量。EA、EB、EC 的长度相同：|€⃗|=1 VE；竞争来自角度、方向、共振、权力绑定和福祉，而不是数字汇率。",
        "このモデルは三つの政府、三つの市場、三つの競合するユーロ・ベクトルを模擬します。EA/EB/EC の長さは同じ |€⃗|=1 VE で、競争は数値的為替ではなく角度・方向・共鳴・権力結合・幸福から生じます。",
        "이 모델은 세 정부, 세 시장, 세 경쟁 유로 벡터를 시뮬레이션합니다. EA/EB/EC의 길이는 모두 |€⃗|=1 VE이며, 경쟁은 숫자 환율이 아니라 각도, 방향, 공명, 권력 결속, 복지에서 나옵니다.",
        "यह मॉडल तीन सरकारों, तीन बाज़ारों और तीन प्रतिस्पर्धी यूरो-वेक्टरों को सिमुलेट करता है। EA, EB और EC की लंबाई समान |€⃗|=1 VE है; प्रतिस्पर्धा अंक वाले विनिमय दर से नहीं, कोण, दिशा, अनुनाद, शक्ति-बाँध और कल्याण से आती है।",
        "המודל מדמה שלוש ממשלות, שלושה שווקים ושלושה וקטורי אירו מתחרים. EA, EB ו-EC באותו אורך |€⃗|=1 VE; התחרות באה מזווית, כיוון, תהודה, קשר עוצמה ורווחה, לא משער חליפין מספרי.",
        "مدل سه دولت، سه بازار و سه بردار یوروی رقابتی را شبیه‌سازی می‌کند. EA، EB و EC همگی طول برابر |€⃗|=1 VE دارند؛ رقابت از زاویه، جهت، تشدید، پیوند قدرت و رفاه می‌آید، نه از نرخ تبدیل عددی.",
        "يحاكي النموذج ثلاث حكومات وثلاثة أسواق وثلاثة متجهات يورو متنافسة. EA وEB وEC لها الطول نفسه |€⃗|=1 VE؛ التنافس يأتي من الزاوية والاتجاه والرنين وارتباط القوة والرفاه، لا من سعر صرف رقمي."),
    "important": _names(
        "Good versus evil remains good versus evil in the angular sense. It is not subsidy, punishment, positive or negative. Government sets the good/evil direction; population sets the orthogonal popular/unpopular direction; the market action lies between these poles.",
        "Gut gegen Böse bleibt Gut gegen Böse im Winkelsinn. Es ist keine Förderung, Strafe oder positiv/negativ. Die Regierung setzt Gut/Böse; die Bevölkerung setzt orthogonal Beliebt/Unbeliebt; die Markthandlung liegt zwischen den Polen.",
        "Добро против зла остаётся угловой осью добро/зло. Это не субсидия, не наказание и не плюс/минус. Правительство задаёт добро/зло, население ортогонально задаёт популярно/непопулярно, действие рынка лежит между полюсами.",
        "Bueno contra malo sigue siendo un eje angular de bueno/malo. No es subsidio, castigo ni positivo/negativo. El gobierno fija bueno/malo; la población fija popular/impopular ortogonal; la acción de mercado queda entre los polos.",
        "Bene contro male resta un asse angolare bene/male. Non è sussidio, punizione o positivo/negativo. Il governo fissa bene/male; la popolazione fissa popolare/impopolare ortogonale; l'azione sta fra i poli.",
        "好/恶仍然是角度意义上的好/恶，不是补贴、惩罚或正负。政府设定好/恶方向；人口设定正交的受欢迎/不受欢迎方向；市场行动位于这些极点之间。",
        "善/悪は角度上の善/悪のままです。補助・罰・正負ではありません。政府が善悪方向を、住民が直交する人気/不人気方向を置き、市場行動はその間にあります。",
        "선/악은 각도 의미의 선/악 그대로입니다. 보조금, 처벌, 양/음이 아닙니다. 정부는 선/악 방향을, 인구는 직교하는 인기/비인기 방향을 정하고 시장 행동은 그 사이에 놓입니다.",
        "अच्छा/बुरा इस मॉडल में कोणीय अर्थ का अच्छा/बुरा ही है। यह सब्सिडी, दंड या सकारात्मक/नकारात्मक नहीं है। सरकार अच्छा/बुरा दिशा देती है, जनता लोकप्रिय/अलोकप्रिय दिशा देती है, और बाज़ार क्रिया बीच में होती है।",
        "טוב/רע נשאר ציר זוויתי של טוב/רע. זה לא סבסוד, עונש או חיובי/שלילי. הממשלה קובעת כיוון טוב/רע; האוכלוסייה קובעת כיוון פופולרי/לא פופולרי ניצב; פעולת השוק ביניהם.",
        "خوب/بد در این مدل همان محور زاویه‌ای خوب/بد است؛ نه یارانه، نه مجازات و نه مثبت/منفی. دولت جهت خوب/بد را می‌گذارد، مردم جهت محبوب/نامحبوب عمود را می‌گذارند و کنش بازار میان آنهاست.",
        "الخير/الشر يبقى محوراً زاوياً للخير/الشر. ليس دعماً ولا عقوبة ولا موجب/سالب. الحكومة تحدد اتجاه الخير/الشر، والسكان يحددون اتجاه محبوب/غير محبوب المتعامد، وحركة السوق تقع بينهما."),
}

GENERIC_LONG = {
    "read": _names(
        "Each simulation part explains only its own abbreviations and units: currency angles, labor hours, goods supply, trade work and indices.",
        "Jeder Simulationsteil erklärt nur seine eigenen Kürzel und Einheiten: Währungswinkel, Arbeitsstunden, Güterversorgung, Handelsarbeit und Indizes.",
        "Каждая часть симуляции объясняет только свои сокращения и единицы: валютные углы, рабочие часы, предложение благ, торговую работу и индексы.",
        "Cada parte de la simulación explica solo sus propias abreviaturas y unidades: ángulos monetarios, horas de trabajo, oferta de bienes, trabajo comercial e índices.",
        "Ogni parte della simulazione spiega solo le proprie abbreviazioni e unità: angoli valutari, ore di lavoro, offerta di beni, lavoro commerciale e indici.",
        "每个模拟部分只解释本部分使用的缩写和单位：货币角、劳动小时、商品供给、贸易功和指数。",
        "各シミュレーション部分は、その部分で使う略号と単位だけを説明します。通貨角、労働時間、財供給、貿易仕事、指数です。",
        "각 시뮬레이션 부분은 해당 부분의 약어와 단위만 설명합니다. 통화 각도, 노동시간, 재화 공급, 무역 일, 지수입니다.",
        "हर सिमुलेशन भाग केवल अपने संक्षेप और इकाइयाँ समझाता है: मुद्रा कोण, श्रम घंटे, वस्तु-आपूर्ति, व्यापार-कार्य और सूचकांक।",
        "כל חלק בסימולציה מסביר רק את הקיצורים והיחידות שלו: זוויות מטבע, שעות עבודה, היצע סחורות, עבודת מסחר ומדדים.",
        "هر بخش شبیه‌سازی فقط اختصارها و واحدهای همان بخش را توضیح می‌دهد: زاویه ارز، ساعت کار، عرضه کالا، کار تجاری و شاخص‌ها.",
        "كل جزء من المحاكاة يشرح اختصاراته ووحداته فقط: زوايا العملة، ساعات العمل، عرض السلع، عمل التجارة والمؤشرات."),
    "currency": _names(
        "This part simulates the three equal Euro-vector currencies as directions on one ring and asks which direction attracts action flow.",
        "Dieser Teil simuliert drei gleich lange Euro-Vektorwährungen als Richtungen auf einem Ring und fragt, welche Richtung Handlungsfluss anzieht.",
        "Эта часть моделирует три равные евро-векторные валюты как направления на одном кольце и спрашивает, какое направление притягивает поток действий.",
        "Esta parte simula tres monedas euro-vectoriales iguales como direcciones en un anillo y pregunta qué dirección atrae el flujo de acción.",
        "Questa parte simula tre valute euro-vettore uguali come direzioni su un anello e chiede quale direzione attira il flusso d'azione.",
        "本部分把三个等长欧元向量货币模拟为同一圆环上的方向，并询问哪一个方向吸引行动流。",
        "この部分では、同じ長さの三つのユーロ・ベクトル通貨を一つのリング上の方向として模擬し、どの方向が行動流を引くかを見ます。",
        "이 부분은 같은 길이의 세 유로 벡터 통화를 하나의 고리 위 방향으로 시뮬레이션하고 어느 방향이 행동 흐름을 끌어들이는지 봅니다.",
        "यह भाग तीन समान यूरो-वेक्टर मुद्राओं को एक वृत्त पर दिशाओं के रूप में सिमुलेट करता है और पूछता है कि कौन-सी दिशा क्रिया-प्रवाह खींचती है।",
        "חלק זה מדמה שלושה מטבעות וקטור-אירו שווים ככיוונים על טבעת אחת ושואל איזה כיוון מושך את זרימת הפעולה.",
        "این بخش سه ارز بردار-یوروی برابر را به صورت جهت‌هایی روی یک حلقه شبیه‌سازی می‌کند و می‌پرسد کدام جهت جریان کنش را جذب می‌کند.",
        "يحاكي هذا الجزء ثلاث عملات يورو-متجهية متساوية كاتجاهات على حلقة واحدة ويسأل أي اتجاه يجذب تدفق الفعل."),
    "labor": _names(
        "This part simulates labor as an angular action and shows where work creates production or fatigue.",
        "Dieser Teil simuliert Arbeit als Winkelhandlung und zeigt, wo Arbeit Produktion oder Ermüdung erzeugt.",
        "Эта часть моделирует труд как угловое действие и показывает, где труд создаёт производство или усталость.",
        "Esta parte simula el trabajo como acción angular y muestra dónde el trabajo crea producción o fatiga.",
        "Questa parte simula il lavoro come azione angolare e mostra dove il lavoro crea produzione o fatica.",
        "本部分把劳动模拟为角度行动，并显示劳动在哪里产生生产或疲劳。",
        "この部分は労働を角度的行動として模擬し、仕事が生産を生む場所と疲労を生む場所を示します。",
        "이 부분은 노동을 각도 행동으로 시뮬레이션하고 일이 생산 또는 피로를 만드는 곳을 보여 줍니다.",
        "यह भाग श्रम को कोणीय क्रिया के रूप में सिमुलेट करता है और दिखाता है कि काम कहाँ उत्पादन या थकान बनाता है।",
        "חלק זה מדמה עבודה כפעולה זוויתית ומראה היכן עבודה יוצרת ייצור או עייפות.",
        "این بخش کار را به صورت کنش زاویه‌ای شبیه‌سازی می‌کند و نشان می‌دهد کار کجا تولید یا خستگی می‌سازد.",
        "يحاكي هذا الجزء العمل كفعل زاوي ويعرض أين يخلق العمل إنتاجاً أو تعباً."),
    "goods": _names(
        "This part simulates need, supply, satisfaction and vector-Euro price; price counts equal VE units and never lengthens a currency vector.",
        "Dieser Teil simuliert Bedarf, Versorgung, Zufriedenheit und Vektor-Euro-Preis; der Preis zählt gleiche VE-Einheiten und verlängert niemals einen Währungsvektor.",
        "Эта часть моделирует потребность, предложение, удовлетворение и цену вектор-евро; цена считает равные единицы VE и никогда не удлиняет валютный вектор.",
        "Esta parte simula necesidad, oferta, satisfacción y precio vector-euro; el precio cuenta unidades VE iguales y nunca alarga un vector monetario.",
        "Questa parte simula bisogno, offerta, soddisfazione e prezzo vettore-euro; il prezzo conta unità VE uguali e non allunga mai un vettore valutario.",
        "本部分模拟需求、供给、满足度和向量欧元价格；价格只计算相等的 VE 单位，绝不拉长货币向量。",
        "この部分では、必要量、供給、満足度、ベクトル・ユーロ価格を模擬します。価格は同じ VE 単位を数えるだけで、通貨ベクトルを長くしません。",
        "이 부분은 필요, 공급, 만족도, 벡터-유로 가격을 시뮬레이션합니다. 가격은 같은 VE 단위를 셀 뿐 통화 벡터 길이를 늘리지 않습니다.",
        "यह भाग आवश्यकता, आपूर्ति, संतुष्टि और वेक्टर-यूरो मूल्य को सिमुलेट करता है; मूल्य समान VE इकाइयाँ गिनता है और मुद्रा-वेक्टर को लंबा नहीं करता।",
        "חלק זה מדמה צורך, היצע, סיפוק ומחיר וקטור-אירו; המחיר סופר יחידות VE שוות ולעולם אינו מאריך וקטור מטבע.",
        "این بخش نیاز، عرضه، رضایت و قیمت بردار-یورو را شبیه‌سازی می‌کند؛ قیمت واحدهای برابر VE را می‌شمارد و هرگز بردار ارز را بلندتر نمی‌کند.",
        "يحاكي هذا الجزء الحاجة والعرض والإشباع وسعر متجه-اليورو؛ السعر يعد وحدات VE متساوية ولا يطيل متجه العملة أبداً."),
    "trade": _names(
        "This part simulates triangular trade and angular work between exporter, importer and trade currency.",
        "Dieser Teil simuliert Dreieckshandel und Winkelarbeit zwischen Exporteur, Importeur und Handelswährung.",
        "Эта часть моделирует треугольную торговлю и угловую работу между экспортёром, импортёром и торговой валютой.",
        "Esta parte simula comercio triangular y trabajo angular entre exportador, importador y moneda comercial.",
        "Questa parte simula commercio triangolare e lavoro angolare tra esportatore, importatore e valuta di scambio.",
        "本部分模拟出口方、进口方和贸易货币之间的三角贸易与角度功。",
        "この部分は、輸出者、輸入者、貿易通貨の間の三角貿易と角度仕事を模擬します。",
        "이 부분은 수출자, 수입자, 무역 통화 사이의 삼각 무역과 각도 일을 시뮬레이션합니다.",
        "यह भाग निर्यातक, आयातक और व्यापार-मुद्रा के बीच त्रिकोणीय व्यापार और कोणीय कार्य सिमुलेट करता है।",
        "חלק זה מדמה מסחר משולש ועבודה זוויתית בין יצואן, יבואן ומטבע המסחר.",
        "این بخش تجارت مثلثی و کار زاویه‌ای میان صادرکننده، واردکننده و ارز تجاری را شبیه‌سازی می‌کند.",
        "يحاكي هذا الجزء تجارة مثلثية وعملاً زاوياً بين المصدّر والمستورد وعملة التجارة."),
    "goals": _names(
        "This part simulates well-being, power, economic strength and tension instead of wealth maximization.",
        "Dieser Teil simuliert Wohlbefinden, Macht, Wirtschaftsstärke und Spannung statt Reichtumsmaximierung.",
        "Эта часть моделирует благополучие, власть, экономическую силу и напряжение вместо максимизации богатства.",
        "Esta parte simula bienestar, poder, fuerza económica y tensión en lugar de maximizar riqueza.",
        "Questa parte simula benessere, potere, forza economica e tensione invece della massimizzazione della ricchezza.",
        "本部分模拟福祉、权力、经济强度和张力，而不是财富最大化。",
        "この部分は、富の最大化ではなく、幸福、権力、経済強度、緊張を模擬します。",
        "이 부분은 부의 극대화 대신 복지, 권력, 경제 강도, 긴장을 시뮬레이션합니다.",
        "यह भाग धन-अधिकतमकरण के बजाय कल्याण, शक्ति, आर्थिक बल और तनाव को सिमुलेट करता है।",
        "חלק זה מדמה רווחה, עוצמה, חוסן כלכלי ומתח במקום מקסום עושר.",
        "این بخش به جای بیشینه‌سازی ثروت، رفاه، قدرت، توان اقتصادی و تنش را شبیه‌سازی می‌کند.",
        "يحاكي هذا الجزء الرفاه والقوة والقوة الاقتصادية والتوتر بدلاً من تعظيم الثروة."),
    "drift": _names(
        "This part simulates slow angular drift of governments, populations and currencies toward successful, powerful or livable actions.",
        "Dieser Teil simuliert langsame Winkeldrift von Regierungen, Bevölkerungen und Währungen hin zu erfolgreichen, mächtigen oder lebbaren Handlungen.",
        "Эта часть моделирует медленный угловой дрейф правительств, населения и валют к успешным, сильным или пригодным для жизни действиям.",
        "Esta parte simula la deriva angular lenta de gobiernos, poblaciones y monedas hacia acciones exitosas, poderosas o habitables.",
        "Questa parte simula la lenta deriva angolare di governi, popolazioni e valute verso azioni riuscite, potenti o vivibili.",
        "本部分模拟政府、人口和货币缓慢漂移到更成功、更有权力或更宜居的行动方向。",
        "この部分は、政府、住民、通貨が成功し、強く、暮らしやすい行動へゆっくり角度ドリフトする様子を模擬します。",
        "이 부분은 정부, 인구, 통화가 성공적이고 강력하거나 살 만한 행동 쪽으로 천천히 각도 표류하는 과정을 시뮬레이션합니다.",
        "यह भाग सरकारों, जनसंख्या और मुद्राओं का सफल, शक्तिशाली या रहने योग्य क्रियाओं की ओर धीमा कोणीय बहाव सिमुलेट करता है।",
        "חלק זה מדמה סחיפה זוויתית איטית של ממשלות, אוכלוסיות ומטבעות לעבר פעולות מצליחות, חזקות או ראויות לחיים.",
        "این بخش رانش زاویه‌ای آهسته دولت‌ها، جمعیت‌ها و ارزها را به سوی کنش‌های موفق، نیرومند یا زیست‌پذیر شبیه‌سازی می‌کند.",
        "يحاكي هذا الجزء انجرافاً زاوياً بطيئاً للحكومات والسكان والعملات نحو أفعال ناجحة أو قوية أو قابلة للعيش."),
    "final": _names(
        "This final part reads the whole run by comparing indices, mini-charts and angular weakness.",
        "Dieser letzte Teil liest den ganzen Lauf über Indizes, Minidiagramme und Winkelschwäche.",
        "Эта финальная часть читает весь прогон через индексы, мини-графики и угловую слабость.",
        "Esta parte final lee toda la corrida comparando índices, minigráficos y debilidad angular.",
        "Questa parte finale legge l'intera esecuzione confrontando indici, mini-grafici e debolezza angolare.",
        "最后部分通过指数、迷你图和角度弱点来解读整个运行。",
        "最後の部分では、指数、ミニチャート、角度的弱さを比べて全体の実行を読みます。",
        "마지막 부분은 지수, 미니 차트, 각도 약점을 비교해 전체 실행을 읽습니다.",
        "अंतिम भाग सूचकांकों, छोटे चार्टों और कोणीय कमजोरी की तुलना से पूरे रन को पढ़ता है।",
        "החלק הסופי קורא את כל הריצה דרך מדדים, תרשימים קטנים וחולשה זוויתית.",
        "بخش نهایی کل اجرا را با مقایسه شاخص‌ها، نمودارهای کوچک و ضعف زاویه‌ای می‌خواند.",
        "يقرأ الجزء النهائي التشغيل كله عبر مقارنة المؤشرات والرسوم الصغيرة والضعف الزاوي."),
    "tick": _names(
        "A tick can be read as a month, quarter or political-market cycle: currency, labor, goods, trade, indices and drift.",
        "Ein Tick kann als Monat, Quartal oder politischer Marktzyklus gelesen werden: Währung, Arbeit, Güter, Handel, Indizes und Drift.",
        "Тик можно читать как месяц, квартал или политико-рыночный цикл: валюта, труд, блага, торговля, индексы и дрейф.",
        "Un tick puede leerse como mes, trimestre o ciclo político-mercado: moneda, trabajo, bienes, comercio, índices y deriva.",
        "Un tick può essere letto come mese, trimestre o ciclo politico-mercato: valuta, lavoro, beni, commercio, indici e deriva.",
        "一个 tick 可理解为一个月、季度或政治市场周期：货币、劳动、商品、贸易、指数和漂移。",
        "1 tick は月、四半期、または政治市場サイクルとして読めます。通貨、労働、財、貿易、指数、ドリフトです。",
        "tick 하나는 월, 분기 또는 정치-시장 주기로 읽을 수 있습니다. 통화, 노동, 재화, 무역, 지수, 표류입니다.",
        "एक tick को महीना, तिमाही या राजनीतिक-बाज़ार चक्र पढ़ा जा सकता है: मुद्रा, श्रम, वस्तु, व्यापार, सूचकांक और बहाव।",
        "טיק יכול להיקרא כחודש, רבעון או מחזור פוליטי-שוק: מטבע, עבודה, טובין, מסחר, מדדים וסחיפה.",
        "یک tick را می‌توان ماه، فصل یا چرخه سیاسی-بازاری خواند: ارز، کار، کالا، تجارت، شاخص‌ها و رانش.",
        "يمكن قراءة tick كشهر أو ربع سنة أو دورة سياسية-سوقية: العملة والعمل والسلع والتجارة والمؤشرات والانجراف."),
    "final_report": _names(
        "The final report asks which vector currency gained power, where well-being stayed livable and where angular tension weakened the economy.",
        "Der Abschlussbericht fragt, welche Vektorwährung Macht gewann, wo Wohlbefinden lebbar blieb und wo Winkelspannung die Wirtschaft schwächte.",
        "Финальный отчёт спрашивает, какая векторная валюта набрала власть, где благополучие осталось пригодным для жизни и где угловое напряжение ослабило экономику.",
        "El informe final pregunta qué moneda vectorial ganó poder, dónde el bienestar siguió vivible y dónde la tensión angular debilitó la economía.",
        "Il rapporto finale chiede quale valuta vettoriale ha guadagnato potere, dove il benessere è rimasto vivibile e dove la tensione angolare ha indebolito l'economia.",
        "最终报告询问哪个向量货币获得权力，哪里福祉仍可维持，哪里角度张力削弱经济。",
        "最終報告は、どのベクトル通貨が権力を得たか、幸福が保たれた場所、角度緊張が経済を弱めた場所を問います。",
        "최종 보고서는 어떤 벡터 통화가 권력을 얻었는지, 어디서 복지가 살 만하게 남았는지, 어디서 각도 긴장이 경제를 약화했는지 묻습니다.",
        "अंतिम रिपोर्ट पूछती है कि कौन-सी वेक्टर-मुद्रा ने शक्ति पाई, कहाँ कल्याण रहने योग्य रहा और कहाँ कोणीय तनाव ने अर्थव्यवस्था कमजोर की।",
        "הדוח הסופי שואל איזה מטבע וקטורי צבר עוצמה, היכן הרווחה נשארה אפשרית והיכן מתח זוויתי החליש את הכלכלה.",
        "گزارش نهایی می‌پرسد کدام ارز برداری قدرت گرفت، کجا رفاه زیست‌پذیر ماند و کجا تنش زاویه‌ای اقتصاد را تضعیف کرد.",
        "يسأل التقرير النهائي أي عملة متجهية اكتسبت قوة، وأين بقي الرفاه قابلاً للعيش، وأين أضعف التوتر الزاوي الاقتصاد."),
    "gallery": _names(
        "The UTF-8 gallery turns the final state into colorful circles, vectors, heat carpets, trade arrows and scenario maps.",
        "Die UTF-8-Galerie verwandelt den Endzustand in bunte Kreise, Vektoren, Wärmeteppiche, Handelspfeile und Szenariokarten.",
        "Галерея UTF-8 превращает финальное состояние в цветные круги, векторы, тепловые ковры, торговые стрелки и карты сценариев.",
        "La galería UTF-8 convierte el estado final en círculos, vectores, alfombras de calor, flechas comerciales y mapas de escenarios.",
        "La galleria UTF-8 trasforma lo stato finale in cerchi colorati, vettori, tappeti di calore, frecce commerciali e mappe di scenario.",
        "UTF-8 图库把最终状态变成彩色圆、向量、热度地毯、贸易箭头和情景地图。",
        "UTF-8 ギャラリーは最終状態をカラフルな円、ベクトル、ヒート絨毯、貿易矢印、シナリオ地図に変換します。",
        "UTF-8 갤러리는 최종 상태를 다채로운 원, 벡터, 열 카펫, 무역 화살표, 시나리오 지도로 바꿉니다.",
        "UTF-8 गैलरी अंतिम अवस्था को रंगीन वृत्त, वेक्टर, ऊष्मा-पट्टी, व्यापार तीर और परिदृश्य-नक्शों में बदलती है।",
        "גלריית UTF-8 הופכת את מצב הסיום לעיגולים צבעוניים, וקטורים, שטיחי חום, חצי מסחר ומפות תרחישים.",
        "گالری UTF-8 حالت نهایی را به دایره‌های رنگی، بردارها، فرش‌های گرما، پیکان‌های تجارت و نقشه‌های سناریو تبدیل می‌کند.",
        "يحوّل معرض UTF-8 الحالة النهائية إلى دوائر ملونة ومتجهات وسجاد حرارة وأسهم تجارة وخرائط سيناريو."),
}

def _long_generic(lang: str, key: str, en: str) -> str:
    lang = normalize_lang(lang)
    if key in LONG_BASE:
        return LONG_BASE[key][lang]
    if key in ("result", "scenario_meaning") or en.startswith("Result:") or en.startswith("Scenario meaning:"):
        return translate_result_summary(lang, key, en)
    prefix = PH.get(lang, {}).get("explain", "Explanation")
    if key in GENERIC_LONG:
        return f"{prefix}: {GENERIC_LONG[key][lang]}"
    return f"{prefix}: {en}"

def L(lang: str, en: str, de: str) -> str:
    lang = normalize_lang(lang)
    if lang == "de":
        return de
    if lang == "en":
        return en
    if en.startswith("TICK ") and ": one simulated period" in en:
        num = en.split(":", 1)[0].replace("TICK", "").strip()
        return {
            "ru": f"ТИК {num}: один моделируемый период",
            "es": f"TICK {num}: un período simulado",
            "it": f"TICK {num}: un periodo simulato",
            "zh": f"周期 {num}：一个模拟时期",
            "ja": f"ティック {num}：一つのシミュレーション期間",
            "ko": f"틱 {num}: 하나의 시뮬레이션 기간",
            "hi": f"टिक {num}: एक सिमुलेटेड अवधि",
            "he": f"טיק {num}: תקופה מדומה אחת",
            "fa": f"تیک {num}: یک دوره شبیه‌سازی‌شده",
            "ar": f"الدورة {num}: فترة محاكاة واحدة",
        }.get(lang, en)
    if en.startswith("Scenario reading for"):
        return _names(
            "Scenario reading: use the comparison as a diagnosis. Resonance calms angles, power pulls vectors toward state currency, and scarcity or fragmentation thickens tension.",
            "Szenario-Lesart: Nutze den Vergleich als Diagnose. Resonanz beruhigt Winkel, Macht zieht Vektoren zur Staatswährung, und Mangel oder Zersplitterung verdicken Spannung.",
            "Чтение сценариев: сравнение служит диагностикой. Резонанс успокаивает углы, власть тянет векторы к государственной валюте, а дефицит или фрагментация усиливают напряжение.",
            "Lectura de escenario: usa la comparación como diagnóstico. La resonancia calma los ángulos, el poder atrae vectores hacia la moneda estatal, y la escasez o fragmentación aumenta la tensión.",
            "Lettura di scenario: usa il confronto come diagnosi. La risonanza calma gli angoli, il potere tira i vettori verso la valuta statale, e scarsità o frammentazione addensano la tensione.",
            "情景解读：把比较当作诊断。共振使角度平静，权力把向量拉向国家货币，稀缺或碎片化会加厚张力。",
            "シナリオ読解：比較を診断として使います。共鳴は角度を落ち着かせ、権力はベクトルを国家通貨へ引き、不足や分断は緊張を厚くします。",
            "시나리오 해석: 비교를 진단으로 사용하세요. 공명은 각도를 진정시키고, 권력은 벡터를 국가 통화 쪽으로 끌며, 부족이나 분절은 긴장을 두껍게 합니다.",
            "परिदृश्य-पढ़ाई: तुलना को निदान की तरह लें। अनुनाद कोणों को शांत करता है, शक्ति वेक्टरों को राज्य-मुद्रा की ओर खींचती है, और अभाव या खंडन तनाव बढ़ाते हैं।",
            "קריאת תרחיש: השתמשו בהשוואה כאבחון. תהודה מרגיעה זוויות, עוצמה מושכת וקטורים למטבע המדינה, ומחסור או פיצול מעבים מתח.",
            "خوانش سناریو: مقایسه را تشخیص بدانید. تشدید زاویه‌ها را آرام می‌کند، قدرت بردارها را به سوی ارز دولتی می‌کشد، و کمبود یا پراکندگی تنش را ضخیم می‌کند.",
            "قراءة السيناريو: استخدم المقارنة كتشخيص. الرنين يهدئ الزوايا، والقوة تسحب المتجهات نحو عملة الدولة، والندرة أو التشظي تزيد التوتر.")[lang]
    if en in COMMON:
        return COMMON[en][lang]
    if en.startswith("TICK ") and "one simulated period" in en:
        num = en.split(":", 1)[0].replace("TICK", "").strip()
        return {
            "ru": f"ТИК {num}: один моделируемый период",
            "es": f"TICK {num}: un período simulado",
            "it": f"TICK {num}: un periodo simulato",
            "zh": f"周期 {num}：一个模拟时期",
            "ja": f"ティック {num}：一つのシミュレーション期間",
            "ko": f"틱 {num}: 하나의 시뮬레이션 기간",
            "hi": f"टिक {num}: एक सिमुलेटेड अवधि",
            "he": f"טיק {num}: תקופה מדומה אחת",
            "fa": f"تیک {num}: یک دوره شبیه‌سازی‌شده",
            "ar": f"الدورة {num}: فترة محاكاة واحدة",
        }.get(lang, en)
    for prefix, translations in AUTO_PHRASES:
        if en.startswith(prefix):
            return translations[lang]
    if en == "Run parameters:":
        return PH[lang]["run"]
    if en == "Selected EU countries:":
        return PH[lang]["selected"]
    if en == "Language:":
        return PH[lang]["language"]
    for prefix, key in LONG_KEYWORDS:
        if en.startswith(prefix):
            return _long_generic(lang, key, en)
    return en

def country_name(spec: Dict[str, object], lang: str) -> str:
    names = spec.get("names", {})
    if isinstance(names, dict):
        return str(names.get(normalize_lang(lang), names.get("en", spec.get("code", "?"))))
    return str(spec.get("code", "?"))

def currency_display_name(code: str, spec: Dict[str, object], lang: str) -> str:
    cname = country_name(spec, lang)
    lang = normalize_lang(lang)
    prefix = _names("Euro vector", "Euro-Vektor", "евро-вектор", "vector euro", "vettore euro", "欧元向量", "ユーロ・ベクトル", "유로 벡터", "यूरो-वेक्टर", "וקטור אירו", "بردار یورو", "متجه يورو")[lang]
    return f"{prefix} {cname}"

# Runtime aliases used by the simulation core. They keep older function names working
# while the new version supports all requested languages and EU countries.
def normalize_lang_code(lang: str) -> str:
    return normalize_lang(lang)

def local_dict(d: Dict[str, str], lang: str) -> str:
    lang = normalize_lang(lang)
    return str(d.get(lang, d.get("en", next(iter(d.values())) if d else "")))

def sector_label(code: str, lang: str) -> str:
    return local_dict(SECTOR_NAMES.get(code, {"en": code}), lang)

def vector_currency_names(spec: Dict[str, object]) -> Dict[str, str]:
    return {lang: currency_display_name(str(spec.get("code", "?")), spec, lang) for lang in SUPPORTED_LANGS}

EU_COUNTRY_BY_ISO3 = {str(c["code"]): c for c in EU_COUNTRIES}
LANGUAGE_NAMES = LANG_NAMES
_ISO2_TO_ISO3 = {
    "AT":"AUT", "BE":"BEL", "BG":"BGR", "HR":"HRV", "CY":"CYP", "CZ":"CZE", "DK":"DNK",
    "EE":"EST", "FI":"FIN", "FR":"FRA", "DE":"DEU", "GR":"GRC", "HU":"HUN", "IE":"IRL",
    "IT":"ITA", "LV":"LVA", "LT":"LTU", "LU":"LUX", "MT":"MLT", "NL":"NLD", "PL":"POL",
    "PT":"PRT", "RO":"ROU", "SK":"SVK", "SI":"SVN", "ES":"ESP", "SE":"SWE",
}
_COUNTRY_NAME_ALIASES: Dict[str, str] = {}
for _spec in EU_COUNTRIES:
    _code = str(_spec["code"])
    _COUNTRY_NAME_ALIASES[_code.lower()] = _code
    for _k, _v in _ISO2_TO_ISO3.items():
        if _v == _code:
            _COUNTRY_NAME_ALIASES[_k.lower()] = _code
    _names_map = _spec.get("names", {})
    if isinstance(_names_map, dict):
        for _name in _names_map.values():
            _COUNTRY_NAME_ALIASES[str(_name).strip().lower()] = _code

def resolve_eu_country_code(raw: str) -> str:
    x = str(raw).strip()
    if not x:
        return ""
    up = x.upper()
    if up in EU_COUNTRY_BY_ISO3:
        return up
    if up in _ISO2_TO_ISO3:
        return _ISO2_TO_ISO3[up]
    return _COUNTRY_NAME_ALIASES.get(x.lower(), "")

def vector_currency_names(profile: Dict[str, object]) -> Dict[str, str]:
    return {lang: currency_display_name("", profile, lang) for lang in SUPPORTED_LANGS}



def normalize_lang_code(lang: str) -> str:
    """Compatibility helper: all language aliases are normalized through normalize_lang()."""
    return normalize_lang(lang)


def local_dict(values: Dict[str, str], lang: str) -> str:
    lang = normalize_lang(lang)
    return values.get(lang, values.get("en", next(iter(values.values()), "")))


def sector_label(sector_code: str, lang: str) -> str:
    labels = SECTOR_NAMES.get(sector_code, {})
    if isinstance(labels, dict):
        return labels.get(normalize_lang(lang), labels.get("en", sector_code))
    return sector_code


EU_COUNTRY_BY_ISO3: Dict[str, Dict[str, object]] = {str(c["code"]): c for c in EU_COUNTRIES}

# Common ISO-2 shortcuts so users may write --countries DE,FR,IT instead of DEU,FRA,ITA.
COUNTRY_CODE_ALIASES = {
    "AT":"AUT", "BE":"BEL", "BG":"BGR", "HR":"HRV", "CY":"CYP", "CZ":"CZE",
    "DK":"DNK", "EE":"EST", "FI":"FIN", "FR":"FRA", "DE":"DEU", "GR":"GRC",
    "HU":"HUN", "IE":"IRL", "IT":"ITA", "LV":"LVA", "LT":"LTU", "LU":"LUX",
    "MT":"MLT", "NL":"NLD", "PL":"POL", "PT":"PRT", "RO":"ROU", "SK":"SVK",
    "SI":"SVN", "ES":"ESP", "SE":"SWE",
}


def resolve_country_code(raw: str) -> str:
    # Accept ISO-3 (DEU), ISO-2 (DE), and exact localized country names where available.
    named = resolve_eu_country_code(str(raw)) if "resolve_eu_country_code" in globals() else ""
    if named:
        return named
    code = str(raw).strip().upper().replace(" ", "")
    return COUNTRY_CODE_ALIASES.get(code, code)


def vector_currency_names(spec: Dict[str, object]) -> Dict[str, str]:
    return {lang: currency_display_name("", spec, lang) for lang in SUPPORTED_LANGS}

def action_label(action: str, lang: str) -> str:
    return ACTION_LABELS.get(action, {}).get(normalize_lang(lang), action)

def scenario_label(scenario: str, lang: str) -> str:
    return SCENARIO_LABELS.get(scenario, {}).get(normalize_lang(lang), scenario)

# -----------------------------------------------------------------------------
# 4. Data classes
# -----------------------------------------------------------------------------

@dataclass
class VectorCurrency:
    code: str
    name_en: str
    name_de: str
    home: str
    angle: float
    color: str
    length: float = 1.0
    power: float = 50.0
    flow: float = 0.0
    share: float = 1.0 / 3.0
    last_target: float = 0.0
    start_angle: float = 0.0
    names: Dict[str, str] = field(default_factory=dict)

    def reset_flow(self) -> None:
        self.flow = 0.0

    def name(self, lang: str) -> str:
        lang = normalize_lang_code(lang)
        return self.names.get(lang, self.name_de if lang == "de" else self.name_en)


@dataclass
class Sector:
    code: str
    name_en: str
    name_de: str
    need: float
    labor_need: float
    productivity: float
    base_price: float
    angle_bias: float
    exportability: float
    volatility: float
    color: str

    def name(self, lang: str) -> str:
        lang = normalize_lang_code(lang)
        return sector_label(self.code, lang) if self.code in SECTOR_NAMES else (self.name_de if lang == "de" else self.name_en)


@dataclass
class AngleState:
    gbw: float
    buw: float
    last_hw: float = 0.0
    last_currency: str = ""
    last_klang: float = 0.0

    def action_angle(self) -> float:
        # The action angle lies between the government good pole and the people's popular pole.
        self.last_hw = circular_mean([self.gbw, self.buw], [0.54, 0.46])
        return self.last_hw

    def orth_error(self) -> float:
        return angle_distance(self.buw, self.gbw + 90.0)


@dataclass
class Country:
    code: str
    name: str
    currency: str
    color: str
    population: float
    tradition: float
    govt_power_style: float
    wellbeing_style: float
    production: Dict[str, float] = field(default_factory=dict)
    labor_hours: Dict[str, float] = field(default_factory=dict)
    imports: Dict[str, float] = field(default_factory=dict)
    exports: Dict[str, float] = field(default_factory=dict)
    demand: Dict[str, float] = field(default_factory=dict)
    supply: Dict[str, float] = field(default_factory=dict)
    satisfaction: Dict[str, float] = field(default_factory=dict)
    prices: Dict[str, float] = field(default_factory=dict)
    angles: Dict[Tuple[str, str], AngleState] = field(default_factory=dict)
    wbi: float = 55.0
    mpi: float = 55.0
    wsk: float = 55.0
    spg: float = 25.0
    fatigue: float = 0.0
    last_currency_mix: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    role: str = ""
    names: Dict[str, str] = field(default_factory=dict)

    def display_name(self, lang: str) -> str:
        return local_dict(self.names, lang) if self.names else self.name

    def reset_tick(self, sectors: List[Sector]) -> None:
        self.production = {s.code: 0.0 for s in sectors}
        self.labor_hours = {s.code: 0.0 for s in sectors}
        self.imports = {s.code: 0.0 for s in sectors}
        self.exports = {s.code: 0.0 for s in sectors}
        self.demand = {s.code: 0.0 for s in sectors}
        self.supply = {s.code: 0.0 for s in sectors}
        self.satisfaction = {s.code: 0.0 for s in sectors}
        self.prices = {s.code: 0.0 for s in sectors}
        self.notes = []
        self.last_currency_mix = {}


@dataclass
class TransactionRecord:
    tick: int
    country: str
    sector: str
    action: str
    amount_ve: float
    hw: float
    chosen_currency: str
    klang_best: float
    shares: Dict[str, float]
    price_ve: float


@dataclass
class TradeRecord:
    tick: int
    sector: str
    exporter: str
    importer: str
    amount: float
    currency: str
    wk_deg: float
    angular_work: float
    joint_hw: float


# -----------------------------------------------------------------------------
# 5. UTF-8 drawing canvas
# -----------------------------------------------------------------------------

class Canvas:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.cells: List[List[Tuple[str, str]]] = [[(" ", "") for _ in range(w)] for _ in range(h)]

    def put(self, x: int, y: int, ch: str, color: str = "") -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.cells[y][x] = (ch, color)

    def put_text(self, x: int, y: int, text: str, color: str = "") -> None:
        for i, ch in enumerate(text):
            self.put(x + i, y, ch, color)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, ch: str, color: str = "") -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.put(x, y, ch, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def render(self) -> str:
        lines = []
        for row in self.cells:
            pieces = []
            for ch, color in row:
                pieces.append(col(ch, color) if color else ch)
            lines.append("".join(pieces).rstrip())
        return "\n".join(lines)


def compass_canvas(points: List[Tuple[float, str, str, str]], width: int = 65, height: int = 27,
                   radius: int = 11, title: str = "") -> str:
    c = Canvas(width, height)
    cx = width // 2
    cy = height // 2
    # Circle
    for deg in range(0, 360, 3):
        x = int(round(cx + math.cos(math.radians(deg)) * radius))
        y = int(round(cy - math.sin(math.radians(deg)) * radius))
        c.put(x, y, "◦", Ansi.DIM)
    # Axis
    for x in range(cx - radius - 2, cx + radius + 3):
        c.put(x, cy, "─", Ansi.DIM)
    for y in range(cy - radius - 1, cy + radius + 2):
        c.put(cx, y, "│", Ansi.DIM)
    c.put(cx, cy, "┼", Ansi.WHITE)
    c.put_text(cx + radius + 4, cy, "0°", Ansi.DIM)
    c.put_text(cx - radius - 6, cy, "180°", Ansi.DIM)
    c.put_text(cx - 2, cy - radius - 3, "90°", Ansi.DIM)
    c.put_text(cx - 3, cy + radius + 2, "270°", Ansi.DIM)
    if title:
        c.put_text(1, 0, title[:width - 2], Ansi.BOLD)
    # Points / vectors
    for angle, label, color, end_ch in points:
        x = int(round(cx + math.cos(math.radians(angle)) * radius))
        y = int(round(cy - math.sin(math.radians(angle)) * radius))
        c.draw_line(cx, cy, x, y, "•", color)
        c.put(x, y, end_ch or angle_arrow(angle), color + Ansi.BOLD if COLOR_ON else "")
        # label near endpoint
        lx = x + (2 if x >= cx else -len(label) - 1)
        ly = y + (1 if y >= cy else -1)
        c.put_text(lx, ly, label, color + Ansi.BOLD if COLOR_ON else "")
    return c.render()


# -----------------------------------------------------------------------------
# 6. Simulation world
# -----------------------------------------------------------------------------

class AngularEconomy:
    def __init__(self, seed: int = 7, ticks: int = 18, detail: str = "full",
                 report_every: int = 1, width: int = 118, colors: bool = True,
                 explanations: bool = True, lang: str = "en", scenario: str = "baseline",
                 gallery: bool = True, compare_scenarios: bool = True,
                 selected_country_ids: Optional[List[str]] = None, auto_seed: bool = False):
        global COLOR_ON, WRAP_WIDTH
        COLOR_ON = colors
        # Screen-width safety margin: render five columns shorter than detected/selected width.
        WRAP_WIDTH = max(50, int(width) - 5)
        self.rng = random.Random(seed)
        self.seed = int(seed)
        self.auto_seed = bool(auto_seed)
        self.max_ticks = ticks
        self.detail = detail
        self.report_every = max(1, report_every)
        self.explanations = explanations
        self.lang = normalize_lang_code(lang)
        self.scenario = scenario
        self.gallery = gallery
        self.compare_scenarios = compare_scenarios
        self.t = 0
        self.params = self._scenario_parameters(scenario)
        self.selected_eu_countries = self._select_eu_countries(selected_country_ids)
        self.selected_eu_codes = [str(c["code"]) for c in self.selected_eu_countries]
        self.country_slot_index: Dict[str, int] = {str(c["code"]): i for i, c in enumerate(self.selected_eu_countries)}
        self.sectors = self._make_sectors()
        self.countries = self._make_countries()
        self.currencies = self._make_currencies()
        self.history: List[Dict[str, object]] = []
        self.transaction_history: List[TransactionRecord] = []
        self.trade_history: List[TradeRecord] = []
        self.currency_history: List[Dict[str, object]] = []
        self._apply_scenario()
        self._init_angles()

    # ------------------------------------------------------------------
    # Initialization and scenarios
    # ------------------------------------------------------------------

    def _scenario_parameters(self, scenario: str) -> Dict[str, float]:
        base = {
            "angle_noise": 18.0,
            "pop_noise": 22.0,
            "orth_noise_multiplier": 1.0,
            "production_scale": 1.0,
            "demand_scale": 1.0,
            "trade_scale": 1.0,
            "power_bias": 0.0,
            "wellbeing_bias": 0.0,
            "currency_drift_scale": 1.0,
            "fragmentation": 0.0,
            "scarcity_price": 1.0,
        }
        if scenario == "resonance":
            base.update({"angle_noise": 6.0, "pop_noise": 7.0, "production_scale": 1.08,
                         "demand_scale": 0.98, "trade_scale": 1.05, "wellbeing_bias": 8.0,
                         "power_bias": 4.0, "fragmentation": -0.25})
        elif scenario == "power":
            base.update({"angle_noise": 11.0, "pop_noise": 22.0, "production_scale": 1.03,
                         "demand_scale": 1.00, "trade_scale": 0.92, "power_bias": 14.0,
                         "wellbeing_bias": -5.0, "currency_drift_scale": 1.25, "fragmentation": 0.12})
        elif scenario == "wellbeing":
            base.update({"angle_noise": 12.0, "pop_noise": 9.0, "production_scale": 1.02,
                         "demand_scale": 0.99, "trade_scale": 0.95, "power_bias": -4.0,
                         "wellbeing_bias": 13.0, "fragmentation": -0.15})
        elif scenario == "fragmented":
            base.update({"angle_noise": 38.0, "pop_noise": 55.0, "production_scale": 0.92,
                         "demand_scale": 1.04, "trade_scale": 0.68, "power_bias": -2.0,
                         "wellbeing_bias": -8.0, "fragmentation": 0.55, "scarcity_price": 1.14})
        elif scenario == "scarcity":
            base.update({"angle_noise": 20.0, "pop_noise": 25.0, "production_scale": 0.74,
                         "demand_scale": 1.24, "trade_scale": 1.10, "power_bias": 2.0,
                         "wellbeing_bias": -12.0, "fragmentation": 0.22, "scarcity_price": 1.35})
        elif scenario == "tradeboom":
            base.update({"angle_noise": 15.0, "pop_noise": 18.0, "production_scale": 1.10,
                         "demand_scale": 1.02, "trade_scale": 1.62, "power_bias": 5.0,
                         "wellbeing_bias": 3.0, "currency_drift_scale": 1.18, "fragmentation": 0.05})
        return base

    def _select_eu_countries(self, selected_country_ids: Optional[List[str]] = None) -> List[Dict[str, object]]:
        if selected_country_ids:
            result: List[Dict[str, object]] = []
            seen = set()
            for raw in selected_country_ids:
                code = resolve_eu_country_code(str(raw)) or resolve_country_code(str(raw))
                if code in EU_COUNTRY_BY_ISO3 and code not in seen:
                    result.append(EU_COUNTRY_BY_ISO3[code])
                    seen.add(code)
            if len(result) >= 3:
                return result[:3]
            # If fewer than three valid codes were supplied, keep them and fill the rest seed-stably.
            for profile in self.rng.sample(EU_COUNTRIES, len(EU_COUNTRIES)):
                code = str(profile["code"])
                if code not in seen:
                    result.append(profile)
                    seen.add(code)
                if len(result) == 3:
                    return result
        return self.rng.sample(EU_COUNTRIES, 3)

    def _make_sectors(self) -> List[Sector]:
        return [
            Sector("FOO", "food",        "Nahrung",       1.18, 0.84, 1.10, 1.10,   6.0, 0.35, 0.38, Ansi.BRIGHT_GREEN),
            Sector("ENE", "energy",      "Energie",       1.05, 0.96, 0.86, 1.62,  38.0, 0.62, 0.62, Ansi.BRIGHT_YELLOW),
            Sector("HOU", "housing",     "Wohnen",        1.00, 0.92, 0.76, 1.86, -24.0, 0.12, 0.30, Ansi.YELLOW),
            Sector("HEA", "health",      "Gesundheit",    1.12, 1.18, 0.92, 1.72,  74.0, 0.08, 0.34, Ansi.BRIGHT_MAGENTA),
            Sector("EDU", "education",   "Bildung",       0.88, 0.78, 1.12, 1.12, 112.0, 0.05, 0.28, Ansi.BRIGHT_CYAN),
            Sector("CUL", "culture",     "Kultur",        0.68, 0.42, 1.18, 0.82, 146.0, 0.30, 0.72, Ansi.MAGENTA),
            Sector("SEC", "security",    "Sicherheit",    0.74, 0.86, 0.98, 1.28, -82.0, 0.04, 0.58, Ansi.BRIGHT_BLUE),
            Sector("DAT", "data",        "Daten",         0.92, 0.56, 1.46, 1.20, 190.0, 0.76, 0.66, Ansi.CYAN),
            Sector("MOB", "mobility",    "Mobilität",     0.82, 0.73, 0.90, 1.40, 232.0, 0.58, 0.48, Ansi.BLUE),
        ]

    def _make_currencies(self) -> Dict[str, VectorCurrency]:
        data: Dict[str, VectorCurrency] = {}
        base_angles = [8.0, 128.0, 248.0]
        for i, c in enumerate(self.countries.values()):
            code = c.currency
            profile = EU_COUNTRY_BY_ISO3.get(c.code, {"code": c.code, "names": c.names})
            names = vector_currency_names(profile)
            # The angle changes by country texture, but length stays fixed at 1 VE.
            angle = norm_angle(base_angles[i] + signed_delta(base_angles[i], c.tradition * 360.0) * 0.08 + self.rng.uniform(-4.5, 4.5))
            cur = VectorCurrency(code, names.get("en", f"Euro-vector {c.code}"), names.get("de", f"Euro-Vektor {c.code}"),
                                 c.code, angle, c.color, 1.0, 50.0 + c.mpi * 0.18)
            cur.names = names
            cur.start_angle = cur.angle
            data[code] = cur
        return data

    def _make_countries(self) -> Dict[str, Country]:
        # Three real EU countries are selected by the seed and placed into three structural roles.
        # The role values are abstract simulation texture, not real demographic statistics.
        roles = [
            ("A", "EA", Ansi.BRIGHT_RED,    1.12, 0.82, 0.68, 0.32, 54.0, 63.0, 58.0, 28.0),
            ("B", "EB", Ansi.BRIGHT_GREEN, 0.98, 0.58, 0.43, 0.67, 66.0, 47.0, 57.0, 24.0),
            ("C", "EC", Ansi.BRIGHT_BLUE,  1.06, 0.70, 0.57, 0.49, 51.0, 56.0, 61.0, 31.0),
        ]
        out: Dict[str, Country] = {}
        for i, profile in enumerate(self.selected_eu_countries):
            role, currency, color, population, tradition, gov_style, well_style, wbi, mpi, wsk, spg = roles[i]
            names = profile["names"]  # type: ignore[index]
            code = str(profile["code"])
            c = Country(
                code, country_name(profile, self.lang), currency, color,
                population=clamp(population + self.rng.uniform(-0.045, 0.045), 0.72, 1.28),
                tradition=clamp(tradition + self.rng.uniform(-0.04, 0.04), 0.35, 0.95),
                govt_power_style=clamp(gov_style + self.rng.uniform(-0.035, 0.035), 0.20, 0.90),
                wellbeing_style=clamp(well_style + self.rng.uniform(-0.035, 0.035), 0.20, 0.90),
                wbi=wbi + self.rng.uniform(-2.5, 2.5),
                mpi=mpi + self.rng.uniform(-2.5, 2.5),
                wsk=wsk + self.rng.uniform(-2.5, 2.5),
                spg=spg + self.rng.uniform(-2.0, 2.0),
            )
            c.role = role
            c.names = names  # type: ignore[assignment]
            out[c.code] = c
        return out

    def _apply_scenario(self) -> None:
        for c in self.countries.values():
            c.wbi = clamp(c.wbi + self.params["wellbeing_bias"], 0, 100)
            c.mpi = clamp(c.mpi + self.params["power_bias"], 0, 100)
            c.govt_power_style = clamp(c.govt_power_style + self.params["power_bias"] / 120.0, 0.1, 0.95)
            c.wellbeing_style = clamp(c.wellbeing_style + self.params["wellbeing_bias"] / 120.0, 0.1, 0.95)
        if self.scenario == "power":
            for cur in self.currencies.values():
                cur.power = clamp(cur.power + 8.0, 0, 100)
        if self.scenario == "fragmented":
            # Move currency angles slightly away from clean 120-degree spacing.
            shifts = {"EA": -18.0, "EB": 27.0, "EC": -34.0}
            for code, shift in shifts.items():
                self.currencies[code].angle = norm_angle(self.currencies[code].angle + shift)
                self.currencies[code].start_angle = self.currencies[code].angle
        if self.scenario == "resonance":
            # Keep identical length; only rotate currencies a little toward a clean common ring.
            shifts = {"EA": 0.0, "EB": -4.0, "EC": 4.0}
            for code, shift in shifts.items():
                self.currencies[code].angle = norm_angle(self.currencies[code].angle + shift)
                self.currencies[code].start_angle = self.currencies[code].angle

    def _init_angles(self) -> None:
        ordered_codes = list(self.countries.keys())
        base_country_offsets = [-12.0, 18.0, -28.0]
        base_pop_offsets = [7.0, -16.0, 11.0]
        country_offsets = {code: base_country_offsets[i] for i, code in enumerate(ordered_codes)}
        pop_offsets = {code: base_pop_offsets[i] for i, code in enumerate(ordered_codes)}
        for c in self.countries.values():
            cur = self.currencies[c.currency]
            for sec in self.sectors:
                for action in ACTIONS:
                    noise = circular_noise(self.rng, self.params["angle_noise"])
                    gbw = cur.angle + sec.angle_bias + ACTION_OFFSET[action] + country_offsets[c.code] + noise
                    pop_noise = circular_noise(self.rng, self.params["pop_noise"])
                    if self.params["fragmentation"] > 0.4:
                        pop_noise += circular_noise(self.rng, 80.0 * self.params["fragmentation"])
                    buw = gbw + 90.0 + pop_offsets[c.code] + pop_noise
                    c.angles[(action, sec.code)] = AngleState(norm_angle(gbw), norm_angle(buw))

    # ------------------------------------------------------------------
    # Core simulation functions
    # ------------------------------------------------------------------

    def specialization_multiplier(self, country_code: str, sector_code: str) -> float:
        # Country-sector competence creates actual export possibilities.
        # For random EU countries this is deterministic model texture, not a real statistic.
        n = sum(ord(ch) for ch in (country_code + sector_code))
        return 0.78 + ((n * 17) % 65) / 100.0

    def choose_currency(self, hw: float) -> Tuple[str, float, Dict[str, float]]:
        codes = list(self.currencies.keys())
        scores = [klang(self.currencies[k].angle, hw) for k in codes]
        shares_list = softmax01(scores, temperature=7.5)
        shares = {k: shares_list[i] for i, k in enumerate(codes)}
        best = max(codes, key=lambda k: shares[k])
        return best, scores[codes.index(best)], shares

    def price_for(self, country: Country, sec: Sector, action: str, hw: float, supply_ratio: float) -> float:
        home_cur = self.currencies[country.currency]
        currency_fit = klang(home_cur.angle, hw)
        shortage_factor = 1.0 + clamp(1.0 - supply_ratio, 0.0, 1.0) * 0.85 * self.params["scarcity_price"]
        angle_factor = 0.72 + (1.0 - currency_fit) * 0.95
        action_factor = {"BUY": 1.00, "SELL": 0.94, "WORK": 0.82}[action]
        mood_factor = 1.08 - clamp(country.wbi / 100.0, 0.0, 1.0) * 0.16
        return max(0.05, sec.base_price * shortage_factor * angle_factor * action_factor * mood_factor)

    def record_transaction(self, rec: TransactionRecord) -> None:
        self.transaction_history.append(rec)
        for code, share in rec.shares.items():
            self.currencies[code].flow += rec.amount_ve * share

    def run(self) -> None:
        self.print_header()
        if self.explanations:
            self.print_preface()
        for t in range(1, self.max_ticks + 1):
            self.t = t
            self.step()
            if t % self.report_every == 0:
                self.print_tick_report(t)
        self.print_final_report()
        if self.gallery:
            self.print_utf8_gallery()

    def simulate_silent(self) -> None:
        for t in range(1, self.max_ticks + 1):
            self.t = t
            self.step()

    def step(self) -> None:
        for cur in self.currencies.values():
            cur.reset_flow()
        for c in self.countries.values():
            c.reset_tick(self.sectors)

        self._simulate_labor_and_production()
        self._simulate_trade_triangle()
        self._simulate_goods_and_transactions()
        self._compute_indices()
        self._rotate_angles()
        self._snapshot_history()

    def _simulate_labor_and_production(self) -> None:
        for c in self.countries.values():
            labor_pressure = 0.0
            for sec in self.sectors:
                st = c.angles[("WORK", sec.code)]
                hw = st.action_angle()
                best, best_k, shares = self.choose_currency(hw)
                st.last_currency = best
                st.last_klang = best_k
                popular_fit = klang(hw, st.buw)
                gov_fit = klang(hw, st.gbw)
                base_hours = c.population * sec.labor_need * 38.0
                hours = base_hours * (0.48 + 0.52 * best_k) * (0.72 + 0.28 * popular_fit)
                hours *= (0.92 + 0.10 * c.tradition)
                c.labor_hours[sec.code] = hours
                production = hours / 38.0 * sec.productivity * (0.82 + 0.26 * gov_fit)
                production *= self.specialization_multiplier(c.code, sec.code)
                production *= self.params["production_scale"]
                c.production[sec.code] = production
                unpop = klang(hw, st.buw + 180.0)
                labor_pressure += sec.labor_need * unpop * (0.8 + 0.4 * sec.volatility)
                price = self.price_for(c, sec, "WORK", hw, supply_ratio=1.0)
                self.record_transaction(TransactionRecord(
                    self.t, c.code, sec.code, "WORK", amount_ve=hours * price / 38.0,
                    hw=hw, chosen_currency=best, klang_best=best_k, shares=shares, price_ve=price))
            c.fatigue = clamp(0.72 * c.fatigue + 3.3 * labor_pressure / max(1.0, len(self.sectors)), 0.0, 100.0)

    def _simulate_trade_triangle(self) -> None:
        # Estimate demand before trade so that excess and deficit are visible.
        for c in self.countries.values():
            for sec in self.sectors:
                soft_need = 1.0 + (c.wbi - 55.0) / 230.0
                if sec.code in ("CUL", "EDU", "DAT", "MOB"):
                    need = c.population * sec.need * clamp(soft_need, 0.75, 1.25)
                else:
                    need = c.population * sec.need
                c.demand[sec.code] = max(0.01, need * self.params["demand_scale"])

        for sec in self.sectors:
            excess = []
            deficit = []
            for c in self.countries.values():
                e = c.production[sec.code] - c.demand[sec.code]
                if e > 0:
                    excess.append([c, e])
                elif e < 0:
                    deficit.append([c, -e])
            excess.sort(key=lambda x: x[1], reverse=True)
            deficit.sort(key=lambda x: x[1], reverse=True)
            for ex in excess:
                exporter, ex_amt = ex[0], ex[1]
                if ex_amt <= 0:
                    continue
                for df in deficit:
                    importer, df_amt = df[0], df[1]
                    if df_amt <= 0 or ex_amt <= 0 or exporter.code == importer.code:
                        continue
                    sell_st = exporter.angles[("SELL", sec.code)]
                    buy_st = importer.angles[("BUY", sec.code)]
                    sell_hw = sell_st.action_angle()
                    buy_hw = buy_st.action_angle()
                    joint_hw = circular_mean([sell_hw, buy_hw], [0.50, 0.50])
                    best, best_k, shares = self.choose_currency(joint_hw)
                    trade_fit = best_k * (0.62 + 0.38 * klang(sell_hw, buy_hw))
                    amount = min(ex_amt, df_amt) * sec.exportability * self.params["trade_scale"] * (0.28 + 0.72 * trade_fit)
                    if amount <= 0.0001:
                        continue
                    exporter.exports[sec.code] += amount
                    importer.imports[sec.code] += amount
                    ex_amt -= amount
                    df[1] -= amount
                    price = (self.price_for(exporter, sec, "SELL", sell_hw, 1.0) +
                             self.price_for(importer, sec, "BUY", buy_hw, 1.0)) / 2.0
                    amount_ve = amount * price
                    for code, share in shares.items():
                        self.currencies[code].flow += amount_ve * share
                    wk = angle_distance(self.currencies[exporter.currency].angle, self.currencies[best].angle)
                    ua = math.radians(wk) * amount_ve
                    self.trade_history.append(TradeRecord(self.t, sec.code, exporter.code, importer.code,
                                                          amount, best, wk, ua, joint_hw))
                ex[1] = ex_amt

    def _simulate_goods_and_transactions(self) -> None:
        for c in self.countries.values():
            for sec in self.sectors:
                final_supply = max(0.0, c.production[sec.code] - c.exports[sec.code] + c.imports[sec.code])
                c.supply[sec.code] = final_supply
                demand = max(0.01, c.demand[sec.code])
                supply_ratio = clamp(final_supply / demand, 0.0, 1.6)
                satisfaction = clamp(final_supply / demand, 0.0, 1.0)
                c.satisfaction[sec.code] = satisfaction

                buy_st = c.angles[("BUY", sec.code)]
                buy_hw = buy_st.action_angle()
                best, best_k, shares = self.choose_currency(buy_hw)
                buy_st.last_currency = best
                buy_st.last_klang = best_k
                price_buy = self.price_for(c, sec, "BUY", buy_hw, supply_ratio)
                c.prices[sec.code] = price_buy
                amount_ve_buy = demand * price_buy * (0.42 + 0.58 * satisfaction)
                self.record_transaction(TransactionRecord(self.t, c.code, sec.code, "BUY", amount_ve_buy,
                                                          buy_hw, best, best_k, shares, price_buy))

                sell_st = c.angles[("SELL", sec.code)]
                sell_hw = sell_st.action_angle()
                best_s, best_k_s, shares_s = self.choose_currency(sell_hw)
                sell_st.last_currency = best_s
                sell_st.last_klang = best_k_s
                price_sell = self.price_for(c, sec, "SELL", sell_hw, supply_ratio)
                amount_ve_sell = max(0.0, c.production[sec.code]) * price_sell * 0.36
                self.record_transaction(TransactionRecord(self.t, c.code, sec.code, "SELL", amount_ve_sell,
                                                          sell_hw, best_s, best_k_s, shares_s, price_sell))
        total_flow = sum(cur.flow for cur in self.currencies.values())
        for cur in self.currencies.values():
            cur.share = cur.flow / total_flow if total_flow > 0 else 1.0 / 3.0

    def _compute_indices(self) -> None:
        for c in self.countries.values():
            mix = {k: 0.0 for k in self.currencies}
            country_flow = 0.0
            for rec in self.transaction_history:
                if rec.tick == self.t and rec.country == c.code:
                    country_flow += rec.amount_ve
                    for code, sh in rec.shares.items():
                        mix[code] += rec.amount_ve * sh
            if country_flow > 0:
                c.last_currency_mix = {k: v / country_flow for k, v in mix.items()}
            else:
                c.last_currency_mix = {k: 1.0 / 3.0 for k in mix}

            need_weighted_sat = 0.0
            pop_harmony = 0.0
            gov_pop_gap = 0.0
            curr_gap = 0.0
            orth_gap = 0.0
            weight_sum = 0.0
            production_ratio_acc = 0.0
            price_pressure = 0.0

            for sec in self.sectors:
                w = sec.need
                weight_sum += w
                need_weighted_sat += c.satisfaction[sec.code] * w
                production_ratio_acc += clamp(c.production[sec.code] / max(0.01, c.demand[sec.code]), 0.0, 1.6) * w
                price_pressure += c.prices[sec.code] / max(0.01, sec.base_price) * w
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    hw = st.last_hw if st.last_hw else st.action_angle()
                    pop_harmony += klang(hw, st.buw) * (w / 3.0)
                    gov_pop_gap += angle_distance(st.gbw, st.buw - 90.0) / 90.0 * (w / 3.0)
                    best_currency = self.currencies.get(st.last_currency, self.currencies[c.currency])
                    curr_gap += (1.0 - klang(best_currency.angle, hw)) * (w / 3.0)
                    orth_gap += st.orth_error() / 90.0 * (w / 3.0)

            weight_sum = max(weight_sum, 0.0001)
            sat = need_weighted_sat / weight_sum
            prod_ratio = production_ratio_acc / weight_sum
            pop_h = pop_harmony / weight_sum
            gov_pop = clamp(gov_pop_gap / weight_sum, 0.0, 2.0)
            curr_g = clamp(curr_gap / weight_sum, 0.0, 1.0)
            orth_g = clamp(orth_gap / weight_sum, 0.0, 2.0)
            price_p = price_pressure / weight_sum

            own_share = c.last_currency_mix.get(c.currency, 0.0)
            own_currency = self.currencies[c.currency]
            gov_currency_fit = []
            for sec in self.sectors:
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    gov_currency_fit.append(klang(own_currency.angle, st.gbw))
            gov_fit_avg = sum(gov_currency_fit) / len(gov_currency_fit)

            trade_flow = sum(c.imports.values()) + sum(c.exports.values())
            trade_norm = clamp(trade_flow / (sum(c.demand.values()) + 0.01), 0.0, 1.0)

            wbi_target = 100.0 * (0.58 * sat + 0.30 * pop_h + 0.12 * clamp(1.0 - c.fatigue / 70.0, 0.0, 1.0))
            wbi_target = wbi_target * (0.90 + 0.12 * c.wellbeing_style)

            mpi_target = 100.0 * (0.52 * own_share + 0.26 * gov_fit_avg + 0.14 * clamp(prod_ratio / 1.25, 0.0, 1.0) + 0.08 * trade_norm)
            mpi_target = mpi_target * (0.92 + 0.10 * c.govt_power_style)

            spg_target = 100.0 * clamp(0.34 * gov_pop + 0.28 * curr_g + 0.22 * orth_g + 0.16 * clamp(price_p - 1.0, 0.0, 1.4), 0.0, 1.0)
            wsk_target = 100.0 * clamp(0.42 * sat + 0.27 * clamp(prod_ratio / 1.2, 0.0, 1.0) + 0.17 * trade_norm + 0.14 * (1.0 - spg_target / 110.0), 0.0, 1.0)

            c.wbi = clamp(0.72 * c.wbi + 0.28 * wbi_target, 0.0, 100.0)
            c.mpi = clamp(0.70 * c.mpi + 0.30 * mpi_target, 0.0, 100.0)
            c.spg = clamp(0.68 * c.spg + 0.32 * spg_target, 0.0, 100.0)
            c.wsk = clamp(0.70 * c.wsk + 0.30 * wsk_target, 0.0, 100.0)

            weakest = min(self.sectors, key=lambda s: c.satisfaction[s.code])
            strongest = max(self.sectors, key=lambda s: c.satisfaction[s.code])
            if c.satisfaction[weakest.code] < 0.72:
                c.notes.append(L(self.lang,
                    f"scarcity angle in {weakest.name(self.lang)} ({c.satisfaction[weakest.code]*100:.0f}% of need covered)",
                    f"Mangelwinkel bei {weakest.name(self.lang)} ({c.satisfaction[weakest.code]*100:.0f}% Bedarf gedeckt)"))
            if c.last_currency_mix.get(c.currency, 0.0) < 0.36:
                dominant = max(c.last_currency_mix, key=lambda k: c.last_currency_mix[k])
                c.notes.append(L(self.lang,
                    f"foreign vector currency {dominant} over-sounds the home vector",
                    f"Fremdwährung {dominant} überklingt die eigene Währung"))
            if c.satisfaction[strongest.code] > 0.98:
                c.notes.append(L(self.lang,
                    f"stable coverage in {strongest.name(self.lang)}",
                    f"stabile Deckung bei {strongest.name(self.lang)}"))

        for code, cur in self.currencies.items():
            home = self.countries[cur.home]
            target = 100.0 * (0.58 * cur.share + 0.42 * home.mpi / 100.0)
            cur.power = clamp(0.78 * cur.power + 0.22 * target, 0.0, 100.0)

    def _rotate_angles(self) -> None:
        for code, cur in self.currencies.items():
            angles = [cur.angle]
            weights = [2.0 + cur.power / 50.0]
            for rec in self.transaction_history:
                if rec.tick != self.t:
                    continue
                sh = rec.shares.get(code, 0.0)
                if sh > 0.08:
                    angles.append(rec.hw)
                    weights.append(sh * rec.amount_ve / 8.0)
            home = self.countries[cur.home]
            for sec in self.sectors:
                for action in ACTIONS:
                    st = home.angles[(action, sec.code)]
                    angles.append(st.gbw)
                    weights.append(0.06 * home.govt_power_style)
            target = circular_mean(angles, weights)
            cur.last_target = target
            cur.angle = rotate_towards(cur.angle, target, (0.020 + 0.0006 * cur.power) * self.params["currency_drift_scale"])
            cur.length = 1.0  # Hard rule: all vector-currency lengths remain Euro length.

        for c in self.countries.values():
            own_cur = self.currencies[c.currency]
            for sec in self.sectors:
                sat = c.satisfaction.get(sec.code, 0.8)
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    hw = st.last_hw if st.last_hw else st.action_angle()
                    gov_target = circular_mean([st.gbw, own_cur.angle, hw],
                                               [2.4 * c.tradition, 1.1 * c.govt_power_style, 0.6 + c.mpi / 120.0])
                    st.gbw = rotate_towards(st.gbw, gov_target, 0.006 + 0.010 * sec.volatility)
                    if action == "BUY":
                        pop_target = hw if sat >= 0.82 else norm_angle(hw + 180.0)
                        pop_rate = 0.012 + 0.018 * sec.volatility
                    elif action == "WORK":
                        pop_target = hw if c.fatigue < 32 else norm_angle(hw + 180.0)
                        pop_rate = 0.009 + 0.012 * sec.volatility
                    else:
                        export_signal = clamp(c.exports[sec.code] / max(0.01, c.production[sec.code]), 0.0, 1.0)
                        pop_target = hw if export_signal > 0.10 or sat > 0.88 else circular_mean([hw, st.buw], [0.4, 1.0])
                        pop_rate = 0.007 + 0.010 * sec.volatility
                    ortho_anchor = norm_angle(st.gbw + 90.0)
                    mixed_target = circular_mean([pop_target, ortho_anchor], [1.0, 0.55 + c.tradition])
                    st.buw = rotate_towards(st.buw, mixed_target, pop_rate)

    def _snapshot_history(self) -> None:
        for c in self.countries.values():
            row = {
                "tick": self.t,
                "country": c.code,
                "WBI": round(c.wbi, 4),
                "MPI": round(c.mpi, 4),
                "ES": round(c.wsk, 4),
                "TD": round(c.spg, 4),
                "FTD": round(c.fatigue, 4),
                "own_currency_share": round(c.last_currency_mix.get(c.currency, 0.0), 4),
                "imports": round(sum(c.imports.values()), 4),
                "exports": round(sum(c.exports.values()), 4),
                "production": round(sum(c.production.values()), 4),
                "need": round(sum(c.demand.values()), 4),
            }
            for sec in self.sectors:
                row[f"sat_{sec.code}"] = round(c.satisfaction[sec.code], 4)
                row[f"price_{sec.code}"] = round(c.prices[sec.code], 4)
            self.history.append(row)
        crow = {"tick": self.t}
        for code, cur in self.currencies.items():
            crow[f"{code}_angle"] = round(cur.angle, 4)
            crow[f"{code}_length"] = round(cur.length, 4)
            crow[f"{code}_power"] = round(cur.power, 4)
            crow[f"{code}_flow"] = round(cur.flow, 4)
            crow[f"{code}_share"] = round(cur.share, 4)
        self.currency_history.append(crow)

    # ------------------------------------------------------------------
    # Local explanation blocks
    # ------------------------------------------------------------------

    def print_header(self) -> None:
        title = L(self.lang,
                  "ANGULAR VECTOR-CURRENCY ECONOMY — COLORFUL PYPY3 SIMULATION",
                  "WINKELWÄHRUNGSWIRTSCHAFT — BUNTE PYPY3-SIMULATION")
        print(rainbow(title))
        print(col(hr("═"), Ansi.BRIGHT_MAGENTA))
        print(wrap(L(self.lang,
            "The model simulates three governments, three markets and three competing Euro vectors. EA, EB and EC all have the same vector length: |€⃗| = 1 VE. Competition does not come from a numerical exchange-rate multiplier. It comes from angle, direction, resonance, power attachment and well-being.",
            "Das Modell simuliert drei Regierungen, drei Märkte und drei konkurrierende Euro-Vektoren. EA, EB und EC haben alle dieselbe Vektorlänge: |€⃗| = 1 VE. Konkurrenz entsteht nicht durch einen Zahlen-Wechselkurs. Sie entsteht durch Winkel, Richtung, Resonanz, Machtbindung und Wohlbefinden.")))
        selected = ", ".join(f"{str(c['code'])}={country_name(c, self.lang)}" for c in self.selected_eu_countries)
        print()
        print(col(L(self.lang, "Selected EU countries:", "Ausgewählte EU-Länder:"), Ansi.BOLD), selected)
        print(col(L(self.lang, "Run parameters:", "Startparameter:"), Ansi.BOLD),
              f"seed={self.seed}, ticks={self.max_ticks}, detail={self.detail}, scenario={scenario_label(self.scenario, self.lang)}, lang={self.lang} ({LANGUAGE_NAMES.get(self.lang, self.lang)}), width={WRAP_WIDTH}, colors={'on' if COLOR_ON else 'off'}")
        if self.auto_seed:
            print(dim(L(self.lang, "Random seed was generated automatically; pass --seed N to reproduce exactly.", "Der Zufalls-Seed wurde automatisch erzeugt; mit --seed N lässt sich der Lauf exakt reproduzieren.")))

    def print_preface(self) -> None:
        section(L(self.lang, "How to read this output", "So liest du diese Ausgabe"), Ansi.BRIGHT_MAGENTA)
        print(wrap(L(self.lang,
            "The explanations are not collected into one giant global dictionary. Each simulation part prints only the abbreviations and units that are used in that part. This is intentional: the currency ring explains vector length and angle share; the labor part explains labor hours and fatigue; the goods part explains need, supply and vector-Euro prices; the trade part explains angular work; the index part explains power and well-being.",
            "Die Erklärungen werden nicht in einem einzigen globalen Wörterbuch gesammelt. Jeder Simulationsteil erklärt nur die Kürzel und Einheiten, die genau dort benutzt werden. Das ist Absicht: Der Währungsring erklärt Vektorlänge und Winkelanteil; der Arbeitsteil erklärt Arbeitsstunden und Ermüdung; der Güterteil erklärt Bedarf, Versorgung und Vektor-Euro-Preise; der Handelsteil erklärt Umlenkungsarbeit; der Indexteil erklärt Macht und Wohlbefinden.")))
        print()
        print(wrap(L(self.lang,
            "Important: good versus evil remains good versus evil in the angular sense of this model. It is not a subsidy axis, not a penalty axis, and not positive versus negative. The government sets a good/evil direction on a circle; the population sets an orthogonal popular/unpopular direction; the market action lies between these angular poles.",
            "Wichtig: Gut gegen Böse bleibt in diesem Modell Gut gegen Böse im Winkelsinn. Es ist keine Förderachse, keine Strafachse und nicht positiv gegen negativ. Die Regierung setzt eine Gut/Böse-Richtung auf dem Kreis; die Bevölkerung setzt eine orthogonale Beliebt/Unbeliebt-Richtung; die Markthandlung liegt zwischen diesen Winkelpolen.")))

    def explain_part(self, key: str) -> None:
        if not self.explanations:
            return
        data = self._part_explanations()[key]
        print(wrap(data["why"]))
        print(table(data["headers"], data["rows"]))

    def _part_explanations(self) -> Dict[str, Dict[str, object]]:
        lang = self.lang
        return {
            "currency": {
                "why": L(lang,
                    "This part simulates the three currencies as directions on one ring. Every currency unit has identical Euro-vector length. The table therefore explains angle competition, not numerical exchange rates. The simulated question is: which vector direction attracts the most action flow in this tick?",
                    "Dieser Teil simuliert die drei Währungen als Richtungen auf einem Ring. Jede Währungseinheit hat dieselbe Euro-Vektorlänge. Die Tabelle erklärt deshalb Winkelkonkurrenz, nicht Zahlen-Wechselkurse. Simuliert wird: Welche Vektorrichtung zieht in diesem Tick den meisten Handlungsfluss an?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["EA/EB/EC", L(lang, "currency code", "Währungscode"), L(lang, "The three competing Euro vectors.", "Die drei konkurrierenden Euro-Vektoren.")],
                    ["|€⃗|", "VE", L(lang, "Vector length. It must remain 1.000 for all currencies.", "Vektorlänge. Sie muss bei allen Währungen 1.000 bleiben.")],
                    ["θ°", L(lang, "degrees", "Grad"), L(lang, "Current direction of a currency on the ring.", "Aktuelle Richtung einer Währung auf dem Ring.")],
                    ["Share", L(lang, "0..100%", "0..100%"), L(lang, "Part of this tick's transaction flow captured by the currency angle.", "Anteil des Transaktionsflusses dieses Ticks, der vom Währungswinkel gebunden wird.")],
                    ["Power", "0..100", L(lang, "Accumulated attachment of market action and home government to this vector.", "Aufgebaute Bindung von Markthandlung und Heimatregierung an diesen Vektor.")],
                    ["WK°", L(lang, "degrees", "Grad"), L(lang, "Angle distance between two currencies; not a money exchange rate.", "Winkelabstand zwischen zwei Währungen; kein Geld-Wechselkurs.")],
                    ["KLG", "0..1", L(lang, "Angular resonance. 1 means same direction, 0 means opposite direction.", "Winkelklang. 1 bedeutet gleiche Richtung, 0 bedeutet Gegenrichtung.")],
                ],
            },
            "labor": {
                "why": L(lang,
                    "This part simulates labor as an angular action, not merely as paid time. Work produces goods when the labor angle resonates with a currency, the government's good pole and the population's popular pole. The simulated question is: where does work create capacity, and where does it create fatigue?",
                    "Dieser Teil simuliert Arbeit als Winkelhandlung, nicht nur als bezahlte Zeit. Arbeit erzeugt Güter, wenn der Arbeitswinkel mit Währung, Gut-Pol der Regierung und Beliebt-Pol der Bevölkerung zusammenklingt. Simuliert wird: Wo erzeugt Arbeit Kapazität, und wo erzeugt sie Ermüdung?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["Workθ", L(lang, "degrees", "Grad"), L(lang, "Action angle of labor in a sector.", "Handlungswinkel der Arbeit in einem Sektor.")],
                    ["WC", L(lang, "currency code", "Währungscode"), L(lang, "Currency whose angle fits the labor action best.", "Währung, deren Winkel am besten zur Arbeitsentscheidung passt.")],
                    ["h", L(lang, "hours", "Stunden"), L(lang, "Abstract labor hours allocated this tick.", "Abstrakte Arbeitsstunden dieses Ticks.")],
                    ["Prod", L(lang, "goods units", "Gütereinheiten"), L(lang, "Production created by labor and productivity.", "Produktion, die aus Arbeit und Produktivität entsteht.")],
                    ["FTD", "0..100", L(lang, "Fatigue from labor close to the unpopular pole.", "Ermüdung durch Arbeit nahe am Unbeliebt-Pol.")],
                ],
            },
            "goods": {
                "why": L(lang,
                    "This part simulates need, supply, satisfaction and vector-Euro prices. Price is a count of equal-length Euro vectors. It does not stretch a vector. The simulated question is: how many identical vector-Euro units are needed when supply, demand and angular tension meet?",
                    "Dieser Teil simuliert Bedarf, Versorgung, Deckung und Vektor-Euro-Preise. Preis ist eine Anzahl gleich langer Euro-Vektoren. Er verlängert keinen Vektor. Simuliert wird: Wie viele identische Vektor-Euro-Einheiten werden gebraucht, wenn Versorgung, Nachfrage und Winkelspannung zusammentreffen?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["Need", L(lang, "goods units", "Gütereinheiten"), L(lang, "Population demand in the sector.", "Bevölkerungsbedarf im Sektor.")],
                    ["Supply", L(lang, "goods units", "Gütereinheiten"), L(lang, "Production minus exports plus imports.", "Produktion minus Exporte plus Importe.")],
                    ["Sat", "0..100%", L(lang, "Need covered by final supply.", "Bedarf, der durch Endversorgung gedeckt wird.")],
                    ["Price", "VE/unit", L(lang, "Number of equal vector-Euro units per goods unit.", "Anzahl gleich langer Vektor-Euro-Einheiten pro Gütereinheit.")],
                    ["Buyθ/Sellθ", L(lang, "degrees", "Grad"), L(lang, "Buy and sell action angles.", "Kauf- und Verkaufs-Handlungswinkel.")],
                    ["BC/SC", L(lang, "currency code", "Währungscode"), L(lang, "Best currency for buy/sell angle.", "Beste Währung für Kauf-/Verkaufswinkel.")],
                    ["ODE", L(lang, "degrees", "Grad"), L(lang, "Average orthogonal deviation of good/evil versus popular/unpopular axes.", "Mittlere Orthogonalitätsabweichung der Gut/Böse- zur Beliebt/Unbeliebt-Achse.")],
                ],
            },
            "trade": {
                "why": L(lang,
                    "This part simulates the trade triangle between three countries. Trade is possible when the exporter's sell angle and the importer's buy angle can form a joint action direction. The simulated question is: how much angular work is needed to move goods without changing the equal Euro-vector length?",
                    "Dieser Teil simuliert das Handelsdreieck zwischen drei Ländern. Handel wird möglich, wenn Verkaufswinkel des Exportlandes und Kaufwinkel des Importlandes eine gemeinsame Handlungsrichtung bilden können. Simuliert wird: Wie viel Umlenkungsarbeit ist nötig, um Güter zu bewegen, ohne die gleiche Euro-Vektorlänge zu verändern?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["Route", L(lang, "country→country", "Land→Land"), L(lang, "Exporter to importer.", "Exportland zu Importland.")],
                    ["Q", L(lang, "goods units", "Gütereinheiten"), L(lang, "Traded quantity.", "Gehandelte Menge.")],
                    ["C", L(lang, "currency code", "Währungscode"), L(lang, "Currency angle used by the joint trade action.", "Währungswinkel, der von der gemeinsamen Handelshandlung genutzt wird.")],
                    ["Jointθ", L(lang, "degrees", "Grad"), L(lang, "Mean action angle between exporter sell angle and importer buy angle.", "Mittlerer Handlungswinkel aus Verkaufswinkel des Exporteurs und Kaufwinkel des Importeurs.")],
                    ["WK°", L(lang, "degrees", "Grad"), L(lang, "Angle distance between exporter's home currency and trade currency.", "Winkelabstand zwischen Heimatwährung des Exporteurs und Handelswährung.")],
                    ["UA", "rad·VE", L(lang, "Angular work: vector-Euro amount multiplied by rotation in radians.", "Umlenkungsarbeit: Vektor-Euro-Menge mal Drehung in Radiant.")],
                ],
            },
            "indices": {
                "why": L(lang,
                    "This part simulates the goal system. The economy does not maximize wealth. It tracks well-being, power, economic strength and tension. The simulated question is: who gains power, who gains well-being, and where does the economy weaken because angles do not cohere?",
                    "Dieser Teil simuliert das Zielsystem. Die Wirtschaft maximiert nicht Reichtum. Sie verfolgt Wohlbefinden, Macht, Wirtschaftsstärke und Spannung. Simuliert wird: Wer gewinnt Macht, wer gewinnt Wohlbefinden, und wo wird die Wirtschaft durch fehlenden Winkelzusammenhalt schwächer?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["WBI", "0..100", L(lang, "Well-being index of the population.", "Wohlbefindenindex der Bevölkerung.")],
                    ["MPI", "0..100", L(lang, "Power index of government/currency attachment.", "Machtindex der Bindung von Regierung und Währung.")],
                    ["ES", "0..100", L(lang, "Economic strength under angular competition.", "Wirtschaftsstärke unter Winkelkonkurrenz.")],
                    ["TD", "0..100", L(lang, "Tension degree. Lower is calmer.", "Spannungsgrad. Niedriger ist ruhiger.")],
                    ["OwnS", "0..100%", L(lang, "Domestic share of the home vector currency.", "Inlandsanteil der eigenen Vektorwährung.")],
                    ["DomC", L(lang, "currency code", "Währungscode"), L(lang, "Dominant currency in local transaction flow.", "Dominante Währung im lokalen Transaktionsfluss.")],
                ],
            },
            "drift": {
                "why": L(lang,
                    "This part simulates angle drift. Governments, populations and currencies do not stay frozen. They rotate slowly toward successful, powerful or livable actions. The simulated question is: which directions become habits, and which directions drift away?",
                    "Dieser Teil simuliert Winkeldrift. Regierungen, Bevölkerungen und Währungen bleiben nicht eingefroren. Sie drehen sich langsam zu erfolgreichen, machtvollen oder lebbaren Handlungen. Simuliert wird: Welche Richtungen werden Gewohnheit, und welche Richtungen driften weg?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["Targetθ", L(lang, "degrees", "Grad"), L(lang, "Direction toward which a currency is slowly rotating.", "Richtung, zu der sich eine Währung langsam dreht.")],
                    ["ΔStart", L(lang, "degrees", "Grad"), L(lang, "Distance between current currency angle and its initial angle.", "Abstand zwischen aktuellem Währungswinkel und Anfangswinkel.")],
                    ["GBW°", L(lang, "degrees", "Grad"), L(lang, "Government good/evil angle: direction of the good pole.", "Gut/Böse-Winkel der Regierung: Richtung des Gut-Pols.")],
                    ["BUW°", L(lang, "degrees", "Grad"), L(lang, "Population popular/unpopular angle: direction of the popular pole.", "Beliebt/Unbeliebt-Winkel der Bevölkerung: Richtung des Beliebt-Pols.")],
                    ["ODE", L(lang, "degrees", "Grad"), L(lang, "Deviation from ideal 90° orthogonality between the axes.", "Abweichung von idealer 90°-Orthogonalität der Achsen.")],
                ],
            },
            "final": {
                "why": L(lang,
                    "This final part reads the whole run. It compares final indices and sparks through time. It explains the result in terms of power, well-being and angular weakness, not in terms of being rich or poor.",
                    "Dieser Abschlussteil liest den ganzen Lauf. Er vergleicht Endindizes und Verlaufssparks. Er erklärt das Ergebnis über Macht, Wohlbefinden und Winkelschwäche, nicht über reich oder arm."),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["spark", L(lang, "UTF-8 mini chart", "UTF-8-Minikurve"), L(lang, "Tiny history line from low ▁ to high █.", "Kleine Verlaufslinie von niedrig ▁ bis hoch █.")],
                    ["OwnS last", "0..100%", L(lang, "Home vector currency share in the final tick.", "Anteil der eigenen Vektorwährung im letzten Tick.")],
                    ["Avg", L(lang, "arithmetic mean", "arithmetischer Mittelwert"), L(lang, "Average across three countries or full scenario run.", "Durchschnitt über drei Länder oder den ganzen Szenariolauf.")],
                ],
            },
        }

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def print_tick_report(self, t: int) -> None:
        section(L(self.lang, f"TICK {t}: one simulated period", f"TICK {t}: ein simulierter Zeitabschnitt"), Ansi.BRIGHT_MAGENTA)
        print(wrap(L(self.lang,
            "A tick can be read as a month, a quarter, or a political-market cycle. The order is: currency ring, labor/production, goods/prices, trade triangle, indices, then angle drift and events.",
            "Ein Tick kann als Monat, Quartal oder politischer Marktzyklus gelesen werden. Die Reihenfolge ist: Währungsring, Arbeit/Produktion, Güter/Preise, Handelsdreieck, Indizes, danach Winkeldrift und Ereignisse.")))
        self.print_currency_ring()
        self.print_labor_report()
        self.print_goods_report()
        self.print_trade_summary()
        self.print_country_indices()
        self.print_drift_and_events()

    def print_currency_ring(self) -> None:
        small_section(L(self.lang, "A) Currency ring: three equally long Euro vectors", "A) Währungsring: drei gleich lange Euro-Vektoren"), Ansi.BRIGHT_CYAN)
        self.explain_part("currency")
        rows = []
        row_colors = []
        for cur in self.currencies.values():
            rows.append([
                cur.code,
                cur.name(self.lang),
                cur.home,
                f"{cur.length:.3f} VE",
                angle_label(cur.angle),
                f"{cur.share*100:5.1f}%",
                f"{cur.power:5.1f}",
                angle_label(cur.last_target),
            ])
            row_colors.append(cur.color)
        print(table([L(self.lang, "Code", "Kürzel"), L(self.lang, "Name", "Name"), L(self.lang, "Home", "Heimat"), "|€⃗|", "θ°", L(self.lang, "Share", "Anteil"), L(self.lang, "Power", "Macht"), L(self.lang, "Targetθ", "Zielθ")], rows, row_colors))
        pairs = []
        codes = list(self.currencies.keys())
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                a = self.currencies[codes[i]]
                b = self.currencies[codes[j]]
                pairs.append([f"{a.code}↔{b.code}", f"{angle_distance(a.angle, b.angle):6.1f}°", f"{klang(a.angle, b.angle):.3f}"])
        print(table([L(self.lang, "Pair", "Paar"), "WK°", "KLG"], pairs))

    def sectors_for_detail(self, c: Country) -> List[Sector]:
        if self.detail == "short":
            scored = []
            for s in self.sectors:
                score = (1.0 - c.satisfaction.get(s.code, 0.0)) * 1.5 + c.prices.get(s.code, s.base_price) / max(0.01, s.base_price) * 0.25
                scored.append((score, s))
            return [s for _, s in sorted(scored, key=lambda x: x[0], reverse=True)[:4]]
        if self.detail == "medium":
            return [s for s in self.sectors if s.code in {"FOO", "ENE", "HOU", "HEA", "DAT", "CUL"}]
        return self.sectors

    def print_labor_report(self) -> None:
        small_section(L(self.lang, "B) Labor market and production", "B) Arbeitsmarkt und Produktion"), Ansi.BRIGHT_CYAN)
        self.explain_part("labor")
        for c in self.countries.values():
            print()
            print(col(f"{c.code} — {c.display_name(self.lang)}", c.color + Ansi.BOLD if COLOR_ON else ""))
            rows = []
            row_colors = []
            for sec in self.sectors_for_detail(c):
                st = c.angles[("WORK", sec.code)]
                rows.append([
                    sec.code,
                    sec.name(self.lang),
                    angle_label(st.last_hw),
                    st.last_currency,
                    f"{st.last_klang:.3f}",
                    f"{c.labor_hours[sec.code]:.2f} h",
                    f"{c.production[sec.code]:.2f}",
                    f"{c.fatigue:5.1f}",
                ])
                row_colors.append(sec.color)
            print(table([L(self.lang, "Sec", "Sek"), L(self.lang, "Name", "Name"), "Workθ", "WC", "KLG", "h", "Prod", "FTD"], rows, row_colors))

    def print_goods_report(self) -> None:
        small_section(L(self.lang, "C) Goods market and vector-Euro prices", "C) Gütermarkt und Vektor-Euro-Preise"), Ansi.BRIGHT_CYAN)
        self.explain_part("goods")
        for c in self.countries.values():
            print()
            print(col(f"{c.code} — {c.display_name(self.lang)}", c.color + Ansi.BOLD if COLOR_ON else ""))
            rows = []
            row_colors = []
            for sec in self.sectors_for_detail(c):
                buy = c.angles[("BUY", sec.code)]
                sell = c.angles[("SELL", sec.code)]
                work = c.angles[("WORK", sec.code)]
                oea = (buy.orth_error() + sell.orth_error() + work.orth_error()) / 3.0
                rows.append([
                    sec.code,
                    sec.name(self.lang),
                    f"{c.demand[sec.code]:.2f}",
                    f"{c.supply[sec.code]:.2f}",
                    f"{c.satisfaction[sec.code]*100:5.1f}%",
                    f"{c.prices[sec.code]:.2f} VE",
                    angle_label(buy.last_hw), buy.last_currency,
                    angle_label(sell.last_hw), sell.last_currency,
                    f"{oea:5.1f}°",
                ])
                row_colors.append(sec.color)
            print(table([L(self.lang, "Sec", "Sek"), L(self.lang, "Name", "Name"), L(self.lang, "Need", "Bedarf"), L(self.lang, "Supply", "Versorgung"), L(self.lang, "Sat", "Deckung"), L(self.lang, "Price", "Preis"), "Buyθ", "BC", "Sellθ", "SC", "ODE"], rows, row_colors))

    def print_trade_summary(self) -> None:
        small_section(L(self.lang, "D) Trade triangle and angular work", "D) Handelsdreieck und Umlenkungsarbeit"), Ansi.BRIGHT_CYAN)
        self.explain_part("trade")
        trades = [tr for tr in self.trade_history if tr.tick == self.t]
        if not trades:
            print(wrap(L(self.lang,
                "No relevant triangle trade emerged in this tick. That can happen when exportability is low or angles are too far apart.",
                "In diesem Tick entstand kein nennenswerter Dreieckshandel. Das kann passieren, wenn Exportfähigkeit niedrig ist oder Winkel zu weit auseinanderliegen.")))
            return
        max_rows = 12 if self.detail != "full" else 30
        rows = []
        for tr in trades[:max_rows]:
            rows.append([
                tr.exporter + "→" + tr.importer,
                tr.sector,
                f"{tr.amount:.3f}",
                tr.currency,
                angle_label(tr.joint_hw),
                f"{tr.wk_deg:5.1f}°",
                f"{tr.angular_work:.3f} rad·VE",
            ])
        print(table(["Route", L(self.lang, "Sec", "Sek"), "Q", "C", "Jointθ", "WK°", "UA"], rows))
        total_ua = sum(tr.angular_work for tr in trades)
        total_amount = sum(tr.amount for tr in trades)
        print(wrap(L(self.lang,
            f"Trade sum: {total_amount:.3f} goods units; angular work sum: {total_ua:.3f} rad·VE. High UA means trade remains possible, but it needs more symbolic and institutional rotation.",
            f"Handelssumme: {total_amount:.3f} Gütereinheiten; Summe Umlenkungsarbeit: {total_ua:.3f} rad·VE. Hohe UA bedeutet: Handel bleibt möglich, benötigt aber mehr symbolische und institutionelle Drehung.")))

    def print_country_indices(self) -> None:
        small_section(L(self.lang, "E) Power, well-being and economic strength", "E) Macht, Wohlbefinden und Wirtschaftsstärke"), Ansi.BRIGHT_CYAN)
        self.explain_part("indices")
        rows = []
        colors = []
        for c in self.countries.values():
            dominant = max(c.last_currency_mix, key=lambda k: c.last_currency_mix[k]) if c.last_currency_mix else "-"
            eig = c.last_currency_mix.get(c.currency, 0.0) * 100.0
            rows.append([
                c.code,
                c.display_name(self.lang),
                gauge(c.wbi),
                gauge(c.mpi),
                gauge(c.wsk),
                tension_gauge(c.spg),
                f"{eig:5.1f}%",
                dominant,
                f"{sum(c.production.values()):.2f}",
                f"{sum(c.imports.values()):.2f}/{sum(c.exports.values()):.2f}",
            ])
            colors.append(c.color)
        print(table([L(self.lang, "Country", "Land"), L(self.lang, "Name", "Name"), "WBI", "MPI", "ES", "TD", "OwnS", "DomC", "Prod", "Imp/Exp"], rows, colors))

    def print_drift_and_events(self) -> None:
        small_section(L(self.lang, "F) Angle drift and event notes", "F) Winkeldrift und Ereignisnotizen"), Ansi.BRIGHT_CYAN)
        self.explain_part("drift")
        rows = []
        colors = []
        for cur in self.currencies.values():
            rows.append([
                cur.code,
                angle_label(cur.start_angle),
                angle_label(cur.angle),
                angle_label(cur.last_target),
                f"{angle_distance(cur.start_angle, cur.angle):5.1f}°",
                f"{cur.length:.3f} VE",
            ])
            colors.append(cur.color)
        print(table(["C", "Startθ", L(self.lang, "Nowθ", "Jetztθ"), L(self.lang, "Targetθ", "Zielθ"), "ΔStart", "|€⃗|"], rows, colors))
        any_note = False
        for c in self.countries.values():
            if c.notes:
                any_note = True
                print(col(c.code + ": ", c.color + Ansi.BOLD if COLOR_ON else "") + "; ".join(c.notes))
        if not any_note:
            print(L(self.lang,
                    "No strong event note. The angular economy is comparatively calm in this tick.",
                    "Keine starke Ereignisnotiz. Die Winkelwirtschaft läuft in diesem Tick vergleichsweise ruhig."))

    def print_final_report(self) -> None:
        section(L(self.lang, "FINAL REPORT", "ABSCHLUSSBERICHT"), Ansi.BRIGHT_MAGENTA)
        self.explain_part("final")
        print(wrap(L(self.lang,
            "The final report does not ask which country became richest. It asks which vector currency gained power attachment, where well-being stayed livable, and where economic strength was weakened by angular tension.",
            "Der Abschlussbericht fragt nicht, welches Land am reichsten wurde. Er fragt, welche Vektorwährung Machtbindung gewann, wo Wohlbefinden lebbar blieb und wo Wirtschaftsstärke durch Winkelspannung geschwächt wurde.")))
        rows = []
        colors = []
        for c in self.countries.values():
            hist = [r for r in self.history if r["country"] == c.code]
            wbi_values = [float(r["WBI"]) for r in hist]
            mpi_values = [float(r["MPI"]) for r in hist]
            es_values = [float(r["ES"]) for r in hist]
            td_values = [float(r["TD"]) for r in hist]
            rows.append([
                c.code,
                c.display_name(self.lang),
                f"{c.wbi:5.1f} {spark(wbi_values, 0, 100)}",
                f"{c.mpi:5.1f} {spark(mpi_values, 0, 100)}",
                f"{c.wsk:5.1f} {spark(es_values, 0, 100)}",
                f"{c.spg:5.1f} {spark(td_values, 0, 100)}",
                f"{c.last_currency_mix.get(c.currency, 0)*100:5.1f}%",
            ])
            colors.append(c.color)
        print(table([L(self.lang, "Country", "Land"), L(self.lang, "Name", "Name"), "WBI", "MPI", "ES", "TD", L(self.lang, "OwnS last", "OwnS zuletzt")], rows, colors))
        print()
        cur_rows = []
        cur_colors = []
        for cur in self.currencies.values():
            cur_rows.append([
                cur.code, cur.name(self.lang), cur.home,
                f"{cur.length:.3f} VE",
                angle_label(cur.angle),
                f"{cur.share*100:5.1f}%",
                f"{cur.power:5.1f}",
            ])
            cur_colors.append(cur.color)
        print(table([L(self.lang, "Currency", "Währung"), L(self.lang, "Name", "Name"), L(self.lang, "Home", "Heimat"), L(self.lang, "Length", "Länge"), "Endθ", "Share", "Power"], cur_rows, cur_colors))
        print()
        print(wrap(self._final_interpretation()))

    def _final_interpretation(self) -> str:
        best_wbi = max(self.countries.values(), key=lambda c: c.wbi)
        best_mpi = max(self.countries.values(), key=lambda c: c.mpi)
        high_td = max(self.countries.values(), key=lambda c: c.spg)
        top_cur = max(self.currencies.values(), key=lambda cur: cur.power)
        return L(self.lang,
            f"Interpretation of this run: {best_wbi.code} has the strongest final well-being, {best_mpi.code} has the strongest power index, and {high_td.code} carries the highest tension degree. The strongest currency by power attachment is {top_cur.code}. Because every currency length remains exactly 1 VE, these differences are not caused by one Euro being longer than another Euro. They are caused by angular fit, angular drift, and how much market action each vector direction captures.",
            f"Interpretation dieses Laufs: {best_wbi.code} hat das stärkste End-Wohlbefinden, {best_mpi.code} den stärksten Machtindex, und {high_td.code} trägt den höchsten Spannungsgrad. Die stärkste Währung nach Machtbindung ist {top_cur.code}. Weil jede Währungslänge exakt 1 VE bleibt, entstehen diese Unterschiede nicht dadurch, dass ein Euro länger wäre als ein anderer Euro. Sie entstehen durch Winkelpassung, Winkeldrift und dadurch, wie viel Markthandlung jede Vektorrichtung bindet.")

    # ------------------------------------------------------------------
    # UTF-8 art gallery
    # ------------------------------------------------------------------

    def print_utf8_gallery(self) -> None:
        section(L(self.lang, "UTF-8 ART GALLERY OF THE ANGULAR ECONOMY", "UTF-8-ART-GALERIE DER WINKELWIRTSCHAFT"), Ansi.BRIGHT_MAGENTA)
        print(wrap(L(self.lang,
            "The gallery comes after the numerical report. It turns the same final state into colorful UTF-8 diagrams: circles, vectors, angle carpets, trade arrows and scenario maps. Each picture has a result summary underneath, including how the same picture should be read under different scenarios.",
            "Die Galerie kommt nach dem Zahlenbericht. Sie verwandelt denselben Endzustand in bunte UTF-8-Diagramme: Kreise, Vektoren, Winkelteppiche, Handelspfeile und Szenariokarten. Unter jedem Bild steht eine Ergebniszusammenfassung, inklusive Lesart für verschiedene Szenarien.")))
        scenario_rows = self._scenario_comparison() if self.compare_scenarios else []
        self.art_currency_compass(scenario_rows)
        self.art_equal_length_proof(scenario_rows)
        self.art_orthogonal_axes(scenario_rows)
        self.art_three_market_vectors(scenario_rows)
        self.art_power_wellbeing_map(scenario_rows)
        self.art_tension_heat_carpet(scenario_rows)
        self.art_trade_triangle(scenario_rows)
        self.art_currency_drift_trails(scenario_rows)
        self.art_sector_satisfaction_mosaic(scenario_rows)
        self.art_price_wave(scenario_rows)
        self.art_scenario_quadrants(scenario_rows)
        self.art_scenario_comparison_table(scenario_rows)

    def gallery_caption(self, no: int, title_en: str, title_de: str) -> None:
        print()
        print(col("╔" + "═" * (WRAP_WIDTH - 2) + "╗", Ansi.BRIGHT_MAGENTA))
        title = f"{no:02d}. " + L(self.lang, title_en, title_de)
        inside = "║ " + title + " " * max(0, WRAP_WIDTH - len(strip_ansi(title)) - 3) + "║"
        print(col(inside, Ansi.BRIGHT_MAGENTA + Ansi.BOLD if COLOR_ON else ""))
        print(col("╚" + "═" * (WRAP_WIDTH - 2) + "╝", Ansi.BRIGHT_MAGENTA))

    def _scenario_comparison(self) -> List[Dict[str, object]]:
        rows = []
        if not self.compare_scenarios:
            return rows
        # Keep scenario comparison silent and deterministic. Use the same tick count so that outputs are comparable.
        old_color = COLOR_ON
        old_width = WRAP_WIDTH
        for i, sc in enumerate(SCENARIOS):
            sim = AngularEconomy(seed=self.seed + 1000 + i * 31, ticks=self.max_ticks,
                                 detail="short", report_every=self.max_ticks, width=max(72, old_width),
                                 colors=False, explanations=False, lang=self.lang,
                                 scenario=sc, gallery=False, compare_scenarios=False,
                                 selected_country_ids=self.selected_eu_codes)
            sim.simulate_silent()
            avg_wbi = sum(c.wbi for c in sim.countries.values()) / 3.0
            avg_mpi = sum(c.mpi for c in sim.countries.values()) / 3.0
            avg_es = sum(c.wsk for c in sim.countries.values()) / 3.0
            avg_td = sum(c.spg for c in sim.countries.values()) / 3.0
            total_ua = sum(tr.angular_work for tr in sim.trade_history)
            top_cur = max(sim.currencies.values(), key=lambda cur: cur.power).code
            rows.append({"scenario": sc, "WBI": avg_wbi, "MPI": avg_mpi, "ES": avg_es,
                         "TD": avg_td, "UA": total_ua, "top": top_cur})
        # Restore terminal settings of the main simulation.
        globals()["COLOR_ON"] = old_color
        globals()["WRAP_WIDTH"] = old_width
        return rows

    def scenario_sentence(self, scenario_rows: List[Dict[str, object]], focus: str) -> str:
        lang = self.lang
        if not scenario_rows:
            return L(lang,
                "Scenario comparison was disabled, so the reading below refers only to the active run.",
                "Der Szenariovergleich wurde deaktiviert; die folgende Lesart bezieht sich nur auf den aktiven Lauf.")
        best_wbi = max(scenario_rows, key=lambda r: r["WBI"])
        best_mpi = max(scenario_rows, key=lambda r: r["MPI"])
        lowest_td = min(scenario_rows, key=lambda r: r["TD"])
        highest_td = max(scenario_rows, key=lambda r: r["TD"])
        vals = {
            "focus": focus,
            "wbi": scenario_label(str(best_wbi["scenario"]), lang),
            "mpi": scenario_label(str(best_mpi["scenario"]), lang),
            "low": scenario_label(str(lowest_td["scenario"]), lang),
            "high": scenario_label(str(highest_td["scenario"]), lang),
        }
        templates = {
            "en": "Scenario reading for {focus}: in the silent comparison, {wbi} has the highest average WBI, {mpi} has the highest average MPI, {low} has the calmest angle field, and {high} has the hardest tension field. Use this picture as a diagnostic: resonance shrinks visual conflict; power pulls vectors toward state currency; scarcity or fragmentation thickens red/yellow tension signs.",
            "de": "Szenario-Lesart für {focus}: Im stillen Vergleich hat {wbi} das höchste durchschnittliche WBI, {mpi} das höchste durchschnittliche MPI, {low} das ruhigste Winkelfeld, und {high} das härteste Spannungsfeld. Nutze dieses Bild als Diagnose: Resonanz verkleinert sichtbare Konflikte; Macht zieht Vektoren zur Staatswährung; Mangel oder Zersplitterung verdicken rote/gelbe Spannungszeichen.",
            "ru": "Сценарное чтение для {focus}: в тихом сравнении {wbi} даёт самый высокий средний WBI, {mpi} — самый высокий средний MPI, {low} — самое спокойное угловое поле, а {high} — самое жёсткое поле напряжения. Диагноз: резонанс сжимает видимый конфликт; власть тянет векторы к государственной валюте; дефицит или дробление усиливают жёлто-красные знаки напряжения.",
            "es": "Lectura de escenario para {focus}: en la comparación silenciosa, {wbi} tiene el WBI medio más alto, {mpi} el MPI medio más alto, {low} el campo angular más tranquilo y {high} el campo de tensión más duro. Diagnóstico: la resonancia reduce conflicto visible; el poder tira vectores hacia la moneda estatal; escasez o fragmentación engrosan señales amarillas/rojas de tensión.",
            "it": "Lettura di scenario per {focus}: nel confronto silenzioso, {wbi} ha il WBI medio più alto, {mpi} ha il MPI medio più alto, {low} ha il campo angolare più calmo e {high} il campo di tensione più duro. Diagnosi: la risonanza riduce il conflitto visibile; il potere tira i vettori verso la valuta statale; scarsità o frammentazione rafforzano i segni gialli/rossi di tensione.",
            "zh": "{focus} 的情景解读：在静默比较中，{wbi} 的平均 WBI 最高，{mpi} 的平均 MPI 最高，{low} 的角度场最平静，{high} 的紧张场最强。诊断：共振减少可见冲突；权力把向量拉向国家货币；稀缺或碎片化会加厚黄/红紧张符号。",
            "ja": "{focus} のシナリオ読解：静かな比較では、{wbi} が平均 WBI 最高、{mpi} が平均 MPI 最高、{low} が最も穏やかな角度場、{high} が最も強い緊張場です。診断：共鳴は見える対立を縮め、権力はベクトルを国家通貨へ引き、希少性や分断は黄/赤の緊張記号を太くします。",
            "ko": "{focus} 시나리오 읽기: 조용한 비교에서 {wbi}는 평균 WBI가 가장 높고, {mpi}는 평균 MPI가 가장 높으며, {low}는 가장 차분한 각도장, {high}는 가장 강한 긴장장입니다. 진단: 공명은 보이는 갈등을 줄이고, 권력은 벡터를 국가 통화로 당기며, 희소성이나 분절은 노랑/빨강 긴장 신호를 두껍게 합니다.",
            "hi": "{focus} के लिए परिदृश्य-पठन: मौन तुलना में {wbi} का औसत WBI सबसे ऊँचा है, {mpi} का औसत MPI सबसे ऊँचा है, {low} का कोणीय क्षेत्र सबसे शांत है और {high} का तनाव क्षेत्र सबसे कठोर है। निदान: अनुनाद दृश्य संघर्ष घटाता है; शक्ति वेक्टरों को राज्य मुद्रा की ओर खींचती है; कमी या विखंडन पीले/लाल तनाव चिह्न बढ़ाते हैं।",
            "he": "קריאת תרחיש עבור {focus}: בהשוואה השקטה, ל-{wbi} יש WBI ממוצע הגבוה ביותר, ל-{mpi} יש MPI ממוצע הגבוה ביותר, {low} הוא שדה הזוויות השקט ביותר ו-{high} הוא שדה המתח הקשה ביותר. אבחון: תהודה מצמצמת קונפליקט נראה; עוצמה מושכת וקטורים למטבע המדינה; מחסור או פיצול מעבים סימני מתח צהובים/אדומים.",
            "fa": "خوانش سناریو برای {focus}: در مقایسه خاموش، {wbi} بالاترین WBI میانگین را دارد، {mpi} بالاترین MPI میانگین را دارد، {low} آرام‌ترین میدان زاویه‌ای است و {high} سخت‌ترین میدان تنش را دارد. تشخیص: تشدید تعارض دیداری را کم می‌کند؛ قدرت بردارها را به ارز دولت می‌کشد؛ کمبود یا چندپارگی نشانه‌های زرد/قرمز تنش را ضخیم می‌کند.",
            "ar": "قراءة السيناريو لـ {focus}: في المقارنة الصامتة، يملك {wbi} أعلى متوسط WBI، ويملك {mpi} أعلى متوسط MPI، و{low} أهدأ حقل زاوي، و{high} أقسى حقل توتر. التشخيص: الرنين يقلل الصراع المرئي؛ القوة تسحب المتجهات نحو عملة الدولة؛ الندرة أو التجزؤ يثخنان علامات التوتر الصفراء/الحمراء.",
        }
        return templates.get(lang, templates["en"]).format(**vals)

    def art_currency_compass(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(1, "Currency compass: three equal-length Euro vectors", "Währungskompass: drei gleich lange Euro-Vektoren")
        points = []
        for cur in self.currencies.values():
            label = f"{cur.code} |€⃗|=1"
            points.append((cur.angle, label, cur.color, angle_arrow(cur.angle)))
        print(compass_canvas(points, title=L(self.lang, "Final currency directions", "Endrichtungen der Währungen")))
        print(wrap(L(self.lang,
            "Result: the picture shows only direction, not monetary length. EA, EB and EC are drawn as different colored arrows because their angles differ; they are not drawn with different radii because their vector length is fixed at 1 VE. The winner of a transaction is therefore the vector whose direction best resonates with the action angle, not the vector with a longer Euro.",
            "Ergebnis: Das Bild zeigt nur Richtung, nicht Geldlänge. EA, EB und EC erscheinen als verschiedenfarbige Pfeile, weil ihre Winkel verschieden sind; sie erscheinen nicht mit unterschiedlichen Radien, weil ihre Vektorlänge fest bei 1 VE liegt. Eine Transaktion gewinnt also die Währung, deren Richtung am besten mit dem Handlungswinkel klingt, nicht die Währung mit einem längeren Euro.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "the currency compass", "den Währungskompass"))))

    def art_equal_length_proof(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(2, "Equal vector-length proof: price is count, not stretch", "Gleichlängenbeweis: Preis ist Anzahl, nicht Streckung")
        print(col("┌" + "─" * 72 + "┐", Ansi.BRIGHT_CYAN))
        for cur in self.currencies.values():
            bar = col("████████████████████", cur.color)
            print(col("│ ", Ansi.BRIGHT_CYAN) + f"{cur.code} {bar} |€⃗| = {cur.length:.3f} VE    θ={cur.angle:6.1f}°" + " " * 6 + col("│", Ansi.BRIGHT_CYAN))
        print(col("└" + "─" * 72 + "┘", Ansi.BRIGHT_CYAN))
        price_samples = []
        for c in self.countries.values():
            sec = max(self.sectors, key=lambda s: c.prices[s.code])
            price_samples.append([c.code, sec.code, sec.name(self.lang), f"{c.prices[sec.code]:.2f} VE/unit"])
        print(table([L(self.lang, "Country", "Land"), L(self.lang, "Sec", "Sek"), L(self.lang, "Sector", "Sektor"), L(self.lang, "Highest price", "Höchster Preis")], price_samples))
        print(wrap(L(self.lang,
            "Result: all three bars have identical length. The price table below the bars shows a different idea: high prices mean that more equal-length vector-Euro units are counted for a good. The price does not mean that EA, EB or EC has become longer. In scarcity scenarios the count usually rises; in resonance scenarios the count often falls because less angular detour is needed.",
            "Ergebnis: Alle drei Balken haben identische Länge. Die Preistabelle darunter zeigt eine andere Idee: Hohe Preise bedeuten, dass mehr gleich lange Vektor-Euro-Einheiten für ein Gut gezählt werden. Der Preis bedeutet nicht, dass EA, EB oder EC länger geworden wäre. In Mangelszenarien steigt diese Anzahl meist; in Resonanzszenarien fällt sie oft, weil weniger Winkelumweg nötig ist.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "equal vector length", "gleiche Vektorlänge"))))

    def _most_orthogonal_pressure(self) -> Tuple[Country, Sector, str, AngleState]:
        best = None
        best_score = -1.0
        for c in self.countries.values():
            for sec in self.sectors:
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    score = st.orth_error() + 55.0 * gegenklang(st.last_hw if st.last_hw else st.action_angle(), self.currencies[c.currency].angle)
                    if score > best_score:
                        best_score = score
                        best = (c, sec, action, st)
        return best  # type: ignore

    def art_orthogonal_axes(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(3, "Government good/evil axis and population popular/unpopular axis", "Regierungsachse Gut/Böse und Bevölkerungsachse Beliebt/Unbeliebt")
        c, sec, action, st = self._most_orthogonal_pressure()
        hw = st.last_hw if st.last_hw else st.action_angle()
        points = [
            (st.gbw, "GOOD/GT", Ansi.BRIGHT_GREEN, "G"),
            (st.gbw + 180, "EVIL/BÖ", Ansi.BRIGHT_RED, "E"),
            (st.buw, "POPULAR/BEL", Ansi.BRIGHT_CYAN, "P"),
            (st.buw + 180, "UNPOPULAR/UNB", Ansi.BRIGHT_MAGENTA, "U"),
            (hw, "ACTION/HW", Ansi.BRIGHT_YELLOW, "◆"),
        ]
        print(compass_canvas(points, title=f"{c.code} {sec.code} {action_label(action, self.lang)}"))
        print(wrap(L(self.lang,
            f"Result: this is the strongest axis-pressure example found in the final state: {c.code}, sector {sec.name(self.lang)}, {action_label(action, self.lang)}. GBW° points to the government good pole; GBW°+180° is the evil pole. BUW° points to the population popular pole; BUW°+180° is the unpopular pole. The action angle lies between the axes. ODE here is {st.orth_error():.1f}°, so the popular/unpopular axis is that far away from ideal orthogonality.",
            f"Ergebnis: Dies ist das stärkste Achsendruck-Beispiel im Endzustand: {c.code}, Sektor {sec.name(self.lang)}, {action_label(action, self.lang)}. GBW° zeigt zum Gut-Pol der Regierung; GBW°+180° ist der Böse-Pol. BUW° zeigt zum Beliebt-Pol der Bevölkerung; BUW°+180° ist der Unbeliebt-Pol. Der Handlungswinkel liegt zwischen den Achsen. Die ODE beträgt hier {st.orth_error():.1f}°, also ist die Beliebt/Unbeliebt-Achse so weit von idealer Orthogonalität entfernt.")))
        print(wrap(L(self.lang,
            "Scenario meaning: resonance keeps the cyan popular axis close to a clean 90° relation with the green good axis; power pursuit often pulls the yellow action toward the government/currency side; well-being pursuit pulls action toward the popular side; fragmented angles scatter all poles and create high tension even when the Euro-vector length is unchanged.",
            "Szenario-Bedeutung: Resonanz hält die türkise Beliebt-Achse nahe an einer sauberen 90°-Beziehung zur grünen Gut-Achse; Machtstreben zieht die gelbe Handlung oft zur Regierungs-/Währungsseite; Wohlbefinden zieht Handlung zur Beliebt-Seite; zersplitterte Winkel streuen alle Pole und erzeugen hohe Spannung, obwohl die Euro-Vektorlänge unverändert bleibt.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "orthogonal axes", "orthogonale Achsen"))))

    def art_three_market_vectors(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(4, "Three market vectors: buy, sell and labor", "Drei Marktvektoren: Kauf, Verkauf und Arbeit")
        # Choose country/sector with lowest satisfaction for diagnostic value.
        c = max(self.countries.values(), key=lambda x: x.spg)
        sec = min(self.sectors, key=lambda s: c.satisfaction[s.code])
        points = []
        colors = {"BUY": Ansi.BRIGHT_GREEN, "SELL": Ansi.BRIGHT_BLUE, "WORK": Ansi.BRIGHT_MAGENTA}
        labels_short = {"BUY": "BUY/K", "SELL": "SELL/V", "WORK": "WORK/A"}
        for action in ACTIONS:
            st = c.angles[(action, sec.code)]
            hw = st.last_hw if st.last_hw else st.action_angle()
            points.append((hw, f"{labels_short[action]} {st.last_currency}", colors[action], "◆"))
        print(compass_canvas(points, title=f"{c.code} {sec.name(self.lang)}"))
        print(wrap(L(self.lang,
            f"Result: the three market actions in {c.code}/{sec.name(self.lang)} do not have to point in the same direction. Buy, sell and labor can use different dominant currencies because each action has its own angle. In the shown final state, need satisfaction in this sector is {c.satisfaction[sec.code]*100:.1f}% and the price is {c.prices[sec.code]:.2f} VE per unit. A weak sector is therefore not simply 'poor'; it can be angularly split between buying, selling and working.",
            f"Ergebnis: Die drei Markthandlungen in {c.code}/{sec.name(self.lang)} müssen nicht in dieselbe Richtung zeigen. Kauf, Verkauf und Arbeit können unterschiedliche dominante Währungen nutzen, weil jede Handlung ihren eigenen Winkel hat. Im gezeigten Endzustand beträgt die Bedarfsdeckung dieses Sektors {c.satisfaction[sec.code]*100:.1f}% und der Preis {c.prices[sec.code]:.2f} VE pro Einheit. Ein schwacher Sektor ist deshalb nicht einfach 'arm'; er kann winkelmäßig zwischen Kaufen, Verkaufen und Arbeiten gespalten sein.")))
        print(wrap(L(self.lang,
            "Scenario meaning: in resonance, the three diamonds cluster and the sector feels coherent; in power pursuit, the work vector may be forced near the state-currency orbit while buy demand remains elsewhere; in scarcity, buy vectors become expensive because need and supply collide; in trade boom, sell vectors become more important and can pull the sector toward export currencies.",
            "Szenario-Bedeutung: In Resonanz clustern die drei Rauten und der Sektor wirkt kohärent; im Machtstreben kann der Arbeitsvektor nahe an die Staatswährung gezogen werden, während Kaufbedarf woanders bleibt; im Mangel werden Kaufvektoren teuer, weil Bedarf und Versorgung kollidieren; im Handelsboom werden Verkaufsvektoren wichtiger und können den Sektor zu Exportwährungen ziehen.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "the three market vectors", "die drei Marktvektoren"))))

    def art_power_wellbeing_map(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(5, "Power versus well-being map", "Macht-gegen-Wohlbefinden-Karte")
        w, h = 64, 22
        canvas = Canvas(w, h)
        x0, y0 = 8, h - 4
        x1, y1 = w - 4, 2
        # Axes
        for x in range(x0, x1 + 1):
            canvas.put(x, y0, "─", Ansi.DIM)
        for y in range(y1, y0 + 1):
            canvas.put(x0, y, "│", Ansi.DIM)
        canvas.put(x0, y0, "└", Ansi.WHITE)
        canvas.put_text(x0 + 2, y0 + 1, "WBI →", Ansi.BRIGHT_GREEN)
        canvas.put_text(1, y1 - 1, "MPI ↑", Ansi.BRIGHT_BLUE)
        # Quadrant labels
        canvas.put_text(x0 + 2, y1 + 1, L(self.lang, "power", "Macht"), Ansi.BRIGHT_BLUE)
        canvas.put_text(x1 - 18, y1 + 1, L(self.lang, "resonance", "Resonanz"), Ansi.BRIGHT_GREEN)
        canvas.put_text(x0 + 2, y0 - 2, L(self.lang, "weak", "schwach"), Ansi.BRIGHT_RED)
        canvas.put_text(x1 - 22, y0 - 2, L(self.lang, "well-being", "Wohlbefinden"), Ansi.BRIGHT_CYAN)
        for c in self.countries.values():
            x = int(round(x0 + (x1 - x0) * clamp(c.wbi / 100.0, 0, 1)))
            y = int(round(y0 - (y0 - y1) * clamp(c.mpi / 100.0, 0, 1)))
            canvas.put(x, y, "●", c.color + Ansi.BOLD if COLOR_ON else "")
            canvas.put_text(min(w - 5, x + 2), y, c.code, c.color + Ansi.BOLD if COLOR_ON else "")
        print(canvas.render())
        print(wrap(L(self.lang,
            "Result: this diagram separates the two main goals. Moving right means higher well-being; moving upward means stronger power attachment. A country in the upper right is not necessarily rich; it is coherent in both goal dimensions. Upper left means power without enough well-being. Lower right means livable society with weak state/currency power. Lower left means weak coherence in both dimensions.",
            "Ergebnis: Dieses Diagramm trennt die zwei Hauptziele. Nach rechts bedeutet mehr Wohlbefinden; nach oben bedeutet stärkere Machtbindung. Ein Land rechts oben ist nicht unbedingt reich; es ist in beiden Zielrichtungen kohärent. Links oben bedeutet Macht ohne genug Wohlbefinden. Rechts unten bedeutet lebbares Gemeinwesen mit schwacher Staats-/Währungsmacht. Links unten bedeutet schwachen Zusammenhalt in beiden Dimensionen.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "power versus well-being", "Macht gegen Wohlbefinden"))))

    def art_tension_heat_carpet(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(6, "Tension heat carpet through time", "Spannungs-Heatcarpet über die Zeit")
        print(col(L(self.lang, "Legend: green low TD, yellow medium TD, red high TD", "Legende: Grün niedrige TD, Gelb mittlere TD, Rot hohe TD"), Ansi.BOLD))
        rows = []
        for c in self.countries.values():
            vals = [float(r["TD"]) for r in self.history if r["country"] == c.code]
            carpet = "".join(heat_block(v, 0, 100) for v in vals)
            rows.append([col(c.code, c.color + Ansi.BOLD if COLOR_ON else ""), carpet, f"last {c.spg:.1f}"])
        print(table([L(self.lang, "Country", "Land"), L(self.lang, "TD over ticks", "TD über Ticks"), L(self.lang, "Final", "Final")], rows))
        print(wrap(L(self.lang,
            "Result: the carpet shows whether tension is episodic or structural. A few yellow/red blocks mean temporary angular friction. A long red band means persistent mismatch between government good/evil axes, population popular/unpopular axes, currency directions and market actions. This directly weakens economic strength in the model.",
            "Ergebnis: Der Teppich zeigt, ob Spannung episodisch oder strukturell ist. Einzelne gelbe/rote Blöcke bedeuten vorübergehende Winkelreibung. Ein langes rotes Band bedeutet dauerhafte Fehlpassung zwischen Gut/Böse-Achsen der Regierung, Beliebt/Unbeliebt-Achsen der Bevölkerung, Währungsrichtungen und Markthandlungen. Das schwächt im Modell direkt die Wirtschaftsstärke.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "the tension carpet", "den Spannungsteppich"))))

    def art_trade_triangle(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(7, "Trade triangle: goods move, vectors rotate", "Handelsdreieck: Güter bewegen sich, Vektoren drehen")
        # Aggregate flows by route.
        flows: Dict[Tuple[str, str], float] = {}
        uas: Dict[Tuple[str, str], float] = {}
        for tr in self.trade_history:
            key = (tr.exporter, tr.importer)
            flows[key] = flows.get(key, 0.0) + tr.amount
            uas[key] = uas.get(key, 0.0) + tr.angular_work
        def arrow(a: str, b: str) -> str:
            q = flows.get((a, b), 0.0)
            ua = uas.get((a, b), 0.0)
            n = int(clamp(q * 5.0, 1, 12)) if q > 0 else 1
            color = Ansi.BRIGHT_GREEN if ua < 1.5 else (Ansi.BRIGHT_YELLOW if ua < 4.0 else Ansi.BRIGHT_RED)
            return col("═" * n + "▶", color) + f" {q:.2f}/{ua:.2f}UA"
        codes = list(self.countries.keys())
        top, left, right = codes[0], codes[1], codes[2]
        def label(code: str, prefix: str = "", suffix: str = "") -> str:
            return col(prefix + code + suffix, self.countries[code].color + Ansi.BOLD if COLOR_ON else "")
        print("\n" + " " * 29 + label(top, "▲ "))
        print(" " * 24 + "╱" + " " * 12 + "╲")
        print(" " * 18 + arrow(left, top) + " " * 6 + arrow(top, right))
        print(" " * 16 + "╱" + " " * 28 + "╲")
        print(label(left, "", " ◀") + " " * 16 + arrow(left, right) + " " * 9 + label(right, "▶ "))
        print(" " * 16 + "╲" + " " * 28 + "╱")
        print(" " * 18 + arrow(top, left) + " " * 6 + arrow(right, top))
        print(" " * 24 + "╲" + " " * 12 + "╱")
        print(" " * 29 + arrow(right, left))
        print(wrap(L(self.lang,
            "Result: each arrow lists quantity/angular work. The first number is traded goods quantity; the second is UA, the angular work in rad·VE. A route can have a modest goods flow but high angular work when the trade currency is far from the exporter's home vector. That route is politically and symbolically expensive even though every Euro-vector still has length 1.",
            "Ergebnis: Jeder Pfeil zeigt Menge/Umlenkungsarbeit. Die erste Zahl ist gehandelte Gütermenge; die zweite ist UA, die Umlenkungsarbeit in rad·VE. Eine Route kann geringe Gütermenge, aber hohe Umlenkungsarbeit haben, wenn die Handelswährung weit von der Heimatwährung des Exporteurs entfernt ist. Diese Route ist politisch und symbolisch teuer, obwohl jeder Euro-Vektor weiterhin Länge 1 hat.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "the trade triangle", "das Handelsdreieck"))))

    def art_currency_drift_trails(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(8, "Currency drift trails", "Währungsdrift-Spuren")
        points = []
        # Draw final arrows plus small trail points from history.
        for cur in self.currencies.values():
            points.append((cur.angle, f"{cur.code} now", cur.color, angle_arrow(cur.angle)))
        print(compass_canvas(points, title=L(self.lang, "Final arrows; trails listed below", "Endpfeile; Spuren darunter")))
        trail_rows = []
        for cur in self.currencies.values():
            vals = [float(r[f"{cur.code}_angle"]) for r in self.currency_history]
            # Create a compact symbolic drift line: arrow char by angle per tick.
            trail = "".join(col(angle_arrow(v), cur.color) for v in vals)
            trail_rows.append([cur.code, angle_label(cur.start_angle), angle_label(cur.angle), f"{angle_distance(cur.start_angle, cur.angle):.1f}°", trail])
        print(table(["C", "Startθ", "Endθ", "Δ", L(self.lang, "trail", "Spur")], trail_rows))
        print(wrap(L(self.lang,
            "Result: the trail is a history of direction changes, not of monetary length changes. A stable trail means the currency kept its angle identity. A turning trail means market action and government attachment pulled it into a new orbit. In power scenarios drift can be strategic; in well-being scenarios it can follow livable demand; in fragmented scenarios it can become unstable zigzagging.",
            "Ergebnis: Die Spur ist ein Verlauf der Richtungsänderungen, nicht der Geldlängenänderungen. Eine stabile Spur bedeutet, dass die Währung ihre Winkelidentität hält. Eine drehende Spur bedeutet, dass Markthandlung und Regierungsbindung sie in einen neuen Orbit gezogen haben. In Machtszenarien kann Drift strategisch sein; in Wohlbefindensszenarien folgt sie lebbarer Nachfrage; in zersplitterten Szenarien kann sie instabiles Zickzack werden.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "currency drift", "Währungsdrift"))))

    def art_sector_satisfaction_mosaic(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(9, "Sector satisfaction mosaic", "Sektor-Deckungs-Mosaik")
        headers = [L(self.lang, "Country", "Land")] + [s.code for s in self.sectors]
        rows = []
        for c in self.countries.values():
            row = [col(c.code, c.color + Ansi.BOLD if COLOR_ON else "")]
            for s in self.sectors:
                sat = c.satisfaction[s.code]
                if sat >= 0.95:
                    cell = col("██", Ansi.BRIGHT_GREEN)
                elif sat >= 0.75:
                    cell = col("▓▓", Ansi.BRIGHT_YELLOW)
                elif sat >= 0.55:
                    cell = col("▒▒", Ansi.YELLOW)
                else:
                    cell = col("░░", Ansi.BRIGHT_RED)
                row.append(cell + f" {sat*100:4.0f}%")
            rows.append(row)
        print(table(headers, rows))
        print(wrap(L(self.lang,
            "Result: the mosaic translates final need coverage into blocks. Green blocks mean that a sector is materially covered and angularly usable enough. Red blocks mean missing coverage, usually from low production, weak trade access, expensive vector count or mismatch between buy/sell/work angles. This is where economic strength weakens even without treating money as wealth maximization.",
            "Ergebnis: Das Mosaik übersetzt finale Bedarfsdeckung in Blöcke. Grüne Blöcke bedeuten, dass ein Sektor materiell gedeckt und winkelmäßig nutzbar genug ist. Rote Blöcke bedeuten fehlende Deckung, meist durch niedrige Produktion, schwachen Handelszugang, teure Vektoranzahl oder Fehlpassung zwischen Kauf-/Verkaufs-/Arbeitswinkeln. Hier wird Wirtschaftsstärke schwach, ohne Geld als Reichtumsmaximierung zu behandeln.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "sector satisfaction", "Sektordeckung"))))

    def art_price_wave(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(10, "Vector-Euro price waves", "Vektor-Euro-Preiswellen")
        for c in self.countries.values():
            vals = [c.prices[s.code] for s in self.sectors]
            lo, hi = min(vals), max(vals)
            wave = spark(vals, lo, hi)
            colored = "".join(col(ch, c.color) for ch in wave)
            labels = " ".join(s.code for s in self.sectors)
            print(col(c.code + " ", c.color + Ansi.BOLD if COLOR_ON else "") + colored + "   " + labels + f"   min={lo:.2f} max={hi:.2f} VE")
        print(wrap(L(self.lang,
            "Result: each wave is the final vector-Euro count per unit across sectors. Peaks are not longer Euros. They are places where more equal-length vector units are required because scarcity, angular mismatch, or local currency distance adds friction. In resonance scenarios waves flatten; in scarcity scenarios they rise; in trade-boom scenarios exportable sectors can either flatten through imports or spike through angular work.",
            "Ergebnis: Jede Welle ist die finale Vektor-Euro-Anzahl pro Einheit über die Sektoren. Spitzen sind keine längeren Euros. Sie sind Stellen, an denen mehr gleich lange Vektoreinheiten gebraucht werden, weil Mangel, Winkel-Fehlpassung oder Distanz zur lokalen Währung Reibung erzeugt. In Resonanzszenarien glätten sich Wellen; in Mangelszenarien steigen sie; in Handelsboom-Szenarien können exportierbare Sektoren durch Importe glatter werden oder durch Umlenkungsarbeit ausschlagen.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "price waves", "Preiswellen"))))

    def art_scenario_quadrants(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(11, "Scenario quadrants: how to classify the economy", "Szenario-Quadranten: wie die Wirtschaft einzuordnen ist")
        quadrants = {
            "resonance": [],
            "power_lock": [],
            "wellbeing_island": [],
            "fracture": [],
        }
        for c in self.countries.values():
            if c.wbi >= 60 and c.mpi >= 55 and c.spg < 50:
                quadrants["resonance"].append(c.code)
            elif c.mpi >= c.wbi + 8:
                quadrants["power_lock"].append(c.code)
            elif c.wbi >= c.mpi + 8:
                quadrants["wellbeing_island"].append(c.code)
            else:
                quadrants["fracture"].append(c.code)
        box_w = 30
        print(col("┌" + "─" * box_w + "┬" + "─" * box_w + "┐", Ansi.BRIGHT_CYAN))
        print(col("│", Ansi.BRIGHT_CYAN) + L(self.lang, " POWER LOCK ", " MACHTKLEMME ").center(box_w) + col("│", Ansi.BRIGHT_CYAN) + L(self.lang, " RESONANCE ", " RESONANZ ").center(box_w) + col("│", Ansi.BRIGHT_CYAN))
        print(col("│", Ansi.BRIGHT_CYAN) + (", ".join(quadrants["power_lock"]) or "—").center(box_w) + col("│", Ansi.BRIGHT_CYAN) + (", ".join(quadrants["resonance"]) or "—").center(box_w) + col("│", Ansi.BRIGHT_CYAN))
        print(col("├" + "─" * box_w + "┼" + "─" * box_w + "┤", Ansi.BRIGHT_CYAN))
        print(col("│", Ansi.BRIGHT_CYAN) + L(self.lang, " FRACTURE ", " BRUCH ").center(box_w) + col("│", Ansi.BRIGHT_CYAN) + L(self.lang, " WELL-BEING ISLAND ", " WOHLBEFINDENSINSEL ").center(box_w) + col("│", Ansi.BRIGHT_CYAN))
        print(col("│", Ansi.BRIGHT_CYAN) + (", ".join(quadrants["fracture"]) or "—").center(box_w) + col("│", Ansi.BRIGHT_CYAN) + (", ".join(quadrants["wellbeing_island"]) or "—").center(box_w) + col("│", Ansi.BRIGHT_CYAN))
        print(col("└" + "─" * box_w + "┴" + "─" * box_w + "┘", Ansi.BRIGHT_CYAN))
        print(wrap(L(self.lang,
            "Result: the quadrant picture gives a political-economic reading. Resonance means power and well-being can coexist with tolerable tension. Power lock means the state/currency side dominates over lived well-being. Well-being island means people live better than the state currency dominates. Fracture means the angles do not yet form a stable goal shape.",
            "Ergebnis: Das Quadrantenbild gibt eine politisch-ökonomische Lesart. Resonanz bedeutet, dass Macht und Wohlbefinden bei tragbarer Spannung zusammengehen. Machtklemme bedeutet, dass Staats-/Währungsseite über gelebtem Wohlbefinden dominiert. Wohlbefindensinsel bedeutet, dass Menschen besser leben, als die Staatswährung dominiert. Bruch bedeutet, dass die Winkel noch keine stabile Zielform bilden.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "scenario quadrants", "Szenario-Quadranten"))))

    def art_scenario_comparison_table(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(12, "Silent scenario comparison", "Stiller Szenariovergleich")
        if not scenario_rows:
            print(L(self.lang, "Scenario comparison disabled.", "Szenariovergleich deaktiviert."))
            return
        rows = []
        colors = []
        for r in scenario_rows:
            label = scenario_label(str(r["scenario"]), self.lang)
            rows.append([
                label,
                f"{float(r['WBI']):5.1f}",
                f"{float(r['MPI']):5.1f}",
                f"{float(r['ES']):5.1f}",
                f"{float(r['TD']):5.1f}",
                f"{float(r['UA']):7.2f}",
                str(r["top"]),
            ])
            if str(r["scenario"]) == "resonance":
                colors.append(Ansi.BRIGHT_GREEN)
            elif str(r["scenario"]) in ("fragmented", "scarcity"):
                colors.append(Ansi.BRIGHT_RED)
            elif str(r["scenario"]) == "power":
                colors.append(Ansi.BRIGHT_BLUE)
            else:
                colors.append(Ansi.BRIGHT_CYAN)
        print(table([L(self.lang, "Scenario", "Szenario"), "Avg WBI", "Avg MPI", "Avg ES", "Avg TD", "Total UA", "Top C"], rows, colors))
        print(wrap(L(self.lang,
            "Result: this final table actually runs the model silently under several scenarios using the same structural rules. It is not a moral ranking. It shows which parameter climate produces more well-being, more power, more strength or more tension. Since all scenarios keep |€⃗|=1 VE for EA, EB and EC, differences across rows are angle-system differences, not Euro-length differences.",
            "Ergebnis: Diese letzte Tabelle lässt das Modell tatsächlich still unter mehreren Szenarien laufen, mit denselben Strukturregeln. Sie ist keine moralische Rangliste. Sie zeigt, welches Parameterklima mehr Wohlbefinden, mehr Macht, mehr Stärke oder mehr Spannung erzeugt. Da alle Szenarien |€⃗|=1 VE für EA, EB und EC beibehalten, sind Unterschiede zwischen den Zeilen Winkel-Systemunterschiede, keine Euro-Längenunterschiede.")))
        print(wrap(L(self.lang,
            "How to use it: choose --scenario resonance to see cleaner angular coherence, --scenario power to see stronger state/currency attachment, --scenario wellbeing to privilege livability, --scenario fragmented for scattered axes, --scenario scarcity for high needs and low production, or --scenario tradeboom for strong export/import motion.",
            "So nutzt du es: Wähle --scenario resonance für klareren Winkelzusammenhalt, --scenario power für stärkere Staats-/Währungsbindung, --scenario wellbeing für Vorrang des Lebbaren, --scenario fragmented für gestreute Achsen, --scenario scarcity für hohen Bedarf und niedrige Produktion oder --scenario tradeboom für starke Export-/Importbewegung.")))

    # ------------------------------------------------------------------
    # Exports
    # ------------------------------------------------------------------

    def export_csv(self, path: str) -> None:
        if not self.history:
            return
        fields = list(self.history[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in self.history:
                w.writerow(r)

    def export_currency_csv(self, path: str) -> None:
        if not self.currency_history:
            return
        fields = list(self.currency_history[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in self.currency_history:
                w.writerow(r)

    def export_markdown(self, path: str) -> None:
        lines = []
        if self.lang == "de":
            lines.append("# Abschlussbericht der Winkelwährungswirtschaft\n\n")
            lines.append(f"Szenario: `{scenario_label(self.scenario, self.lang)}`  \nSeed: `{self.seed}`  \nTicks: `{self.max_ticks}`  \n\n")
            lines.append("## Währungen\n\n")
            lines.append("| Währung | Heimat | Länge | Endwinkel | Anteil zuletzt | Macht |\n")
            lines.append("|---|---:|---:|---:|---:|---:|\n")
            for cur in self.currencies.values():
                lines.append(f"| {cur.code} {cur.name(self.lang)} | {cur.home} | {cur.length:.3f} VE | {cur.angle:.2f}° | {cur.share*100:.2f}% | {cur.power:.2f} |\n")
            lines.append("\n## Länder\n\n")
            lines.append("| Land | WBI | MPI | ES | TD | Eigene Währung zuletzt |\n")
            lines.append("|---|---:|---:|---:|---:|---:|\n")
            for c in self.countries.values():
                lines.append(f"| {c.code} {c.display_name(self.lang)} | {c.wbi:.2f} | {c.mpi:.2f} | {c.wsk:.2f} | {c.spg:.2f} | {c.last_currency_mix.get(c.currency, 0)*100:.2f}% |\n")
            lines.append("\nDie Simulation maximiert keinen Reichtum. Alle drei Währungen behalten dieselbe Vektorlänge von 1 VE; die Konkurrenz entsteht durch Winkel.\n")
        else:
            lines.append("# Angular Vector-Currency Economy Final Report\n\n")
            lines.append(f"Scenario: `{scenario_label(self.scenario, self.lang)}`  \nSeed: `{self.seed}`  \nTicks: `{self.max_ticks}`  \n\n")
            lines.append("## Currencies\n\n")
            lines.append("| Currency | Home | Length | End angle | Last share | Power |\n")
            lines.append("|---|---:|---:|---:|---:|---:|\n")
            for cur in self.currencies.values():
                lines.append(f"| {cur.code} {cur.name(self.lang)} | {cur.home} | {cur.length:.3f} VE | {cur.angle:.2f}° | {cur.share*100:.2f}% | {cur.power:.2f} |\n")
            lines.append("\n## Countries\n\n")
            lines.append("| Country | WBI | MPI | ES | TD | Home currency last |\n")
            lines.append("|---|---:|---:|---:|---:|---:|\n")
            for c in self.countries.values():
                lines.append(f"| {c.code} {c.display_name(self.lang)} | {c.wbi:.2f} | {c.mpi:.2f} | {c.wsk:.2f} | {c.spg:.2f} | {c.last_currency_mix.get(c.currency, 0)*100:.2f}% |\n")
            lines.append("\nThe simulation does not maximize wealth. All three currencies keep the same vector length of 1 VE; competition arises from angles.\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(lines))



# -----------------------------------------------------------------------------
# 6b. Multilingual semantic output layer
# -----------------------------------------------------------------------------
# The first v3 layer already translates the core model. This layer catches the
# longer explanatory sentences, glossary rows, dynamic interpretations and gallery
# result summaries so that every requested language receives a semantic explanation
# instead of a mixed English fallback.

COMMON.update({
    "Scenario comparison was disabled, so the reading below refers only to the active run.": _names("Scenario comparison was disabled, so the reading below refers only to the active run.","Der Szenariovergleich wurde deaktiviert; die folgende Lesart bezieht sich nur auf den aktiven Lauf.","Сравнение сценариев отключено; чтение ниже относится только к активному запуску.","La comparación de escenarios fue desactivada; la lectura siguiente se refiere solo a la ejecución activa.","Il confronto tra scenari è disattivato; la lettura seguente riguarda solo la corsa attiva.","情景比较已禁用；下面的解读只针对当前运行。","シナリオ比較は無効です。以下の読み方は現在の実行だけを対象にします。","시나리오 비교가 비활성화되어 아래 해석은 현재 실행에만 해당합니다.","परिदृश्य तुलना बंद है; नीचे की पढ़ाई केवल सक्रिय रन पर लागू है।","השוואת התרחישים כבויה; הקריאה להלן מתייחסת רק להרצה הפעילה.","مقایسه سناریو غیرفعال است؛ خوانش زیر فقط به اجرای فعال مربوط است.","مقارنة السيناريوهات معطلة؛ والقراءة أدناه تخص التشغيل النشط فقط."),
})

COMMON.update({
    "Targetθ": _names("Targetθ","Zielθ","Цельθ","Objetivoθ","Obiettivoθ","目标θ","目標θ","목표θ","लक्ष्यθ","יעדθ","هدفθ","الهدفθ"),
    "OwnS last": _names("OwnS last","OwnS zuletzt","посл. OwnS","OwnS final","OwnS finale","最终 OwnS","最終 OwnS","최종 OwnS","अंतिम OwnS","OwnS אחרון","OwnS نهایی","OwnS النهائي"),
    "UTF-8 mini chart": _names("UTF-8 mini chart","UTF-8-Minikurve","мини-график UTF-8","minigráfico UTF-8","mini grafico UTF-8","UTF-8 迷你图","UTF-8 ミニ図","UTF-8 미니 차트","UTF-8 सूक्ष्म चार्ट","תרשים זעיר UTF-8","نمودار کوچک UTF-8","رسم صغير UTF-8"),
    "arithmetic mean": _names("arithmetic mean","arithmetischer Mittelwert","среднее арифметическое","media aritmética","media aritmetica","算术平均","算術平均","산술 평균","अंकगणितीय औसत","ממוצע חשבוני","میانگین حسابی","متوسط حسابي"),
    "Route": _names("Route","Route","маршрут","ruta","rotta","路线","経路","경로","मार्ग","נתיב","مسیر","المسار"),
    "Sector": _names("Sector","Sektor","сектор","sector","settore","部门","部門","부문","क्षेत्र","מגזר","بخش","القطاع"),
    "Highest price": _names("Highest price","Höchster Preis","наивысшая цена","precio máximo","prezzo massimo","最高价格","最高価格","최고 가격","सबसे ऊँचा मूल्य","המחיר הגבוה","بالاترین قیمت","أعلى سعر"),
    "Final currency directions": _names("Final currency directions","Endrichtungen der Währungen","итоговые направления валют","direcciones finales de las monedas","direzioni finali delle valute","货币最终方向","通貨の最終方向","통화의 최종 방향","मुद्राओं की अंतिम दिशाएँ","כיווני המטבעות הסופיים","جهت‌های نهایی ارزها","الاتجاهات النهائية للعملات"),
    "the currency compass": _names("the currency compass","den Währungskompass","валютный компас","la brújula monetaria","la bussola valutaria","货币罗盘","通貨コンパス","통화 나침반","मुद्रा कम्पास","מצפן המטבעות","قطب‌نمای ارز","بوصلة العملات"),
    "equal vector length": _names("equal vector length","gleiche Vektorlänge","равную длину вектора","longitud vectorial igual","lunghezza vettoriale uguale","等向量长度","同じベクトル長","같은 벡터 길이","समान वेक्टर लंबाई","אורך וקטור שווה","طول برداری برابر","طول متجه متساوٍ"),
    "orthogonal axes": _names("orthogonal axes","orthogonale Achsen","ортогональные оси","ejes ortogonales","assi ortogonali","正交轴","直交軸","직교 축","लंबवत अक्ष","צירים ניצבים","محورهای عمود","محاور متعامدة"),
    "the three market vectors": _names("the three market vectors","die drei Marktvektoren","три рыночных вектора","los tres vectores de mercado","i tre vettori di mercato","三个市场向量","三つの市場ベクトル","세 시장 벡터","तीन बाज़ार वेक्टर","שלושת וקטורי השוק","سه بردار بازار","متجهات السوق الثلاثة"),
    "power versus well-being": _names("power versus well-being","Macht gegen Wohlbefinden","власть против благополучия","poder frente a bienestar","potere contro benessere","权力对福祉","権力対幸福","권력 대 복지","शक्ति बनाम कल्याण","עוצמה מול רווחה","قدرت در برابر رفاه","القوة مقابل الرفاه"),
    "the tension carpet": _names("the tension carpet","den Spannungsteppich","ковёр напряжения","la alfombra de tensión","il tappeto della tensione","张力地毯","緊張カーペット","긴장 카펫","तनाव कालीन","שטיח המתח","فرش تنش","بساط التوتر"),
    "the trade triangle": _names("the trade triangle","das Handelsdreieck","торговый треугольник","el triángulo comercial","il triangolo commerciale","贸易三角","貿易三角形","무역 삼각형","व्यापार त्रिकोण","משולש המסחר","مثلث تجارت","مثلث التجارة"),
    "currency drift": _names("currency drift","Währungsdrift","дрейф валют","deriva monetaria","deriva valutaria","货币漂移","通貨ドリフト","통화 표류","मुद्रा बहाव","סחיפת מטבע","رانش ارز","انجراف العملة"),
    "sector satisfaction": _names("sector satisfaction","Sektordeckung","покрытие секторов","cobertura sectorial","copertura settoriale","部门满足度","部門充足度","부문 충족","क्षेत्र पूर्ति","כיסוי מגזרי","پوشش بخشی","تغطية القطاعات"),
    "price waves": _names("price waves","Preiswellen","ценовые волны","olas de precios","onde di prezzo","价格波","価格の波","가격 파동","मूल्य तरंगें","גלי מחיר","موج‌های قیمت","موجات السعر"),
    "scenario quadrants": _names("scenario quadrants","Szenarioquadranten","квадранты сценариев","cuadrantes de escenario","quadranti di scenario","情景象限","シナリオ象限","시나리오 사분면","परिदृश्य चतुर्थांश","רבעוני תרחיש","ربع‌های سناریو","أرباع السيناريو"),
    "Legend: green low TD, yellow medium TD, red high TD": _names("Legend: green low TD, yellow medium TD, red high TD","Legende: grün niedriger TD, gelb mittlerer TD, rot hoher TD","Легенда: зелёный низкий TD, жёлтый средний TD, красный высокий TD","Leyenda: verde TD bajo, amarillo TD medio, rojo TD alto","Legenda: verde TD basso, giallo TD medio, rosso TD alto","图例：绿色低TD，黄色中TD，红色高TD","凡例: 緑=低TD、黄=中TD、赤=高TD","범례: 초록 낮은 TD, 노랑 중간 TD, 빨강 높은 TD","कथा: हरा कम TD, पीला मध्यम TD, लाल उच्च TD","מקרא: ירוק TD נמוך, צהוב בינוני, אדום גבוה","راهنما: سبز TD کم، زرد متوسط، قرمز زیاد","المفتاح: أخضر TD منخفض، أصفر متوسط، أحمر مرتفع"),
    "TD over ticks": _names("TD over ticks","TD über Ticks","TD по тикам","TD por ciclos","TD per tick","随周期的TD","時点ごとのTD","틱별 TD","चक्रों पर TD","TD לאורך מחזורים","TD در تیک‌ها","TD عبر الدورات"),
    "Final arrows; trails listed below": _names("Final arrows; trails listed below","Endpfeile; Spuren darunter","итоговые стрелки; следы ниже","flechas finales; rastros abajo","frecce finali; tracce sotto","最终箭头；下方列轨迹","最終矢印；下に軌跡","최종 화살표; 아래에 흔적","अंतिम तीर; नीचे पथ","חיצים סופיים; עקבות למטה","پیکان‌های نهایی؛ ردها پایین","الأسهم النهائية؛ الآثار أدناه"),
    "Scenario comparison disabled.": _names("Scenario comparison disabled.","Szenariovergleich deaktiviert.","сравнение сценариев отключено.","comparación de escenarios desactivada.","confronto scenari disattivato.","情景比较已关闭。","シナリオ比較は無効です。","시나리오 비교가 꺼져 있습니다.","परिदृश्य तुलना बंद है।","השוואת תרחישים כבויה.","مقایسه سناریو غیرفعال است.","مقارنة السيناريوهات معطلة."),
})

COMMON.update({
    "Currency compass: three equal-length Euro vectors": _names("Currency compass: three equal-length Euro vectors","Währungskompass: drei gleich lange Euro-Vektoren","Валютный компас: три равных евро-вектора","Brújula monetaria: tres euro-vectores iguales","Bussola valutaria: tre euro-vettori uguali","货币罗盘：三个等长欧元向量","通貨コンパス: 同じ長さの三つのユーロ・ベクトル","통화 나침반: 같은 길이의 세 유로 벡터","मुद्रा कम्पास: समान लंबाई वाले तीन यूरो-वेक्टर","מצפן מטבעות: שלושה וקטורי אירו שווים","قطب‌نمای ارز: سه بردار یوروی هم‌طول","بوصلة العملات: ثلاثة متجهات يورو متساوية الطول"),
    "Equal vector-length proof: price is count, not stretch": _names("Equal vector-length proof: price is count, not stretch","Gleichlängenbeweis: Preis ist Anzahl, nicht Streckung","Доказательство равной длины: цена — счёт, не растяжение","Prueba de longitud igual: precio es conteo, no estiramiento","Prova di lunghezza uguale: il prezzo è conteggio, non stiramento","等长证明：价格是计数，不是拉伸","同じ長さの証明: 価格は数であり伸長ではない","같은 길이 증명: 가격은 개수이지 늘림이 아님","समान लंबाई प्रमाण: मूल्य गिनती है, खिंचाव नहीं","הוכחת אורך שווה: מחיר הוא ספירה, לא מתיחה","اثبات طول برابر: قیمت شمارش است، نه کشش","إثبات الطول المتساوي: السعر عدد لا تمديد"),
    "Government good/evil axis and population popular/unpopular axis": _names("Government good/evil axis and population popular/unpopular axis","Regierungsachse Gut/Böse und Bevölkerungsachse Beliebt/Unbeliebt","Ось добро/зло правительства и ось популярно/непопулярно населения","Eje bueno/malo del gobierno y eje popular/impopular de la población","Asse bene/male del governo e asse popolare/impopolare della popolazione","政府好/恶轴与人口受欢迎/不受欢迎轴","政府の善/悪軸と住民の人気/不人気軸","정부 선/악 축과 인구 인기/비인기 축","सरकार अच्छा/बुरा अक्ष और जनता लोकप्रिय/अलोकप्रिय अक्ष","ציר טוב/רע ממשלתי וציר פופולרי/לא פופולרי של האוכלוסייה","محور خوب/بد دولت و محور محبوب/نامحبوب مردم","محور الخير/الشر للحكومة ومحور محبوب/غير محبوب للسكان"),
    "Three market vectors: buy, sell and labor": _names("Three market vectors: buy, sell and labor","Drei Marktvektoren: Kauf, Verkauf und Arbeit","Три рыночных вектора: покупка, продажа и труд","Tres vectores de mercado: compra, venta y trabajo","Tre vettori di mercato: acquisto, vendita e lavoro","三个市场向量：购买、销售和劳动","三つの市場ベクトル: 購入・販売・労働","세 시장 벡터: 구매, 판매, 노동","तीन बाज़ार वेक्टर: खरीद, बिक्री और श्रम","שלושה וקטורי שוק: קנייה, מכירה ועבודה","سه بردار بازار: خرید، فروش و کار","ثلاثة متجهات سوق: الشراء والبيع والعمل"),
    "Power versus well-being map": _names("Power versus well-being map","Macht-gegen-Wohlbefinden-Karte","Карта власть против благополучия","Mapa poder frente a bienestar","Mappa potere contro benessere","权力对福祉地图","権力対幸福マップ","권력 대 복지 지도","शक्ति बनाम कल्याण नक्शा","מפת עוצמה מול רווחה","نقشه قدرت در برابر رفاه","خريطة القوة مقابل الرفاه"),
    "Tension heat carpet through time": _names("Tension heat carpet through time","Spannungs-Heatcarpet über die Zeit","Тепловой ковёр напряжения во времени","Alfombra térmica de tensión en el tiempo","Tappeto termico della tensione nel tempo","随时间的张力热地毯","時間を通じた緊張ヒートカーペット","시간에 따른 긴장 히트 카펫","समय पर तनाव ताप-कालीन","שטיח חום של מתח לאורך זמן","فرش حرارتی تنش در زمان","بساط حرارة التوتر عبر الزمن"),
    "Trade triangle: goods move, vectors rotate": _names("Trade triangle: goods move, vectors rotate","Handelsdreieck: Güter bewegen sich, Vektoren drehen","Торговый треугольник: блага движутся, векторы вращаются","Triángulo comercial: los bienes se mueven, los vectores giran","Triangolo commerciale: i beni si muovono, i vettori ruotano","贸易三角：商品移动，向量旋转","貿易三角形: 財が動き、ベクトルが回転する","무역 삼각형: 재화는 움직이고 벡터는 회전","व्यापार त्रिकोण: वस्तुएँ चलती हैं, वेक्टर घूमते हैं","משולש מסחר: טובין נעים, וקטורים מסתובבים","مثلث تجارت: کالا حرکت می‌کند، بردارها می‌چرخند","مثلث التجارة: السلع تتحرك والمتجهات تدور"),
    "Currency drift trails": _names("Currency drift trails","Währungsdrift-Spuren","Следы дрейфа валют","Rastros de deriva monetaria","Tracce di deriva valutaria","货币漂移轨迹","通貨ドリフトの軌跡","통화 표류 흔적","मुद्रा बहाव पथ","עקבות סחיפת מטבע","ردهای رانش ارز","آثار انجراف العملة"),
    "Sector satisfaction mosaic": _names("Sector satisfaction mosaic","Sektor-Deckungs-Mosaik","Мозаика покрытия секторов","Mosaico de cobertura sectorial","Mosaico di copertura settoriale","部门满足马赛克","部門充足モザイク","부문 충족 모자이크","क्षेत्र पूर्ति मोज़ेक","פסיפס כיסוי מגזרי","موزاییک پوشش بخشی","فسيفساء تغطية القطاعات"),
    "Vector-Euro price waves": _names("Vector-Euro price waves","Vektor-Euro-Preiswellen","Ценовые волны вектор-евро","Olas de precio vector-euro","Onde di prezzo vettore-euro","向量欧元价格波","ベクトル・ユーロ価格波","벡터-유로 가격 파동","वेक्टर-यूरो मूल्य तरंगें","גלי מחיר וקטור-אירו","موج‌های قیمت بردار-یورو","موجات سعر متجه-اليورو"),
    "Scenario quadrants: how to classify the economy": _names("Scenario quadrants: how to classify the economy","Szenario-Quadranten: wie die Wirtschaft einzuordnen ist","Квадранты сценариев: как классифицировать экономику","Cuadrantes de escenario: cómo clasificar la economía","Quadranti di scenario: come classificare l'economia","情景象限：如何分类经济","シナリオ象限: 経済をどう分類するか","시나리오 사분면: 경제를 분류하는 법","परिदृश्य चतुर्थांश: अर्थव्यवस्था को कैसे वर्गीकृत करें","רבעוני תרחיש: איך לסווג את הכלכלה","ربع‌های سناریو: اقتصاد را چگونه دسته‌بندی کنیم","أرباع السيناريو: كيف نصنف الاقتصاد"),
    "Silent scenario comparison": _names("Silent scenario comparison","Stiller Szenariovergleich","Тихое сравнение сценариев","Comparación silenciosa de escenarios","Confronto silenzioso degli scenari","静默情景比较","サイレント・シナリオ比較","조용한 시나리오 비교","मौन परिदृश्य तुलना","השוואת תרחישים שקטה","مقایسه سناریوی خاموش","مقارنة سيناريو صامتة"),
    " POWER LOCK ": _names(" POWER LOCK "," MACHTKLEMME "," ЗАМОК ВЛАСТИ "," BLOQUEO DE PODER "," BLOCCO DI POTERE "," 权力锁定 "," 権力ロック "," 권력 잠금 "," शक्ति लॉक "," נעילת כוח "," قفل قدرت "," قفل القوة "),
    " RESONANCE ": _names(" RESONANCE "," RESONANZ "," РЕЗОНАНС "," RESONANCIA "," RISONANZA "," 共振 "," 共鳴 "," 공명 "," अनुनाद "," תהודה "," تشدید "," رنين "),
    " FRACTURE ": _names(" FRACTURE "," BRUCH "," РАЗЛОМ "," FRACTURA "," FRATTURA "," 断裂 "," 分裂 "," 균열 "," टूटन "," שבר "," گسست "," كسر "),
    " WELL-BEING ISLAND ": _names(" WELL-BEING ISLAND "," WOHLBEFINDENSINSEL "," ОСТРОВ БЛАГОПОЛУЧИЯ "," ISLA DE BIENESTAR "," ISOLA DEL BENESSERE "," 福祉岛 "," 幸福島 "," 복지 섬 "," कल्याण द्वीप "," אי רווחה "," جزیره رفاه "," جزيرة الرفاه "),
})

COMMON.update({
    "The three competing Euro vectors.": _names("The three competing Euro vectors.","Die drei konkurrierenden Euro-Vektoren.","Три конкурирующих евро-вектора.","Los tres euro-vectores competidores.","I tre euro-vettori concorrenti.","三个竞争的欧元向量。","競合する三つのユーロ・ベクトル。","경쟁하는 세 유로 벡터.","तीन प्रतिस्पर्धी यूरो-वेक्टर।","שלושת וקטורי האירו המתחרים.","سه بردار یوروی رقیب.","متجهات اليورو الثلاثة المتنافسة."),
    "Vector length. It must remain 1.000 for all currencies.": _names("Vector length. It must remain 1.000 for all currencies.","Vektorlänge. Sie muss bei allen Währungen 1.000 bleiben.","Длина вектора; для всех валют она остаётся 1.000.","Longitud del vector; debe quedar en 1.000 para todas las monedas.","Lunghezza del vettore; deve restare 1.000 per tutte le valute.","向量长度；所有货币必须保持 1.000。","ベクトル長。すべての通貨で 1.000 のままです。","벡터 길이. 모든 통화에서 1.000으로 유지됩니다.","वेक्टर लंबाई; सभी मुद्राओं में 1.000 रहती है।","אורך וקטור; נשאר 1.000 בכל המטבעות.","طول بردار؛ برای همه ارزها 1.000 می‌ماند.","طول المتجه؛ يبقى 1.000 لكل العملات."),
    "Current direction of a currency on the ring.": _names("Current direction of a currency on the ring.","Aktuelle Richtung einer Währung auf dem Ring.","Текущее направление валюты на кольце.","Dirección actual de una moneda en el anillo.","Direzione attuale di una valuta sull'anello.","货币在环上的当前方向。","リング上の通貨の現在方向。","고리 위 통화의 현재 방향.","वृत्त पर मुद्रा की वर्तमान दिशा।","הכיוון הנוכחי של מטבע על הטבעת.","جهت کنونی ارز روی حلقه.","الاتجاه الحالي للعملة على الحلقة."),
    "Part of this tick's transaction flow captured by the currency angle.": _names("Part of this tick's transaction flow captured by the currency angle.","Anteil des Transaktionsflusses dieses Ticks, den der Währungswinkel bindet.","Доля потока сделок этого тика, захваченная углом валюты.","Parte del flujo de transacciones de este ciclo captada por el ángulo monetario.","Quota del flusso di transazioni del tick catturata dall'angolo valutario.","本周期交易流被货币角度捕获的份额。","この時点の取引流のうち通貨角が捉えた部分。","이 틱의 거래 흐름 중 통화 각도가 잡은 부분.","इस चक्र के लेन-देन प्रवाह का वह भाग जिसे मुद्रा कोण पकड़ता है।","חלק מזרם העסקאות במחזור זה שנקלט בזווית המטבע.","بخشی از جریان تراکنش این تیک که زاویه ارز جذب می‌کند.","جزء من تدفق معاملات هذه الدورة تلتقطه زاوية العملة."),
    "Accumulated attachment of market action and home government to this vector.": _names("Accumulated attachment of market action and home government to this vector.","Aufgebaute Bindung von Markthandlung und Heimatregierung an diesen Vektor.","Накопленная привязка рыночного действия и домашнего правительства к этому вектору.","Vinculación acumulada de acción de mercado y gobierno propio a este vector.","Legame accumulato di azione di mercato e governo nazionale a questo vettore.","市场行动和本国政府对该向量的累积绑定。","市場行動と自国政府がこのベクトルへ積み上げた結合。","시장 행동과 본국 정부가 이 벡터에 쌓은 결속.","बाज़ार क्रिया और गृह सरकार का इस वेक्टर से जमा जुड़ाव।","הקשר המצטבר של פעולת שוק וממשלת הבית לווקטור זה.","وابستگی انباشته کنش بازار و دولت خانگی به این بردار.","الارتباط المتراكم لحركة السوق والحكومة المحلية بهذا المتجه."),
    "Angle distance between two currencies; not a money exchange rate.": _names("Angle distance between two currencies; not a money exchange rate.","Winkelabstand zwischen zwei Währungen; kein Geld-Wechselkurs.","Угловое расстояние между валютами; не денежный курс.","Distancia angular entre dos monedas; no es un tipo de cambio monetario.","Distanza angolare tra due valute; non è un cambio monetario.","两种货币之间的角距离；不是货币汇率。","二つの通貨の角度距離。貨幣の為替レートではありません。","두 통화 사이의 각도 거리; 돈 환율이 아닙니다.","दो मुद्राओं के बीच कोण दूरी; धन-विनिमय दर नहीं।","מרחק זוויתי בין שני מטבעות; לא שער חליפין כספי.","فاصله زاویه‌ای میان دو ارز؛ نرخ تبدیل پولی نیست.","مسافة زاوية بين عملتين؛ ليست سعر صرف نقدي."),
    "Angular resonance. 1 means same direction, 0 means opposite direction.": _names("Angular resonance. 1 means same direction, 0 means opposite direction.","Winkelresonanz. 1 heißt gleiche Richtung, 0 heißt Gegenrichtung.","Угловой резонанс: 1 — одно направление, 0 — противоположное.","Resonancia angular: 1 misma dirección, 0 dirección opuesta.","Risonanza angolare: 1 stessa direzione, 0 direzione opposta.","角度共振：1 表示同向，0 表示反向。","角度共鳴。1 は同方向、0 は反対方向。","각도 공명: 1은 같은 방향, 0은 반대 방향.","कोणीय अनुनाद: 1 समान दिशा, 0 विपरीत दिशा।","תהודה זוויתית: 1 אותו כיוון, 0 כיוון מנוגד.","تشدید زاویه‌ای: 1 هم‌جهت، 0 خلاف‌جهت.","رنين زاوي: 1 نفس الاتجاه، 0 اتجاه معاكس."),
    "Action angle of labor in a sector.": _names("Action angle of labor in a sector.","Handlungswinkel der Arbeit in einem Sektor.","Угол действия труда в секторе.","Ángulo de acción del trabajo en un sector.","Angolo d'azione del lavoro in un settore.","某部门劳动的行动角。","部門における労働の行動角。","부문 내 노동의 행동 각도.","किसी क्षेत्र में श्रम का क्रिया-कोण।","זווית הפעולה של עבודה במגזר.","زاویه کنش کار در یک بخش.","زاوية فعل العمل في قطاع."),
    "Currency whose angle fits the labor action best.": _names("Currency whose angle fits the labor action best.","Währung, deren Winkel am besten zur Arbeitshandlung passt.","Валюта, чей угол лучше всего подходит действию труда.","Moneda cuyo ángulo encaja mejor con la acción laboral.","Valuta il cui angolo si adatta meglio all'azione lavorativa.","角度最适合劳动行动的货币。","労働行動に最も合う角度の通貨。","노동 행동에 각도가 가장 잘 맞는 통화.","जिस मुद्रा का कोण श्रम क्रिया से सबसे अच्छा मिलता है।","מטבע שהזווית שלו מתאימה ביותר לפעולת העבודה.","ارزی که زاویه‌اش بهترین سازگاری را با کنش کار دارد.","العملة التي تناسب زاويتها فعل العمل أكثر."),
    "Abstract labor hours allocated this tick.": _names("Abstract labor hours allocated this tick.","Abstrakte Arbeitsstunden, die in diesem Tick zugeteilt werden.","Абстрактные рабочие часы, выделенные в этом тике.","Horas laborales abstractas asignadas en este ciclo.","Ore di lavoro astratte assegnate in questo tick.","本周期分配的抽象劳动小时。","この時点で割り当てられた抽象労働時間。","이 틱에 배정된 추상 노동시간.","इस चक्र में बाँटे गए अमूर्त श्रम घंटे।","שעות עבודה מופשטות שהוקצו במחזור זה.","ساعت‌های کار انتزاعی تخصیص‌یافته در این تیک.","ساعات العمل المجردة المخصصة في هذه الدورة."),
    "Production created by labor and productivity.": _names("Production created by labor and productivity.","Produktion aus Arbeit und Produktivität.","Производство, созданное трудом и производительностью.","Producción creada por trabajo y productividad.","Produzione creata da lavoro e produttività.","由劳动和生产率产生的产出。","労働と生産性から生じる生産。","노동과 생산성이 만든 생산량.","श्रम और उत्पादकता से बना उत्पादन।","ייצור שנוצר מעבודה ופריון.","تولید حاصل از کار و بهره‌وری.","الإنتاج الناتج من العمل والإنتاجية."),
    "Fatigue from labor close to the unpopular pole.": _names("Fatigue from labor close to the unpopular pole.","Ermüdung durch Arbeit nahe am Unbeliebt-Pol.","Усталость от труда возле непопулярного полюса.","Fatiga por trabajo cerca del polo impopular.","Fatica da lavoro vicino al polo impopolare.","劳动接近不受欢迎极点造成的疲劳。","不人気極に近い労働から来る疲労。","비인기 극에 가까운 노동에서 생기는 피로.","अलोकप्रिय ध्रुव के पास श्रम से थकान।","עייפות מעבודה קרובה לקוטב הלא-פופולרי.","خستگی ناشی از کار نزدیک قطب نامحبوب.","إرهاق من العمل قرب قطب غير المحبوب."),
    "Population demand in the sector.": _names("Population demand in the sector.","Bedarf der Bevölkerung im Sektor.","Спрос населения в секторе.","Demanda de la población en el sector.","Domanda della popolazione nel settore.","该部门的人口需求。","部門における住民需要。","부문 내 인구 수요.","क्षेत्र में जनता की माँग।","ביקוש האוכלוסייה במגזר.","تقاضای جمعیت در بخش.","طلب السكان في القطاع."),
    "Production minus exports plus imports.": _names("Production minus exports plus imports.","Produktion minus Exporte plus Importe.","Производство минус экспорт плюс импорт.","Producción menos exportaciones más importaciones.","Produzione meno esportazioni più importazioni.","生产减出口加进口。","生産から輸出を引き輸入を足したもの。","생산-수출+수입.","उत्पादन घटा निर्यात, जोड़ा आयात।","ייצור פחות יצוא ועוד יבוא.","تولید منهای صادرات به‌علاوه واردات.","الإنتاج ناقص الصادرات زائد الواردات."),
    "Need covered by final supply.": _names("Need covered by final supply.","Bedarf, der durch Endversorgung gedeckt ist.","Потребность, покрытая итоговым предложением.","Necesidad cubierta por la oferta final.","Bisogno coperto dall'offerta finale.","最终供给覆盖的需求。","最終供給で満たされた需要。","최종 공급이 충족한 필요.","अंतिम आपूर्ति से पूरी हुई जरूरत।","צורך שכוסה באספקה הסופית.","نیازی که عرضه نهایی پوشش داده است.","الحاجة التي غطاها العرض النهائي."),
    "Number of equal vector-Euro units per goods unit.": _names("Number of equal vector-Euro units per goods unit.","Anzahl gleicher Vektor-Euro-Einheiten pro Gütereinheit.","Число равных вектор-евро на единицу блага.","Número de unidades vector-euro iguales por unidad de bien.","Numero di unità vettore-euro uguali per unità di bene.","每单位商品所需的等长向量欧元数量。","財一単位あたりの同じ長さのベクトル・ユーロ数。","재화 단위당 같은 길이의 벡터-유로 수.","प्रति वस्तु इकाई समान वेक्टर-यूरो की संख्या।","מספר יחידות וקטור-אירו שוות לכל יחידת טובין.","تعداد واحدهای بردار-یوروی برابر برای هر واحد کالا.","عدد وحدات متجه-اليورو المتساوية لكل وحدة سلعة."),
    "Buy and sell action angles.": _names("Buy and sell action angles.","Handlungswinkel für Kauf und Verkauf.","Углы действий покупки и продажи.","Ángulos de acción de compra y venta.","Angoli d'azione di acquisto e vendita.","买入和卖出行动角。","購入と販売の行動角。","구매와 판매 행동 각도.","खरीद और बिक्री के क्रिया-कोण।","זוויות פעולה של קנייה ומכירה.","زاویه‌های کنش خرید و فروش.","زوايا فعل الشراء والبيع."),
    "Best currency for buy/sell angle.": _names("Best currency for buy/sell angle.","Beste Währung für Kauf-/Verkaufswinkel.","Лучшая валюта для угла покупки/продажи.","Mejor moneda para el ángulo de compra/venta.","Migliore valuta per l'angolo acquisto/vendita.","最适合买/卖角的货币。","購入/販売角に最も合う通貨。","구매/판매 각도에 가장 맞는 통화.","खरीद/बिक्री कोण के लिए सबसे अनुकूल मुद्रा।","המטבע המתאים ביותר לזווית קנייה/מכירה.","بهترین ارز برای زاویه خرید/فروش.","أفضل عملة لزاوية الشراء/البيع."),
    "Average orthogonal deviation of good/evil versus popular/unpopular axes.": _names("Average orthogonal deviation of good/evil versus popular/unpopular axes.","Durchschnittliche Orthogonalitätsabweichung von Gut/Böse zu Beliebt/Unbeliebt.","Среднее отклонение ортогональности осей добро/зло и популярно/непопулярно.","Desviación ortogonal media entre bueno/malo y popular/impopular.","Deviazione ortogonale media tra bene/male e popolare/impopolare.","好/恶轴与受欢迎/不受欢迎轴之间的平均正交偏差。","善/悪軸と人気/不人気軸の平均直交偏差。","선/악 축과 인기/비인기 축의 평균 직교 편차.","अच्छा/बुरा और लोकप्रिय/अलोकप्रिय अक्षों की औसत लंबवत विचलन।","סטייה ניצבת ממוצעת בין צירי טוב/רע ופופולרי/לא פופולרי.","میانگین انحراف عمودیت میان محور خوب/بد و محبوب/نامحبوب.","متوسط انحراف التعامد بين محوري الخير/الشر والمحبوب/غير المحبوب."),
    "Exporter to importer.": _names("Exporter to importer.","Exporteur zu Importeur.","Экспортёр к импортёру.","Exportador a importador.","Esportatore verso importatore.","出口方到进口方。","輸出国から輸入国へ。","수출자에서 수입자로.","निर्यातक से आयातक।","יצואן ליבואן.","صادرکننده به واردکننده.","من المصدّر إلى المستورد."),
    "Traded quantity.": _names("Traded quantity.","Gehandelte Menge.","Торгуемое количество.","Cantidad comerciada.","Quantità scambiata.","交易数量。","取引量。","거래량.","व्यापारित मात्रा।","כמות נסחרת.","مقدار معامله‌شده.","الكمية المتداولة."),
    "Currency angle used by the joint trade action.": _names("Currency angle used by the joint trade action.","Währungswinkel der gemeinsamen Handelshandlung.","Угол валюты, используемый совместным торговым действием.","Ángulo monetario usado por la acción comercial conjunta.","Angolo valutario usato dall'azione commerciale congiunta.","联合贸易行动使用的货币角。","共同貿易行動が用いる通貨角。","공동 무역 행동이 쓰는 통화 각도.","संयुक्त व्यापार क्रिया में प्रयुक्त मुद्रा कोण।","זווית המטבע שבה משתמשת פעולת המסחר המשותפת.","زاویه ارزی که کنش مشترک تجارت به کار می‌برد.","زاوية العملة التي يستخدمها فعل التجارة المشترك."),
    "Mean action angle between exporter sell angle and importer buy angle.": _names("Mean action angle between exporter sell angle and importer buy angle.","Mittlerer Handlungswinkel zwischen Verkaufswinkel des Exporteurs und Kaufwinkel des Importeurs.","Средний угол действия между углом продажи экспортёра и углом покупки импортёра.","Ángulo medio entre venta del exportador y compra del importador.","Angolo medio tra vendita dell'esportatore e acquisto dell'importatore.","出口方卖出角与进口方买入角之间的平均行动角。","輸出側販売角と輸入側購入角の平均行動角。","수출자 판매각과 수입자 구매각 사이의 평균 행동각.","निर्यातक बिक्री कोण और आयातक खरीद कोण के बीच औसत क्रिया-कोण।","זווית פעולה ממוצעת בין זווית מכירת היצואן וזווית קניית היבואן.","زاویه کنش میانگین میان زاویه فروش صادرکننده و خرید واردکننده.","زاوية الفعل المتوسطة بين زاوية بيع المصدّر وزاوية شراء المستورد."),
    "Angle distance between exporter's home currency and trade currency.": _names("Angle distance between exporter's home currency and trade currency.","Winkelabstand zwischen Heimatwährung des Exporteurs und Handelswährung.","Угловая дистанция между домашней валютой экспортёра и валютой сделки.","Distancia angular entre moneda propia del exportador y moneda comercial.","Distanza angolare tra valuta dell'esportatore e valuta di scambio.","出口方本国货币与贸易货币之间的角距离。","輸出側の自国通貨と貿易通貨の角度距離。","수출자 자국 통화와 무역 통화 사이의 각도 거리.","निर्यातक की गृह मुद्रा और व्यापार मुद्रा के बीच कोण दूरी।","מרחק זוויתי בין מטבע הבית של היצואן למטבע המסחר.","فاصله زاویه‌ای میان ارز خانگی صادرکننده و ارز تجارت.","المسافة الزاوية بين عملة المصدّر المحلية وعملة التجارة."),
    "Angular work: vector-Euro amount multiplied by rotation in radians.": _names("Angular work: vector-Euro amount multiplied by rotation in radians.","Umlenkungsarbeit: Vektor-Euro-Menge mal Drehung in Radiant.","Угловая работа: количество вектор-евро, умноженное на поворот в радианах.","Trabajo angular: cantidad vector-euro multiplicada por giro en radianes.","Lavoro angolare: quantità vettore-euro moltiplicata per rotazione in radianti.","角度功：向量欧元数量乘以弧度旋转。","角度仕事: ベクトル・ユーロ量×ラジアン回転。","각도 일: 벡터-유로량 × 라디안 회전.","कोणीय कार्य: वेक्टर-यूरो मात्रा गुणा रेडियन में घुमाव।","עבודה זוויתית: כמות וקטור-אירו כפול סיבוב ברדיאנים.","کار زاویه‌ای: مقدار بردار-یورو ضربدر چرخش به رادیان.","العمل الزاوي: كمية متجه-اليورو مضروبة بالدوران بالراديان."),
    "Well-being index of the population.": _names("Well-being index of the population.","Wohlbefindenindex der Bevölkerung.","Индекс благополучия населения.","Índice de bienestar de la población.","Indice di benessere della popolazione.","人口福祉指数。","住民の幸福指数。","인구 복지 지수.","जनता का कल्याण सूचकांक।","מדד רווחת האוכלוסייה.","شاخص رفاه جمعیت.","مؤشر رفاه السكان."),
    "Power index of government/currency attachment.": _names("Power index of government/currency attachment.","Machtindex der Regierungs-/Währungsbindung.","Индекс власти привязки правительства/валюты.","Índice de poder de vínculo gobierno/moneda.","Indice di potere del legame governo/valuta.","政府/货币绑定的权力指数。","政府/通貨結合の権力指数。","정부/통화 결속의 권력 지수.","सरकार/मुद्रा जुड़ाव का शक्ति सूचकांक।","מדד עוצמה של קשר ממשלה/מטבע.","شاخص قدرت پیوند دولت/ارز.","مؤشر قوة ارتباط الحكومة/العملة."),
    "Economic strength under angular competition.": _names("Economic strength under angular competition.","Wirtschaftsstärke unter Winkelkonkurrenz.","Экономическая сила при угловой конкуренции.","Fuerza económica bajo competencia angular.","Forza economica sotto concorrenza angolare.","角度竞争下的经济强度。","角度競争下の経済強度。","각도 경쟁 아래의 경제 강도.","कोणीय प्रतिस्पर्धा के अधीन आर्थिक बल।","חוסן כלכלי תחת תחרות זוויתית.","توان اقتصادی زیر رقابت زاویه‌ای.","القوة الاقتصادية تحت المنافسة الزاوية."),
    "Tension degree. Lower is calmer.": _names("Tension degree. Lower is calmer.","Spannungsgrad. Niedriger ist ruhiger.","Степень напряжения; ниже — спокойнее.","Grado de tensión; más bajo es más tranquilo.","Grado di tensione; più basso è più calmo.","张力程度；越低越平静。","緊張度。低いほど穏やか。","긴장도. 낮을수록 안정적.","तनाव डिग्री; कम मान शांत है।","דרגת מתח; נמוך יותר רגוע יותר.","درجه تنش؛ کمتر یعنی آرام‌تر.","درجة التوتر؛ الأقل أكثر هدوءاً."),
    "Domestic share of the home vector currency.": _names("Domestic share of the home vector currency.","Inlandsanteil der eigenen Vektorwährung.","Внутренняя доля домашней векторной валюты.","Cuota interna de la moneda vectorial propia.","Quota interna della valuta vettoriale nazionale.","本国向量货币的国内份额。","自国ベクトル通貨の国内比率。","자국 벡터 통화의 국내 점유율.","गृह वेक्टर-मुद्रा का घरेलू हिस्सा।","חלק מקומי של מטבע הווקטור הביתי.","سهم داخلی ارز برداری خانگی.","الحصة المحلية لعملة المتجه المحلية."),
    "Dominant currency in local transaction flow.": _names("Dominant currency in local transaction flow.","Dominante Währung im lokalen Transaktionsfluss.","Доминирующая валюта в местном потоке сделок.","Moneda dominante en el flujo local de transacciones.","Valuta dominante nel flusso locale di transazioni.","本地交易流中的主导货币。","地域取引流で支配的な通貨。","지역 거래 흐름의 지배 통화.","स्थानीय लेन-देन प्रवाह की प्रमुख मुद्रा।","מטבע דומיננטי בזרם העסקאות המקומי.","ارز غالب در جریان تراکنش محلی.","العملة المهيمنة في تدفق المعاملات المحلي."),
    "Direction toward which a currency is slowly rotating.": _names("Direction toward which a currency is slowly rotating.","Richtung, zu der sich eine Währung langsam dreht.","Направление, к которому валюта медленно вращается.","Dirección hacia la que una moneda gira lentamente.","Direzione verso cui una valuta ruota lentamente.","货币缓慢旋转指向的方向。","通貨がゆっくり回転して向かう方向。","통화가 천천히 회전해 가는 방향.","जिस दिशा में मुद्रा धीरे घूमती है।","הכיוון שאליו המטבע מסתובב לאט.","جهتی که ارز آهسته به سوی آن می‌چرخد.","الاتجاه الذي تدور إليه العملة ببطء."),
    "Distance between current currency angle and its initial angle.": _names("Distance between current currency angle and its initial angle.","Abstand zwischen aktuellem Währungswinkel und Anfangswinkel.","Расстояние между текущим углом валюты и начальным углом.","Distancia entre el ángulo monetario actual y el inicial.","Distanza tra angolo valutario attuale e iniziale.","当前货币角与初始角之间的距离。","現在の通貨角と初期角の距離。","현재 통화 각도와 초기 각도의 거리.","वर्तमान मुद्रा कोण और आरंभिक कोण की दूरी।","מרחק בין זווית המטבע הנוכחית לזווית ההתחלתית.","فاصله میان زاویه کنونی ارز و زاویه آغازین.","المسافة بين زاوية العملة الحالية وزاويتها الابتدائية."),
    "Government good/evil angle: direction of the good pole.": _names("Government good/evil angle: direction of the good pole.","Gut/Böse-Winkel der Regierung: Richtung des Gut-Pols.","Угол добро/зло правительства: направление полюса добра.","Ángulo bueno/malo del gobierno: dirección del polo bueno.","Angolo bene/male del governo: direzione del polo bene.","政府好/恶角：好极点的方向。","政府の善/悪角: 善極の方向。","정부 선/악 각도: 선 극의 방향.","सरकार अच्छा/बुरा कोण: अच्छे ध्रुव की दिशा।","זווית טוב/רע של הממשלה: כיוון קוטב הטוב.","زاویه خوب/بد دولت: جهت قطب خوب.","زاوية الخير/الشر للحكومة: اتجاه قطب الخير."),
    "Population popular/unpopular angle: direction of the popular pole.": _names("Population popular/unpopular angle: direction of the popular pole.","Beliebt/Unbeliebt-Winkel der Bevölkerung: Richtung des Beliebt-Pols.","Угол популярно/непопулярно населения: направление популярного полюса.","Ángulo popular/impopular de la población: dirección del polo popular.","Angolo popolare/impopolare della popolazione: direzione del polo popolare.","人口受欢迎/不受欢迎角：受欢迎极点方向。","住民の人気/不人気角: 人気極の方向。","인구 인기/비인기 각도: 인기 극의 방향.","जनता लोकप्रिय/अलोकप्रिय कोण: लोकप्रिय ध्रुव की दिशा।","זווית פופולרי/לא פופולרי של האוכלוסייה: כיוון קוטב הפופולרי.","زاویه محبوب/نامحبوب مردم: جهت قطب محبوب.","زاوية محبوب/غير محبوب لدى السكان: اتجاه قطب المحبوب."),
    "Deviation from ideal 90° orthogonality between the axes.": _names("Deviation from ideal 90° orthogonality between the axes.","Abweichung von idealer 90°-Orthogonalität der Achsen.","Отклонение от идеальной ортогональности 90° между осями.","Desviación de la ortogonalidad ideal de 90° entre ejes.","Deviazione dall'ortogonalità ideale di 90° tra assi.","轴之间相对于理想90°正交的偏差。","軸間の理想的な90°直交からの偏差。","축 사이 이상적 90° 직교에서 벗어난 정도.","अक्षों के बीच आदर्श 90° लंबवतता से विचलन।","סטייה מאורתוגונליות אידאלית של 90° בין הצירים.","انحراف از عمودیت ایده‌آل 90 درجه میان محورها.","الانحراف عن التعامد المثالي 90° بين المحاور."),
    "Tiny history line from low ▁ to high █.": _names("Tiny history line from low ▁ to high █.","Kleine Verlaufslinie von niedrig ▁ bis hoch █.","Крошечная линия истории от низкого ▁ до высокого █.","Línea histórica pequeña de bajo ▁ a alto █.","Piccola linea storica da basso ▁ ad alto █.","从低 ▁ 到高 █ 的迷你历史线。","低 ▁ から高 █ への小さな履歴線。","낮음 ▁ 에서 높음 █ 까지의 작은 이력선.","निम्न ▁ से उच्च █ तक छोटी इतिहास रेखा।","קו היסטוריה קטן מנמוך ▁ לגבוה █.","خط تاریخچه کوچک از کم ▁ تا زیاد █.","خط تاريخ صغير من منخفض ▁ إلى مرتفع █."),
    "Home vector currency share in the final tick.": _names("Home vector currency share in the final tick.","Anteil der eigenen Vektorwährung im letzten Tick.","Доля домашней векторной валюты в последнем тике.","Cuota de la moneda vectorial propia en el ciclo final.","Quota della valuta vettoriale nazionale nel tick finale.","最终周期中本国向量货币的份额。","最終時点の自国ベクトル通貨比率。","최종 틱의 자국 벡터 통화 점유율.","अंतिम चक्र में गृह वेक्टर-मुद्रा का हिस्सा।","חלק מטבע הווקטור הביתי במחזור האחרון.","سهم ارز برداری خانگی در تیک پایانی.","حصة عملة المتجه المحلية في الدورة النهائية."),
    "Average across three countries or full scenario run.": _names("Average across three countries or full scenario run.","Durchschnitt über drei Länder oder den ganzen Szenariolauf.","Среднее по трём странам или всему сценарию.","Promedio de tres países o de todo el escenario.","Media su tre paesi o sull'intero scenario.","三个国家或完整情景运行的平均值。","三カ国または全シナリオ実行の平均。","세 국가 또는 전체 시나리오 실행의 평균.","तीन देशों या पूरे परिदृश्य का औसत।","ממוצע על פני שלוש מדינות או ריצת תרחיש מלאה.","میانگین سه کشور یا کل اجرای سناریو.","المتوسط عبر ثلاث دول أو كامل تشغيل السيناريو."),
})

_LONG_ML = {
    "read": _names(
        "Each simulation part explains only the abbreviations and units it uses directly above that part.",
        "Jeder Simulationsteil erklärt direkt darüber nur die Kürzel und Einheiten, die genau dort benutzt werden.",
        "Каждая часть симуляции прямо над собой объясняет только свои сокращения и единицы.",
        "Cada parte de la simulación explica justo encima solo sus propias abreviaturas y unidades.",
        "Ogni parte della simulazione spiega subito sopra solo le proprie abbreviazioni e unità.",
        "每个模拟部分只在本部分上方解释自己使用的缩写和单位。",
        "各シミュレーション部分は、その直前でその部分だけの略号と単位を説明します。",
        "각 시뮬레이션 부분은 바로 위에서 그 부분에 쓰는 약어와 단위만 설명합니다.",
        "हर सिमुलेशन भाग अपने ऊपर केवल उसी भाग के संक्षेप और इकाइयाँ समझाता है।",
        "כל חלק בסימולציה מסביר ממש מעליו רק את הקיצורים והיחידות שלו.",
        "هر بخش شبیه‌سازی درست بالای خود فقط اختصارها و واحدهای همان بخش را توضیح می‌دهد.",
        "كل جزء من المحاكاة يشرح فوقه مباشرةً اختصاراته ووحداته فقط."),
    "currency": _names(
        "This part simulates the three equal Euro-vector currencies as directions on one ring. It asks which vector direction captures action flow; it does not simulate numerical exchange-rate length.",
        "Dieser Teil simuliert die drei gleich langen Euro-Vektorwährungen als Richtungen auf einem Ring. Er fragt, welche Vektorrichtung Handlungsfluss bindet; er simuliert keine Zahlen-Wechselkurslänge.",
        "Эта часть имитирует три равные евро-векторные валюты как направления на одном кольце и спрашивает, какое направление захватывает поток действий; это не численный курс.",
        "Esta parte simula las tres monedas vector-euro iguales como direcciones en un anillo. Pregunta qué dirección captura flujo de acción; no simula longitud de tipo de cambio numérico.",
        "Questa parte simula le tre valute vettore-euro uguali come direzioni su un anello. Chiede quale direzione cattura il flusso d'azione; non simula cambi numerici.",
        "本部分把三种等长欧元向量货币模拟为同一环上的方向，询问哪一方向捕获行动流；它不模拟数字汇率长度。",
        "この部分は三つの同じ長さのユーロ・ベクトル通貨を一つのリング上の方向として模擬し、どの方向が行動流を捉えるかを見ます。数値為替の長さではありません。",
        "이 부분은 길이가 같은 세 유로 벡터 통화를 한 고리의 방향으로 시뮬레이션하고, 어느 방향이 행동 흐름을 잡는지 묻습니다. 숫자 환율 길이는 아닙니다.",
        "यह भाग तीन समान यूरो-वेक्टर मुद्राओं को एक वृत्त की दिशाओं के रूप में सिमुलेट करता है और पूछता है कि कौन-सी दिशा क्रिया प्रवाह पकड़ती है; यह अंक-विनिमय दर नहीं है।",
        "חלק זה מדמה שלושה מטבעות וקטור-אירו שווים ככיוונים על טבעת אחת, ושואל איזה כיוון לוכד זרם פעולה; זה לא שער חליפין מספרי.",
        "این بخش سه ارز بردار-یوروی برابر را به‌صورت جهت‌هایی روی یک حلقه شبیه‌سازی می‌کند و می‌پرسد کدام جهت جریان کنش را جذب می‌کند؛ این نرخ تبدیل عددی نیست.",
        "يحاكي هذا الجزء العملات الثلاث متجه-اليورو المتساوية كاتجاهات على حلقة واحدة ويسأل أي اتجاه يلتقط تدفق الفعل؛ وليس طول سعر صرف رقمي."),
    "labor": _names(
        "This part simulates labor as an angular action. Work creates capacity when labor angle, good/evil axis, popular/unpopular axis and currency direction resonate; otherwise it creates fatigue.",
        "Dieser Teil simuliert Arbeit als Winkelhandlung. Arbeit erzeugt Kapazität, wenn Arbeitswinkel, Gut/Böse-Achse, Beliebt/Unbeliebt-Achse und Währungsrichtung zusammenklingen; sonst erzeugt sie Ermüdung.",
        "Эта часть имитирует труд как угловое действие: мощность возникает при резонансе угла труда, оси добро/зло, оси популярности и валютного направления; иначе возникает усталость.",
        "Esta parte simula el trabajo como acción angular: crea capacidad cuando resuenan ángulo laboral, eje bueno/malo, eje popular/impopular y moneda; si no, crea fatiga.",
        "Questa parte simula il lavoro come azione angolare: crea capacità se angolo del lavoro, asse bene/male, popolare/impopolare e valuta risuonano; altrimenti crea fatica.",
        "本部分把劳动模拟为角度行动；当劳动角、好/恶轴、受欢迎/不受欢迎轴和货币方向共振时产生能力，否则产生疲劳。",
        "この部分は労働を角度行動として扱います。労働角、善悪軸、人気/不人気軸、通貨方向が共鳴すると能力を生み、ずれると疲労を生みます。",
        "이 부분은 노동을 각도 행동으로 봅니다. 노동각, 선/악 축, 인기/비인기 축, 통화 방향이 공명하면 역량이 생기고, 아니면 피로가 생깁니다.",
        "यह भाग श्रम को कोणीय क्रिया मानता है। श्रम कोण, अच्छा/बुरा अक्ष, लोकप्रिय/अलोकप्रिय अक्ष और मुद्रा दिशा मिलें तो क्षमता बनती है, वरना थकान।",
        "חלק זה מדמה עבודה כפעולה זוויתית. כאשר זווית העבודה, ציר טוב/רע, ציר פופולרי/לא פופולרי וכיוון המטבע מהדהדים נוצרת יכולת; אחרת נוצרת עייפות.",
        "این بخش کار را کنش زاویه‌ای می‌بیند. اگر زاویه کار، محور خوب/بد، محور محبوب/نامحبوب و جهت ارز تشدید شوند ظرفیت ایجاد می‌شود؛ وگرنه خستگی.",
        "يحاكي هذا الجزء العمل كفعل زاوي. إذا تناغمت زاوية العمل ومحور الخير/الشر ومحور محبوب/غير محبوب واتجاه العملة نشأت قدرة؛ وإلا نشأ إرهاق."),
    "goods": _names(
        "This part simulates need, supply, satisfaction and vector-Euro price. Price is a count of equal VE units per good, not a stretching of any currency vector.",
        "Dieser Teil simuliert Bedarf, Versorgung, Deckung und Vektor-Euro-Preis. Preis ist eine Anzahl gleicher VE-Einheiten pro Gut, keine Streckung eines Währungsvektors.",
        "Эта часть имитирует потребность, предложение, покрытие и цену вектор-евро. Цена — счёт равных VE на благо, а не растяжение валютного вектора.",
        "Esta parte simula necesidad, oferta, cobertura y precio vector-euro. El precio cuenta unidades VE iguales por bien; no estira ningún vector monetario.",
        "Questa parte simula bisogno, offerta, copertura e prezzo vettore-euro. Il prezzo conta unità VE uguali per bene; non allunga nessun vettore valutario.",
        "本部分模拟需求、供给、满足度和向量欧元价格。价格是每件商品所需等长VE单位的计数，不会拉长任何货币向量。",
        "この部分は需要、供給、充足度、ベクトル・ユーロ価格を模擬します。価格は財あたり同じVE単位の数で、通貨ベクトルを伸ばすものではありません。",
        "이 부분은 필요, 공급, 충족, 벡터-유로 가격을 시뮬레이션합니다. 가격은 재화당 같은 VE 단위의 개수이지 통화 벡터를 늘리는 것이 아닙니다.",
        "यह भाग जरूरत, आपूर्ति, पूर्ति और वेक्टर-यूरो मूल्य को सिमुलेट करता है। मूल्य समान VE इकाइयों की गिनती है, मुद्रा वेक्टर की लंबाई नहीं।",
        "חלק זה מדמה צורך, אספקה, כיסוי ומחיר וקטור-אירו. מחיר הוא ספירת יחידות VE שוות לכל טובין, לא מתיחת וקטור מטבע.",
        "این بخش نیاز، عرضه، پوشش و قیمت بردار-یورو را شبیه‌سازی می‌کند. قیمت شمارش واحدهای برابر VE برای هر کالا است، نه کشیدن بردار ارز.",
        "يحاكي هذا الجزء الحاجة والعرض والتغطية وسعر متجه-اليورو. السعر هو عدد وحدات VE متساوية لكل سلعة، لا تمديد لمتجه العملة."),
    "trade": _names(
        "This part simulates triangular trade and angular work between exporter, importer and trade currency. Trade can work materially while still being symbolically expensive in rad·VE.",
        "Dieser Teil simuliert Dreieckshandel und Umlenkungsarbeit zwischen Exporteur, Importeur und Handelswährung. Handel kann materiell funktionieren und zugleich symbolisch teuer in rad·VE sein.",
        "Эта часть имитирует треугольную торговлю и угловую работу между экспортёром, импортёром и валютой сделки. Торговля может работать материально, но быть символически дорогой в rad·VE.",
        "Esta parte simula comercio triangular y trabajo angular entre exportador, importador y moneda. El comercio puede funcionar materialmente y aun así ser simbólicamente caro en rad·VE.",
        "Questa parte simula commercio triangolare e lavoro angolare tra esportatore, importatore e valuta. Il commercio può funzionare materialmente ma costare simbolicamente in rad·VE.",
        "本部分模拟出口方、进口方和贸易货币之间的三角贸易与角度功。贸易在物质上可行，同时在 rad·VE 中可能象征性昂贵。",
        "この部分は輸出側・輸入側・貿易通貨の三角貿易と角度仕事を模擬します。物質的に可能でも、rad·VEでは象徴的に高くつくことがあります。",
        "이 부분은 수출자, 수입자, 무역 통화 사이의 삼각 무역과 각도 일을 시뮬레이션합니다. 물질적으로 가능해도 rad·VE로는 상징적으로 비쌀 수 있습니다.",
        "यह भाग निर्यातक, आयातक और व्यापार मुद्रा के बीच त्रिकोण व्यापार और कोणीय कार्य को सिमुलेट करता है। व्यापार भौतिक रूप से संभव पर rad·VE में प्रतीकात्मक रूप से महँगा हो सकता है।",
        "חלק זה מדמה מסחר משולש ועבודה זוויתית בין יצואן, יבואן ומטבע מסחר. המסחר יכול לעבוד חומרית אך להיות סמלי יקר ב-rad·VE.",
        "این بخش تجارت مثلثی و کار زاویه‌ای میان صادرکننده، واردکننده و ارز تجارت را شبیه‌سازی می‌کند. تجارت می‌تواند از نظر مادی کار کند اما در rad·VE نمادیناً گران باشد.",
        "يحاكي هذا الجزء تجارة مثلثية وعملاً زاوياً بين المصدّر والمستورد وعملة التجارة. قد تنجح التجارة مادياً لكنها تكون مكلفة رمزياً بوحدة rad·VE."),
    "goals": _names(
        "This part simulates the target system: power, well-being, economic strength and tension. The model does not maximize wealth; it asks which angular order becomes powerful and livable.",
        "Dieser Teil simuliert das Zielsystem: Macht, Wohlbefinden, Wirtschaftsstärke und Spannung. Das Modell maximiert keinen Reichtum; es fragt, welche Winkelordnung machtvoll und lebbar wird.",
        "Эта часть имитирует систему целей: власть, благополучие, экономическую силу и напряжение. Модель не максимизирует богатство; она спрашивает, какой угловой порядок становится сильным и пригодным для жизни.",
        "Esta parte simula el sistema de metas: poder, bienestar, fuerza económica y tensión. No maximiza riqueza; pregunta qué orden angular se vuelve poderoso y habitable.",
        "Questa parte simula il sistema degli obiettivi: potere, benessere, forza economica e tensione. Non massimizza ricchezza; chiede quale ordine angolare diventa potente e vivibile.",
        "本部分模拟目标系统：权力、福祉、经济强度和张力。模型不最大化财富，而询问哪种角度秩序变得有力且宜居。",
        "この部分は目標体系—権力、幸福、経済強度、緊張—を模擬します。富の最大化ではなく、どの角度秩序が強く住みよいかを問います。",
        "이 부분은 목표 체계인 권력, 복지, 경제 강도, 긴장을 시뮬레이션합니다. 부를 최대화하지 않고 어떤 각도 질서가 강하고 살 만한지 묻습니다.",
        "यह भाग लक्ष्य-तंत्र—शक्ति, कल्याण, आर्थिक बल और तनाव—को सिमुलेट करता है। मॉडल धन नहीं बढ़ाता; पूछता है कौन-सा कोण क्रम शक्तिशाली और जीने योग्य बनता है।",
        "חלק זה מדמה את מערכת היעדים: עוצמה, רווחה, חוסן כלכלי ומתח. המודל אינו ממקסם עושר; הוא שואל איזה סדר זוויתי נעשה חזק וראוי לחיים.",
        "این بخش نظام هدف را شبیه‌سازی می‌کند: قدرت، رفاه، توان اقتصادی و تنش. مدل ثروت را بیشینه نمی‌کند؛ می‌پرسد کدام نظم زاویه‌ای قدرتمند و زیست‌پذیر می‌شود.",
        "يحاكي هذا الجزء نظام الأهداف: القوة والرفاه والقوة الاقتصادية والتوتر. لا يعظم النموذج الثروة؛ بل يسأل أي نظام زاوي يصبح قوياً وقابلاً للعيش."),
    "drift": _names(
        "This part simulates slow angle drift. Governments, populations and currencies rotate toward actions that become powerful, successful or livable habits.",
        "Dieser Teil simuliert langsame Winkeldrift. Regierungen, Bevölkerungen und Währungen drehen sich zu Handlungen, die machtvoll, erfolgreich oder lebbar zur Gewohnheit werden.",
        "Эта часть имитирует медленный дрейф углов. Правительства, население и валюты поворачиваются к действиям, которые становятся сильными, успешными или пригодными привычками.",
        "Esta parte simula deriva angular lenta. Gobiernos, poblaciones y monedas giran hacia acciones que se vuelven hábitos poderosos, exitosos o habitables.",
        "Questa parte simula una lenta deriva angolare. Governi, popolazioni e valute ruotano verso azioni che diventano abitudini potenti, riuscite o vivibili.",
        "本部分模拟缓慢角度漂移。政府、人口和货币会转向变得有力、成功或宜居的行动习惯。",
        "この部分はゆっくりした角度ドリフトを模擬します。政府・住民・通貨は、強く成功し住みよい習慣となる行動へ回転します。",
        "이 부분은 느린 각도 표류를 시뮬레이션합니다. 정부, 인구, 통화는 강하고 성공적이며 살 만한 습관이 되는 행동으로 회전합니다.",
        "यह भाग धीमे कोण बहाव को सिमुलेट करता है। सरकार, जनता और मुद्राएँ उन क्रियाओं की ओर घूमती हैं जो शक्तिशाली, सफल या जीने योग्य आदत बनती हैं।",
        "חלק זה מדמה סחיפת זווית איטית. ממשלות, אוכלוסיות ומטבעות מסתובבים אל פעולות שנעשות חזקות, מצליחות או ראויות לחיים.",
        "این بخش رانش کند زاویه را شبیه‌سازی می‌کند. دولت‌ها، مردم و ارزها به سوی کنش‌هایی می‌چرخند که عادت‌های قدرتمند، موفق یا زیست‌پذیر می‌شوند.",
        "يحاكي هذا الجزء انجرافاً زاوياً بطيئاً. الحكومات والسكان والعملات تدور نحو أفعال تصبح عادات قوية أو ناجحة أو قابلة للعيش."),
    "final": _names(
        "This final part reads the whole run through indices and mini-charts. It explains strength and weakness through power, well-being and angular tension, not through rich/poor labels.",
        "Dieser Abschlussteil liest den ganzen Lauf über Indizes und Minikurven. Er erklärt Stärke und Schwäche über Macht, Wohlbefinden und Winkelspannung, nicht über reich/arm.",
        "Финальная часть читает весь запуск через индексы и мини-графики. Сила и слабость объясняются властью, благополучием и угловым напряжением, а не ярлыками богат/беден.",
        "La parte final lee toda la ejecución con índices y minigráficos. Explica fuerza y debilidad por poder, bienestar y tensión angular, no por rico/pobre.",
        "La parte finale legge l'intera corsa con indici e mini grafici. Spiega forza e debolezza tramite potere, benessere e tensione angolare, non con ricco/povero.",
        "最终部分通过指数和迷你图读取整个运行，用权力、福祉和角度张力解释强弱，而不是用富/穷标签。",
        "最終部分は指数とミニ図で全体を読みます。強弱を富/貧ではなく、権力・幸福・角度緊張で説明します。",
        "최종 부분은 지수와 미니 차트로 전체 실행을 읽습니다. 부자/가난이 아니라 권력, 복지, 각도 긴장으로 강약을 설명합니다.",
        "अंतिम भाग सूचकांकों और सूक्ष्म चार्ट से पूरे रन को पढ़ता है। यह अमीर/गरीब नहीं, शक्ति, कल्याण और कोण तनाव से बल-कमज़ोरी समझाता है।",
        "החלק הסופי קורא את כל ההרצה דרך מדדים ותרשימים קטנים. הוא מסביר חוזק וחולשה דרך עוצמה, רווחה ומתח זוויתי, לא דרך עשיר/עני.",
        "بخش پایانی کل اجرا را با شاخص‌ها و نمودارهای کوچک می‌خواند. قوت و ضعف را با قدرت، رفاه و تنش زاویه‌ای توضیح می‌دهد، نه با برچسب فقیر/غنی.",
        "يقرأ الجزء النهائي كامل التشغيل عبر المؤشرات والرسوم الصغيرة. يفسر القوة والضعف بالقوة والرفاه والتوتر الزاوي، لا بتسميات غني/فقير."),
    "tick": _names(
        "A tick may mean a month, quarter or political-market cycle. The cycle runs currency ring, labor, goods, trade, indices, then angle drift and events.",
        "Ein Tick kann Monat, Quartal oder politischer Marktzyklus sein. Die Reihenfolge ist Währungsring, Arbeit, Güter, Handel, Indizes, dann Winkeldrift und Ereignisse.",
        "Тик может означать месяц, квартал или политико-рыночный цикл: валютное кольцо, труд, блага, торговля, индексы, затем дрейф углов и события.",
        "Un ciclo puede ser mes, trimestre o ciclo político-mercado: anillo monetario, trabajo, bienes, comercio, índices, luego deriva y eventos.",
        "Un tick può essere mese, trimestre o ciclo politico-mercato: anello valutario, lavoro, beni, commercio, indici, poi deriva ed eventi.",
        "一个周期可理解为月、季度或政治-市场循环：货币环、劳动、商品、贸易、指数，然后角度漂移和事件。",
        "一つの時点は月・四半期・政治市場サイクルとして読めます。通貨リング、労働、財、貿易、指数、その後に角度ドリフトとイベントです。",
        "틱은 월, 분기 또는 정치-시장 주기로 읽을 수 있습니다. 순서는 통화 고리, 노동, 재화, 무역, 지수, 각도 표류와 사건입니다.",
        "एक टिक महीना, तिमाही या राजनीतिक-बाज़ार चक्र हो सकता है: मुद्रा वृत्त, श्रम, वस्तुएँ, व्यापार, सूचकांक, फिर कोण बहाव और घटनाएँ।",
        "טיק יכול להיות חודש, רבעון או מחזור פוליטי-שוק: טבעת מטבע, עבודה, טובין, מסחר, מדדים, ואז סחיפת זוויות ואירועים.",
        "یک تیک می‌تواند ماه، فصل یا چرخه سیاسی-بازاری باشد: حلقه ارز، کار، کالا، تجارت، شاخص‌ها، سپس رانش زاویه و رویدادها.",
        "يمكن قراءة الدورة كشهر أو ربع سنة أو دورة سياسية-سوقية: حلقة العملة، العمل، السلع، التجارة، المؤشرات، ثم انجراف الزوايا والأحداث."),
    "gallery": _names(
        "The gallery converts the final state into UTF-8 circles, vectors, heat fields, trade arrows and scenario maps; every picture has a scenario reading below it.",
        "Die Galerie übersetzt den Endzustand in UTF-8-Kreise, Vektoren, Hitzefelder, Handelspfeile und Szenariokarten; unter jedem Bild steht eine Szenario-Lesart.",
        "Галерея переводит финальное состояние в круги UTF-8, векторы, тепловые поля, торговые стрелки и карты сценариев; под каждым рисунком есть чтение сценариев.",
        "La galería convierte el estado final en círculos UTF-8, vectores, campos de calor, flechas comerciales y mapas de escenario; bajo cada imagen hay lectura de escenarios.",
        "La galleria converte lo stato finale in cerchi UTF-8, vettori, campi di calore, frecce commerciali e mappe di scenario; sotto ogni immagine c'è una lettura.",
        "图库把最终状态转换为 UTF-8 圆、向量、热场、贸易箭头和情景图；每幅图下方都有情景解读。",
        "ギャラリーは最終状態をUTF-8の円、ベクトル、熱領域、貿易矢印、シナリオ地図に変換し、各図の下に読み方を置きます。",
        "갤러리는 최종 상태를 UTF-8 원, 벡터, 열장, 무역 화살표, 시나리오 지도로 바꾸며 각 그림 아래에 시나리오 해석을 둡니다.",
        "गैलरी अंतिम अवस्था को UTF-8 वृत्तों, वेक्टरों, ताप-क्षेत्रों, व्यापार तीरों और परिदृश्य नक्शों में बदलती है; हर चित्र के नीचे परिदृश्य पढ़ना है।",
        "הגלריה מתרגמת את המצב הסופי לעיגולי UTF-8, וקטורים, שדות חום, חיצי מסחר ומפות תרחיש; מתחת לכל תמונה מופיעה קריאת תרחיש.",
        "گالری وضعیت نهایی را به دایره‌های UTF-8، بردارها، میدان‌های حرارتی، پیکان‌های تجارت و نقشه‌های سناریو تبدیل می‌کند؛ زیر هر تصویر خوانش سناریو آمده است.",
        "يحوّل المعرض الحالة النهائية إلى دوائر UTF-8 ومتجهات وحقول حرارية وأسهم تجارة وخرائط سيناريو؛ وتحت كل صورة قراءة للسيناريو."),
}
_LONG_ML["final_report"] = _LONG_ML["final"]

_RESULT_ML = [
    ("Result: the picture shows only direction", _names(
        "Result: the compass shows direction only. The three Euro vectors have equal length; transactions favor the direction that resonates best with the action angle.",
        "Ergebnis: Der Kompass zeigt nur Richtung. Die drei Euro-Vektoren sind gleich lang; Transaktionen bevorzugen die Richtung, die am besten mit dem Handlungswinkel klingt.",
        "Итог: компас показывает только направление. Три евро-вектора равны по длине; сделки выбирают направление с лучшим резонансом к углу действия.",
        "Resultado: la brújula muestra solo dirección. Los tres euro-vectores tienen la misma longitud; las transacciones favorecen la dirección que mejor resuena con la acción.",
        "Risultato: la bussola mostra solo direzione. I tre euro-vettori hanno uguale lunghezza; le transazioni favoriscono la direzione che risuona meglio con l'azione.",
        "结果：罗盘只显示方向。三个欧元向量等长；交易偏向与行动角最共振的方向。",
        "結果: コンパスは方向だけを示します。三つのユーロ・ベクトルは同じ長さで、取引は行動角と最も共鳴する方向を選びます。",
        "결과: 나침반은 방향만 보여줍니다. 세 유로 벡터의 길이는 같고, 거래는 행동각과 가장 잘 공명하는 방향을 선호합니다.",
        "परिणाम: कम्पास केवल दिशा दिखाता है। तीनों यूरो-वेक्टर समान लंबाई के हैं; लेन-देन उस दिशा को चुनते हैं जो क्रिया-कोण से सबसे अधिक मिलती है।",
        "תוצאה: המצפן מציג כיוון בלבד. שלושת וקטורי האירו שווים באורכם; עסקאות מעדיפות את הכיוון שמהדהד הכי טוב עם זווית הפעולה.",
        "نتیجه: قطب‌نما فقط جهت را نشان می‌دهد. سه بردار یورو هم‌طول‌اند؛ تراکنش‌ها جهتی را ترجیح می‌دهند که با زاویه کنش بیشترین تشدید را دارد.",
        "النتيجة: تعرض البوصلة الاتجاه فقط. متجهات اليورو الثلاثة متساوية الطول؛ وتفضّل المعاملات الاتجاه الأكثر رنيناً مع زاوية الفعل.")),
    ("Result: all three bars have identical length", _names(
        "Result: all bars are equally long. A high price means more equal VE units are counted per good; it never means a currency vector became longer.",
        "Ergebnis: Alle Balken sind gleich lang. Ein hoher Preis bedeutet mehr gleiche VE-Einheiten pro Gut; er bedeutet nie, dass ein Währungsvektor länger wurde.",
        "Итог: все полосы одинаковы. Высокая цена означает больше равных VE за благо, а не удлинение валютного вектора.",
        "Resultado: todas las barras son iguales. Un precio alto cuenta más unidades VE iguales por bien; no alarga ninguna moneda.",
        "Risultato: tutte le barre sono uguali. Un prezzo alto conta più unità VE uguali per bene; non allunga nessuna valuta.",
        "结果：所有条形等长。高价格表示每件商品计入更多等长VE单位，并不表示货币向量变长。",
        "結果: すべての棒は同じ長さです。高価格は財あたり同じVE単位が多く数えられることを意味し、通貨ベクトルが伸びたことではありません。",
        "결과: 모든 막대 길이는 같습니다. 높은 가격은 재화당 같은 VE 단위를 더 많이 세는 것이지 통화 벡터가 길어진 것이 아닙니다.",
        "परिणाम: सभी पट्टियाँ समान लंबाई की हैं। ऊँचा मूल्य प्रति वस्तु अधिक समान VE इकाइयाँ गिनता है; मुद्रा वेक्टर लंबा नहीं होता।",
        "תוצאה: כל העמודות באותו אורך. מחיר גבוה פירושו יותר יחידות VE שוות לכל טובין, לא וקטור מטבע ארוך יותר.",
        "نتیجه: همه نوارها هم‌طول‌اند. قیمت بالا یعنی واحدهای برابر VE بیشتری برای هر کالا شمرده می‌شود؛ نه اینکه بردار ارز بلندتر شده باشد.",
        "النتيجة: كل الأشرطة متساوية الطول. السعر المرتفع يعني عدّ وحدات VE متساوية أكثر لكل سلعة، لا أن متجه العملة صار أطول.")),
    ("Result: this is the strongest axis-pressure example", _names(
        "Result: the drawing shows where good/evil and popular/unpopular axes press hardest against one another. High ODE means the population axis is far from ideal orthogonality.",
        "Ergebnis: Die Zeichnung zeigt, wo Gut/Böse- und Beliebt/Unbeliebt-Achse am stärksten gegeneinander drücken. Hohe ODE heißt: Die Bevölkerungsachse ist weit von idealer Orthogonalität entfernt.",
        "Итог: рисунок показывает, где оси добро/зло и популярно/непопулярно сильнее всего давят друг на друга. Высокая ODE означает далёкость от идеальной ортогональности.",
        "Resultado: el dibujo muestra dónde los ejes bueno/malo y popular/impopular chocan con más fuerza. ODE alto significa que el eje popular está lejos de la ortogonalidad ideal.",
        "Risultato: il disegno mostra dove bene/male e popolare/impopolare premono di più. ODE alto indica distanza dall'ortogonalità ideale.",
        "结果：图形显示好/恶轴与受欢迎/不受欢迎轴压力最大的地方。ODE 高表示人口轴远离理想正交。",
        "結果: 図は善/悪軸と人気/不人気軸が最も強く押し合う場所を示します。ODE が高いほど理想直交から離れています。",
        "결과: 그림은 선/악 축과 인기/비인기 축이 가장 세게 충돌하는 곳을 보여줍니다. ODE가 높으면 이상적 직교에서 멀다는 뜻입니다.",
        "परिणाम: चित्र दिखाता है कि अच्छा/बुरा और लोकप्रिय/अलोकप्रिय अक्ष कहाँ सबसे ज़्यादा दबाव बनाते हैं। ऊँची ODE आदर्श लंबवतता से दूरी है।",
        "תוצאה: הציור מראה היכן צירי טוב/רע ופופולרי/לא פופולרי לוחצים הכי חזק. ODE גבוה פירושו ריחוק מאורתוגונליות אידאלית.",
        "نتیجه: تصویر نشان می‌دهد محورهای خوب/بد و محبوب/نامحبوب کجا بیشترین فشار را دارند. ODE بالا یعنی دوری از عمودیت ایده‌آل.",
        "النتيجة: يوضح الرسم أين يضغط محورا الخير/الشر والمحبوب/غير المحبوب بقوة أكبر. ODE المرتفع يعني ابتعاداً عن التعامد المثالي.")),
    ("Result: the three market actions", _names(
        "Result: buy, sell and work may point to different currencies. A weak sector can be angularly split even when it is not simply poor.",
        "Ergebnis: Kaufen, Verkaufen und Arbeiten können zu verschiedenen Währungen zeigen. Ein schwacher Sektor kann winkelmäßig gespalten sein, ohne einfach arm zu sein.",
        "Итог: покупка, продажа и труд могут указывать на разные валюты. Слабый сектор может быть углово расколот, а не просто беден.",
        "Resultado: comprar, vender y trabajar pueden apuntar a monedas distintas. Un sector débil puede estar dividido angularmente sin ser solo pobre.",
        "Risultato: acquisto, vendita e lavoro possono puntare a valute diverse. Un settore debole può essere diviso angolarmente, non semplicemente povero.",
        "结果：购买、销售和劳动可能指向不同货币。弱部门可能是角度上分裂，而不只是贫穷。",
        "結果: 購入・販売・労働は別々の通貨を向くことがあります。弱い部門は単に貧しいのではなく、角度的に分裂している場合があります。",
        "결과: 구매, 판매, 노동은 서로 다른 통화를 가리킬 수 있습니다. 약한 부문은 단순히 가난한 것이 아니라 각도적으로 갈라질 수 있습니다.",
        "परिणाम: खरीद, बिक्री और काम अलग-अलग मुद्राओं की ओर जा सकते हैं। कमजोर क्षेत्र केवल गरीब नहीं, कोणीय रूप से विभाजित हो सकता है।",
        "תוצאה: קנייה, מכירה ועבודה עשויות להצביע למטבעות שונים. מגזר חלש יכול להיות מפוצל זוויתית, לא רק עני.",
        "نتیجه: خرید، فروش و کار ممکن است به ارزهای مختلف اشاره کنند. یک بخش ضعیف می‌تواند از نظر زاویه‌ای شکافته باشد، نه صرفاً فقیر.",
        "النتيجة: قد يشير الشراء والبيع والعمل إلى عملات مختلفة. قد يكون القطاع الضعيف منقسماً زاوياً، وليس فقيراً فقط.")),
    ("Result: this diagram separates the two main goals", _names(
        "Result: the map separates well-being from power. Upper right means both goals are coherent; upper left means power without enough lived well-being; lower right means livable but weak state/currency power.",
        "Ergebnis: Die Karte trennt Wohlbefinden von Macht. Rechts oben heißt: beide Ziele sind kohärent; links oben heißt: Macht ohne genug gelebtes Wohlbefinden; rechts unten heißt: lebbar, aber schwache Staats-/Währungsmacht.",
        "Итог: карта разделяет благополучие и власть. Верхний правый угол — согласованность обоих; верхний левый — власть без достаточного благополучия; нижний правый — жизнь возможна, но власть валюты слаба.",
        "Resultado: el mapa separa bienestar y poder. Arriba derecha: ambos coherentes; arriba izquierda: poder sin suficiente bienestar vivido; abajo derecha: vida aceptable con poder estatal/monetario débil.",
        "Risultato: la mappa separa benessere e potere. In alto a destra entrambi sono coerenti; in alto a sinistra c'è potere senza benessere sufficiente; in basso a destra vita possibile ma potere debole.",
        "结果：地图区分福祉与权力。右上表示两者协调；左上表示权力强但生活福祉不足；右下表示可生活但国家/货币权力弱。",
        "結果: 地図は幸福と権力を分けます。右上は両方が整合、左上は幸福不足の権力、右下は住みよいが国家/通貨権力が弱い状態です。",
        "결과: 지도는 복지와 권력을 분리합니다. 오른쪽 위는 둘 다 일관되고, 왼쪽 위는 복지 없는 권력, 오른쪽 아래는 살 만하지만 국가/통화 권력이 약한 상태입니다.",
        "परिणाम: नक्शा कल्याण और शक्ति को अलग करता है। दायाँ ऊपर दोनों का मेल, बायाँ ऊपर कल्याण बिना शक्ति, दायाँ नीचे जीने योग्य पर कमजोर राज्य/मुद्रा शक्ति।",
        "תוצאה: המפה מפרידה רווחה מעוצמה. ימין למעלה פירושו שני היעדים קוהרנטיים; שמאל למעלה עוצמה בלי מספיק רווחה; ימין למטה חיים סבירים עם כוח מדינה/מטבע חלש.",
        "نتیجه: نقشه رفاه را از قدرت جدا می‌کند. بالا-راست یعنی هر دو منسجم‌اند؛ بالا-چپ قدرت بدون رفاه کافی؛ پایین-راست زیست‌پذیر اما با قدرت دولت/ارز ضعیف.",
        "النتيجة: تفصل الخريطة الرفاه عن القوة. أعلى اليمين يعني اتساق الهدفين؛ أعلى اليسار قوة بلا رفاه كافٍ؛ أسفل اليمين قابلية عيش مع قوة دولة/عملة ضعيفة.")),
    ("Result: the carpet shows whether tension", _names(
        "Result: the carpet shows whether tension is temporary or structural. Long yellow/red bands mean persistent mismatch between government, population, currency and action angles.",
        "Ergebnis: Der Teppich zeigt, ob Spannung vorübergehend oder strukturell ist. Lange gelb/rote Bänder bedeuten dauerhafte Fehlpassung zwischen Regierung, Bevölkerung, Währung und Handlung.",
        "Итог: ковёр показывает, временно ли напряжение или структурно. Длинные жёлто-красные полосы означают устойчивое несовпадение углов правительства, населения, валюты и действия.",
        "Resultado: la alfombra muestra si la tensión es temporal o estructural. Bandas largas amarillas/rojas indican desajuste persistente entre gobierno, población, moneda y acción.",
        "Risultato: il tappeto mostra se la tensione è temporanea o strutturale. Fasce gialle/rosse lunghe indicano disallineamento persistente tra governo, popolazione, valuta e azione.",
        "结果：地毯显示张力是暂时还是结构性的。长黄/红带表示政府、人口、货币和行动角长期错配。",
        "結果: カーペットは緊張が一時的か構造的かを示します。長い黄/赤帯は政府・住民・通貨・行動角の持続的な不一致を意味します。",
        "결과: 카펫은 긴장이 일시적인지 구조적인지 보여줍니다. 긴 노랑/빨강 띠는 정부, 인구, 통화, 행동 각도의 지속적 불일치를 뜻합니다.",
        "परिणाम: कालीन दिखाता है तनाव अस्थायी है या संरचनात्मक। लंबी पीली/लाल पट्टियाँ सरकार, जनता, मुद्रा और क्रिया कोणों का स्थायी असंगति दिखाती हैं।",
        "תוצאה: השטיח מראה אם המתח זמני או מבני. רצועות צהובות/אדומות ארוכות מציינות חוסר התאמה מתמשך בין ממשלה, אוכלוסייה, מטבע ופעולה.",
        "نتیجه: فرش نشان می‌دهد تنش موقتی است یا ساختاری. نوارهای زرد/قرمز بلند یعنی ناسازگاری پایدار میان دولت، مردم، ارز و زاویه کنش.",
        "النتيجة: يبين البساط هل التوتر مؤقت أم بنيوي. الأشرطة الصفراء/الحمراء الطويلة تعني عدم توافق مستمراً بين الحكومة والسكان والعملة وزوايا الفعل.")),
    ("Result: each arrow lists quantity/angular work", _names(
        "Result: each arrow combines traded quantity with angular work. A route may move few goods but still be expensive when it requires much rotation in rad·VE.",
        "Ergebnis: Jeder Pfeil verbindet Handelsmenge mit Umlenkungsarbeit. Eine Route kann wenig Güter bewegen und trotzdem teuer sein, wenn sie viel Drehung in rad·VE braucht.",
        "Итог: каждая стрелка соединяет объём торговли и угловую работу. Маршрут может перевозить мало благ, но быть дорогим при большой ротации в rad·VE.",
        "Resultado: cada flecha une cantidad comerciada y trabajo angular. Una ruta puede mover pocos bienes y aun así ser cara si exige mucha rotación en rad·VE.",
        "Risultato: ogni freccia unisce quantità scambiata e lavoro angolare. Una rotta può muovere pochi beni ma essere cara se richiede molta rotazione in rad·VE.",
        "结果：每个箭头同时表示交易量和角度功。路线可能货量小，但若需要大量 rad·VE 旋转仍然昂贵。",
        "結果: 各矢印は取引量と角度仕事を結びます。財の量が少なくても、rad·VE の回転が大きければ高コストです。",
        "결과: 각 화살표는 거래량과 각도 일을 함께 보여줍니다. 물량이 적어도 rad·VE 회전이 크면 비쌉니다.",
        "परिणाम: हर तीर व्यापार मात्रा और कोणीय कार्य जोड़ता है। मार्ग कम वस्तुएँ ले जाए फिर भी rad·VE में अधिक घुमाव से महँगा हो सकता है।",
        "תוצאה: כל חץ מחבר כמות מסחר ועבודה זוויתית. נתיב יכול להעביר מעט טובין אך להיות יקר אם דרושה הרבה סיבוביות ב-rad·VE.",
        "نتیجه: هر پیکان مقدار تجارت و کار زاویه‌ای را ترکیب می‌کند. مسیر ممکن است کالای کمی جابه‌جا کند اما با چرخش زیاد در rad·VE گران باشد.",
        "النتيجة: يجمع كل سهم كمية التجارة والعمل الزاوي. قد يحرك المسار سلعاً قليلة لكنه يكون مكلفاً إذا احتاج دوراناً كبيراً بوحدة rad·VE.")),
    ("Result: the trail is a history", _names(
        "Result: the trails show history of direction changes, not changes of Euro length. Stable trails mean preserved currency identity; zigzags mean unstable angular pulls.",
        "Ergebnis: Die Spuren zeigen Richtungsänderungen, nicht Änderungen der Euro-Länge. Stabile Spuren bedeuten erhaltene Währungsidentität; Zickzack heißt instabiler Winkelzug.",
        "Итог: следы показывают историю направлений, а не изменение длины евро. Стабильные следы — сохранённая идентичность; зигзаги — неустойчивые угловые тяги.",
        "Resultado: los rastros muestran cambios de dirección, no de longitud euro. Rastros estables preservan identidad; zigzags indican tirones angulares inestables.",
        "Risultato: le tracce mostrano cambi di direzione, non di lunghezza dell'euro. Tracce stabili preservano identità; zigzag indicano trazioni angolari instabili.",
        "结果：轨迹显示方向变化历史，而不是欧元长度变化。稳定轨迹表示货币身份保持；锯齿表示角度拉力不稳。",
        "結果: 軌跡は方向変化の履歴で、ユーロ長の変化ではありません。安定した軌跡は通貨同一性の維持、ジグザグは不安定な角度引力です。",
        "결과: 흔적은 방향 변화의 역사이지 유로 길이 변화가 아닙니다. 안정된 흔적은 통화 정체성 보존, 지그재그는 불안정한 각도 당김입니다.",
        "परिणाम: पथ दिशा-परिवर्तन का इतिहास है, यूरो लंबाई का नहीं। स्थिर पथ मुद्रा पहचान बचाते हैं; ज़िगज़ैग अस्थिर कोण खिंचाव है।",
        "תוצאה: העקבות הן היסטוריה של שינויי כיוון, לא של אורך אירו. עקבות יציבים משמרים זהות מטבע; זיגזג מציין משיכות זוויתיות לא יציבות.",
        "نتیجه: ردها تاریخ تغییر جهت‌اند، نه تغییر طول یورو. رد پایدار یعنی هویت ارز حفظ شده؛ زیگزاگ یعنی کشش زاویه‌ای ناپایدار.",
        "النتيجة: الآثار تاريخ تغيّر الاتجاه، لا تغيّر طول اليورو. الآثار المستقرة تحفظ هوية العملة؛ والتعرج يعني شدوداً زاوية غير مستقرة.")),
    ("Result: the mosaic translates final need coverage", _names(
        "Result: the mosaic shows final need coverage. Green means covered and usable; red means missing coverage from shortage, trade friction, high VE count or angular mismatch.",
        "Ergebnis: Das Mosaik zeigt die endgültige Bedarfsdeckung. Grün heißt gedeckt und nutzbar; rot heißt fehlende Deckung durch Mangel, Handelsreibung, hohe VE-Anzahl oder Winkelbruch.",
        "Итог: мозаика показывает итоговое покрытие потребностей. Зелёный — покрыто и пригодно; красный — нехватка из-за дефицита, трения торговли, высокой VE-цены или углового разрыва.",
        "Resultado: el mosaico muestra la cobertura final de necesidades. Verde: cubierto y usable; rojo: falta por escasez, fricción comercial, alto conteo VE o desajuste angular.",
        "Risultato: il mosaico mostra la copertura finale dei bisogni. Verde: coperto e utilizzabile; rosso: mancanza per scarsità, attrito commerciale, alto conteggio VE o disallineamento angolare.",
        "结果：马赛克显示最终需求覆盖。绿色表示已覆盖且可用；红色表示因短缺、贸易摩擦、高VE计数或角度错配而缺口。",
        "結果: モザイクは最終需要充足を示します。緑は充足して使える、赤は不足・貿易摩擦・高VE数・角度不一致による欠落です。",
        "결과: 모자이크는 최종 필요 충족을 보여줍니다. 초록은 충족되고 사용 가능함, 빨강은 부족, 무역 마찰, 높은 VE 개수 또는 각도 불일치로 인한 결핍입니다.",
        "परिणाम: मोज़ेक अंतिम जरूरत पूर्ति दिखाता है। हरा ढका और उपयोगी है; लाल कमी, व्यापार घर्षण, ऊँची VE गिनती या कोण असंगति से कमी है।",
        "תוצאה: הפסיפס מציג כיסוי צורך סופי. ירוק פירושו מכוסה ושמיש; אדום פירושו מחסור עקב נדירות, חיכוך מסחר, ספירת VE גבוהה או אי התאמה זוויתית.",
        "نتیجه: موزاییک پوشش نهایی نیاز را نشان می‌دهد. سبز یعنی پوشش و قابلیت استفاده؛ قرمز یعنی کمبود به‌علت ندرت، اصطکاک تجارت، شمارش VE بالا یا ناسازگاری زاویه‌ای.",
        "النتيجة: تعرض الفسيفساء تغطية الحاجة النهائية. الأخضر يعني مغطى وقابل للاستعمال؛ الأحمر يعني نقصاً بسبب ندرة أو احتكاك تجاري أو عدّ VE عالٍ أو عدم توافق زاوي.")),
    ("Result: each wave is the final vector-Euro count", _names(
        "Result: price waves show equal VE units counted per sector. Peaks are not longer Euros; they mark scarcity, angular mismatch or local currency distance.",
        "Ergebnis: Preiswellen zeigen gezählte gleiche VE-Einheiten je Sektor. Spitzen sind keine längeren Euros; sie markieren Mangel, Winkelbruch oder Distanz zur lokalen Währung.",
        "Итог: ценовые волны показывают равные VE, считанные по секторам. Пики — не длинные евро, а дефицит, угловое несовпадение или дистанция к местной валюте.",
        "Resultado: las olas de precio muestran unidades VE iguales contadas por sector. Los picos no son euros más largos; indican escasez, desajuste angular o distancia monetaria local.",
        "Risultato: le onde di prezzo mostrano unità VE uguali contate per settore. I picchi non sono euro più lunghi; indicano scarsità, disallineamento o distanza dalla valuta locale.",
        "结果：价格波显示各部门计入的等长VE单位。峰值不是更长的欧元，而是短缺、角度错配或本地货币距离。",
        "結果: 価格波は部門ごとに数えられる同じVE単位を示します。ピークは長いユーロではなく、不足・角度不一致・地域通貨距離です。",
        "결과: 가격 파동은 부문별로 세어진 같은 VE 단위를 보여줍니다. 봉우리는 더 긴 유로가 아니라 부족, 각도 불일치, 지역 통화 거리입니다.",
        "परिणाम: मूल्य तरंगें प्रत्येक क्षेत्र में गिनी गई समान VE इकाइयाँ दिखाती हैं। शिखर लंबे यूरो नहीं, अभाव, कोण असंगति या स्थानीय मुद्रा दूरी हैं।",
        "תוצאה: גלי מחיר מציגים יחידות VE שוות שנספרות לפי מגזר. שיאים אינם אירו ארוכים יותר; הם מציינים מחסור, אי התאמה זוויתית או מרחק מטבע מקומי.",
        "نتیجه: موج‌های قیمت واحدهای برابر VE شمرده‌شده در هر بخش را نشان می‌دهند. قله‌ها یوروی بلندتر نیستند؛ نشانه کمبود، ناسازگاری زاویه‌ای یا فاصله ارز محلی‌اند.",
        "النتيجة: تظهر موجات السعر وحدات VE المتساوية المحسوبة لكل قطاع. القمم ليست يورو أطول، بل ندرة أو عدم توافق زاوي أو مسافة عن العملة المحلية.")),
    ("Result: the quadrant picture", _names(
        "Result: the quadrants give a political-economic reading: resonance combines power and well-being; power lock dominates lived welfare; well-being island is livable but weak; fracture has no stable angular shape.",
        "Ergebnis: Die Quadranten geben eine politisch-ökonomische Lesart: Resonanz verbindet Macht und Wohlbefinden; Power Lock dominiert gelebtes Wohl; Well-being Island ist lebbar, aber schwach; Fracture hat keine stabile Winkelform.",
        "Итог: квадранты дают политико-экономическое чтение: резонанс соединяет власть и благополучие; power lock доминирует над жизненным благом; остров благополучия пригоден, но слаб; fracture не имеет устойчивой формы.",
        "Resultado: los cuadrantes dan lectura político-económica: resonancia une poder y bienestar; power lock domina el bienestar vivido; isla de bienestar es habitable pero débil; fractura no tiene forma angular estable.",
        "Risultato: i quadranti leggono politicamente l'economia: risonanza unisce potere e benessere; power lock domina il benessere vissuto; isola di benessere è vivibile ma debole; frattura non ha forma stabile.",
        "结果：象限给出政治经济解读：共振结合权力与福祉；权力锁定压过生活福祉；福祉岛可生活但弱；断裂没有稳定角度形态。",
        "結果: 象限は政治経済の読みを与えます。共鳴は権力と幸福を結び、権力ロックは生活幸福を支配し、幸福島は住みよいが弱く、分裂は安定した角度形を持ちません。",
        "결과: 사분면은 정치경제적 해석입니다. 공명은 권력과 복지를 결합하고, 권력 잠금은 체감 복지를 압도하며, 복지 섬은 살 만하지만 약하고, 균열은 안정된 각도 형상이 없습니다.",
        "परिणाम: चतुर्थांश राजनीतिक-आर्थिक पढ़ाई देते हैं: अनुनाद शक्ति और कल्याण जोड़ता है; power lock जीवन-कल्याण दबाता है; कल्याण द्वीप जीने योग्य पर कमजोर है; fracture स्थिर कोण रूप नहीं रखता।",
        "תוצאה: הרבעונים נותנים קריאה פוליטית-כלכלית: תהודה מחברת עוצמה ורווחה; נעילת כוח גוברת על רווחה חיה; אי רווחה ראוי לחיים אך חלש; שבר חסר צורה זוויתית יציבה.",
        "نتیجه: ربع‌ها خوانش سیاسی-اقتصادی می‌دهند: تشدید قدرت و رفاه را جمع می‌کند؛ قفل قدرت رفاه زیسته را غلبه می‌دهد؛ جزیره رفاه زیست‌پذیر اما ضعیف است؛ گسست شکل زاویه‌ای پایدار ندارد.",
        "النتيجة: تعطي الأرباع قراءة سياسية-اقتصادية: الرنين يجمع القوة والرفاه؛ قفل القوة يهيمن على الرفاه المعيش؛ جزيرة الرفاه قابلة للعيش لكنها ضعيفة؛ الكسر لا يملك شكلاً زاوياً مستقراً.")),
    ("Result: this final table actually runs", _names(
        "Result: the table runs the same model under several scenario climates. It is not a moral ranking; it shows which climate produces more well-being, power, strength or tension while |€⃗| remains 1 VE.",
        "Ergebnis: Die Tabelle lässt dasselbe Modell unter mehreren Szenarioklimata laufen. Sie ist keine moralische Rangliste; sie zeigt, welches Klima mehr Wohlbefinden, Macht, Stärke oder Spannung erzeugt, während |€⃗| bei 1 VE bleibt.",
        "Итог: таблица запускает ту же модель в разных климатах сценариев. Это не моральный рейтинг; она показывает, где больше благополучия, власти, силы или напряжения при |€⃗|=1 VE.",
        "Resultado: la tabla ejecuta el mismo modelo bajo varios climas de escenario. No es ranking moral; muestra qué clima produce más bienestar, poder, fuerza o tensión mientras |€⃗| sigue en 1 VE.",
        "Risultato: la tabella esegue lo stesso modello in vari climi di scenario. Non è una classifica morale; mostra quale clima genera più benessere, potere, forza o tensione mentre |€⃗| resta 1 VE.",
        "结果：表格在不同情景气候下运行同一模型。这不是道德排名；它显示在 |€⃗| 保持 1 VE 时，哪种气候产生更多福祉、权力、强度或张力。",
        "結果: 表は同じモデルを複数のシナリオ気候で動かします。道徳順位ではなく、|€⃗|=1 VE のまま、どの気候が幸福・権力・強度・緊張を多く生むかを示します。",
        "결과: 표는 같은 모델을 여러 시나리오 기후에서 실행합니다. 도덕 순위가 아니며, |€⃗|=1 VE가 유지되는 동안 어떤 기후가 복지, 권력, 강도, 긴장을 더 만드는지 보여줍니다.",
        "परिणाम: तालिका उसी मॉडल को कई परिदृश्य-जलवायुओं में चलाती है। यह नैतिक रैंकिंग नहीं; दिखाती है कि |€⃗|=1 VE रहते किस जलवायु से अधिक कल्याण, शक्ति, बल या तनाव बनता है।",
        "תוצאה: הטבלה מריצה את אותו מודל בכמה אקלים-תרחיש. זו אינה דרגה מוסרית; היא מראה איזה אקלים יוצר יותר רווחה, עוצמה, חוזק או מתח בזמן ש-|€⃗| נשאר 1 VE.",
        "نتیجه: جدول همان مدل را در چند اقلیم سناریویی اجرا می‌کند. رتبه‌بندی اخلاقی نیست؛ نشان می‌دهد با ثابت ماندن |€⃗|=1 VE کدام اقلیم رفاه، قدرت، توان یا تنش بیشتری می‌سازد.",
        "النتيجة: يشغّل الجدول النموذج نفسه تحت عدة مناخات سيناريو. ليس ترتيباً أخلاقياً؛ بل يبين أي مناخ ينتج رفاهاً أو قوة أو متانة أو توتراً أكثر مع بقاء |€⃗|=1 VE.")),
]

_SCENARIO_MEANING_ML = _names(
    "Scenario meaning: resonance reduces visible conflict; power pursuit pulls vectors toward state currency; well-being pursuit pulls them toward lived popularity; scarcity and fragmentation make red/yellow tension signs thicker.",
    "Szenario-Bedeutung: Resonanz reduziert sichtbaren Konflikt; Machtstreben zieht Vektoren zur Staatswährung; Wohlbefinden zieht sie zur gelebten Beliebtheit; Mangel und Zersplitterung verdicken rote/gelbe Spannungszeichen.",
    "Смысл сценариев: резонанс уменьшает видимый конфликт; стремление к власти тянет векторы к государственной валюте; благополучие тянет к живой популярности; дефицит и фрагментация усиливают жёлто-красное напряжение.",
    "Sentido de escenarios: la resonancia reduce conflicto visible; la búsqueda de poder tira vectores hacia la moneda estatal; el bienestar tira hacia popularidad vivida; escasez y fragmentación engrosan señales rojas/amarillas.",
    "Significato degli scenari: la risonanza riduce il conflitto visibile; il potere tira i vettori verso la valuta statale; il benessere verso la popolarità vissuta; scarsità e frammentazione ispessiscono rosso/giallo.",
    "情景含义：共振减少可见冲突；权力追求把向量拉向国家货币；福祉追求把它们拉向生活中的受欢迎；稀缺和碎片化会加厚红/黄张力信号。",
    "シナリオの意味: 共鳴は見える対立を減らし、権力志向はベクトルを国家通貨へ、幸福志向は生活上の人気へ引き、希少性と分断は赤/黄の緊張を強めます。",
    "시나리오 의미: 공명은 보이는 갈등을 줄이고, 권력 추구는 벡터를 국가 통화 쪽으로, 복지 추구는 체감 인기 쪽으로 당기며, 부족과 분절은 빨강/노랑 긴장 신호를 키웁니다.",
    "परिदृश्य अर्थ: अनुनाद दृश्य संघर्ष घटाता है; शक्ति-प्रयास वेक्टरों को राज्य मुद्रा की ओर खींचता है; कल्याण उन्हें जीवित लोकप्रियता की ओर; अभाव और विखंडन लाल/पीले तनाव चिह्न बढ़ाते हैं।",
    "משמעות תרחיש: תהודה מצמצמת קונפליקט נראה; חתירה לעוצמה מושכת וקטורים למטבע המדינה; רווחה מושכת לפופולריות חיה; מחסור ופיצול מעבים סימני מתח אדומים/צהובים.",
    "معنای سناریو: تشدید تعارض دیدنی را کم می‌کند؛ پیگیری قدرت بردارها را به ارز دولت می‌کشد؛ پیگیری رفاه به محبوبیت زیسته؛ کمبود و پراکندگی نشانه‌های تنش زرد/قرمز را ضخیم می‌کند.",
    "معنى السيناريو: الرنين يقلل الصراع المرئي؛ السعي إلى القوة يسحب المتجهات نحو عملة الدولة؛ السعي إلى الرفاه يسحبها نحو الشعبية المعيشة؛ الندرة والتشظي يزيدان إشارات التوتر الصفراء/الحمراء.")


def _long_generic(lang: str, key: str, en: str) -> str:  # type: ignore[no-redef]
    lang = normalize_lang(lang)
    if key in LONG_BASE:
        return LONG_BASE[key][lang]
    if key in _LONG_ML:
        return _LONG_ML[key][lang]
    if key == "scenario_meaning" or en.startswith("Scenario meaning:"):
        return _SCENARIO_MEANING_ML[lang]
    if key == "result" or en.startswith("Result:"):
        return _localized_result(lang, en)
    return en if lang == "en" else (COMMON.get(en, {}).get(lang) if isinstance(COMMON.get(en), dict) else en)


def _localized_result(lang: str, en: str) -> str:
    lang = normalize_lang(lang)
    if lang == "en":
        return en
    for prefix, variants in _RESULT_ML:
        if en.startswith(prefix):
            return variants[lang]
    if ":" in en:
        body = en.split(":", 1)[1].strip()
        result_word = PH.get(lang, {}).get("result", "Result")
        return result_word + ": " + body
    return en


def _localized_trade_sum(lang: str, en: str) -> str:
    if lang == "en":
        return en
    # Expected: Trade sum: X goods units; angular work sum: Y rad·VE. ...
    x = "?"; y = "?"
    try:
        rest = en.split("Trade sum:", 1)[1].strip()
        x = rest.split("goods units", 1)[0].strip()
        y = rest.split("angular work sum:", 1)[1].split("rad·VE", 1)[0].strip()
    except Exception:
        pass
    return _names(
        en,
        f"Handelssumme: {x} Gütereinheiten; Summe Umlenkungsarbeit: {y} rad·VE. Hohe UA heißt: Handel ist möglich, braucht aber mehr symbolische und institutionelle Drehung.",
        f"Сумма торговли: {x} единиц благ; сумма угловой работы: {y} rad·VE. Высокая UA означает, что торговля возможна, но требует больше символического и институционального поворота.",
        f"Suma comercial: {x} unidades de bienes; suma de trabajo angular: {y} rad·VE. UA alto significa que el comercio es posible, pero exige más giro simbólico e institucional.",
        f"Somma commerciale: {x} unità di beni; somma del lavoro angolare: {y} rad·VE. UA alto significa commercio possibile ma con più rotazione simbolica e istituzionale.",
        f"贸易总量：{x} 商品单位；角度功总和：{y} rad·VE。UA 高表示贸易仍可行，但需要更多象征性和制度性旋转。",
        f"貿易合計: {x} 財単位; 角度仕事合計: {y} rad·VE。UA が高いほど、貿易は可能でも象徴的・制度的回転が多く必要です。",
        f"무역 합계: {x} 재화 단위; 각도 일 합계: {y} rad·VE. UA가 높으면 무역은 가능하지만 상징적·제도적 회전이 더 필요합니다.",
        f"व्यापार योग: {x} वस्तु इकाइयाँ; कोणीय कार्य योग: {y} rad·VE। ऊँचा UA बताता है कि व्यापार संभव है, पर अधिक प्रतीकात्मक और संस्थागत घुमाव चाहिए।",
        f"סכום מסחר: {x} יחידות טובין; סכום עבודה זוויתית: {y} rad·VE. UA גבוה אומר שמסחר אפשרי אך דורש יותר סיבוב סמלי ומוסדי.",
        f"جمع تجارت: {x} واحد کالا؛ جمع کار زاویه‌ای: {y} rad·VE. UA بالا یعنی تجارت ممکن است اما چرخش نمادین و نهادی بیشتری می‌خواهد.",
        f"مجموع التجارة: {x} وحدات سلع؛ مجموع العمل الزاوي: {y} rad·VE. UA المرتفع يعني أن التجارة ممكنة لكنها تحتاج دوراناً رمزياً ومؤسسياً أكبر.")[lang]


def _localized_interpretation(lang: str, en: str) -> str:
    lang = normalize_lang(lang)
    if lang == "en":
        return en
    # Extract the four main codes from the fixed English template.
    codes = []
    try:
        a = en.split("Interpretation of this run:", 1)[1]
        codes.append(a.split(" has the strongest final well-being", 1)[0].strip())
        b = a.split(" has the strongest final well-being,", 1)[1]
        codes.append(b.split(" has the strongest power index", 1)[0].strip())
        c = b.split(" has the strongest power index, and", 1)[1]
        codes.append(c.split(" carries the highest tension degree", 1)[0].strip())
        d = c.split("The strongest currency by power attachment is", 1)[1]
        codes.append(d.split(".", 1)[0].strip())
    except Exception:
        codes = ["?", "?", "?", "?"]
    w, p, t, cur = codes
    return _names(
        en,
        f"Interpretation dieses Laufs: {w} hat das stärkste End-Wohlbefinden, {p} den stärksten Machtindex, und {t} trägt den höchsten Spannungsgrad. Die stärkste Währung nach Machtbindung ist {cur}. Alle Währungen bleiben exakt 1 VE lang; die Unterschiede entstehen aus Winkelpassung, Drift und gebundenem Handlungsfluss.",
        f"Интерпретация запуска: у {w} самое сильное итоговое благополучие, у {p} самый сильный индекс власти, а {t} несёт наибольшее напряжение. Самая сильная валюта по привязке власти — {cur}. Все валюты остаются длиной ровно 1 VE; различия возникают из углового соответствия, дрейфа и захваченного потока действий.",
        f"Interpretación de la ejecución: {w} tiene el mayor bienestar final, {p} el mayor índice de poder y {t} el mayor grado de tensión. La moneda más fuerte por vínculo de poder es {cur}. Todas las monedas mantienen longitud exacta de 1 VE; las diferencias nacen de ajuste angular, deriva y flujo de acción captado.",
        f"Interpretazione della corsa: {w} ha il benessere finale più forte, {p} l'indice di potere più forte e {t} il grado di tensione più alto. La valuta più forte per legame di potere è {cur}. Tutte le valute restano esattamente lunghe 1 VE; le differenze vengono da adattamento angolare, deriva e flusso d'azione catturato.",
        f"本次运行解读：{w} 的最终福祉最强，{p} 的权力指数最强，{t} 的张力程度最高。按权力绑定最强的货币是 {cur}。所有货币长度仍精确为 1 VE；差异来自角度匹配、漂移和被捕获的行动流。",
        f"この実行の解釈: {w} は最終幸福が最も強く、{p} は権力指数が最も強く、{t} は緊張度が最も高いです。権力結合で最も強い通貨は {cur} です。全通貨の長さは正確に 1 VE のままで、差は角度適合・ドリフト・捕捉した行動流から生じます。",
        f"이번 실행 해석: {w}는 최종 복지가 가장 강하고, {p}는 권력 지수가 가장 강하며, {t}는 긴장도가 가장 높습니다. 권력 결속 기준 가장 강한 통화는 {cur}입니다. 모든 통화 길이는 정확히 1 VE로 유지되고 차이는 각도 적합, 표류, 포착된 행동 흐름에서 나옵니다.",
        f"इस रन की व्याख्या: {w} का अंतिम कल्याण सबसे मजबूत है, {p} का शक्ति सूचकांक सबसे मजबूत है, और {t} का तनाव स्तर सबसे ऊँचा है। शक्ति-बाँध से सबसे मजबूत मुद्रा {cur} है। सभी मुद्राएँ ठीक 1 VE लंबी रहती हैं; अंतर कोण-मेल, बहाव और पकड़े गए क्रिया प्रवाह से बनते हैं।",
        f"פירוש ההרצה: ל-{w} הרווחה הסופית החזקה ביותר, ל-{p} מדד העוצמה החזק ביותר, ו-{t} נושא את דרגת המתח הגבוהה ביותר. המטבע החזק ביותר לפי קשר עוצמה הוא {cur}. כל המטבעות נשארים בדיוק באורך 1 VE; ההבדלים נובעים מהתאמת זוויות, סחיפה וזרם פעולה שנלכד.",
        f"تفسیر اجرا: {w} قوی‌ترین رفاه نهایی را دارد، {p} قوی‌ترین شاخص قدرت را دارد و {t} بالاترین درجه تنش را حمل می‌کند. قوی‌ترین ارز از نظر پیوند قدرت {cur} است. طول همه ارزها دقیقاً 1 VE می‌ماند؛ تفاوت‌ها از سازگاری زاویه، رانش و جریان کنش جذب‌شده می‌آیند.",
        f"تفسير التشغيل: لدى {w} أقوى رفاه نهائي، ولدى {p} أقوى مؤشر قوة، وتحمل {t} أعلى درجة توتر. أقوى عملة بحسب ارتباط القوة هي {cur}. تبقى كل العملات بطول 1 VE تماماً؛ والفروق تأتي من ملاءمة الزوايا والانجراف وتدفق الفعل الملتقط.")[lang]


def _localized_scenario_reading(lang: str, en: str) -> str:
    lang = normalize_lang(lang)
    if lang == "en":
        return en
    # Keep the dynamic scenario names if extraction succeeds.
    try:
        focus = en.split("Scenario reading for ", 1)[1].split(":", 1)[0]
    except Exception:
        focus = ""
    return _names(
        en,
        f"Szenario-Lesart für {focus}: Resonanz senkt sichtbaren Konflikt; Machtstreben zieht Vektoren zur Staatswährung; Wohlbefinden zieht zu gelebter Beliebtheit; Mangel und Zersplitterung verstärken gelb/rote Spannungssignale.",
        f"Чтение сценария для {focus}: резонанс снижает видимый конфликт; стремление к власти тянет векторы к государственной валюте; благополучие тянет к живой популярности; дефицит и фрагментация усиливают жёлто-красное напряжение.",
        f"Lectura de escenario para {focus}: la resonancia reduce conflicto visible; la búsqueda de poder tira vectores hacia la moneda estatal; el bienestar tira hacia la popularidad vivida; escasez y fragmentación intensifican señales amarillas/rojas.",
        f"Lettura di scenario per {focus}: la risonanza riduce il conflitto visibile; il potere tira i vettori verso la valuta statale; il benessere verso la popolarità vissuta; scarsità e frammentazione intensificano i segnali giallo/rossi.",
        f"{focus} 的情景解读：共振减少可见冲突；权力追求把向量拉向国家货币；福祉追求拉向生活中的受欢迎；稀缺与碎片化会增强黄/红张力信号。",
        f"{focus} のシナリオ解釈: 共鳴は可視的対立を減らし、権力志向はベクトルを国家通貨へ、幸福志向は生活上の人気へ引き、希少性と分断は黄/赤の緊張を強めます。",
        f"{focus}에 대한 시나리오 해석: 공명은 보이는 갈등을 줄이고, 권력 추구는 벡터를 국가 통화 쪽으로, 복지 추구는 체감 인기 쪽으로 당기며, 부족과 분절은 노랑/빨강 긴장 신호를 키웁니다.",
        f"{focus} के लिए परिदृश्य-पढ़ाई: अनुनाद दृश्य संघर्ष घटाता है; शक्ति-प्रयास वेक्टरों को राज्य मुद्रा की ओर खींचता है; कल्याण जीवित लोकप्रियता की ओर; अभाव और विखंडन पीले/लाल तनाव संकेत बढ़ाते हैं।",
        f"קריאת תרחיש עבור {focus}: תהודה מפחיתה קונפליקט נראה; חתירה לעוצמה מושכת וקטורים למטבע המדינה; רווחה מושכת לפופולריות חיה; מחסור ופיצול מגבירים סימני מתח צהובים/אדומים.",
        f"خوانش سناریو برای {focus}: تشدید تعارض دیدنی را کم می‌کند؛ پیگیری قدرت بردارها را به ارز دولت می‌کشد؛ رفاه به محبوبیت زیسته؛ کمبود و پراکندگی نشانه‌های زرد/قرمز تنش را تقویت می‌کنند.",
        f"قراءة السيناريو لـ {focus}: الرنين يقلل الصراع المرئي؛ السعي إلى القوة يسحب المتجهات نحو عملة الدولة؛ الرفاه يسحب نحو الشعبية المعيشة؛ الندرة والتشظي يزيدان إشارات التوتر الصفراء/الحمراء.")[lang]


def L(lang: str, en: str, de: str) -> str:  # type: ignore[no-redef]
    lang = normalize_lang(lang)
    if lang == "de":
        return de
    if lang == "en":
        return en
    if en in COMMON:
        return COMMON[en][lang]
    if en.startswith("TICK ") and ": one simulated period" in en:
        n = en.split()[1].split(":")[0]
        return _names(en, f"TICK {n}: ein simulierter Zeitabschnitt", f"ТИК {n}: один смоделированный период", f"CICLO {n}: un periodo simulado", f"TICK {n}: un periodo simulato", f"周期 {n}：一个模拟时期", f"時点 {n}: 一つの模擬期間", f"틱 {n}: 하나의 시뮬레이션 기간", f"चक्र {n}: एक सिमुलेटेड अवधि", f"טיק {n}: תקופה מדומה אחת", f"تیک {n}: یک دوره شبیه‌سازی‌شده", f"الدورة {n}: فترة محاكاة واحدة")[lang]
    if en.startswith("Trade sum:"):
        return _localized_trade_sum(lang, en)
    if en.startswith("Interpretation of this run:"):
        return _localized_interpretation(lang, en)
    if en.startswith("Scenario reading for "):
        return _localized_scenario_reading(lang, en)
    if en.startswith("Scenario meaning:"):
        return _long_generic(lang, "scenario_meaning", en)
    if en.startswith("Result:"):
        return _localized_result(lang, en)
    for prefix, key in LONG_KEYWORDS:
        if en.startswith(prefix):
            return _long_generic(lang, key, en)
    return en

# -----------------------------------------------------------------------------
# 7. CLI
# -----------------------------------------------------------------------------


def normalize_detail(s: str) -> str:
    mapping = {"kurz": "short", "mittel": "medium", "voll": "full",
               "short": "short", "medium": "medium", "full": "full"}
    return mapping.get(s, s)


def fresh_seed() -> int:
    return random.SystemRandom().randint(1, 2_147_483_647)


def detected_width(requested_width: int) -> int:
    # Returns the real requested/detected width. AngularEconomy itself applies
    # the single 5-character right-side safety margin.
    if requested_width and requested_width > 0:
        base = requested_width
    else:
        base = shutil.get_terminal_size((118, 24)).columns
    return max(55, base)


def parse_args(argv: List[str]) -> argparse.Namespace:
    lang_list = ", ".join(SUPPORTED_LANGS)
    p = argparse.ArgumentParser(
        description="Colorful PyPy3 simulation of an angular vector-currency economy / Winkelwährungswirtschaft.")
    p.add_argument("--lang", "--language", "--sprache", default="en",
                   help=("Output language. Default: en. Options/aliases include: " + lang_list +
                         "; deutsch, russisch, spanisch, italienisch, chinesisch, japanisch, koreanisch, indisch/hindi, hebräisch, persisch, arabisch."))
    p.add_argument("--deutsch", action="store_true", help="Shortcut for --lang de.")
    p.add_argument("--ticks", type=int, default=18, help="Number of simulation periods. Default: 18")
    p.add_argument("--seed", type=int, default=None,
                   help="Random seed. If omitted, a fresh seed is generated at every start. Same seed => same EU countries and same run.")
    p.add_argument("--countries", "--laender", default="",
                   help="Optional comma-separated EU country codes, e.g. DE,FR,IT or DEU,FRA,ITA. Missing slots are filled by seed.")
    p.add_argument("--scenario", choices=SCENARIOS, default="baseline",
                   help="Scenario climate: baseline, resonance, power, wellbeing, fragmented, scarcity, tradeboom.")
    p.add_argument("--detail", choices=["short", "medium", "full", "kurz", "mittel", "voll"], default="full",
                   help="Output detail for sector tables. Default: full")
    p.add_argument("--report-every", "--bericht-jeder", type=int, default=1,
                   help="Print detailed report only every n-th tick. Default: 1")
    p.add_argument("--width", "--breite", type=int, default=0,
                   help="Output text width before the automatic 5-character right margin. Default: detect terminal width.")
    p.add_argument("--no-color", "--ohne-farbe", action="store_true", help="Disable ANSI colors.")
    p.add_argument("--without-explanations", "--ohne-erklaerungen", action="store_true",
                   help="Skip local explanatory blocks above each simulation part.")
    p.add_argument("--only-manual", "--nur-handbuch", action="store_true",
                   help="Print header and local glossary previews, then stop.")
    p.add_argument("--no-utf8-gallery", "--ohne-utf8-galerie", action="store_true",
                   help="Do not print the final UTF-8 art gallery.")
    p.add_argument("--no-scenario-comparison", action="store_true",
                   help="Do not run silent comparison scenarios for the gallery.")
    p.add_argument("--export-csv", default="", help="Path for country history CSV.")
    p.add_argument("--export-currencies-csv", "--export-waehrungen-csv", default="", help="Path for currency history CSV.")
    p.add_argument("--export-md", default="", help="Path for final Markdown report.")
    return p.parse_args(argv)

def main(argv: List[str]) -> int:
    args = parse_args(argv)
    lang = "de" if args.deutsch else normalize_lang(args.lang)
    detail = normalize_detail(args.detail)
    seed = int(args.seed) if args.seed is not None else fresh_seed()
    selected_ids = [x.strip() for x in args.countries.split(",") if x.strip()]
    sim = AngularEconomy(seed=seed, ticks=max(1, args.ticks), detail=detail,
                         report_every=max(1, args.report_every), width=detected_width(args.width),
                         colors=not args.no_color, explanations=not args.without_explanations,
                         lang=lang, scenario=args.scenario, gallery=not args.no_utf8_gallery,
                         compare_scenarios=not args.no_scenario_comparison,
                         selected_country_ids=selected_ids or None,
                         auto_seed=args.seed is None)
    if args.only_manual:
        sim.print_header()
        sim.print_preface()
        for key in ["currency", "labor", "goods", "trade", "indices", "drift", "final"]:
            small_section(key.upper(), Ansi.BRIGHT_CYAN)
            sim.explain_part(key)
        return 0
    sim.run()
    if args.export_csv:
        sim.export_csv(args.export_csv)
        print(col(f"\nCSV exported: {args.export_csv}" if lang == "en" else f"\nCSV exportiert: {args.export_csv}", Ansi.BRIGHT_GREEN))
    if args.export_currencies_csv:
        sim.export_currency_csv(args.export_currencies_csv)
        print(col(f"Currency CSV exported: {args.export_currencies_csv}" if lang == "en" else f"Währungs-CSV exportiert: {args.export_currencies_csv}", Ansi.BRIGHT_GREEN))
    if args.export_md:
        sim.export_markdown(args.export_md)
        print(col(f"Markdown report exported: {args.export_md}" if lang == "en" else f"Markdownbericht exportiert: {args.export_md}", Ansi.BRIGHT_GREEN))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        raise SystemExit(0)
