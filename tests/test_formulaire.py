"""Le formulaire du simulateur garde ce qu'on lui a dit.

Trois fautes l'ont fait oublier, chacune sans un mot. Le formulaire d'un
retraité ne renvoyait pas sa situation : « Calculer » le ramenait au formulaire
d'un actif, sa pension ignorée, le calcul fait sur le salaire de l'exemple. Une
saisie refusée se rendait sur le formulaire de l'exemple : une date de trop, et
toute la carrière était à retaper. Et rien de ce qui avait été saisi ne
survivait à un détour par une autre page — ce que le script d'``index.html``
tient désormais dans le stockage du navigateur, et que les derniers essais
vérifient de loin, faute de navigateur dans la suite.

Les formulaires sont lus ici comme un navigateur les soumet : les champs
nommés et actifs, l'option choisie de chaque menu, le texte de chaque zone, les
champs vides en moins — ce que fait l'écouteur de soumission d'``index.html``.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from retraite_notionnelle.web.pages import (
    AGE_DEBUT_MAXIMAL,
    AGE_DEBUT_MINIMAL,
    AGE_LIQUIDATION_MAXIMAL,
    AGE_LIQUIDATION_MINIMAL,
    Contexte,
    Saisie,
    _formulaire,
    _simulateur_court,
    rendre,
)

RACINE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


class _Soumission(HTMLParser):
    """Les champs que le navigateur enverrait, pour le premier formulaire dont
    la cible est ``action``."""

    def __init__(self, action: str) -> None:
        super().__init__(convert_charrefs=True)
        self._action = action
        self._dedans = False
        self._vu = False
        self._menu: list | None = None
        self._zone: list | None = None
        self.champs: list[tuple[str, str]] = []

    def handle_starttag(self, balise: str, attributs: list) -> None:
        attrs = dict(attributs)
        if balise == "form":
            if not self._vu and attrs.get("action") == self._action:
                self._dedans = self._vu = True
            return
        if not self._dedans or "disabled" in attrs:
            return
        nom = attrs.get("name")
        if balise == "input" and nom:
            if attrs.get("type") in ("submit", "button", "file", "reset", "image"):
                return
            if attrs.get("type") in ("checkbox", "radio") and "checked" not in attrs:
                return
            self.champs.append((nom, attrs.get("value") or ""))
        elif balise == "select" and nom:
            self._menu = [nom, None, None]
        elif balise == "option" and self._menu is not None:
            valeur = attrs.get("value") or ""
            if self._menu[2] is None:
                self._menu[2] = valeur
            if "selected" in attrs:
                self._menu[1] = valeur
        elif balise == "textarea" and nom:
            self._zone = [nom, ""]

    def handle_endtag(self, balise: str) -> None:
        if balise == "form":
            self._dedans = False
        elif balise == "select" and self._menu is not None:
            nom, choisie, premiere = self._menu
            self.champs.append((nom, choisie if choisie is not None else premiere or ""))
            self._menu = None
        elif balise == "textarea" and self._zone is not None:
            self.champs.append((self._zone[0], self._zone[1]))
            self._zone = None

    def handle_data(self, donnees: str) -> None:
        if self._zone is not None:
            self._zone[1] += donnees


def _soumettre(html: str, action: str = "#/simuler") -> dict[str, str]:
    lecteur = _Soumission(action)
    lecteur.feed(html)
    assert lecteur.champs, f"aucun formulaire vers {action}"
    # La dernière valeur l'emporte et les vides ne partent pas : c'est ce que
    # fait `URLSearchParams.set` dans l'écouteur de soumission.
    envoyes: dict[str, str] = {}
    for nom, valeur in lecteur.champs:
        if valeur.strip():
            envoyes[nom] = valeur
        else:
            envoyes.pop(nom, None)
    return envoyes


BASE = {
    "unite_revenu": "euros_mois", "montants": "net", "situation": "actif",
    "saisie_par": "revenu", "naissance": "1970-04-12", "debut": "1990-09-01",
    "statut": "salarie_prive_non_cadre", "salaire": "2800",
    "liquidation": "2034-05-01",
}

SAISIES = {
    "l'exemple": {},
    # Sans revenu : saisie par la pension, la carrière n'en a pas — c'est lui
    # que la page cherche —, et le formulaire n'a pas de champ pour en porter.
    "un retraité, par sa pension": {
        **{cle: valeur for cle, valeur in BASE.items() if cle != "salaire"},
        "situation": "retraite", "saisie_par": "pension", "pension": "1780",
        "naissance": "1955-06-01", "debut": "1975-09-01",
        "liquidation": "2017-07-01",
    },
    "un retraité, par ce qu'il gagnait": {
        **BASE, "situation": "retraite", "saisie_par": "revenu",
        "naissance": "1955-06-01", "debut": "1975-09-01",
        "liquidation": "2017-07-01",
    },
    "en multiples du salaire moyen": {**BASE, "unite_revenu": "moyen", "salaire": "1.3"},
    "en brut": {**BASE, "montants": "brut", "salaire": "4200"},
    "trois périodes, dont une sans emploi": {
        **BASE, "metier2_debut": "2001-03-01", "metier2_statut": "chomage_indemnise",
        "metier3_debut": "2003-01-01", "metier3_statut": "fonctionnaire_etat",
        "metier3_salaire": "2600",
    },
    "le relevé, les options": {
        **BASE, "sexe": "F", "profil": "plat", "primes": "0.2", "enfants": "3",
        "interruptions": "1995:1996:education_enfant",
        "releve": "1998:salarie_prive_non_cadre:14200:4\n"
                  "1999:salarie_prive_non_cadre:15100:4",
    },
    "des règles, dont celles qui n'ont pas de champ": {
        **BASE, "indexation": "prix", "table": "par_sexe", "lissage": "3",
        "reprise": "40", "bascule": "2030", "euros": "2025",
        "age_reference": "cliquet_legal", "conversion_acquis": "liquidation",
    },
}


@pytest.mark.parametrize("nom", list(SAISIES))
def test_le_formulaire_renvoie_tout_ce_qu_il_a_recu(contexte, nom):
    """Rendre une saisie dans le formulaire, puis le soumettre tel quel, rend la
    même saisie. Un champ que le formulaire ne porte pas — la situation, la
    saisie par la pension, l'âge de référence — se perdait au premier
    « Calculer », et rien ne le disait : la page revenait, calculée sur autre
    chose."""
    saisie = Saisie.depuis_requete(SAISIES[nom])
    renvoyee = Saisie.depuis_requete(_soumettre(_formulaire(saisie, contexte)))
    assert renvoyee.requete() == saisie.requete()


def test_une_saisie_refusee_se_remontre_telle_qu_elle_a_ete_envoyee(contexte):
    """Le refus dit quoi corriger ; le formulaire garde tout le reste. Il
    repartait de l'exemple, et c'est une carrière de trois métiers qu'il
    fallait retaper pour une date."""
    envoyee = {
        **BASE, "salaire": "3100", "enfants": "2", "indexation": "prix",
        "metier2_debut": "2000-01-01", "metier2_statut": "salarie_prive_cadre",
        "metier2_salaire": "3900",
        # Le troisième commence avant le deuxième : c'est lui qui est refusé.
        "metier3_debut": "1995-06-01", "metier3_statut": "artisan",
        "metier3_salaire": "2400",
    }
    _, corps = rendre(contexte, "/simuler", envoyee)
    assert "Saisie refusée" in corps and "Métier n° 3" in corps
    assert 'id="resultats"' not in corps
    soumise = _soumettre(corps)
    assert {cle: soumise.get(cle) for cle in envoyee} == envoyee

    # Un retraité refusé garde sa pension : le formulaire reste le sien.
    retraite = {**SAISIES["un retraité, par sa pension"],
                "liquidation": "1970-01-01"}
    _, corps = rendre(contexte, "/simuler", retraite)
    assert "Saisie refusée" in corps
    soumise = _soumettre(corps)
    assert {cle: soumise.get(cle) for cle in retraite} == retraite


def test_une_ligne_incomplete_laisse_les_autres_en_place(contexte):
    """Une ligne de métier à moitié remplie ne se lit pas : la lecture s'y
    arrête, les lignes d'avant restent, et c'est la ligne vide qui suit qui
    la recevra — le script de la page y remet ce qui a été envoyé."""
    envoyee = {
        **BASE, "metier2_debut": "2000-01-01", "metier2_statut": "salarie_prive_cadre",
        "metier2_salaire": "3900", "metier3_debut": "2008-01-01",
    }
    _, corps = rendre(contexte, "/simuler", envoyee)
    assert "Saisie refusée" in corps and "Métier n° 3" in corps
    soumise = _soumettre(corps)
    assert {cle: soumise[cle] for cle in envoyee if cle != "metier3_debut"} == {
        cle: valeur for cle, valeur in envoyee.items() if cle != "metier3_debut"}
    # La ligne vide qui suit est bien la troisième.
    assert 'name="metier3_debut"' in corps and 'name="metier4_debut"' not in corps


def test_une_adresse_forgee_retombe_sur_l_exemple_sans_perdre_sa_forme(contexte):
    """Ce qui ne se lit pas du tout repart de l'exemple, mais garde ce qui décide
    de la forme du formulaire : un retraité y retrouve le champ de sa pension,
    et non celui d'un revenu."""
    _, corps = rendre(contexte, "/simuler", {
        "situation": "retraite", "montants": "brut", "naissance": "hier",
    })
    assert "Saisie refusée" in corps
    soumise = _soumettre(corps)
    assert soumise["situation"] == "retraite" and soumise["saisie_par"] == "pension"
    assert soumise["montants"] == "brut" and "pension" in soumise
    assert "salaire" not in soumise


