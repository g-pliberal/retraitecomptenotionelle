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
    "unite_revenu=euros_mois&montants=net&situation=actif"
    "&saisie_par=revenu&naissance=2000-01-01&liquidation=2064-01-01"
    "&debut=2021-01-01&statut=salarie_prive_non_cadre&salaire=2800"
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


#: La charte du Parti Libéral Français, celle de son site « Fonction publique :
#: les chiffres » : la page sur le fond clair, le bandeau de tête en pétrole,
#: les titres en Jost.
CHARTE = {"fond": "rgb(244, 247, 247)", "bandeau": "rgb(0, 51, 64)", "titre": "Jost"}


def test_chaque_page_porte_la_charte_du_parti():
    """Le 8 novembre 2026, le propriétaire trouvait le site « très austère et
    très compliqué à comprendre pour l'électeur », et voulait le style de son
    autre site, qui « ressemble beaucoup plus au style du parti » : le fond
    vert profond de l'affiche de septembre cède à la charte du parti — la page
    claire, le bandeau pétrole qui porte le logo et le nom du parti, les
    titres en Jost, le safran pour ce qui compte. Chaque page, à chaque
    largeur, la porte.
    """
    fautes = []
    for visite in mesures():
        charte = visite["replie"]["charte"]
        ou = _ou(visite, "fermés")
        if charte["fond"] != CHARTE["fond"]:
            fautes.append(f"{ou} : fond {charte['fond']}")
        if charte["bandeau"] != CHARTE["bandeau"]:
            fautes.append(f"{ou} : bandeau {charte['bandeau']}")
        if (charte["titre"] or "").split(",")[0].strip().strip('"') != CHARTE["titre"]:
            fautes.append(f"{ou} : titre en {charte['titre']}")
        if not charte["logo"]:
            fautes.append(f"{ou} : pas de logo dans le bandeau")
        if not charte["parti"]:
            fautes.append(f"{ou} : pas le nom du parti dans le bandeau")
    assert not fautes, f"{len(fautes)} écarts à la charte :\n" + "\n".join(fautes[:60])


#: La coquille du site « Fonction publique : les chiffres », lue dans sa feuille
#: de style (``g-pliberal/Nombre-de-fonctionnaires``, ``assets/css/style.css``) :
#: la lueur turquoise de l'en-tête (``.entete``, ``#0a5a62``), le surtitre du
#: bandeau en capitales safran (``.bandeau__surtitre``), le titre à 700, le
#: mot surligné au safran (``.souligne``), le pied en pétrole foncé, aux
#: titres safran (``.pied``).
COQUILLE = {"lueur": "rgb(10, 90, 98)", "safran": "rgb(233, 197, 61)",
            "surlignage": "rgba(233, 197, 61, 0.55)", "blanc": "rgb(255, 255, 255)",
            "graisse": "700", "pied": "rgb(0, 36, 46)", "colonnes": 3}


def test_la_coquille_est_celle_du_site_du_parti():
    """Le 9 novembre 2026, le propriétaire : « J'aimerais que le site reprenne
    encore plus l'aspect de mon autre site ». La charte du 8 novembre en avait
    pris les couleurs, la police et le logo ; la coquille en prend la mise en
    page : le bandeau et l'affiche sous une même lueur turquoise, le surtitre
    en capitales safran espacées, le titre en gras, dont un passage est
    surligné au safran plutôt qu'écrit en safran, et le pied de page en bande
    pétrole foncé d'un bord à l'autre, rangé en trois colonnes au large, en
    une seule sur un téléphone.
    """
    fautes = []
    for visite in mesures():
        coquille = visite["replie"]["coquille"]
        ou = _ou(visite, "fermés")
        for nom in ("lueurDuBandeau", "lueurDeLAffiche"):
            if COQUILLE["lueur"] not in (coquille[nom] or ""):
                fautes.append(f"{ou} : {nom}, {coquille[nom]}")
        surtitre = coquille["surtitre"]
        if (not surtitre or surtitre["casse"] != "uppercase" or surtitre["espace"] <= 0
                or surtitre["couleur"] != COQUILLE["safran"]):
            fautes.append(f"{ou} : surtitre, {surtitre}")
        if coquille["graisseDuTitre"] != COQUILLE["graisse"]:
            fautes.append(f"{ou} : titre à {coquille['graisseDuTitre']}")
        surlignage = coquille["surlignage"]
        if surlignage and (surlignage["couleur"] != COQUILLE["blanc"]
                           or COQUILLE["surlignage"] not in surlignage["fond"]):
            fautes.append(f"{ou} : surlignage, {surlignage}")
        pied = coquille["pied"] or {}
        if pied.get("fond") != COQUILLE["pied"]:
            fautes.append(f"{ou} : pied sur {pied.get('fond')}")
        if abs(pied.get("largeur", 0) - visite["largeur"]) > 1:
            fautes.append(f"{ou} : pied large de {pied.get('largeur')}")
        if pied.get("titres") != COQUILLE["colonnes"]:
            fautes.append(f"{ou} : {pied.get('titres')} titres au pied")
        elif pied["couleurDesTitres"] != COQUILLE["safran"]:
            fautes.append(f"{ou} : titres du pied en {pied['couleurDesTitres']}")
        attendues = COQUILLE["colonnes"] if visite["largeur"] >= 1024 else None
        if visite["largeur"] <= 390:
            attendues = 1
        if attendues and pied.get("colonnes") != attendues:
            fautes.append(f"{ou} : pied en {pied.get('colonnes')} colonnes")
    assert not fautes, f"{len(fautes)} écarts à la coquille :\n" + "\n".join(fautes[:60])


