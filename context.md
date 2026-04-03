Cilj projekta je razviti funkcionalan prototip aplikacije koji može:
    • zaprimiti korisnički sadržaj 
    • odrediti radi li se o slici ili videu 
    • proslijediti sadržaj odgovarajućem modelu za analizu 
    • vratiti procjenu je li sadržaj autentičan ili deepfake 
    • prikazati objašnjenje rezultata i osnovnu statistiku analize 
 Faza dizajna arhitekture sustava
Predložena arhitektura
Frontend (Angular)
    • korisničko sučelje za upload slike ili videa 
    • prikaz statusa obrade 
    • prikaz rezultata analize 
    • prikaz statistike i objašnjenja rezultata 
Backend (Python REST API)
    • prihvat i validacija datoteka 
    • prepoznavanje tipa medija 
    • preprocesiranje sadržaja 
    • pozivanje odgovarajućeg modela 
    • generiranje odgovora za frontend 
AI/inference sloj
    • modul za detekciju slike 
    • modul za detekciju videa 
    • normalizacija rezultata različitih modela u jedinstven format 
Primjer toka obrade
    1. Korisnik učita datoteku. 
    2. Frontend šalje datoteku backendu. 
    3. Backend provjerava je li riječ o slici ili videu. 
    4. Backend poziva odgovarajući modul. 
    5. Model vraća rezultat, npr. vjerojatnost deepfake sadržaja. 
    6. Backend formira čitljiv odgovor. 
    7. Frontend prikazuje rezultat i dodatnu statistiku. 
Rezultat faze: dijagram arhitekture, popis API ruta i logika obrade.

Preporučeni podržani formati za upload
Za početnu verziju aplikacije najbolje je ograničiti podržane formate na najčešće i tehnički najjednostavnije:
Slike
    • .jpg 
    • .jpeg 
    • .png 
Video
    • .mp4 
    • .mov 
    • .avi kao opcionalno, ako ga backend može stabilno obraditi

Najbolji izbor za strukturu projekta: DeepfakeBench
Kao baza za projekt, DeepfakeBench je vrlo dobar izbor jer okuplja velik broj implementiranih detektora i dataset protokola u jedinstvenom frameworku. Benchmark je uveden kao standardizirani okvir za usporedbu modela, a aktualni repozitorij podržava desetke image i video detektora. 

Preporuka za slike
Model	Razina težine	Kvaliteta	Opis	Preporuka za projekt
Xception	⭐ Lako	⭐⭐⭐⭐	Klasični CNN model, najčešće korišten u deepfake detekciji	✅ NAJBOLJI izbor za početak
EfficientNet	⭐⭐ Lako-srednje	⭐⭐⭐⭐	Moderniji i efikasniji od Xceptiona	✅ Vrlo dobra alternativa
ResNet (50/101)	⭐⭐ Lako-srednje	⭐⭐⭐	Stabilan baseline model	✔ ako želiš jednostavnost
MobileNet	⭐ Lako	⭐⭐⭐	Lagan model, dobar za brze aplikacije	✔ ako želiš brzu inferenciju
Vision Transformer (ViT)	⭐⭐⭐ Srednje	⭐⭐⭐⭐	Transformer-based model za slike	✔ naprednija verzija

Preporuka za video
Model	Razina težine	Kvaliteta	Opis	Preporuka za projekt
Frame-based (Xception/EfficientNet)	⭐ Lako	⭐⭐⭐	Video se dijeli na frameove → svaki frame se analizira	✅ NAJBOLJI za početak
CNN + LSTM	⭐⭐⭐ Srednje	⭐⭐⭐⭐	Kombinira sliku + vremensku komponentu	✔ dobra srednja opcija

Najbolje javno dostupne baze podataka za testiranje
Dataset	Tip podataka	Veličina	Kvaliteta	Opis	Težina korištenja	Preporuka
FaceForensics++	video + slike	⭐⭐⭐ Srednje (~1000 videa)	⭐⭐⭐⭐	Najčešće korišten dataset, uključuje više metoda manipulacije (Deepfakes, FaceSwap, Face2Face)	⭐ Lako	✅ OBAVEZNO koristiti
Celeb-DF	video	⭐⭐⭐ Srednje	⭐⭐⭐⭐⭐	Realističniji deepfakeovi, bolji za testiranje generalizacije	⭐⭐ Lako-srednje	✅ Preporučeno

 Faza razvoja backenda
Funkcionalnosti backenda
    • endpoint za upload datoteke 
    • validacija veličine i formata datoteke 
    • detekcija vrste medija 
    • obrada slike ili izdvajanje frameova iz videa 
    • pozivanje modela za inferenciju 
    • izračun i oblikovanje rezultata 
    • slanje JSON odgovora frontend aplikaciji 
Moguće API rute
    • POST /analyze – upload i analiza datoteke 
    • GET /health – provjera rada sustava 
    • GET /models – informacije o dostupnim modelima 
Logika obrade
Za slike backend može:
    • učitati sliku 
    • promijeniti dimenzije i normalizirati ulaz 
    • pokrenuti model 
    • vratiti klasifikaciju i postotak pouzdanosti 
Za video backend može:
    • izdvojiti određeni broj frameova 
    • analizirati frameove ili sekvence 
    • agregirati rezultate više frameova 
    • vratiti ukupnu procjenu i eventualne sumnjive segmente 

Faza razvoja frontenda
Frontend u Angularu treba korisniku omogućiti jednostavno i razumljivo korištenje sustava. Fokus treba biti na jasnoći, jednostavnosti i transparentnom prikazu rezultata.
Glavni dijelovi sučelja
    • početna stranica s opisom svrhe sustava 
    • forma za upload datoteke 
    • prikaz učitane slike ili osnovnih podataka o videu 
    • indikator obrade 
    • stranica ili komponenta s rezultatima analize 
Što prikazati korisniku nakon analize
    • je li sadržaj vjerojatno autentičan ili deepfake 
    • razina sigurnosti modela, npr. u postocima 
    • korišteni tip analize 
    • sažeto objašnjenje zašto je sadržaj označen kao sumnjiv 
    • vizualni prikaz statistike, npr. graf, progress bar ili kartice 
