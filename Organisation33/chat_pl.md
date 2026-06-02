# Historia czatu – Polski

**Zakres:** widoczna historia czatu do prośby o eksport.  
**Temat:** funktor jako struktura regulowania technologii; prawa za technologią, o technologii i przeciw technologii.

---

## Wiadomość 1 – Użytkownik

Funktor jest właściwą strukturą bazową do budowania praw państwowych, aby ograniczać technologię albo opisywać, dokąd technologia może lub powinna iść dalej — tam, gdzie technologia nie jest jeszcze naprawdę zła. Dzięki funktorowi można określić, gdzie można kontynuować, gdzie trzeba się zatrzymać, a nawet gdzie technologia powinna zostać zdemontowana.

---

## Wiadomość 2 – Asystent

Tak — **jako idea strukturalna funktor jest bardzo mocny**. Ale sformułowałbym to precyzyjniej:

**Funktor nie jest samym prawem. Jest strukturą tłumaczenia między stanem technologicznym a działaniem normatywnym.**

Czyli nie: „Funktor decyduje moralnie”.

Lecz:

> Funktor regulacyjny odwzorowuje rozwój technologii, konteksty użycia i eskalacje na stany prawne: dozwolone, wymagające obserwacji, wymagające zezwolenia, ograniczone, zakazane albo podlegające demontażowi.

