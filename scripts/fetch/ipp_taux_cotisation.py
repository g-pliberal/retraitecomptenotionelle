#!/usr/bin/env python3
"""Taux de cotisation retraite chez l'IPP, et l'ancrage de chaque marche au JORF.

    python scripts/fetch/ipp_taux_cotisation.py

CE QU'IL SERT À DÉCIDER. Deux séries du dépôt ne peuvent pas être certifiées, et
il fallait dire mieux que « pas certifiées » :

* le **régime général avant 1982**, que la base LEGI ne date pas — l'article 3
  du décret n° 67-803 n'y a qu'une version, de quatorze ans, portant l'état de
  1979 (voir ``dila_legi_taux_cotisation.py``) ;
* les **complémentaires du privé**, Agirc, Arrco et le régime unifié, dont les
  taux ne sont dans aucun texte réglementaire.

Les deux venaient d'OpenFisca-France. Or OpenFisca n'est pas la source : il
transcrit les **barèmes de l'Institut des politiques publiques**, qui sont
l'amont. Et ces barèmes portent, en regard de chaque marche, deux colonnes que
la transcription perd en route — ``reference``, qui nomme le texte, et
``official_journal_date``, qui donne sa date de publication au *Journal
officiel*. C'est avec elles qu'on peut dire ce que vaut une série sans la
certifier.

CE QUE LE RÉCUPÉRATEUR EN FAIT, ET CE QU'IL NE PRÉTEND PAS FAIRE

Il ne remonte rien d'un cran de fiabilité. L'IPP est une transcription comme
OpenFisca, et c'est même **la sienne** : les confronter n'est pas croiser deux
lectures indépendantes, c'est vérifier une copie contre son original. Le dire
est le premier résultat de ce script, et le contrôle de `verifier_donnees.py`
l'écrit à chaque exécution.

Il fait trois choses qui, elles, ajoutent quelque chose :

1. **L'ANCRAGE.** Pour chaque marche datée, il cherche dans l'index JORF du
   dépôt le texte que l'IPP nomme, à la date qu'il annonce. Une marche est
   *ancrée* quand ce texte existe, publié ce jour-là, avec ce numéro. La
   CHRONOLOGIE de la série devient alors vérifiable même quand sa VALEUR ne
   l'est pas — et la chronologie est ce dont dépend la règle du 1er janvier.

2. **LE CONSTAT SUR LES COMPLÉMENTAIRES.** L'IPP laisse la colonne
   ``official_journal_date`` VIDE pour l'Agirc et l'Arrco, et écrit dans
   ``reference`` « Accords ARRCO du 12/11/86 », « Accord AGIRC du 09/02/1994 ».
   Ce n'est pas une négligence : ces taux sont fixés par des accords
   collectifs, et le *Journal officiel* n'en publie que l'AVIS D'EXTENSION, qui
   renvoie au Bulletin officiel Conventions collectives sans jamais écrire le
   chiffre. La source amont dit donc elle-même qu'il n'y a pas de texte
   officiel à lire. C'est la démonstration que ces taux ne se certifieront pas,
   et elle est mécanique plutôt qu'affirmée.

3. **LES DÉCRETS QUE LA SÉRIE IGNORE.** Le récupérateur interroge le JORF, sur
   la période que l'IPP couvre, pour les décrets qui annoncent dans leur titre
   des taux de cotisation du régime général, et signale ceux qu'aucune marche
   ne rejoint. Il en trouve un, et il compte : le **décret n° 79-650 du
   30 juillet 1979** a relevé « à titre exceptionnel, par dérogation aux
   dispositions du décret n° 78-1213 » les taux du régime général « du 01-08 au
   31-12-1979 et du 01-01-1980 au 31-01-1981 ». La fenêtre couvre DEUX premiers
   janvier, 1980 et 1981, et ni l'IPP ni OpenFisca ne la portent : les taux que
   le dépôt sert pour ces deux années sont donc trop bas, d'un montant que la
   notice du *Journal officiel* n'écrit pas — elle ne nomme même aucun risque.
   C'est pourquoi le garde-fou de ``dila_legi_taux_cotisation.py`` n'exige pas
   le mot « vieillesse » : sur la période certifiée, un décret de cette forme ne
   doit pas pouvoir passer.

CE QU'IL NE COUVRE PAS. Les barèmes IPP de la CNAV ne commencent pas plus tôt
qu'OpenFisca — 1er octobre 1967 —, et rien n'a été trouvé avant. Les années
1945-1966 restent celles du COR, au niveau ``estimee``.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dila_index import chemin_index, meta, recuperer  # noqa: E402

RACINE = "https://baremes.ipp.eu/parameters/prelevements-sociaux"
SORTIE = Path("data/brut/ipp_taux_cotisation.json")
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Les barèmes lus, et le nom qu'ils portent dans le dépôt. Les quatre premiers
#: sont exactement les composantes que ``taux_cotisation_annuels.csv`` décrit
#: pour le régime général ; les suivants sont les taux d'appel des
#: complémentaires, qui servent ici de démonstration et non de valeur.
BAREMES = {
    "cnav_salarie_plafonnee":
        "prelevements_sociaux.cotisations_securite_sociale_regime_general"
        ".cnav.salarie.vieillesse_plafonnee",
    "cnav_employeur_plafonnee":
        "prelevements_sociaux.cotisations_securite_sociale_regime_general"
        ".cnav.employeur.vieillesse_plafonnee",
    "cnav_salarie_deplafonnee":
        "prelevements_sociaux.cotisations_securite_sociale_regime_general"
        ".cnav.salarie.vieillesse_deplafonnee",
    "cnav_employeur_deplafonnee":
        "prelevements_sociaux.cotisations_securite_sociale_regime_general"
        ".cnav.employeur.vieillesse_deplafonnee",
    "arrco_taux_appel":
        "prelevements_sociaux.regimes_complementaires_retraite_secteur_prive"
        ".arrco.taux_appel",
    "agirc_taux_appel":
        "prelevements_sociaux.regimes_complementaires_retraite_secteur_prive"
        ".agirc.taux_appel",
    "agirc_arrco_taux_appel":
        "prelevements_sociaux.regimes_complementaires_retraite_secteur_prive"
        ".agirc_arrco.tx_appel",
}

#: Les barèmes qui alimentent la série annuelle du régime général, et la
#: composante qu'ils portent.
COMPOSANTES_CNAV = {
    "cnav_salarie_plafonnee": "salarie_plafonnee",
    "cnav_employeur_plafonnee": "employeur_plafonnee",
    "cnav_salarie_deplafonnee": "salarie_deplafonnee",
    "cnav_employeur_deplafonnee": "employeur_deplafonnee",
}

#: Un numéro de texte dans une référence IPP : « Décret 78-1213 du 26/12/1978 »,
#: « Décret 2014-1531 du 17/12/2014, art. 4 ».
NUMERO = re.compile(r"(?:D[ée]cret|Loi|Ordonnance|Arr[êe]t[ée])\s+n?°?\s*"
                    r"(\d{2,4}-\d{1,5})", re.I)

#: Comment le JORF écrit un numéro dans un titre, selon l'époque :
#: « Décret n°78-1213 du… », « Décret n° 2014-1531 du… », « Décret no 95-1356 ».
TITRE_NUMERO = ("%n°{num} %", "%n° {num} %", "%no {num} %", "%n°{num},%")

#: La requête qui cherche les décrets que la série pourrait ignorer. Même forme
#: que le garde-fou de ``dila_legi_taux_cotisation.py``, et sans le mot
#: « vieillesse » pour la même raison.
REQUETE_DECRETS = (
    'titre:taux AND (titre:cotisation OR titre:cotisations) AND '
    'titre:"regime general"'
)

#: La période sur laquelle on cherche les décrets ignorés : celle que l'IPP
#: couvre et que la base LEGI ne date pas.
FENETRE_IGNORES = (1967, 1982)

#: Les décrets que la requête ramène sur la fenêtre et qui n'ont rien à voir
#: avec le taux vieillesse du régime général, avec la raison.
DECRETS_SANS_EFFET = {
    # Toute la descendance du décret n° 67-804, qui fixe les taux dus au titre
    # des salariés PARTIELLEMENT rattachés au régime général — régimes spéciaux
    # couverts par lui pour une partie des risques seulement. Ce n'est pas le
    # taux du régime général, et le dépôt ne le porte nulle part.
    "JORFTEXT000000513505": "décret n° 67-804 du 20 septembre 1967 : salariés "
                            "partiellement rattachés au régime général",
    "JORFTEXT000000309437": "décret n° 70-681 du 30 juillet 1970 : tableau du "
                            "décret n° 67-804",
    "JORFTEXT000000679975": "décret n° 70-1317 du 23 décembre 1970 : idem",
    "JORFTEXT000000510011": "décret n° 73-1210 du 29 décembre 1973 : idem",
    "JORFTEXT000000861786": "décret n° 75-1274 du 29 décembre 1975 : idem",
    "JORFTEXT000000861797": "décret n° 76-895 du 29 septembre 1976 : idem",
    "JORFTEXT000000697114": "décret n° 78-1214 du 26 décembre 1978 : idem",
    "JORFTEXT000000880152": "décret n° 79-651 du 30 juillet 1979 : relèvement "
                            "temporaire, mais du décret n° 67-804",
    "JORFTEXT000000859010": "décret n° 81-1014 du 13 novembre 1981 : idem",
    "JORFTEXT000000328902": "décret n° 80-298 du 24 avril 1980 : taux et "
                            "conditions d'exonération de l'assurance MALADIE",
    "JORFTEXT000000868863":
        "décret n° 68-579 du 29 juin 1968 : réduction du seul taux MALADIE, "
        "article 5 du décret n° 67-803",
    "JORFTEXT000001880626":
        "décret n° 68-579, seconde fiche du même texte",
    "JORFTEXT000000518662":
        "décret n° 77-677 du 29 juin 1977 : abrogation du 2e alinéa de "
        "l'article 5, qui exonérait les gains les plus faibles",
    "JORFTEXT000002075848":
        "décret n° 77-677, seconde fiche du même texte",
}


#: Le décret qui FERME la période sans la dater : le n° 81-1013 du 13 novembre
#: 1981 abroge le n° 67-803 et refixe le taux. Sa notice porte les chiffres —
#: c'est la seule du JORF ancien à le faire — et ils doivent être ceux que la
#: série IPP porte à cette date. Ce n'est pas une certification : le décret dit
#: ce qui vaut à PARTIR du 14 novembre 1981, non ce qui valait avant. Mais un
#: décret qui refixe un taux sans le changer confirme le niveau qu'il trouve, et
#: le récupérateur le vérifie plutôt que de l'affirmer.
CORROBORATION = {
    "id": "JORFTEXT000000503485",
    "decret": "décret n° 81-1013 du 13 novembre 1981",
    "motif": re.compile(r"VIEILLESSE\s*:\s*[\d,]+%\s*\(\s*([\d,]+)%\s*POUR\s+L['’]EMPLOYEUR"
                        r"[^)]*?([\d,]+)%\s*POUR\s+LES?\s+SALARIES?", re.I),
    "annee": 1981,
    "attendu": {"employeur_plafonnee": 0.082, "salarie_plafonnee": 0.047},
}


def corroborer(db: sqlite3.Connection, serie: dict[str, dict]) -> dict:
    """La notice du décret de 1981 porte-t-elle le niveau que la série annonce ?"""
    ligne = db.execute("SELECT titre, texte FROM doc WHERE id = ?",
                       (CORROBORATION["id"],)).fetchone()
    if ligne is None:
        return {"verdict": "texte absent de l'index"}
    trouve = CORROBORATION["motif"].search(f"{ligne[0]} {ligne[1]}")
    if trouve is None:
        return {"verdict": "la notice ne porte plus les taux annoncés"}
    lus = {"employeur_plafonnee": _taux(trouve.group(1) + " %"),
           "salarie_plafonnee": _taux(trouve.group(2) + " %")}
    portee = serie.get(str(CORROBORATION["annee"]), {})
    ecarts = {c: (portee.get(c), lus[c]) for c in lus
              if portee.get(c) is None or abs(portee[c] - lus[c]) > 1e-9}
    return {
        "decret": CORROBORATION["decret"], "lus": lus,
        "annee": CORROBORATION["annee"],
        "verdict": "le Journal officiel confirme le niveau porté par la série"
                   if not ecarts else f"écart : {ecarts}",
    }


def _telecharger(parametre: str) -> list[dict[str, str]]:
    demande = urllib.request.Request(f"{RACINE}/{parametre}/csv", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return list(csv.DictReader(io.StringIO(reponse.read().decode("utf-8"))))


def _taux(brut: str) -> float | None:
    """« 6,55 % », « 127 % » -> fraction. Une cellule vide n'est pas un zéro."""
    texte = (brut or "").replace(" ", " ").replace(" ", " ").strip()
    if not texte or "%" not in texte:
        return None
    return float(texte.replace("%", "").replace(" ", "").replace(",", ".")) / 100


