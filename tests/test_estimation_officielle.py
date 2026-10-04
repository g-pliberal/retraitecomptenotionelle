"""« Mon estimation retraite » contre le scénario 1 : la confrontation outillée.

`scripts/estimation_officielle.py` relie le relevé de carrière qu'un assuré
télécharge à l'estimation que la caisse lui affiche (docs/architecture.md,
§ 3.5, troisième voie). Ces tests tiennent ses promesses sur des relevés et une
estimation FICTIFS, écrits à la forme des gabarits de `tests/test_releve_lu.py` :
aucune donnée personnelle n'entre au dépôt, pas même dans ses tests. Le script
refuse un fichier personnel rangé dans le dépôt ; il lit le PDF du relevé comme
son texte ; il poursuit la carrière comme la page le dit, et la liquide à la date
de chaque départ, en euros de la page, majoration pour enfants comprise ; et
l'écart qu'il imprime est celui du modèle à la caisse, ligne par ligne, puis
étage par étage.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import re
import shutil
import sys
import unicodedata
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "estimation_officielle_sous_test", RACINE / "scripts" / "estimation_officielle.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # ses dataclasses s'y cherchent
    spec.loader.exec_module(module)
    return module


estimation_officielle = _module()
Refus = estimation_officielle.Refus


def _releve(au_plafond: float | None = None, naissance: str = "12/05/1966",
            debut: int = 1988) -> str:
    """Un relevé du régime général à la forme de `REGIME_GENERAL` : une ligne
    par année, des francs jusqu'en 2001, des euros ensuite ; ``au_plafond``
    met l'année 2024 à ce revenu."""
    lignes = ["Relevé de carrière",
              f"DUPONT Marie — Date de naissance : {naissance}",
              "Régime général",
              "Année Employeur ou situation Revenu d'activité Trimestres"]
    for annee in range(debut, 2026):
        if annee < 2002:
            montant = 60_000 + 3_000 * (annee - 1988)
        elif annee == 2024 and au_plafond is not None:
            montant = au_plafond
        else:
            montant = 18_300 + 600 * (annee - 2002)
        lignes.append(f"{annee} SOCIETE DUPONT SA {montant:,.0f} 4".replace(",", " "))
    return "\n".join(lignes) + "\n"


def _estimation(**remplacements) -> dict:
    """Une estimation recopiée, fictive : deux départs, deux caisses."""
    donnees = {
        "lu_le": dt.date(2026, 10, 4),
        "convention": {
            "texte": "Montants bruts mensuels, en euros 2026.",
            "montants": "brut", "periodicite": "mensuel", "euros_de": 2026,
            "revenus_futurs": "Une évolution régulière de vos revenus est appliquée.",
        },
        "assure": {"sexe": "F", "enfants": 3},
        "departs": [
            {"age": "64 ans", "date": dt.date(2030, 6, 1), "trimestres": 160,
             "regimes": [{"libelle": "Assurance retraite", "brut": 1000},
                         {"libelle": "Agirc-Arrco", "brut": 400}],
             "total_brut": 1400, "net": 1250},
            {"age": "67 ans", "date": dt.date(2033, 6, 1),
             "regimes": [{"libelle": "Assurance retraite", "brut": 1200},
                         {"libelle": "Agirc-Arrco", "brut": 480}]},
        ],
    }
    for cle, valeur in remplacements.items():
        donnees[cle] = valeur
    return donnees


@pytest.fixture(scope="module")
def contexte():
    return estimation_officielle.Contexte()


@pytest.fixture(scope="module")
def catalogue(contexte):
    return contexte.simulateur().catalogue


def _lecture(texte: str):
    return estimation_officielle.lire_releve(texte.strip().split("\n"))


def _confrontation(contexte, catalogue, revenus_futurs="salaire_moyen", texte=None,
                   croissance=0.0, **estimation):
    return estimation_officielle.Confrontation(
        _lecture(texte or _releve()),
        estimation_officielle.lire_estimation(_estimation(**estimation), catalogue),
        revenus_futurs, contexte, croissance)


