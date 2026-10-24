"""Le relevé de carrière déposé sur le site, et ce que la lecture en tire.

Le simulateur accepte une carrière année par année ; ce module-ci lit le
document que la caisse imprime et écrit cette saisie à la place de l'assuré.
Il ne sait rien du PDF — `moteur/js/lecture-pdf.js` en a fait des lignes de
texte avant lui —, et tout de ce qu'une caisse écrit dessus.

Les relevés d'essai sont écrits ici, à la forme des documents officiels : un
tableau par régime, une ligne par employeur, des francs avant 2002, des
périodes assimilées sans revenu. Le lecteur est celui du site,
`moteur/js/releve-lu.js`, que node fait tourner (`tests/js/lire-releve.mjs`).
Son jumeau Python, qui faisait foi, est parti à l'action 161, étape 3, relu
et confronté avant : sa lecture des relevés d'essai reste, figée, la référence
(`tests/temoins/releves_lus.json`).
"""

from __future__ import annotations

import functools
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

from retraite_notionnelle.droit.releve import points_de_l_annee, revenu_des_points
from retraite_notionnelle.lignes import json_en_lignes
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.web.site import disponible, module, rendre

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
from lecture_pdf import lignes_pdf  # noqa: E402

pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : le lecteur du relevé ne tourne pas sans lui")

#: Le lecteur du site, que node fait tourner sur un lot de relevés.
LECTEUR = RACINE / "tests" / "js" / "lire-releve.mjs"
#: La lecture figée des relevés d'essai, sans barème et au convertisseur d'essai.
TEMOIN = RACINE / "tests" / "temoins" / "releves_lus.json"

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

#: La même caisse sur trois années, dont les points disent plus ou moins le
#: revenu : en 2003, cent points par trimestre, quel que soit le revenu ; en
#: 2015, 412 points, sous le plafond ; en 2016, 550, le plus haut du barème.
LIBERAL_EN_POINTS = """
CARMF - Caisse autonome de retraite des médecins de France
Année Régime Points Trimestres retenus
2003 Régime de base 400 4
2015 Régime de base 412 4
2016 Régime de base 550 4
"""

#: Un exploitant agricole, sous une forme inventée : la retraite
#: proportionnelle et la complémentaire obligatoire comptent toutes deux en
#: points, chacune dans son tableau. En 2019, les 23 points du plancher.
EXPLOITANT = """
Relevé de carrière
MSA - Exploitants agricoles
Retraite de base
2018 Retraite proportionnelle 4 trim. 80 pts
2019 Retraite proportionnelle 4 trim. 23 pts
Retraite complémentaire obligatoire
2018 4 trim. 221,89 pts
"""

#: Des années que seules les complémentaires chiffrent, sous une forme
#: inventée : deux emplois en 2018, un du privé et un de la fonction publique ;
#: une année de cadre en 2010 ; une période assimilée en 2012, dont les points
#: sont ceux du salaire d'avant ; une année sans montant ni points en 2013.
DEUX_EMPLOIS = """
Relevé de carrière
Régime général
2012 Maladie 0 4
2013 Salarié 0 4
Agirc-Arrco 2018 0 trim. 12 pts
Ircantec 2018 1 trim. 30 pts
Agirc 2010 0 trim. 15 pts
Agirc-Arrco 2012 0 trim. 40 pts
"""

#: Rien qui ressemble à un relevé : la lecture doit rendre une carrière vide
#: plutôt que d'inventer des années.
SANS_RIEN = """
Bulletin de salaire de janvier 2024
Net à payer 2 431,55
Cotisation vieillesse plafonnée 6,90
"""


#: L'estimation retraite que délivre Info Retraite, à la forme du document réel
#: — lu le 22 septembre 2026, et c'est lui qui a écrit ce cas. Les noms et les
#: montants sont inventés ; la MISE EN PAGE ne l'est pas, et c'est elle qui
#: compte. Le document lu avait été ré-exporté par une suite bureautique pour
#: être anonymisé : son CONTENU — les deux tableaux, les en-têtes, les unités,
#: les pièges — est celui de la caisse, sa couche de doublure est celle de
#: l'éditeur. Les deux sont ici, parce que les deux se présenteront. Elle empile deux tableaux — les trimestres par année, les revenus
#: par période —, coupe chaque année en deux lignes, et mêle au tout des pièges
#: qui ressemblent à s'y méprendre à des lignes de carrière : un pied de page
#: daté, une valeur du point à une date, une phrase française chiffrée, une
#: projection de départ en 2060, et une couche de doublure où toute une page
#: est collée bout à bout.
ESTIMATION = """
Relevé de carrière
Détail par année
Année Durée tous régimes Durée par régime Points par régime
4 trim. L’Assurance retraite
2025 4 trim. 188,40 pts Agirc-Arrco
4 trim. L’Assurance retraite
2024 4 trim. 121,05 pts Agirc-Arrco
1 trim. L’Assurance retraite
2023 1 trim. 6,5 pts Agirc-Arrco
0 trim. L’Assurance retraite
2022 0 trim. 4 pts Ircantec
Détail de votre carrière
Employeur/activité Date début Date fin Revenus* Régime(s)
01/01/2025 31/12/2025 42 800 €
01/10/2024 31/12/2024 11 400 € L’Assurance retraite, Agirc-Arrco
FONDERIE DU NORD
01/01/2024 24/09/2024 33 600 €
06/08/2023 13/08/2023 640 € Agirc-Arrco
24/07/2023 04/08/2023 910 € L’Assurance retraite, Agirc-Arrco
INTERIM DU CENTRE
01/12/2022 31/12/2022 L’Assurance retraite
*Revenu d'activité soumis à cotisations retraite.
3 / 7 Edité le 22/09/2026
1,4386 € Valeur du point au 01/11/2025 :
Pour valider un trimestre, il faut avoir perçu un certain revenu. En 2026, il faut avoir perçu au moins 1 803,00 € pour valider 1 trimestre.
01/06/2060 169 trimestres 2 764,30 € En partant au avec , vous pourriez avoir droit à bruts par mois et
01/01/202531/12/202542 800 €01/10/202431/12/202411 400 €FONDERIE DU NORDL’Assurance retraite, Agirc-Arrco01/01/202424/09/202433 600 €
"""

