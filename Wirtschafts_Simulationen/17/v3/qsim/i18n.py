# -*- coding: utf-8 -*-
"""Small localization layer for the UTF-8 reports.

The simulation data model deliberately stays language-neutral.  This module
localizes the human-facing report text, CLI summaries and important labels.
No external translation package is used, so the project remains PyPy3/stdlib
only.
"""

from __future__ import print_function

LANG_ALIASES = {
    "en": "en", "eng": "en", "english": "en", "englisch": "en",
    "de": "de", "deu": "de", "ger": "de", "german": "de", "deutsch": "de",
    "ru": "ru", "rus": "ru", "russian": "ru", "russisch": "ru", "русский": "ru",
    "ja": "ja", "jp": "ja", "japanese": "ja", "japanisch": "ja", "日本語": "ja",
    "ko": "ko", "kr": "ko", "korean": "ko", "koreanisch": "ko", "한국어": "ko",
    "es": "es", "spa": "es", "spanish": "es", "spanisch": "es", "espanol": "es", "español": "es",
    "fr": "fr", "fre": "fr", "fra": "fr", "french": "fr", "französisch": "fr", "franzoesisch": "fr", "francais": "fr", "français": "fr",
    "hi": "hi", "hin": "hi", "hindi": "hi", "हिन्दी": "hi", "हिंदी": "hi",
    "zh": "zh", "cn": "zh", "chinese": "zh", "chinesisch": "zh", "中文": "zh", "汉语": "zh", "漢語": "zh",
}

LANG_LABELS = {
    "en": "English",
    "de": "Deutsch",
    "ru": "Русский",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "hi": "हिन्दी",
    "zh": "中文",
}

PUBLIC_LANGUAGE_NAMES = ["english", "deutsch", "russisch", "japanisch", "koreanisch", "spanisch", "französisch", "hindi", "chinesisch"]


def normalize_language(value):
    if value is None:
        return "en"
    key = str(value).strip().lower().replace("_", "-")
    if key in LANG_ALIASES:
        return LANG_ALIASES[key]
    # Accept forms such as zh-cn, en-US, de-DE.
    head = key.split("-", 1)[0]
    if head in LANG_ALIASES:
        return LANG_ALIASES[head]
    raise ValueError("Unsupported language: %s. Supported: %s" % (value, ", ".join(PUBLIC_LANGUAGE_NAMES)))


