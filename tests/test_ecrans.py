"""Le site sur tous les écrans : rien ne déborde, et ce qui va ensemble se voit ensemble.

Les témoins de pages figent ce que le site ÉCRIT ; ce qu'un écran en MONTRE
leur échappe. Le 23 octobre 2026, à 390 points de large, la page Coût
débordait de 140 points — la page entière glissait de gauche à droite —, et
quarante de ses cadres défilaient en largeur : chaque graphique, réduit d'un
tiers puis élargi à 30 rem pour rester lisible, chaque schéma, chaque tableau
de plus de trois colonnes. Les quatre montants du simulateur s'étageaient sur
1 400 pixels, près de deux écrans de téléphone : on ne pouvait pas les
comparer sans faire défiler. Le propriétaire l'a demandé en ces termes : que
tout tienne sur l'écran, sans que rien ne soit caché sur la largeur, et que
ce qui se lit ensemble — un graphique et sa légende, les scénarios du
simulateur — se voie en même temps.

Ces tests le vérifient dans un vrai moteur de rendu, Chromium sans fenêtre,
que pilote ``tests/js/ecrans.mjs`` : chaque page, à chaque largeur, dépliants
fermés puis ouverts. Sans Chromium sur la machine, ils sont passés ; GitHub
en a un. ``NAVIGATEUR`` désigne celui qu'on veut.
"""

from __future__ import annotations

import functools
import http.server
import json
import os
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
PILOTE = RACINE / "tests" / "js" / "ecrans.mjs"

#: Les largeurs visitées, en points CSS, et la hauteur de l'écran qui va avec :
#: le plus petit téléphone encore vendu, le téléphone courant, la tablette en
#: hauteur puis en largeur, et le bureau.
ECRANS = [(320, 640), (390, 800), (768, 1024), (1024, 768), (1440, 900)]

#: Une carrière entière, telle que le simulateur la met dans l'adresse quand
#: on calcule le formulaire tel qu'il s'ouvre.
REQUETE = (
    "unite_revenu=euros_mois&montants=brut&situation=actif"
    "&saisie_par=revenu&naissance=2000-01-01&liquidation=2064-01-01"
    "&debut=2021-01-01&statut=salarie_prive_non_cadre&salaire=3500"
    "&emploi_retraite_employeur=autre&sexe=H&profil=auto&primes=0&enfants=0"
    "&indexation=masse_salariale&lissage=1&table=unisexe&population=niveau_de_vie"
    "&rattachement=salaire&part_cotisation=salariale&contribution_etat=retraite_seule"
    "&foyer=seul&projection=cor_reference&esperance_vie=centrale&emploi=cor_2026"
    "&stock=prix&frais=paliers&taux=forwards&bascule=2026&euros=2026"
)

#: La page des résultats : le simulateur, la carrière derrière le `#`.
RESULTATS = f"simuler/#{REQUETE}"

#: Les dix routes, des adresses relatives à la racine du site : l'accueil, puis
#: chaque page dans son dossier (action 174), les résultats entre le
#: formulaire vierge et la page Coût.
ROUTES = ["./", "simuler/", RESULTATS, "cout/", "risque/", "partager/",
          "saviez-vous/", "cas-types/", "avantages/", "methode/"]

#: La fenêtre qu'on rétrécit sans changer de page, au large, sur une page qui
#: pose des schémas de front, d'un écran à l'autre : du bureau à la tablette en
#: largeur, où la demi-colonne passe de 532 à 432 points, sans que la page
#: toute faite, dessinée à 480, ait à changer ; puis à un écran de 900 points,
#: où elle tombe à 370 et où le dessin ne tient plus.
RETRECIR = {"depuis": 1440, "vers": [{"largeur": 1024, "hauteur": 768},
                                      {"largeur": 900, "hauteur": 700}]}

#: Les écrans où chaque route s'ouvre à neuf, comme Lighthouse l'ouvre en
#: mobile puis en bureau, pour mesurer ce qu'elle décale en se chargeant.
CHARGEMENTS = [(390, 800), (1440, 900)]


def navigateur() -> str | None:
    """Un Chromium ou un Chrome : celui que désigne ``NAVIGATEUR``, celui des
    sessions Claude Code (``PLAYWRIGHT_BROWSERS_PATH``), ou le premier du
    système."""
    if os.environ.get("NAVIGATEUR"):
        return os.environ["NAVIGATEUR"]
    for dossier in (os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), "/opt/pw-browsers"):
        if dossier and Path(dossier).is_dir():
            # `chrome-linux`, ou `chrome-linux64` pour les Chromium récents de
            # Playwright : sans ce dernier, le test passait sans rien jouer.
            trouves = sorted(Path(dossier).glob("chromium-*/chrome-linux*/chrome"))
            if trouves:
                return str(trouves[-1])
    for nom in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
                "chrome"):
        if shutil.which(nom):
            return shutil.which(nom)
    for chemin in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if Path(chemin).exists():
            return chemin
    return None


