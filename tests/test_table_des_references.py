"""La table des références : chaque élément du calcul a sa source, ou dit qu'il n'en a pas.

`data/reference/references_par_element.yaml` dit, pour chaque élément du
calcul (l'âge, la durée, le salaire de référence, le taux, la décote et la
surcote, les points, le minimum, la réversion…) et chaque famille de régimes,
à quoi le dépôt se confronte : un exemple officiel, une grille posée sans le
code, le simulateur d'une caisse, un autre modèle — ou l'absence, déclarée
avec sa raison. Le texte reste l'arbitre : une référence confirme ou
contredit, elle ne tranche pas.

Ces tests tiennent la table complète et à jour. Toute fiche de la carte
appartient à un élément ; tout élément a une case par famille ; une case dit
ses références, ou son absence, ou qu'elle est sans objet ; une référence
nommée existe au dépôt ; et ce que le dépôt sait déjà — ses exemples
officiels, ses grilles, les modèles que ses fiches citent — se retrouve dans
la table, qui ne peut ni l'oublier ni le prétendre à tort. Action 137.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "table_des_references", RACINE / "scripts" / "table_des_references.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def tdr():
    return _module()


@pytest.fixture(scope="module")
def table(tdr):
    return tdr.charger_table()


@pytest.fixture(scope="module")
def releve(tdr, table):
    return tdr.releve(table)


def _mots(texte) -> int:
    return len(str(texte or "").split())


def test_chaque_fiche_de_la_carte_appartient_a_un_seul_element(tdr, table):
    fiches = tdr.fiches()
    appartenance = tdr.element_de_chaque_fiche(table, fiches)
    orphelines = sorted(set(fiches) - set(appartenance))
    assert not orphelines, (
        f"{len(orphelines)} fiche(s) sans élément : donnez-leur un domaine, ou "
        f"nommez-les sous `fiches` d'un élément : {orphelines}")
    doubles = sorted(f for f, els in appartenance.items() if len(els) > 1)
    assert not doubles, f"fiches rangées dans deux éléments : {doubles}"
    inconnues = sorted(f for e in table["elements"] for f in e.get("fiches", [])
                       if f not in fiches)
    assert not inconnues, f"fiches nommées que la carte n'a pas : {inconnues}"


def test_chaque_element_a_une_case_par_famille(tdr, table):
    familles = set(tdr.FAMILLES)
    assert set(tdr.familles_de_regime().values()) <= familles, (
        "une famille de l'inventaire manque à la table")
    fautes = [(e["id"], sorted(familles ^ set(e.get("cellules", {}))))
              for e in table["elements"] if set(e.get("cellules", {})) != familles]
    assert not fautes, f"cases manquantes ou en trop : {fautes}"


def test_chaque_case_dit_ses_references_son_absence_ou_qu_elle_est_sans_objet(tdr, table):
    fautes = []
    for e in table["elements"]:
        for famille, case in e["cellules"].items():
            dits = [cle for cle in ("references", "absence", "sans_objet") if case.get(cle)]
            if len(dits) != 1:
                fautes.append(f"{e['id']}/{famille} : {dits or 'rien'}")
            for cle in ("absence", "sans_objet"):
                if case.get(cle) and _mots(case[cle]) < 8:
                    fautes.append(f"{e['id']}/{famille} : `{cle}` en moins de huit mots")
    assert not fautes, "\n".join(fautes)


def test_une_case_n_est_sans_objet_que_si_aucune_fiche_ne_la_touche(releve, table):
    fautes = [f"{e['id']}/{famille} : {sorted(releve[e['id'], famille]['fiches'])[:5]}"
              for e in table["elements"] for famille, case in e["cellules"].items()
              if case.get("sans_objet") and releve[e["id"], famille]["fiches"]]
    assert not fautes, "cases sans objet que des fiches touchent :\n" + "\n".join(fautes)


def test_chaque_reference_nommee_existe_au_depot(tdr, table):
    modeles = tdr.modeles()
    sources = tdr.sources_a_explorer()
    fautes = []
    for e in table["elements"]:
        for famille, case in e["cellules"].items():
            for ref in case.get("references") or []:
                ou = f"{e['id']}/{famille}"
                sorte = ref.get("sorte")
                if sorte not in tdr.SORTES:
                    fautes.append(f"{ou} : sorte inconnue {sorte!r}")
                elif sorte == "modele":
                    m = modeles.get(ref.get("id"))
                    if m is None:
                        fautes.append(f"{ou} : modèle {ref.get('id')!r} absent du registre")
                    elif "scenario_1" not in (m.get("confronte") or []):
                        fautes.append(f"{ou} : {ref['id']} ne confronte pas le droit réel")
                elif sorte in ("simulateur_caisse", "page_officielle"):
                    s = sources.get(ref.get("id"))
                    if s is None:
                        fautes.append(f"{ou} : source {ref.get('id')!r} absente du vivier")
                    elif (sorte == "simulateur_caisse") != (s.get("nature") == "simulateur"):
                        fautes.append(f"{ou} : {ref['id']} est de nature {s.get('nature')}")
                elif "id" in ref:
                    fautes.append(f"{ou} : une {sorte} se compte au dépôt, sans `id`")
    assert not fautes, "\n".join(fautes)


def test_chaque_grandeur_des_exemples_et_des_grilles_appartient_a_un_element(tdr, table):
    rangees = {cle for e in table["elements"] for cle in e.get("attendus", {})}
    connues = tdr.grandeurs_comparees()
    assert not sorted(connues - rangees), (
        f"grandeurs comparées qu'aucun élément ne range : {sorted(connues - rangees)}")


def test_les_exemples_et_les_grilles_du_depot_sont_dans_leur_case_et_seulement_la(releve, table):
    fautes = []
    for e in table["elements"]:
        for famille, case in e["cellules"].items():
            dites = {r["sorte"] for r in case.get("references") or []}
            trouve = releve[e["id"], famille]
            for sorte, cle in (("exemple_officiel", "exemples"),
                               ("grille_independante", "preuves")):
                if bool(trouve[cle]) != (sorte in dites):
                    fautes.append(
                        f"{e['id']}/{famille} : le dépôt a {len(trouve[cle])} {cle}, "
                        f"la case {'les cite' if sorte in dites else 'ne les cite pas'}")
    assert not fautes, "\n".join(fautes)


def test_chaque_modele_qu_une_fiche_cite_est_dans_la_table(tdr, releve, table):
    """Seuls comptent les modèles qui confrontent le droit réel : un modèle de
    coût (TAXIPP) qu'une fiche cite n'est pas une référence du calcul."""
    du_droit = {i for i, m in tdr.modeles().items() if "scenario_1" in (m.get("confronte") or [])}
    fautes = []
    for e in table["elements"]:
        cites = {r.get("id") for case in e["cellules"].values()
                 for r in case.get("references") or [] if r.get("sorte") == "modele"}
        des_fiches = set().union(*(releve[e["id"], f]["referents"] for f in e["cellules"])) & du_droit
        if des_fiches - cites:
            fautes.append(f"{e['id']} : {sorted(des_fiches - cites)}")
    assert not fautes, "modèles cités par les fiches, oubliés par la table :\n" + "\n".join(fautes)