UI = {
    "en": {
        "report_title": "Q Economy Simulation – colorful UTF-8 art report",
        "report_intro1": "This report replaces dry terminal output with many colorful UTF-8 art panels. Every panel first explains what is being simulated and why that view matters. An interpretation follows after the drawing so the chart remains economically readable instead of merely decorative.",
        "report_intro2": "The colors are intentionally strong: rainbow bars represent positive quantities, production, employment or distribution; risk and debt indicators move from green through yellow/orange to red. In the terminal version ANSI colors are added; in plain files the colors remain as UTF-8/emoji blocks.",
        "desc_header": "What is simulated, and why?",
        "eval_header": "Interpretation",
        "scenario": "Scenario", "periods": "Periods", "households": "Households", "firms": "Firms", "banks": "Banks",
        "bqp_market": "BQP / market turnover", "price_index": "Price index", "unemployment": "Unemployment", "inflation_last": "Inflation last period", "q_money_positive": "Positive Q money", "q_debt": "Q debt", "ratio": "ratio", "credit_stock": "Credit stock", "household_gini": "Household Gini",
        "start": "Start", "end": "End", "min": "Min", "max": "Max", "average": "Average", "minimum": "Minimum", "maximum": "Maximum",
        "coin": "Coin", "meaning": "Meaning", "assets": "Assets", "debts": "Debts", "price": "Price", "sector": "Sector", "sales": "Sales", "profit": "Profit", "automation": "Auto", "labor_type": "Labor type", "employment": "Employment", "wage": "Wage", "capital_stock": "Capital stock",
        "legend_debt_heat": "Legend: green = almost no debt, yellow/orange = tense, red = strong semantic debt",
        "top_debt_coins": "Top debt coins", "price_times": "Price×", "household_distribution_note": "Household wealth distribution. Negative ranges show debt or poverty positions.",
        "read_as": "Read as", "no_events": "No special events in the log.", "period_short": "P", "done": "Done. The main outputs are localized, colorful UTF-8 art reports.", "output_folder": "Output folder", "important_files": "Most important files", "raw_data": "Raw data remain available for your own analysis", "scenario_done": "scenario simulated", "comparison_saved": "Comparison saved",
        "progress_unemployment_short": "UN", "progress_inflation_short": "Infl", "progress_debt": "Debt",
        "scenario_comparison_title": "Scenario comparison – colorful UTF-8 art", "scenario_comparison_intro": "Several political and economic scenarios are compared. The drawings show not only final values but also how growth, employment, debt, price stability and distribution are weighted differently.",
        "unknown_scenario": "Skipping unknown scenario",
        "language": "Language", "width": "Width",
        "q_flow_reading": "task → division → model → form → code/rule/delegation → structure/service/operation → compression/architecture/generation/machine",
        "no_crisis_mode": "productive investment", "no_crisis_reason": "growth without acute crisis mode",
        "commons": "Q8/Q9/Q12 commons", "commons_reason": "strengthen reuse and tools",
    },
    "de": {
        "report_title": "Q-Wirtschaftssimulation – farbiger UTF-8-Art-Bericht",
        "report_intro1": "Dieser Bericht ersetzt trockene Terminalausgaben durch viele farbige UTF-8-Art-Darstellungen. Jede Abbildung erklärt zuerst, was simuliert wird und warum diese Sicht wichtig ist. Danach folgt eine Auswertung, damit die Grafik nicht nur dekorativ ist, sondern ökonomisch lesbar wird.",
        "report_intro2": "Die Farben sind bewusst kräftig: Regenbogenbalken stehen für positive Mengen, Produktion, Beschäftigung oder Verteilung; Risiko- und Schuldanzeigen gehen von Grün über Gelb/Orange nach Rot. In der Terminalfassung werden zusätzlich ANSI-Farben verwendet; in Textdateien bleiben UTF-8- und Emoji-Blöcke erhalten.",
        "desc_header": "Was wird simuliert und warum?",
        "eval_header": "Auswertung",
        "scenario": "Szenario", "periods": "Perioden", "households": "Haushalte", "firms": "Firmen", "banks": "Banken",
        "bqp_market": "BQP / Marktumsatz", "price_index": "Preisindex", "unemployment": "Arbeitslosigkeit", "inflation_last": "Inflation letzte Per.", "q_money_positive": "Q-Geldmenge positiv", "q_debt": "Q-Schulden", "ratio": "Verhältnis", "credit_stock": "Kreditbestand", "household_gini": "Haushalts-Gini",
        "start": "Start", "end": "Ende", "min": "Min", "max": "Max", "average": "Durchschnitt", "minimum": "Minimum", "maximum": "Maximum",
        "coin": "Münze", "meaning": "Bedeutung", "assets": "Vermögen", "debts": "Schulden", "price": "Kurs", "sector": "Sektor", "sales": "Umsatz", "profit": "Profit", "automation": "Auto", "labor_type": "Arbeitstyp", "employment": "Beschäftigung", "wage": "Lohn", "capital_stock": "Kapitalstock",
        "legend_debt_heat": "Legende: grün = kaum Schuld, gelb/orange = angespannt, rot = starke semantische Schuld",
        "top_debt_coins": "Top-Schuldmünzen", "price_times": "Preis×", "household_distribution_note": "Haushaltsvermögen als Verteilung. Negative Bereiche zeigen Schuld- oder Armutspositionen.",
        "read_as": "Lesart", "no_events": "Keine besonderen Ereignisse im Protokoll.", "period_short": "P", "done": "Fertig. Die Hauptausgaben sind lokalisierte, farbige UTF-8-Art-Berichte.", "output_folder": "Ausgabeordner", "important_files": "Wichtigste Dateien", "raw_data": "Rohdaten bleiben zusätzlich für eigene Analysen erhalten", "scenario_done": "Szenario simuliert", "comparison_saved": "Vergleich gespeichert",
        "progress_unemployment_short": "AL", "progress_inflation_short": "Infl", "progress_debt": "Schuld",
        "scenario_comparison_title": "Szenariovergleich – farbige UTF-8-Art", "scenario_comparison_intro": "Verglichen werden mehrere politische und wirtschaftliche Szenarien. Die Abbildungen zeigen nicht nur Endwerte, sondern machen sichtbar, welche Szenarien Wachstum, Beschäftigung, Schulden, Preisstabilität und Verteilung unterschiedlich gewichten.",
        "unknown_scenario": "Überspringe unbekanntes Szenario", "language": "Sprache", "width": "Breite",
        "q_flow_reading": "Aufgabe → Teilung → Modell → Form → Code/Regel/Delegation → Struktur/Dienst/Betrieb → Kompression/Architektur/Generierung/Maschine",
        "no_crisis_mode": "produktive Investition", "no_crisis_reason": "Wachstum ohne akuten Krisenmodus",
        "commons": "Q8/Q9/Q12-Commons", "commons_reason": "Wiederverwendung und Werkzeuge stärken",
    },
    "ru": {
        "report_title": "Симуляция Q-экономики — цветной отчёт UTF-8 art", "report_intro1": "Отчёт заменяет сухой вывод наборами цветных UTF-8-панелей. Перед каждой панелью объясняется, что моделируется и зачем этот взгляд нужен; после панели даётся интерпретация.", "report_intro2": "Радужные полосы показывают положительные объёмы, производство, занятость или распределение; риск и долг движутся от зелёного к жёлтому, оранжевому и красному.",
        "desc_header": "Что моделируется и почему?", "eval_header": "Оценка", "scenario": "Сценарий", "periods": "Периоды", "households": "Домохозяйства", "firms": "Фирмы", "banks": "Банки", "bqp_market": "BQP / оборот рынка", "price_index": "Индекс цен", "unemployment": "Безработица", "inflation_last": "Инфляция", "q_money_positive": "Положительные Q-деньги", "q_debt": "Q-долг", "ratio": "отношение", "credit_stock": "Кредит", "household_gini": "Джини", "start": "Старт", "end": "Конец", "min": "Мин", "max": "Макс", "average": "Среднее", "minimum": "Минимум", "maximum": "Максимум", "coin": "Монета", "meaning": "Смысл", "assets": "Активы", "debts": "Долги", "price": "Цена", "sector": "Сектор", "sales": "Продажи", "profit": "Прибыль", "automation": "Авто", "labor_type": "Тип труда", "employment": "Занятость", "wage": "Зарплата", "capital_stock": "Капитал", "legend_debt_heat": "Легенда: зелёный = мало долга, жёлтый/оранжевый = напряжение, красный = сильный смысловой долг", "top_debt_coins": "Главные долговые монеты", "price_times": "Цена×", "household_distribution_note": "Распределение богатства домохозяйств; отрицательные зоны показывают долг или бедность.", "read_as": "Читать как", "no_events": "Особых событий нет.", "period_short": "P", "done": "Готово. Основные выходы — локализованные цветные UTF-8 отчёты.", "output_folder": "Папка вывода", "important_files": "Главные файлы", "raw_data": "Сырые данные также сохранены", "scenario_done": "сценарий смоделирован", "comparison_saved": "Сравнение сохранено", "progress_unemployment_short": "Безр", "progress_inflation_short": "Инфл", "progress_debt": "Долг", "scenario_comparison_title": "Сравнение сценариев — цветной UTF-8 art", "scenario_comparison_intro": "Сравниваются несколько политико-экономических сценариев и их баланс роста, занятости, долга, ценовой стабильности и распределения.", "unknown_scenario": "Пропускаю неизвестный сценарий", "language": "Язык", "width": "Ширина", "q_flow_reading": "задача → деление → модель → форма → код/правило/делегирование → структура/служба/операция → сжатие/архитектура/генерация/машина", "no_crisis_mode": "продуктивные инвестиции", "no_crisis_reason": "рост без острого кризиса", "commons": "общие Q8/Q9/Q12", "commons_reason": "усилить повторное использование и инструменты"},
    "ja": {
        "report_title": "Q経済シミュレーション — カラフルUTF-8アート報告", "report_intro1": "この報告は乾いた数値出力を、色の強いUTF-8アートの図に置き換えます。各図の前に何をシミュレートしているかと理由を書き、図の後に読み取りを示します。", "report_intro2": "虹色バーは正の量・生産・雇用・分布を示し、リスクと債務は緑から黄/橙、赤へ進みます。端末ではANSI色も使えます。", "desc_header": "何を、なぜシミュレートするか", "eval_header": "評価", "scenario": "シナリオ", "periods": "期間", "households": "家計", "firms": "企業", "banks": "銀行", "bqp_market": "BQP / 市場取引", "price_index": "物価指数", "unemployment": "失業", "inflation_last": "インフレ", "q_money_positive": "正のQ貨幣", "q_debt": "Q債務", "ratio": "比率", "credit_stock": "信用残高", "household_gini": "家計ジニ", "start": "開始", "end": "終了", "min": "最小", "max": "最大", "average": "平均", "minimum": "最小", "maximum": "最大", "coin": "硬貨", "meaning": "意味", "assets": "資産", "debts": "債務", "price": "価格", "sector": "部門", "sales": "売上", "profit": "利益", "automation": "自動化", "labor_type": "労働型", "employment": "雇用", "wage": "賃金", "capital_stock": "資本", "legend_debt_heat": "凡例: 緑=低債務、黄/橙=緊張、赤=強い意味債務", "top_debt_coins": "主要債務硬貨", "price_times": "価格×", "household_distribution_note": "家計資産の分布。負の領域は債務または貧困位置を示します。", "read_as": "読み方", "no_events": "特別なイベントはありません。", "period_short": "P", "done": "完了。主な出力はローカライズされたカラーUTF-8報告です。", "output_folder": "出力フォルダ", "important_files": "重要ファイル", "raw_data": "生データも保存されています", "scenario_done": "シナリオ完了", "comparison_saved": "比較を保存しました", "progress_unemployment_short": "失業", "progress_inflation_short": "インフレ", "progress_debt": "債務", "scenario_comparison_title": "シナリオ比較 — カラーUTF-8アート", "scenario_comparison_intro": "複数の政策・経済シナリオを比較し、成長、雇用、債務、物価安定、分配の違いを示します。", "unknown_scenario": "未知のシナリオをスキップ", "language": "言語", "width": "幅", "q_flow_reading": "課題 → 分割 → モデル → 形 → コード/規則/委任 → 構造/サービス/運用 → 圧縮/建築/生成/機械", "no_crisis_mode": "生産的投資", "no_crisis_reason": "急性危機なしの成長", "commons": "Q8/Q9/Q12コモンズ", "commons_reason": "再利用と道具を強化"},
    "ko": {
        "report_title": "Q 경제 시뮬레이션 — 컬러 UTF-8 아트 보고서", "report_intro1": "이 보고서는 건조한 숫자 출력을 여러 색의 UTF-8 아트 패널로 바꿉니다. 각 패널 앞에는 무엇을 시뮬레이션하는지와 왜 중요한지를 설명하고, 뒤에는 해석을 붙입니다.", "report_intro2": "무지개 막대는 양의 수량, 생산, 고용, 분포를 나타내고 위험과 부채는 초록에서 노랑/주황, 빨강으로 이동합니다.", "desc_header": "무엇을 왜 시뮬레이션하는가", "eval_header": "해석", "scenario": "시나리오", "periods": "기간", "households": "가계", "firms": "기업", "banks": "은행", "bqp_market": "BQP / 시장 매출", "price_index": "가격지수", "unemployment": "실업", "inflation_last": "인플레이션", "q_money_positive": "양의 Q 화폐", "q_debt": "Q 부채", "ratio": "비율", "credit_stock": "신용잔액", "household_gini": "가계 지니", "start": "시작", "end": "끝", "min": "최소", "max": "최대", "average": "평균", "minimum": "최소", "maximum": "최대", "coin": "동전", "meaning": "의미", "assets": "자산", "debts": "부채", "price": "가격", "sector": "부문", "sales": "매출", "profit": "이익", "automation": "자동화", "labor_type": "노동유형", "employment": "고용", "wage": "임금", "capital_stock": "자본", "legend_debt_heat": "범례: 초록=낮은 부채, 노랑/주황=긴장, 빨강=강한 의미 부채", "top_debt_coins": "주요 부채 동전", "price_times": "가격×", "household_distribution_note": "가계 부의 분포입니다. 음수 구간은 부채나 빈곤 위치를 뜻합니다.", "read_as": "읽는 법", "no_events": "특별한 사건이 없습니다.", "period_short": "P", "done": "완료. 주요 출력은 현지화된 컬러 UTF-8 보고서입니다.", "output_folder": "출력 폴더", "important_files": "중요 파일", "raw_data": "원시 데이터도 저장됩니다", "scenario_done": "시나리오 완료", "comparison_saved": "비교 저장됨", "progress_unemployment_short": "실업", "progress_inflation_short": "물가", "progress_debt": "부채", "scenario_comparison_title": "시나리오 비교 — 컬러 UTF-8 아트", "scenario_comparison_intro": "여러 정책·경제 시나리오를 비교하며 성장, 고용, 부채, 가격 안정, 분배의 차이를 보여줍니다.", "unknown_scenario": "알 수 없는 시나리오 건너뜀", "language": "언어", "width": "폭", "q_flow_reading": "과제 → 분할 → 모델 → 형태 → 코드/규칙/위임 → 구조/서비스/운영 → 압축/아키텍처/생성/기계", "no_crisis_mode": "생산적 투자", "no_crisis_reason": "급성 위기 없는 성장", "commons": "Q8/Q9/Q12 공유재", "commons_reason": "재사용과 도구 강화"},
    "es": {
        "report_title": "Simulación de economía Q — informe colorido UTF-8 art", "report_intro1": "Este informe sustituye la salida seca por muchos paneles coloridos de arte UTF-8. Antes de cada panel se explica qué se simula y por qué importa; después se ofrece una interpretación económica.", "report_intro2": "Las barras arcoíris muestran cantidades positivas, producción, empleo o distribución; riesgo y deuda van de verde a amarillo/naranja y rojo.", "desc_header": "¿Qué se simula y por qué?", "eval_header": "Evaluación", "scenario": "Escenario", "periods": "Periodos", "households": "Hogares", "firms": "Empresas", "banks": "Bancos", "bqp_market": "BQP / facturación", "price_index": "Índice de precios", "unemployment": "Desempleo", "inflation_last": "Inflación", "q_money_positive": "Dinero Q positivo", "q_debt": "Deuda Q", "ratio": "relación", "credit_stock": "Crédito", "household_gini": "Gini hogares", "start": "Inicio", "end": "Fin", "min": "Mín", "max": "Máx", "average": "Promedio", "minimum": "Mínimo", "maximum": "Máximo", "coin": "Moneda", "meaning": "Significado", "assets": "Activos", "debts": "Deudas", "price": "Precio", "sector": "Sector", "sales": "Ventas", "profit": "Beneficio", "automation": "Auto", "labor_type": "Tipo de trabajo", "employment": "Empleo", "wage": "Salario", "capital_stock": "Capital", "legend_debt_heat": "Leyenda: verde = poca deuda, amarillo/naranja = tensión, rojo = deuda semántica fuerte", "top_debt_coins": "Monedas de deuda principales", "price_times": "Precio×", "household_distribution_note": "Distribución de riqueza de hogares; rangos negativos indican deuda o pobreza.", "read_as": "Lectura", "no_events": "No hay eventos especiales en el registro.", "period_short": "P", "done": "Listo. Las salidas principales son informes UTF-8 art localizados y coloridos.", "output_folder": "Carpeta de salida", "important_files": "Archivos principales", "raw_data": "Los datos brutos siguen disponibles", "scenario_done": "escenario simulado", "comparison_saved": "Comparación guardada", "progress_unemployment_short": "Des", "progress_inflation_short": "Infl", "progress_debt": "Deuda", "scenario_comparison_title": "Comparación de escenarios — UTF-8 art colorido", "scenario_comparison_intro": "Se comparan varios escenarios políticos y económicos para ver crecimiento, empleo, deuda, estabilidad de precios y distribución.", "unknown_scenario": "Omitiendo escenario desconocido", "language": "Idioma", "width": "Ancho", "q_flow_reading": "tarea → división → modelo → forma → código/regla/delegación → estructura/servicio/operación → compresión/arquitectura/generación/máquina", "no_crisis_mode": "inversión productiva", "no_crisis_reason": "crecimiento sin crisis aguda", "commons": "comunes Q8/Q9/Q12", "commons_reason": "reforzar reutilización y herramientas"},
    "fr": {
        "report_title": "Simulation d’économie Q — rapport UTF-8 art coloré", "report_intro1": "Ce rapport remplace la sortie sèche par de nombreux panneaux colorés en art UTF-8. Avant chaque panneau, il explique ce qui est simulé et pourquoi cette vue compte; après, il donne une lecture économique.", "report_intro2": "Les barres arc-en-ciel indiquent les quantités positives, la production, l’emploi ou la distribution; le risque et la dette vont du vert au jaune/orange puis au rouge.", "desc_header": "Que simule-t-on et pourquoi ?", "eval_header": "Évaluation", "scenario": "Scénario", "periods": "Périodes", "households": "Ménages", "firms": "Entreprises", "banks": "Banques", "bqp_market": "BQP / chiffre d’affaires", "price_index": "Indice des prix", "unemployment": "Chômage", "inflation_last": "Inflation", "q_money_positive": "Monnaie Q positive", "q_debt": "Dette Q", "ratio": "rapport", "credit_stock": "Crédit", "household_gini": "Gini ménages", "start": "Début", "end": "Fin", "min": "Min", "max": "Max", "average": "Moyenne", "minimum": "Minimum", "maximum": "Maximum", "coin": "Pièce", "meaning": "Sens", "assets": "Actifs", "debts": "Dettes", "price": "Prix", "sector": "Secteur", "sales": "Ventes", "profit": "Profit", "automation": "Auto", "labor_type": "Type de travail", "employment": "Emploi", "wage": "Salaire", "capital_stock": "Capital", "legend_debt_heat": "Légende : vert = peu de dette, jaune/orange = tension, rouge = forte dette sémantique", "top_debt_coins": "Principales pièces de dette", "price_times": "Prix×", "household_distribution_note": "Répartition de la richesse des ménages; les zones négatives indiquent dette ou pauvreté.", "read_as": "Lecture", "no_events": "Aucun événement particulier dans le journal.", "period_short": "P", "done": "Terminé. Les principales sorties sont des rapports UTF-8 art localisés et colorés.", "output_folder": "Dossier de sortie", "important_files": "Fichiers principaux", "raw_data": "Les données brutes restent disponibles", "scenario_done": "scénario simulé", "comparison_saved": "Comparaison enregistrée", "progress_unemployment_short": "Chôm", "progress_inflation_short": "Infl", "progress_debt": "Dette", "scenario_comparison_title": "Comparaison de scénarios — UTF-8 art coloré", "scenario_comparison_intro": "Plusieurs scénarios politiques et économiques sont comparés afin de voir croissance, emploi, dette, stabilité des prix et distribution.", "unknown_scenario": "Scénario inconnu ignoré", "language": "Langue", "width": "Largeur", "q_flow_reading": "tâche → division → modèle → forme → code/règle/délégation → structure/service/exploitation → compression/architecture/génération/machine", "no_crisis_mode": "investissement productif", "no_crisis_reason": "croissance sans crise aiguë", "commons": "communs Q8/Q9/Q12", "commons_reason": "renforcer réutilisation et outils"},
    "hi": {
        "report_title": "Q अर्थव्यवस्था सिमुलेशन — रंगीन UTF-8 art रिपोर्ट", "report_intro1": "यह रिपोर्ट सूखे अंकीय आउटपुट को रंगीन UTF-8 आर्ट पैनलों में बदलती है। हर पैनल से पहले बताया जाता है कि क्या सिमुलेट हो रहा है और क्यों; बाद में आर्थिक व्याख्या दी जाती है।", "report_intro2": "इंद्रधनुषी पट्टियाँ सकारात्मक मात्रा, उत्पादन, रोजगार या वितरण दिखाती हैं; जोखिम और ऋण हरे से पीले/नारंगी और लाल की ओर जाते हैं।", "desc_header": "क्या सिमुलेट हो रहा है और क्यों?", "eval_header": "मूल्यांकन", "scenario": "परिदृश्य", "periods": "अवधियाँ", "households": "परिवार", "firms": "कंपनियाँ", "banks": "बैंक", "bqp_market": "BQP / बाज़ार कारोबार", "price_index": "मूल्य सूचकांक", "unemployment": "बेरोज़गारी", "inflation_last": "मुद्रास्फीति", "q_money_positive": "सकारात्मक Q धन", "q_debt": "Q ऋण", "ratio": "अनुपात", "credit_stock": "ऋण भंडार", "household_gini": "परिवार गिनी", "start": "आरंभ", "end": "अंत", "min": "न्यून", "max": "अधिक", "average": "औसत", "minimum": "न्यूनतम", "maximum": "अधिकतम", "coin": "सिक्का", "meaning": "अर्थ", "assets": "संपत्ति", "debts": "ऋण", "price": "मूल्य", "sector": "क्षेत्र", "sales": "बिक्री", "profit": "लाभ", "automation": "स्वचालन", "labor_type": "कार्य प्रकार", "employment": "रोज़गार", "wage": "मज़दूरी", "capital_stock": "पूँजी", "legend_debt_heat": "संकेत: हरा=कम ऋण, पीला/नारंगी=तनाव, लाल=मजबूत अर्थगत ऋण", "top_debt_coins": "मुख्य ऋण सिक्के", "price_times": "मूल्य×", "household_distribution_note": "परिवार संपत्ति का वितरण; नकारात्मक क्षेत्र ऋण या गरीबी दिखाते हैं।", "read_as": "पढ़ें", "no_events": "लॉग में कोई विशेष घटना नहीं।", "period_short": "P", "done": "पूर्ण। मुख्य आउटपुट स्थानीयकृत रंगीन UTF-8 art रिपोर्ट हैं।", "output_folder": "आउटपुट फ़ोल्डर", "important_files": "मुख्य फ़ाइलें", "raw_data": "कच्चा डेटा भी उपलब्ध है", "scenario_done": "परिदृश्य सिमुलेट हुआ", "comparison_saved": "तुलना सहेजी गई", "progress_unemployment_short": "बेरो", "progress_inflation_short": "मुद्रा", "progress_debt": "ऋण", "scenario_comparison_title": "परिदृश्य तुलना — रंगीन UTF-8 art", "scenario_comparison_intro": "कई राजनीतिक और आर्थिक परिदृश्यों की तुलना की जाती है ताकि वृद्धि, रोजगार, ऋण, मूल्य स्थिरता और वितरण दिखें।", "unknown_scenario": "अज्ञात परिदृश्य छोड़ा गया", "language": "भाषा", "width": "चौड़ाई", "q_flow_reading": "कार्य → विभाजन → मॉडल → रूप → कोड/नियम/प्रतिनिधि → संरचना/सेवा/संचालन → संपीड़न/वास्तुकला/जनन/मशीन", "no_crisis_mode": "उत्पादक निवेश", "no_crisis_reason": "तीव्र संकट के बिना वृद्धि", "commons": "Q8/Q9/Q12 कॉमन्स", "commons_reason": "पुनः उपयोग और औज़ार मजबूत करें"},
    "zh": {
        "report_title": "Q经济模拟 — 彩色UTF-8艺术报告", "report_intro1": "本报告把枯燥的数字输出变成多个彩色UTF-8艺术面板。每个面板前说明模拟什么、为什么重要；面板后给出经济解读。", "report_intro2": "彩虹条表示正向数量、生产、就业或分布；风险和债务从绿色走向黄色/橙色和红色。", "desc_header": "模拟什么，为什么？", "eval_header": "解读", "scenario": "场景", "periods": "周期", "households": "家庭", "firms": "企业", "banks": "银行", "bqp_market": "BQP / 市场营业额", "price_index": "价格指数", "unemployment": "失业", "inflation_last": "通胀", "q_money_positive": "正Q货币", "q_debt": "Q债务", "ratio": "比率", "credit_stock": "信贷余额", "household_gini": "家庭基尼", "start": "开始", "end": "结束", "min": "最小", "max": "最大", "average": "平均", "minimum": "最小", "maximum": "最大", "coin": "硬币", "meaning": "含义", "assets": "资产", "debts": "债务", "price": "价格", "sector": "部门", "sales": "销售", "profit": "利润", "automation": "自动化", "labor_type": "劳动类型", "employment": "就业", "wage": "工资", "capital_stock": "资本", "legend_debt_heat": "图例：绿=债务很少，黄/橙=紧张，红=强语义债务", "top_debt_coins": "主要债务硬币", "price_times": "价格×", "household_distribution_note": "家庭财富分布；负区间表示债务或贫困位置。", "read_as": "读作", "no_events": "日志中没有特殊事件。", "period_short": "P", "done": "完成。主要输出是本地化的彩色UTF-8艺术报告。", "output_folder": "输出文件夹", "important_files": "重要文件", "raw_data": "原始数据也已保存", "scenario_done": "场景已模拟", "comparison_saved": "比较已保存", "progress_unemployment_short": "失业", "progress_inflation_short": "通胀", "progress_debt": "债务", "scenario_comparison_title": "场景比较 — 彩色UTF-8艺术", "scenario_comparison_intro": "比较多个政治和经济场景，显示增长、就业、债务、价格稳定与分配的差异。", "unknown_scenario": "跳过未知场景", "language": "语言", "width": "宽度", "q_flow_reading": "任务 → 分解 → 模型 → 形式 → 代码/规则/委托 → 结构/服务/运行 → 压缩/架构/生成/机器", "no_crisis_mode": "生产性投资", "no_crisis_reason": "没有急性危机的增长", "commons": "Q8/Q9/Q12公共资源", "commons_reason": "加强复用和工具"},
}

