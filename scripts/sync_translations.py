#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "translations"
LOCALES_JS = ROOT / "custom_components" / "smart_plug_multilevel_light" / "static" / "smart-plug-multilevel-light-locales.js"

# Keep these four user-facing strings synchronized in every supported locale.
# Obsolete description keys are removed so every locale matches strings.json.
# They intentionally stay concise; High/Medium/Low/Dim are mode-name examples and remain unchanged.
T = {
    "af": ("Slegs stroomsensors wat aan die gekose slimprop behoort, is hier beskikbaar.", "Gewoonlik is geen ekstra vertraging nodig nie. As 'n lamp wat met sy eie knoppie afgeskakel is nie vanuit Home Assistant aanskakel nie, stel 'n klein vertraging in, byvoorbeeld 0,7 s.", "Leer eers die helderheidsmodusse van 'n nuwe lamp. Gebruik die fisiese knoppie op die lamp om elke helderheidsvlak te kies en voeg dit hieronder by, byvoorbeeld High, Medium, Low en Dim.", "Byvoorbeeld: High, Medium, Low of Dim."),
    "ar": ("لا تتوفر هنا إلا مستشعرات التيار التابعة للمقبس الذكي المحدد.", "عادةً لا يلزم أي تأخير إضافي. إذا لم يضئ المصباح الذي أُطفئ بزرّه عند تشغيله من Home Assistant، فاضبط تأخيرًا صغيرًا، مثل 0.7 ثانية.", "علّم التكامل أولًا أوضاع سطوع المصباح الجديد. استخدم الزر الفعلي على المصباح لاختيار كل مستوى سطوع وأضفه أدناه، مثل High وMedium وLow وDim.", "مثال: High أو Medium أو Low أو Dim."),
    "bg": ("Тук са достъпни само сензорите за ток, принадлежащи на избрания умен контакт.", "Обикновено не е нужно допълнително забавяне. Ако лампа, изключена от собствения ѝ бутон, не се включва от Home Assistant, задайте малко забавяне, например 0,7 s.", "Първо обучете интеграцията на режимите на яркост на новата лампа. С физическия бутон на лампата изберете всяко ниво и го добавете по-долу, например High, Medium, Low и Dim.", "Например: High, Medium, Low или Dim."),
    "bn": ("এখানে শুধু নির্বাচিত স্মার্ট প্লাগের কারেন্ট সেন্সরগুলোই উপলভ্য।", "সাধারণত অতিরিক্ত বিলম্বের দরকার হয় না। ল্যাম্পের নিজস্ব বোতাম দিয়ে বন্ধ করার পর Home Assistant থেকে চালু না হলে ছোট একটি বিলম্ব দিন, যেমন 0.7 s।", "নতুন ল্যাম্পের উজ্জ্বলতার মোডগুলো আগে ইন্টিগ্রেশনকে শেখান। ল্যাম্পের ফিজিক্যাল বোতাম দিয়ে প্রতিটি উজ্জ্বলতার স্তর নির্বাচন করে নিচে যোগ করুন, যেমন High, Medium, Low এবং Dim।", "উদাহরণ: High, Medium, Low বা Dim।"),
    "bs": ("Ovdje su dostupni samo senzori struje koji pripadaju odabranoj pametnoj utičnici.", "Obično nije potrebno dodatno kašnjenje. Ako se lampa ugašena vlastitim dugmetom ne uključi iz Home Assistanta, postavite malo kašnjenje, na primjer 0,7 s.", "Najprije naučite integraciju režimima svjetline nove lampe. Fizičkim dugmetom na lampi odaberite svaki nivo i dodajte ga ispod, na primjer High, Medium, Low i Dim.", "Na primjer: High, Medium, Low ili Dim."),
    "ca": ("Aquí només estan disponibles els sensors de corrent que pertanyen a l'endoll intel·ligent seleccionat.", "Normalment no cal cap retard addicional. Si un llum apagat amb el seu propi botó no s'encén des de Home Assistant, definiu un petit retard, per exemple 0,7 s.", "Primer ensenyeu a la integració els modes de brillantor del llum nou. Amb el botó físic del llum, seleccioneu cada nivell i afegiu-lo a continuació, per exemple High, Medium, Low i Dim.", "Per exemple: High, Medium, Low o Dim."),
    "cs": ("Zde jsou dostupné pouze snímače proudu patřící k vybrané chytré zásuvce.", "Obvykle není potřeba žádné další zpoždění. Pokud se lampa vypnutá vlastním tlačítkem nezapne z Home Assistantu, nastavte malé zpoždění, například 0,7 s.", "Nejprve integraci naučte režimy jasu nové lampy. Fyzickým tlačítkem na lampě vyberte jednotlivé úrovně a přidejte je níže, například High, Medium, Low a Dim.", "Například: High, Medium, Low nebo Dim."),
    "cy": ("Dim ond synwyryddion cerrynt sy'n perthyn i'r plwg clyfar a ddewiswyd sydd ar gael yma.", "Fel arfer nid oes angen oedi ychwanegol. Os nad yw lamp a ddiffoddwyd â'i botwm ei hun yn troi ymlaen o Home Assistant, gosodwch oedi bach, er enghraifft 0.7 s.", "Yn gyntaf dysgwch foddau disgleirdeb y lamp newydd i'r integreiddiad. Defnyddiwch fotwm corfforol y lamp i ddewis pob lefel a'i hychwanegu isod, er enghraifft High, Medium, Low a Dim.", "Er enghraifft: High, Medium, Low neu Dim."),
    "da": ("Kun strømsensorer, der hører til den valgte smart-stikdåse, er tilgængelige her.", "Normalt er der ikke behov for ekstra forsinkelse. Hvis en lampe, der er slukket med sin egen knap, ikke tænder fra Home Assistant, så indstil en lille forsinkelse, f.eks. 0,7 s.", "Lær først integrationen den nye lampes lysstyrketilstande. Brug lampens fysiske knap til at vælge hvert niveau og tilføj det nedenfor, f.eks. High, Medium, Low og Dim.", "For eksempel: High, Medium, Low eller Dim."),
    "de": ("Hier sind nur Stromsensoren verfügbar, die zur ausgewählten Smart-Steckdose gehören.", "Normalerweise ist keine zusätzliche Verzögerung erforderlich. Wenn sich eine mit ihrer eigenen Taste ausgeschaltete Lampe nicht über Home Assistant einschalten lässt, stellen Sie eine kleine Verzögerung ein, z. B. 0,7 s.", "Lernen Sie zuerst die Helligkeitsstufen der neuen Lampe an. Wählen Sie mit der physischen Taste der Lampe jede Stufe aus und fügen Sie sie unten hinzu, z. B. High, Medium, Low und Dim.", "Zum Beispiel: High, Medium, Low oder Dim."),
    "el": ("Εδώ είναι διαθέσιμοι μόνο οι αισθητήρες ρεύματος που ανήκουν στην επιλεγμένη έξυπνη πρίζα.", "Συνήθως δεν χρειάζεται πρόσθετη καθυστέρηση. Αν μια λάμπα που έκλεισε από το δικό της κουμπί δεν ανάβει από το Home Assistant, ορίστε μια μικρή καθυστέρηση, π.χ. 0,7 s.", "Πρώτα εκπαιδεύστε την ενσωμάτωση στις λειτουργίες φωτεινότητας της νέας λάμπας. Με το φυσικό κουμπί της λάμπας επιλέξτε κάθε επίπεδο και προσθέστε το παρακάτω, π.χ. High, Medium, Low και Dim.", "Για παράδειγμα: High, Medium, Low ή Dim."),
    "en": ("Only current sensors belonging to the selected smart plug are available here.", "Usually no additional delay is needed. If a lamp switched off with its own button does not turn on from Home Assistant, set a small delay, for example 0.7 s.", "For a new lamp, first teach the integration its brightness modes. Use the physical button on the lamp to select each brightness level and add it below, for example High, Medium, Low, and Dim.", "For example: High, Medium, Low, or Dim."),
    "en-GB": ("Only current sensors belonging to the selected smart plug are available here.", "Usually no additional delay is needed. If a lamp switched off with its own button does not turn on from Home Assistant, set a small delay, for example 0.7 s.", "For a new lamp, first teach the integration its brightness modes. Use the physical button on the lamp to select each brightness level and add it below, for example High, Medium, Low, and Dim.", "For example: High, Medium, Low, or Dim."),
    "eo": ("Ĉi tie disponeblas nur kurentosensiloj apartenantaj al la elektita inteligenta ingo.", "Kutime ne necesas aldona prokrasto. Se lampo malŝaltita per sia propra butono ne ŝaltiĝas el Home Assistant, agordu malgrandan prokraston, ekzemple 0,7 s.", "Unue instruu al la integriĝo la brilreĝimojn de la nova lampo. Per la fizika butono de la lampo elektu ĉiun nivelon kaj aldonu ĝin sube, ekzemple High, Medium, Low kaj Dim.", "Ekzemple: High, Medium, Low aŭ Dim."),
    "es": ("Aquí solo están disponibles los sensores de corriente que pertenecen al enchufe inteligente seleccionado.", "Normalmente no se necesita ningún retraso adicional. Si una lámpara apagada con su propio botón no se enciende desde Home Assistant, establece un pequeño retraso, por ejemplo 0,7 s.", "Primero enseña a la integración los modos de brillo de la nueva lámpara. Usa el botón físico de la lámpara para seleccionar cada nivel y añadirlo abajo, por ejemplo High, Medium, Low y Dim.", "Por ejemplo: High, Medium, Low o Dim."),
    "es-419": ("Aquí solo están disponibles los sensores de corriente que pertenecen al enchufe inteligente seleccionado.", "Normalmente no se necesita ningún retraso adicional. Si una lámpara apagada con su propio botón no se enciende desde Home Assistant, configura un pequeño retraso, por ejemplo 0,7 s.", "Primero enseña a la integración los modos de brillo de la nueva lámpara. Usa el botón físico de la lámpara para seleccionar cada nivel y agregarlo abajo, por ejemplo High, Medium, Low y Dim.", "Por ejemplo: High, Medium, Low o Dim."),
    "et": ("Siin on saadaval ainult valitud nutipistikule kuuluvad vooluandurid.", "Tavaliselt pole lisaviivitust vaja. Kui oma nupust välja lülitatud lamp ei lülitu Home Assistantist sisse, määrake väike viivitus, näiteks 0,7 s.", "Kõigepealt õpetage integratsioonile uue lambi heledusrežiimid. Valige lambi füüsilise nupuga iga tase ja lisage see allpool, näiteks High, Medium, Low ja Dim.", "Näiteks: High, Medium, Low või Dim."),
    "eu": ("Hemen hautatutako entxufe adimendunari dagozkion korronte-sentsoreak bakarrik daude erabilgarri.", "Normalean ez da atzerapen gehigarririk behar. Bere botoiarekin itzalitako lanpara Home Assistant-etik pizten ez bada, ezarri atzerapen txiki bat, adibidez 0,7 s.", "Lehenik, irakatsi integrazioari lanpara berriaren distira-moduak. Lanpararen botoi fisikoarekin hautatu maila bakoitza eta gehitu behean, adibidez High, Medium, Low eta Dim.", "Adibidez: High, Medium, Low edo Dim."),
    "fa": ("در اینجا فقط حسگرهای جریان متعلق به پریز هوشمند انتخاب‌شده در دسترس هستند.", "معمولاً نیازی به تأخیر اضافی نیست. اگر چراغی که با دکمه خودش خاموش شده از Home Assistant روشن نمی‌شود، یک تأخیر کوتاه، مثلاً ۰٫۷ ثانیه تنظیم کنید.", "ابتدا حالت‌های روشنایی چراغ جدید را به یکپارچه‌سازی آموزش دهید. با دکمه فیزیکی چراغ هر سطح را انتخاب و در پایین اضافه کنید، مثلاً High، Medium، Low و Dim.", "برای مثال: High، Medium، Low یا Dim."),
    "fi": ("Tässä ovat käytettävissä vain valittuun älypistorasiaan kuuluvat virta-anturit.", "Yleensä lisäviivettä ei tarvita. Jos omasta painikkeestaan sammutettu lamppu ei syty Home Assistantista, aseta pieni viive, esimerkiksi 0,7 s.", "Opeta ensin integraatiolle uuden lampun kirkkaustilat. Valitse lampun fyysisellä painikkeella jokainen taso ja lisää se alle, esimerkiksi High, Medium, Low ja Dim.", "Esimerkiksi: High, Medium, Low tai Dim."),
    "fr": ("Seuls les capteurs de courant appartenant à la prise intelligente sélectionnée sont disponibles ici.", "En général, aucun délai supplémentaire n'est nécessaire. Si une lampe éteinte avec son propre bouton ne s'allume pas depuis Home Assistant, définissez un petit délai, par exemple 0,7 s.", "Commencez par apprendre à l'intégration les modes de luminosité de la nouvelle lampe. Utilisez le bouton physique de la lampe pour sélectionner chaque niveau et l'ajouter ci-dessous, par exemple High, Medium, Low et Dim.", "Par exemple : High, Medium, Low ou Dim."),
    "fy": ("Hjir binne allinnich stroomsensors beskikber dy't by de selektearre smartstekker hearre.", "Meastal is gjin ekstra fertraging nedich. As in lampe dy't mei de eigen knop útset is net oangiet fanút Home Assistant, stel dan in lytse fertraging yn, bygelyks 0,7 s.", "Lear de yntegraasje earst de helderheidsmodi fan de nije lampe. Selektearje mei de fysike knop op de lampe elk nivo en foegje it hjirûnder ta, bygelyks High, Medium, Low en Dim.", "Bygelyks: High, Medium, Low of Dim."),
    "ga": ("Níl ar fáil anseo ach braiteoirí srutha a bhaineann leis an soicéad cliste roghnaithe.", "De ghnáth ní bhíonn moill bhreise de dhíth. Mura lasann lampa a múchadh lena chnaipe féin ó Home Assistant, socraigh moill bheag, mar shampla 0.7 s.", "Ar dtús múin modhanna gile an lampa nua don chomhtháthú. Úsáid cnaipe fisiciúil an lampa chun gach leibhéal a roghnú agus cuir leis thíos é, mar shampla High, Medium, Low agus Dim.", "Mar shampla: High, Medium, Low nó Dim."),
    "gl": ("Aquí só están dispoñibles os sensores de corrente que pertencen ao enchufe intelixente seleccionado.", "Normalmente non é necesario ningún atraso adicional. Se unha lámpada apagada co seu propio botón non acende desde Home Assistant, define un pequeno atraso, por exemplo 0,7 s.", "Primeiro ensina á integración os modos de brillo da nova lámpada. Usa o botón físico da lámpada para seleccionar cada nivel e engadilo abaixo, por exemplo High, Medium, Low e Dim.", "Por exemplo: High, Medium, Low ou Dim."),
    "gsw": ("Da sind nur Stromsensoren verfügbar, wo zur ausgewählten Smart-Steckdose ghöred.", "Normalerwiis bruuchts kei zusätzligi Verzögerig. Wenn e Lampe, wo mit ihrem eigene Chnopf usgschaltet wurde, nöd über Home Assistant aagoht, stell e chliini Verzögerig ii, zum Biispiel 0,7 s.", "Lern zerscht d'Helligkeitsstufe vo de neue Lampe aa. Wähl mit em physische Chnopf vo de Lampe jedi Stufe und füeg si unde hinzu, zum Biispiel High, Medium, Low und Dim.", "Zum Biispiel: High, Medium, Low oder Dim."),
    "he": ("כאן זמינים רק חיישני זרם השייכים לשקע החכם שנבחר.", "בדרך כלל אין צורך בהשהיה נוספת. אם מנורה שכובתה באמצעות הכפתור שלה לא נדלקת מ-Home Assistant, הגדר השהיה קצרה, למשל 0.7 שניות.", "תחילה למד את האינטגרציה את מצבי הבהירות של המנורה החדשה. השתמש בכפתור הפיזי במנורה כדי לבחור כל רמה ולהוסיף אותה למטה, למשל High, Medium, Low ו-Dim.", "לדוגמה: High, Medium, Low או Dim."),
    "hi": ("यहाँ केवल चुने गए स्मार्ट प्लग से जुड़े करंट सेंसर उपलब्ध हैं।", "आमतौर पर अतिरिक्त देरी की जरूरत नहीं होती। यदि अपने बटन से बंद किया गया लैंप Home Assistant से चालू नहीं होता, तो थोड़ी देरी सेट करें, जैसे 0.7 s।", "पहले इंटीग्रेशन को नए लैंप के ब्राइटनेस मोड सिखाएँ। लैंप के भौतिक बटन से हर स्तर चुनें और नीचे जोड़ें, जैसे High, Medium, Low और Dim।", "उदाहरण: High, Medium, Low या Dim।"),
    "hr": ("Ovdje su dostupni samo senzori struje koji pripadaju odabranoj pametnoj utičnici.", "Obično nije potrebna dodatna odgoda. Ako se svjetiljka ugašena vlastitim gumbom ne uključi iz Home Assistanta, postavite malu odgodu, primjerice 0,7 s.", "Najprije naučite integraciju načinima svjetline nove svjetiljke. Fizičkim gumbom na svjetiljci odaberite svaku razinu i dodajte je ispod, primjerice High, Medium, Low i Dim.", "Na primjer: High, Medium, Low ili Dim."),
    "hu": ("Itt csak a kiválasztott okoskonnektorhoz tartozó áramérzékelők érhetők el.", "Általában nincs szükség további késleltetésre. Ha a saját gombjával kikapcsolt lámpa nem kapcsol be a Home Assistantból, állítson be kis késleltetést, például 0,7 s-ot.", "Először tanítsa meg az integrációnak az új lámpa fényerőmódjait. A lámpa fizikai gombjával válassza ki az egyes szinteket, és adja hozzá őket lent, például High, Medium, Low és Dim.", "Például: High, Medium, Low vagy Dim."),
    "hy": ("Այստեղ հասանելի են միայն ընտրված խելացի վարդակին պատկանող հոսանքի սենսորները։", "Սովորաբար լրացուցիչ ուշացում պետք չէ։ Եթե իր կոճակով անջատված լամպը Home Assistant-ից չի միանում, սահմանեք փոքր ուշացում, օրինակ՝ 0.7 վրկ։", "Նախ ինտեգրմանը սովորեցրեք նոր լամպի պայծառության ռեժիմները։ Լամպի ֆիզիկական կոճակով ընտրեք յուրաքանչյուր մակարդակը և ավելացրեք ստորև, օրինակ՝ High, Medium, Low և Dim։", "Օրինակ՝ High, Medium, Low կամ Dim։"),
    "id": ("Hanya sensor arus milik smart plug yang dipilih yang tersedia di sini.", "Biasanya tidak diperlukan penundaan tambahan. Jika lampu yang dimatikan dengan tombolnya sendiri tidak menyala dari Home Assistant, atur penundaan kecil, misalnya 0,7 s.", "Pertama, ajarkan mode kecerahan lampu baru ke integrasi. Gunakan tombol fisik pada lampu untuk memilih setiap tingkat dan tambahkan di bawah, misalnya High, Medium, Low, dan Dim.", "Contoh: High, Medium, Low, atau Dim."),
    "is": ("Hér eru aðeins straumskynjarar sem tilheyra valda snjalltenglinum tiltækir.", "Venjulega þarf enga viðbótartöf. Ef lampi sem slökkt var á með eigin hnappi kviknar ekki úr Home Assistant skaltu stilla litla töf, til dæmis 0,7 s.", "Kenndu fyrst samþættingunni birtustillingar nýja lampans. Notaðu hnappinn á lampanum til að velja hvert stig og bættu því við hér fyrir neðan, til dæmis High, Medium, Low og Dim.", "Til dæmis: High, Medium, Low eða Dim."),
    "it": ("Qui sono disponibili solo i sensori di corrente appartenenti alla presa smart selezionata.", "Di solito non è necessario alcun ritardo aggiuntivo. Se una lampada spenta con il proprio pulsante non si accende da Home Assistant, imposta un piccolo ritardo, ad esempio 0,7 s.", "Per prima cosa insegna all'integrazione le modalità di luminosità della nuova lampada. Usa il pulsante fisico della lampada per selezionare ogni livello e aggiungerlo qui sotto, ad esempio High, Medium, Low e Dim.", "Ad esempio: High, Medium, Low o Dim."),
    "ja": ("ここでは、選択したスマートプラグに属する電流センサーのみ利用できます。", "通常、追加の遅延は不要です。ランプ本体のボタンで消灯した後、Home Assistant から点灯できない場合は、0.7 秒などの短い遅延を設定してください。", "新しいランプでは、最初に明るさモードを統合に学習させます。ランプ本体の物理ボタンで各明るさレベルを選び、下に追加してください。例: High、Medium、Low、Dim。", "例: High、Medium、Low、Dim。"),
    "ka": ("აქ ხელმისაწვდომია მხოლოდ არჩეულ ჭკვიან როზეტთან დაკავშირებული დენის სენსორები.", "ჩვეულებრივ დამატებითი დაყოვნება საჭირო არ არის. თუ საკუთარი ღილაკით გამორთული ნათურა Home Assistant-იდან არ ირთვება, დააყენეთ მცირე დაყოვნება, მაგალითად 0,7 s.", "ჯერ ინტეგრაციას ასწავლეთ ახალი ნათურის სიკაშკაშის რეჟიმები. ნათურის ფიზიკური ღილაკით აირჩიეთ თითოეული დონე და დაამატეთ ქვემოთ, მაგალითად High, Medium, Low და Dim.", "მაგალითად: High, Medium, Low ან Dim."),
    "ko": ("여기에서는 선택한 스마트 플러그에 속한 전류 센서만 사용할 수 있습니다.", "일반적으로 추가 지연은 필요하지 않습니다. 램프 자체 버튼으로 끈 뒤 Home Assistant에서 켜지지 않으면 0.7초와 같은 짧은 지연을 설정하세요.", "새 램프는 먼저 밝기 모드를 통합에 학습시켜야 합니다. 램프의 물리 버튼으로 각 밝기 단계를 선택해 아래에 추가하세요. 예: High, Medium, Low, Dim.", "예: High, Medium, Low 또는 Dim."),
    "lb": ("Hei sinn nëmmen Stroumsensoren verfügbar, déi zu der ausgewielter Smart-Steckdous gehéieren.", "Normalerweis ass keng zousätzlech Verzögerung néideg. Wann eng Luucht, déi mat hirem eegene Knäppchen ausgeschalt gouf, net aus Home Assistant uschalt, setzt eng kleng Verzögerung, zum Beispill 0,7 s.", "Léiert als éischt d'Hellegkeetsmodi vun der neier Luucht un. Wielt mam physesche Knäppchen op der Luucht all Niveau a füügt en hei drënner bäi, zum Beispill High, Medium, Low an Dim.", "Zum Beispill: High, Medium, Low oder Dim."),
    "lt": ("Čia pasiekiami tik pasirinktam išmaniajam lizdui priklausantys srovės jutikliai.", "Paprastai papildomo delsimo nereikia. Jei savo mygtuku išjungta lempa neįsijungia iš Home Assistant, nustatykite nedidelį delsą, pavyzdžiui, 0,7 s.", "Pirmiausia išmokykite integraciją naujos lempos ryškumo režimų. Fiziniu lempos mygtuku pasirinkite kiekvieną lygį ir pridėkite jį žemiau, pavyzdžiui, High, Medium, Low ir Dim.", "Pavyzdžiui: High, Medium, Low arba Dim."),
    "lv": ("Šeit ir pieejami tikai izvēlētajai viedajai kontaktligzdai piederošie strāvas sensori.", "Parasti papildu aizture nav nepieciešama. Ja lampa, kas izslēgta ar savu pogu, neieslēdzas no Home Assistant, iestatiet nelielu aizturi, piemēram, 0,7 s.", "Vispirms iemāciet integrācijai jaunās lampas spilgtuma režīmus. Ar lampas fizisko pogu izvēlieties katru līmeni un pievienojiet to zemāk, piemēram, High, Medium, Low un Dim.", "Piemēram: High, Medium, Low vai Dim."),
    "mk": ("Тука се достапни само сензорите за струја што припаѓаат на избраниот паметен приклучок.", "Обично не е потребно дополнително доцнење. Ако светилка исклучена со сопственото копче не се вклучува од Home Assistant, поставете мало доцнење, на пример 0,7 s.", "Прво научете ја интеграцијата на режимите на осветленост на новата светилка. Со физичкото копче на светилката изберете го секое ниво и додајте го подолу, на пример High, Medium, Low и Dim.", "На пример: High, Medium, Low или Dim."),
    "ml": ("തിരഞ്ഞെടുത്ത സ്മാർട്ട് പ്ലഗിനോടു ബന്ധപ്പെട്ട കറന്റ് സെൻസറുകൾ മാത്രമാണ് ഇവിടെ ലഭ്യമാകുന്നത്.", "സാധാരണയായി അധിക വൈകൽ ആവശ്യമില്ല. സ്വന്തം ബട്ടൺ ഉപയോഗിച്ച് ഓഫ് ചെയ്ത ലാമ്പ് Home Assistant-ൽ നിന്ന് ഓൺ ആകുന്നില്ലെങ്കിൽ 0.7 s പോലുള്ള ചെറിയ വൈകൽ സജ്ജമാക്കുക.", "ആദ്യം പുതിയ ലാമ്പിന്റെ ബ്രൈറ്റ്നസ് മോഡുകൾ ഇന്റഗ്രേഷനെ പഠിപ്പിക്കുക. ലാമ്പിലെ ഫിസിക്കൽ ബട്ടൺ ഉപയോഗിച്ച് ഓരോ ലെവലും തിരഞ്ഞെടുത്ത് താഴെ ചേർക്കുക, ഉദാഹരണത്തിന് High, Medium, Low, Dim.", "ഉദാഹരണം: High, Medium, Low അല്ലെങ്കിൽ Dim."),
    "nb": ("Bare strømsensorer som tilhører den valgte smartpluggen er tilgjengelige her.", "Vanligvis trengs ingen ekstra forsinkelse. Hvis en lampe som er slått av med sin egen knapp ikke slår seg på fra Home Assistant, sett en liten forsinkelse, for eksempel 0,7 s.", "Lær først integrasjonen lysstyrkemodusene til den nye lampen. Bruk den fysiske knappen på lampen til å velge hvert nivå og legg det til nedenfor, for eksempel High, Medium, Low og Dim.", "For eksempel: High, Medium, Low eller Dim."),
    "nl": ("Hier zijn alleen stroomsensoren beschikbaar die bij de geselecteerde slimme stekker horen.", "Normaal is geen extra vertraging nodig. Als een lamp die met zijn eigen knop is uitgeschakeld niet via Home Assistant inschakelt, stel dan een kleine vertraging in, bijvoorbeeld 0,7 s.", "Leer de integratie eerst de helderheidsstanden van de nieuwe lamp. Selecteer met de fysieke knop op de lamp elk niveau en voeg het hieronder toe, bijvoorbeeld High, Medium, Low en Dim.", "Bijvoorbeeld: High, Medium, Low of Dim."),
    "nn": ("Berre straumsensorar som høyrer til den valde smartpluggen er tilgjengelege her.", "Vanlegvis trengst inga ekstra forseinking. Dersom ei lampe som er slått av med sin eigen knapp ikkje slår seg på frå Home Assistant, set ei lita forseinking, til dømes 0,7 s.", "Lær først integrasjonen lysstyrkemodusane til den nye lampa. Bruk den fysiske knappen på lampa til å velje kvart nivå og legg det til nedanfor, til dømes High, Medium, Low og Dim.", "Til dømes: High, Medium, Low eller Dim."),
    "pl": ("Tutaj dostępne są tylko czujniki prądu należące do wybranego inteligentnego gniazdka.", "Zwykle dodatkowe opóźnienie nie jest potrzebne. Jeśli lampa wyłączona własnym przyciskiem nie włącza się z Home Assistant, ustaw niewielkie opóźnienie, np. 0,7 s.", "Najpierw naucz integrację trybów jasności nowej lampy. Fizycznym przyciskiem na lampie wybierz każdy poziom i dodaj go poniżej, np. High, Medium, Low i Dim.", "Na przykład: High, Medium, Low lub Dim."),
    "pt": ("Aqui só estão disponíveis os sensores de corrente pertencentes à tomada inteligente selecionada.", "Normalmente não é necessário qualquer atraso adicional. Se uma lâmpada desligada pelo próprio botão não ligar a partir do Home Assistant, defina um pequeno atraso, por exemplo 0,7 s.", "Primeiro ensine à integração os modos de brilho da nova lâmpada. Use o botão físico da lâmpada para selecionar cada nível e adicioná-lo abaixo, por exemplo High, Medium, Low e Dim.", "Por exemplo: High, Medium, Low ou Dim."),
    "pt-BR": ("Aqui só estão disponíveis os sensores de corrente pertencentes à tomada inteligente selecionada.", "Normalmente não é necessário atraso adicional. Se uma lâmpada desligada pelo próprio botão não ligar pelo Home Assistant, defina um pequeno atraso, por exemplo 0,7 s.", "Primeiro ensine à integração os modos de brilho da nova lâmpada. Use o botão físico da lâmpada para selecionar cada nível e adicioná-lo abaixo, por exemplo High, Medium, Low e Dim.", "Por exemplo: High, Medium, Low ou Dim."),
    "ro": ("Aici sunt disponibili doar senzorii de curent care aparțin prizei inteligente selectate.", "De obicei nu este necesară nicio întârziere suplimentară. Dacă o lampă oprită cu propriul buton nu pornește din Home Assistant, setați o întârziere mică, de exemplu 0,7 s.", "Mai întâi învățați integrarea modurile de luminozitate ale noii lămpi. Folosiți butonul fizic al lămpii pentru a selecta fiecare nivel și adăugați-l mai jos, de exemplu High, Medium, Low și Dim.", "De exemplu: High, Medium, Low sau Dim."),
    "ru": ("Здесь доступны только датчики тока, относящиеся к выбранной умной розетке.", "Обычно дополнительная задержка не нужна. Если лампа, выключенная собственной кнопкой, не включается из Home Assistant, задайте небольшую задержку, например 0,7 с.", "Для новой лампы сначала обучите интеграцию её режимам яркости. Вручную, кнопкой на самой лампе, выбирайте каждый уровень яркости и добавляйте его ниже, например High, Medium, Low и Dim.", "Например: High, Medium, Low или Dim."),
    "sk": ("Tu sú dostupné iba snímače prúdu patriace k vybranej inteligentnej zásuvke.", "Zvyčajne nie je potrebné žiadne ďalšie oneskorenie. Ak sa lampa vypnutá vlastným tlačidlom nezapne z Home Assistanta, nastavte malé oneskorenie, napríklad 0,7 s.", "Najprv integráciu naučte režimy jasu novej lampy. Fyzickým tlačidlom na lampe vyberte každú úroveň a pridajte ju nižšie, napríklad High, Medium, Low a Dim.", "Napríklad: High, Medium, Low alebo Dim."),
    "sl": ("Tukaj so na voljo samo senzorji toka, ki pripadajo izbrani pametni vtičnici.", "Običajno dodatna zakasnitev ni potrebna. Če se svetilka, izklopljena z lastnim gumbom, ne vklopi iz Home Assistanta, nastavite majhno zakasnitev, na primer 0,7 s.", "Najprej integracijo naučite načine svetlosti nove svetilke. S fizičnim gumbom na svetilki izberite vsako raven in jo dodajte spodaj, na primer High, Medium, Low in Dim.", "Na primer: High, Medium, Low ali Dim."),
    "sq": ("Këtu janë të disponueshëm vetëm sensorët e rrymës që i përkasin prizës inteligjente të zgjedhur.", "Zakonisht nuk nevojitet vonesë shtesë. Nëse një llambë e fikur me butonin e vet nuk ndizet nga Home Assistant, vendosni një vonesë të vogël, p.sh. 0,7 s.", "Fillimisht mësojini integrimit mënyrat e ndriçimit të llambës së re. Me butonin fizik të llambës zgjidhni çdo nivel dhe shtojeni më poshtë, p.sh. High, Medium, Low dhe Dim.", "Për shembull: High, Medium, Low ose Dim."),
    "sr": ("Овде су доступни само сензори струје који припадају изабраној паметној утичници.", "Обично није потребно додатно кашњење. Ако се лампа угашена сопственим дугметом не укључи из Home Assistant-а, подесите мало кашњење, на пример 0,7 s.", "Прво научите интеграцију режимима осветљености нове лампе. Физичким дугметом на лампи изаберите сваки ниво и додајте га испод, на пример High, Medium, Low и Dim.", "На пример: High, Medium, Low или Dim."),
    "sr-Latn": ("Ovde su dostupni samo senzori struje koji pripadaju izabranoj pametnoj utičnici.", "Obično nije potrebno dodatno kašnjenje. Ako se lampa ugašena sopstvenim dugmetom ne uključi iz Home Assistant-a, podesite malo kašnjenje, na primer 0,7 s.", "Prvo naučite integraciju režimima osvetljenosti nove lampe. Fizičkim dugmetom na lampi izaberite svaki nivo i dodajte ga ispod, na primer High, Medium, Low i Dim.", "Na primer: High, Medium, Low ili Dim."),
    "sv": ("Här är bara strömsensorer som tillhör den valda smarta kontakten tillgängliga.", "Vanligtvis behövs ingen extra fördröjning. Om en lampa som stängts av med sin egen knapp inte tänds från Home Assistant, ställ in en liten fördröjning, till exempel 0,7 s.", "Lär först integrationen den nya lampans ljusstyrkelägen. Använd lampans fysiska knapp för att välja varje nivå och lägg till den nedan, till exempel High, Medium, Low och Dim.", "Till exempel: High, Medium, Low eller Dim."),
    "ta": ("இங்கே தேர்ந்தெடுக்கப்பட்ட ஸ்மார்ட் பிளக்கைச் சேர்ந்த மின்னோட்ட சென்சார்கள் மட்டுமே கிடைக்கும்.", "பொதுவாக கூடுதல் தாமதம் தேவையில்லை. தனது சொந்த பொத்தானால் அணைக்கப்பட்ட விளக்கு Home Assistant-இல் இருந்து எரியவில்லை என்றால் 0.7 s போன்ற சிறிய தாமதத்தை அமைக்கவும்.", "முதலில் புதிய விளக்கின் பிரகாச முறைகளை ஒருங்கிணைப்புக்கு கற்பிக்கவும். விளக்கின் இயற்பியல் பொத்தானைப் பயன்படுத்தி ஒவ்வொரு நிலையையும் தேர்ந்தெடுத்து கீழே சேர்க்கவும், உதாரணமாக High, Medium, Low, Dim.", "உதாரணமாக: High, Medium, Low அல்லது Dim."),
    "te": ("ఇక్కడ ఎంచుకున్న స్మార్ట్ ప్లగ్‌కు చెందిన కరెంట్ సెన్సర్లు మాత్రమే అందుబాటులో ఉంటాయి.", "సాధారణంగా అదనపు ఆలస్యం అవసరం లేదు. తన బటన్‌తో ఆఫ్ చేసిన ల్యాంప్ Home Assistant నుండి ఆన్ కాకపోతే 0.7 s వంటి చిన్న ఆలస్యం సెట్ చేయండి.", "ముందుగా కొత్త ల్యాంప్ బ్రైట్‌నెస్ మోడ్‌లను ఇంటిగ్రేషన్‌కు నేర్పండి. ల్యాంప్‌పై ఉన్న భౌతిక బటన్‌తో ప్రతి స్థాయిని ఎంచుకుని క్రింద జోడించండి, ఉదాహరణకు High, Medium, Low, Dim.", "ఉదాహరణకు: High, Medium, Low లేదా Dim."),
    "th": ("ที่นี่จะแสดงเฉพาะเซ็นเซอร์กระแสที่เป็นของสมาร์ทปลั๊กที่เลือกเท่านั้น", "โดยปกติไม่จำเป็นต้องหน่วงเวลาเพิ่มเติม หากหลอดไฟที่ปิดด้วยปุ่มของตัวเองไม่เปิดจาก Home Assistant ให้ตั้งค่าหน่วงเวลาเล็กน้อย เช่น 0.7 s", "สำหรับหลอดไฟใหม่ ให้สอนโหมดความสว่างแก่การผสานรวมก่อน ใช้ปุ่มจริงบนหลอดไฟเลือกแต่ละระดับแล้วเพิ่มด้านล่าง เช่น High, Medium, Low และ Dim", "ตัวอย่าง: High, Medium, Low หรือ Dim"),
    "tr": ("Burada yalnızca seçilen akıllı prize ait akım sensörleri kullanılabilir.", "Genellikle ek gecikme gerekmez. Kendi düğmesiyle kapatılan bir lamba Home Assistant'tan açılmıyorsa küçük bir gecikme ayarlayın, örneğin 0,7 s.", "Önce entegrasyona yeni lambanın parlaklık modlarını öğretin. Lambanın fiziksel düğmesiyle her seviyeyi seçip aşağıya ekleyin, örneğin High, Medium, Low ve Dim.", "Örneğin: High, Medium, Low veya Dim."),
    "uk": ("Тут доступні лише датчики струму, що належать вибраній розумній розетці.", "Зазвичай додаткова затримка не потрібна. Якщо лампа, вимкнена власною кнопкою, не вмикається з Home Assistant, задайте невелику затримку, наприклад 0,7 с.", "Для нової лампи спочатку навчіть інтеграцію її режимам яскравості. Фізичною кнопкою на лампі вибирайте кожен рівень і додавайте його нижче, наприклад High, Medium, Low і Dim.", "Наприклад: High, Medium, Low або Dim."),
    "ur": ("یہاں صرف منتخب اسمارٹ پلگ سے متعلق کرنٹ سینسر دستیاب ہیں۔", "عام طور پر اضافی تاخیر کی ضرورت نہیں ہوتی۔ اگر اپنے بٹن سے بند کیا گیا لیمپ Home Assistant سے آن نہ ہو تو تھوڑی سی تاخیر مقرر کریں، مثلاً 0.7 s۔", "پہلے انٹیگریشن کو نئے لیمپ کے برائٹنس موڈ سکھائیں۔ لیمپ کے فزیکل بٹن سے ہر سطح منتخب کریں اور نیچے شامل کریں، مثلاً High، Medium، Low اور Dim۔", "مثال: High، Medium، Low یا Dim۔"),
    "vi": ("Ở đây chỉ có các cảm biến dòng điện thuộc ổ cắm thông minh đã chọn.", "Thông thường không cần thêm độ trễ. Nếu đèn đã tắt bằng nút riêng không bật từ Home Assistant, hãy đặt một độ trễ nhỏ, ví dụ 0,7 s.", "Trước tiên hãy dạy tích hợp các chế độ độ sáng của đèn mới. Dùng nút vật lý trên đèn để chọn từng mức và thêm bên dưới, ví dụ High, Medium, Low và Dim.", "Ví dụ: High, Medium, Low hoặc Dim."),
    "zh-Hans": ("此处仅提供属于所选智能插座的电流传感器。", "通常不需要额外延迟。如果使用灯具自身按钮关闭后无法从 Home Assistant 开启，请设置一个较短的延迟，例如 0.7 s。", "对于新灯具，请先让集成学习其亮度模式。使用灯具上的实体按钮依次选择每个亮度级别并在下方添加，例如 High、Medium、Low 和 Dim。", "例如：High、Medium、Low 或 Dim。"),
    "zh-Hant": ("此處僅提供屬於所選智慧插座的電流感測器。", "通常不需要額外延遲。如果使用燈具本身的按鈕關閉後無法從 Home Assistant 開啟，請設定較短的延遲，例如 0.7 s。", "對於新燈具，請先讓整合學習其亮度模式。使用燈具上的實體按鈕依序選擇每個亮度級別並在下方新增，例如 High、Medium、Low 和 Dim。", "例如：High、Medium、Low 或 Dim。"),
}