def _total(servi) -> float:
    return sum(servi.par_regime.values())


# ---------------------------------------------------------------------------
# Rien de personnel au dépôt
# ---------------------------------------------------------------------------

@pytest.mark.skipif(shutil.which("git") is None, reason="git absent")
def test_un_fichier_personnel_du_depot_est_refuse_s_il_n_est_pas_ignore(tmp_path):
    """Un relevé posé dans le dépôt y entrerait au premier `git add -A` : il est
    refusé avant d'être lu, qu'il existe ou non. Ce que git ignore — la mémoire
    des calculs, `.cache/` — et ce qui est hors du dépôt passent."""
    with pytest.raises(Refus, match="sans y être ignoré"):
        estimation_officielle.hors_du_depot(RACINE / "releve_fictif.pdf")
    with pytest.raises(Refus, match="sans y être ignoré"):
        estimation_officielle.hors_du_depot(RACINE / "docs" / "estimation.yaml")
    ignore = RACINE / ".cache" / "estimation_fictive.yaml"
    assert estimation_officielle.hors_du_depot(ignore) == ignore.resolve()
    dehors = tmp_path / "estimation.yaml"
    assert estimation_officielle.hors_du_depot(dehors) == dehors.resolve()


def test_le_script_n_ecrit_aucun_fichier():
    """Il imprime, et c'est tout : aucune écriture de fichier dans son code, pour
    que rien de ce qu'il lit ne finisse sur le disque à côté du dépôt."""
    source = (RACINE / "scripts" / "estimation_officielle.py").read_text(encoding="utf-8")
    assert not re.search(r"write_text|write_bytes|open\(|\.mkdir\(|shutil\.", source)


# ---------------------------------------------------------------------------
# Le relevé et l'estimation, lus
# ---------------------------------------------------------------------------

def test_le_releve_pdf_se_lit_comme_son_texte(tmp_path):
    """Le PDF téléchargé passe par `lecture_pdf`, puis par `lire_releve` : la
    saisie qu'il donne est celle de son texte. Le document est fabriqué à la
    main, une ligne de texte par ligne du relevé."""
    texte = unicodedata.normalize("NFKD", _releve().replace("—", "-"))
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    lignes = texte.strip().split("\n")
    contenu = b"BT /F1 10 Tf 70 760 Td " + b" 0 -14 Td ".join(
        b"(" + ligne.encode("latin-1") + b") Tj" for ligne in lignes) + b" ET"
    pdf = (b"%PDF-1.5\n1 0 obj\n<< /Length " + str(len(contenu)).encode()
           + b" >>\nstream\n" + contenu + b"\nendstream\nendobj\ntrailer\n<< >>\n%%EOF\n")
    (tmp_path / "releve.pdf").write_bytes(pdf)
    (tmp_path / "releve.txt").write_text(texte, encoding="utf-8")
    assert estimation_officielle.lignes_du_releve(tmp_path / "releve.pdf") == lignes
    du_pdf = estimation_officielle.lire(tmp_path / "releve.pdf")
    du_texte = estimation_officielle.lire(tmp_path / "releve.txt")
    assert du_pdf.parametres() == du_texte.parametres()
    assert du_pdf.naissance == "1966-05-12"
    (tmp_path / "vide.txt").write_text("Rien à lire\n", encoding="utf-8")
    with pytest.raises(Refus, match="aucune année"):
        estimation_officielle.lire(tmp_path / "vide.txt")


def test_le_gabarit_se_lit_et_dit_ce_qui_reste_a_remplir(catalogue, capsys):
    """`--modele` imprime le gabarit ; tel quel, il est refusé sur la première
    chose qu'il reste à recopier, la convention de la page."""
    assert estimation_officielle.main(["--modele"]) == 0
    gabarit = yaml.safe_load(capsys.readouterr().out)
    assert {"lu_le", "convention", "assure", "releve", "departs"} <= set(gabarit)
    with pytest.raises(Refus, match="mot pour mot"):
        estimation_officielle.lire_estimation(gabarit, catalogue)


