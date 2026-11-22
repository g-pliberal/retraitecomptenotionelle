"""La carte de justesse dit aussi, de chaque partie, à quoi elle se confronte.

Une partie a sa référence : un témoin ou une grille, que la carte connaît
déjà (« officielle ») ; à défaut, un autre modèle qui lit le droit réel et que
sa fiche cite (`referents`, « modele ») ; à défaut, une source repérée qu'il
reste à rejouer, que la fiche nomme sous `a_confronter` (un simulateur ou une
page de caisse du vivier, un modèle du registre) ; à défaut, l'absence, que la
fiche dit sous `sans_reference`, avec sa raison. Le texte reste l'arbitre :
une référence confirme ou contredit, elle ne tranche pas.

Ces tests tiennent chaque fiche de la carte à l'une de ces quatre réponses,
et la vue par domaine que le tableau de bord en tire. Action 137, la
confrontation permanente demandée le 22 novembre 2026.
"""

from __future__ import annotations

import sys

import pytest

from retraite_notionnelle.noyau import carte, justesse

from test_justesse import LUE, _etat, _fiche, _grille

sys.path.insert(0, str(justesse.RACINE / "scripts"))


# --- La référence d'une partie, sur des cas fabriqués ----------------------

def test_un_temoin_ou_une_grille_font_une_reference_officielle():
    exemple = {"id": "ex", "attendu": {"taux_liquidation": 0.5}}
    versions = [{"id": "v1", "statut": "lue", "textes": [LUE], "exemples": ["ex"]}]
    assert _etat(_fiche(versions=versions), [exemple])["reference"] == "officielle"
    assert _etat(_fiche(), preuves=[_grille()])["reference"] == "officielle"


def test_un_exemple_en_ecart_reste_une_reference():
    """Un exemple qui contredit le dépôt est une référence : il dit où relire."""
    versions = [{"id": "v1", "statut": "lue", "textes": [LUE], "exemples": ["ex"]}]
    ecart = {"id": "ex", "ecart_connu": {"modele": {"x": 1}}}
    assert _etat(_fiche(versions=versions), [ecart])["reference"] == "officielle"


def test_un_modele_du_droit_reel_cite_par_la_fiche_fait_une_reference_de_modele():
    fiche = _fiche(referents={"openfisca_france_pension": {"equivalent": "x"}})
    assert _etat(fiche)["reference"] == "modele"
    assert _etat(fiche)["modeles"] == ["openfisca_france_pension"]


def test_un_modele_de_cout_n_est_pas_une_reference_du_calcul():
    """TAXIPP ne confronte que les masses : il ne vérifie aucune règle."""
    assert _etat(_fiche(referents={"taxipp": "les prélèvements"}))["reference"] == "a_declarer"


def test_une_source_a_rejouer_puis_l_absence_dite_puis_rien():
    a_rejouer = _fiche(a_confronter=[{"source": "ensap_pecari", "quoi": "le taux"}])
    assert _etat(a_rejouer)["reference"] == "a_confronter"
    muette = _fiche(sans_reference="Aucune caisse ne publie d'exemple et aucun modèle ne la code.")
    assert _etat(muette)["reference"] == "aucune"
    assert _etat(_fiche())["reference"] == "a_declarer"


def test_la_vue_par_domaine_compte_chaque_partie_dans_son_domaine_et_ses_familles():
    fiches = {"a": {**_fiche(), "id": "a", "domaine": "age"},
              "b": {**_fiche(referents={"trajectoire": "x"}), "id": "b"}}
    calcules = justesse.etats(fiches, [], [_grille(parties=[{"fiche": "a", "version": "v1"}])])
    vue = justesse.references_par_domaine(calcules, fiches, {"regime_general": "base_prive"})
    assert vue["age"]["base_prive"] == {"officielle": 1}
    assert vue[justesse.SANS_DOMAINE]["base_prive"] == {"modele": 1}


def test_le_tableau_de_bord_ecrit_les_references_par_domaine():
    import tableau_de_bord

    fiches = {"a": {**_fiche(), "id": "a", "domaine": "age"},
              "b": {**_fiche(sans_reference="Rien n'est publié sur cette règle, ni modèle ni exemple."),
                    "id": "b", "domaine": "age"}}
    calcules = justesse.etats(fiches, [], [_grille(parties=[{"fiche": "a", "version": "v1"}])])
    vue = justesse.references_par_domaine(calcules, fiches, {"regime_general": "base_prive"})
    texte = "\n".join(tableau_de_bord.references_de_la_carte(vue))
    assert "| age | 1 sur 2 |" in texte


# --- Les fiches du dépôt ----------------------------------------------------

@pytest.fixture(scope="module")
def fiches():
    return carte.fiches()


@pytest.fixture(scope="module")
def calcules(fiches):
    return justesse.etats(fiches)


def test_chaque_partie_dans_le_champ_a_sa_reference_ou_son_absence_dite(calcules):
    """Une règle que le simulateur calcule dit à quoi elle se confronte, ou
    qu'elle n'a rien : `a_confronter` ou `sans_reference` dans sa fiche."""
    muettes = sorted({p["fiche"] for p in calcules.values()
                      if p["etat"] != "hors_champ" and p["reference"] == "a_declarer"})
    assert not muettes, (
        f"{len(muettes)} fiche(s) sans référence ni absence dite : {muettes[:20]}")


def test_une_absence_dite_se_dit_en_une_phrase_et_ne_contredit_pas_le_depot(fiches, calcules):
    """Une fiche découpée peut avoir des versions confirmées et d'autres non :
    l'absence vaut pour celles-ci, et n'a plus lieu d'être quand aucune ne
    reste sans référence."""
    fautes = []
    for nom, fiche in fiches.items():
        dit = fiche.get("sans_reference")
        if dit is None:
            continue
        if len(str(dit).split()) < 8:
            fautes.append(f"{nom} : `sans_reference` en moins de huit mots")
        if not any(p["fiche"] == nom and p["reference"] == "aucune" for p in calcules.values()):
            fautes.append(f"{nom} : `sans_reference`, mais chacune de ses parties a une "
                          "référence ; ôter `sans_reference`")
    assert not fautes, "\n".join(fautes)


def test_ce_qu_une_fiche_dit_a_confronter_existe_au_vivier_ou_au_registre(fiches):
    vivier, du_droit = justesse.vivier(), justesse.modeles_du_droit_reel()
    fautes = []
    for nom, fiche in fiches.items():
        for dit in fiche.get("a_confronter") or []:
            source = dit.get("source") if isinstance(dit, dict) else None
            if source not in vivier and source not in du_droit:
                fautes.append(f"{nom} : {source!r} n'est ni au vivier ni au registre")
            elif not str(dit.get("quoi") or "").strip():
                fautes.append(f"{nom} : {source} sans `quoi`")
    assert not fautes, "\n".join(fautes)
