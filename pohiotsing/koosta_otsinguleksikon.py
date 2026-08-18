import re

sisendfail = "tugiverbid_leksikon_final.txt"
valjundfail = "tugiverbid_valjund.txt"

lemmade_yhendid = []
kaanded = {"obj": "obj", "part": "Par","gen": "Gen","nom": "Nom"}

with open(sisendfail, encoding="utf-8") as fail:
    for rida in fail:
        morf_leid = re.search(r"<morf>\{(.*?)</morf>", rida)

        if not morf_leid:
            continue

        morfiosa = morf_leid.group(1)

        # iga jupp annab lemma, sõnaliigi ja märgendid, nt:
        # "arvamust    arvamus+t //_S_ com sg part" -> ("arvamus+t", "S", "com sg part")
        # "kiita    kiit+a //_V_" -> ("kiit+a", "V", "")
        lemmad_ja_liigid = re.findall(r"[^\s{}]+\s+([^\s{}]+)\s+//_?([A-Z])_?\s*([^/{]*)", morfiosa)
        puhastatud = []

        for i in range(len(lemmad_ja_liigid)):
            algvorm = morfiosa.split("//{")[i].strip().split()[0].lower()
            lemma = lemmad_ja_liigid[i][0]
            sonaliik = lemmad_ja_liigid[i][1]
            morf_tunnused = lemmad_ja_liigid[i][2].split()

            if i == len(lemmad_ja_liigid) - 1:
                if sonaliik == "V":
                    lemma = lemma.split("+", 1)[0] + "ma"
                elif  algvorm.endswith("ma"): # parandab sellised read nagu "lööma    lööm+0 //_S_ com sg part"
                    lemma =  algvorm
                else:
                    lemma = re.sub(r"\+.*", "", lemma)
            elif sonaliik == "V":
                break
            elif i > 0:
                lemma = algvorm
            else:
                lemma = re.sub(r"\+.*", "", lemma)

            if i == 0 and sonaliik != "V":
                kaane = ""

                for tunnus in morf_tunnused:
                    if tunnus in kaanded:
                        kaane = kaanded[tunnus]
                        break

                if kaane != "":
                    lemma = lemma + ":" + kaane
            #pakku=mine -> pakkumine
            lemma = lemma.replace("=", "")
            puhastatud.append(lemma)
        if puhastatud:
            lemmade_yhendid.append(" ".join(puhastatud))

unikaalsed_read = []
korduvad_read = set()

for rida in lemmade_yhendid:
    if rida not in korduvad_read:
        unikaalsed_read.append(rida)
        korduvad_read.add(rida)

with open(valjundfail, "w", encoding="utf-8") as fail:
    for rida in unikaalsed_read:
        fail.write(rida + "\n")