def test_une_caisse_connue_trouve_ses_regimes(catalogue):
    """La page nomme la caisse qui paie ; le script en connaît les régimes, et
    une ligne dit les siens dans `codes` quand il ne la connaît pas."""
    estimation = estimation_officielle.lire_estimation(_estimation(), catalogue)
    (premier, second) = estimation.departs[0].regimes
    assert "regime_general" in premier.codes and "agirc_arrco" in second.codes
    assert estimation.departs[1].total_brut == 1680
    assert estimation.revenu_annuel is None and estimation.corrections == {}


@pytest.mark.parametrize("modification, motif", [
    (lambda e: e["convention"].update(montants="net"), "bruts mensuels"),
    (lambda e: e["convention"].update(revenus_futurs=""), "revenus_futurs"),
    (lambda e: e["convention"].update(revenu_annuel="à voir"), "revenu_annuel"),
    (lambda e: e["departs"][0].update(total_brut=1500), "la recopie est à revoir"),
    (lambda e: e["departs"][0]["regimes"].append({"libelle": "Caisse X", "brut": 0}),
     "pas connue"),
    (lambda e: e["departs"][0]["regimes"][0].update(codes=["regime_general", "arrco"]),
     "mêle les étages"),
    (lambda e: e["departs"][0]["regimes"][1].update(codes=["regime_general"]),
     "deux lignes"),
    (lambda e: e["departs"][0].update(date=dt.date(2030, 6, 15)), "premier jour"),
    (lambda e: e["assure"].update(sexe="X"), "H ou F"),
])
def test_une_recopie_douteuse_est_refusee(catalogue, modification, motif):
    """Ce qui ferait un écart sans rapport avec le droit : un net pris pour un
    brut, des lignes qui ne font pas le total de la page, une caisse dont on
    ne sait pas les régimes, un départ au milieu d'un mois."""
    estimation = _estimation()
    modification(estimation)
    with pytest.raises(Refus, match=motif):
        estimation_officielle.lire_estimation(estimation, catalogue)


def test_une_naissance_contredite_ou_absente_est_refusee(contexte, catalogue):
    with pytest.raises(Refus, match="n'est pas celle"):
        _confrontation(contexte, catalogue,
                       assure={"sexe": "F", "naissance": dt.date(1966, 5, 13)})
    sans_naissance = _releve().replace("DUPONT Marie — Date de naissance : 12/05/1966\n", "")
    with pytest.raises(Refus, match="assure.naissance"):
        _confrontation(contexte, catalogue, texte=sans_naissance)
    # Le numéro de sécurité sociale — inventé, et impossible : une commune et
    # un rang à zéro — ne donne que le mois : il ne suffit pas, mais il
    # contrôle la date recopiée.
    par_le_numero = _releve().replace("DUPONT Marie — Date de naissance : 12/05/1966",
                                      "Numéro de sécurité sociale 2 66 05 99 000 000")
    with pytest.raises(Refus, match="n'en dit que le mois, 1966-05"):
        _confrontation(contexte, catalogue, texte=par_le_numero)
    with pytest.raises(Refus, match="une naissance en 1966-05, l'estimation le 1966-06-12"):
        _confrontation(contexte, catalogue, texte=par_le_numero,
                       assure={"sexe": "F", "naissance": dt.date(1966, 6, 12)})
    assert _confrontation(contexte, catalogue, texte=par_le_numero,
                          assure={"sexe": "F", "naissance": dt.date(1966, 5, 12)}
                          ).naissance == "1966-05-12"


# ---------------------------------------------------------------------------
# La carrière à venir, et les années corrigées
# ---------------------------------------------------------------------------

