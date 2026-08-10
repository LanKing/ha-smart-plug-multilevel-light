#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "translations"

# current_stability_samples label/helper, round_brightness_to_5 label/helper
T = {
    "af": ("Stroomstabiliteitsfilter", "Vereis dieselfde veranderde stroomwaarde hierdie aantal kere agtermekaar voordat die helderheidsmodus verander. ON/OFF word onmiddellik toegepas. 0 deaktiveer die filter; verstek is 2.", "Rond helderheid tot 5% af", "Rond die berekende helderheid tot die naaste 5% af. Deaktiveer om heel persentasies sonder 5%-stappe te gebruik."),
    "ar": ("مرشح استقرار التيار", "يتطلب تكرار قيمة التيار الجديدة نفسها بهذا العدد على التوالي قبل تغيير وضع السطوع. يتم تطبيق ON/OFF فورًا. القيمة 0 تعطل المرشح؛ الافتراضي 2.", "تقريب السطوع إلى 5%", "يقرب السطوع المحسوب إلى أقرب 5%. عطّل هذا الخيار لاستخدام نسب مئوية صحيحة دون خطوات 5%."),
    "bg": ("Филтър за стабилност на тока", "Изисква една и съща нова стойност на тока да бъде отчетена толкова пъти поред, преди да се смени режимът на яркост. ON/OFF се прилагат веднага. 0 изключва филтъра; по подразбиране е 2.", "Закръгляне на яркостта до 5%", "Закръгля изчислената яркост до най-близките 5%. Изключете, за да използвате цели проценти без стъпки от 5%."),
    "bn": ("কারেন্ট স্থিতিশীলতা ফিল্টার", "উজ্জ্বলতার মোড বদলানোর আগে পরিবর্তিত কারেন্টের একই মান পরপর এতবার পাওয়া আবশ্যক। ON/OFF সঙ্গে সঙ্গে প্রয়োগ হয়। 0 ফিল্টার বন্ধ করে; ডিফল্ট 2।", "উজ্জ্বলতা 5% ধাপে রাউন্ড করুন", "গণনা করা উজ্জ্বলতা নিকটতম 5%-এ রাউন্ড করে। 5% ধাপ ছাড়া পূর্ণ শতাংশ ব্যবহার করতে এটি বন্ধ করুন।"),
    "bs": ("Filter stabilnosti struje", "Za promjenu režima svjetline ista nova vrijednost struje mora biti prijavljena ovoliko puta zaredom. ON/OFF se primjenjuju odmah. 0 isključuje filter; zadano je 2.", "Zaokruži svjetlinu na 5%", "Zaokružuje izračunatu svjetlinu na najbližih 5%. Isključite za cijele procente bez koraka od 5%."),
    "ca": ("Filtre d'estabilitat del corrent", "Exigeix que el mateix valor de corrent nou es notifiqui aquest nombre de vegades seguides abans de canviar el mode de brillantor. ON/OFF s'apliquen immediatament. 0 desactiva el filtre; el valor per defecte és 2.", "Arrodoneix la brillantor al 5%", "Arrodoneix la brillantor calculada al 5% més proper. Desactiveu-ho per utilitzar percentatges enters sense passos del 5%."),
    "cs": ("Filtr stability proudu", "Před změnou režimu jasu vyžaduje, aby byla stejná nová hodnota proudu nahlášena tolikrát za sebou. ON/OFF se použije okamžitě. 0 filtr vypne; výchozí hodnota je 2.", "Zaokrouhlovat jas na 5%", "Zaokrouhlí vypočtený jas na nejbližších 5 %. Vypněte pro použití celých procent bez kroků po 5 %."),
    "cy": ("Hidlydd sefydlogrwydd cerrynt", "Mae'n gofyn i'r un gwerth cerrynt newydd gael ei adrodd y nifer hwn o weithiau yn olynol cyn newid y modd disgleirdeb. Mae ON/OFF yn cael eu cymhwyso ar unwaith. Mae 0 yn analluogi'r hidlydd; y rhagosodiad yw 2.", "Talgrynnu disgleirdeb i 5%", "Talgrynna'r disgleirdeb a gyfrifwyd i'r 5% agosaf. Analluogwch i ddefnyddio canrannau cyfan heb gamau 5%."),
    "da": ("Filter for strømstabilitet", "Kræver, at den samme nye strømværdi rapporteres dette antal gange i træk, før lysstyrketilstanden ændres. ON/OFF anvendes straks. 0 deaktiverer filteret; standard er 2.", "Afrund lysstyrke til 5%", "Afrunder den beregnede lysstyrke til nærmeste 5 %. Deaktivér for at bruge hele procenter uden trin på 5 %."),
    "de": ("Stromstabilitätsfilter", "Erfordert, dass derselbe neue Stromwert so oft hintereinander gemeldet wird, bevor der Helligkeitsmodus geändert wird. ON/OFF wird sofort übernommen. 0 deaktiviert den Filter; Standard ist 2.", "Helligkeit auf 5% runden", "Rundet die berechnete Helligkeit auf die nächsten 5 %. Deaktivieren, um ganze Prozentwerte ohne 5-%-Schritte zu verwenden."),
    "el": ("Φίλτρο σταθερότητας ρεύματος", "Απαιτεί η ίδια νέα τιμή ρεύματος να αναφερθεί τόσες φορές διαδοχικά πριν αλλάξει η λειτουργία φωτεινότητας. Τα ON/OFF εφαρμόζονται αμέσως. Το 0 απενεργοποιεί το φίλτρο· προεπιλογή 2.", "Στρογγυλοποίηση φωτεινότητας στο 5%", "Στρογγυλοποιεί την υπολογισμένη φωτεινότητα στο πλησιέστερο 5%. Απενεργοποιήστε το για ακέραια ποσοστά χωρίς βήματα 5%."),
    "en": ("Current stability filter", "Requires the same changed current value this many times in a row before changing the detected brightness mode. ON/OFF are applied immediately. 0 disables the filter; the default is 2.", "Round brightness to 5%", "Rounds calculated brightness to the nearest 5%. Disable this to use whole percentages without 5% steps."),
    "en-GB": ("Current stability filter", "Requires the same changed current value this many times in a row before changing the detected brightness mode. ON/OFF are applied immediately. 0 disables the filter; the default is 2.", "Round brightness to 5%", "Rounds calculated brightness to the nearest 5%. Disable this to use whole percentages without 5% steps."),
    "eo": ("Filtrilo de kurenta stabileco", "Postulas ke la sama nova kurentvaloro estu raportita tiom da fojoj sinsekve antaŭ ŝanĝi la brilreĝimon. ON/OFF aplikiĝas tuj. 0 malŝaltas la filtrilon; defaŭlte estas 2.", "Rondigi brilon al 5%", "Rondigas la kalkulitan brilon al la plej proksima 5%. Malŝaltu por uzi tutajn procentojn sen 5%-paŝoj."),
    "es": ("Filtro de estabilidad de corriente", "Exige que el mismo valor nuevo de corriente se informe este número de veces seguidas antes de cambiar el modo de brillo detectado. ON/OFF se aplican inmediatamente. 0 desactiva el filtro; el valor predeterminado es 2.", "Redondear brillo al 5%", "Redondea el brillo calculado al 5% más cercano. Desactívalo para usar porcentajes enteros sin pasos del 5%."),
    "es-419": ("Filtro de estabilidad de corriente", "Requiere que el mismo valor nuevo de corriente se reporte esta cantidad de veces seguidas antes de cambiar el modo de brillo detectado. ON/OFF se aplican de inmediato. 0 desactiva el filtro; el valor predeterminado es 2.", "Redondear brillo al 5%", "Redondea el brillo calculado al 5% más cercano. Desactívalo para usar porcentajes enteros sin pasos del 5%."),
    "et": ("Voolu stabiilsusfilter", "Enne heledusrežiimi muutmist peab sama uus vooluväärtus saabuma nii mitu korda järjest. ON/OFF rakendub kohe. 0 lülitab filtri välja; vaikimisi on 2.", "Ümarda heledus 5%-ni", "Ümardab arvutatud heleduse lähima 5%-ni. Lülitage välja, et kasutada täisprotsente ilma 5% sammudeta."),
    "eu": ("Korronte-egonkortasunaren iragazkia", "Distira modua aldatu aurretik korronte-balio berri bera jarraian horrenbeste aldiz jasotzea eskatzen du. ON/OFF berehala aplikatzen dira. 0-k iragazkia desgaitzen du; lehenetsia 2 da.", "Biribildu distira %5era", "Kalkulatutako distira hurbileneko %5era biribiltzen du. Desgaitu %5eko urratsik gabeko ehuneko osoak erabiltzeko."),
    "fa": ("فیلتر پایداری جریان", "پیش از تغییر حالت روشنایی، باید مقدار جدید جریان به همین تعداد بار پیاپی یکسان گزارش شود. ON/OFF بلافاصله اعمال می‌شود. 0 فیلتر را غیرفعال می‌کند؛ مقدار پیش‌فرض 2 است.", "گرد کردن روشنایی به 5%", "روشنایی محاسبه‌شده را به نزدیک‌ترین 5% گرد می‌کند. برای استفاده از درصدهای صحیح بدون گام 5% آن را غیرفعال کنید."),
    "fi": ("Virran vakaussuodatin", "Sama uusi virta-arvo on raportoitava näin monta kertaa peräkkäin ennen kirkkaustilan vaihtamista. ON/OFF toteutetaan heti. 0 poistaa suodattimen käytöstä; oletus on 2.", "Pyöristä kirkkaus 5%:iin", "Pyöristää lasketun kirkkauden lähimpään 5 prosenttiin. Poista käytöstä, jos haluat kokonaiset prosentit ilman 5 % askelia."),
    "fr": ("Filtre de stabilité du courant", "Exige que la même nouvelle valeur de courant soit signalée ce nombre de fois de suite avant de changer le mode de luminosité détecté. ON/OFF sont appliqués immédiatement. 0 désactive le filtre ; la valeur par défaut est 2.", "Arrondir la luminosité à 5%", "Arrondit la luminosité calculée au multiple de 5 % le plus proche. Désactivez cette option pour utiliser des pourcentages entiers sans pas de 5 %."),
    "fy": ("Filter foar stroomstabiliteit", "Fereasket dat deselde nije stroomwearde dit oantal kearen efterinoar rapportearre wurdt foardat de helderheidsmodus feroaret. ON/OFF wurdt daliks tapast. 0 skeakelt it filter út; standert is 2.", "Helderheid ôfrûnje op 5%", "Rûnet de berekkene helderheid ôf op de tichtstbye 5%. Skeakelje út foar hiele persintaazjes sûnder stappen fan 5%."),
    "ga": ("Scagaire cobhsaíochta srutha", "Éilíonn sé go dtuairisceofar an luach srutha nua céanna an líon seo uaireanta as a chéile sula n-athraítear an mód gile. Cuirtear ON/OFF i bhfeidhm láithreach. Díchumasaíonn 0 an scagaire; is é 2 an réamhshocrú.", "Slánaigh gile go 5%", "Slánaíonn sé an gile ríofa go dtí an 5% is gaire. Díchumasaigh chun céatadáin iomlána a úsáid gan céimeanna 5%."),
    "gl": ("Filtro de estabilidade da corrente", "Require que o mesmo novo valor de corrente se informe este número de veces seguidas antes de cambiar o modo de brillo detectado. ON/OFF aplícanse inmediatamente. 0 desactiva o filtro; o valor predeterminado é 2.", "Redondear brillo ao 5%", "Redondea o brillo calculado ao 5% máis próximo. Desactívao para usar porcentaxes enteiras sen pasos do 5%."),
    "gsw": ("Stromstabilitätsfilter", "De gliich neui Stromwert muess so oft hinderänand gmäldet wärde, bevor de Helligkeitsmodus wechslet. ON/OFF wird sofort übernoh. 0 schaltet de Filter us; Standard isch 2.", "Helligkeit uf 5% runde", "Rundet d berechneti Helligkeit uf di nöchste 5%. Uschalte für ganzi Prozent ohni 5%-Schritt."),
    "he": ("מסנן יציבות זרם", "דורש שאותו ערך זרם חדש ידווח מספר זה של פעמים ברצף לפני שינוי מצב הבהירות. ON/OFF מוחלים מיד. 0 משבית את המסנן; ברירת המחדל היא 2.", "עיגול בהירות ל-5%", "מעגל את הבהירות המחושבת ל-5% הקרובים ביותר. השבת כדי להשתמש באחוזים שלמים ללא צעדים של 5%."),
    "hi": ("करंट स्थिरता फ़िल्टर", "ब्राइटनेस मोड बदलने से पहले बदला हुआ वही करंट मान लगातार इतनी बार रिपोर्ट होना आवश्यक है। ON/OFF तुरंत लागू होते हैं। 0 फ़िल्टर बंद करता है; डिफ़ॉल्ट 2 है।", "ब्राइटनेस को 5% पर राउंड करें", "गणना की गई ब्राइटनेस को निकटतम 5% पर राउंड करता है। 5% चरणों के बिना पूर्ण प्रतिशत उपयोग करने के लिए इसे बंद करें।"),
    "hr": ("Filtar stabilnosti struje", "Za promjenu načina svjetline ista nova vrijednost struje mora biti prijavljena ovoliko puta zaredom. ON/OFF se primjenjuju odmah. 0 isključuje filtar; zadano je 2.", "Zaokruži svjetlinu na 5%", "Zaokružuje izračunatu svjetlinu na najbližih 5%. Isključite za cijele postotke bez koraka od 5%."),
    "hu": ("Áramstabilitási szűrő", "A fényerőmód váltása előtt ugyanazt az új áramértéket ennyiszer kell egymás után jelenteni. Az ON/OFF azonnal érvényesül. A 0 kikapcsolja a szűrőt; az alapérték 2.", "Fényerő kerekítése 5%-ra", "A számított fényerőt a legközelebbi 5%-ra kerekíti. Kapcsolja ki egész százalékok használatához 5%-os lépések nélkül."),
    "hy": ("Հոսանքի կայունության զտիչ", "Պահանջում է, որ հոսանքի նույն նոր արժեքը այսքան անգամ անընդմեջ հաղորդվի՝ նախքան պայծառության ռեժիմը փոխելը։ ON/OFF-ը կիրառվում է անմիջապես։ 0-ը անջատում է զտիչը, լռելյայնը՝ 2։", "Պայծառությունը կլորացնել 5%-ով", "Հաշվարկված պայծառությունը կլորացնում է մոտակա 5%-ին։ Անջատեք՝ ամբողջ տոկոսներ օգտագործելու համար առանց 5% քայլերի։"),
    "id": ("Filter kestabilan arus", "Memerlukan nilai arus baru yang sama dilaporkan sebanyak ini berturut-turut sebelum mode kecerahan berubah. ON/OFF diterapkan segera. 0 menonaktifkan filter; bawaan 2.", "Bulatkan kecerahan ke 5%", "Membulatkan kecerahan yang dihitung ke 5% terdekat. Nonaktifkan untuk menggunakan persentase bulat tanpa langkah 5%."),
    "is": ("Straumstöðugleikasía", "Krefst þess að sama nýja straumgildi berist svona oft í röð áður en birtustilling breytist. ON/OFF gildir strax. 0 slekkur á síunni; sjálfgefið er 2.", "Námunda birtu að 5%", "Námundar reiknaða birtu að næstu 5%. Slökktu til að nota heil prósent án 5% skrefa."),
    "it": ("Filtro stabilità corrente", "Richiede che lo stesso nuovo valore di corrente venga riportato questo numero di volte consecutive prima di cambiare la modalità di luminosità rilevata. ON/OFF vengono applicati immediatamente. 0 disattiva il filtro; il valore predefinito è 2.", "Arrotonda luminosità al 5%", "Arrotonda la luminosità calcolata al 5% più vicino. Disattiva per usare percentuali intere senza passi del 5%."),
    "ja": ("電流安定化フィルター", "検出した明るさモードを変更する前に、同じ新しい電流値がこの回数連続で報告される必要があります。ON/OFF は常に即時反映されます。0 で無効、既定値は 2 です。", "明るさを5%単位に丸める", "計算された明るさを最も近い5%に丸めます。5%刻みを使わず整数パーセントを使用する場合は無効にします。"),
    "ka": ("დენის სტაბილურობის ფილტრი", "სიკაშკაშის რეჟიმის შეცვლამდე იგივე ახალი დენის მნიშვნელობა ზედიზედ ამდენჯერ უნდა დაფიქსირდეს. ON/OFF დაუყოვნებლივ გამოიყენება. 0 თიშავს ფილტრს; ნაგულისხმევია 2.", "სიკაშკაშის დამრგვალება 5%-მდე", "გამოთვლილ სიკაშკაშეს უახლოეს 5%-მდე ამრგვალებს. გამორთეთ მთელი პროცენტების გამოსაყენებლად 5%-იანი ნაბიჯების გარეშე."),
    "ko": ("전류 안정성 필터", "감지된 밝기 모드를 변경하기 전에 동일한 새 전류 값이 이 횟수만큼 연속 보고되어야 합니다. ON/OFF는 즉시 적용됩니다. 0은 필터를 끄며 기본값은 2입니다.", "밝기를 5% 단위로 반올림", "계산된 밝기를 가장 가까운 5%로 반올림합니다. 5% 단계 없이 정수 퍼센트를 사용하려면 끄세요."),
    "lb": ("Stroumstabilitéitsfilter", "Dee selwechten neie Stroumwäert muss esou dacks hannertenee gemellt ginn, ier den Hellegkeetsmodus ännert. ON/OFF gëtt direkt iwwerholl. 0 deaktivéiert de Filter; Standard ass 2.", "Hellegkeet op 5% ronnen", "Rënnt déi berechent Hellegkeet op déi nootste 5%. Desaktivéiert fir ganz Prozent ouni 5%-Schrëtt ze benotzen."),
    "lt": ("Srovės stabilumo filtras", "Prieš keičiant ryškumo režimą ta pati nauja srovės reikšmė turi būti gauta tiek kartų iš eilės. ON/OFF taikoma iš karto. 0 išjungia filtrą; numatyta 2.", "Apvalinti ryškumą iki 5%", "Apskaičiuotą ryškumą suapvalina iki artimiausių 5%. Išjunkite, jei norite naudoti sveikus procentus be 5% žingsnių."),
    "lv": ("Strāvas stabilitātes filtrs", "Pirms spilgtuma režīma maiņas tai pašai jaunajai strāvas vērtībai jābūt saņemtai tik reižu pēc kārtas. ON/OFF tiek piemērots nekavējoties. 0 izslēdz filtru; noklusējums ir 2.", "Noapaļot spilgtumu līdz 5%", "Noapaļo aprēķināto spilgtumu līdz tuvākajiem 5%. Izslēdziet, lai izmantotu veselus procentus bez 5% soļiem."),
    "mk": ("Филтер за стабилност на струјата", "Бара истата нова вредност на струјата да биде пријавена толку пати по ред пред да се смени режимот на осветленост. ON/OFF се применуваат веднаш. 0 го исклучува филтерот; стандардно е 2.", "Заокружи осветленост на 5%", "Ја заокружува пресметаната осветленост на најблиските 5%. Исклучете за цели проценти без чекори од 5%."),
    "ml": ("കറന്റ് സ്ഥിരത ഫിൽറ്റർ", "ബ്രൈറ്റ്നസ് മോഡ് മാറ്റുന്നതിന് മുമ്പ് അതേ പുതിയ കറന്റ് മൂല്യം തുടർച്ചയായി ഇത്ര തവണ റിപ്പോർട്ട് ചെയ്യണം. ON/OFF ഉടൻ പ്രയോഗിക്കും. 0 ഫിൽറ്റർ ഓഫ് ചെയ്യും; ഡീഫോൾട്ട് 2 ആണ്.", "ബ്രൈറ്റ്നസ് 5% ആയി റൗണ്ട് ചെയ്യുക", "കണക്കാക്കിയ ബ്രൈറ്റ്നസ് ഏറ്റവും അടുത്ത 5%-ലേക്ക് റൗണ്ട് ചെയ്യുന്നു. 5% ഘട്ടങ്ങളില്ലാതെ പൂർണ്ണ ശതമാനം ഉപയോഗിക്കാൻ ഇത് ഓഫ് ചെയ്യുക."),
    "nb": ("Filter for strømstabilitet", "Krever at den samme nye strømverdien rapporteres så mange ganger på rad før lysstyrkemodusen endres. ON/OFF brukes umiddelbart. 0 deaktiverer filteret; standard er 2.", "Avrund lysstyrke til 5%", "Avrunder beregnet lysstyrke til nærmeste 5 %. Deaktiver for å bruke hele prosenter uten trinn på 5 %."),
    "nl": ("Stroomstabiliteitsfilter", "Vereist dat dezelfde nieuwe stroomwaarde dit aantal keren achter elkaar wordt gemeld voordat de helderheidsmodus verandert. ON/OFF wordt direct toegepast. 0 schakelt het filter uit; standaard is 2.", "Helderheid afronden op 5%", "Rondt de berekende helderheid af op de dichtstbijzijnde 5%. Schakel uit om hele percentages zonder stappen van 5% te gebruiken."),
    "nn": ("Filter for straumstabilitet", "Krev at den same nye straumverdien blir rapportert så mange gonger på rad før lysstyrkemodusen blir endra. ON/OFF blir brukt med ein gong. 0 slår av filteret; standard er 2.", "Rund lysstyrke til 5%", "Rundar berekna lysstyrke til næraste 5 %. Slå av for å bruke heile prosent utan steg på 5 %."),
    "pl": ("Filtr stabilności prądu", "Wymaga, aby ta sama nowa wartość prądu została zgłoszona tyle razy z rzędu przed zmianą wykrytego trybu jasności. ON/OFF są stosowane natychmiast. 0 wyłącza filtr; domyślnie 2.", "Zaokrąglaj jasność do 5%", "Zaokrągla obliczoną jasność do najbliższych 5%. Wyłącz, aby używać pełnych procentów bez kroków co 5%."),
    "pt": ("Filtro de estabilidade da corrente", "Exige que o mesmo novo valor de corrente seja comunicado este número de vezes seguidas antes de alterar o modo de brilho detetado. ON/OFF são aplicados imediatamente. 0 desativa o filtro; o valor predefinido é 2.", "Arredondar brilho para 5%", "Arredonda o brilho calculado para os 5% mais próximos. Desative para usar percentagens inteiras sem passos de 5%."),
    "pt-BR": ("Filtro de estabilidade da corrente", "Exige que o mesmo novo valor de corrente seja informado esta quantidade de vezes seguidas antes de alterar o modo de brilho detectado. ON/OFF são aplicados imediatamente. 0 desativa o filtro; o padrão é 2.", "Arredondar brilho para 5%", "Arredonda o brilho calculado para os 5% mais próximos. Desative para usar percentuais inteiros sem passos de 5%."),
    "ro": ("Filtru de stabilitate a curentului", "Necesită ca aceeași valoare nouă a curentului să fie raportată de atâtea ori consecutiv înainte de schimbarea modului de luminozitate. ON/OFF se aplică imediat. 0 dezactivează filtrul; implicit este 2.", "Rotunjire luminozitate la 5%", "Rotunjește luminozitatea calculată la cel mai apropiat 5%. Dezactivați pentru procente întregi fără pași de 5%."),
    "ru": ("Фильтр стабильности тока", "Требует получить одно и то же новое значение тока указанное число раз подряд, прежде чем менять определённый режим яркости. ON/OFF применяются сразу. 0 отключает фильтр; значение по умолчанию — 2.", "Округлять яркость до 5%", "Округляет рассчитанную яркость до ближайших 5%. Отключите, чтобы использовать целые проценты без шага 5%."),
    "sk": ("Filter stability prúdu", "Pred zmenou režimu jasu vyžaduje, aby bola rovnaká nová hodnota prúdu nahlásená toľkokrát za sebou. ON/OFF sa použije okamžite. 0 filter vypne; predvolené je 2.", "Zaokrúhľovať jas na 5%", "Zaokrúhli vypočítaný jas na najbližších 5 %. Vypnite pre celé percentá bez krokov po 5 %."),
    "sl": ("Filter stabilnosti toka", "Pred spremembo načina svetlosti mora biti ista nova vrednost toka sporočena tolikokrat zapored. ON/OFF se uporabi takoj. 0 izklopi filter; privzeto je 2.", "Zaokroži svetlost na 5%", "Zaokroži izračunano svetlost na najbližjih 5%. Izklopite za cele odstotke brez korakov po 5%."),
    "sq": ("Filtri i stabilitetit të rrymës", "Kërkon që e njëjta vlerë e re e rrymës të raportohet kaq herë radhazi para ndryshimit të modalitetit të ndriçimit. ON/OFF zbatohen menjëherë. 0 çaktivizon filtrin; parazgjedhja është 2.", "Rrumbullakos ndriçimin në 5%", "Rrumbullakos ndriçimin e llogaritur në 5% më të afërt. Çaktivizojeni për përqindje të plota pa hapa 5%."),
    "sr": ("Филтер стабилности струје", "Захтева да иста нова вредност струје буде пријављена оволико пута заредом пре промене режима осветљености. ON/OFF се примењују одмах. 0 искључује филтер; подразумевано је 2.", "Заокружи осветљеност на 5%", "Заокружује израчунату осветљеност на најближих 5%. Искључите за целе проценте без корака од 5%."),
    "sr-Latn": ("Filter stabilnosti struje", "Zahteva da ista nova vrednost struje bude prijavljena ovoliko puta zaredom pre promene režima osvetljenosti. ON/OFF se primenjuju odmah. 0 isključuje filter; podrazumevano je 2.", "Zaokruži osvetljenost na 5%", "Zaokružuje izračunatu osvetljenost na najbližih 5%. Isključite za cele procente bez koraka od 5%."),
    "sv": ("Filter för strömstabilitet", "Kräver att samma nya strömvärde rapporteras så här många gånger i rad innan ljusstyrkeläget ändras. ON/OFF tillämpas direkt. 0 inaktiverar filtret; standard är 2.", "Avrunda ljusstyrka till 5%", "Avrundar beräknad ljusstyrka till närmaste 5 %. Inaktivera för hela procent utan steg på 5 %."),
    "ta": ("மின்னோட்ட நிலைத்தன்மை வடிகட்டி", "பிரகாச நிலையை மாற்றும் முன் அதே புதிய மின்னோட்ட மதிப்பு தொடர்ந்து இத்தனை முறை அறிக்கையிடப்பட வேண்டும். ON/OFF உடனடியாக செயல்படும். 0 வடிகட்டியை முடக்கும்; இயல்புநிலை 2.", "பிரகாசத்தை 5% ஆக வட்டமிடு", "கணக்கிடப்பட்ட பிரகாசத்தை அருகிலுள்ள 5%-க்கு வட்டமிடும். 5% படிகள் இல்லாமல் முழு சதவீதங்களை பயன்படுத்த இதை முடக்கவும்."),
    "te": ("కరెంట్ స్థిరత్వ ఫిల్టర్", "బ్రైట్‌నెస్ మోడ్ మార్చే ముందు అదే కొత్త కరెంట్ విలువ వరుసగా ఇన్ని సార్లు రిపోర్ట్ కావాలి. ON/OFF వెంటనే అమలవుతాయి. 0 ఫిల్టర్‌ను ఆపుతుంది; డిఫాల్ట్ 2.", "బ్రైట్‌నెస్‌ను 5%కు రౌండ్ చేయి", "లెక్కించిన బ్రైట్‌నెస్‌ను సమీప 5%కు రౌండ్ చేస్తుంది. 5% దశలు లేకుండా పూర్తి శాతాలను ఉపయోగించడానికి దీన్ని ఆఫ్ చేయండి."),
    "th": ("ตัวกรองความเสถียรของกระแส", "ต้องได้รับค่ากระแสใหม่ค่าเดิมติดต่อกันตามจำนวนนี้ก่อนเปลี่ยนโหมดความสว่างที่ตรวจพบ ON/OFF มีผลทันที ค่า 0 ปิดตัวกรอง; ค่าเริ่มต้นคือ 2", "ปัดความสว่างเป็นช่วง 5%", "ปัดค่าความสว่างที่คำนวณได้เป็น 5% ที่ใกล้ที่สุด ปิดตัวเลือกนี้เพื่อใช้เปอร์เซ็นต์จำนวนเต็มโดยไม่มีขั้น 5%"),
    "tr": ("Akım kararlılığı filtresi", "Algılanan parlaklık modu değişmeden önce aynı yeni akım değerinin bu kadar kez art arda raporlanmasını gerektirir. ON/OFF hemen uygulanır. 0 filtreyi kapatır; varsayılan 2'dir.", "Parlaklığı %5'e yuvarla", "Hesaplanan parlaklığı en yakın %5'e yuvarlar. %5 adımları olmadan tam yüzdeler kullanmak için kapatın."),
    "uk": ("Фільтр стабільності струму", "Вимагає отримати однакове нове значення струму вказану кількість разів поспіль перед зміною визначеного режиму яскравості. ON/OFF застосовуються одразу. 0 вимикає фільтр; типове значення — 2.", "Округляти яскравість до 5%", "Округлює розраховану яскравість до найближчих 5%. Вимкніть, щоб використовувати цілі відсотки без кроку 5%."),
    "ur": ("کرنٹ استحکام فلٹر", "برائٹنس موڈ بدلنے سے پہلے وہی نیا کرنٹ ویلیو مسلسل اتنی بار رپورٹ ہونا ضروری ہے۔ ON/OFF فوراً لاگو ہوتے ہیں۔ 0 فلٹر بند کرتا ہے؛ ڈیفالٹ 2 ہے۔", "برائٹنس کو 5% پر راؤنڈ کریں", "حساب شدہ برائٹنس کو قریب ترین 5% پر راؤنڈ کرتا ہے۔ 5% مراحل کے بغیر مکمل فیصد استعمال کرنے کے لیے اسے بند کریں۔"),
    "vi": ("Bộ lọc ổn định dòng điện", "Yêu cầu cùng một giá trị dòng điện mới được báo cáo liên tiếp số lần này trước khi đổi chế độ độ sáng. ON/OFF được áp dụng ngay lập tức. 0 tắt bộ lọc; mặc định là 2.", "Làm tròn độ sáng theo 5%", "Làm tròn độ sáng tính toán đến 5% gần nhất. Tắt để dùng phần trăm nguyên không theo bước 5%."),
    "zh-Hans": ("电流稳定性过滤器", "在更改检测到的亮度模式前，要求同一个新的电流值连续报告指定次数。ON/OFF 始终立即生效。0 表示禁用过滤器；默认值为 2。", "亮度按5%取整", "将计算出的亮度舍入到最接近的5%。关闭后可使用不按5%步进的整数百分比。"),
    "zh-Hant": ("電流穩定性過濾器", "在變更偵測到的亮度模式前，要求同一個新的電流值連續回報指定次數。ON/OFF 一律立即生效。0 表示停用過濾器；預設值為 2。", "亮度按5%取整", "將計算出的亮度四捨五入到最接近的5%。關閉後可使用不按5%步進的整數百分比。"),
}