class _Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def mesures() -> tuple:
    """Ce que le navigateur a mesuré : chaque route à chaque largeur,
    dépliants fermés puis ouverts."""
    return tuple(_pilote()["visites"])


def chargements() -> tuple:
    """Chaque route ouverte à neuf, à chaque écran de ``CHARGEMENTS`` : les
    décalages de mise en page notés jusqu'à la fin du rendu, et leur CLS."""
    return tuple(_pilote()["chargements"])


def jouer(plan_du_pilote: dict) -> dict:
    """Le pilote du navigateur, joué sur le dépôt servi tel quel : ``plan_du_pilote``
    dit ce qu'il visite (``tests/js/ecrans.mjs``), le serveur et l'adresse de la
    racine sont ajoutés ici."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pilote du navigateur ne tourne pas sans lui")
    chemin = navigateur()
    if chemin is None:
        pytest.skip("aucun Chromium sur cette machine : NAVIGATEUR en désigne un")
    serveur = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(_Silencieux, directory=str(RACINE)))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    # Un plan par processus : la suite se répartit sur plusieurs, et chacun a
    # son serveur, sur son port.
    plan = RACINE / ".cache" / f"ecrans-{os.getpid()}.json"
    racine = f"http://127.0.0.1:{serveur.server_address[1]}/"
    try:
        plan.parent.mkdir(exist_ok=True)
        plan.write_text(json.dumps({
            "racine": racine, **plan_du_pilote,
        }), encoding="utf-8")
        execution = subprocess.run(
            ["node", str(PILOTE), chemin, str(plan)], cwd=RACINE,
            capture_output=True, text=True, encoding="utf-8", timeout=900, check=False)
    finally:
        serveur.shutdown()
        plan.unlink(missing_ok=True)
    assert execution.returncode == 0, execution.stderr[-3000:]
    return json.loads(execution.stdout)


@functools.lru_cache(maxsize=None)
def _pilote() -> dict:
    """Le pilote du navigateur sur les écrans, joué une fois par processus."""
    return jouer({
        "ecrans": [{"largeur": l, "hauteur": h} for l, h in ECRANS],
        "routes": ROUTES,
        "retrecir": RETRECIR,
        "chargements": [{"largeur": l, "hauteur": h} for l, h in CHARGEMENTS],
    })


def _ou(visite: dict, etat: str) -> str:
    return f"{visite['route'][:40]} à {visite['largeur']} points, dépliants {etat}"


def test_aucune_page_ne_deborde_en_largeur():
    """Ni la page, ni aucun de ses cadres : rien ne se lit en glissant de
    gauche à droite, et rien ne sort de l'écran, à aucune largeur.

    Un tableau trop large ne défile plus dans sa boîte : il se recompose, une
    ligne par fiche ; un graphique se redessine à la largeur du téléphone au
    lieu d'être réduit puis élargi ; une carte à publier se lit à la taille de
    l'écran.
    """
    fautes = []
    for visite in mesures():
        for etat in ("replie", "deplie"):
            mesure = visite[etat]
            lieu = _ou(visite, "fermés" if etat == "replie" else "ouverts")
            if mesure["deborde"]:
                fautes.append(f"{lieu} : la page fait {mesure['deborde']} points de large")
            for cadre in mesure["defilants"]:
                fautes.append(f"{lieu} : défile en largeur — {cadre}")
            for element in mesure["sortants"]:
                fautes.append(f"{lieu} : sort de l'écran — {element}")
    assert not fautes, f"{len(fautes)} débordements :\n" + "\n".join(fautes[:80])


def test_aucune_case_de_tableau_ne_deborde_sur_sa_voisine():
    """Une valeur qui ne se coupe pas tient dans sa case, à toute largeur.

    Le 24 octobre 2026, à 390 points, le tableau de la page Pourquoi changer
    qui dit ce que le système verse et encaisse se repliait en rangée, ses
    trois valeurs côte à côte : « 14,1 % · 422 Md € » ne tenait pas dans sa
    colonne et passait sur la suivante, qu'on lisait « 422 Md€13,9 % ». La
    page n'en était pas plus large, ni le tableau : rien ne le voyait (action
    173, étape 6).
    """
    fautes = [f"{_ou(visite, 'fermés' if etat == 'replie' else 'ouverts')} : {case}"
              for visite in mesures() for etat in ("replie", "deplie")
              for case in visite[etat]["chevauchees"]]
    assert not fautes, f"{len(fautes)} cases débordent :\n" + "\n".join(fautes[:60])


#: Le CLS admis au chargement : 100 au Lighthouse en demande 0,04 au plus, et
#: rien ne doit bouger.
CLS_MAXIMAL = 0.01


def test_aucune_page_ne_se_decale_en_se_chargeant():
    """Ouverte à neuf, une page ne bouge pas sous les yeux de qui la lit.

    Le 25 octobre 2026, Lighthouse comptait à presque toutes un CLS proche de
    1, le quart de la note de Performance (action 174) : l'en-tête, posé vide
    sous l'écran d'attente, se remplissait avec la page et poussait tout
    ``<main>`` ; le pied, posé sous l'attente, plongeait de plusieurs écrans ;
    le serif du chapeau, demandé au rendu seulement, arrivait après coup et
    lui ôtait une ligne. Chaque route s'ouvre ici à neuf, en mobile puis en
    bureau, comme Lighthouse l'ouvre.
    """
    fautes = [f"{c['route'][:40]} à {c['largeur']} points : CLS {c['cls']:.3f} — "
              + " ; ".join(f"{d['valeur']:.3f} à {d['instant']} ms : {', '.join(d['sources'])}"
                           for d in c["decalages"])
              for c in chargements() if c["cls"] > CLS_MAXIMAL]
    assert not fautes, f"{len(fautes)} chargements décalent :\n" + "\n".join(fautes)


def test_tout_texte_se_detache_de_son_fond():
    """Un texte se lit sur son fond : 4,5 pour 1 au moins entre leurs
    luminances, 3 pour 1 en grand — 24 px, ou 18,66 px en gras. WCAG 1.4.3, et
    la règle ``color-contrast`` d'axe, que joue Lighthouse (action 174) : le
    25 octobre 2026, le manque en euros des cartes de résultats, écrit en
    ``--manque`` sur le fond des cartes, n'y faisait que 3,75. La couleur du
    texte se fond sur le premier fond opaque de ses ancêtres ; sur une image
    ou un dégradé, elle ne se calcule pas, et le texte est laissé de côté,
    comme axe le laisse.
    """
    fautes = [f"{_ou(visite, 'fermés' if etat == 'replie' else 'ouverts')} : {texte}"
              for visite in mesures() for etat in ("replie", "deplie")
              for texte in visite[etat]["contrastes"]]
    assert not fautes, f"{len(fautes)} textes trop pâles :\n" + "\n".join(fautes[:60])


#: Le plus grand vide admis entre deux blocs qui se suivent : quarante points
#: sur un téléphone, où chaque ligne de blanc repousse la suivante hors de
#: l'écran, cinquante-six au large.
VIDE_MAXIMAL = {320: 40, 390: 40, 768: 56, 1024: 56, 1440: 56}


def test_aucune_page_ne_laisse_de_grand_vide():
    """Un blanc sépare deux blocs ; au-delà, il ne sépare plus, il éloigne.

    Le 23 octobre 2026, le propriétaire trouvait « beaucoup d'espaces sans
    justification » : soixante-quatre points entre le formulaire de l'accueil
    et les engagements, quarante-huit au-dessus de chaque titre de section sur
    un téléphone, une ligne vide réservée sous chaque graphique à une aide au
    clavier invisible. Le plus grand vide de chaque page est tenu.
    """
    fautes = []
    for visite in mesures():
        seuil = VIDE_MAXIMAL[visite["largeur"]]
        for vide in visite["replie"]["vides"]:
            if vide["vide"] > seuil:
                fautes.append(f"{_ou(visite, 'fermés')} : {vide['vide']} points entre "
                              f"{vide['entre']}")
    assert not fautes, f"{len(fautes)} vides :\n" + "\n".join(fautes[:60])


def test_aucune_page_ne_leve_d_erreur_a_aucune_largeur():
    """Redessiner un graphique à la largeur de l'écran passe par le script :
    une exception y laisserait la page à moitié rendue."""
    fautes = [f"{_ou(visite, 'fermés')} : {erreur}"
              for visite in mesures() for erreur in visite["erreurs"]]
    assert not fautes, "\n".join(fautes)


#: Les alertes de l'onglet « Issues » qu'on garde, chacune pour sa raison.
#: `bday` est la valeur que la norme HTML et le critère 1.3.5 des WCAG (RGAA
#: 11.13) donnent à une date de naissance entière
#: (`test_les_champs_qui_decrivent_la_personne_sont_reconnaissables`) ;
#: l'autoremplissage de Chrome ne connaît que `bday-day`, `bday-month` et
#: `bday-year`, et dit « non standard » toute autre valeur où se lit « bday ».
ALERTES_ADMISES = {
    'FormInputHasWrongButWellIntendedAutocompleteValueError input#naissance[autocomplete="bday"]',
}


def test_aucune_page_ne_porte_d_alerte_dans_l_onglet_issues():
    """Ce que l'onglet « Issues » des outils de développement de Chrome
    signale — un champ sans `id` ni `name`, une valeur d'`autocomplete` qu'il
    ne connaît pas — se voit de qui ouvre la console : chaque alerte se
    corrige, ou se déclare dans `ALERTES_ADMISES` avec sa raison."""
    fautes = sorted({f"{visite['route'][:40]} : {alerte}"
                     for visite in mesures() for alerte in visite["alertes"]
                     if alerte not in ALERTES_ADMISES})
    assert not fautes, f"{len(fautes)} alertes :\n" + "\n".join(fautes)


def test_un_trace_et_sa_legende_se_voient_ensemble():
    """La légende touche son tracé, au-dessus ou à côté, et les deux tiennent
    dans un seul écran : la lecture au survol écrit ses valeurs dans la
    légende, qu'il faut donc voir en même temps que la courbe qu'on touche."""
    fautes = []
    for visite in mesures():
        for trace in visite["deplie"]["traces"]:
            lieu = f"{_ou(visite, 'ouverts')}, « {trace['nom'][:60]} »"
            if trace["ecart"] > 24:
                fautes.append(f"{lieu} : {trace['ecart']} points entre le tracé et sa légende")
            if trace["etendue"] > trace["place"]:
                fautes.append(f"{lieu} : tracé et légende font {trace['etendue']} points, "
                              f"l'écran en montre {trace['place']}")
    assert not fautes, f"{len(fautes)} tracés loin de leur légende :\n" + "\n".join(fautes[:60])


#: Les pages dont les rangées repliées gardent côte à côte leurs valeurs
#: courtes. Chaque page des étapes 4 à 10 de l'action 173 s'y ajoute quand on
#: la reprend : le 23 octobre 2026, à 320 points, Droits non cotisés et les
#: résultats du simulateur empilaient encore, en fiche, deux valeurs courtes
#: que la colonne minimale de 8,5 rem ne laisse pas tenir ensemble. Simuler,
#: le formulaire et ses résultats, à l'étape 4 ; Coût, à l'étape 5 ;
#: Pourquoi changer, à l'étape 6 ; Partager et Le saviez-vous ?, à l'étape 7 ;
#: Carrières types, à l'étape 8, où une rangée en porte sept ; Droits non
#: cotisés, à l'étape 9 ; Méthode et sources, à l'étape 10 : toutes les pages
#: du site.
COTE_A_COTE = ROUTES


def test_deux_valeurs_courtes_d_une_rangee_repliee_se_lisent_cote_a_cote():
    """Un tableau replié garde côte à côte les valeurs courtes d'une rangée,
    qu'on lit ensemble — aujourd'hui, avec notre programme ; les sept
    générations d'une carrière type — : deux par ligne au moins, jamais une.

    Le pli comptait dans leur longueur le texte des bulles du glossaire, qu'on
    ne voit pas tant qu'on ne les ouvre pas : sur l'accueil, à 390 points, une
    case qui portait « trimestres » ou « décote » passait pour une phrase,
    prenait la ligne entière et rejetait sa voisine dessous — trois rangées sur
    dix, quand les sept autres restaient côte à côte (action 173, étape 3).
    La règle ne comptait que les rangées de deux valeurs ; à 320 points, une
    fiche de trois et plus les mettait une par ligne, la colonne de 8,5 rem
    n'en laissant pas tenir deux : chaque carrière de Carrières types sur sept
    lignes, la grille sur 5 199 pixels (action 173, étape 8).
    """
    fautes = [f"{_ou(visite, 'fermés' if etat == 'replie' else 'ouverts')} : {rangee}"
              for visite in mesures() if visite["route"] in COTE_A_COTE
              for etat in ("replie", "deplie")
              for rangee in visite[etat]["empilees"]]
    assert not fautes, f"{len(fautes)} rangées empilées :\n" + "\n".join(fautes[:60])


def test_une_grille_repliee_garde_ses_colonnes():
    """Une grille se lit en colonnes : la génération 1940 d'une carrière type
    sous celle de la carrière d'avant, sous l'en-tête qui la nomme.

    Une grille, c'est plus de trois colonnes de nombres courts sous des
    en-têtes courts : les écarts de Carrières types, une génération par
    colonne. Repliée, elle met sur une ligne autant de valeurs d'une rangée que
    la largeur en tient. À 390 points, elle passait en fiche, deux valeurs par
    ligne : sept générations sur quatre lignes, chaque carrière sur 247 pixels
    et la grille sur 3 210, quand ses sept valeurs tiennent sur une ligne de
    351 (action 173, étape 8).
    """
    fautes = [f"{_ou(visite, 'fermés' if etat == 'replie' else 'ouverts')} : {rangee}"
              for visite in mesures() for etat in ("replie", "deplie")
              for rangee in visite[etat]["grilles"]]
    assert not fautes, f"{len(fautes)} rangées de grille éparpillées :\n" + "\n".join(fautes[:60])


#: Dès cette largeur, les schémas de Sankey qu'une carte compare vont de front.
#: À 1 440 points, ceux de la carte « Qui paie quoi », le système actuel et la
#: proposition, s'empilaient sur 1 340 pixels, pour un écran de 900 : on ne
#: voyait jamais le second avec le premier (action 173, étape 5).
DEUX_SCHEMAS_DE_FRONT = 1024


def test_les_schemas_qu_une_carte_compare_se_voient_ensemble():
    """Deux schémas à la même échelle se comparent d'un regard : de front dès
    qu'il y a la place, à la même hauteur, et au bureau tous deux dans un seul
    écran, de leurs titres au bas du plus haut. Un milliard y a la même
    épaisseur ; encore faut-il voir les deux épaisseurs en même temps.

    Sur la tablette en largeur, sous un bandeau de deux rangées, ils prennent à
    peu près toute la hauteur de l'écran : la borne n'y est pas tenue, que le
    moindre nœud de plus ferait tomber, et leurs caisses, alignées en haut, s'y
    comparent quand même. Sur un téléphone et une tablette en hauteur, ils
    restent l'un sous l'autre, chacun à la largeur de la colonne.
    """
    fautes = []
    for visite in mesures():
        lieu = _ou(visite, "fermés")
        if visite["route"] == "cout/":
            assert visite["replie"]["schemas"], f"{lieu} : la carte des flux n'a plus deux schémas"
        if visite["largeur"] < DEUX_SCHEMAS_DE_FRONT:
            continue
        for carte in visite["replie"]["schemas"]:
            if carte["colonnes"] < carte["nombre"] or carte["rangees"] > 1:
                fautes.append(f"{lieu}, carte {carte['carte']} : {carte['nombre']} schémas sur "
                              f"{carte['colonnes']} colonne(s) et {carte['rangees']} rangée(s)")
            au_bureau = (visite["largeur"], visite["hauteur"]) == ECRANS[-1]
            if au_bureau and carte["etendue"] > carte["place"]:
                fautes.append(f"{lieu}, carte {carte['carte']} : les schémas s'étagent sur "
                              f"{carte['etendue']} points, pour {carte['place']} à l'écran")
    assert not fautes, f"{len(fautes)} schémas loin l'un de l'autre :\n" + "\n".join(fautes)


#: Les neuf pages toutes faites, aux deux écrans que Lighthouse émule, et une page
#: dont le pilote ôte l'``onload`` de la feuille entière.
STYLES = [{"route": route, "largeur": largeur, "hauteur": hauteur}
          for route in ROUTES if "#" not in route
          for largeur, hauteur in CHARGEMENTS] + [
    {"route": "risque/", "largeur": 390, "hauteur": 800, "sans_onload": True}]


@functools.lru_cache(maxsize=None)
def _styles() -> list[dict]:
    """Chaque page ouverte deux fois : avec la feuille entière, puis la feuille
    refusée au navigateur, la page n'ayant que le style de son en-tête."""
    return jouer({"ecrans": [], "routes": [], "chargements": [], "adresses": [],
                  "styles": STYLES})["styles"]


