"""Rendu HTML, sans moteur de gabarits.

Le projet n'a qu'une dépendance obligatoire (PyYAML) ; on ne lui en ajoute pas
une pour produire quelques pages. Les fonctions ci-dessous assemblent du HTML
et échappent systématiquement ce qui vient de l'utilisateur.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape

FEUILLE_DE_STYLE = """
:root {
  color-scheme: light dark;
  --fond: #fbfaf7;
  --fond-carte: #ffffff;
  --fond-appui: #f2efe9;
  --texte: #1b1a17;
  --texte-doux: #5c574d;
  --trait: #ddd7cb;
  /* Bordure des CHAMPS, distincte du filet décoratif : un contour de champ est
     ce qui dit où l'on peut écrire, et doit donc atteindre 3:1 sur les deux
     fonds qu'il sépare — celui du champ et celui de la carte qui le porte
     (WCAG 2.1, 1.4.11). Le filet `--trait` plafonne à 1,4:1 ; mesuré ici :
     3,38:1 sur le fond, 3,53:1 sur la carte. */
  --trait-champ: #8e887a;
  --accent: #7a2e1e;
  --accent-doux: #f0e2dd;
  --actuel: #03729a;
  --retroactif: #9e4334;
  --prospectif: #817f2a;
  --retroactif-employeur: #86538b;
  --prospectif-employeur: #107550;
  --alerte: #8a5a00;
  /* Palette des graphiques : neuf teintes, assez distinctes pour se suivre
     empilées, assez proches pour ne pas jurer avec le reste de la page. */
  --serie-1: #3f5c66;
  --serie-2: #a2472e;
  --serie-3: #6a6a4d;
  --serie-4: #7c5a86;
  --serie-5: #35705f;
  --serie-6: #b07d2b;
  --serie-7: #4a6f9c;
  --serie-8: #8a6552;
  --serie-9: #9a9186;
}
@media (prefers-color-scheme: dark) {
  :root {
    --fond: #16151a;
    --fond-carte: #1e1d23;
    --fond-appui: #26252c;
    --texte: #ece9e3;
    --texte-doux: #a5a099;
    --trait: #35333c;
    --trait-champ: #787581;
    --accent: #e08b6f;
    --accent-doux: #3a2820;
    --actuel: #3d9bc2;
    --retroactif: #cb745f;
    --prospectif: #837118;
    --retroactif-employeur: #a27dc0;
    --prospectif-employeur: #39a48a;
    --alerte: #e0b062;
    --serie-1: #8fb2c0;
    --serie-2: #e08b6f;
    --serie-3: #bcbc8e;
    --serie-4: #c39ccd;
    --serie-5: #79bda9;
    --serie-6: #e0b062;
    --serie-7: #8fabd4;
    --serie-8: #c8a08a;
    --serie-9: #b3aca2;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--fond);
  color: var(--texte);
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  /* En `rem` et non en pixels : une taille en pixels ignore la préférence de
     taille de police du navigateur, sur laquelle comptent ceux qui l'ont
     agrandie une fois pour toutes. 1,0625rem vaut les 17px d'origine quand la
     préférence n'a pas été touchée. */
  font-size: 1.0625rem;
  line-height: 1.6;
}
main { max-width: 60rem; margin: 0 auto; padding: 0 1.25rem; }
/* Lien d'évitement : premier élément parcouru au clavier, invisible tant qu'il
   n'a pas le focus. Sans lui, atteindre le contenu depuis la barre d'adresse
   impose de traverser les six liens de l'en-tête à chaque page (WCAG 2.4.1). Il
   n'est pas caché par `display:none`, qui le sortirait de l'ordre de tabulation
   : il est simplement remonté hors de l'écran. */
.evitement {
  position: absolute; left: 0.5rem; top: -4rem; z-index: 10;
  background: var(--fond-carte); color: var(--accent);
  border: 1px solid var(--accent); border-radius: 0 0 4px 4px;
  padding: 0.5rem 0.9rem; font-size: 0.92rem; text-decoration: none;
  transition: top 0.15s;
}
.evitement:focus { top: 0; }
/* `<main>` reçoit le focus au changement de page (voir index.html) : sans quoi
   le clavier repartirait du haut du document à chaque calcul. Il ne porte pas
   de contour pour autant — ce n'est pas un élément interactif, et le cerner
   tout entier n'apprendrait rien. */
main:focus { outline: none; }

header.bandeau {
  border-bottom: 1px solid var(--trait);
  background: var(--fond-carte);
  padding: 1.25rem 0 1rem;
  margin-bottom: 2rem;
}
header.bandeau .interieur {
  max-width: 60rem; margin: 0 auto; padding: 0 1.25rem;
  display: flex; flex-wrap: wrap; gap: 0.75rem 1.5rem;
  align-items: baseline; justify-content: space-between;
}
header.bandeau h1 { font-size: 1.2rem; margin: 0; letter-spacing: 0.01em; }
header.bandeau h1 a { color: inherit; text-decoration: none; }
nav a {
  color: var(--texte-doux); text-decoration: none;
  margin-left: 1.1rem; font-size: 0.92rem;
  border-bottom: 1px solid transparent;
}
nav a:hover, nav a[aria-current="page"] {
  color: var(--accent); border-bottom-color: var(--accent);
}
h2 { font-size: 1.35rem; margin: 2.5rem 0 0.75rem; font-weight: 600; }
h3 { font-size: 1.05rem; margin: 1.75rem 0 0.5rem; font-weight: 600; }
p { margin: 0.7rem 0; }
a { color: var(--accent); }
.chapeau { font-size: 1.08rem; color: var(--texte-doux); max-width: 44rem; }
.carte {
  background: var(--fond-carte); border: 1px solid var(--trait);
  border-radius: 6px; padding: 1.25rem 1.4rem; margin: 1.5rem 0;
}
.note {
  border-left: 3px solid var(--accent); background: var(--accent-doux);
  padding: 0.85rem 1.1rem; margin: 1.5rem 0; font-size: 0.95rem;
  border-radius: 0 4px 4px 0;
}
.note.avertissement { border-left-color: var(--alerte); }
.discret { color: var(--texte-doux); font-size: 0.9rem; }
/* Un champ des mentions légales que l'éditeur n'a pas encore renseigné. Il est
   marqué, et non masqué : un trou visible se comble, un trou discret reste. */
.a-completer {
  font-style: normal; color: var(--alerte);
  border-bottom: 1px dashed currentColor;
}
form .grille {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
  gap: 1rem 1.5rem;
}
/* Les aides de saisie n'ont pas toutes la même longueur : celle qui passe à la
   ligne décalait son champ d'un cran vers le bas, et les champs d'une même
   rangée ne s'alignaient plus. Chaque cellule devient une colonne dont le
   libellé absorbe la hauteur en trop ; les champs se posent alors sur la même
   ligne, quelle que soit l'aide au-dessus. */
form .grille > div { display: flex; flex-direction: column; }
form .grille > div > label { flex: 1 0 auto; }
label { display: block; font-size: 0.88rem; color: var(--texte-doux); margin-bottom: 0.25rem; }
/* Pas d'`opacity` ici : à 0,8 sur `--texte-doux`, l'aide tombait à 4,23:1 sur
   le fond clair, sous le plancher de 4,5:1 des textes courants (WCAG 1.4.3).
   La couleur pleine la remonte à 6,88:1, et la taille suffit à la distinguer du
   libellé. */
label .aide { display: block; font-size: 0.8rem; }
input, select {
  width: 100%; padding: 0.45rem 0.6rem; font: inherit; font-size: 0.95rem;
  color: var(--texte); background: var(--fond); border: 1px solid var(--trait-champ);
  border-radius: 4px;
}
/* Un seul indicateur de focus pour tout ce qui se parcourt au clavier — champs,
   liens, bouton, dépliants, tableaux défilants. Le contour du navigateur varie
   d'un moteur à l'autre et disparaît sur fond sombre ; celui-ci est posé et
   mesuré : `--accent` tient 8,99:1 sur le fond clair, 7,00:1 sur le sombre. */
:focus-visible {
  outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px;
}
input:focus, select:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
button {
  font: inherit; font-size: 0.98rem; padding: 0.55rem 1.4rem; cursor: pointer;
  color: var(--fond-carte); background: var(--accent);
  border: 1px solid var(--accent); border-radius: 4px;
}
button:hover { opacity: 0.9; }
/* Les métiers de la carrière : une boîte par métier, la dernière en pointillé
   parce qu'elle n'en décrit encore aucun — c'est celle qui sert à en ajouter. */
.metiers { display: grid; gap: 0.9rem; margin: 0.9rem 0 0; }
.metier {
  border: 1px solid var(--trait); border-radius: 4px; padding: 0.9rem 1rem;
  /* `<fieldset>` porte des marges et un padding propres à chaque navigateur. */
  margin: 0; min-width: 0;
}
.metier.facultatif { border-style: dashed; }
/* Le rang du métier est la LÉGENDE du groupe : « Revenu brut mensuel » est le
   même libellé dans les deux blocs, et seule cette légende dit lequel on
   remplit — à l'œil comme à l'oreille (WCAG 3.3.2). */
.metier > .rang {
  margin: 0; padding: 0 0.35rem; font-size: 0.78rem; letter-spacing: 0.05em;
  text-transform: uppercase; color: var(--texte-doux);
}
details { margin-top: 1.25rem; }
summary { cursor: pointer; color: var(--texte-doux); font-size: 0.92rem; }
summary:hover { color: var(--accent); }
details > .grille { margin-top: 1rem; }
/* Un tableau plus large que l'écran défile horizontalement. La zone qui défile
   doit pouvoir recevoir le focus, sinon elle est inatteignable au clavier chez
   les moteurs qui ne rendent pas focusables les boîtes défilantes (WCAG 2.1.1)
   : le HTML lui donne `tabindex="0"`, et le style rend ce focus visible. */
.defilant { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
/* Le titre du tableau, énoncé par les synthèses vocales avant son contenu et
   lu à l'écran comme l'intitulé de la grille. */
caption {
  caption-side: top; text-align: left; font-size: 0.88rem;
  color: var(--texte-doux); padding: 0 0 0.5rem;
}
tbody th { font-weight: 600; }
th, td { text-align: right; padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--trait); }
th:first-child, td:first-child { text-align: left; }
thead th { font-size: 0.82rem; color: var(--texte-doux); font-weight: 600; }
tbody tr:last-child td { border-bottom: none; }
td.nombre, th.nombre { font-variant-numeric: tabular-nums; }
.scenario { margin: 1.4rem 0; }
/* Le bloc des montants passe sous l'intitulé D'UN SEUL TENANT quand la place
   manque : c'est l'entête qui se replie, pas le montant. Depuis que les sommes
   portent les centimes, un intitulé sur deux lignes ne laissait plus la largeur
   des deux colonnes, et la seconde tombait seule sous la première — alors que
   les deux chiffres doivent justement rester côte à côte. */
.scenario .entete { display: flex; justify-content: space-between; gap: 0.2rem 1rem;
                    align-items: baseline; flex-wrap: wrap; }
.scenario .titre { flex: 1 1 14rem; }
.scenario .titre { font-weight: 600; }
/* Deux montants par scénario, côte à côte : le pouvoir d'achat d'aujourd'hui,
   mis en avant, et la somme nominale du mois du départ, en retrait. Ils
   partagent la même ligne de base pour se lire comme un seul chiffre donné en
   deux unités, et non comme deux résultats concurrents. */
.scenario .montant { display: flex; justify-content: flex-end; align-items: baseline;
                     gap: 1.1rem; flex-wrap: nowrap; margin-left: auto;
                     font-variant-numeric: tabular-nums; }
.scenario .chiffre { display: flex; flex-direction: column; align-items: flex-end;
                     white-space: nowrap; }
.scenario .chiffre .somme { line-height: 1.2; }
.scenario .chiffre .unite { font-size: 0.78rem; color: var(--texte-doux); }
.scenario .principal .somme { font-size: 1.45rem; font-weight: 600; }
.scenario .depart { padding-left: 1.1rem; border-left: 1px solid var(--trait); }
.scenario .depart .somme { font-size: 1.05rem; color: var(--texte-doux); }
.scenario .montant .annuel { color: var(--texte-doux); font-size: 0.85rem; }
.barre { height: 12px; background: var(--fond-appui); border-radius: 6px; margin-top: 0.4rem; }
.barre > span { display: block; height: 100%; border-radius: 6px; }
.barre.actuel > span { background: var(--actuel); }
.barre.retroactif > span { background: var(--retroactif); }
.barre.prospectif > span { background: var(--prospectif); }
.barre.retroactif-employeur > span { background: var(--retroactif-employeur); }
.barre.prospectif-employeur > span { background: var(--prospectif-employeur); }
.scenario .glose { font-size: 0.88rem; color: var(--texte-doux); margin-top: 0.35rem; }
.fiches { display: grid; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr)); gap: 1rem; }
.fiche .valeur { font-size: 1.2rem; font-variant-numeric: tabular-nums; }
.fiche .etiquette { font-size: 0.82rem; color: var(--texte-doux); }
.etiquette-fiabilite {
  display: inline-block; font-size: 0.78rem; letter-spacing: 0.04em;
  text-transform: uppercase; padding: 0.15rem 0.5rem; border-radius: 3px;
  background: var(--fond-appui); color: var(--texte-doux);
}
/* Graphiques : du SVG écrit à la main, dont seules les couleurs et les tailles
   de texte sont ici. Le tracé lui-même est dans `graphique()`. */
