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

import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import pytest

from retraite_notionnelle.web.site import disponible, module, rendre, site
from outils_pont import saisie_du_portage

#: Le formulaire est du texte du site : il se lit dans le portage, par node,
#: comme la saisie qu'il renvoie (action 161, étape 6).
pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : le site ne se lit pas sans lui")
pages = module("pages")


def _formulaire(requete: dict) -> str:
    """Le formulaire que le site rend pour cette saisie, lue par sa saisie à lui."""
    return pages.formulaire(module("saisie").Saisie.depuis_requete(requete), site().contexte)

RACINE = Path(__file__).resolve().parents[1]


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
        "naissances": "1996,1999-04",
        "interruptions": "1995:1996:education_enfant", "temps_partiel": "1999:1999:80",
        "dispenses": "2016:2017:rsa", "lodeom": "competitivite",
        "releve": "1998:salarie_prive_non_cadre:14200:4\n"
                  "1999:salarie_prive_non_cadre:15100:4",
    },
    # Le conjoint collaborateur à l'option (action 138, étape 18) : son menu ne
    # paraît qu'avec une période de conjoint collaborateur.
    "une collaboratrice, à l'option": {
        **BASE, "metier2_debut": "2008-01-01",
        "metier2_statut": "conjoint_collaborateur_artisan", "metier2_salaire": "3000",
        "collaborateur": "moitie",
    },
    # La réversion des non-salariés agricoles (action 138, étape 8) : ses deux
    # champs ne paraissent qu'avec une période agricole ; nulle, elle reste dite.
    "une veuve d'exploitant, à la réversion nulle": {
        **BASE, "statut": "exploitant_agricole", "reversion_agricole": "2010-03",
        "reversion_agricole_mensuel": "0",
    },
    "des règles, dont celles qui n'ont pas de champ": {
        **BASE, "indexation": "prix", "table": "par_sexe", "lissage": "3",
        "reprise": "40", "bascule": "2030", "euros": "2025",
        "age_reference": "cliquet_legal", "conversion_acquis": "liquidation",
    },
}


@pytest.mark.parametrize("nom", list(SAISIES))
def test_le_formulaire_renvoie_tout_ce_qu_il_a_recu(nom):
    """Rendre une saisie dans le formulaire, puis le soumettre tel quel, rend la
    même saisie. Un champ que le formulaire ne porte pas — la situation, la
    saisie par la pension, l'âge de référence — se perdait au premier
    « Calculer », et rien ne le disait : la page revenait, calculée sur autre
    chose."""
    saisie = saisie_du_portage(SAISIES[nom])
    renvoyee = saisie_du_portage(_soumettre(_formulaire(SAISIES[nom])))
    assert renvoyee.requete() == saisie.requete()


def test_une_saisie_refusee_se_remontre_telle_qu_elle_a_ete_envoyee():
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
    _, corps = rendre("/simuler", envoyee)
    assert "Saisie refusée" in corps and "Métier n° 3" in corps
    assert 'id="resultats"' not in corps
    soumise = _soumettre(corps)
    assert {cle: soumise.get(cle) for cle in envoyee} == envoyee

    # Un retraité refusé garde sa pension : le formulaire reste le sien.
    retraite = {**SAISIES["un retraité, par sa pension"],
                "liquidation": "1970-01-01"}
    _, corps = rendre("/simuler", retraite)
    assert "Saisie refusée" in corps
    soumise = _soumettre(corps)
    assert {cle: soumise.get(cle) for cle in retraite} == retraite


def test_une_ligne_incomplete_laisse_les_autres_en_place():
    """Une ligne de métier à moitié remplie ne se lit pas : la lecture s'y
    arrête, les lignes d'avant restent, et c'est la ligne vide qui suit qui
    la recevra — le script de la page y remet ce qui a été envoyé."""
    envoyee = {
        **BASE, "metier2_debut": "2000-01-01", "metier2_statut": "salarie_prive_cadre",
        "metier2_salaire": "3900", "metier3_debut": "2008-01-01",
    }
    _, corps = rendre("/simuler", envoyee)
    assert "Saisie refusée" in corps and "Métier n° 3" in corps
    soumise = _soumettre(corps)
    assert {cle: soumise[cle] for cle in envoyee if cle != "metier3_debut"} == {
        cle: valeur for cle, valeur in envoyee.items() if cle != "metier3_debut"}
    # La ligne vide qui suit est bien la troisième.
    assert 'name="metier3_debut"' in corps and 'name="metier4_debut"' not in corps