def test_chaque_page_se_peint_avec_son_seul_style():
    """Le style qu'une page porte en tête suffit à la peindre telle que la
    feuille entière la peint : chaque élément à la même place, de la même taille,
    dans la même couleur et la même police — routeur passé, tableaux repliés. Il
    ne lui manque rien qu'on verrait arriver avec la feuille entière (action 174,
    proposition du 27 octobre 2026)."""
    fautes = [f"{cas['route']} à {cas['largeur']} points : " + " ; ".join(cas["ecarts"])
              for cas in _styles() if cas.get("ecarts")]
    assert not fautes, "\n".join(fautes)


def test_la_feuille_entiere_devient_effective_meme_sans_son_onload():
    """Déclarée pour l'impression, la feuille entière ne bloque pas l'affichage ;
    son ``onload`` la rend effective une fois chargée. Une politique de sécurité
    qui refuse les gestionnaires en ligne le neutraliserait : le routeur le fait
    alors, sans quoi les gestes et les résultats resteraient sans style."""
    for cas in _styles():
        assert cas["media"] == "all", (
            f"{cas['route']} à {cas['largeur']} points"
            f"{' sans son onload' if cas.get('sans_onload') else ''} : "
            f"la feuille entière reste en « {cas['media']} »")


def _retrecissements(largeur: int):
    """Les pages de schémas de front, rétrécies à cet écran : la visite et ce
    que la page a fait de la fenêtre qui rétrécit."""
    retrecies = [(visite, retrecie) for visite in mesures() for retrecie in visite["retrecie"] or []
                 if retrecie["largeur"] == largeur]
    assert retrecies, f"aucune page de schémas rétrécie de {RETRECIR['depuis']} à {largeur} points"
    return retrecies