#: Le corps des pages du site « Fonction publique : les chiffres », lu dans la
#: même feuille de style : la carte de chiffre (``.chiffre`` : surface blanche,
#: barre safran de 6 points, valeur en Jost à 700, libellé à 600, détail en
#: ``--texte-doux``), le surtitre de section (``.surtitre`` : capitales
#: espacées à 700, en ``--accent``, tiret safran), les titres à 700, la bande
#: alternée (``.section--alt``, ``--surface-2``), les encadrés (``.encadre`` :
#: barre de 5 points, ``--info-fond`` et ``--info-bord``, ``--alerte-fond`` et
#: ``--alerte-bord`` pour l'attention), le plan (``.sommaire-page`` : une carte
#: blanche aux liens nus), l'appel (``.appel``, ici ``.carte-appel`` : pétrole, lueur ``#0f6f72``,
#: bouton safran) et les boutons de l'affiche (``.bouton--safran``,
#: ``.bouton--clair``).
CORPS = {
    "blanc": "rgb(255, 255, 255)", "safran": "rgb(233, 197, 61)",
    "barre": "6px rgb(233, 197, 61)", "graisse": "700", "libelle": "600",
    "doux": "rgb(68, 96, 106)", "accent": "rgb(0, 105, 95)",
    "appui": "rgb(233, 240, 241)",
    "information": ("rgb(227, 244, 241)", "5px rgb(0, 105, 95)"),
    "attention": ("rgb(255, 246, 219)", "5px rgb(184, 134, 11)"),
    "petrole": "rgb(0, 51, 64)", "lueur": "rgb(15, 111, 114)",
    "filet": "rgba(255, 255, 255, 0.55)", "nu": "rgba(0, 0, 0, 0)",
}

#: Ce qui sépare au moins le bord d'une carte de chiffre de sa valeur, en
#: points : la barre de 6 points, et de quoi la détacher du texte.
RETRAIT_D_UN_CHIFFRE = 16

#: Les boutons que l'affiche de l'accueil porte sous son chapeau.
ACTIONS_DE_L_ACCUEIL = 2