.graphique { margin: 1.3rem 0 1.7rem; }
.graphique svg { display: block; width: 100%; height: auto; overflow: visible; }
.graphique .grille { stroke: var(--trait); stroke-width: 1; }
.graphique .axe { stroke: var(--texte-doux); stroke-width: 1; }
.graphique .repere {
  stroke: var(--texte-doux); stroke-width: 1; stroke-dasharray: 3 3;
}
.graphique .courbe {
  fill: none; stroke-width: 2.5;
  stroke-linejoin: round; stroke-linecap: round;
}
.graphique .bande { stroke: none; }
.graphique .graduation {
  fill: var(--texte-doux); font-family: inherit; font-size: 12px;
  font-variant-numeric: tabular-nums;
}
ul.legende {
  list-style: none; margin: 0.6rem 0 0; padding: 0;
  display: flex; flex-wrap: wrap; gap: 0.3rem 1.2rem; font-size: 0.86rem;
}
ul.legende li { display: flex; align-items: baseline; gap: 0.4rem; }
.pastille {
  display: inline-block; flex: none;
  width: 0.7rem; height: 0.7rem; border-radius: 2px;
}
/* Ce qu'un tableau ne peut pas porter dans ses cellules sans devenir illisible
   — la phrase qui explique une ligne. Elle était autrefois dans un attribut
   `title`, c'est-à-dire nulle part pour qui n'a pas de souris. */