#: Le relevé de carrière qu'info-retraite délivre en 2026, à la forme du
#: document réel — lu le 4 octobre 2026, dans l'ordre où `lecture_pdf` le rend
#: depuis qu'il suit le repère de la page —, mais inventé de bout en bout :
#: aucun nom, aucune date, aucun montant n'est celui d'une carrière réelle. Un
#: résumé par caisse, puis deux tableaux, des années les plus anciennes aux plus
#: récentes. « Détail par année » tient chaque année sur deux sous-lignes :
#: l'année, la durée tous régimes et les points de la complémentaire, dont le
#: nom passe en tête parce qu'il est posé un dixième de point plus haut ; puis
#: la durée du régime de base. « Détail de votre carrière » porte une ligne par
#: période, le nom de l'employeur au-dessus de son bloc, les régimes sur la
#: première ligne du bloc seulement. Une même paie y figure deux fois quand la
#: base et la complémentaire ne la voient pas tout à fait de même — une ligne
#: « L'Assurance retraite », une ligne « Agirc-Arrco » —, et une période que
#: seule l'Agirc-Arrco écrit à part y suit une ligne commune aux deux ; des
#: années y dépassent le plafond de la Sécurité sociale ; un contrat de la
#: fonction publique y est déclaré à l'Assurance retraite et à l'Ircantec ; et
#: la date de naissance n'y est qu'à moitié, dans le numéro de sécurité
#: sociale — inventé lui aussi, et impossible : un rang et une commune à zéro.
RELEVE_2026 = """
Relevé de carrière LEMOINE Camille
Vos droits par régime
L’Assurance retraite Total 21 trimestres
Ircantec Total 48 points
Agirc-Arrco Total 704,91 points
Edité le 15/09/2026 1 / 3
Relevé de carrière LEMOINE Camille
Numéro de sécurité sociale 2 98 08 99 000 000
Détail par année
Année Durée Durée par régime Points par régime
tous régimes
Agirc-Arrco 2018 0 trim. 2,90 pts
L’Assurance retraite 0 trim. (A)
Ircantec 2019 1 trim. 7 pts
L’Assurance retraite 1 trim.
Agirc-Arrco 2020 1 trim. 9,50 pts
L’Assurance retraite 1 trim.
Agirc-Arrco 2021 4 trim. 96,44 pts
L’Assurance retraite 4 trim.
Agirc-Arrco 2022 4 trim. 187,62 pts
L’Assurance retraite 4 trim.
Agirc-Arrco 2023 4 trim. 198,10 pts
L’Assurance retraite 4 trim.
Agirc-Arrco 2024 4 trim. 210,35 pts
L’Assurance retraite 4 trim.
Ircantec 2025 3 trim. 41 pts
L’Assurance retraite 3 trim.
(A) Le revenu de l’année ne valide aucun trimestre.
Edité le 15/09/2026 2 / 3
Relevé de carrière LEMOINE Camille
Détail de votre carrière 2 98 08 99 000 000
Employeur/activité Date début Date fin Revenus* Régime(s)
LIBRAIRIE DES QUAIS
02/07/2018 28/07/2018 655 € L’Assurance retraite, Agirc-Arrco
COMMUNE DE VALBRUNE
07/10/2019 20/12/2019 2 885 € L’Assurance retraite, Ircantec
08/09/2025 19/12/2025 6 045 €
MISSIONS DES DEUX RIVES
02/03/2020 27/03/2020 1 165 € L’Assurance retraite, Agirc-Arrco
10/01/2022 25/02/2022 4 065 €
MISSIONS DES DEUX RIVES
06/04/2020 24/04/2020 845 € Agirc-Arrco
CENTRE DE FORMATION DU LITTORAL
07/09/2020 27/11/2020 L’Assurance retraite
TRANSPORTS VALLIER
02/03/2021 17/12/2021 18 315 € L’Assurance retraite
03/01/2022 16/12/2022 30 485 €
TRANSPORTS VALLIER
02/03/2021 18/06/2021 7 285 € Agirc-Arrco
21/06/2021 26/11/2021 9 135 €
29/11/2021 17/12/2021 1 905 €
03/01/2022 15/12/2022 30 715 €
ATELIERS DU PORT
04/01/2023 22/12/2023 49 765 € L’Assurance retraite, Agirc-Arrco
03/01/2024 20/12/2024 52 345 €
*Revenu d'activité soumis à cotisations retraite.
Edité le 15/09/2026 3 / 3
"""