def test_une_periode_se_retire_et_les_suivantes_remontent():
    """On pouvait ajouter une période, pas en retirer : il fallait vider ses
    champs un à un (le propriétaire, le 20 octobre 2026). Chaque période après
    la première porte donc « Retirer cette période » ; le formulaire revient
    sans elle, et celles qui la suivaient remontent d'un rang. La première,
    qui porte la carrière, ne se retire pas, et la ligne vide n'est pas encore
    une période."""
    trois = SAISIES["trois périodes, dont une sans emploi"]
    html = _formulaire(trois)
    bouton = r'<button type="button" class="second retirer" data-rang="(\d+)">' \
        r"Retirer cette période</button>"
    assert re.findall(bouton, html) == ["2", "3"]

    soumise = _soumettre(html)

    def metiers(requete):
        return {cle: valeur for cle, valeur in requete.items() if cle.startswith("metier")}

    def reste(requete):
        return {cle: valeur for cle, valeur in requete.items()
                if not cle.startswith("metier")}

    sans_la_deuxieme = pages.requete_sans_periode(soumise, 2)
    assert metiers(sans_la_deuxieme) == {
        "metier2_debut": trois["metier3_debut"], "metier2_statut": trois["metier3_statut"],
        "metier2_salaire": trois["metier3_salaire"]}
    assert reste(sans_la_deuxieme) == reste(soumise)
    sans_la_troisieme = pages.requete_sans_periode(soumise, 3)
    assert sans_la_troisieme == {cle: valeur for cle, valeur in soumise.items()
                                 if not cle.startswith("metier3_")}
    assert pages.requete_sans_periode(soumise, 1) == soumise

    # Rendue, la carrière n'a plus que deux périodes, et la ligne vide suit.
    apres = _formulaire(sans_la_deuxieme)
    assert re.findall(bouton, apres) == ["2"]
    assert 'name="metier3_debut"' in apres and 'name="metier4_debut"' not in apres
    assert [metier.statut for metier in saisie_du_portage(sans_la_deuxieme).metiers] \
        == [trois["metier3_statut"]]

    # Le script de la page la branche : au clic, les champs du formulaire,
    # moins la période.
    script = _script()
    assert 'closest?.("button.retirer")' in script and "requeteSansPeriode(" in script


def test_une_adresse_forgee_retombe_sur_l_exemple_sans_perdre_sa_forme():
    """Ce qui ne se lit pas du tout repart de l'exemple, mais garde ce qui décide
    de la forme du formulaire : un retraité y retrouve le champ de sa pension,
    et non celui d'un revenu."""
    _, corps = rendre("/simuler", {
        "situation": "retraite", "montants": "brut", "naissance": "hier",
    })
    assert "Saisie refusée" in corps
    soumise = _soumettre(corps)
    assert soumise["situation"] == "retraite" and soumise["saisie_par"] == "pension"
    assert soumise["montants"] == "brut" and "pension" in soumise
    assert "salaire" not in soumise


def test_la_consigne_ne_parle_de_l_exemple_que_devant_l_exemple():
    """« L'exemple est déjà rempli » au-dessus d'une carrière saisie — la sienne,
    une adresse partagée, la saisie que le navigateur a gardée — la faisait
    passer pour l'exemple."""
    vierge = _formulaire({})
    saisie = _formulaire(BASE)
    assert "L'exemple est déjà rempli" in vierge
    assert "L'exemple est déjà rempli" not in saisie
    assert "Modifiez ce qu'il faut, puis recalculez." in saisie
    for html in (vierge, saisie):
        assert 'class="consigne"' in html


def test_l_exemple_est_un_jeune_actif():
    """L'exemple que le simulateur ouvre déjà rempli est un jeune actif, né en
    2000, que la réforme prendrait au début de sa carrière : c'est à lui que le
    site s'adresse d'abord (le propriétaire, le 20 octobre 2026). Il était né
    en 1975. La saisie du portage le porte, et le formulaire vierge le montre :
    premier emploi à 21 ans, en janvier 2021, départ à 64 ans, en janvier
    2064."""
    assert module("saisie").DEFAUTS["naissance"] == 2000
    vierge = _formulaire({})
    for nom, valeur in (("naissance", "2000-01-01"), ("debut", "2021-01-01"),
                        ("liquidation", "2064-01-01")):
        assert re.search(rf'id="{nom}" name="{nom}" value="{valeur}"', vierge), nom