dl.gloses { margin: 0.8rem 0 0; font-size: 0.9rem; }
dl.gloses dt { font-weight: 600; margin-top: 0.7rem; }
dl.gloses dd { margin: 0.15rem 0 0; padding: 0; color: var(--texte-doux); }
ul.serree { margin: 0.5rem 0; padding-left: 1.2rem; }
ul.serree li { margin: 0.3rem 0; }
footer {
  /* Hors de <main>, le pied porte lui-même la boîte que <main> lui prêtait.
     Le filet doit s'aligner sur le texte : la largeur est donc celle de la
     *zone de contenu* de <main> — 60rem moins ses deux marges intérieures —
     et le padding horizontal reste nul, sans quoi le filet déborderait. */
  width: calc(100% - 2.5rem); max-width: 57.5rem;
  margin: 3rem auto 0; padding: 1.25rem 0 5rem;
  border-top: 1px solid var(--trait);
  font-size: 0.88rem; color: var(--texte-doux);
}
.erreur {
  border-left: 3px solid var(--retroactif); background: var(--fond-appui);
  padding: 0.85rem 1.1rem; margin: 1.5rem 0;
}
pre.json {
  background: var(--fond-appui); border: 1px solid var(--trait); border-radius: 4px;
  padding: 0.9rem 1.1rem; overflow-x: auto; max-height: 26rem; overflow-y: auto;
  font-size: 0.82rem; line-height: 1.45;
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
.chargement { text-align: center; padding: 4rem 1rem; color: var(--texte-doux); }
.chargement .jauge {
  height: 6px; width: min(24rem, 80%); margin: 1.5rem auto 0;
  background: var(--fond-appui); border-radius: 3px; overflow: hidden;
}
.chargement .jauge > span {
  display: block; height: 100%; width: 30%; background: var(--accent);
  animation: glisse 1.4s ease-in-out infinite;
}
@keyframes glisse {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(333%); }
}
body.calcul-en-cours main { opacity: 0.45; transition: opacity 0.2s; }

/* Téléphone : le montant passe sous l'intitulé du scénario plutôt que de se
   serrer contre lui, et la page respire un peu moins large. */