# Section names localized for the report. These are used in every language.
SECTION_NAMES = {
    "macro": {"en": "Macro cockpit", "de": "Makro-Cockpit", "ru": "Макро-панель", "ja": "マクロ・コックピット", "ko": "거시 계기판", "es": "Panel macro", "fr": "Tableau macro", "hi": "मैक्रो कॉकपिट", "zh": "宏观驾驶舱"},
    "bqp": {"en": "BQP time path", "de": "BQP-Zeitpfad", "ru": "Траектория BQP", "ja": "BQP時系列", "ko": "BQP 시간 경로", "es": "Trayectoria BQP", "fr": "Trajectoire BQP", "hi": "BQP समय पथ", "zh": "BQP时间路径"},
    "credit": {"en": "Money, credit and debt", "de": "Geld, Kredit und Schulden", "ru": "Деньги, кредит и долг", "ja": "貨幣・信用・債務", "ko": "화폐·신용·부채", "es": "Dinero, crédito y deuda", "fr": "Monnaie, crédit et dette", "hi": "धन, ऋण और कर्ज", "zh": "货币、信贷与债务"},
    "labor": {"en": "Labor market and wages", "de": "Arbeitsmarkt und Löhne", "ru": "Рынок труда и зарплаты", "ja": "労働市場と賃金", "ko": "노동시장과 임금", "es": "Trabajo y salarios", "fr": "Travail et salaires", "hi": "श्रम बाज़ार और मजदूरी", "zh": "劳动力市场与工资"},
    "prices": {"en": "Price level and inflation", "de": "Preisniveau und Inflation", "ru": "Цены и инфляция", "ja": "物価水準とインフレ", "ko": "가격 수준과 물가", "es": "Precios e inflación", "fr": "Prix et inflation", "hi": "मूल्य स्तर और मुद्रास्फीति", "zh": "价格水平与通胀"},
    "qmatrix": {"en": "Q coin matrix", "de": "Q-Münzenmatrix", "ru": "Матрица Q-монет", "ja": "Q硬貨マトリクス", "ko": "Q 동전 행렬", "es": "Matriz de monedas Q", "fr": "Matrice des pièces Q", "hi": "Q सिक्का मैट्रिक्स", "zh": "Q硬币矩阵"},
    "qdebt": {"en": "Q debt heatmap", "de": "Q-Schuld-Hitzekarte", "ru": "Теплокарта Q-долга", "ja": "Q債務ヒートマップ", "ko": "Q 부채 히트맵", "es": "Mapa de calor de deuda Q", "fr": "Carte de chaleur de dette Q", "hi": "Q ऋण हीटमैप", "zh": "Q债务热图"},
    "shortages": {"en": "Goods shortages", "de": "Güterengpässe", "ru": "Дефициты товаров", "ja": "財・サービス不足", "ko": "상품 부족", "es": "Escaseces de bienes", "fr": "Pénuries de biens", "hi": "वस्तु कमी", "zh": "商品短缺"},
    "sectors": {"en": "Sector map", "de": "Sektorenlandkarte", "ru": "Карта секторов", "ja": "部門マップ", "ko": "부문 지도", "es": "Mapa sectorial", "fr": "Carte sectorielle", "hi": "क्षेत्र मानचित्र", "zh": "部门地图"},
    "public": {"en": "Government, banks and foreign trade", "de": "Staat, Banken und Außenhandel", "ru": "Государство, банки и внешняя торговля", "ja": "政府・銀行・対外取引", "ko": "정부·은행·대외무역", "es": "Estado, bancos y comercio exterior", "fr": "État, banques et commerce extérieur", "hi": "राज्य, बैंक और विदेश व्यापार", "zh": "政府、银行与外贸"},
    "households": {"en": "Households and inequality", "de": "Haushalte und Ungleichheit", "ru": "Домохозяйства и неравенство", "ja": "家計と不平等", "ko": "가계와 불평등", "es": "Hogares y desigualdad", "fr": "Ménages et inégalité", "hi": "परिवार और असमानता", "zh": "家庭与不平等"},
    "automation": {"en": "Capital and automation", "de": "Kapital und Automatisierung", "ru": "Капитал и автоматизация", "ja": "資本と自動化", "ko": "자본과 자동화", "es": "Capital y automatización", "fr": "Capital et automatisation", "hi": "पूँजी और स्वचालन", "zh": "资本与自动化"},
    "qflow": {"en": "Q1 to Q20 production chain", "de": "Q1 bis Q20 als Produktionskette", "ru": "Производственная цепочка Q1–Q20", "ja": "Q1からQ20の生産連鎖", "ko": "Q1에서 Q20 생산 사슬", "es": "Cadena productiva Q1–Q20", "fr": "Chaîne productive Q1–Q20", "hi": "Q1 से Q20 उत्पादन श्रृंखला", "zh": "Q1到Q20生产链"},
    "risk": {"en": "Risk radar", "de": "Risiko-Radar", "ru": "Радар рисков", "ja": "リスク・レーダー", "ko": "위험 레이더", "es": "Radar de riesgo", "fr": "Radar des risques", "hi": "जोखिम रडार", "zh": "风险雷达"},
    "events": {"en": "Event timeline", "de": "Ereignis-Timeline", "ru": "Лента событий", "ja": "イベント時系列", "ko": "이벤트 타임라인", "es": "Cronología de eventos", "fr": "Chronologie des événements", "hi": "घटना समयरेखा", "zh": "事件时间线"},
    "policy": {"en": "Policy map", "de": "Maßnahmenkarte", "ru": "Карта мер", "ja": "政策マップ", "ko": "정책 지도", "es": "Mapa de medidas", "fr": "Carte des mesures", "hi": "नीति मानचित्र", "zh": "政策地图"},
}