def test_la_consigne_ne_parle_de_l_exemple_que_devant_l_exemple(contexte):
    """« L'exemple est déjà rempli » au-dessus d'une carrière saisie — la sienne,
    une adresse partagée, la saisie que le navigateur a gardée — la faisait
    passer pour l'exemple."""
    vierge = _formulaire(Saisie.depuis_requete({}), contexte)
    saisie = _formulaire(Saisie.depuis_requete(BASE), contexte)
    assert "L'exemple est déjà rempli" in vierge
    assert "L'exemple est déjà rempli" not in saisie
    assert "Modifiez ce qu'il faut, puis recalculez." in saisie
    for html in (vierge, saisie):
        assert 'class="consigne"' in html


def test_le_simulateur_court_deplace_ses_bornes_avec_la_naissance(contexte):
    """Ses dates portent leurs âges limites, comme celles du formulaire entier :
    sans eux, le script de la page ne déplaçait pas les bornes du calendrier, et
    elles restaient celles d'un assuré né en 1975 — un départ à 64 ans devenait
    impossible à envoyer pour qui était né en 1990."""
    court = _simulateur_court(contexte)
    for nom, (mini, maxi) in {
        "debut": (AGE_DEBUT_MINIMAL, AGE_DEBUT_MAXIMAL),
        "liquidation": (AGE_LIQUIDATION_MINIMAL, AGE_LIQUIDATION_MAXIMAL),
    }.items():
        champ = re.search(rf'<input type="date" id="{nom}"[^>]*>', court).group(0)
        assert f'data-age-min="{mini}"' in champ and f'data-age-max="{maxi}"' in champ