def patch(path: Path, locale: str) -> bool:
    filter_label, filter_help, rounding_label, rounding_help = T[locale]
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    for root, step_name in (("config", "settings"), ("options", "init")):
        step = data.setdefault(root, {}).setdefault("step", {}).setdefault(step_name, {})
        labels = step.setdefault("data", {})
        helpers = step.setdefault("data_description", {})
        desired_labels = {
            "current_stability_samples": filter_label,
            "round_brightness_to_5": rounding_label,
        }
        desired_helpers = {
            "current_stability_samples": filter_help,
            "round_brightness_to_5": rounding_help,
        }
        for key, value in desired_labels.items():
            if labels.get(key) != value:
                labels[key] = value
                changed = True
        for key, value in desired_helpers.items():
            if helpers.get(key) != value:
                helpers[key] = value
                changed = True

    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    locales = sorted(path.stem for path in TRANSLATIONS.glob("*.json"))
    missing = sorted(set(locales) - set(T))
    extra = sorted(set(T) - set(locales))
    if missing or extra:
        raise SystemExit(f"Locale map mismatch. Missing mappings: {missing}; extra mappings: {extra}")

    changed = []
    for locale in locales:
        path = TRANSLATIONS / f"{locale}.json"
        if patch(path, locale):
            changed.append(str(path.relative_to(ROOT)))

    print(f"Updated {len(changed)} files")
    for item in changed:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
