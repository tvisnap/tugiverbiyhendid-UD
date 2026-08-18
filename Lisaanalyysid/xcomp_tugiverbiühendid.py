import csv
from pyconll.conllu import conllu

csv_fail = "tugiverbid_leiud.csv"
conllu_fail = "tugiverbid_kandidaatlaused.conllu"
valjund_fail = "xcomp_tulemused.csv"

# Laused ID järgi
laused = {}

for lause in conllu.load_from_file(conllu_fail):
    lause_id = lause.meta["sent_id"]
    laused[lause_id] = lause

leiud = []

# Vaatan iga kandidaadi kandidaatverbi
with open(csv_fail, encoding="utf-8") as f:
    for rida in csv.DictReader(f, delimiter=";"):

        lause = laused[rida["Lause_ID"]]
        verbi_id = rida["Verbi token"]

        tokenid = {}

        for token in lause.tokens:
            tokenid[token.id] = token

        verb = tokenid[verbi_id]

        # Otsin kandidaatverbiga compound:prt-seoses komponendi
        for token in lause.tokens:
            if token.head == verbi_id and token.deprel == "xcomp":
                leiud.append((rida["Lause_ID"], verb.lemma, token.lemma))

with open(valjund_fail, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Lause_ID", "Verb", "Xcomp"])
    writer.writerows(leiud)

print("Kokku:", len(leiud))
print("Väljundfail:", valjund_fail)
