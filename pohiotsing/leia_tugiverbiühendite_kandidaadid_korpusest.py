import csv
from collections import defaultdict
from pyconll.conllu import conllu


yhendite_fail = "tugiverbid_valjund.txt"
korpuse_failid = ["et_edt-ud-train.conllu", "et_edt-ud-test.conllu", "et_edt-ud-dev.conllu"]
valjundi_fail = "tugiverbid_leiud.csv"
t2iustatud_valjundi_fail = "t2iustatud_leiud.csv"
kandidaatlausete_fail = "tugiverbid_kandidaatlaused.conllu"

yhendid = defaultdict(list)
kandidaatlaused = {}

# Teen dict'i, et otsing käiks kiiremini.
# Nt "kuri_tegu:obj toime panema" läheb verbi "panema" alla.
with open(yhendite_fail, encoding="utf-8") as f:
    for rida in f:
        osad = rida.strip().split()
        if osad:
            yhendid[osad[-1]].append(osad)


# Kui sama ühend esineb leksikonis mitme käändemärgendiga,
# kontrollitakse obj-märgendiga varianti esimesena.
for verb in yhendid:
    obj_yhendid = []
    muud_yhendid = []

    for yhend in yhendid[verb]:
        if yhend[0].endswith(":obj"):
            obj_yhendid.append(yhend)
        else:
            muud_yhendid.append(yhend)

    yhendid[verb] = obj_yhendid + muud_yhendid

tulemused = []
t2iustatud_tulemused = []

# Sama korpuse esinemust ei lisata mitu korda,
# kui leksikonis on sama ühend eri käändemärgenditega.
nahtud_kandidaadid = set()