def test_le_simulateur_court_deplace_ses_bornes_avec_la_naissance():
    """Ses dates portent leurs âges limites, comme celles du formulaire entier :
    sans eux, le script de la page ne déplaçait pas les bornes du calendrier, et
    elles restaient celles d'un assuré né en 1975 — un départ à 64 ans devenait
    impossible à envoyer pour qui était né en 1990."""
    court = pages.simulateur_court(site().contexte)
    saisie = module("saisie")
    for nom, (mini, maxi) in {
        "debut": (saisie.AGE_DEBUT_MINIMAL, saisie.AGE_DEBUT_MAXIMAL),
        "liquidation": (saisie.AGE_LIQUIDATION_MINIMAL, saisie.AGE_LIQUIDATION_MAXIMAL),
    }.items():
        champ = re.search(rf'<input type="date" id="{nom}"[^>]*>', court).group(0)
        assert f'data-age-min="{mini}"' in champ and f'data-age-max="{maxi}"' in champ


# -- la mémoire, dans le script de la page -------------------------------------


def _script() -> str:
    """Le routeur de la page, ``moteur/js/routeur.js`` : le script qu'``index.html``
    portait en ligne jusqu'à l'action 174."""
    return (RACINE / "moteur" / "js" / "routeur.js").read_text(encoding="utf-8")


def _fonction(script: str, nom: str) -> str:
    debut = script.index(f"function {nom}(")
    return script[debut:script.index("\n}\n", debut)]


def test_la_saisie_n_est_gardee_que_par_le_navigateur():
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

    _, corps = rendre("/simuler", {})
    assert "Tout se calcule et se garde dans votre navigateur : rien n'en sort." \
        in corps
    assert '<button type="button" class="second oublier" hidden>Réinitialiser</button>' \
        in corps
    assert 'closest?.("button.oublier")' in script and "oublierMemoire();" in script


def test_le_formulaire_se_reinitialise_d_un_bouton_qui_se_voit():
    """« Réinitialiser » ramène le formulaire à l'exemple, et se voit dès qu'il y
    a quelque chose à réinitialiser. Il s'appelait « Effacer ma saisie », et ne
    paraissait que lorsque le navigateur avait retenu une saisie : devant une
    adresse partagée, ou dans un navigateur qui ne retient rien — une
    navigation privée, un cadre d'une autre origine —, le formulaire ne
    laissait que changer les données, et rien ne disait comment repartir de
    zéro (le propriétaire, le 20 octobre 2026)."""
    bouton = re.compile(
        r'<button type="button" class="second oublier"( hidden)?>Réinitialiser</button>')
    vierge = bouton.search(_formulaire({}))
    assert vierge and vierge.group(1), "devant l'exemple, il n'y a rien à réinitialiser"
    saisie = bouton.search(_formulaire(BASE))
    assert saisie and not saisie.group(1), \
        "devant une carrière saisie, le bouton reste caché"
    # Le script de la page ne le cache plus faute de mémoire : il le montre
    # aussi dès que le formulaire diffère de ce que le rendu a écrit, que le
    # navigateur retienne la frappe ou non.
    corps = _fonction(_script(), "montrerLaMemoire")
    assert "bouton.hidden &&" in corps and "formulaire._rendue" in corps


def test_le_champ_des_dispenses_nomme_chaque_motif_et_ses_annees():
    """Le champ des dispenses de l'assiette minimale (action 138, étape 18) dit,
    sous son point d'interrogation, chaque motif de la table et les années où
    il dispense, lues dans le paquet : un motif de plus ne s'y perd pas, et une
    année corrigée dans la table l'est aussi sur la page."""
    html = _formulaire({"dispenses": "2016:2017:rsa"})
    bloc = re.search(r'<div><label for="dispenses">.*?</div>', html, re.S)
    assert bloc, "le formulaire n'a pas de champ des dispenses"
    assert 'name="dispenses" value="2016:2017:rsa"' in bloc.group(0)
    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    for motif, (_, debut, fin, _) in paquet["dispenses_assiette_minimale"].items():
        annees = f"de {debut} à {fin}" if fin is not None else f"depuis {debut}"
        assert re.search(f"« {motif} »[^;.]*{annees}", bloc.group(0)), (motif, annees)


def test_le_menu_de_la_lodeom_offre_chaque_bareme_du_paquet():
    """Le menu de la Lodeom (action 138, étape 18) offre « non », puis chaque
    barème du bloc ``lodeom`` du paquet, sous son libellé, et garde celui qu'on
    a choisi. Replié dans les options, il ne coûte rien au formulaire vierge."""
    formulaire = _formulaire({"lodeom": "competitivite_renforcee"})
    bloc = re.search(r'<div><label for="lodeom">.*?</select></div>', formulaire, re.S)
    assert bloc, "le formulaire n'a pas de menu de la Lodeom"
    options = re.findall(r'<option value="([^"]*)"( selected)?>([^<]*)</option>', bloc.group(0))
    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    baremes = paquet["prelevements_remuneration"]["profils"]["salarie_prive"]["lodeom"]["baremes"]
    assert [(code, unescape(texte)) for code, _, texte in options] == [("", "non")] + [
        (code, bareme["libelle"]) for code, bareme in baremes.items()]
    assert [code for code, choisi, _ in options if choisi] == ["competitivite_renforcee"]