SECTION_KEYS = ["macro", "bqp", "credit", "labor", "prices", "qmatrix", "qdebt", "shortages", "sectors", "public", "households", "automation", "qflow", "risk", "events", "policy"]

# Detailed English and German text. Other languages use rich localized templates.
SECTION_DETAIL = {
    "en": {
        "macro_desc": "The final state of the whole economy is simulated: BQP, price level, inflation, unemployment, positive Q money, Q debt, credit stock and inequality. This view matters because it shows whether the economy is merely large or actually viable. In a Q economy, high turnover is not enough; money, debt, labor and the semantic coin structure must fit together.",
        "macro_eval": "The cockpit should be read as a solvency test, not as a simple dashboard. High output with high debt may hide semantic insolvency, especially if debt clusters in Q16 operation, Q18 architecture or Q20 modules. Low unemployment with rising inflation may signal capacity pressure; low inflation with high unemployment may signal weak demand or a qualification mismatch.",
        "bqp_desc": "The time path of the Brutto-Q-Produkt, roughly the market value movement in the simulation, is tracked over all periods. This is not a strict national-accounting GDP; it is the simulated market turnover and value creation. The curve matters because it shows whether production and demand grow, stagnate or break down during crises.",
        "bqp_eval": "Read the BQP line together with transactions and exports. If BQP rises while transactions fall, a few expensive goods or export channels may dominate. If BQP falls while transactions continue, the economy is busy but value-poor, which often means wrong prices, shortages or low productivity.",
        "credit_desc": "Monetary carrying capacity is simulated: positive Q money, Q debt, credit stock, new lending, repayments and default losses. The view is necessary because this economy has semantic debt. Debt is especially critical when it appears in operation, architecture or machine capability.",
        "credit_eval": "A healthy credit path creates the right Q coins later. Credit that only creates liquidity while widening Q10, Q16 or Q18 gaps becomes a structural crisis. Defaults are not just financial losses; they reveal missing ability to deliver promised coin types.",
        "labor_desc": "The labor market is simulated through employment, unemployment, average wage and the distribution across all labor types. This matters because the model is a full economy: agriculture, construction, care, trade, industry, energy, research, software/AI and many other forms of work. Labor here is social production capacity, not only intelligence work.",
        "labor_eval": "The employment bars show whether the economy works broadly or overuses single areas. A healthy system needs food, energy, construction, care, logistics, education, maintenance and public service besides software and AI. High unemployment with high shortages points to mismatched skills or sectoral allocation, not to a lack of needs.",
        "prices_desc": "Price index and inflation are simulated across periods. This view matters because price pressure in a Q economy is not only a money-supply problem. It can come from real goods shortages, wrong Q structure, credit overextension or weak operating capacity.",
        "prices_eval": "Imports can buffer shortages, but they are not an unlimited rescue. Rising import values with persistent shortages point to a structural supply problem. Deflation with high debt may be just as dangerous as inflation because debts become harder to repair.",
        "qmatrix_desc": "The full semantic balance of Q1 to Q20 is simulated: positive holdings, debts and market prices. This matrix is the heart of the Q economy. It shows not just how much value exists but which kind of value is missing or dominant. Four Q1 coins equal one Q20 nominally, but they do not replace a finished machine.",
        "qmatrix_eval": "The matrix reveals whether the economy is concentrated in low base coins, middle operation coins or high system and capital coins. Red debt segments in Q16, Q18, Q19 or Q20 are serious because they affect operation, architecture, generation and finished modules. High Q5 holdings without Q10/Q18 cover indicate code or production bubbles.",
        "qdebt_desc": "The concentration of Q debts by coin type is simulated. The heatmap matters because it immediately shows where the semantic pressure sits. A Q1 debt is an unresolved task; a Q18 debt is missing architecture; a Q20 debt is missing module or machine maturity.",
        "qdebt_eval": "The darkest or reddest fields are the first repair targets. They are not only financial loads but missing capabilities. If top debts are system or capital coins, policy should not merely stimulate demand; it should build structure, operation, architecture or module capacity.",
        "shortages_desc": "The simulation shows which real goods and services were not sufficiently available. This connects the Q system to ordinary economic supply: food, energy, housing, health, education, transport, industry, culture, security and other goods. A currency remains abstract unless it translates into real provision.",
        "shortages_eval": "High shortages mean demand was not met by production, imports or public stabilization. The price multiplier is crucial: a high shortage with a strong price increase is a hard supply bottleneck; a high shortage without price reaction may show market inertia or public buffering.",
        "sectors_desc": "The economic structure is simulated by sector: sales, profit, firm count and automation. This matters because a complete economy cannot depend on one sector. Agriculture, raw materials, energy, industry, construction, health, education, logistics, trade, finance, public services, culture, maintenance, research, environment and security must interact.",
        "sectors_eval": "The largest sales bars show where demand is concentrated. Profit bars show whether sectors build capital or bleed out. Negative profit zones can point to input shortages, price caps, weak demand or heavy debt. High automation is productive only if employment, skill and Q10/Q16/Q18 structure keep pace.",
        "public_desc": "Public finances, credit channels and foreign trade are simulated. The panel is needed because crises do not arise only inside firms. Transfers, public purchases, loans, repayments, defaults, exports and imports can stabilize or destabilize the whole economy.",
        "public_eval": "A viable state stabilizes without merely shifting debt. Public buying is productive when it creates Q16 infrastructure, Q12 tools, education, health or commons. Banks are useful when loans finance real transformation; they become dangerous when defaults rise and credit hides semantic gaps.",
        "households_desc": "The distribution of household wealth is simulated. This matters because an economy can be unstable even when totals look good if households lack access to work, education, health or consumption. Inequality weakens demand, social stability and the ability to turn new Q1 tasks into productive work.",
        "households_eval": "The distribution shows whether wealth is broad or concentrated. A high Gini does not automatically mean collapse, but it means participation and demand are narrowing. In a Q economy this is especially important because education and skills determine which coins households can create.",
        "automation_desc": "The simulation shows which sectors build capital stock and automation. This matters because automation is not only software or AI. Industry, logistics, energy, construction, health, administration, agriculture and maintenance can all become automated or capital-intensive. It is productive only when human and institutional structures catch up.",
        "automation_eval": "Sectors with high capital and high automation can raise productivity strongly. They can also displace employment or create Q16/Q18 debt if operation and architecture do not grow with them. A healthy automation wave needs education, maintenance, interfaces and robust operating infrastructure.",
        "qflow_desc": "The basic movement of the Q economy is simulated: task becomes division, model, form, operation, system, architecture, generation and finally module or machine. This view is justified because it makes the meaning of the coins visible. The economy does not only produce goods; it transforms difficulty into functioning structure.",
        "qflow_eval": "The markers show which stations are solid and which are stressed. A break between Q5/Q13 and Q18/Q20 is especially critical: then there is much implementation or service activity but too little architecture and module maturity. A break between Q1 and Q3 means tasks are not understood or modeled well.",
        "risk_desc": "The crisis sensitivity of the economy is simulated across several stress axes: unemployment, debt load, inflation, architecture and operation debt, goods shortages, inequality and credit defaults. This matters because crises rarely emerge from one number; they emerge from coupled weaknesses.",
        "risk_eval": "Red or long risk bars are the priority crisis channels. If several axes are high at once, the response should not be one-dimensional. Money policy alone does not fix architecture debt, and a job program alone does not fix an energy bottleneck. The Q economy requires repair by coin type and sector.",
        "events_desc": "The timeline simulates the sequence of important events: warnings, defaults, bankruptcies, public programs and stress signals. This view matters because metrics show states while events explain paths. A crisis rarely appears suddenly; it accumulates warning signs.",
        "events_eval": "The timeline helps sort causes. Early clusters of warnings mean the final state was prepared. Late clusters of defaults point to credit or liquidity stress. Many public measures show that the state already acted as stabilizer and should be evaluated for effectiveness.",
        "policy_desc": "This panel simulates a prioritization of possible economic policy levers from the end state. It does not claim automatic truth; it translates measured stress into possible interventions such as debt restructuring, Q18 architecture programs, Q16 operating infrastructure, public jobs, bottleneck investment, commons funds or import buffers.",
        "policy_eval": "The policy map is a diagnostic translation, not a command. The main rule remains: do not flood abstract money into a semantic coin gap. The missing coin type has to be repaired or productively created.",
    },
    "de": {}
}