def _jour(brut: str) -> date:
    """L'IPP date ses marches en jj/mm/aaaa."""
    jour, mois, annee = (int(x) for x in brut.split("/"))
    return date(annee, mois, jour)


def marches(lignes: list[dict[str, str]], colonne: str) -> list[dict]:
    """Les changements datés d'un barème, du plus ancien au plus récent."""
    lues = []
    for ligne in lignes:
        valeur = _taux(ligne.get(colonne, ""))
        if valeur is None:
            continue
        reference = (ligne.get("reference") or "").strip()
        numero = NUMERO.search(reference)
        lues.append({
            "effet": _jour(ligne["date"]).isoformat(),
            "valeur": valeur,
            "reference": reference,
            "numero": numero.group(1) if numero else "",
            "journal_officiel": (ligne.get("official_journal_date") or "").strip(),
        })
    return sorted(lues, key=lambda m: m["effet"])


def ancrer(db: sqlite3.Connection, marche: dict) -> dict:
    """Le texte que l'IPP nomme est-il au JORF, ce jour-là, sous ce numéro ?"""
    if not marche["journal_officiel"] or not marche["numero"]:
        return {**marche, "ancrage": "sans date au Journal officiel"}
    publie = date.fromisoformat(marche["journal_officiel"])
    for gabarit in TITRE_NUMERO:
        trouve = db.execute(
            "SELECT id, date, titre FROM doc WHERE num = '' AND titre LIKE ? "
            "AND date = ? LIMIT 1",
            (gabarit.format(num=marche["numero"]), publie.isoformat()),
        ).fetchone()
        if trouve:
            return {**marche, "ancrage": "ancrée", "texte": trouve[0],
                    "titre": trouve[2][:120]}
    return {**marche, "ancrage": "absente de l'index à cette date"}


