"""Le relevé de carrière déposé sur le site, et ce que la lecture en tire.

Le simulateur accepte une carrière année par année ; ce module-ci lit le
document que la caisse imprime et écrit cette saisie à la place de l'assuré.
Il ne sait rien du PDF — `moteur/js/lecture-pdf.js` en a fait des lignes de
texte avant lui —, et tout de ce qu'une caisse écrit dessus.

Les relevés d'essai sont écrits ici, à la forme des documents officiels : un
tableau par régime, une ligne par employeur, des francs avant 2002, des
périodes assimilées sans revenu. Chacun passe par les DEUX implémentations, et
la saisie qu'elles rendent doit être la même au caractère près.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.web.pages import Contexte, rendre
from retraite_notionnelle.web.releve_lu import REGIMES, lire_releve

RACINE = Path(__file__).resolve().parents[1]

#: Le relevé du régime général : une caisse, un tableau, une ligne par employeur
#: — et une année coupée en deux, moitié emploi moitié chômage.
REGIME_GENERAL = """
Relevé de carrière
DUPONT Marie — Date de naissance : 12/05/1962
Régime général
Année Employeur ou situation Revenu d'activité Trimestres
1998 GARAGE MARTIN 94 500 4
1999 GARAGE MARTIN 98 200 4
2000 GARAGE MARTIN 51 000 2
2000 Chômage 2
2001 SOCIETE DUPONT SA 112 400 4
2002 SOCIETE DUPONT SA 18 300 4
2003 SOCIETE DUPONT SA 19 100 4
Total 22 trimestres
"""

#: Le relevé de situation individuelle : un tableau par régime, des points pour
#: les complémentaires, un état de services pour la fonction publique.
TOUS_REGIMES = """
Relevé de situation individuelle
Année Situation Revenus Nombre de trimestres
Régime général (Cnav)
2010 Salarié 29 500 4
2011 Salarié 30 100 4
2012 Maladie 0 4
2013 Salarié 31 800 4
Agirc-Arrco
2010 Points Arrco 320,50
2011 Points Agirc 415,20
Ircantec
2005 Points 120
Service des retraites de l'État
Services du 01/09/1996 au 31/08/2001 Professeur certifié
"""

#: Une carrière ancienne : anciens francs avant 1960, francs ensuite, service
#: national, et le passage à l'euro au milieu.
ANCIENNE = """
Relevé de carrière
Régime général
1957 USINE RENAULT 480 000 4
1958 USINE RENAULT 512 000 4
1959 Service national 4
1960 USINE RENAULT 6 400 4
1961 USINE RENAULT 7 100 4
2001 USINE RENAULT 148 000 4
2002 USINE RENAULT 23 400 4
"""

#: Une carrière de libéral : la caisse compte en points, et le relevé ne porte
#: aucun revenu qu'on puisse lire.
LIBERAL = """
CARMF - Caisse autonome de retraite des médecins de France
Année Régime Points Trimestres retenus
2015 Régime de base 550 4
2016 Régime de base 560 4
"""

#: Rien qui ressemble à un relevé : la lecture doit rendre une carrière vide
#: plutôt que d'inventer des années.
SANS_RIEN = """
Bulletin de salaire de janvier 2024
Net à payer 2 431,55
Cotisation vieillesse plafonnée 6,90
"""

RELEVES = {
    "regime_general": REGIME_GENERAL,
    "tous_regimes": TOUS_REGIMES,
    "ancienne": ANCIENNE,
    "liberal": LIBERAL,
    "sans_rien": SANS_RIEN,
}


def _lire(nom: str):
    return lire_releve(RELEVES[nom].strip().split("\n"))


def test_une_annee_coupee_par_employeur_est_recollee():
    """Un relevé coupe l'année autant de fois que l'assuré a eu d'employeurs,
    et le champ du formulaire n'accepte qu'une ligne par année : les revenus
    s'additionnent, les trimestres aussi, plafonnés à quatre."""
    lecture = _lire("regime_general")
    annees = {ligne.annee: ligne for ligne in lecture.lignes}
    assert sorted(annees) == [1998, 1999, 2000, 2001, 2002, 2003]
    # 51 000 francs et une période de chômage : le revenu est celui de l'emploi,
    # les quatre trimestres sont ceux des deux lignes réunies.
    assert annees[2000].trimestres == 4
    assert round(annees[2000].revenu) == round(51_000 / 6.55957)
    assert annees[2000].motif == "chomage_indemnise"
    # L'année garde son motif mais reste travaillée : elle porte un revenu, et
    # une année qui porte un revenu n'est pas une interruption.
    assert lecture.interruptions == ()


def test_les_francs_sont_convertis_et_les_anciens_francs_aussi():
    """Avant 2002 un relevé porte des francs, et des anciens francs avant 1960.
    Le simulateur, lui, ne connaît que l'euro de l'année."""
    lecture = _lire("ancienne")
    revenus = {ligne.annee: round(ligne.revenu) for ligne in lecture.lignes}
    assert revenus[1957] == round(480_000 / 655.957)
    assert revenus[1960] == round(6_400 / 6.55957)
    assert revenus[2002] == 23_400
    assert any("anciens francs" in note for note in lecture.notes)


def test_une_annee_sans_revenu_devient_une_interruption():
    """Le relevé nomme la période — service national, maladie, chômage — et le
    formulaire la porte dans son champ « Interruptions », par plages."""
    lecture = _lire("ancienne")
    assert lecture.interruptions == ((1959, 1959, "service_militaire"),)
    assert _lire("tous_regimes").interruptions == ((2012, 2012, "maladie"),)


