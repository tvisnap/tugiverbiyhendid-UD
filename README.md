# Tugiverbiühendite tuvastamine eesti keele UD puudepangas

See repositoorium sisaldab Tanel Visnapi magistritöö "Objekti funktsioonis noomeniga tugiverbiühendite leksikonipõhine tuvastamine eesti keele UD sõltuvuspuude pangas" praktilise osa materjale. Repositooriumis on töös kasutatud Pythoni skriptid, leksikonid ja otsingu tulemused.

## Põhifailid

- `leia_tugiverbiühendite_kandidaadid_korpusest.py` - Pythoni skript, mis otsib tööleksikonis kirjeldatud noomeni- ja verbilemma kombinatsioone UD puudepangast. Põhiotsingus peab noomen olema verbiga `obj`-seoses või objekti rinnastatud liige. Lisaks kontrollitakse täiustatud sõltuvusi ning ainult täiustatud sõltuvustes leitud `obj`-seosega juhud salvestatakse eraldi väljundisse.
- `tugiverbid_leksikon_final.txt` - Eesti keele verbikesksete püsiühendite andmebaasist (EKVPA) koostatud tööleksikon (263 rida).
- `tugiverbid_valjund_final.txt` - otsingu jaoks normaliseeritud otsinguleksikon. Pärast teisendamist ja duplikaatide eemaldamist on selles 259 kirjet.
- `tugiverbid_leiud_final.csv` - põhiotsingu lõplik väljund: 516 kandidaati 509 lauses.

## Kasutamine

Skript on kirjutatud Python 3.14.3 jaoks ja kasutab `pyconll` teegi versiooni 4.1.1.

Skripti käivitamiseks peavad samas kaustas olema järgmised failid: 

- `leia_tugiverbiühendite_kandidaadid_korpusest.py`
- `tugiverbid_valjund_final.txt`
- `et_edt-ud-train.conllu`
- `et_edt-ud-test.conllu`
- `et_edt-ud-dev.conllu`

Vajaliku teegi saab paigaldada käsurealt:
```bash
py -m pip install pyconll==4.1.1
```
Seejärel saab skripti käivitada käsuga, olles käsureal failidega samas kaustas:
```bash
py leia_tugiverbiühendite_kandidaadid_korpusest.py
```

Skriptis tuleb määrata kasutatava CoNLL-U korpuse failinimi või failinimed muutujas `korpuse_failid`. Otsinguleksikoni failinimi on määratud muutujas `yhendite_fail`.

Kasutatud korpust ennast repositooriumis ei jagata. Magistritöös kasutati eesti keele UD sõltuvuspuude panka. Selle leiab siit: https://github.com/UniversalDependencies/UD_Estonian-EDT/ (versioon 2.18 seisuga 18.08.2026)

Seal asuvad programmi jooksutamiseks vajalikud failid, kui kasutada Githubi repos olevat programmi muutmata kujul:
`et_edt-ud-train.conllu`,
`et_edt-ud-dev.conllu`,
`et_edt-ud-test.conllu` 

## Otsingu põhimõte

Otsing kasutab otsinguleksikoni ning kontrollib, kas samas lauses esineb leksikonis kirjeldatud verb ja noomen ning kas noomen on põhimärgenduses verbi objekt. Arvesse võetakse ka juhtumeid, kus noomen on rinnastatud verbi objektiga. Leksikonis olevat käändemärgendit kandidaadi leidmisel piirava tingimusena ei kasutata.

Täiustatud sõltuvusi kontrollitakse eraldi. Kui tööleksikonis olev noomen ei ole põhimärgenduses verbi objekt, kuid täiustatud sõltuvustes on noomeni ja verbi vahel `obj`-seos, salvestatakse leid eraldi väljundisse ja seda ei arvestata põhikandidaatide hulka.

## Failid

### `pohiotsing`

- `koosta_otsinguleksikon.py` – koostab tööleksikonist põhiotsingus kasutatava otsinguleksikoni.
- `leia_tugiverbiühendite_kandidaadid_korpusest.py` – otsib UD puudepangast leksikonis kirjeldatud tugiverbiühendite kandidaate.
- `tugiverbid_leksikon_final.txt` – EKVPA põhjal koostatud tööleksikon.
- `tugiverbid_valjund.txt` – põhiotsingus kasutatav otsinguleksikon.
- `tugiverbid_leiud.csv` – põhiotsinguga leitud kandidaadid.
- `t2iustatud_leiud.csv` – ainult täiustatud sõltuvuste abil leitud kandidaadid.
- `tugiverbid_kandidaatlaused.conllu` – põhiotsingu kandidaatlaused CoNLL-U kujul.

### `Lisaanalyysid`

- `afiksaaladverbid_tugiverbiühendid.py` + `xcomp_tugiverbiühendid.py` – otsivad kandidaat, kus tugiverbiga on seotud afiksaaladverb või esineb `xcomp`-seos.
- `afiksaaladverbid_tulemused.csv` + `xcomp_tulemused.csv` – `xcomp`/afiksaaladverbide analüüsi tulemused.
- `tugiverbid_leiud_k2sitsi+TOKENID.ods` – põhiotsingu kandidaatide käsitsi hindamise tabel + statistika analüüsi jaoks