@media (max-width: 34rem) {
  body { font-size: 1rem; }
  main { padding: 0 1rem; }
  footer { width: calc(100% - 2rem); padding: 1.25rem 0 4rem; }
  .carte { padding: 1rem 1.1rem; }
  header.bandeau .interieur { gap: 0.4rem 1rem; }
  nav a { margin: 0 1.1rem 0 0; }
  .scenario .entete { flex-direction: column; gap: 0.15rem; }
  /* Le montant passe sous l'intitulé : les deux chiffres s'alignent alors sur
     le bord gauche, comme lui, et restent l'un à côté de l'autre. */
  .scenario .montant { justify-content: flex-start; gap: 0.9rem; }
  .scenario .chiffre { align-items: flex-start; }
  .scenario .depart { padding-left: 0.9rem; }
  .fiches { grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr)); }
  form .grille { gap: 0.9rem; }
  /* Le SVG se réduit avec la page : ses textes, exprimés en unités du viewBox,
     se réduiraient d'autant et deviendraient illisibles. On les grossit donc
     dans le repère pour qu'ils gardent leur taille à l'écran. */
  .graphique .graduation { font-size: 20px; }
}

/* Écran très étroit : les deux chiffres ne tiennent plus l'un à côté de
   l'autre et passent l'un sous l'autre. Le trait qui les sépare n'a alors plus
   rien à séparer, et pendrait dans le vide. */
@media (max-width: 22rem) {
  /* Les deux chiffres ne tiennent plus l'un à côté de l'autre : ils passent
     l'un sous l'autre, et le trait qui les sépare n'a plus rien à séparer. */
  .scenario .montant { flex-wrap: wrap; }
  .scenario .depart { padding-left: 0; border-left: none; }
}

/* Mouvement réduit : la jauge d'attente glisse sans fin, et une animation qui
   ne s'arrête jamais déclenche nausées et migraines chez qui y est sensible
   (WCAG 2.2.2 et 2.3.3). Le système le signale ; on l'écoute. La jauge reste,
   immobile et pleine : elle dit encore « ça travaille », sans bouger. */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  .chargement .jauge > span { width: 100%; }
}

/* Impression : le lecteur qui imprime une simulation veut les chiffres. La
   navigation ne s'y suit pas, et une zone qui défile ne défile plus — le
   tableau qu'elle contient serait coupé à la largeur de la page. Le formulaire,
   lui, reste : ses champs portent les valeurs saisies, et sont la seule trace
   imprimée de ce qui a été simulé. Les adresses des liens externes sont
   dépliées, faute de quoi une page imprimée renvoie à des liens qu'on ne peut
   pas suivre. */
@media print {
  header.bandeau nav, .evitement { display: none; }
  body { background: #fff; color: #000; font-size: 11pt; }
  .defilant { overflow: visible; }
  .carte, .note, table, .graphique, .scenario { break-inside: avoid; }
  a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.85em; }
}
"""

DEPOT = "https://github.com/g-pliberal/retraitecomptenotionelle"

LIENS = (
    ("/", "Simuler"),
    ("/cas-types", "Cas types"),
    ("/cout", "Coût"),
    ("/methode", "Méthode"),
    ("/donnees", "Données"),
)


def lien(chemin: str, ancre: str = "") -> str:
    """Adresse d'une page interne.

    Le site tient dans une seule page : la navigation passe par l'ancre de
    l'adresse (``#/cas-types``). L'ancre de section, elle, ne peut pas s'y
    ajouter — la place est prise — et n'est acceptée que pour que les appels
    disent vers quoi ils pointent.
    """
    return "#" + chemin


def navigation(chemin_actif: str = "/") -> str:
    return "".join(
        f'<a href="{lien(chemin)}"'
        + (' aria-current="page"' if chemin == chemin_actif else "")
        + f">{escape(libelle)}</a>"
        for chemin, libelle in LIENS
    )


def entete(chemin_actif: str = "/") -> str:
    """Bandeau de tête, précédé du lien d'évitement.

    Le lien d'évitement est le premier élément parcouru au clavier. Le repère de
    navigation porte un nom : une page peut en compter plusieurs, et « navigation »
    tout court ne dit pas laquelle on parcourt.
    """
    return f"""<a class="evitement" href="#contenu">Aller au contenu</a>
<header class="bandeau"><div class="interieur">
  <h1><a href="{lien('/')}">Retraite à comptes notionnels</a></h1>
  <nav aria-label="Navigation principale">{navigation(chemin_actif)}</nav>
</div></header>"""


def pied() -> str:
    """Pied de page.

    Il porte ce que la loi exige d'atteindre depuis n'importe quelle page — les
    mentions légales — et ce que le lecteur doit savoir avant de citer un
    chiffre : d'où vient le modèle, en quelle unité il compte, et qu'il ne vaut
    pas relevé de carrière.
    """
    return f"""<footer>
  <p><strong>Ce simulateur n'a aucune valeur officielle.</strong> Il n'émane
  d'aucune caisse de retraite et ne vaut ni relevé de carrière, ni estimation
  de vos droits : c'est un modèle, appliqué à ce que vous saisissez.
  Pour vos droits réels, seule fait foi votre caisse
  (<a href="https://www.info-retraite.fr/">info-retraite.fr</a>).</p>
  <p>Modèle ouvert, code et données sur <a href="{DEPOT}">GitHub</a> (licence MIT).
  Les montants sont bruts, exprimés en euros constants de l'année de référence.
  Les séries d'avant 1950 et les paramètres de régime restent saisis à la main :
  <a href="{DEPOT}/blob/main/docs/limites.md">lire les limites</a> avant de citer un chiffre.</p>
  <p><a href="{lien('/mentions')}">Mentions légales, données personnelles et accessibilité</a></p>