# Use the original German wording by translating the English concepts in a compact way.
SECTION_DETAIL["de"].update({
    "macro_desc": "Simuliert wird der Endzustand der gesamten Volkswirtschaft: BQP, Preisniveau, Inflation, Arbeitslosigkeit, Q-Geldmenge, Q-Schulden, Kreditbestand und Ungleichheit. Diese Darstellung ist wichtig, weil sie sichtbar macht, ob die Wirtschaft nur groß wirkt oder auch tragfähig ist. In einer Q-Ökonomie reicht ein hoher Umsatz nicht aus; entscheidend ist, ob Geld, Schuld, Arbeit und semantische Münzstruktur zusammenpassen.",
    "macro_eval": "Das Cockpit ist als Solvenzprüfung zu lesen, nicht als bloße Übersicht. Hoher Output mit hoher Schuld kann semantische Zahlungsunfähigkeit verstecken, besonders bei Q16-Betrieb, Q18-Architektur oder Q20-Modulen. Niedrige Arbeitslosigkeit mit starker Inflation zeigt Kapazitätsdruck; niedrige Inflation mit hoher Arbeitslosigkeit zeigt eher Nachfrageschwäche oder Qualifikationsbruch.",
    "bqp_desc": "Simuliert wird die Entwicklung des Brutto-Q-Produkts beziehungsweise des Marktumsatzes über alle Perioden. Das BQP ist hier kein strenges reales Bruttoinlandsprodukt, sondern die beobachtete Wertbewegung im Simulationsmarkt. Die Kurve ist wichtig, weil sie zeigt, ob Produktion und Nachfrage wachsen, stagnieren oder in Krisenphasen einbrechen.",
    "bqp_eval": "Der BQP-Pfad muss mit Transaktionen und Exporten gelesen werden. Steigt BQP bei fallenden Transaktionen, dominieren möglicherweise wenige teure Güter oder Exportkanäle. Fällt BQP trotz vieler Transaktionen, ist die Wirtschaft beschäftigt, aber wertarm: ein Hinweis auf schlechte Preise, Engpässe oder geringe Produktivität.",
    "credit_desc": "Simuliert wird die monetäre Tragfähigkeit: positive Q-Geldmenge, Q-Schulden, Kreditbestand, neue Kredite, Rückzahlungen und Ausfallverluste. Die Darstellung ist notwendig, weil diese Wirtschaft semantische Schulden kennt. Eine hohe Schuld ist besonders kritisch, wenn sie in Betrieb, Architektur oder Maschinenfähigkeit liegt.",
    "credit_eval": "Gesund ist ein Kreditpfad nur, wenn die finanzierte Produktion später passende Q-Münzen erzeugt. Kredit, der nur Liquidität schafft, aber Q10-, Q16- oder Q18-Lücken vergrößert, wird zur Strukturkrise. Ausfälle sind nicht nur Finanzverluste, sondern zeigen fehlende Fähigkeit, versprochene Münzarten zu liefern.",
    "labor_desc": "Simuliert wird der Arbeitsmarkt über Beschäftigung, Arbeitslosigkeit, Durchschnittslohn und die Verteilung auf alle Arbeitstypen. Das ist wichtig, weil das Modell ausdrücklich eine ganze Wirtschaft abbildet: Landwirtschaft, Bau, Pflege, Handel, Industrie, Energie, Forschung, Software/KI und viele andere Arbeitsformen. Arbeit ist hier gesellschaftliche Produktionsfähigkeit, nicht nur Intelligenzarbeit.",
    "labor_eval": "Die Beschäftigungsbalken zeigen, ob die Volkswirtschaft breit arbeitet oder nur einzelne Bereiche übernutzt. Ein gesundes System braucht nicht nur Software/KI, sondern Nahrung, Energie, Bau, Pflege, Logistik, Bildung, Wartung und öffentliche Dienste. Hohe Arbeitslosigkeit bei hohen Engpässen weist auf Qualifikations- oder Sektorfehlanpassung hin.",
    "prices_desc": "Simuliert wird, wie sich Preisindex und Inflation über die Perioden bewegen. Diese Sicht ist wichtig, weil Preisdruck in der Q-Ökonomie nicht nur Geldmengenproblem ist. Preissteigerungen können aus realen Güterengpässen, falscher Q-Struktur, Kreditüberdehnung oder mangelnder Betriebsfähigkeit entstehen.",
    "prices_eval": "Importe wirken als Puffer, aber nicht als unbegrenzte Rettung. Steigen Importwerte, während Engpässe bestehen bleiben, liegt wahrscheinlich ein strukturelles Angebotsproblem vor. Deflation mit hoher Schuld kann ebenso gefährlich sein, weil Reparatur der Schulden schwerer wird.",
    "qmatrix_desc": "Simuliert wird die vollständige semantische Bilanz aller Münzen Q1 bis Q20: positive Bestände, Schulden und Marktpreise. Diese Darstellung ist das Herz der Q-Wirtschaft. Sie zeigt nicht nur, wie viel Wert vorhanden ist, sondern welche Art von Wert fehlt oder dominiert. Vier Q1 sind nominal so viel wert wie eine Q20, aber sie ersetzen keine fertige Maschine.",
    "qmatrix_eval": "Die Matrix macht sichtbar, ob die Wirtschaft in niedrigen Grundmünzen, mittleren Operationsmünzen oder hohen System- und Kapitalmünzen konzentriert ist. Rote Schuldsegmente in Q16, Q18, Q19 oder Q20 sind besonders ernst. Hohe Q5-Bestände ohne Q10/Q18-Deckung deuten auf Code- oder Produktionsblasen hin.",
    "qdebt_desc": "Simuliert wird die Konzentration der Q-Schulden nach Münzart. Die Hitzekarte ist wichtig, weil sie sofort zeigt, an welcher semantischen Stelle die Wirtschaft unter Druck steht. Eine Grundschuld Q1 ist eine ungelöste Aufgabe; eine Q18-Schuld ist fehlende Architektur; eine Q20-Schuld ist fehlende Maschinen- oder Modulreife.",
    "qdebt_eval": "Die dunkelsten oder rötesten Felder sind die ersten Reparaturziele. Sie zeigen nicht nur finanzielle Last, sondern fehlende Fähigkeit. Wenn die Top-Schulden in System- oder Kapitalmünzen liegen, sollte Politik gezielt Struktur, Betrieb, Architektur oder Modulbau fördern.",
    "shortages_desc": "Simuliert wird, welche realen Güter und Dienste nicht ausreichend verfügbar waren. Diese Sicht verbindet das Q-System mit der gewöhnlichen Wirtschaft: Nahrung, Energie, Wohnen, Gesundheit, Bildung, Transport, Industrie, Kultur, Sicherheit und weitere Güter. Eine Währung bleibt abstrakt, wenn sie nicht in reale Versorgung übersetzt wird.",
    "shortages_eval": "Hohe Engpässe zeigen, dass Nachfrage nicht durch Produktion, Importe oder öffentliche Stabilisierung gedeckt wurde. Entscheidend ist das Preisverhältnis. Ein hoher Engpass mit starkem Preisaufschlag ist ein harter Angebotsmangel; ein hoher Engpass ohne Preisreaktion kann auf Marktträgheit oder staatliche Puffer hindeuten.",
    "sectors_desc": "Simuliert wird die Wirtschaftsstruktur nach Sektoren: Umsatz, Profit, Anzahl der Firmen und Automatisierungsgrad. Diese Abbildung ist wichtig, weil eine vollständige Volkswirtschaft nicht an einem einzigen Sektor hängt. Landwirtschaft, Rohstoffe, Energie, Industrie, Bau, Gesundheit, Bildung, Logistik, Handel, Finanzwesen, öffentlicher Dienst, Kultur, Wartung, Forschung, Umwelt und Sicherheit müssen zusammenwirken.",
    "sectors_eval": "Die größten Umsatzbalken zeigen, wo die Nachfrage konzentriert ist. Die Profitbalken zeigen, ob Sektoren Kapital aufbauen oder ausbluten. Negative Profitzonen können auf Inputmangel, Preisdeckel, Nachfrageschwäche oder hohe Schuldlast hinweisen. Hohe Automatisierung ist produktiv, wird aber riskant, wenn Beschäftigung, Qualifikation oder Q10/Q16/Q18-Struktur nicht mitwachsen.",
    "public_desc": "Simuliert werden öffentliche Finanzen, Kreditkanäle und Außenhandel. Diese Darstellung ist nötig, weil Krisen nicht nur innerhalb von Firmen entstehen. Transfers, öffentliche Käufe, Kredite, Rückzahlungen, Ausfälle, Exporte und Importe stabilisieren oder destabilisieren das ganze System.",
    "public_eval": "Ein tragfähiger Staat stabilisiert, ohne nur Schulden zu verschieben. Öffentliche Käufe sind produktiv, wenn sie Q16-Infrastruktur, Q12-Werkzeuge, Bildung, Gesundheit oder Gemeingüter erzeugen. Banken sind nützlich, wenn Kredit echte Transformation finanziert; sie werden gefährlich, wenn Ausfälle steigen und Kredite semantische Lücken verdecken.",
    "households_desc": "Simuliert wird die Verteilung des Haushaltsvermögens. Diese Abbildung ist wichtig, weil eine Wirtschaft auch dann instabil werden kann, wenn die Gesamtsumme gut aussieht, aber Haushalte keinen Zugang zu Arbeit, Bildung, Gesundheit oder Konsum haben. Ungleichheit schwächt Nachfrage, soziale Stabilität und die Fähigkeit, neue Q1-Aufgaben produktiv zu bearbeiten.",
    "households_eval": "Die Verteilung zeigt, ob Vermögen breit liegt oder in wenigen oberen Bereichen konzentriert ist. Ein hoher Gini-Wert bedeutet nicht automatisch Zusammenbruch, aber er zeigt, dass Teilhabe und Nachfrage enger werden. In einer Q-Wirtschaft ist das besonders relevant, weil Bildung und Fähigkeiten bestimmen, welche Münzen Haushalte erzeugen können.",
    "automation_desc": "Simuliert wird, welche Sektoren Kapitalstock und Automatisierungsgrad aufbauen. Diese Sicht ist wichtig, weil Automatisierung nicht nur Software/KI bedeutet. Auch Industrie, Logistik, Energie, Bau, Gesundheit, Verwaltung, Landwirtschaft und Wartung können automatisiert oder kapitalintensiver werden. Produktiv ist das nur, wenn die menschliche und institutionelle Struktur nachzieht.",
    "automation_eval": "Sektoren mit hohem Kapital und hoher Automatisierung können Produktivität stark erhöhen. Sie können aber auch Beschäftigung verdrängen oder Q16-/Q18-Schulden erzeugen, wenn Betrieb und Architektur nicht mitwachsen. Eine gesunde Automatisierungswelle braucht Ausbildung, Wartung, Schnittstellen und robuste Betriebsinfrastruktur.",
    "qflow_desc": "Simuliert wird die Grundbewegung der Q-Ökonomie: Aufgabe wird zu Teilung, Modell, Form, Operation, System, Architektur, Generierung und schließlich Modul oder Maschine. Diese Darstellung macht den Sinn der Münzen sichtbar. Die Wirtschaft produziert nicht nur Ware, sondern verwandelt Schwierigkeit in funktionsfähige Struktur.",
    "qflow_eval": "Die Markierungen zeigen, welche Stationen solide und welche belastet sind. Besonders kritisch ist ein Bruch zwischen Q5/Q13 und Q18/Q20: dann gibt es viel Implementierung oder Dienste, aber zu wenig Architektur und Modulreife. Ein Bruch zwischen Q1 und Q3 bedeutet, dass Aufgaben nicht gut verstanden oder modelliert werden.",
    "risk_desc": "Simuliert wird die Krisenanfälligkeit der Wirtschaft anhand mehrerer Stressachsen: Arbeitslosigkeit, Schuldenlast, Inflation, Architektur- und Betriebsschuld, Güterengpässe, Ungleichheit und Kreditausfälle. Diese Darstellung ist wichtig, weil Krisen selten aus nur einer Kennzahl entstehen. Sie entstehen durch Koppelungen.",
    "risk_eval": "Rote oder lange Risikobalken sind die vorrangigen Krisenkanäle. Wenn mehrere Achsen gleichzeitig hoch stehen, sollte die Reaktion nicht eindimensional sein. Geldpolitik allein löst keine Architekturschuld, und ein Jobprogramm allein löst keinen Energieengpass. Die Q-Ökonomie verlangt gezielte Reparatur nach Münzart und Sektor.",
    "events_desc": "Simuliert wird die zeitliche Folge wichtiger Ereignisse: Warnungen, Defaults, Insolvenzen, öffentliche Programme oder andere Stresssignale. Diese Abbildung ist wichtig, weil Kennzahlen nur Zustände zeigen, während Ereignisse den Verlauf erklären. Eine Krise entsteht selten plötzlich; sie sammelt Vorzeichen.",
    "events_eval": "Die Timeline hilft, Ursachen zu sortieren. Häufen sich Warnungen früh, dann war die Endlage vorbereitet. Häufen sich Defaults spät, kann eine Kredit- oder Liquiditätskrise entstanden sein. Viele öffentliche Maßnahmen zeigen, dass der Staat bereits als Stabilisator aktiv war und auf Wirksamkeit geprüft werden sollte.",
    "policy_desc": "Simuliert wird keine automatische Wahrheit, sondern eine Priorisierung möglicher wirtschaftspolitischer Hebel aus dem Endzustand. Die Karte übersetzt Stresspunkte in mögliche Interventionen: Schuldenrestrukturierung, Q18-Architekturprogramm, Q16-Betriebsinfrastruktur, öffentliches Jobprogramm, Engpassinvestitionen, Commons-Fonds oder Importpuffer.",
    "policy_eval": "Die Maßnahmenkarte ist kein Befehl, sondern eine Diagnoseübersetzung. Der wichtigste Grundsatz bleibt: keine abstrakte Geldflutung, wenn eine semantische Münzlücke vorliegt. Die passende Münze muss repariert oder produktiv erzeugt werden.",
})

