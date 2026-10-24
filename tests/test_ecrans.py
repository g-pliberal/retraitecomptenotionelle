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
#: on calcule le formulaire tel qu'il s'ouvre : la page des résultats.
RESULTATS = (
    "/simuler?unite_revenu=euros_mois&montants=brut&situation=actif"
    "&saisie_par=revenu&naissance=2000-01-01&liquidation=2064-01-01"
    "&debut=2021-01-01&statut=salarie_prive_non_cadre&salaire=3500"
    "&emploi_retraite_employeur=autre&sexe=H&profil=auto&primes=0&enfants=0"
    "&indexation=masse_salariale&lissage=1&table=unisexe&population=niveau_de_vie"
    "&rattachement=salaire&part_cotisation=salariale&contribution_etat=retraite_seule"
    "&foyer=seul&projection=cor_reference&esperance_vie=centrale&emploi=cor_2026"
    "&stock=prix&frais=paliers&taux=forwards&bascule=2026&euros=2026"
)

ROUTES = ["/", "/simuler", RESULTATS, "/cout", "/risque", "/partager",
          "/saviez-vous", "/cas-types", "/avantages", "/methode"]


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


@functools.lru_cache(maxsize=None)
def mesures() -> tuple:
    """Ce que le navigateur a mesuré, une fois par processus : chaque route à
    chaque largeur, dépliants fermés puis ouverts."""
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
    try:
        plan.parent.mkdir(exist_ok=True)
        plan.write_text(json.dumps({
            "adresse": f"http://127.0.0.1:{serveur.server_address[1]}/index.html",
            "ecrans": [{"largeur": l, "hauteur": h} for l, h in ECRANS],
            "routes": ROUTES,
        }), encoding="utf-8")
        execution = subprocess.run(
            ["node", str(PILOTE), chemin, str(plan)], cwd=RACINE,
            capture_output=True, text=True, encoding="utf-8", timeout=900, check=False)
    finally:
        serveur.shutdown()
        plan.unlink(missing_ok=True)
    assert execution.returncode == 0, execution.stderr[-3000:]
    return tuple(json.loads(execution.stdout))


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
#: Carrières types, à l'étape 8, où une rangée en porte sept.
COTE_A_COTE = ["/", "/simuler", RESULTATS, "/cout", "/risque", "/partager",
               "/saviez-vous", "/cas-types"]


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
        if visite["route"] in ("/partager", "/saviez-vous"):
            assert visite["replie"]["cartes"], f"{lieu} : aucune grille de cartes"
        for grille in visite["replie"]["cartes"]:
            if visite["largeur"] >= DEUX_CARTES_DE_FRONT and grille["colonnes"] < 2:
                fautes.append(f"{lieu} : une carte par ligne, sur {grille['largeur']} points")
            if grille["plusPetite"] < TAILLE_LUE_MINIMALE:
                fautes.append(f"{lieu} : une carte se lit à {grille['plusPetite']} pixels")
    assert not fautes, f"{len(fautes)} grilles de cartes :\n" + "\n".join(fautes)