def patch_file(path: Path, locale: str) -> bool:
    power_sensor, power_delay, modes, _ = T[locale]
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    settings = data.setdefault("config", {}).setdefault("step", {}).setdefault("settings", {})
    if "description" in settings:
        settings.pop("description", None)
        changed = True
    desc = settings.setdefault("data_description", {})
    desired = {
        "power_sensor": power_sensor,
        "power_cycle_delay": power_delay,
        "modes": modes,
    }
    desc.pop("current_sensor", None)
    for key, value in desired.items():
        if desc.get(key) != value:
            desc[key] = value
            changed = True

    init = data.setdefault("options", {}).setdefault("step", {}).setdefault("init", {})
    desc = init.setdefault("data_description", {})
    desc.pop("current_sensor", None)
    for key, value in desired.items():
        if desc.get(key) != value:
            desc[key] = value
            changed = True

    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def patch_frontend_locales() -> bool:
    text = LOCALES_JS.read_text(encoding="utf-8")
    original = text

    # Current runtime semantics are −15%; remove stale −10% wording from every locale.
    replacements = [
        (r"10\s?%", "15%"),
        (r"۱۰\s?٪", "۱۵٪"),
        (r"١٠\s?٪", "١٥٪"),
        (r"१०\s?%", "१५%"),
        (r"১০\s?%", "১৫%"),
        (r"๑๐\s?%", "๑๕%"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)

    # Add a localized helper used below the mode-name input. Existing locale objects
    # are single-line objects, so inject the key immediately after measured_current.
    for locale, (_, _, _, mode_help) in T.items():
        marker = re.compile(rf"(\b{re.escape(locale)}:\{{[^\n]*?measured_current:\"(?:[^\"\\]|\\.)*\",)")
        match = marker.search(text)
        if not match:
            continue
        if "mode_name_help:" in match.group(0):
            continue
        escaped = mode_help.replace("\\", "\\\\").replace('"', '\\"')
        text = text[: match.end()] + f'mode_name_help:"{escaped}",' + text[match.end() :]

    if text != original:
        LOCALES_JS.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    locales = sorted(path.stem for path in TRANSLATIONS.glob("*.json"))
    missing = sorted(set(locales) - set(T))
    extra = sorted(set(T) - set(locales))
    if missing or extra:
        raise SystemExit(f"Locale map mismatch. Missing mappings: {missing}; extra mappings: {extra}")

    changed = []
    for locale in locales:
        path = TRANSLATIONS / f"{locale}.json"
        if patch_file(path, locale):
            changed.append(str(path.relative_to(ROOT)))
    if patch_frontend_locales():
        changed.append(str(LOCALES_JS.relative_to(ROOT)))

    print(f"Updated {len(changed)} files")
    for item in changed:
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