def test_le_corps_des_pages_est_celui_du_site_du_parti():
    """Le 9 novembre 2026, la coquille prise (étape 4), les deux sites
    s'écartaient encore par le corps des pages (action 189, étape 5) : six
    engagements en pile de lignes numérotées, la valeur à droite ; des cartes
    de chiffres au libellé posé sur la valeur ; un fond uni d'un bout à l'autre,
    des intertitres de graisses inégales, des surtitres en casse de phrase ;
    un « En clair » blanc à barre safran ; un plan en pastilles ; un appel
    final en carte blanche ; une affiche sans bouton.

    Le propriétaire a tranché : les six engagements passent en grille de
    cartes, trois par deux au large, au gabarit des « Quatre chiffres pour
    commencer ». Le reste se lit dans la feuille de style du site du parti.
    """
    fautes = []
    for visite in mesures():
        accueil = visite["route"] == "./"
        for etat in ("replie", "deplie"):
            corps = visite[etat]["corps"]
            ou = _ou(visite, "fermés" if etat == "replie" else "ouverts")
            for carte in corps["chiffres"]:
                attendu = {"fond": CORPS["blanc"], "barre": CORPS["barre"],
                           "graisse": CORPS["graisse"], "valeurDAbord": True,
                           "graisseDuLibelle": CORPS["libelle"]}
                ecarts = {cle: carte[cle] for cle, valeur in attendu.items()
                          if carte[cle] != valeur}
                if "Jost" not in (carte["police"] or ""):
                    ecarts["police"] = carte["police"]
                if carte["couleurDuDetail"] not in (None, CORPS["doux"]):
                    ecarts["couleurDuDetail"] = carte["couleurDuDetail"]
                # Sur un téléphone, la valeur et son libellé passaient sous la
                # barre, coupés par le bord de la carte.
                if carte["retrait"] < RETRAIT_D_UN_CHIFFRE:
                    ecarts["retrait"] = carte["retrait"]
                if ecarts:
                    fautes.append(f"{ou} : chiffre {carte['nom']}, {ecarts}")
            for surtitre in corps["surtitres"]:
                # Sur le pétrole de la carte d'appel, le surtitre est en
                # safran, comme celui de l'affiche.
                couleur = CORPS["safran" if surtitre["surLePetrole"] else "accent"]
                if (surtitre["casse"] != "uppercase" or surtitre["espace"] <= 0
                        or surtitre["couleur"] != couleur
                        or surtitre["graisse"] != CORPS["graisse"]
                        or surtitre["tiret"] != CORPS["safran"]):
                    fautes.append(f"{ou} : surtitre, {surtitre}")
            fautes += [f"{ou} : intertitre {titre}" for titre in corps["intertitres"]]
            for bande in corps["bandes"]:
                if (bande["fond"] != CORPS["appui"] or bande["fondDuDebord"] != CORPS["appui"]
                        or bande["gauche"] > 0 or bande["droite"] < visite["largeur"]):
                    fautes.append(f"{ou} : bande, {bande}")
            for encadre in corps["encadres"]:
                attendu = CORPS["attention" if encadre["attention"] else "information"]
                if (encadre["fond"], encadre["barre"]) != attendu:
                    fautes.append(f"{ou} : encadré {encadre}")
            for plan in corps["plans"]:
                if (plan["fond"] != CORPS["blanc"] or plan["barre"] != "1px"
                        or plan["titre"] != "Jost 700" or plan["fondDuLien"] != CORPS["nu"]
                        or plan["bordDuLien"] != "0px"):
                    fautes.append(f"{ou} : plan, {plan}")
            for appel in corps["appels"]:
                if (appel["fond"] != CORPS["petrole"] or CORPS["lueur"] not in appel["lueur"]
                        or appel["titre"] != CORPS["blanc"]
                        or appel["bouton"] != CORPS["safran"]):
                    fautes.append(f"{ou} : appel, {appel}")
            actions = corps["actionsDeLAffiche"]
            if actions and (actions[0]["fond"] != CORPS["safran"] or any(
                    (action["fond"], action["bord"]) != (CORPS["nu"], CORPS["filet"])
                    for action in actions[1:]) or not corps["sousLeChapeau"]):
                fautes.append(f"{ou} : boutons de l'affiche, {actions}")
            if not accueil:
                continue
            if len(actions) != ACTIONS_DE_L_ACCUEIL:
                fautes.append(f"{ou} : {len(actions)} boutons à l'affiche")
            if len(corps["bandes"]) < 2:
                fautes.append(f"{ou} : {len(corps['bandes'])} bandes alternées")
            if len(corps["appels"]) != 1:
                fautes.append(f"{ou} : {len(corps['appels'])} appels")
            grille = (corps["colonnesDesEngagements"], corps["rangeesDesEngagements"])
            if visite["largeur"] >= 1024 and grille != (3, 2):
                fautes.append(f"{ou} : engagements en {grille[0]} colonnes, {grille[1]} rangées")
            if visite["largeur"] <= 390 and grille != (1, 6):
                fautes.append(f"{ou} : engagements en {grille[0]} colonnes, {grille[1]} rangées")
    assert not fautes, f"{len(fautes)} écarts au corps des pages :\n" + "\n".join(fautes[:60])


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


#: Les tailles de police que l'accueil emploie au large, en points : le texte
#: et ses deux voisins, le chapeau, l'intertitre, les chiffres et le titre.
TAILLES_ACCUEIL = 9

#: Ce que la coquille du site du parti a rendu à l'accueil le 9 novembre 2026,
#: et rien d'autre : le surtitre en capitales, et le gras de ses titres.
SURTITRE_DE_L_AFFICHE = "p.surtitre"
GRAISSE_MAXIMALE = 700