#: Le seul tableau des années du relevé de 2026, collé sans le résumé qui le
#: précède : chaque année s'y ouvre sur la ligne de sa complémentaire, et la
#: base n'est nommée qu'à la sous-ligne suivante.
TABLEAU_DES_ANNEES = """
Relevé de carrière
Numéro de sécurité sociale 1 97 03 971 00 000 12
Détail par année
Année Durée Durée par régime Points par régime
Agirc-Arrco 2018 0 trim. 2,90 pts
L’Assurance retraite 0 trim. (A)
Ircantec 2019 1 trim. 7 pts
L’Assurance retraite 1 trim.
"""

#: Le relevé d'info-retraite d'une carrière dont la dernière année s'arrête en
#: juin, inventé de bout en bout : les mois qui suivent manquent, que les
#: régimes ne les aient pas encore enregistrés ou qu'ils n'aient pas été
#: travaillés.
DERNIERE_ANNEE_INCOMPLETE = """
Relevé de carrière
Détail de votre carrière
Employeur/activité Date début Date fin Revenus* Régime(s)
IMPRIMERIE DES COTEAUX
05/09/2016 23/12/2016 7 340 € L’Assurance retraite, Agirc-Arrco
03/01/2017 22/12/2017 24 610 €
02/01/2018 21/12/2018 25 870 €
02/01/2019 14/06/2019 12 930 €
*Revenu d'activité soumis à cotisations retraite.
Edité le 06/03/2020 2 / 2
"""

#: Les deux écarts que la relecture des deux lecteurs a trouvés, avant le
#: retrait du jumeau Python (action 161, étape 3) : une marque qui se combine à
#: sa lettre hors des accents courants, qui coupait en deux, sous le
#: JavaScript, le nom d'un régime ou d'un motif ; et un compte de trimestres
#: étiqueté qui n'est pas entier, que le JavaScript gardait tel quel.
MARQUE_RARE = chr(0x1DC4)
ECARTS_DE_LA_RELECTURE = f"""
Re{MARQUE_RARE}levé de carrière
Re{MARQUE_RARE}gime général
2010 SOCIETE 29 500 € 2,5 trim.
2011 Se{MARQUE_RARE}rvice national 4
"""

RELEVES = {
    "ecarts_de_la_relecture": ECARTS_DE_LA_RELECTURE,
    "estimation": ESTIMATION,
    "releve_2026": RELEVE_2026,
    "tableau_des_annees": TABLEAU_DES_ANNEES,
    "regime_general": REGIME_GENERAL,
    "tous_regimes": TOUS_REGIMES,
    "ancienne": ANCIENNE,
    "liberal": LIBERAL,
    "liberal_en_points": LIBERAL_EN_POINTS,
    "exploitant": EXPLOITANT,
    "deux_emplois": DEUX_EMPLOIS,
    "sans_rien": SANS_RIEN,
    "derniere_annee_incomplete": DERNIERE_ANNEE_INCOMPLETE,
    "derniere_annee_au_premier": DERNIERE_ANNEE_INCOMPLETE.replace("14/06/2019",
                                                                   "01/03/2019"),
}


@dataclass(frozen=True)
class LigneLue:
    """Une année, telle que le lecteur l'a rendue."""

    annee: int
    statut: str
    revenu: float
    trimestres: int | None
    motif: str | None
    source: str


@dataclass(frozen=True)
class Lecture:
    """Ce que le lecteur a rendu d'un relevé, comme le site le reçoit."""

    lignes: tuple[LigneLue, ...]
    interruptions: tuple[tuple[int, int, str], ...]
    ignorees: tuple[str, ...]
    regimes: tuple[str, ...]
    notes: tuple[str, ...]
    naissance: str | None
    mois_de_naissance: str | None
    saisie: tuple[tuple[str, str], ...]

    @property
    def vide(self) -> bool:
        return not self.lignes

    def parametres(self) -> dict[str, str]:
        """La saisie du formulaire : le relevé, et les interruptions."""
        return dict(self.saisie)


def _en_lecture(brut: dict) -> Lecture:
    return Lecture(tuple(LigneLue(*ligne) for ligne in brut["lignes"]),
                   tuple(tuple(plage) for plage in brut["interruptions"]),
                   tuple(brut["ignorees"]), tuple(brut["regimes"]), tuple(brut["notes"]),
                   brut["naissance"], brut["mois_de_naissance"],
                   tuple(brut["saisie"].items()))