def test_les_revenus_a_venir_poursuivent_la_derniere_annee(contexte, catalogue):
    """Sans revenu donné par la page, la carrière poursuit la dernière année du
    relevé : au rythme du salaire moyen, ou des prix, plus ce que `--croissance`
    y ajoute, l'année du départ au prorata de ses mois ; `aucun` l'arrête."""
    moyen = _confrontation(contexte, catalogue)
    macro, arrondi = moyen.macro, estimation_officielle.arrondi
    salaire = estimation_officielle.salaire_moyen_annuel
    assert moyen.releve_prolonge(dt.date(2027, 6, 1)).split("\n")[-2:] == [
        f"2026:salarie_prive_non_cadre:"
        f"{arrondi(32_100 * salaire(macro, 2026) / salaire(macro, 2025))}",
        f"2027:salarie_prive_non_cadre:"
        f"{arrondi(32_100 * salaire(macro, 2027) / salaire(macro, 2025) * 5 / 12)}",
    ]
    prix = _confrontation(contexte, catalogue, "prix", croissance=1.0)
    assert prix.releve_prolonge(dt.date(2027, 1, 1)).split("\n")[-1] == (
        f"2026:salarie_prive_non_cadre:"
        f"{arrondi(32_100 * macro.coefficient_prix(2025, 2026) * 1.01)}")
    depart = moyen.estimation.departs[1]
    totaux = {(hypothese, croissance): _total(
        _confrontation(contexte, catalogue, hypothese, croissance=croissance).servi(depart))
        for hypothese, croissance in (("aucun", 0.0), ("prix", 0.0), ("prix", 1.0),
                                      ("salaire_moyen", 0.0))}
    assert totaux[("aucun", 0.0)] < totaux[("prix", 0.0)] < totaux[("salaire_moyen", 0.0)]
    assert totaux[("prix", 0.0)] < totaux[("prix", 1.0)]
    with pytest.raises(Refus, match="le relevé porte encore 2025"):
        moyen.carriere(dt.date(2025, 12, 1))
    with pytest.raises(Refus, match="--croissance"):
        _confrontation(contexte, catalogue, "salaire_moyen", croissance=1.0)


def test_la_carriere_a_venir_part_du_revenu_que_la_page_retient(contexte, catalogue):
    """La page prête à la situation actuelle un revenu annuel, en euros de son
    année : la carrière à venir part de lui, et non de la dernière année du
    relevé, sous le statut de son emploi."""
    convention = dict(_estimation()["convention"], revenu_annuel=30_000.0)
    confrontation = _confrontation(contexte, catalogue, "prix", convention=convention)
    assert confrontation.revenus_a_venir() == ([("salarie_prive_non_cadre", 30_000.0)], 2026)
    assert confrontation.releve_prolonge(dt.date(2027, 1, 1)).split("\n")[-1] == (
        "2026:salarie_prive_non_cadre:30000")
    assert "le revenu annuel que la page retient, en euros de 2026" in (
        estimation_officielle.rapport(confrontation))


def test_une_annee_mal_lue_se_corrige_a_la_main(contexte, catalogue):
    """La lecture peut additionner une même paie que deux régimes déclarent à
    part : l'estimation privée porte alors le revenu juste, année par année,
    et le rapport le dit. Une année que la lecture n'a pas est refusée."""
    corrigee = _confrontation(contexte, catalogue, releve={"corrections": {2010: 20_000}})
    assert "2010:salarie_prive_non_cadre:20000:4" in corrigee.releve.split("\n")
    assert "corrigées à la main, d'après le relevé : 2010" in (
        estimation_officielle.rapport(corrigee))
    depart = corrigee.estimation.departs[0]
    assert _total(corrigee.servi(depart)) != _total(
        _confrontation(contexte, catalogue).servi(depart))
    with pytest.raises(Refus, match="l'année 1950 est sur 0 lignes"):
        _confrontation(contexte, catalogue, releve={"corrections": {1950: 1_000}})