def en_vigueur(marches_lues: list[dict], annee: int,
               annee_ouverture: int) -> float | None:
    """Le taux au 1er janvier, règle du dépôt ; l'année d'ouverture exceptée.

    L'exception ne vaut QUE pour l'année où la série entière commence — 1967,
    où le barème ouvre au 1er octobre et où exiger le 1er janvier reviendrait à
    n'écrire aucun taux. Elle ne vaut pas pour une composante qui apparaît plus
    tard : la cotisation DÉPLAFONNÉE naît le 1er février 1991, et au 1er janvier
    de cette année-là elle vaut zéro, pas 1,60 %.
    """
    premier_janvier = f"{annee}-01-01"
    anterieures = [m for m in marches_lues if m["effet"] <= premier_janvier]
    if anterieures:
        return anterieures[-1]["valeur"]
    if annee != annee_ouverture:
        return None
    ouverture = [m for m in marches_lues if m["effet"][:4] == str(annee)]
    return ouverture[0]["valeur"] if ouverture else None


def decrets_ignores(db: sqlite3.Connection, ancrees: set[str]) -> list[str]:
    """Les décrets du JORF de la fenêtre qu'aucune marche ne rejoint."""
    debut, fin = FENETRE_IGNORES
    restants = []
    for ident, publie, titre in db.execute(
        "SELECT doc.id, doc.date, doc.titre FROM fts JOIN doc ON doc.rowid = fts.rowid "
        "WHERE fts MATCH ? AND doc.date >= ? AND doc.date < ? AND doc.num = '' "
        "AND upper(doc.nature) = 'DECRET' ORDER BY doc.date",
        (REQUETE_DECRETS, str(debut), str(fin)),
    ):
        if ident in ancrees or ident in DECRETS_SANS_EFFET:
            continue
        restants.append(f"{publie}  {ident}  {titre[:130]}")
    return restants