def test_une_fenetre_retrecie_redessine_ses_schemas_a_leur_demi_colonne():
    """Une fenêtre qu'on rétrécit au large garde ses schémas de front à leur
    taille : la page se redessine sur place, chacun à sa nouvelle demi-colonne,
    ses textes à la taille que la feuille de style leur donne.

    Le redimensionnement ne redessinait une page qu'en passant les 720 points,
    où ses courbes changent de cadre ; un schéma dessiné à la demi-colonne du
    bureau, 532 unités, se serait montré sur 432 points sur la tablette,
    réduit d'un cinquième. Ici la fenêtre tombe à 900 points : la demi-colonne
    à 370, loin des 480 du dessin tout fait.
    """
    fautes = []
    for visite, retrecie in _retrecissements(900):
        lieu = f"{visite['route'][:40]}, de {visite['largeur']} à {retrecie['largeur']} points"
        if not retrecie["redessinee"]:
            fautes.append(f"{lieu} : la page ne s'est pas redessinée")
        for schema in retrecie["schemas"]:
            if abs(schema["dessin"] - schema["montre"]) > 4:
                fautes.append(f"{lieu} : un schéma dessiné sur {schema['dessin']} unités "
                              f"se montre sur {schema['montre']} points")
    assert not fautes, "\n".join(fautes)