def test_le_menu_du_conjoint_collaborateur_ne_parait_qu_avec_lui():
    """Le menu de l'option du conjoint collaborateur (action 138, étape 18)
    offre le forfait, puis 33,33 % et 50 % du revenu du chef, et ne paraît
    qu'avec une période de conjoint collaborateur, ou une option déjà dite ; le
    revenu de cette période se dit alors celui du chef d'entreprise, et sans
    effet au forfait."""
    assert 'name="collaborateur"' not in _formulaire(BASE)
    periode = {**BASE, "metier2_debut": "2008-01-01",
               "metier2_statut": "conjoint_collaborateur_commercant",
               "metier2_salaire": "3000"}
    formulaire = _formulaire(periode)
    bloc = re.search(r'<div><label for="collaborateur">.*?</select></div>', formulaire, re.S)
    assert bloc, "le formulaire n'a pas de menu du conjoint collaborateur"
    options = re.findall(r'<option value="([^"]*)"( selected)?>([^<]*)</option>', bloc.group(0))
    assert [(code, unescape(texte)) for code, _, texte in options] == [
        ("", "le forfait, le tiers du plafond"),
        ("tiers", "33,33 % du revenu du chef d'entreprise"),
        ("moitie", "50 % du revenu du chef d'entreprise")]
    assert [code for code, choisi, _ in options if choisi] == [""]
    revenu = re.search(r'<label for="metier2_salaire">(.*?)</label>', formulaire, re.S)
    assert revenu and "chef d" in unescape(revenu.group(1)), revenu
    assert "sans effet au forfait" in unescape(revenu.group(1))
    a_l_option = unescape(re.search(r'<label for="metier2_salaire">(.*?)</label>',
                                    _formulaire({**periode, "collaborateur": "tiers"}),
                                    re.S).group(1))
    assert "33,33" in a_l_option and "sans effet" not in a_l_option
    assert 'name="collaborateur"' in _formulaire({**BASE, "collaborateur": "tiers"})


def test_la_reversion_agricole_ne_parait_qu_avec_une_periode_agricole():
    """Les deux champs de la réversion des non-salariés agricoles (action 138,
    étape 8) — le mois où elle commence, son montant brut de ce mois, borné à
    zéro — ne paraissent qu'avec une période de chef ou de collaborateur
    agricole, aux métiers ou au relevé, ou une réversion déjà dite ; leur bulle
    annonce la présomption qui tient sans eux (``pas_de_reversion_agricole``)."""
    assert 'name="reversion_agricole' not in _formulaire(BASE)
    for requete in ({**BASE, "statut": "exploitant_agricole"},
                    {**BASE, "metier2_debut": "2008-01-01",
                     "metier2_statut": "collaborateur_agricole", "metier2_salaire": "1500"},
                    {**BASE, "releve": "1998:salarie_prive_non_cadre:14200:4\n"
                                       "1999 : exploitant_agricole : 9000"},
                    {**BASE, "reversion_agricole": "2010-03",
                     "reversion_agricole_mensuel": "0"}):
        formulaire = _formulaire(requete)
        assert 'name="reversion_agricole"' in formulaire, requete
        assert re.search(r'<input type="number" id="reversion_agricole_mensuel" '
                         r'name="reversion_agricole_mensuel" value="[^"]*" min="0"',
                         formulaire), requete
    dite = _formulaire({**BASE, "statut": "exploitant_agricole",
                        "reversion_agricole": "2010-03", "reversion_agricole_mensuel": "0"})
    assert 'id="reversion_agricole" name="reversion_agricole" value="2010-03"' in dite
    assert 'name="reversion_agricole_mensuel" value="0"' in dite
    libelle = re.search(r'<label for="reversion_agricole">(.*?)</label>', dite, re.S)
    assert libelle, "le champ de la réversion n'a pas de libellé"
    bulle = unescape(re.sub(r"<[^>]+>", "", libelle.group(1)))
    for phrase in ("L. 732-41", "D. 732-110", "Sans réversion déclarée",
                   "de 1999 à 2008", "6,55957"):
        assert phrase in bulle, phrase