</footer>"""


# -- fragments ---------------------------------------------------------------


def nombre(valeur: float, decimales: int = 2) -> str:
    """Nombre \u00e0 la fran\u00e7aise : virgule d\u00e9cimale, espace ins\u00e9cable des milliers."""
    return f"{valeur:,.{decimales}f}".replace(",", "\u202f").replace(".", ",")


def euros(montant: float) -> str:
    """Montant en euros, à l'euro près.

    L'unité de tout ce qui n'est pas une pension : capital notionnel,
    cotisations cumulées, salaires portés au compte. Les centimes y seraient du
    bruit — ces grandeurs se lisent par leur ordre de grandeur.
    """
    return nombre(montant, 0) + "\u202f\u20ac"


def euros_centimes(montant: float) -> str:
    """Montant en euros ET en centimes.

    L'unité des PENSIONS, parce que c'est celle que la caisse verse : depuis le
    1er décembre 1986, les prestations de vieillesse sont payées « sur un
    montant non arrondi (y compris les centimes) » — décrets n° 86-130 et
    86-131 du 28 janvier 1986, circulaire Cnav 49/86 du 25 juin 1986. La règle
    d'arrondi qui la précédait — total trimestriel porté au multiple de
    50 centimes supérieur, loi n° 50-147 du 3 février 1950 — a été supprimée à
    cette date. Afficher l'euro rond laissait croire à un arrondi que le droit
    ne fait pas.
    """
    return nombre(montant, 2) + "\u202f\u20ac"


def pourcentage(valeur: float, signe: bool = False, decimales: int = 1) -> str:
    texte = nombre(valeur * 100, decimales)
    if signe and valeur >= 0:
        texte = "+" + texte
    return texte + "\u202f%"


_GROUPES = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?")
_DECIMAL = re.compile(r"\d+\.\d+")
_AVANT_POURCENT = re.compile(r"(\d)%")


def franciser(texte: str) -> str:
    """Convertit les nombres à l'anglaise produits par le moteur.

    « 17,542 € × rendement 6.00% » devient « 17 542 € × rendement 6,00 % ».
    Le moteur formate ses libellés de calcul pour un terminal ; la page web les
    présente à un lecteur francophone, pour qui « 17,542 » se lit 17,5.
    """
    texte = _GROUPES.sub(lambda m: m.group(0).replace(",", "\u202f"), texte)
    texte = _DECIMAL.sub(lambda m: m.group(0).replace(".", ","), texte)
    return _AVANT_POURCENT.sub("\\1\u202f%", texte)


def champ(nom: str, libelle: str, valeur: str, aide: str = "",
          type_: str = "text", **attributs: str) -> str:
    supplement = "".join(
        f' {cle.rstrip("_").replace("_", "-")}="{escape(str(val))}"'
        for cle, val in attributs.items()
    )
    aide_html = f'<span class="aide">{escape(aide)}</span>' if aide else ""
    return (
        f'<div><label for="{nom}">{escape(libelle)}{aide_html}</label>'
        f'<input type="{type_}" id="{nom}" name="{nom}" '
        f'value="{escape(str(valeur))}"{supplement}></div>'
    )


def cache(nom: str, valeur: str) -> str:
    """Un champ que le formulaire porte sans le montrer.

    Sert à ce que le formulaire renvoie un réglage qui ne se change pas dans le
    formulaire mais par un lien — l'unité de saisie des salaires : la changer
    convertit les montants, ce qu'un menu HTML ne sait pas faire.
    """
    return f'<input type="hidden" name="{nom}" value="{escape(str(valeur))}">'


def liste(nom: str, libelle: str, options: list[tuple[str, str]],
          selection: str, aide: str = "", **attributs: str) -> str:
    supplement = "".join(
        f' {cle.rstrip("_").replace("_", "-")}="{escape(str(val))}"'
        for cle, val in attributs.items()
    )
    choix = "".join(
        f'<option value="{escape(code)}"'
        + (" selected" if code == selection else "")
        + f">{escape(texte)}</option>"
        for code, texte in options
    )
    aide_html = f'<span class="aide">{escape(aide)}</span>' if aide else ""
    return (
        f'<div><label for="{nom}">{escape(libelle)}{aide_html}</label>'
        f'<select id="{nom}" name="{nom}"{supplement}>{choix}</select></div>'
    )


@dataclass
class Cellule:
    """Cellule de tableau portant une teinte de fond proportionnelle à sa valeur."""

    html: str
    intensite: float = 0.0

    def style(self) -> str:
        if not self.intensite:
            return ""
        # Teintes calibrées pour rester lisibles sur fond clair comme sur fond
        # sombre : rouge = pension plus faible, vert-de-gris = pension plus forte.
        couleur = "162, 71, 46" if self.intensite < 0 else "90, 116, 80"
        alpha = min(abs(self.intensite), 1.0) * 0.30
        return f' style="background: rgba({couleur}, {alpha:.2f})"'


def tableau(entetes: list[str], lignes: list[list[str | Cellule]],
            classes_colonnes: list[str] | None = None, titre: str = "",
            entete_de_ligne: bool = False) -> str:
    """Tableau de données.

    ``titre`` devient le ``<caption>``. Sans lui, un lecteur d'écran qui arrive
    sur la grille annonce « tableau, 4 colonnes, 41 lignes » et rien de plus :
    il faut en sortir pour deviner ce qu'elle contient. Il nomme aussi la zone
    défilante, qui porte ``tabindex`` afin d'être atteignable au clavier là où
    le tableau dépasse la largeur de l'écran.

    ``entete_de_ligne`` promeut la première cellule de chaque ligne en
    ``<th scope="row">``. C'est ce qui permet à la synthèse vocale d'annoncer
    « Cnav, 2019, 89,4 » plutôt que trois nombres nus : sans en-tête de ligne,
    une cellule lue au hasard dans la grille n'est rattachée à rien.
    """
    classes = classes_colonnes or ["" for _ in entetes]
    tete = "".join(
        f'<th class="{cls}" scope="col">{escape(intitule)}</th>'
        for intitule, cls in zip(entetes, classes)
    )

    def _cellule(cellule: str | Cellule, cls: str, premiere: bool) -> str:
        balise = "th" if premiere and entete_de_ligne else "td"
        portee = ' scope="row"' if balise == "th" else ""
        return (
            f'<{balise} class="{cls}"{portee}'
            + (cellule.style() if isinstance(cellule, Cellule) else "")
            + ">"
            + (cellule.html if isinstance(cellule, Cellule) else cellule)
            + f"</{balise}>"
        )

    corps = "".join(
        "<tr>" + "".join(
            _cellule(cellule, cls, rang == 0)
            for rang, (cellule, cls) in enumerate(zip(ligne, classes))
        ) + "</tr>"
        for ligne in lignes
    )
    legende = f"<caption>{escape(titre)}</caption>" if titre else ""
    nom = f' role="region" aria-label="{escape(titre)}"' if titre else ""
    return (
        f'<div class="defilant" tabindex="0"{nom}><table>{legende}'
        f"<thead><tr>{tete}</tr></thead>"
        f"<tbody>{corps}</tbody></table></div>"
    )


def gloses(entrees: list[tuple[str, str]]) -> str:
    """Les phrases qu'un tableau ne peut pas porter dans ses cellules.

    Elles tenaient jusqu'ici dans un attribut ``title``, c'est-à-dire nulle part
    : une infobulle de survol ne s'ouvre ni au clavier, ni au doigt, ni sous une
    synthèse vocale. Sorties du tableau, elles se lisent dans tous les cas.
    """
    if not entrees:
        return ""
    corps = "".join(
        f"<dt>{escape(terme)}</dt><dd>{escape(texte)}</dd>"
        for terme, texte in entrees
    )
    return f'<dl class="gloses">{corps}</dl>'


def fiche(etiquette: str, valeur: str) -> str:
    return (
        f'<div class="fiche"><div class="valeur">{valeur}</div>'
        f'<div class="etiquette">{escape(etiquette)}</div></div>'
    )


# -- graphiques --------------------------------------------------------------
#
# Le dépôt n'a pas de bibliothèque de tracé, et n'en aura pas : le site charge
# ses propres fichiers et rien d'autre. Les graphiques sont donc du SVG écrit à
# la main, en deux exemplaires — ici et dans ``moteur/js/gabarit.js`` —, et
# comparés caractère par caractère par les témoins. D'où deux règles de
# construction qu'il ne faut pas enfreindre :
#
#   * toutes les coordonnées passent par ``nombre_brut``, qui arrondit comme
#     Python le fait, pour que les deux rendus produisent la même chaîne ;
#   * le pas des graduations est cherché par ITÉRATION sur une échelle de
#     valeurs rondes, jamais par un logarithme, dont les deux langages ne
#     garantissent pas le même dernier bit.
#
# Les couleurs sont des variables CSS : le graphique suit le thème clair ou
# sombre sans que rien ne soit recalculé.

#: Cadre de tracé, en unités du ``viewBox``. Le SVG est redimensionné par le
#: navigateur ; ces nombres ne sont donc pas des pixels mais un repère.
LARGEUR_TRACE = 720
HAUTEUR_TRACE = 300
MARGE_GAUCHE = 66
MARGE_DROITE = 24
MARGE_HAUT = 26
MARGE_BAS = 28
#: La marge de droite loge la MOITIÉ de la dernière graduation d'abscisse, qui
#: est centrée sur elle : trop étroite, « 2024 » déborderait du viewBox.

#: Nombre d'intervalles de l'axe vertical. Cinq : assez pour lire, assez peu
#: pour ne pas encombrer, et surtout assez pour qu'un maximum de 427 tienne dans
#: une échelle qui monte à 500 plutôt qu'à 800 — avec quatre intervalles, la
#: moitié du cadre restait vide.
DIVISIONS_Y = 5

#: Échelle des pas de graduation admissibles, multipliée par des puissances de
#: dix. On la parcourt du plus petit au plus grand jusqu'à couvrir la valeur
#: maximale : aucune fonction transcendante n'intervient, donc aucun écart
#: possible entre les deux portages.
PAS_RONDS = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0)

#: Écart minimal, en années, entre une décennie graduée et une borne de l'axe.
#: Les bornes sont graduées d'office — ce sont elles qui datent la série —, et
#: une décennie trop proche de l'une d'elles ne fait que chevaucher son
#: étiquette. Six ans : « 2020 » et « 2024 » ne tiennent pas côte à côte sur
#: l'écran d'un téléphone, où les textes du repère sont grossis.
ECART_MINIMAL_GRADUATIONS = 6

#: Écart vertical minimal, en unités du repère, entre deux étiquettes posées au
#: bout des courbes. Les couleurs des cinq scénarios ne suffisent pas à les
#: distinguer — mesuré : la pire paire voisine tombe à ΔE 4,3 sous deutéranopie,
#: et à 11,8 en vision normale, sous le plancher de 15. Une étiquette en bout de
#: courbe donne un second encodage, qui ne dépend pas de la couleur ; encore
#: faut-il que deux étiquettes ne se recouvrent pas.
#: 22 et non 12 : sur téléphone les textes du repère sont grossis de 12 à 20
#: unités du viewBox, et deux étiquettes séparées de douze s'y chevauchaient.
ESPACEMENT_ETIQUETTES = 22.0


@dataclass(frozen=True)
class Serie:
    """Une courbe ou une bande d'un graphique."""

    libelle: str
    #: Valeurs alignées sur les abscisses passées au graphique. ``None`` marque
    #: une année sans valeur : la courbe y est interrompue plutôt qu'inventée.
    valeurs: tuple[float | None, ...]
    #: Expression CSS de la couleur, en général ``var(--...)``.
    couleur: str
    #: Trait discontinu, pour distinguer deux courbes de même famille.
    tirets: bool = False
    #: Glose affichée dans la légende, sous le libellé.
    glose: str = ""