def test_une_page_toute_faite_garde_son_dessin_dans_la_tolerance_de_la_colonne():
    """Le dessin tout fait des schémas de front, 480 unités, convient aux
    demi-colonnes de 432 à 532 points : la fenêtre qui passe de 1 440 à
    1 024 points ne redessine pas la page, dont le moteur n'a pas à charger ;
    ses schémas se montrent à moins de 12 % de leur dessin."""
    fautes = []
    for visite, retrecie in _retrecissements(1024):
        lieu = f"{visite['route'][:40]}, de {visite['largeur']} à {retrecie['largeur']} points"
        if "#" not in visite["route"] and retrecie["redessinee"]:
            fautes.append(f"{lieu} : la page toute faite s'est redessinée pour 11 % d'écart")
        for schema in retrecie["schemas"]:
            if abs(schema["dessin"] - schema["montre"]) > 0.12 * schema["dessin"] + 4:
                fautes.append(f"{lieu} : un schéma dessiné sur {schema['dessin']} unités "
                              f"se montre sur {schema['montre']} points")
    assert not fautes, "\n".join(fautes)


def test_l_image_d_une_carte_pose_de_front_les_schemas_qu_elle_compare():
    """L'image que compose « Partager » a 1 200 pixels de large, quel que soit
    l'écran qui la compose : les schémas qu'une carte compare s'y posent de
    front, chacun sur sa moitié, à la même hauteur, quand ils y tiennent sans
    rétrécir — dessinés à la demi-colonne, ou à la largeur d'un téléphone.
    Aucun n'y rétrécit : ses textes y gardent au moins la taille que la page
    leur donne. Ceux que la tablette en hauteur dessine sur sa colonne
    entière s'y empilent, chacun à toute sa largeur.

    Elle les empilait toujours : ceux qu'un téléphone de 320 points dessine y
    prenaient près de quatre fois leur taille, et l'image près de cinq mille
    pixels de haut. Posés de front sans y regarder, ceux de la tablette en
    hauteur y auraient eu des textes de dix pixels.
    """
    fautes = []
    for visite in mesures():
        if visite["route"] != "cout/":
            continue
        lieu = _ou(visite, "ouverts")
        image = visite["image"]
        assert image and image["largeur"], f"{lieu} : « Partager » n'a composé aucune image"
        traces = image["traces"]
        if len(traces) != 2:
            fautes.append(f"{lieu} : {len(traces)} schémas dans l'image, deux attendus")
            continue
        for trace, dessin in zip(traces, image["dessins"]):
            if trace["largeur"] < dessin:
                fautes.append(f"{lieu} : un schéma dessiné sur {dessin} unités rétrécit "
                              f"à {trace['largeur']} pixels dans l'image")
        if visite["largeur"] < 768 or visite["largeur"] >= DEUX_SCHEMAS_DE_FRONT:
            gauche, droite = sorted(traces, key=lambda trace: trace["x"])
            if gauche["y"] != droite["y"] or gauche["x"] + gauche["largeur"] > droite["x"]:
                fautes.append(f"{lieu} : les schémas de l'image ne sont pas de front — {traces}")
    assert not fautes, f"{len(fautes)} images :\n" + "\n".join(fautes)