def test_les_points_agirc_disent_le_cadre():
    """Aucune colonne du régime général ne dit si l'emploi était un emploi de
    cadre ; les points Agirc, eux, le disent — c'était leur objet."""
    lecture = _lire("tous_regimes")
    statuts = {ligne.annee: ligne.statut for ligne in lecture.lignes}
    assert statuts[2011] == "salarie_prive_cadre"
    assert statuts[2010] == "salarie_prive_non_cadre"
    assert statuts[2013] == "salarie_prive_non_cadre"


def test_un_regime_complementaire_ne_fait_pas_une_annee_de_plus():
    """Ses points feraient un revenu qui n'en est pas un, et ses lignes
    doubleraient celles de la base."""
    lecture = _lire("tous_regimes")
    assert [ligne.annee for ligne in lecture.lignes] == [2010, 2011, 2012, 2013]
    assert "ircantec" in lecture.regimes


def test_un_etat_de_services_sur_plusieurs_annees_est_montre_et_non_devine():
    """« du 01/09/1996 au 31/08/2001 » couvre six années, dont le relevé ne dit
    ni le revenu ni la répartition : la ligne ressort telle quelle."""
    lecture = _lire("tous_regimes")
    assert any("01/09/1996" in ligne for ligne in lecture.ignorees)


def test_un_regime_en_points_ne_rend_aucun_revenu():
    """La CARMF compte en points : lire 550 comme un revenu de 550 € écrirait
    un chiffre que le relevé ne porte pas."""
    lecture = _lire("liberal")
    assert [ligne.annee for ligne in lecture.lignes] == [2015, 2016]
    assert all(ligne.revenu == 0 for ligne in lecture.lignes)
    assert all(ligne.trimestres == 4 for ligne in lecture.lignes)
    assert any("points" in note for note in lecture.notes)


def test_un_document_qui_n_est_pas_un_releve_ne_rend_pas_de_carriere():
    """Une fiche de paie porte une année et des nombres ; elle ne décrit aucune
    carrière, et la lecture ne doit pas en fabriquer une.

    C'est un vrai document qui l'a imposé : le rapport de l'OPEF sur les frais
    de l'épargne retraite, cent pages sans le moindre relevé, nommait au
    passage la Banque de France et rendait vingt-deux « années de carrière »
    qui n'avaient jamais existé. Un formulaire rempli de ces chiffres-là serait
    pire que vide : le lecteur les corrigerait au lieu de comprendre qu'il
    s'est trompé de fichier. On exige donc de reconnaître le document — son
    titre, ou l'en-tête de la colonne des trimestres.
    """
    lecture = _lire("sans_rien")
    assert lecture.vide
    assert any("ne ressemble pas" in note for note in lecture.notes)


def test_la_date_de_naissance_de_l_en_tete_est_lue():
    """Le relevé la porte en tête, et c'est la seule donnée du formulaire, hors
    la carrière, qu'il donne — celle dont l'âge légal et la durée requise
    dépendent. La ligne qui la porte n'est pas pour autant une année de
    carrière : lue comme telle, elle ouvrirait un emploi à zéro an."""
    lecture = _lire("regime_general")
    assert lecture.naissance == "1962-05-12"
    assert 1962 not in {ligne.annee for ligne in lecture.lignes}
    assert _lire("liberal").naissance is None


def test_le_plafond_du_releve_est_dit():
    """Le revenu porté au compte du régime général s'arrête au plafond de la
    Sécurité sociale : le simulateur lit donc un salaire tronqué, et il doit le
    dire à qui dépose son relevé plutôt que de le laisser croire exact."""
    assert any("plafonné" in note for note in _lire("regime_general").notes)


def test_tous_les_statuts_cites_existent_au_catalogue():
    """Un statut mal orthographié ferait un refus de saisie à l'import, et
    l'assuré n'aurait aucun moyen de comprendre pourquoi."""
    codes = set(Contexte().simulateur().affiliations.codes)
    inconnus = {regime.statut for regime in REGIMES if regime.statut not in codes}
    assert not inconnus, f"statuts absents du catalogue : {sorted(inconnus)}"


def test_la_saisie_produite_se_simule_sans_refus():
    """Le bout du chemin : ce que la lecture écrit doit être ce que le
    formulaire accepte. Une saisie que le simulateur refuse serait un import
    qui échoue chez le lecteur, après le dépôt de son relevé."""
    parametres = _lire("regime_general").parametres()
    _, corps = rendre(Contexte(), "/simuler", {
        "naissance": "1978-05-01", "depart": "2043-05-01",
        "releve": parametres["releve"], "interruptions": parametres["interruptions"],
    })
    assert 'class="erreur"' not in corps, corps[:400]


def test_le_portage_javascript_lit_les_memes_releves():
    """Le site lit le PDF déposé avec `moteur/js/releve-lu.js` ; ce fichier-ci
    fait foi. Les deux doivent rendre la MÊME saisie — le relevé, les
    interruptions, les lignes ignorées, les régimes et les notes."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    noms = sorted(RELEVES)
    entree = [RELEVES[nom].strip().split("\n") for nom in noms]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as fichier:
        json.dump(entree, fichier, ensure_ascii=False)
        fichier.flush()
        execution = subprocess.run(
            ["node", "tests/js/comparer-releve.mjs", fichier.name],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8",
            check=False,
        )
    assert execution.returncode == 0, execution.stdout + execution.stderr
    rendu = json.loads(execution.stdout)

    for nom, javascript in zip(noms, rendu):
        lecture = lire_releve(RELEVES[nom].strip().split("\n"))
        attendu = dict(lecture.parametres())
        attendu["ignorees"] = list(lecture.ignorees)
        attendu["regimes"] = list(lecture.regimes)
        attendu["notes"] = list(lecture.notes)
        attendu["naissance"] = lecture.naissance
        assert javascript == attendu, nom