def nombre_brut(valeur: float, decimales: int = 1) -> str:
    """Nombre à l'anglaise, pour un attribut SVG — jamais pour du texte lu."""
    return f"{valeur:.{decimales}f}"


def pas_graduation(maximum: float, divisions: int = DIVISIONS_Y) -> float:
    """Plus petit pas rond dont ``divisions`` intervalles couvrent ``maximum``."""
    if maximum <= 0:
        return 1.0
    base = 1e-9
    while base < 1e12:
        for facteur in PAS_RONDS:
            pas = base * facteur
            if pas * divisions >= maximum:
                return pas
        base *= 10.0
    return base


def _abscisse(annee: int, premiere: int, derniere: int) -> float:
    largeur = LARGEUR_TRACE - MARGE_GAUCHE - MARGE_DROITE
    if derniere == premiere:
        return MARGE_GAUCHE + largeur / 2
    return MARGE_GAUCHE + largeur * (annee - premiere) / (derniere - premiere)


def _ordonnee(valeur: float, sommet: float) -> float:
    hauteur = HAUTEUR_TRACE - MARGE_HAUT - MARGE_BAS
    if sommet <= 0:
        return HAUTEUR_TRACE - MARGE_BAS
    return HAUTEUR_TRACE - MARGE_BAS - hauteur * valeur / sommet


