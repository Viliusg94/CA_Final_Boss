Galutinis atsiskaitymas

Egzamino tikslas yra sukurti korektiška algoritmą, kuris kuo tobuliau sugebėtų išspręsti pagrindinį duomenų rinkinio uždavinį ir leistų naudotojams juo lengvai naudotis. Rinkinį rasite čia: https://benchmark.ini.rub.de/gtsrb_dataset.html

Pagrindiniai Uždaviniai:

1. Turite paversti duomenų rinkinį į duomenų bazės rinkinį, tai nereiškia, kad reikia nuotraukas sudėti į duomenų bazę, tiesiog vietoje CSV, kuris yra šalia failų, reikėtų sukurti duomenų bazę, kuri saugotu csv esančius duomenis.

2. Atlikite įvairias ženklų transformacijas (kurios būtų naudingos, ištraukite reikalingus duomenis, šis duomenų rinkinys, jau turi papildomus rinkinius, kuriuose yra įvairūs papildomi elementai, jeigu ištrauksite patys, įvertinimas bus didesnis, bet išgauti papildomus parametrus būtina).

3. Komunikacija su duomenų baze privalo vykti per SQL Alchemy biblioteką

4. Naudotojas privalo galėti įdėti naują savo nuotrauką, su kelio ženklu. Turi būti galima įkelti nuotrauką tiek testavimo tiek treniravimo apmokymui.

5. Turi būti minimali naudotojo sąsają, kad naudotojas galėtų paleisti modelio apmokymą įkėlęs norimas papildomas nuotraukas.

6. Turi būti galimybė naudotojui neįkeliant nuotraukos (nei į testavimą nei treniravimą) gauti rezultatą. T.Y pasirenką pasirinkimą vienos nuotraukos nuspėjimas ir jam išvedamas būtent tos nuotraukos rezultatas.

7. Galutiniai rezultatai taip pat saugomi duomenų bazėje. Naudotojo testai saugomi atskirai priskyrus naudotojui

8. Privalo būti, bent vienas paprastas Modelis (toks, kaip KNN, SVM, Random forest, linear, logistic, Boosting, Arima, K-means ar kitas modelis (ne visi iš išvardytų modelių tinka šitam konkrečiam uždaviniui, įsitikinkite, kad jūsų uždavinys ir modelis yra suderinami))

9. Privalo būti bent vienas Neuroninis tinklas, kuris atliktų spėjimus, pavyzdžiui, RNN, CNN, FEED Forward neural network, Transformer.

10. Palyginti paprastą modelį ir neuroninį tinklą, kuris yra geresnis, padarykite išvadas. Pasirinkite dar vieną modelį savo nuožiūrą (galutiniame variante privalo būti, bent 3 skirtingi modeliai (cnn ir rnn skaitomi, kaip du skirtingi modeliai)

11. Privaloma Neuroniniui tinklui atlikti, bent 20-30 įvairių pakeitimų (įskaitant su hyperparametrais), tai įeina sluoksnių, neuronų kiekio, learning rate, batch size, optimizer ir kitų hyperparametrų keitimas visi šie testai užrašomi išvadų lentelėje.

12. Privalote pateikti kuo daugiau metrikų, tinkančių uždaviniui, tai reiškia neapsiribokite tik viena metrika

13. Privalote pateikti įvairius naudingus grafikus naudotojui paprašius (pavyzdžiui, kokių ženklų daugiausiai) arba sudėtingesnius grafikus, kaip modelio rezultatai atskiroms grupėms nuotraukų. (Čia gali dirbti jūsų fantazija, turi būti, bent 4 prasmingi grafikai).

Pagrindinės sąlygos

1. Neuroninio tinklo panaudojimas sudaro 3 balus (vadinasi, padarius tobulą neuroninį tinklą, gausite +3 balus)

2. Korektiškos išvados su įvairių hyperparametrų testavimo rezultatais ir tekstinėmis išvadomis sudarys 20% balo

3. Likusios dalys, kaip duomenų bazės panaudojimas, paprasto modelio sukūrimas, naudotojo įvestis, korektiškas duomenų paruošimas sudarys likusius 5 balus.

Papildomi reikalavimai

1. Privalomas Github naudojamas (atsiskaitomasis darbas turi būti įkeltas į Github, jo nuoroda pasidalinta su dėstytoju), taip, pat darbo metu privalote atnaujinti kodą (negalima, įkelti visko prieš atsiskaitymą, turėtų būti, bent 3 šakos ir bent 5 commitai (per visas šakas) šio punkto nevykdymas (-1 balas)

2. Privalomas tvarkingas projektas, su tinkama struktūra (klasės, metodai, funkcijos, modeliai viskas atskiruose failuose). Rekomendacija laikytis per Flask paskaitas išmoktos struktūros. Turi būti try exceptai, funkcijos objektai ir t.t.


Bonus balai

1. Įsiaiškinsite ir pamėginsite panaudoti transformerius (darbui su nuotraukomis, tinkami specifiniai transformeriai). https://en.wikipedia.org/wiki/Vision_transformer (+3 balai, už tvarkingą ir pilnai veikiantį sprendimą)

2. Flaske padarykite galimybę keisti hyperparametrus (+ 0.5 balo)

3. Padarykite, kad programa galėtų veikti su video (mašinos važiuojančios kelyje) ir galėtų realiu laiku atsinaujinti, kokius ženklus mato. (+1 balas)

4. Panaudokite, daugiau nei tik pikselius iš nuotraukos (negalima konvertuoti į pikselius ir tiek, reikia panaudoti, bent vieną iš šių arba kitų jums žinomų parametrų Haar/Hog/Hue Histograms) (sąryšiumi su 2 pagrindinio uždavinio punktu)

5. Papildomai išmėginkite su kažkieno kito modeliu (iš interneto pvz huggingface, palyginkite su savo rezultatais (+1.5) balo

Papildomos sąlygos

1. Negebant paaiškinti, kažkurios eilutės, kuri yra jūsų parašytame kode, balas mažinamas per 0.5, vadinasi, negebant paaiškinti 2 eilučių, netenkate 10% galutinio įvertinimo.

2. Akivaizdžiai aklai kopijuojant ChatGPT kodą ir nesuprantant, kas yra nukopijuota, maksimalus balas yra 5.

3. Galutinis įvertinimas, taip pat priklausys ir nuo jūsų galutinio modelio tikslumo (galbūt šis modelis nebus neuroninis tinklas). Įvertinus visus, bus imama kreivė t.y. jeigu geriausio studento rezultatas bus MSE = 1000 arba tikslumas = 90%, kiekvienas 10% nuokrypis, nuo geriausio rezultato, vertinamas, kaip -0.5 balo, vadinasi, jeigu geriausias studentas gaus MSE = 1000, o jūsų mse bus 1400 (40% didesnis, nei geriausio