def _ouvrir(base: str) -> sqlite3.Connection:
    chemin = chemin_index(base)
    if not chemin.exists():
        print(f"Index {base} absent : récupération de l'index publié.")
        recuperer(base, chemin)
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    print(f"Index {base:<5} {meta(db, 'dump') or '?'}, "
          f"à jour au {meta(db, 'dernier_increment') or '?'}")
    return db


def main() -> int:
    try:
        jorf = _ouvrir("jorf")
    except (LookupError, RuntimeError, OSError) as erreur:
        print(f"ÉCHEC   index JORF : {erreur}", file=sys.stderr)
        return 1

    baremes: dict[str, list[dict]] = {}
    for nom, parametre in BAREMES.items():
        try:
            lignes = _telecharger(parametre)
        except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
            print(f"ÉCHEC   {nom} : {erreur}", file=sys.stderr)
            return 1
        colonne = next((c for c in (lignes[0] if lignes else {})
                        if c not in ("date", "reference", "official_journal_date",
                                     "notes")), None)
        if colonne is None:
            print(f"ÉCHEC   {nom} : aucune colonne de valeur", file=sys.stderr)
            return 1
        baremes[nom] = [ancrer(jorf, m) for m in marches(lignes, colonne)]
        ancrees = sum(1 for m in baremes[nom] if m["ancrage"] == "ancrée")
        print(f"OK      {nom:<26} {len(baremes[nom]):>2} marches, "
              f"{ancrees} ancrée(s) au Journal officiel")

    # La série annuelle de la CNAV, au 1er janvier, pour la confrontation.
    annees = sorted({int(m["effet"][:4])
                     for nom in COMPOSANTES_CNAV for m in baremes[nom]})
    ouverture = min(annees)
    serie = {}
    for annee in range(ouverture, date.today().year + 1):
        composantes = {
            champ: en_vigueur(baremes[nom], annee, ouverture) or 0.0
            for nom, champ in COMPOSANTES_CNAV.items()
        }
        if composantes["salarie_plafonnee"] + composantes["employeur_plafonnee"] > 0:
            serie[str(annee)] = composantes

    identifiants = {m.get("texte") for nom in COMPOSANTES_CNAV
                    for m in baremes[nom] if m.get("texte")}
    corroboration = corroborer(jorf, serie)
    ignores = decrets_ignores(jorf, identifiants | {CORROBORATION["id"]})

    charge = {
        "source": "Institut des politiques publiques, barèmes socio-fiscaux",
        "url": RACINE,
        "recupere_le": date.today().isoformat(),
        "index_jorf": {"dump": meta(jorf, "dump"),
                       "dernier_increment": meta(jorf, "dernier_increment")},
        "note": "l'IPP est la source AMONT d'OpenFisca-France : le confronter à "
                "OpenFisca vérifie une copie, non deux lectures indépendantes. "
                "Ce que ce fichier ajoute est l'ANCRAGE de chaque marche au "
                "texte que l'IPP nomme, et la liste des décrets qu'aucune "
                "marche ne rejoint.",
        "baremes": baremes,
        "serie_cnav": serie,
        "corroboration_1981": corroboration,
        "decrets_ignores": ignores,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(charge, ensure_ascii=False, indent=1),
                      encoding="utf-8")

    for nom in ("arrco_taux_appel", "agirc_taux_appel", "agirc_arrco_taux_appel"):
        sans = [m for m in baremes[nom] if m["ancrage"] != "ancrée"]
        if sans:
            citee = next((m["reference"] for m in sans if m["reference"]), "sans référence")
            print(f"        {nom} : {len(sans)}/{len(baremes[nom])} marches sans "
                  f"date au Journal officiel — « {citee[:70]} »")
    print(f"        corroboration 1981 : {corroboration['verdict']}")
    if ignores:
        print(f"\nDÉCRET(S) QUE LA SÉRIE IGNORE, sur {FENETRE_IGNORES[0]}-"
              f"{FENETRE_IGNORES[1] - 1} :")
        for ligne in ignores:
            print(f"        {ligne}")
    print(f"\n{len(serie)} années de la CNAV écrites dans {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