GENERIC_DESC = {
    "ru": "Эта панель моделирует «{name}». Она нужна, потому что Q-экономика должна связывать деньги, долг, труд, сектора, реальные блага и семантические монеты, а не смотреть на один показатель. Ширина рисунка автоматически подгоняется под экран с запасом, чтобы окно не выходило за границы терминала.",
    "ja": "この図は「{name}」をシミュレートします。Q経済では貨幣、債務、労働、部門、実物供給、意味的な硬貨構造を同時に見る必要があるため、この表示が必要です。図の幅は画面幅から余白を引いて自動調整されます。",
    "ko": "이 패널은 ‘{name}’을 시뮬레이션합니다. Q 경제에서는 화폐, 부채, 노동, 부문, 실제 공급, 의미적 동전 구조를 함께 보아야 하므로 이 보기가 필요합니다. 그림 폭은 화면 폭에서 여유를 빼 자동으로 맞춰집니다.",
    "es": "Este panel simula «{name}». Es necesario porque la economía Q debe leer dinero, deuda, trabajo, sectores, bienes reales y estructura semántica de monedas al mismo tiempo, no una sola cifra. El ancho del dibujo se adapta automáticamente a la pantalla con un margen de seguridad.",
    "fr": "Ce panneau simule « {name} ». Il est nécessaire parce que l’économie Q doit lire ensemble monnaie, dette, travail, secteurs, biens réels et structure sémantique des pièces, et non un seul indicateur. La largeur du dessin s’adapte automatiquement à l’écran avec une marge de sécurité.",
    "hi": "यह पैनल “{name}” को सिमुलेट करता है। Q अर्थव्यवस्था में धन, ऋण, काम, क्षेत्र, वास्तविक वस्तुएँ और अर्थगत सिक्का-संरचना को साथ पढ़ना पड़ता है, केवल एक संख्या को नहीं। चित्र की चौड़ाई स्क्रीन से पाँच अक्षर घटाकर स्वतः फिट की जाती है।",
    "zh": "此面板模拟“{name}”。Q经济不能只看一个数字，而要同时阅读货币、债务、劳动、部门、真实供给和语义硬币结构。图形宽度会按屏幕宽度自动调整，并预留安全边距。",
}