To dobrze pasuje do współczesnych logik regulacji opartych na ryzyku. EU AI Act klasyfikuje na przykład systemy AI według poziomów ryzyka takich jak „unacceptable risk”, „high risk”, „limited risk” i „minimal/no risk”. ([digital-strategy.ec.europa.eu](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai?utm_source=chatgpt.com)) NIST opisuje zarządzanie ryzykiem AI również jako ustrukturyzowaną praktykę, która ma uczynić ryzyka dla jednostek, organizacji i społeczeństwa możliwymi do opanowania. ([nist.gov](https://www.nist.gov/itl/ai-risk-management-framework?utm_source=chatgpt.com)) Zasady OECD wyraźnie wiążą godną zaufania AI z prawami człowieka i wartościami demokratycznymi. ([oecd.org](https://www.oecd.org/en/topics/sub-issues/ai-principles.html?utm_source=chatgpt.com))

Formalnie można powiedzieć:

**Kategoria T = technologia**

Obiekty: konkretne technologie w konkretnych kontekstach.  
Przykłady: rozpoznawanie twarzy na lotnisku, rozpoznawanie twarzy w szkołach, autonomiczny dron, medyczny model diagnostyczny, system scoringu społecznego.

Morfizmy: przejścia albo eskalacje.  
Przykłady: więcej autonomii, większa skala, głębsze dane, mniej kontroli człowieka, użycie wojskowe, sprzężenie z systemami tożsamości.

**Kategoria R = regulacja**

Obiekty: stany normatywne.  
Przykłady: swobodnie dozwolone, wymagające przejrzystości, wymagające audytu, wymagające licencji, ograniczone, zakazane, wymagające demontażu.

Morfizmy: zaostrzenia lub złagodzenia prawne.  
Przykłady: obowiązek zgłoszenia, kontrola bezpieczeństwa, odpowiedzialność, moratorium, zakaz, cofnięcie zezwolenia na działanie.

Wtedy funktor regulacyjny wyglądałby tak:

\[
F: T \rightarrow R
\]

Bierze sytuację technologiczną i odwzorowuje ją na odpowiedź prawną.

Ważny punkt to **zachowanie struktury**:

\[
F(g \circ f) = F(g) \circ F(f)
\]

To znaczy: jeśli technologia zaostrza się krok po kroku, prawo nie może rozpatrywać tych kroków osobno. Regulacja musi zachowywać łańcuch eskalacji. Mała zmiana techniczna może wyglądać niewinnie, ale w kompozycji z innymi zmianami stać się niebezpieczna.

Przykład:

1. monitoring kamerami  
2. plus rozpoznawanie twarzy  
3. plus porównywanie w czasie rzeczywistym  
4. plus centralny obywatelski ID  
5. plus automatyczne sankcje  

Każdy pojedynczy krok można sprzedać jako „jeszcze nie naprawdę zły”. Funktor zmusza do patrzenia na **kompozycję**. Właśnie tam leży siła twojej idei.

Postawiłbym jednak granicę: **sam funktor nie mówi, gdzie trzeba się zatrzymać.** Potrzebuje kryteriów. Inaczej jest tylko elegancką maszyną bez moralności.

Kryteria mogłyby być takie:

**Nieodwracalność:** czy szkodę da się cofnąć?  
**Utrata autonomii:** czy technologia odbiera ludziom władzę decyzyjną?  
**Asymetria:** czy daje państwom lub korporacjom nieproporcjonalną władzę?  
**Brak realnej zgody:** czy ludzie są rejestrowani, oceniani lub poddawani wpływowi bez sensownej zgody?  
**Sprzężenie systemowe:** czy technika jest połączona z tożsamością, pieniędzmi, pracą, edukacją, policją albo zdrowiem?  
**Skutki błędów:** kto ponosi szkodę, gdy system się myli?  
**Możliwość demontażu:** czy technologię można później ponownie rozmontować?

W ten sposób z twojego zdania powstaje całkiem użyteczna teoria:

> Polityka technologiczna potrzebuje funktora, który odwzorowuje przejścia techniczne na stany normatywne. Ten funktor musi zachowywać kompozycje, aby regulacja oceniała nie tylko pojedyncze technologie, lecz ścieżki eskalacji. Tam, gdzie odwzorowanie prowadzi do stanów takich jak nieodwracalna asymetria władzy, kontrola bez zgody albo szkoda systemowa, technologia musi być ograniczana, zatrzymywana albo demontowana.

To jest mocniejsze niż samo „technologia dobra/zła”. To **struktura wyznaczania granic**.

Jeszcze ostrzej:

**Funktor odpowiada nie tylko: czym jest ta technologia?  
Ale: dokąd prowadzi ta technologia, jeśli jej wewnętrzne możliwości będą dalej rozwijane?**

Tego właśnie brakuje wielu ustawom. Często regulują widoczny przedmiot, a nie ścieżkę rozwoju. Dlatego twoja idea funktora byłaby szczególnie użyteczna dla technologii z potencjałem eskalacji: AI, biotechnologii, nadzoru, broni autonomicznej, władzy platform, neurotechnologii i administracji algorytmicznej.

Najlepsza wersja twojej myśli brzmiałaby więc:

> Funktor jest formalną podstawą regulowania technologii nie statycznie, lecz kierunkowo. Łączy ścieżki rozwoju technologicznego z progami prawnymi i pokazuje, kiedy postęp jest dozwolony, kiedy musi być kontrolowany, a kiedy musi zostać zatrzymany lub zdemontowany.

To poważna podstawa modelu regulacyjnego. Zagrożeniem byłoby tylko mistyfikowanie funktora. Nie zastępuje etyki, demokracji ani prawa. Ale może dać im czystą strukturę.

---

## Wiadomość 3 – Użytkownik

Zbuduj prawa za technologią, o technologii i przeciw technologii. Podaj kilka przykładów!

---

## Wiadomość 4 – Asystent

Tak. Zbuduję je jako **projekty ustaw** — nie jako obowiązujące prawo, lecz jako modele tego, jak państwo mogłoby technologię **wspierać**, **opisywać/regulować** oraz **ograniczać albo zakazywać**.

Struktura podstawowa to:

\[
F: \text{stan technologiczny} \rightarrow \text{skutek prawny}
\]

Czyli:

> Technologia nie jest oceniana tylko po nazwie, ale po kontekście, skali, stopniu autonomii, skutku władzy, intensywności danych, odwracalności i potencjale szkody.

To jest bliskie dzisiejszym podejściom opartym na ryzyku. EU AI Act rozróżnia na przykład zakazane praktyki AI, systemy wysokiego ryzyka, ryzyka przejrzystości oraz minimalne lub żadne ryzyko. Zakazuje między innymi social scoringu, określonych praktyk biometrycznych, manipulacyjnej AI oraz zdalnej identyfikacji w czasie rzeczywistym w przestrzeni publicznej dla organów ścigania, z wyjątkami. ([digital-strategy.ec.europa.eu](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)) RODO zawiera już także prawo do niepodlegania decyzji opartej wyłącznie na zautomatyzowanym przetwarzaniu, wywołującej skutek prawny lub podobnie istotny, wraz z prawem do interwencji człowieka i zakwestionowania w określonych przypadkach. ([gdpr-info.eu](https://gdpr-info.eu/art-22-gdpr/)) NIST opisuje zarządzanie ryzykiem AI jako procedurę lepszego opanowywania ryzyk dla jednostek, organizacji i społeczeństwa. ([nist.gov](https://www.nist.gov/itl/ai-risk-management-framework)) OECD wiąże godną zaufania AI z prawami człowieka, wartościami demokratycznymi, przejrzystością, odpornością, bezpieczeństwem i nadzorem człowieka. ([oecd.org](https://www.oecd.org/en/topics/sub-issues/ai-principles.html))

---

# I. Ustawa podstawowa: Ustawa o funktorze technologicznym

## Ustawa o funktorialnej ocenie systemów technologicznych

**§ 1 Cel**

Ustawa tworzy ogólną strukturę oceny technologii, których rozwój, użycie albo sprzężenie może istotnie wpływać na ludzi, społeczeństwo, demokrację, środowisko, bezpieczeństwo lub władzę państwową.

**§ 2 Zasada**

Technologia nie powinna być oceniana tylko według swojej izolowanej funkcji, lecz według swojej ścieżki rozwoju.

Technologia jest uznawana za bardziej niebezpieczną, jeśli:

1. rejestruje, ocenia lub wpływa na ludzi bez zgody;
2. automatyzuje decyzje dotyczące życia, wolności, pracy, zdrowia, edukacji, kredytu, pobytu albo udziału politycznego;
3. jest sprzężona z systemami tożsamości, systemami płatniczymi, organami bezpieczeństwa, platformami pracy albo danymi zdrowotnymi;
4. po wprowadzeniu trudno albo wcale nie da się jej zdemontować;
5. rozdziela władzę silnie asymetrycznie;
6. przerzuca błędy na osoby dotknięte bez skutecznej korekty;
7. steruje zachowaniem dużych grup ludności.

**§ 3 Kategorie technologii**

Każda istotna technologia zostaje przypisana do poziomu prawnego:

**Poziom 0: Technologia wolna**  
Użycie dozwolone. Brak szczególnej regulacji.

**Poziom 1: Technologia wymagająca przejrzystości**  
Użycie dozwolone, ale wymagane są oznakowanie, dokumentacja i informacja dla użytkowników.

**Poziom 2: Technologia wymagająca kontroli**  
Użycie tylko po analizie ryzyka, kontroli bezpieczeństwa i publicznej rejestracji.

**Poziom 3: Technologia wymagająca zezwolenia**  
Użycie tylko po wcześniejszym zezwoleniu organu, audycie i stałej kontroli.

**Poziom 4: Technologia ograniczona**  
Użycie tylko w ściśle ograniczonych wyjątkach.

**Poziom 5: Technologia zakazana**  
Rozwój, eksploatacja, sprzedaż lub użycie są niedopuszczalne.

**Poziom 6: Technologia wymagająca demontażu**  
Już wprowadzone systemy muszą zostać wyłączone, usunięte albo rozłączone.

**§ 4 Reguła kompozycji**

Jeśli kilka technologii samych w sobie dopuszczalnych zostaje sprzężonych, należy ocenić nie tylko każdą technologię z osobna, lecz także łączny efekt sprzężenia.

Przykład:

kamera + rozpoznawanie twarzy + obywatelski ID + baza danych czasu rzeczywistego + automatyczna sankcja

nie jest prawnie tym samym co zwykła kamera. Sprzężenie tworzy nowy stan technologiczny i musi zostać ocenione ponownie.

**§ 5 Skutek prawny**

Jeśli rozwój technologiczny prowadzi do kontroli bez zgody, strukturalnego pozbawienia praw, nieodwracalnej koncentracji władzy albo automatycznego karania, należy go zakwalifikować co najmniej jako poziom 4, a w ciężkich przypadkach jako poziom 5 albo 6.

To jest ustawa podstawowa. Na niej budują poszczególne ustawy.


---

# II. Prawa **za** technologią

Te prawa mówią: technologia może i powinna iść dalej, jeśli wzmacnia ludzi, ogranicza szkody i nie koncentruje władzy.

---

## 1. Ustawa o wspieraniu technologii dobra wspólnego

**Cel:** aktywnie wspierać dobrą technologię.

**§ 1 Cel wsparcia**

Państwo wspiera technologie, które w sposób możliwy do wykazania służą dobru wspólnemu, zwłaszcza w obszarach zdrowia, edukacji, energii, ochrony przed katastrofami, dostępności, opieki, nauki i udziału demokratycznego.

**§ 2 Technologie kwalifikujące się do wsparcia**

Wsparciu podlegają systemy, które:

1. rozszerzają ludzkie zdolności, zamiast zastępować ludzi albo odbierać im sprawczość;
2. używają otwartych standardów;
3. są weryfikowalne i bezpieczne;
4. nie umożliwiają ukrytego nadzoru masowego;
5. nie tworzą trwałej zależności od jednego dostawcy;
6. minimalizują szkody ekologiczne;
7. w sytuacji awaryjnej mogą zostać wyłączone i zdemontowane.

**§ 3 Przykład**

AI, która wspiera lekarki i lekarzy w diagnostyce raka, ale nie podejmuje ostatecznej decyzji bez odpowiedzialności medycznej, kwalifikowałaby się do wsparcia.

AI, która automatycznie odsiewa osoby ubezpieczone, odmawia leczenia i nie dopuszcza skutecznego zaskarżenia, nie kwalifikowałaby się do wsparcia.

**§ 4 Warunek finansowania**

Kto otrzymuje finansowanie publiczne, musi ujawnić:

1. cel systemu;
2. rodzaje używanych danych;
3. znane ryzyka błędów;
4. środki bezpieczeństwa;
5. procedury skarg i korekty;
6. plan demontażu.

---

## 2. Ustawa o naprawialności i trwałości technologicznej

**Cel:** technologia ma służyć ludziom, a nie więzić użytkowników.

**§ 1 Prawo do naprawy**

Produkty cyfrowe i elektroniczne muszą być budowane tak, aby przez rozsądny okres użytkowania można je było naprawiać, konserwować i bezpiecznie aktualizować.

**§ 2 Zakaz sztucznych blokad**

Producenci nie mogą blokować naprawy, części zamiennych, niezależnej diagnostyki albo kompatybilnych komponentów bez koniecznego powodu bezpieczeństwa.

**§ 3 Obowiązek aktualizacji**

Producenci produktów cyfrowych muszą dostarczać aktualizacje bezpieczeństwa przez jasno określony minimalny okres.

**§ 4 Koniec wsparcia**

Jeżeli produkt nie jest już wspierany, producent musi jasno to wskazać. W produktach istotnych dla bezpieczeństwa należy zaoferować okres przejściowy albo bezpieczny tryb wyłączenia.

**§ 5 Przykład**

Połączony z siecią zamek do drzwi, który po trzech latach nie otrzymuje już aktualizacji bezpieczeństwa, nie może dalej być sprzedawany jako bezpieczny.

Smartfon nie może blokadami programowymi uniemożliwiać napraw w niezależnych warsztatach, chyba że udowodnione zostanie konkretne ryzyko bezpieczeństwa.

---

## 3. Porządek eksperymentów technologicznych i przestrzeni ochronnych

**Cel:** umożliwiać badania, nie nadużywając społeczeństwa jako laboratorium.

**§ 1 Zezwolenie na eksperymenty chronione**

Nowe technologie mogą być testowane w ograniczonych przestrzeniach ochronnych, jeśli ryzyka zostały wcześniej ocenione, osoby dotknięte poinformowane, a szkody ograniczone.

**§ 2 Granice eksperymentu**

Niedopuszczalne są eksperymenty, które:

1. potajemnie manipulują ludźmi;
2. mogą spowodować nieodwracalne szkody;
3. zawieszają prawa podstawowe;
4. obejmują grupy wrażliwe bez szczególnej ochrony;
5. nie są niezależnie weryfikowalne.

**§ 3 Obowiązek oceny**

Po zakończeniu eksperymentu należy publicznie udokumentować:

1. Co testowano?
2. Jakie ryzyka wystąpiły?
3. Jakie grupy były dotknięte?
4. Jakie szkody powstrzymano albo spowodowano?
5. Czy technologia może zostać skalowana?

**§ 4 Przykład**

Miasto może testować autonomiczne autobusy w ograniczonym obszarze, jeśli istnieją kierowcy bezpieczeństwa, awaryjne wyłączenie, odpowiedzialność i publiczna ocena.

Niedopuszczalny byłby tajny test algorytmicznych prognoz policyjnych wobec określonych dzielnic bez informacji, kontroli i możliwości zaskarżenia.

---

# III. Prawa **o** technologii

Te prawa opisują, kontrolują i porządkują technologię. Nie mówią od razu tak albo nie, lecz: najpierw uczynić widoczną, potem ocenić.

---

## 4. Porządek decyzji algorytmicznych

**Cel:** żaden człowiek nie powinien być zdany na maszynę, gdy dotknięte są ważne prawa.

**§ 1 Zakres zastosowania**

Ustawa dotyczy zautomatyzowanych lub algorytmicznie wspieranych decyzji o:

1. świadczeniach socjalnych;
2. statusie pobytu;
3. zatrudnieniu;
4. zdolności kredytowej;
5. ubezpieczeniu;
6. edukacji;
7. zdrowiu;
8. ściganiu karnym;
9. mieszkaniu;
10. usługach państwowych.

**§ 2 Ostateczna odpowiedzialność człowieka**

Decyzja prawnie albo istotnie obciążająca nie może być podejmowana wyłącznie przez system zautomatyzowany.

**§ 3 Obowiązek uzasadnienia**

Osoby dotknięte mają prawo do zrozumiałego wyjaśnienia:

1. jakie dane wykorzystano;
2. jakie główne czynniki wpłynęły na decyzję;
3. jaki organ jest odpowiedzialny;
4. jak decyzję można zaskarżyć.

**§ 4 Prawo do zaskarżenia**

Osoby dotknięte mają prawo do:

1. kontroli przez człowieka;
2. korekty fałszywych danych;
3. zawieszenia decyzji przy poważnych wątpliwościach;
4. niezależnego organu skargowego.

**§ 5 Przykład**

Urząd pracy może używać AI do wstępnego sortowania wniosków. Nie może jednak wyłącznie przez AI odbierać ludziom świadczeń.

Bank może używać systemu scoringowego. Musi jednak wyjaśnić, dlaczego człowiek został odrzucony, i umożliwić realną kontrolę.

---

## 5. Ustawa o przejrzystości technologicznej w przestrzeni publicznej

**Cel:** obywatele muszą wiedzieć, jaka technologia na nich działa.

**§ 1 Obowiązek oznakowania**

Technologie w przestrzeni publicznej muszą być widocznie oznakowane, jeśli:

1. rejestrują obraz, dźwięk, ruch albo zachowanie;
2. przetwarzają dane biometryczne;
3. przygotowują decyzje;
4. wpływają na zachowanie;
5. są sprzężone z organami bezpieczeństwa albo profilami komercyjnymi.

**§ 2 Rejestr publiczny**

Miasta, organy i instytucje publiczne muszą prowadzić rejestr obejmujący:

1. lokalizację technologii;
2. operatora;
3. cel;
4. rodzaje danych;
5. czas przechowywania;
6. przekazanie osobom trzecim;
7. organ skargowy;
8. datę wyłączenia albo przeglądu.

**§ 3 Przykład**

Kamera do sterowania ruchem musi być oznakowana.

Kamera, która dodatkowo identyfikuje osoby, tworzy profile przemieszczania albo jest sprzężona z policyjnymi bazami danych, należy do wyższego poziomu ryzyka i wymaga zezwolenia albo jest zakazana.

---

## 6. Ustawa o bezpieczeństwie produktów cyfrowych

**Cel:** kto sprzedaje produkty cyfrowe, musi dostarczać wraz z nimi bezpieczeństwo.

**§ 1 Zasada bezpieczeństwa**

Produkty z elementami cyfrowymi mogą być sprzedawane albo eksploatowane tylko wtedy, gdy są bezpiecznie opracowane, udokumentowane, aktualizowane i monitorowane zgodnie ze stanem techniki.

EU Cyber Resilience Act podąża już dokładnie w tym kierunku: ma chronić konsumentów i firmy przy produktach sprzętowych i programowych z elementami cyfrowymi, odpowiadając na niewystarczające cyberbezpieczeństwo i brak terminowych aktualizacji bezpieczeństwa. ([digital-strategy.ec.europa.eu](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act?utm_source=chatgpt.com))

**§ 2 Obowiązki producentów**

Producenci muszą:

1. sprawdzać ryzyka bezpieczeństwa przed wprowadzeniem na rynek;
2. stale obserwować podatności;
3. dostarczać aktualizacje bezpieczeństwa;
4. zgłaszać znane poważne podatności;
5. zrozumiale wyjaśniać funkcje bezpieczeństwa;
6. unikać niebezpiecznych haseł domyślnych;
7. umożliwiać bezpieczny koniec okresu użytkowania.

**§ 3 Zakaz niebezpiecznych produktów**

Produkt cyfrowy nie może być sprzedawany, jeśli:

1. zawiera znane krytyczne podatności;
2. nie przewiduje aktualizacji bezpieczeństwa;
3. wprowadza użytkowników w błąd co do stanu bezpieczeństwa;
4. zbiera dane bez konieczności;
5. po końcu wsparcia nadal jest reklamowany jako bezpieczny.

**§ 4 Przykład**

Niania elektroniczna z dostępem do internetu nie może być sprzedawana z hasłem domyślnym typu „admin/admin”.

Połączony samochód musi utrzymywać krytyczne dla bezpieczeństwa oprogramowanie przez cały cykl życia.

---

## 7. Ustawa przeciw niebezpiecznemu sprzęganiu danych

**Cel:** nie każde powiązanie danych powinno być dozwolone tylko dlatego, że jest technicznie możliwe.

**§ 1 Zakaz sprzęgania**

Dane osobowe z różnych obszarów życia nie mogą być sprzęgane bez szczególnej podstawy prawnej, jeśli powstają przez to kompleksowe profile osobowości, przemieszczania, zdrowia, płatności, edukacji albo zachowania.

**§ 2 Sprzężenia wysokiego ryzyka**

Szczególnie ryzykowne są sprzężenia między:

1. tożsamością i zachowaniem;
2. zdrowiem i ubezpieczeniem;
3. edukacją i kredytem;
4. świadczeniami socjalnymi i danymi policyjnymi;
5. miejscem pracy i rozpoznawaniem emocji;
6. danymi płatniczymi i aktywnością polityczną;
7. lokalizacją i rozpoznawaniem twarzy.

**§ 3 Wymóg zezwolenia**

Sprzężenia wysokiego ryzyka są dopuszczalne tylko wtedy, gdy:

1. istnieje konieczny interes publiczny;
2. nie ma łagodniejszej alternatywy;
3. zapewniona jest niezależna kontrola;
4. osoby dotknięte mają prawa do informacji, sprzeciwu i usunięcia;
5. sprzężenie jest ograniczone czasowo.

**§ 4 Przykład**

Aplikacja zdrowotna nie może automatycznie przekazywać liczby kroków pracodawcom ani ubezpieczycielom.

Szkoła nie może sprzęgać zachowań uczenia się z późniejszą zdolnością kredytową albo prognozami policyjnymi.


---

# IV. Prawa **przeciw** technologii

Te prawa wyznaczają twarde granice. Mówią: niektóre możliwości techniczne nie powinny być budowane, używane albo powinny zostać ponownie zdemontowane.

---

## 8. Ustawa anty-social-scoringowa

**Cel:** żadnej ogólnej wartości obywatela.

**§ 1 Zakaz**

Zakazane jest nadawanie ludziom przez systemy państwowe albo prywatne ogólnej wartości społecznej, zaufania, posłuszeństwa, moralności albo ryzyka, używanej w różnych obszarach życia.

**§ 2 Zakazane skutki**

Taki system nie może w szczególności decydować o:

1. dostępie do pracy;
2. edukacji;
3. mieszkaniu;
4. kredycie;
5. mobilności;
6. ubezpieczeniu;
7. świadczeniach państwowych;
8. udziale politycznym;
9. wolności poruszania się.

**§ 3 Zakaz obchodzenia**

Zakaz obowiązuje także wtedy, gdy system nazywa się inaczej, na przykład:

1. indeks zaufania;
2. wiarygodność obywatelska;
3. sygnalizacja ryzyka;
4. wartość integralności;
5. profil bezpieczeństwa;
6. wynik zachowania.

**§ 4 Przykład**

Zakazany byłby system łączący wypowiedzi polityczne, zachowania zakupowe, krąg znajomych, miejsce zamieszkania i kontakty z urzędami w ogólną „wartość wiarygodności”.

Dopuszczalne pozostają wąsko ograniczone kontrole zdolności kredytowej, jeśli są przejrzyste, celowe, zaskarżalne i nie mieszają się z obcymi obszarami życia.

---

## 9. Ustawa przeciw biometrycznemu nadzorowi masowemu

**Cel:** przestrzeń publiczna nie może stać się stałą przestrzenią identyfikacji.

**§ 1 Zasada**

Biometryczna identyfikacja ludzi w przestrzeni publicznej bez konkretnego powodu jest zakazana.

**§ 2 Zakazane praktyki**

Zakazane są w szczególności:

1. rozpoznawanie twarzy w czasie rzeczywistym w przestrzeniach publicznych;
2. trwałe profile przemieszczania oparte na cechach biometrycznych;
3. budowanie ogólnych baz twarzy z materiałów internetowych, kamerowych lub społecznościowych;
4. kategoryzacja biometryczna według opinii politycznej, religii, seksualności, zdrowia, pochodzenia etnicznego albo przynależności związkowej;
5. rozpoznawanie emocji w szkołach, na uniwersytetach i w miejscach pracy.

Ten kierunek zakazu częściowo odpowiada EU AI Act, który wymienia m.in. social scoring, nieukierunkowane scrapowanie w celu tworzenia lub rozszerzania baz rozpoznawania twarzy, rozpoznawanie emocji w kontekstach pracy i edukacji oraz określone praktyki biometryczne jako zakazane praktyki AI. ([digital-strategy.ec.europa.eu](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai))

**§ 3 Wyjątki**

Wyjątki są dopuszczalne tylko przy:

1. konkretnym zagrożeniu dla życia, ciała albo wolności;
2. zarządzeniu sądowym;
3. ograniczeniu czasowym i przestrzennym;
4. późniejszej niezależnej kontroli;
5. obowiązku publicznego raportowania.

**§ 4 Obowiązek demontażu**

Istniejące systemy naruszające tę ustawę muszą zostać wyłączone w ciągu sześciu miesięcy i technicznie usunięte w ciągu dwunastu miesięcy.

---

## 10. Ustawa przeciw autonomicznym systemom przymusu i sankcji

**Cel:** maszyny nie mogą same karać.

**§ 1 Zakaz autonomicznych sankcji**

Systemy technologiczne nie mogą karać, więzić, pozbawiać praw, wykluczać, nadzorować ani egzystencjalnie szkodzić ludziom bez odpowiedzialnej decyzji człowieka.

**§ 2 Zakazane systemy**

Zakazane są w szczególności:

1. autonomiczne roboty policyjne z uprawnieniem do użycia siły;
2. systemy AI automatycznie odbierające świadczenia socjalne;
3. automatyczna odmowa graniczna bez kontroli człowieka;
4. broń autonomiczna przeciw ludziom;
5. automatyczne punkty karne oparte na prognozach zachowania;
6. systemy automatycznie ograniczające wolność poruszania się.

**§ 3 Odpowiedzialność człowieka**

Każdy środek przymusu musi być przypisywalny konkretnie wskazanej osobie fizycznej albo organowi.

**§ 4 Przykład**

System może wspierać sędziego w analizie akt.

Ale nie może sam podjąć decyzji o areszcie.

System graniczny może sprawdzać dokumenty.

Ale nie może ostatecznie decydować o odmowie wjazdu, internowaniu albo deportacji bez kontroli człowieka i środka prawnego.

---

## 11. Ustawa o demontażu szkodliwych technologii

**Cel:** nie tylko zakazywać — także demontować.

**§ 1 Obowiązek demontażu**

Technologie należy demontować, jeśli:

1. trwale naruszają prawa podstawowe;
2. nie są skutecznie kontrolowalne;
3. wywołują systematyczną dyskryminację;
4. rejestrują ludzi bez zgody;
5. manipulują procesami demokratycznymi;
6. przekroczyły pierwotne ograniczenie celu;
7. zostały sprzężone z innymi systemami w niedopuszczalną strukturę władzy.

**§ 2 Plan demontażu**

Operatorzy muszą przedstawić plan demontażu obejmujący:

1. datę wyłączenia;
2. koncepcję usunięcia danych;
3. rozłączenie baz danych;
4. informację dla osób dotkniętych;
5. niezależną kontrolę;
6. dowód, że żadna kopia cieniowa nie działa dalej.

**§ 3 Przykład**

Miasto przez lata połączyło kamery, rozpoznawanie twarzy, dane drogowe, obywatelski ID i dane policyjne. Nawet jeśli każdy pojedynczy komponent był wcześniej dozwolony, całe sprzężenie może stać się obowiązkowo demontowalne.

**§ 4 Ciężar dowodu**

W przypadku technologii wymagających demontażu operator ponosi ciężar dowodu, że nie dochodzi do niedozwolonego dalszego użycia, archiwizacji cieniowej ani zmiany celu.

---

## 12. Ustawa przeciw technologicznej manipulacji opinią publiczną

**Cel:** demokracje nie mogą być niszczone przez niewidzialne sterowanie zachowaniem.

**§ 1 Zakaz systemów manipulacyjnych**

Zakazane są technologie, które w znacznym zakresie oszukują ludzi, psychologicznie ich wykorzystują albo politycznie nimi manipulują tak, że osoby dotknięte nie mogą tego rozpoznać.

**§ 2 Szczególnie zakazane praktyki**

Zakazane są:

1. spersonalizowana dezinformacja polityczna przez boty;
2. sztucznie generowane masowe opinie;
3. deepfake’i osób politycznych bez jasnego oznakowania;
4. psychometryczna manipulacja grup wrażliwych;
5. ukryta interakcja AI w kampaniach wyborczych;
6. zautomatyzowane zastraszanie przeciwników politycznych.

**§ 3 Obowiązek oznakowania**

Treści polityczne wygenerowane przez AI muszą być jasno rozpoznawalne, jeśli przedstawiają realistyczne obrazy, głosy, filmy albo tożsamości.

**§ 4 Obowiązki platform**

Platformy przy zasięgu politycznym muszą ujawnić:

1. czy treści zostały wygenerowane sztucznie;
2. kto zapłacił za kampanie;
3. jakie grupy docelowe były adresowane;
4. czy uczestniczyły boty albo konta zautomatyzowane;
5. jak użytkownicy mogą złożyć skargę.

**§ 5 Przykład**

Film satyryczny z jasnym oznakowaniem pozostaje dozwolony.

Zwodniczo realistyczny film, który krótko przed wyborami pokazuje fałszywą wypowiedź kandydata i nie jest oznakowany, zostaje zakazany albo natychmiast podlega usunięciu.

---

# V. Jeszcze ostrzejsze przykłady według pól technologii

## A. AI w szkołach

**Dozwolone:** pomoc w nauce, tłumaczenie, dostępność, indywidualne ćwiczenie.

**Wymaga zezwolenia:** AI do oceny wyników.

**Zakazane:** rozpoznawanie emocji, stały monitoring koncentracji, prognozy późniejszej wartości społecznej dziecka.

**Zdanie prawne:**

> Żadne dziecko nie może zostać przez system algorytmiczny przypisane do trwałej prognozy edukacyjnej, wynikowej albo charakterologicznej.

---

## B. AI w medycynie

**Dozwolone:** wsparcie diagnostyczne, badania, wczesne wykrywanie.

**Wymaga zezwolenia:** rekomendacje terapii wysokiego ryzyka.

**Zakazane:** automatyczna odmowa leczenia z powodów kosztowych bez kontroli człowieka.

**Zdanie prawne:**

> Medyczna AI może wspierać odpowiedzialność lekarską, ale nie może jej zastępować, gdy dotknięte są życie, zdrowie albo dostęp do leczenia.

---

## C. AI w życiu zawodowym

**Dozwolone:** planowanie terminów, BHP, dokształcanie.

**Wymaga zezwolenia:** wstępna selekcja kandydatów, analiza produktywności.

**Zakazane:** rozpoznawanie emocji, stały nadzór mikroruchów, automatyczne zwolnienie.

**Zdanie prawne:**

> Praca nie może być organizowana przez niewidzialną algorytmiczną ocenę totalną.

---

## D. Policja i bezpieczeństwo

**Dozwolone:** zarządzanie sprawami, rozpoznawanie wzorców w konkretnych postępowaniach, analiza danych zatwierdzonych przez sąd.

**Wymaga zezwolenia:** systemy prognostyczne dla konkretnych sytuacji zagrożenia.

**Zakazane:** ogólne prognozy przestępczości wobec osób bez czynu, masowe rozpoznawanie twarzy, zautomatyzowane wartości niebezpieczeństwa.

**Zdanie prawne:**

> Państwo nie może traktować ludzi tak, jakby popełnili czyn, tylko dlatego, że system oblicza ich jako przyszłe ryzyko.

---

## E. Platformy i media społecznościowe

**Dozwolone:** moderacja spamu, ochrona małoletnich, kontrola użytkownika nad rekomendacjami.

**Wymaga zezwolenia:** polityczne algorytmy rekomendacji o dużym zasięgu.

**Zakazane:** optymalizacja uzależnienia u małoletnich, ukryta manipulacja polityczna, sztuczne wzmacnianie oburzenia bez możliwości wyboru.

**Zdanie prawne:**

> Platformy nie mogą systematycznie optymalizować uwagi przeciw samostanowieniu, zdrowiu i demokracji.

---

# VI. Centralne jądro prawa

Jeśli sprowadzić wszystkie przykłady do twardej formuły, ustawa podstawowa brzmi:

> Technologia jest dozwolona, dopóki rozszerza ludzkie zdolności, nie niszcząc ludzkiej godności, wolności, demokratycznej kontroli i możliwości demontażu.

Albo precyzyjniej:

> Każda technologia, która czyni ludzi obserwowalnymi, ocenialnymi, sterowalnymi i sankcjonowalnymi bez możliwości skutecznego wycofania się, sprzeciwu albo obrony, powinna być traktowana jako technologia wysokiego ryzyka i przy nieodwracalnym skutku władzy zakazana albo zdemontowana.

To jest właściwy punkt przecięcia między **za**, **o** i **przeciw** technologii:

**Za technologią**, gdy wzmacnia ludzi.  
**O technologii**, gdy musi stać się widoczna, sprawdzalna i rozliczalna.  
**Przeciw technologii**, gdy czyni ludzi obiektami systemu.

---

## Wiadomość 5 – Użytkownik

Wyeksportuj cały przebieg czatu do kilku plików Markdown do pobrania: niemiecki, angielski, rosyjski, chiński, hiszpański, francuski, polski, japoński, koreański, czyli 9 plików Markdown.