def test_un_assure_jeune_se_confronte_comme_un_autre(contexte, catalogue):
    """Le modèle n'accepte pas un départ avant quarante ans : le script ne lui
    en demande aucun, même pour qui n'a qu'une dizaine d'années de carrière ; et
    un départ qu'il refuse sort en refus, non en trace d'erreur."""
    jeune = _releve(naissance="14/09/1993", debut=2015)
    a_64_ans = {"age": "64 ans", "date": dt.date(2057, 10, 1),
                "regimes": [{"libelle": "Assurance retraite", "brut": 1500},
                            {"libelle": "Agirc-Arrco", "brut": 500}]}
    trop_tard = dict(a_64_ans, age="82 ans", date=dt.date(2075, 10, 1))
    confrontation = _confrontation(contexte, catalogue, texte=jeune,
                                   departs=[a_64_ans, trop_tard])
    (premier, second) = confrontation.estimation.departs
    servi = confrontation.servi(premier)
    assert servi.ouverte and servi.trimestres > 120
    with pytest.raises(Refus, match="le modèle l'accepte"):
        confrontation.servi(second)


# ---------------------------------------------------------------------------
# Le scénario 1, dans la convention de la page
# ---------------------------------------------------------------------------

def test_chaque_regime_porte_sa_part_et_le_tout_fait_la_pension(contexte, catalogue):
    """Brut mensuel par régime : sa pension, minima compris, et sa part de la
    majoration pour enfants, que le moteur compte à côté. Leur somme est la
    pension du scénario 1, dans les euros de la page."""
    confrontation = _confrontation(contexte, catalogue)
    depart = confrontation.estimation.departs[1]
    comparaison = confrontation.simulateur.simuler(confrontation.carriere(depart.date))
    servi = estimation_officielle.servi(comparaison)
    actuel = comparaison.actuel
    assert any(a.code == "majoration_enfants" for a in actuel.avantages_appliques)
    attendu = ((actuel.pension_annuelle + actuel.pension_hors_repartition)
               * comparaison.coefficient_euros_constants / 12)
    assert _total(servi) + servi.minimum_vieillesse == pytest.approx(attendu, rel=1e-12)
    assert comparaison.carriere.date_liquidation.annee == 2033
    assert comparaison.carriere.date_liquidation.mois == 6


def test_le_modele_est_ramene_aux_euros_de_la_page(contexte, catalogue):
    """Le même départ, lu dans une page en euros de 2026 ou de 2028, la carrière
    à venir constante en euros : le modèle suit, d'un coefficient qui est celui
    des prix."""
    convention = dict(_estimation()["convention"], euros_de=2028)
    en_2026 = _confrontation(contexte, catalogue, "aucun")
    en_2028 = _confrontation(contexte, catalogue, "aucun", convention=convention)
    lire = estimation_officielle.lire_estimation
    servi_2026 = en_2026.servi(lire(_estimation(), catalogue).departs[1])
    servi_2028 = en_2028.servi(lire(_estimation(convention=convention), catalogue).departs[1])
    assert _total(servi_2028) / _total(servi_2026) == pytest.approx(
        en_2026.macro.coefficient_prix(2026, 2028), rel=1e-9)