for korpuse_fail in korpuse_failid:
    print(f"Töötlen faili: {korpuse_fail}")

    for lause in conllu.iter_from_file(korpuse_fail):

        # Teen tokenite nimekirja ja lemmaindeksi.
        tokenid = []
        tokenid_lemma_jargi = defaultdict(list)

        for token in lause.tokens:
            tokenid.append(token)

            if token.lemma:
                tokenid_lemma_jargi[token.lemma.lower()].append(token)

        lause_id = lause.meta.get("sent_id", "")
        lause_tekst = lause.meta.get("text", "")

        # Vaatan läbi ainult need tugiverbid,
        # mis selles lauses esinevad.
        for tugiverbi_lemma, verbi_yhendid in yhendid.items():

            if tugiverbi_lemma not in tokenid_lemma_jargi:
                continue

            for verbi_token in tokenid_lemma_jargi[tugiverbi_lemma]:

                if verbi_token.upos != "VERB":
                    continue

                verbi_tegumood = set()

                if verbi_token.feats and "Voice" in verbi_token.feats:
                    verbi_tegumood = verbi_token.feats["Voice"]

                on_passiiv = "Pass" in verbi_tegumood

                for yhend in verbi_yhendid:

                    # Ühest leksikonikirjest võib rinnastuse tõttu
                    # tulla samas lauses mitu kandidaati.
                    leitud_variandid = []

                    # *** 2-osaline ühend, nt "remont:Par tegema". ***

                    if len(yhend) == 2:

                        # Käändemärgendit ei kasutata.
                        # "remont:obj" -> "remont"
                        esimese_lemma = yhend[0].split(":")[0]

                        for kandidaat in tokenid_lemma_jargi.get(esimese_lemma, []):
                            objekti_seos = ""

                            # Noomen on verbi otsene objekt.
                            if kandidaat.head == verbi_token.id and kandidaat.deprel == "obj":
                                objekti_seos = "obj"

                            # Noomen on rinnastatud verbi objektiga.
                            elif kandidaat.deprel == "conj":
                                praegune_token = kandidaat

                                # Liigume rinnastuse esimese liikmeni.
                                while praegune_token.deprel == "conj":
                                    for token in tokenid:
                                        if token.id == praegune_token.head:
                                            praegune_token = token
                                            break

                                # Rinnastuse esimene liige peab olema sama verbi objekt.
                                if praegune_token.head == verbi_token.id and praegune_token.deprel == "obj":
                                    objekti_seos = "conj->obj"

                            # Kui põhimärgenduses pole obj-seost,
                            # aga täiustatud sõltuvuses on noomeni ja verbi vahel,
                            # siis salvestatakse see kandidaat
                            if not objekti_seos and kandidaat.deps.get(verbi_token.id) == ("obj",):
                                objekti_seos = "enhanced-obj"

                            if not objekti_seos:
                                continue

                            komponendi_tokenid = [kandidaat]
                            leitud_tokenid = [kandidaat, verbi_token]
                            kandidaadi_voti = (lause_id, verbi_token.id, kandidaat.id)

                            if kandidaadi_voti in nahtud_kandidaadid:
                                continue

                            nahtud_kandidaadid.add(kandidaadi_voti)

                            leitud_variandid.append((komponendi_tokenid, leitud_tokenid, objekti_seos))

                    # *** 3-osaline ühend, nt "kuri_tegu:obj toime panema". ***

                    elif len(yhend) == 3:
                        esimese_lemma = yhend[0].split(":")[0]
                        keskmine_lemma = yhend[1]
                        keskmine_token = None

                        # Otsime kolmeosalise ühendi keskmist komponenti,
                        # nt "vastu" või "toime".
                        # See peab alluma samale verbile.
                        for kandidaat in tokenid_lemma_jargi.get(keskmine_lemma, []):
                            if kandidaat.head == verbi_token.id:
                                keskmine_token = kandidaat
                                break

                        if not keskmine_token:
                            continue

                        for kandidaat in tokenid_lemma_jargi.get(esimese_lemma, []):
                            objekti_seos = ""

                            # Noomen on verbi otsene objekt.
                            if kandidaat.head == verbi_token.id and kandidaat.deprel == "obj":
                                objekti_seos = "obj"

                            # Noomen on rinnastatud verbi objektiga.
                            elif kandidaat.deprel == "conj":
                                praegune_token = kandidaat

                                # Liigume rinnastuse esimese liikmeni.
                                while praegune_token.deprel == "conj":
                                    for token in tokenid:
                                        if token.id == praegune_token.head:
                                            praegune_token = token
                                            break

                                # Rinnastuse esimene liige peab olema sama verbi objekt.
                                if praegune_token.head == verbi_token.id and praegune_token.deprel == "obj":
                                    objekti_seos = "conj->obj"

                            if not objekti_seos and kandidaat.deps.get(verbi_token.id) == ("obj",):
                                objekti_seos = "enhanced-obj"

                            if not objekti_seos:
                                continue

                            komponendi_tokenid = [kandidaat, keskmine_token]
                            leitud_tokenid = [kandidaat, keskmine_token, verbi_token]
                            kandidaadi_voti = (lause_id,verbi_token.id,kandidaat.id, keskmine_token.id)

                            if kandidaadi_voti in nahtud_kandidaadid:
                                continue

                            nahtud_kandidaadid.add(kandidaadi_voti)

                            leitud_variandid.append((komponendi_tokenid, leitud_tokenid, objekti_seos))

                    # Lisan kõik leitud kandidaadid väljundisse.
                    for komponendi_tokenid, leitud_tokenid, objekti_seos in leitud_variandid:

                        # Panen leitud tokenid samasse järjekorda, nagu need lauses esinevad.
                        leitud_tokenid_oiges_jarjekorras = []

                        for token in tokenid:
                            if token in leitud_tokenid:
                                leitud_tokenid_oiges_jarjekorras.append(token)

                        tugiverbiyhend = " ".join(yhend)

                        rida = {
                            "Ühend": tugiverbiyhend,
                            "Lause_ID": lause_id,
                            "Leitud ühendikandidaat": " ".join(token.form for token in leitud_tokenid_oiges_jarjekorras),
                            "Komponendi seos": " | ".join(token.deprel for token in komponendi_tokenid),
                            "Komponendi kääne": " | ".join(",".join(sorted(token.feats.get("Case", set()))) for token in komponendi_tokenid),
                            "Passiiv": "jah" if on_passiiv else "ei",
                            "Reegel": objekti_seos,
                            "Lause tekst": lause_tekst,
                            "Noomeni token": komponendi_tokenid[0].id,
                            "Verbi token": verbi_token.id
                            }

                        if objekti_seos == "enhanced-obj":
                            t2iustatud_tulemused.append(rida)
                        else:
                            tulemused.append(rida)
                            kandidaatlaused[lause_id] = lause

valjad = [
    "Ühend",
    "Lause_ID",
    "Leitud ühendikandidaat",
    "Komponendi seos",
    "Komponendi kääne",
    "Passiiv",
    "Reegel",
    "Lause tekst",
    "Noomeni token",
    "Verbi token"
]

tulemused = sorted(tulemused, key=lambda rida: rida["Lause_ID"])
t2iustatud_tulemused = sorted(t2iustatud_tulemused, key=lambda rida: rida["Lause_ID"])

# Tavalised kandidaadid
with open(valjundi_fail, "w", encoding="utf-8", newline="") as f:
    tekst = csv.DictWriter(f, fieldnames=valjad, delimiter=";")
    tekst.writeheader()

    for rida in tulemused:
        tekst.writerow(rida)

# Täiustatud sõltuvuste tulemused
with open(t2iustatud_valjundi_fail, "w", encoding="utf-8", newline="") as f:
    tekst = csv.DictWriter(f, fieldnames=valjad, delimiter=";")
    tekst.writeheader()

    for rida in t2iustatud_tulemused:
        tekst.writerow(rida)

with open(kandidaatlausete_fail, "w", encoding="utf-8") as f:
    conllu.write_corpus(kandidaatlaused.values(), f)

print("Kandidaate:", len(tulemused))
print("Väljundfail:", valjundi_fail)
print("Täiustatud sõltuvuste abil leitud kandidaate:", len(t2iustatud_tulemused))
print("Täiustatud väljund:", t2iustatud_valjundi_fail)
print("Kandidaatlauseid:", len(kandidaatlaused))
print("Kandidaatlausete fail:", kandidaatlausete_fail)