def test_les_quatre_systemes_se_comparent_d_un_seul_regard():
    """Les quatre pensions que la carrière vaudrait, dans un seul écran : du
    titre du premier système au montant du dernier, rien à faire défiler."""
    fautes = []
    for visite in mesures():
        if visite["route"] != RESULTATS:
            continue
        montants = visite["replie"]["montants"]
        assert montants and montants["nombre"] == 4, f"{_ou(visite, 'fermés')} : {montants}"
        if montants["etendue"] > montants["place"]:
            fautes.append(f"{_ou(visite, 'fermés')} : les quatre montants s'étagent sur "
                          f"{montants['etendue']} points, pour {montants['place']} à l'écran")
    assert not fautes, "\n".join(fautes)


#: Dès cette largeur, les cartes à publier vont deux par ligne. À 1 024 points,
#: la tablette en largeur, la grille les rangeait une par une, sur 944 points :
#: un chiffre de 110 pixels, une carte par écran, et Le saviez-vous ? sur près
#: de onze mille pixels, deux fois plus qu'au bureau (action 173, étape 7).
DEUX_CARTES_DE_FRONT = 1024

#: La plus petite taille, en pixels, de ce qu'on lit sur une carte : sa phrase
#: et son détail. L'aperçu réduit l'image ; il ne la réduit pas sous ce qui se
#: lit.
TAILLE_LUE_MINIMALE = 12