def test_le_plafond_dit_quel_releve_on_a_lu(contexte, catalogue):
    """Le relevé du seul régime général ne porte le revenu que sous le plafond :
    une année qui le touche minore la complémentaire du modèle, et le rapport le
    dit. Une année qui le dépasse dit l'inverse : ce relevé-là porte le revenu
    entier, et la complémentaire compte ce qui dépasse."""
    plafond = contexte.simulateur().macro.plafond_securite_sociale
    au_plafond = _confrontation(contexte, catalogue, texte=_releve(au_plafond=plafond(2024)))
    serie = au_plafond.macro.plafond_securite_sociale
    assert estimation_officielle.annees_au_plafond(au_plafond.lecture, serie) == [2024]
    assert "1 année(s) au plafond" in estimation_officielle.rapport(au_plafond)
    au_dessus = _confrontation(contexte, catalogue,
                               texte=_releve(au_plafond=1.2 * plafond(2024)))
    assert estimation_officielle.annees_au_dessus_du_plafond(au_dessus.lecture, serie) == [2024]
    texte = estimation_officielle.rapport(au_dessus)
    assert "porte le revenu entier" in texte and "année(s) au plafond" not in texte
    sans = _confrontation(contexte, catalogue)
    assert not estimation_officielle.annees_au_plafond(sans.lecture, serie)
    assert not estimation_officielle.annees_au_dessus_du_plafond(sans.lecture, serie)


# ---------------------------------------------------------------------------
# Le tableau des écarts
# ---------------------------------------------------------------------------

def test_l_ecart_est_celui_du_modele_a_la_caisse_ligne_puis_etage(catalogue):
    """Le tableau, sans le modèle : chaque ligne de la caisse contre les régimes
    qu'elle couvre, un régime que la page n'affiche pas à part, puis les étages
    et le total, en euros et en pour cent de la caisse."""
    servi = estimation_officielle.Servi(
        par_regime={"regime_general": 1000.0, "agirc_arrco": 450.0, "arrco": 100.0,
                    "ircantec": 30.0},
        minimum_vieillesse=0.0, trimestres=168, ouverte=True, motif_ouverture="age_legal")
    depart = estimation_officielle.lire_estimation(_estimation(), catalogue).departs[0]
    lignes = estimation_officielle.tableau(depart, servi, catalogue)
    texte = "\n".join(lignes)
    assert "trimestres : caisse 160, modèle 168" in lignes[0]
    assert re.search(r"Assurance retraite\s+1 000\s+1 000\s+\+0\s+\+0,0 %", texte)
    assert re.search(r"Agirc-Arrco\s+400\s+550\s+\+150\s+\+37,5 %", texte)
    assert re.search(r"\(absent de la page\)\s+0\s+30\s+\+30\s+—", texte)
    assert re.search(r"= retraite de base\s+1 000\s+1 000\s+\+0", texte)
    assert re.search(r"= retraite complémentaire\s+400\s+580\s+\+180\s+\+45,0 %", texte)
    assert re.search(r"= total\s+1 400\s+1 580\s+\+180\s+\+12,9 %", texte)
    assert "net de la caisse : 1 250 €" in texte


def test_la_ligne_de_commande_imprime_le_rapport(tmp_path, capsys):
    """De bout en bout, sur deux fichiers hors du dépôt : le rapport sort sur la
    sortie standard, un départ par bloc ; un refus sort en erreur, code 2."""
    (tmp_path / "releve.txt").write_text(_releve(), encoding="utf-8")
    (tmp_path / "estimation.yaml").write_text(
        yaml.safe_dump(_estimation(), allow_unicode=True), encoding="utf-8")
    code = estimation_officielle.main([
        "--releve", str(tmp_path / "releve.txt"),
        "--estimation", str(tmp_path / "estimation.yaml"),
        "--revenus-futurs", "prix", "--croissance", "0.5"])
    sortie = capsys.readouterr()
    assert code == 0, sortie.err
    assert sortie.out.count("Départ le ") == 2
    assert "Départ le 2033-06-01 (67 ans)" in sortie.out
    assert "lue le 2026-10-04 : brut mensuel, euros de 2026" in sortie.out
    assert "au rythme des prix, plus 0,50 % par an" in sortie.out
    (tmp_path / "estimation.yaml").write_text("convention: {}\n", encoding="utf-8")
    assert estimation_officielle.main([
        "--releve", str(tmp_path / "releve.txt"),
        "--estimation", str(tmp_path / "estimation.yaml")]) == 2
    assert "refusé" in capsys.readouterr().err