def test_l_accueil_se_compose_sur_une_seule_echelle():
    """L'accueil retouché le 5 novembre 2026 (compétence unslop) : la
    hiérarchie vient de la taille et de la couleur, plus des capitales ni de la
    graisse. Il comptait 32 libellés en capitales espacées, cinq graisses, de
    400 à 900, 22 tailles, dont des fractionnaires (14,4 et 15,6 points), un
    italique d'insistance, et des centaines de marges hors de la grille de
    4 points — 9,6, 11,2, 13,6 dans les cases et les lignes de questions.

    Aucune capitale par le style, aucun italique, aucune graisse au-delà de
    600, à toute largeur ; au large, une échelle courte de tailles entières, et
    chaque marge, retrait ou écart sur la grille de 4 points.

    Le 9 novembre 2026, le propriétaire a voulu que le site « reprenne encore
    plus l'aspect » de celui du parti, dont le surtitre est en capitales
    espacées et les titres à 700 : ces deux points lui sont rendus, le reste de
    la règle tient.
    """
    fautes = []
    accueil = [visite for visite in mesures() if visite["route"] == "./"]
    assert accueil, "l'accueil n'a pas été visité"
    for visite in accueil:
        for etat in ("replie", "deplie"):
            ou = _ou(visite, "fermés" if etat == "replie" else "ouverts")
            typo = visite[etat]["typographie"]
            fautes += [f"{ou} : en capitales, {nom}" for nom in typo["capitales"]
                       if not nom.startswith(SURTITRE_DE_L_AFFICHE)]
            fautes += [f"{ou} : en italique, {nom}" for nom in typo["italiques"]]
            lourdes = sorted(g for g in typo["graisses"] if int(g) > GRAISSE_MAXIMALE)
            if lourdes:
                fautes.append(f"{ou} : graisses {lourdes}")
            if visite["largeur"] != 1440:
                continue
            tailles = sorted(float(t) for t in typo["tailles"])
            if len(tailles) > TAILLES_ACCUEIL or any(t != round(t) for t in tailles):
                fautes.append(f"{ou} : {len(tailles)} tailles, {tailles}")
            fautes += [f"{ou} : hors grille, {cote}" for cote in typo["horsGrille"]]
    assert not fautes, f"{len(fautes)} écarts :\n" + "\n".join(fautes[:80])


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


def test_l_adresse_d_une_carte_ne_se_coupe_que_faute_de_place():
    """Le pied d'une carte porte le compte et l'adresse, un seul mot de
    trente-six signes. Quand les deux ne tiennent pas sur une ligne, l'adresse
    passe sous le compte, entière ; elle ne se coupe en plein mot que si elle ne
    tient pas, seule, sur une ligne du pied. Le compte allongé en @pliberalfr
    (28 octobre 2026), elle se coupait à 390 points, le téléphone le plus
    courant : « …/#simulateu », puis « r »."""
    fautes = []
    for visite in mesures():
        for grille in visite["replie"]["cartes"]:
            fautes += [f"{_ou(visite, 'fermés')} : {adresse}"
                       for adresse in grille["adressesCoupees"]]
    assert not fautes, f"{len(fautes)} adresses coupées :\n" + "\n".join(fautes)


# -- les gestes qui se chevauchent -------------------------------------------

#: Ce que les courses retiennent : le paquet de données, que le premier calcul
#: charge, et le lecteur des PDF, qu'un relevé déposé charge.
PAQUET = "moteur/donnees.json"
LECTURE_PDF = "moteur/js/lecture-pdf.js"

#: La page a fini — rendue, ou en échec.
PRETE = '"pret" in document.body.dataset'

#: Un relevé du régime général, tel qu'on le télécharge en texte.
RELEVE = """Relevé de carrière
Régime général
Année Employeur ou situation Revenu d'activité Trimestres
1998 GARAGE MARTIN 94 500 4
1999 GARAGE MARTIN 98 200 4
2001 SOCIETE DUPONT SA 112 400 4
"""


def _deposer(nom: str, texte: str) -> str:
    """Le geste de qui dépose un fichier sur l'encadré du relevé."""
    return f"""(() => {{
      const transfert = new DataTransfer();
      transfert.items.add(new File([{json.dumps(texte)}], {json.dumps(nom)}));
      document.querySelector("#contenu .depot").dispatchEvent(new DragEvent("drop",
        {{ dataTransfer: transfert, bubbles: true, cancelable: true }}));
      return true;
    }})()"""