def _graduations_x(premiere: int, derniere: int) -> list[int]:
    """Décennies comprises dans la plage, plus les deux bornes."""
    annees = [a for a in range(premiere, derniere + 1) if a % 10 == 0]
    if premiere not in annees:
        annees.insert(0, premiere)
    if derniere not in annees:
        annees.append(derniere)
    # Deux graduations trop proches se chevauchent : on retire la décennie
    # voisine plutôt que la borne, qui porte l'information.
    return [
        a for a in annees
        if a in (premiere, derniere)
        or (a - premiere >= ECART_MINIMAL_GRADUATIONS
            and derniere - a >= ECART_MINIMAL_GRADUATIONS)
    ]


def _chemin(serie: Serie, annees: tuple[int, ...], sommet: float) -> str:
    """Chemin SVG d'une courbe, interrompu là où la série n'a pas de valeur."""
    morceaux: list[str] = []
    commence = False
    for annee, valeur in zip(annees, serie.valeurs):
        if valeur is None:
            commence = False
            continue
        x = nombre_brut(_abscisse(annee, annees[0], annees[-1]))
        y = nombre_brut(_ordonnee(valeur, sommet))
        morceaux.append(f"{'M' if not commence else 'L'}{x} {y}")
        commence = True
    return " ".join(morceaux)


def _bande(basses: list[float], hautes: list[float],
           annees: tuple[int, ...], sommet: float) -> str:
    """Chemin fermé d'une bande empilée : le dessus à l'aller, le dessous au retour."""
    aller = [
        f"{'M' if rang == 0 else 'L'}"
        f"{nombre_brut(_abscisse(annee, annees[0], annees[-1]))} "
        f"{nombre_brut(_ordonnee(haute, sommet))}"
        for rang, (annee, haute) in enumerate(zip(annees, hautes))
    ]
    retour = [
        f"L{nombre_brut(_abscisse(annee, annees[0], annees[-1]))} "
        f"{nombre_brut(_ordonnee(basse, sommet))}"
        for annee, basse in zip(reversed(annees), reversed(basses))
    ]
    return " ".join(aller + retour) + " Z"


def _sommet(series: tuple[Serie, ...], empile: bool) -> tuple[float, float]:
    """Sommet de l'axe vertical et pas de graduation."""
    if empile:
        maximum = max(
            (sum(v for v in colonne if v is not None)
             for colonne in zip(*(s.valeurs for s in series))),
            default=0.0,
        )
    else:
        maximum = max(
            (v for serie in series for v in serie.valeurs if v is not None),
            default=0.0,
        )
    pas = pas_graduation(maximum)
    return pas * DIVISIONS_Y, pas


def _etiquettes_de_fin(series: tuple[Serie, ...], annees: tuple[int, ...],
                       sommet: float, etiquettes: tuple[str, ...]) -> str:
    """Le libellé court de chaque courbe, posé à son extrémité droite.

    Second encodage de l'identité, exigé ici parce que la couleur seule ne
    sépare pas les cinq scénarios. Les étiquettes sont écartées les unes des
    autres quand deux courbes finissent trop près : sans cela, les scénarios 3
    et 4, que trente-huit mille euros séparent au bout de quarante ans,
    superposeraient leurs chiffres.
    """
    poses: list[tuple[float, int, str]] = []
    for rang, (serie, texte) in enumerate(zip(series, etiquettes)):
        derniere = next(
            (v for v in reversed(serie.valeurs) if v is not None), None
        )
        if derniere is None or not texte:
            continue
        poses.append((_ordonnee(derniere, sommet), rang, texte))
    if not poses:
        return ""

    # Tri sur (ordonnée, rang) : le rang départage deux courbes de même hauteur,
    # pour que les deux portages posent les étiquettes dans le même ordre.
    poses.sort(key=lambda pose: (pose[0], pose[1]))
    ecartees: list[tuple[float, str]] = []
    precedent = float("-inf")
    for y, _, texte in poses:
        y = max(y, precedent + ESPACEMENT_ETIQUETTES)
        ecartees.append((y, texte))
        precedent = y

    # Débordement par le bas : tout le paquet remonte d'un bloc, plutôt que la
    # dernière étiquette sorte du cadre.
    base = _ordonnee(0.0, sommet)
    debord = max(0.0, precedent - base)
    x = nombre_brut(LARGEUR_TRACE - MARGE_DROITE + 4)
    return "".join(
        f'<text class="graduation" x="{x}" y="{nombre_brut(y - debord)}" '
        f'dy="0.32em" text-anchor="start">{escape(texte)}</text>'
        for y, texte in ecartees
    )