def test_les_cartes_a_publier_vont_deux_par_ligne_et_se_lisent():
    """Les cartes se comparent, deux par ligne dès qu'il y a la place, et chacune
    se lit : sa phrase et son détail ne tombent jamais sous douze pixels.

    Deux de front à 1 024 points, dans l'image réduite, porteraient leur détail
    à neuf pixels : les cartes y prennent les tailles de lecture du
    téléphone, et ne reprennent le format de l'image que le temps de la
    composer.
    """
    fautes = []
    for visite in mesures():
        lieu = _ou(visite, "fermés")
        if visite["route"] in ("partager/", "saviez-vous/"):
            assert visite["replie"]["cartes"], f"{lieu} : aucune grille de cartes"
        for grille in visite["replie"]["cartes"]:
            if visite["largeur"] >= DEUX_CARTES_DE_FRONT and grille["colonnes"] < 2:
                fautes.append(f"{lieu} : une carte par ligne, sur {grille['largeur']} points")
            if grille["plusPetite"] < TAILLE_LUE_MINIMALE:
                fautes.append(f"{lieu} : une carte se lit à {grille['plusPetite']} pixels")
    assert not fautes, f"{len(fautes)} grilles de cartes :\n" + "\n".join(fautes)


# -- le lancement du navigateur ----------------------------------------------

#: Le module par lequel le pilote lance Chromium et attend son protocole, et
#: un programme qui l'appelle comme lui, sur un faux navigateur : l'adresse du
#: protocole sur sa sortie, ou l'erreur, qui l'arrête.
LANCEUR = RACINE / "tests" / "js" / "navigateur.mjs"
OUVRIR = """
const [lanceur, chemin, delai] = process.argv.slice(1);
const { ouvrirLeNavigateur } = await import(lanceur);
const { adresse, fermer } = await ouvrirLeNavigateur(chemin, { delai: Number(delai) });
fermer();
process.stdout.write(adresse);
"""

_FAUX_NAVIGATEUR = pytest.mark.skipif(
    shutil.which("node") is None or os.name == "nt",
    reason="le faux navigateur est un script sh, que node lance")


def _ouvrir(chemin: Path, delai: int, timeout: float = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", "--input-type=module", "-e", OUVRIR, LANCEUR.as_uri(), str(chemin), str(delai)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", timeout=timeout,
        check=False)