GENERIC_EVAL = {
    "ru": "Оценка читается по длине и цвету полос. Длинные красные или оранжевые элементы указывают на стресс; зелёные и радужные элементы показывают мощность или положительный запас. Если несколько стрессов растут одновременно, нужна целевая починка по монете и сектору, а не абстрактное добавление денег.",
    "ja": "読み取りはバーの長さと色で行います。長い赤や橙はストレス、緑や虹色は容量または正の余力を示します。複数のストレスが同時に高い場合、抽象的な貨幣投入ではなく、硬貨種類と部門ごとの修復が必要です。",
    "ko": "해석은 막대의 길이와 색으로 읽습니다. 긴 빨강/주황은 스트레스를, 초록과 무지개색은 능력이나 양의 여유를 뜻합니다. 여러 스트레스가 동시에 높으면 단순한 돈 투입이 아니라 동전 종류와 부문별 수리가 필요합니다.",
    "es": "La evaluación se lee por longitud y color. Barras largas rojas o naranjas señalan estrés; barras verdes o arcoíris señalan capacidad o reserva positiva. Si varios estreses crecen a la vez, la respuesta debe reparar la moneda y el sector adecuados, no inyectar dinero abstracto sin dirección.",
    "fr": "L’évaluation se lit par la longueur et la couleur. Les longues barres rouges ou orange indiquent un stress; les barres vertes ou arc-en-ciel indiquent capacité ou réserve positive. Si plusieurs tensions montent ensemble, la réponse doit réparer la bonne pièce et le bon secteur, pas seulement ajouter de la monnaie abstraite.",
    "hi": "मूल्यांकन पट्टियों की लंबाई और रंग से पढ़ें। लंबी लाल या नारंगी पट्टियाँ तनाव दिखाती हैं; हरी और इंद्रधनुषी पट्टियाँ क्षमता या सकारात्मक भंडार दिखाती हैं। यदि कई तनाव साथ बढ़ते हैं, तो उपाय सिक्का-प्रकार और क्षेत्र के हिसाब से होना चाहिए, केवल अमूर्त धन डालना पर्याप्त नहीं है।",
    "zh": "解读主要看条形的长度和颜色。长的红色或橙色表示压力；绿色和彩虹色表示能力或正向余量。如果多个压力同时升高，回应应按硬币类型和部门定向修复，而不是只投入抽象货币。",
}

Q_NAMES = {
    "en": {1:"Difficulty",2:"Complexity",3:"Abstraction",4:"Crystallization",5:"Coding",6:"Declaration",7:"Delegation",8:"Library",9:"Framework",10:"Constraint",11:"Interface",12:"Toolbox",13:"Program/Service",14:"Orchestration",15:"Application",16:"Operation",17:"Compression",18:"Architecture",19:"Generation",20:"Module/Machine"},
    "de": {1:"Schwierigkeit",2:"Komplexität",3:"Abstraktion",4:"Kristallisation",5:"Kodierung",6:"Deklaration",7:"Delegation",8:"Bibliothek",9:"Framework",10:"Constraint",11:"Schnittstelle",12:"Toolbox",13:"Programm/Dienst",14:"Orchestrierung",15:"Anwendung",16:"Betrieb",17:"Kompression",18:"Architektur",19:"Generierung",20:"Modul/Maschine"},
}