def graphique(titre: str, annees: tuple[int, ...], series: tuple[Serie, ...],
              unite: str = "", empile: bool = False, decimales: int = 0,
              legende: bool = True, repere: float | None = None,
              libelle_repere: str = "",
              etiquettes: tuple[str, ...] = ()) -> str:
    """Graphique en courbes, ou en bandes empilées si ``empile``.

    ``titre`` n'est pas affiché : il est le texte alternatif du SVG, c'est-à-dire
    ce que lit une synthèse vocale. Ce que voit l'œil est dans la légende et
    dans la phrase qui précède le graphique.

    ``repere`` marque une année d'un trait vertical. Il sert à dire où
    l'observation s'arrête et où la projection commence — une frontière qu'un
    graphique doit montrer, faute de quoi il donne à une hypothèse l'apparence
    d'une mesure.
    """
    if not annees or not series:
        return ""

    sommet, pas = _sommet(series, empile)
    gauche = nombre_brut(_abscisse(annees[0], annees[0], annees[-1]))
    droite = nombre_brut(_abscisse(annees[-1], annees[0], annees[-1]))

    lignes = []
    for division in range(DIVISIONS_Y + 1):
        valeur = pas * division
        y = nombre_brut(_ordonnee(valeur, sommet))
        lignes.append(
            f'<line class="grille" x1="{gauche}" y1="{y}" x2="{droite}" y2="{y}"/>'
            f'<text class="graduation" x="{nombre_brut(MARGE_GAUCHE - 6)}" y="{y}" '
            f'dy="0.32em" text-anchor="end">{nombre(valeur, decimales)}</text>'
        )
    base = nombre_brut(_ordonnee(0.0, sommet))
    for annee in _graduations_x(annees[0], annees[-1]):
        x = nombre_brut(_abscisse(annee, annees[0], annees[-1]))
        lignes.append(
            f'<text class="graduation" x="{x}" '
            f'y="{nombre_brut(HAUTEUR_TRACE - MARGE_BAS + 16)}" '
            f'text-anchor="middle">{annee}</text>'
        )

    traces = []
    if empile:
        # La PREMIÈRE série est la bande du BAS : la légende se lit alors dans
        # l'ordre du graphique, de bas en haut, et non à l'envers.
        cumul = [0.0 for _ in annees]
        for serie in series:
            hautes = [
                bas + (valeur or 0.0) for bas, valeur in zip(cumul, serie.valeurs)
            ]
            traces.append(
                f'<path class="bande" fill="{serie.couleur}" '
                f'd="{_bande(cumul, hautes, annees, sommet)}"/>'
            )
            cumul = hautes
    else:
        for serie in series:
            tirets = ' stroke-dasharray="5 4"' if serie.tirets else ""
            traces.append(
                f'<path class="courbe" stroke="{serie.couleur}"{tirets} '
                f'd="{_chemin(serie, annees, sommet)}"/>'
            )

    unite_html = (
        f'<text class="graduation" x="{nombre_brut(MARGE_GAUCHE - 6)}" '
        f'y="{nombre_brut(MARGE_HAUT - 10)}" text-anchor="end">{escape(unite)}</text>'
        if unite else ""
    )
    repere_html = ""
    if repere is not None and annees[0] <= repere <= annees[-1]:
        x = nombre_brut(_abscisse(repere, annees[0], annees[-1]))
        etiquette = (
            f'<text class="graduation" x="{nombre_brut(_abscisse(repere, annees[0], annees[-1]) + 5)}" '
            f'y="{nombre_brut(MARGE_HAUT + 8)}" text-anchor="start">'
            f"{escape(libelle_repere)}</text>"
            if libelle_repere else ""
        )
        repere_html = (
            f'<line class="repere" x1="{x}" y1="{nombre_brut(MARGE_HAUT)}" '
            f'x2="{x}" y2="{base}"/>{etiquette}'
        )
    legende_html = _legende(series) if legende else ""
    etiquettes_html = (
        _etiquettes_de_fin(series, annees, sommet, etiquettes) if etiquettes else ""
    )
    return (
        f'<figure class="graphique">'
        f'<svg viewBox="0 0 {LARGEUR_TRACE} {HAUTEUR_TRACE}" role="img" '
        f'aria-label="{escape(titre)}">'
        f"{''.join(lignes)}{''.join(traces)}"
        f'<line class="axe" x1="{gauche}" y1="{base}" x2="{droite}" y2="{base}"/>'
        f"{repere_html}{unite_html}{etiquettes_html}"
        f"</svg>{legende_html}</figure>"
    )


def _legende(series: tuple[Serie, ...]) -> str:
    """Légende du graphique, posée en ``<figcaption>``.

    Ce n'est pas un ornement : le SVG est annoncé comme une image, et la légende
    est la seule chose qui dise, en texte, ce que chaque couleur représente.
    Dans la figure, elle en devient le nom accessible ; hors d'elle, elle
    n'était qu'une liste flottant sous un dessin.
    """
    entrees = "".join(
        f'<li><span class="pastille" style="background:{serie.couleur}"></span>'
        f"<span>{escape(serie.libelle)}"
        + (f' <span class="discret">{escape(serie.glose)}</span>' if serie.glose else "")
        + "</span></li>"
        for serie in series
    )
    return f'<figcaption><ul class="legende">{entrees}</ul></figcaption>'