def _faux_navigateur(dossier: Path, muets: int) -> Path:
    """Un faux Chromium : il note chaque lancement, son processus et ses
    arguments, et écrit d'abord, comme le vrai, une erreur de D-Bus ; puis il se
    tait à ses ``muets`` premiers lancements, et ouvre son protocole aux
    suivants."""
    journal = dossier / "lancements"
    faux = dossier / "chrome"
    faux.write_text(
        "#!/bin/sh\n"
        f"echo \"$$ $*\" >> '{journal}'\n"
        "echo '[1:2:1025/135455.621031:ERROR:dbus/bus.cc:405] Failed to connect to the bus' >&2\n"
        f"if [ $(wc -l < '{journal}') -gt {muets} ]; then\n"
        "  echo \"DevTools listening on ws://127.0.0.1:9/devtools/browser/$$\" >&2\n"
        "fi\n"
        "exec sleep 60\n", encoding="utf-8")
    faux.chmod(0o755)
    return faux


def _lancements(dossier: Path) -> list[tuple[int, str]]:
    """Chaque lancement du faux navigateur : son processus, son profil."""
    journal = dossier / "lancements"
    if not journal.exists():
        return []
    lancements = []
    for ligne in journal.read_text(encoding="utf-8").splitlines():
        processus, *arguments = ligne.split()
        lancements.append((int(processus), next(
            argument.split("=", 1)[1] for argument in arguments
            if argument.startswith("--user-data-dir="))))
    return lancements


def _vivant(processus: int) -> bool:
    try:
        os.kill(processus, 0)
    except ProcessLookupError:
        return False
    return True


@_FAUX_NAVIGATEUR
def test_un_navigateur_muet_a_son_premier_lancement_est_relance_sur_un_profil_neuf(tmp_path):
    """Le 25 octobre 2026, deux courses de suite, GitHub a perdu les tests des
    écrans : sur la machine neuve, chargée par les autres tests, le premier
    Chromium n'avait pas ouvert son protocole au bout de trente secondes. Un
    lancement suivant l'ouvrait, ce que les premiers avaient lu du disque resté
    en mémoire. Muet passé le délai, Chromium est tué et relancé, sur un profil
    neuf, que rien de ce que le mort a laissé n'encombre.
    """
    ouvert = _ouvrir(_faux_navigateur(tmp_path, muets=1), delai=2000)
    assert ouvert.returncode == 0, ouvert.stderr
    (muet, profil_du_muet), (relance, profil_relance) = _lancements(tmp_path)
    assert ouvert.stdout == f"ws://127.0.0.1:9/devtools/browser/{relance}"
    assert profil_du_muet != profil_relance
    assert not _vivant(muet), "le premier navigateur, muet, n'a pas été tué"
    assert not Path(profil_du_muet).exists() and not Path(profil_relance).exists()


@_FAUX_NAVIGATEUR
def test_un_navigateur_toujours_muet_n_est_relance_qu_une_fois(tmp_path):
    """Muet deux fois, il échoue, et dit ce qu'il a écrit à chaque lancement."""
    ouvert = _ouvrir(_faux_navigateur(tmp_path, muets=2), delai=1000)
    assert ouvert.returncode == 1
    assert "n'a pas ouvert son protocole" in ouvert.stderr, ouvert.stderr
    assert ouvert.stderr.count("Failed to connect to the bus") == 2, ouvert.stderr
    lancements = _lancements(tmp_path)
    assert len(lancements) == 2
    assert not any(_vivant(processus) or Path(profil).exists()
                   for processus, profil in lancements)


@_FAUX_NAVIGATEUR
@pytest.mark.parametrize("cas", ["absent", "casse"])
def test_un_navigateur_absent_ou_casse_echoue_aussitot_avec_son_message(tmp_path, cas):
    """Ni attendu ni relancé : ce qui manque est sur la machine, et son message
    le dit."""
    chemin = tmp_path / "chrome"
    if cas == "casse":
        chemin.write_text(
            "#!/bin/sh\n"
            f"echo \"$$ $*\" >> '{tmp_path / 'lancements'}'\n"
            "echo \"chrome: error while loading shared libraries: libnss3.so\" >&2\n"
            "exit 127\n", encoding="utf-8")
        chemin.chmod(0o755)
    # Aussitôt : bien avant le délai, que le processus n'attendrait pas.
    ouvert = _ouvrir(chemin, delai=120_000, timeout=30)
    assert ouvert.returncode == 1
    attendu = (f"spawn {chemin} ENOENT" if cas == "absent"
               else "error while loading shared libraries: libnss3.so")
    assert attendu in ouvert.stderr, ouvert.stderr
    assert len(_lancements(tmp_path)) == (1 if cas == "casse" else 0)