SCENARIO_TEXT = {
    "en": {
        "balanced": "Balanced starting economy without a large shock.",
        "code_bubble": "Software/AI booms while constraints, operation and architecture come under pressure.",
        "energy_crisis": "Energy production is depressed; prices and follow-on costs rise.",
        "food_crisis": "Agricultural shock with food shortages.",
        "architecture_crisis": "Q18 architecture is scarce; technical debt becomes visible faster.",
        "automation_wave": "Automation rises sharply; productivity grows, but labor displacement appears.",
        "public_investment": "The state increases education, infrastructure, health and commons funds.",
        "austerity": "Public spending and transfers fall; private markets must carry more.",
        "climate_shock": "Agriculture, construction, energy and environment are stressed by climate effects.",
    },
    "de": {
        "balanced": "Ausgewogene Startwirtschaft ohne großen Schock.",
        "code_bubble": "Software/KI boomt, aber Constraints, Betrieb und Architektur geraten unter Druck.",
        "energy_crisis": "Energieproduktion ist gedrückt, Energiepreise und Folgekosten steigen.",
        "food_crisis": "Landwirtschaftlicher Schock mit Nahrungsmittelknappheit.",
        "architecture_crisis": "Q18-Architektur ist knapp; technische Schulden werden schneller sichtbar.",
        "automation_wave": "Automatisierung steigt stark; Produktivität wächst, aber Arbeitsmarktverdrängung entsteht.",
        "public_investment": "Staat erhöht Bildung, Infrastruktur, Gesundheit und Gemeingüterfonds.",
        "austerity": "Staatliche Ausgaben und Transfers sinken; private Märkte müssen mehr tragen.",
        "climate_shock": "Landwirtschaft, Bau, Energie und Umwelt werden durch Klimafolgen belastet.",
    },
}


SCENARIO_TEXT.update({
    "ru": {
        "balanced": "Сбалансированная стартовая экономика без крупного шока.",
        "code_bubble": "Бум ПО/ИИ, но ограничения, эксплуатация и архитектура под давлением.",
        "energy_crisis": "Производство энергии снижено; цены и последующие издержки растут.",
        "food_crisis": "Аграрный шок с дефицитом продовольствия.",
        "architecture_crisis": "Архитектура Q18 дефицитна; технический долг быстрее становится видимым.",
        "automation_wave": "Автоматизация резко растёт; производительность растёт, но труд вытесняется.",
        "public_investment": "Государство увеличивает расходы на образование, инфраструктуру, здоровье и commons.",
        "austerity": "Госрасходы и трансферты падают; частные рынки несут больше нагрузки.",
        "climate_shock": "Сельское хозяйство, строительство, энергия и экология испытывают климатический стресс.",
    },
    "ja": {
        "balanced": "大きなショックのない均衡的な初期経済。",
        "code_bubble": "ソフトウェア/AIがブーム化し、制約・運用・建築が圧迫される。",
        "energy_crisis": "エネルギー生産が低下し、価格と波及費用が上昇する。",
        "food_crisis": "農業ショックによる食料不足。",
        "architecture_crisis": "Q18建築が不足し、技術債務が早く表面化する。",
        "automation_wave": "自動化が急増し、生産性は伸びるが雇用代替が起きる。",
        "public_investment": "国家が教育、インフラ、健康、コモンズ投資を増やす。",
        "austerity": "公的支出と移転が減り、民間市場の負担が増える。",
        "climate_shock": "農業、建設、エネルギー、環境が気候影響で圧迫される。",
    },
    "ko": {
        "balanced": "큰 충격이 없는 균형 잡힌 시작 경제.",
        "code_bubble": "소프트웨어/AI는 호황이지만 제약, 운영, 아키텍처가 압박받는다.",
        "energy_crisis": "에너지 생산이 낮아지고 가격과 파급 비용이 오른다.",
        "food_crisis": "농업 충격과 식량 부족.",
        "architecture_crisis": "Q18 아키텍처가 부족해 기술 부채가 더 빨리 드러난다.",
        "automation_wave": "자동화가 급증해 생산성은 커지지만 노동 대체가 발생한다.",
        "public_investment": "국가가 교육, 인프라, 건강, 공유재 투자를 늘린다.",
        "austerity": "공공 지출과 이전이 줄어 민간 시장 부담이 커진다.",
        "climate_shock": "농업, 건설, 에너지, 환경이 기후 충격을 받는다.",
    },
    "es": {
        "balanced": "Economía inicial equilibrada sin gran choque.",
        "code_bubble": "Software/IA crece, pero restricciones, operación y arquitectura quedan bajo presión.",
        "energy_crisis": "La producción de energía cae; precios y costes derivados suben.",
        "food_crisis": "Choque agrícola con escasez de alimentos.",
        "architecture_crisis": "La arquitectura Q18 escasea; la deuda técnica se vuelve visible antes.",
        "automation_wave": "La automatización sube con fuerza; crece la productividad, pero aparece desplazamiento laboral.",
        "public_investment": "El Estado aumenta educación, infraestructura, salud y fondos comunes.",
        "austerity": "Bajan gasto público y transferencias; los mercados privados cargan más.",
        "climate_shock": "Agricultura, construcción, energía y ambiente sufren efectos climáticos.",
    },
    "fr": {
        "balanced": "Économie initiale équilibrée sans grand choc.",
        "code_bubble": "Le logiciel/IA est en boom, mais contraintes, exploitation et architecture sont sous pression.",
        "energy_crisis": "La production d’énergie baisse; prix et coûts indirects montent.",
        "food_crisis": "Choc agricole avec pénurie alimentaire.",
        "architecture_crisis": "L’architecture Q18 est rare; la dette technique devient visible plus vite.",
        "automation_wave": "L’automatisation progresse fortement; la productivité augmente mais l’emploi est déplacé.",
        "public_investment": "L’État augmente éducation, infrastructures, santé et fonds communs.",
        "austerity": "Les dépenses publiques et transferts baissent; les marchés privés portent plus.",
        "climate_shock": "Agriculture, construction, énergie et environnement sont stressés par le climat.",
    },
    "hi": {
        "balanced": "बड़े झटके के बिना संतुलित आरंभिक अर्थव्यवस्था।",
        "code_bubble": "सॉफ्टवेयर/AI तेज़ी से बढ़ता है, पर constraints, संचालन और वास्तुकला दबाव में आते हैं।",
        "energy_crisis": "ऊर्जा उत्पादन घटता है; कीमतें और आगे की लागतें बढ़ती हैं।",
        "food_crisis": "कृषि झटका और भोजन की कमी।",
        "architecture_crisis": "Q18 वास्तुकला कम है; तकनीकी ऋण जल्दी दिखने लगता है।",
        "automation_wave": "स्वचालन तेज़ बढ़ता है; उत्पादकता बढ़ती है, पर श्रम विस्थापन आता है।",
        "public_investment": "राज्य शिक्षा, अवसंरचना, स्वास्थ्य और commons में निवेश बढ़ाता है।",
        "austerity": "सार्वजनिक खर्च और transfers घटते हैं; निजी बाज़ार अधिक भार उठाते हैं।",
        "climate_shock": "कृषि, निर्माण, ऊर्जा और पर्यावरण जलवायु प्रभाव से दबते हैं।",
    },
    "zh": {
        "balanced": "没有大型冲击的均衡初始经济。",
        "code_bubble": "软件/AI繁荣，但约束、运行和架构承压。",
        "energy_crisis": "能源生产下降；价格和连带成本上升。",
        "food_crisis": "农业冲击导致食物短缺。",
        "architecture_crisis": "Q18架构稀缺；技术债务更快显现。",
        "automation_wave": "自动化快速上升；生产率增长，但出现劳动替代。",
        "public_investment": "国家增加教育、基础设施、健康和公共资源投资。",
        "austerity": "公共支出和转移支付下降；私人市场承担更多。",
        "climate_shock": "农业、建筑、能源和环境受到气候影响压力。",
    },
})

def t(lang, key):
    code = normalize_language(lang)
    if key in UI.get(code, {}):
        return UI[code][key]
    return UI["en"].get(key, key)


def lang_label(lang):
    return LANG_LABELS.get(normalize_language(lang), "English")


def section_name(lang, key):
    code = normalize_language(lang)
    m = SECTION_NAMES.get(key, {})
    return m.get(code) or m.get("en") or key


def section_title(lang, index, key):
    return "UTF-8 Art %02d – %s" % (index, section_name(lang, key))


def section_description(lang, key):
    code = normalize_language(lang)
    detail = SECTION_DETAIL.get(code, {})
    k = key + "_desc"
    if k in detail:
        return detail[k]
    return GENERIC_DESC.get(code, GENERIC_DESC.get("es", UI["en"]["report_intro1"])).format(name=section_name(code, key))


def section_evaluation(lang, key):
    code = normalize_language(lang)
    detail = SECTION_DETAIL.get(code, {})
    k = key + "_eval"
    if k in detail:
        return detail[k]
    return GENERIC_EVAL.get(code, GENERIC_EVAL.get("es", "Read the length and color of the bars."))


def q_name_lang(q, lang):
    code = normalize_language(lang)
    return Q_NAMES.get(code, Q_NAMES["en"]).get(int(q), "Q%d" % int(q))


def scenario_description(scenario, lang):
    code = normalize_language(lang)
    return SCENARIO_TEXT.get(code, SCENARIO_TEXT["en"]).get(scenario, scenario)