def _lire_en_lot(cas: list[dict]) -> list[dict]:
    """La lecture brute de chaque cas, par node, en un seul appel."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as fichier:
        json.dump(cas, fichier, ensure_ascii=False)
        fichier.flush()
        execution = subprocess.run(["node", str(LECTEUR), fichier.name], cwd=RACINE,
                                   capture_output=True, text=True, encoding="utf-8",
                                   check=False)
    assert execution.returncode == 0, execution.stdout + execution.stderr
    return json.loads(execution.stdout)


def lire_releve(lignes: list[str], annee_maximale: int | None = None,
                convertisseur: str | None = None) -> Lecture:
    """Un relevé lu par le lecteur du site ; le convertisseur des points est
    ``None``, ``"modele"`` (le barème du scénario 1, comme le site) ou
    ``"par_cent"`` (l'essai de ``tests/js/lire-releve.mjs``)."""
    (brut,) = _lire_en_lot([{"lignes": lignes, "anneeMaximale": annee_maximale,
                             "convertisseur": convertisseur}])
    return _en_lecture(brut)


#: Les convertisseurs sous lesquels chaque relevé d'essai se lit.
CONVERTISSEURS = (None, "par_cent", "modele")


@functools.lru_cache(maxsize=None)
def _lectures() -> dict[tuple[str, str | None], dict]:
    """Chaque relevé d'essai sous chaque convertisseur, lus d'un seul appel."""
    cles = [(nom, convertisseur) for nom in sorted(RELEVES)
            for convertisseur in CONVERTISSEURS]
    bruts = _lire_en_lot([{"lignes": RELEVES[nom].strip().split("\n"),
                           "convertisseur": convertisseur} for nom, convertisseur in cles])
    return dict(zip(cles, bruts))


def _lire(nom: str, convertisseur: str | None = None) -> Lecture:
    return _en_lecture(_lectures()[(nom, convertisseur)])


@pytest.fixture(scope="module")
def moteur():
    """Le scénario 1, dont le barème convertit les points en revenu."""
    return Simulateur().scenario_actuel


@pytest.fixture(scope="module")
def convertir(moteur):
    """Le barème du modèle, qui dit ce que la lecture doit trouver."""
    return functools.partial(revenu_des_points, moteur)


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
    un chiffre que le relevé ne porte pas. Sans le barème que l'appelant passe,
    l'année reste sans montant, et la note le dit."""
    lecture = _lire("liberal")
    assert [ligne.annee for ligne in lecture.lignes] == [2015, 2016]
    assert all(ligne.revenu == 0 for ligne in lecture.lignes)
    assert all(ligne.trimestres == 4 for ligne in lecture.lignes)
    assert any("points" in note for note in lecture.notes)


def test_les_points_d_un_liberal_disent_son_revenu(moteur):
    """Le barème du régime de base des libéraux convertit les points en
    revenu : le plus bas qui les ouvre, que la pension recalculée de la saisie
    retrouve. En 2016, ce sont les 550 points du plafond, et la note dit que le
    revenu a pu le dépasser ; en 2003, cent points par trimestre ne disent
    aucun revenu, et l'année reste sans montant, signalée comme telle."""
    lecture = _lire("liberal_en_points", "modele")
    lues = {ligne.annee: ligne for ligne in lecture.lignes}
    assert lues[2003].revenu == 0
    assert points_de_l_annee(moteur, "medecin_liberal", 2015, "base",
                             lues[2015].revenu, 4) >= 412 - 1e-6
    assert lues[2016].revenu == round(5 * moteur.macro.plafond_securite_sociale(2016))
    (convertie,) = [note for note in lecture.notes if "ne chiffre qu'en points" in note]
    assert "2015 et 2016" in convertie and "En 2016, ce sont les points du plafond" in convertie
    (sans_revenu,) = [note for note in lecture.notes if "sans revenu" in note]
    assert sans_revenu.startswith("L'année 2003 est lue sans revenu")


def test_une_annee_que_seule_la_complementaire_chiffre(moteur):
    """Le tableau des années du relevé de 2026, collé seul, ne porte aucun
    revenu : les points de l'Agirc-Arrco et de l'Ircantec le disent, chacun au
    barème du statut qui les ouvre."""
    lecture = _lire("tableau_des_annees", "modele")
    lues = {ligne.annee: ligne for ligne in lecture.lignes}
    assert lues[2018].statut == "salarie_prive_non_cadre"
    assert lues[2019].statut == "contractuel_public"
    assert points_de_l_annee(moteur, "salarie_prive_non_cadre", 2018, "complementaire",
                             lues[2018].revenu, 0) >= 2.90 - 1e-6
    assert points_de_l_annee(moteur, "contractuel_public", 2019, "complementaire",
                             lues[2019].revenu, 1) >= 7 - 1e-6
    assert not any("sans revenu" in note for note in lecture.notes)
    # Une année qui porte un revenu le garde : ses points ne s'y ajoutent pas.
    assert _lire("releve_2026", "modele").parametres() == _lire("releve_2026").parametres()


def test_la_base_et_la_complementaire_d_un_emploi_disent_chacune_un_plancher(convertir):
    """Les points de la retraite proportionnelle et ceux de la complémentaire
    disent chacun un revenu que l'exploitant a au moins atteint : l'année prend
    le plus haut. Les 23 points du plancher ne disent rien."""
    lues = {ligne.annee: ligne for ligne in _lire("exploitant", "modele").lignes}
    base = convertir("exploitant_agricole", 2018, "base", 80, 4)
    complementaire = convertir("exploitant_agricole", 2018, "complementaire", 221.89, 4)
    assert lues[2018].revenu == max(base.revenu, complementaire.revenu)
    assert lues[2019].revenu == 0


def test_deux_emplois_chiffres_en_points_s_ajoutent():
    """Deux statuts la même année sont deux emplois : leurs revenus s'ajoutent,
    et l'année prend le statut du plus grand. Une année de cadre convertit
    ses points au barème du cadre ; une période assimilée ne convertit rien,
    ses points étant ceux du salaire d'avant."""
    lecture = _lire("deux_emplois", "par_cent")
    lues = {ligne.annee: ligne for ligne in lecture.lignes}
    assert (lues[2018].revenu, lues[2018].statut) == (4200, "contractuel_public")
    assert (lues[2010].revenu, lues[2010].statut) == (1500, "salarie_prive_cadre")
    assert lues[2012].revenu == 0 and lecture.interruptions == ((2012, 2012, "maladie"),)
    (sans_revenu,) = [note for note in lecture.notes if "sans revenu" in note]
    assert sans_revenu.startswith("L'année 2013 est lue sans revenu")


def test_l_estimation_d_info_retraite_se_lit_en_entier():
    """Le document réel, et les cinq pièges qu'il porte.

    C'est le premier vrai relevé que la lecture ait vu, et il a corrigé quatre
    défauts d'un coup. Ce cas les tient tous : les deux tableaux qui se
    complètent — les trimestres d'un côté, les revenus de l'autre —, l'année
    coupée en deux lignes, la période que seule une caisse complémentaire a
    reportée, et les quatre lignes qui ressemblent à une carrière sans en être
    une.
    """
    lecture = _lire("estimation")
    lues = {ligne.annee: ligne for ligne in lecture.lignes}

    # Les années du relevé, et elles seules : ni 2026 (le pied de page et la
    # phrase sur le revenu minimum), ni 2060 (une projection de départ).
    assert sorted(lues) == [2022, 2023, 2024, 2025]

    # Les revenus s'additionnent sur l'année, la période que seule l'Agirc-Arrco
    # a reportée comprise — 640 € qu'une lecture qui jette ces lignes perdait.
    assert round(lues[2023].revenu) == 640 + 910
    assert round(lues[2024].revenu) == 33_600 + 11_400
    assert round(lues[2025].revenu) == 42_800

    # Les trimestres viennent de l'AUTRE tableau, celui qui n'a pas de revenus,
    # et dont chaque ligne nomme une caisse complémentaire.
    assert [lues[annee].trimestres for annee in (2022, 2023, 2024, 2025)] == [0, 1, 4, 4]

    # 1,4386 € n'est pas un revenu de 2025 : c'est la valeur du point, datée.
    assert round(lues[2025].revenu) == 42_800
    # La ligne de carrière dont la cellule « revenus » est vide ressort telle
    # quelle : elle existe, et le lecteur doit pouvoir la compléter.
    assert any("01/12/2022" in ligne for ligne in lecture.ignorees)


def test_le_releve_de_2026_se_lit_en_entier():
    """Les années, les trimestres du premier tableau, les revenus du second,
    et ce qui ne se lit pas : la période d'une formation sans revenu, que le
    lecteur doit voir pour la compléter. Le pied de page daté, le numéro de
    sécurité sociale et le résumé par caisse ne font aucune année."""
    lecture = _lire("releve_2026")
    lues = {ligne.annee: ligne for ligne in lecture.lignes}
    assert sorted(lues) == list(range(2018, 2026))
    assert [lues[annee].trimestres for annee in sorted(lues)] == [0, 1, 1, 4, 4, 4, 4, 3]
    assert {annee: round(ligne.revenu) for annee, ligne in lues.items()} == {
        2018: 655, 2019: 2_885, 2020: 1_165 + 845, 2021: 18_315,
        2022: 30_485 + 4_065, 2023: 49_765, 2024: 52_345, 2025: 6_045,
    }
    assert lecture.ignorees == ("07/09/2020 27/11/2020 L’Assurance retraite",)
    assert lecture.regimes == ("regime_general", "ircantec", "arrco")
    # La date entière n'y est pas : le numéro de sécurité sociale n'en dit
    # que le mois.
    assert lecture.naissance is None
    assert lecture.mois_de_naissance == "1998-08"


@pytest.mark.parametrize(("numero", "premiere", "attendu"), [
    ("1 05 11 99 000 000", 2023, "2005-11"),
    ("2 62 05 99 000 000 41", 1981, "1962-05"),
    ("1 62 05 2A 000 000", 1981, "1962-05"),
    ("1 62 05 971 00 000", 1981, "1962-05"),
    ("2 62 20 99 000 000", 1981, None),
])
def test_le_numero_de_securite_sociale_donne_le_mois_de_naissance(numero, premiere,
                                                                  attendu):
    """Le relevé d'info-retraite ne porte pas la date de naissance en clair,
    mais son numéro de sécurité sociale en porte l'année, sans le siècle, et
    le mois. Le siècle se lit dans la carrière : l'année de naissance est la
    dernière qui finit par ces deux chiffres sans dépasser la première année
    travaillée. Un mois hors de 01 à 12 ne se lit pas. Et le numéro ne
    ressort nulle part : ni dans la saisie, ni dans une ligne ignorée, ni dans
    une note."""
    lecture = lire_releve(["Relevé de carrière", f"Numéro de sécurité sociale {numero}",
                           "Régime général", f"{premiere} EMPLOI SAISONNIER 3 200 2"])
    assert lecture.naissance is None
    assert lecture.mois_de_naissance == attendu
    assert [ligne.annee for ligne in lecture.lignes] == [premiere]
    sorties = [*lecture.parametres().values(), *lecture.ignorees, *lecture.notes,
               *(ligne.source for ligne in lecture.lignes)]
    assert not any(numero[2:8] in sortie for sortie in sorties)
    # La date de naissance écrite en clair l'emporte, et donne son mois.
    assert _lire("regime_general").mois_de_naissance == "1962-05"


def test_une_paie_vue_par_la_base_et_par_la_complementaire_ne_compte_qu_une_fois():
    """Quand la base et la complémentaire ne voient pas la même paie tout à
    fait de même — une date, quelques euros —, le relevé la porte deux fois
    sous le même employeur : un bloc qui ne nomme que « L'Assurance
    retraite », un bloc qui ne nomme que « Agirc-Arrco », chacun poursuivi
    sans le répéter. Les additionner doublait le revenu de l'année ; c'est
    celui de la base qui compte."""
    lecture = _lire("releve_2026")
    lues = {ligne.annee: ligne for ligne in lecture.lignes}
    assert round(lues[2021].revenu) == 18_315
    assert round(lues[2022].revenu) == 30_485 + 4_065
    assert any("une seconde fois" in note for note in lecture.notes)
    assert not any("une seconde fois" in note for note in _lire("tous_regimes").notes)


def test_une_periode_que_seule_la_complementaire_ecrit_compte_sans_base_a_part():
    """Une ligne « Agirc-Arrco » qui suit une ligne commune aux deux caisses,
    l'année où rien ne nomme la base seule, n'a pas de double : elle écrit à
    part une période que la base compte aussi. Le relevé réel du 4 octobre le
    montre, dont la base valide un trimestre que ses propres lignes, sans
    celle-ci, n'atteignent pas. Ici, 1 165 € ne valident aucun trimestre en
    2020 — le seuil est de 150 fois le SMIC horaire, 1 522,50 € —, et la base
    en compte un : il faut les 845 € de la ligne « Agirc-Arrco »."""
    lues = {ligne.annee: ligne for ligne in _lire("releve_2026").lignes}
    assert round(lues[2020].revenu) == 1_165 + 845
    assert lues[2020].trimestres == 1


def test_la_premiere_annee_du_tableau_ne_se_perd_pas_sans_le_resume():
    """Lu dans l'ordre de la page, le tableau des années nomme la complémentaire
    d'une année avant sa base. Sans le résumé qui le précède, rien n'avait
    encore nommé de base à la première année, et sa ligne ressortait parmi
    celles qu'on ne comprend pas : elle prend la première base que le document
    nomme."""
    lecture = _lire("tableau_des_annees")
    assert [(ligne.annee, ligne.trimestres, ligne.statut) for ligne in lecture.lignes] == [
        (2018, 0, "salarie_prive_non_cadre"), (2019, 1, "contractuel_public")]
    assert lecture.ignorees == ()
    # Son numéro, inventé, est celui d'un assuré né outre-mer, clé comprise.
    assert lecture.mois_de_naissance == "1997-03"


def test_l_ircantec_avec_la_base_dit_un_contractuel_public():
    """« L'Assurance retraite, Ircantec » : le régime général et l'Ircantec
    couvrent ensemble un agent contractuel de la fonction publique, et non un
    salarié du privé. La ligne qui suit dans le bloc, sans répéter les
    régimes, relève du même contrat."""
    lecture = _lire("releve_2026")
    statuts = {ligne.annee: ligne.statut for ligne in lecture.lignes}
    assert statuts[2019] == "contractuel_public"
    assert statuts[2025] == "contractuel_public"
    assert statuts[2024] == "salarie_prive_non_cadre"
    assert any("Ircantec" in note for note in lecture.notes)


def test_le_releve_de_2026_se_lit_dans_son_pdf_comme_dans_ses_lignes():
    """Le document tel qu'info-retraite le fabrique : un repère retourné en
    vingtièmes de point, une ``Tm`` par ligne, la page coupée en deux flux au
    milieu d'un objet texte. Lu sans le repère, il sortait du bas vers le
    haut, et chaque ligne de bloc prenait le régime du bloc du dessous."""
    lignes = RELEVE_2026.strip().split("\n")
    pdf = _pdf_d_info_retraite(lignes)
    assert lignes_pdf(pdf) == lignes
    assert lire_releve(lignes_pdf(pdf)).parametres() == _lire("releve_2026").parametres()


def _pdf_d_info_retraite(lignes: list[str]) -> bytes:
    """Un PDF à la façon du relevé d'info-retraite (2026), une ligne par ``Tm``.

    Le texte est en WinAnsi, que la police déclare, avec une table ToUnicode
    pour le signe euro et l'apostrophe ; la page pose deux flux, et le second
    commence au milieu d'un objet texte."""
    def chaine(ligne: str) -> bytes:
        brut = ligne.encode("cp1252")
        for special in (b"\\", b"(", b")"):
            brut = brut.replace(special, b"\\" + special)
        return b"(" + brut + b")"

    poses = [b"1 0 0 -1 794 %d Tm %s Tj" % (900 + 280 * rang, chaine(ligne))
             for rang, ligne in enumerate(lignes)]
    moitie = len(poses) // 2
    premier = (b"0.05 0 0 -0.05 0 841.9 cm BT /F1 180 Tf "
               + b" ".join(poses[:moitie]))
    second = b" ".join(poses[moitie:]) + b" ET"
    table = (b"1 begincodespacerange\n<00> <FF>\nendcodespacerange\n"
             b"2 beginbfchar\n<80> <20AC>\n<92> <2019>\nendbfchar\n")

    def objet(numero: int, corps: bytes) -> bytes:
        return b"%d 0 obj\n" % numero + corps + b"\nendobj\n"

    def flux(donnees: bytes) -> bytes:
        return b"<< /Length %d >>\nstream\n" % len(donnees) + donnees + b"\nendstream"

    return (b"%PDF-1.5\n"
            + objet(1, b"<< /Type /Page /Resources << /Font << /F1 4 0 R >> >> "
                       b"/Contents [2 0 R 3 0 R] >>")
            + objet(2, flux(premier)) + objet(3, flux(second))
            + objet(4, b"<< /Type /Font /Subtype /TrueType "
                       b"/Encoding /WinAnsiEncoding /ToUnicode 5 0 R >>")
            + objet(5, flux(table))
            + b"trailer\n<< >>\n%%EOF\n")


def test_une_marque_rare_et_des_trimestres_non_entiers_se_lisent_sans_ecart():
    """Une marque qui se combine à sa lettre s'efface comme un accent : le
    titre, le régime et le motif se reconnaissent. Un compte de trimestres est
    entier : « 2,5 trim. » en compte deux, et la saisie ne reçoit jamais de
    fraction."""
    lecture = _lire("ecarts_de_la_relecture")
    lues = {ligne.annee: ligne for ligne in lecture.lignes}
    assert sorted(lues) == [2010, 2011]
    assert (round(lues[2010].revenu), lues[2010].trimestres) == (29_500, 2)
    assert lecture.interruptions == ((2011, 2011, "service_militaire"),)
    assert lecture.regimes == ("regime_general",)
    assert lecture.parametres()["releve"].split("\n")[0] == "2010:salarie_prive_non_cadre:29500:2"


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
    dire à qui dépose son relevé plutôt que de le laisser croire exact. Le
    relevé d'info-retraite, lui, porte le « revenu d'activité soumis à
    cotisations retraite », plafond franchi compris — 52 345 € en 2024, pour
    un plafond de 46 368 € — : la même note y serait fausse."""
    assert any("plafonné" in note for note in _lire("regime_general").notes)
    assert not any("plafonné" in note for note in _lire("releve_2026").notes)


def test_le_releve_incomplet_avant_le_depart_est_dit():
    """Un relevé n'est souvent complet qu'à la liquidation : le chômage non
    indemnisé, le service militaire, les périodes reconnues équivalentes
    accomplies à l'étranger n'entrent au compte qu'à une régularisation
    tardive, le plus souvent au départ (DREES, Dossier solidarité et santé
    n° 37, mars 2013, encadré 1). Un relevé déposé plus tôt peut les omettre,
    et rien, dans le document, ne dit s'il est déjà complet : la note
    accompagne toute carrière lue, et aucun document dont rien n'a été lu."""
    for nom in RELEVES:
        lecture = _lire(nom)
        dite = any("incomplet avant le départ" in note for note in lecture.notes)
        assert dite == bool(lecture.lignes), nom


def _arret(lignes: list[str]) -> list[str]:
    return [note for note in lire_releve(lignes).notes
            if note.startswith("Le relevé s'arrête le ")]


@pytest.mark.parametrize(("fin", "dite"), [
    ("14/06/2019", "14 juin 2019"),
    ("01/03/2019", "1er mars 2019"),
    ("29/11/2019", "29 novembre 2019"),
    ("16/12/2019", None),
])
def test_une_derniere_annee_qui_s_arrete_avant_decembre_est_dite(fin, dite):
    """Le relevé d'info-retraite date ses périodes, et sa dernière année n'est
    souvent pas finie : les régimes enregistrent les droits les plus récents
    avec retard, le document le dit lui-même. La simulation compte pourtant
    chaque ligne pour une année entière et prolonge jusqu'au départ le revenu de
    la dernière — celui de quelques mois, vu comme celui d'une année. Quand la
    période la plus tardive finit avant décembre, la note le dit, avec sa date,
    et invite à compléter la carrière ou à déclarer les années sans emploi ; une
    période finie en décembre ne laisse aucun mois entier à ajouter."""
    notes = _arret(DERNIERE_ANNEE_INCOMPLETE.replace("14/06/2019", fin).strip().split("\n"))
    if dite is None:
        assert not notes
        return
    assert len(notes) == 1
    assert notes[0].startswith(f"Le relevé s'arrête le {dite} : ")
    assert "ajoutez au revenu de 2019 ce que vous avez gagné après cette date" in notes[0]
    assert "« Interruptions »" in notes[0]


def test_la_fin_du_releve_est_celle_de_sa_periode_la_plus_tardive():
    """Une période sans revenu couvre ses mois autant qu'un emploi : une
    maladie qui suit le dernier emploi recule la date où le relevé s'arrête.
    Un relevé sans dates n'a rien à en dire, ni un relevé dont la dernière
    période finit en décembre — l'estimation le 31, le relevé de 2026 le 19."""
    lignes = DERNIERE_ANNEE_INCOMPLETE.strip().split("\n")
    rang = lignes.index("*Revenu d'activité soumis à cotisations retraite.")
    maladie = lignes[:rang] + ["MALADIE", "17/06/2019 29/11/2019 L’Assurance retraite"]
    assert _arret(maladie + lignes[rang:])[0].startswith(
        "Le relevé s'arrête le 29 novembre 2019 : ")
    for nom in ("regime_general", "tous_regimes", "estimation", "releve_2026"):
        assert _arret(RELEVES[nom].strip().split("\n")) == [], nom


def test_tous_les_statuts_cites_existent_au_catalogue():
    """Un statut mal orthographié ferait un refus de saisie à l'import, et
    l'assuré n'aurait aucun moyen de comprendre pourquoi."""
    codes = set(Simulateur().affiliations.codes)
    regimes = module("releve-lu").REGIMES
    inconnus = {regime.statut for regime in regimes if regime.statut not in codes}
    assert not inconnus, f"statuts absents du catalogue : {sorted(inconnus)}"


def test_la_saisie_produite_se_simule_sans_refus():
    """Le bout du chemin : ce que la lecture écrit doit être ce que le
    formulaire accepte. Une saisie que le simulateur refuse serait un import
    qui échoue chez le lecteur, après le dépôt de son relevé."""
    parametres = _lire("regime_general").parametres()
    _, corps = rendre("/simuler", {
        "naissance": "1978-05-01", "depart": "2043-05-01",
        "releve": parametres["releve"], "interruptions": parametres["interruptions"],
    })
    assert 'class="erreur"' not in corps, corps[:400]


@pytest.mark.parametrize("convertisseur", [None, "par_cent"], ids=["sans_bareme", "par_cent"])
def test_les_releves_d_essai_se_lisent_comme_la_lecture_figee(convertisseur):
    """Le jumeau Python du lecteur faisait foi, et ce test comparait le site à
    lui. Il est parti à l'action 161, étape 3, relu fonction par fonction et
    confronté avant sur des milliers de relevés ; sa lecture des relevés
    d'essai reste, figée dans `tests/temoins/releves_lus.json` : la référence
    du lecteur du site, au caractère près — les années, la saisie, les lignes
    ignorées, les régimes, les notes, la naissance. Le barème du modèle n'y
    entre pas, qui bouge avec les données : ses conversions ont leurs tests,
    plus haut. Une lecture qui change exprès se refige, dans un commit à elle :
    ``REFIGER_LES_RELEVES_LUS=1 python -m pytest tests/test_releve_lu.py -k figee``."""
    cle = convertisseur or "sans_bareme"
    lues = {nom: _lectures()[(nom, convertisseur)] for nom in sorted(RELEVES)}
    temoin = json.loads(TEMOIN.read_text(encoding="utf-8"))
    if os.environ.get("REFIGER_LES_RELEVES_LUS"):
        temoin[cle] = lues
        TEMOIN.write_text(json_en_lignes(temoin) + "\n", encoding="utf-8")
        pytest.skip(f"lecture refigée : {TEMOIN.relative_to(RACINE)}, {cle}")
    assert sorted(temoin[cle]) == sorted(RELEVES), "un relevé d'essai sans lecture figée"
    for nom in sorted(RELEVES):
        assert lues[nom] == temoin[cle][nom], nom