#: Les messages d'erreur que la page porte en tête.
MESSAGES = ('({messages: [...document.querySelectorAll("#contenu > .erreur")]'
            '.map((m) => m.textContent.slice(0, 60))})')


def _rendus(nom: str, gestes: list[dict]) -> dict:
    """Le simulateur ouvert sur une carrière, que le moteur doit calculer ; le
    paquet refusé une demi-seconde après sa demande, les ``gestes`` faits
    entre-temps."""
    return {
        "nom": nom, "depart": "simuler/#naissance=1980", "retenir": [PAQUET],
        "etapes": [{"attendre": PAQUET}, *gestes, {"pause": 500}, {"refuser": PAQUET},
                   {"jusqua": PRETE}, {"pause": 300}],
        "rendre": MESSAGES,
    }


COURSES = [
    _rendus("un rendu", []),
    _rendus("deux rendus", [{"geste": 'location.hash = "naissance=1981"'}]),
    {
        # La page Coût toute faite, recalculée sur place sous un réglage, deux
        # fois de suite, le paquet refusé chaque fois.
        "nom": "deux échecs de suite", "depart": "cout/", "retenir": [PAQUET],
        "etapes": [
            {"jusqua": PRETE},
            {"geste": 'location.hash = "indexation=prix"'},
            {"refuser": PAQUET}, {"jusqua": PRETE},
            {"geste": 'location.hash = "indexation=masse_salariale"'},
            {"refuser": PAQUET}, {"jusqua": PRETE}, {"pause": 300},
        ],
        "rendre": MESSAGES,
    },
    {
        # Un PDF déposé, dont la lecture attend son module ; puis un relevé en
        # texte, lu jusqu'au bout pendant ce temps ; puis le module du PDF.
        "nom": "deux relevés", "depart": "simuler/", "retenir": [LECTURE_PDF],
        "etapes": [
            {"jusqua": PRETE},
            {"geste": _deposer("scan.pdf", "%PDF-1.4\n%%EOF\n")},
            {"attendre": LECTURE_PDF},
            {"geste": _deposer("releve.txt", RELEVE)},
            {"jusqua": 'document.querySelector("#contenu .rapport-releve")'
                       '.textContent.includes("années lues")'},
            {"laisser": LECTURE_PDF},
            {"jusqua": 'performance.getEntriesByType("resource")'
                       f'.some((e) => e.name.endsWith("{LECTURE_PDF}"))'},
            {"pause": 1000},
        ],
        "rendre": """(() => {
          const rapport = document.querySelector("#contenu .rapport-releve");
          return { rapport: rapport.textContent, echec: rapport.classList.contains("echec"),
                   releve: document.querySelector('#contenu textarea[name="releve"]').value };
        })()""",
    },
]


@functools.lru_cache(maxsize=None)
def _courses() -> dict:
    """Chaque course jouée, par son nom."""
    resultat = jouer({"ecrans": [], "routes": [], "chargements": [], "courses": COURSES})
    return {course["nom"]: course for course in resultat["courses"]}


def test_un_moteur_qui_ne_se_charge_pas_ne_le_dit_qu_une_fois():
    """Deux rendus se chevauchent — l'adresse change pendant que le paquet se
    charge — et le paquet ne vient pas : seul le dernier rendu le dit. Le
    9 novembre 2026, chacun posait son message, le second devant le premier,
    l'échec passant avant la garde du numéro de rendu (action 190, étape 2).
    Deux échecs l'un après l'autre, sur une page recalculée sur place, ne
    posent pas non plus deux messages : le second remplace le premier."""
    for nom in ("un rendu", "deux rendus", "deux échecs de suite"):
        course = _courses()[nom]
        assert not course["fautes"], f"{nom} : {course['fautes']}"
        assert len(course["messages"]) == 1, f"{nom} : {course['messages']}"


def test_le_dernier_releve_depose_l_emporte():
    """Un second relevé déposé pendant que le premier se lit l'emporte, même
    lu le premier : la lecture d'avant s'efface sans rien écrire. Sans garde,
    la plus lente écrivait la dernière — le compte rendu d'un PDF illisible
    sous une carrière remplie par le relevé suivant (action 190, étape 2)."""
    course = _courses()["deux relevés"]
    assert not course["fautes"], course["fautes"]
    assert "années lues" in course["rapport"] and not course["echec"], course["rapport"]
    assert "1998" in course["releve"], course["releve"]


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