# -- la mémoire, dans le script de la page -------------------------------------


def _script() -> str:
    page = (RACINE / "index.html").read_text(encoding="utf-8")
    return re.search(r'<script type="module">(.*?)</script>', page, re.S).group(1)


def _fonction(script: str, nom: str) -> str:
    debut = script.index(f"function {nom}(")
    return script[debut:script.index("\n}\n", debut)]


def test_la_saisie_n_est_gardee_que_par_le_navigateur(contexte):
    """Le stockage local, et lui seul, garde la saisie : il ne sort pas de la
    machine. Trois fonctions y touchent, et chacune sous ``try`` — un
    navigateur qui le refuse, en navigation privée, doit laisser le simulateur
    marcher comme avant. Le simulateur le dit, et un bouton l'efface."""
    script = _script()
    touches = {nom: _fonction(script, nom)
               for nom in ("lireMemoire", "ecrireMemoire", "oublierMemoire")}
    assert sum(corps.count("window.localStorage") for corps in touches.values()) \
        == len(re.findall(r"\blocalStorage\.", script)), \
        "le stockage est lu hors des trois fonctions"
    for nom, corps in touches.items():
        assert "try {" in corps and "catch" in corps, f"{nom} n'est pas protégée"
    for autre in ("sessionStorage", "indexedDB", "document.cookie"):
        assert autre not in script

    _, corps = rendre(contexte, "/simuler", {})
    assert "Tout se calcule et se garde dans votre navigateur : rien n'en sort." \
        in corps
    assert '<button type="button" class="second oublier" hidden>Effacer ma saisie</button>' \
        in corps
    assert 'closest?.("button.oublier")' in script and "oublierMemoire();" in script
