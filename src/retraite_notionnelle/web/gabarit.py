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
  --liberal: #c04a9a;
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
    --liberal: #c86bb0;
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
header.bandeau h1 a {
  color: inherit; text-decoration: none;
  display: inline-flex; align-items: center; gap: 0.5rem;
}
header.bandeau h1 .icone { color: var(--accent); width: 1.15em; height: 1.15em; }
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
.note.avertissement {
  border-left-color: var(--alerte);
  display: flex; align-items: flex-start; gap: 0.6rem;
}
/* Le pictogramme garde sa taille quand le texte passe à la ligne, et se pose
   sur la première ligne plutôt qu'au milieu du bloc. */
.note.avertissement > .icone {
  color: var(--alerte); width: 1.15em; height: 1.15em; margin-top: 0.12em;
}
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
/* `hidden` seul ne masque rien ici : `display: flex` ci-dessus l'emporte sur la
   feuille du navigateur. La règle est écrite pour le champ de revenu d'une
   période sans emploi, que la page retire dès que le motif est choisi. */
form .grille > div[hidden] { display: none; }
form .grille > div > label { flex: 1 0 auto; }
label { display: block; font-size: 0.88rem; color: var(--texte-doux); margin-bottom: 0.25rem; }
/* Pas d'`opacity` ici : à 0,8 sur `--texte-doux`, l'aide tombait à 4,23:1 sur
   le fond clair, sous le plancher de 4,5:1 des textes courants (WCAG 1.4.3).
   La couleur pleine la remonte à 6,88:1, et la taille suffit à la distinguer du
   libellé. */
label .aide { display: block; font-size: 0.8rem; }
/* Ce qu'une date saisie vaut en âge, sous le champ qui la porte : « soit
   64 ans et 7 mois ». Le calendrier a remplacé les champs d'âge ; cette ligne
   rend l'âge qu'ils disaient, et la page le recalcule à chaque frappe. */
.calcul {
  display: block; font-size: 0.8rem; color: var(--texte-doux); margin-top: 0.3rem;
}
input, select, textarea {
  width: 100%; padding: 0.45rem 0.6rem; font: inherit; font-size: 0.95rem;
  color: var(--texte); background: var(--fond); border: 1px solid var(--trait-champ);
  border-radius: 4px;
}
/* Le relevé de carrière se lit en colonnes : une police à chasse fixe aligne
   les années les unes sous les autres, et une faute de frappe s'y voit. Le
   redimensionnement reste vertical — l'élargir déborderait de la carte. */
textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.88rem; line-height: 1.45; resize: vertical;
}
/* Un seul indicateur de focus pour tout ce qui se parcourt au clavier — champs,
   liens, bouton, dépliants, tableaux défilants. Le contour du navigateur varie
   d'un moteur à l'autre et disparaît sur fond sombre ; celui-ci est posé et
   mesuré : `--accent` tient 8,99:1 sur le fond clair, 7,00:1 sur le sombre. */
:focus-visible {
  outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px;
}
input:focus, select:focus, textarea:focus {
  outline: 2px solid var(--accent); outline-offset: 1px;
}
button {
  font: inherit; font-size: 0.98rem; padding: 0.55rem 1.4rem; cursor: pointer;
  color: var(--fond-carte); background: var(--accent);
  border: 1px solid var(--accent); border-radius: 4px;
}
button:hover { opacity: 0.9; }
/* Un lien qui a le poids d'un bouton : il ouvre le simulateur, c'est-à-dire
   la seule chose que la page Coût invite à faire. Il reste un lien — il mène à
   une autre adresse, se copie et s'ouvre dans un onglet —, seul son habit
   change. */
.actions { display: flex; flex-wrap: wrap; gap: 0.75rem 1.4rem; align-items: center;
           margin: 1.1rem 0 0; }
a.bouton {
  display: inline-block; text-decoration: none;
  color: var(--fond-carte); background: var(--accent);
  border: 1px solid var(--accent); border-radius: 4px;
  padding: 0.55rem 1.4rem; font-size: 0.98rem;
}
a.bouton:hover { opacity: 0.9; }
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
/* Les pictogrammes. Un seul jeu — Lucide, grille de 24, trait de 2 —, une
   seule règle : ils prennent la taille et la couleur du texte qui les porte.
   C'est ce qui les fait tenir ensemble partout, du titre du site au chevron
   d'un dépliant, sans qu'aucune taille soit écrite deux fois. */
.icone {
  width: 1.05em; height: 1.05em; flex: none; vertical-align: -0.16em;
}
details { margin-top: 1.25rem; }
/* Le résumé d'un dépliant porte SON chevron, et non celui du navigateur : le
   marqueur natif n'a ni la même forme ni la même taille d'un moteur à l'autre,
   et ne suit aucune de nos grilles. Il est donc masqué partout, une fois. */
summary {
  cursor: pointer; color: var(--texte-doux); font-size: 0.92rem;
  display: flex; align-items: center; gap: 0.45rem; list-style: none;
}
summary::-webkit-details-marker { display: none; }
summary::marker { content: ""; }
summary > .icone { color: var(--accent); transition: transform 0.15s; }
details[open] > summary > .icone { transform: rotate(180deg); }
summary:hover { color: var(--accent); }
details > .grille { margin-top: 1rem; }
/* Une section repliée. Son titre a le poids d'un intertitre, parce qu'il en
   tient lieu : c'est lui qu'on parcourt pour savoir ce que la page contient
   encore. Les sections se suivent sans espace entre elles, séparées par un
   filet, pour qu'une pile de dix se lise comme un sommaire. */
details.section { margin: 0; border-top: 1px solid var(--trait); }
details.section:last-of-type { border-bottom: 1px solid var(--trait); }
details.section > summary {
  color: var(--texte); font-size: 1rem; font-weight: 600;
  padding: 0.85rem 0.2rem; gap: 0.6rem;
}
details.section > summary:hover { color: var(--accent); }
details.section > .dedans { padding: 0 0 1.2rem 1.65rem; }
details.section > .dedans > :first-child { margin-top: 0; }
details.section > .dedans > h4 {
  font-size: 0.98rem; font-weight: 600; margin: 1.5rem 0 0.4rem;
}
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
/* Une colonne de PHRASES, et non de nombres : elle se lit alignée à gauche,
   comme tout texte. Les cellules d'un tableau sont alignées à droite par
   défaut, ce qui convient aux chiffres qu'on compare colonne par colonne, et
   pas du tout à « des trimestres, et 72 barèmes différents ». */
td.texte, th.texte { text-align: left; }
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
.barre.liberal > span { background: var(--liberal); }
.scenario .glose { font-size: 0.88rem; color: var(--texte-doux); margin-top: 0.35rem; }
.fiches { display: grid; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr)); gap: 1rem; }
.fiche .valeur { font-size: 1.2rem; font-variant-numeric: tabular-nums; }
.fiche .etiquette { font-size: 0.82rem; color: var(--texte-doux); }
.fiche .precision { font-size: 0.82rem; color: var(--texte-doux); margin-top: 0.3rem; }
/* Les trois chiffres d'ouverture d'une page : ce sont eux qu'on emporte si on
   ne lit rien d'autre, et ils doivent donc se lire de loin, avant le texte.
   L'étiquette passe AU-DESSUS du nombre — on lit « ce qui rentre » puis
   « 417 Md € », dans cet ordre, et non un nombre dont on cherche le sens. */
.fiches.reperes { gap: 0.9rem; margin: 1.5rem 0; }
.fiches.reperes .fiche {
  background: var(--fond-carte); border: 1px solid var(--trait);
  border-radius: 8px; padding: 1rem 1.1rem;
  display: flex; flex-direction: column;
}
.fiches.reperes .fiche .valeur {
  font-size: 1.9rem; line-height: 1.15; font-weight: 600; order: 2;
}
.fiches.reperes .fiche .etiquette {
  order: 1; font-size: 0.86rem; margin-bottom: 0.25rem;
}
.fiches.reperes .fiche .precision { order: 3; margin-top: 0.35rem; }
/* Quelques idées, une par bloc. Elles se lisent côte à côte, de même poids :
   c'est ce qui les distingue d'une liste, où la première l'emporte. */
.points { display: grid; grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr));
          gap: 1rem; margin: 1.5rem 0; }
.points .point { background: var(--fond-carte); border: 1px solid var(--trait);
                 border-radius: 8px; padding: 1rem 1.1rem; }
.points .point > h3 { margin: 0 0 0.3rem; font-size: 1rem; }
.points .point > p { margin: 0; font-size: 0.95rem; color: var(--texte-doux); }

/* Une question, sa réponse, le tracé qui la montre. Encadrée pour se découper :
   une capture de ce bloc se comprend hors du site. */
section.cle {
  background: var(--fond-carte); border: 1px solid var(--trait);
  border-radius: 8px; padding: 1.3rem 1.4rem 1rem; margin: 1.75rem 0;
}
section.cle > h3 { margin: 0; font-size: 1.15rem; }
section.cle > .reponse {
  font-size: 1.1rem; line-height: 1.5; max-width: 46rem; margin: 0.4rem 0 0.2rem;
}
section.cle > .source {
  font-size: 0.82rem; color: var(--texte-doux); margin: 0.2rem 0 0;
}
/* Le bouton qui compose l'image. Discret — il ne dispute pas la place au
   graphique —, mais toujours au même endroit : en bas à droite de la carte,
   là où se trouve ce qu'on fait d'un contenu qu'on vient de lire. */
section.cle > .partage { margin: 0.6rem 0 0; text-align: right; }
section.cle > .partage > .partager {
  font: inherit; font-size: 0.85rem; cursor: pointer;
  color: var(--accent); background: none;
  border: 1px solid var(--trait-champ); border-radius: 4px;
  padding: 0.35rem 0.8rem;
  display: inline-flex; align-items: center; gap: 0.4rem;
}
section.cle > .partage > .partager:hover {
  border-color: var(--accent); background: var(--accent-doux);
}
section.cle > .partage > .partager[disabled] { opacity: 0.6; cursor: progress; }
section.cle > .donnees-graphique { margin-bottom: 0.6rem; }
/* Le mot de jargon et sa définition. Tout est en ligne — le mot doit couler
   dans sa phrase comme n'importe quel autre —, et l'enveloppe est simplement
   `relative` pour servir de repère à la bulle posée dessous. */
.mot { position: relative; }
.mot > .terme {
  /* Le bouton hérite de la phrase qui le porte, taille et graisse comprises :
     sans cela un mot du glossaire se serait vu d'abord comme un bouton, et
     seulement ensuite comme un mot. Seul le pointillé le signale. */
  font: inherit; color: inherit; background: none; border: none;
  border-bottom: 1px dotted var(--accent); border-radius: 0;
  padding: 0; margin: 0; cursor: help;
}
/* L'appel d'une bulle : un point d'interrogation, et non un mot souligné. Il
   suit un titre ou un libellé de champ, et ouvre ce qui n'est nécessaire ni
   pour remplir le formulaire, ni pour lire un résultat. La cible tactile fait
   au moins 24 px de côté (WCAG 2.5.8) : le `min-width`/`min-height` l'impose,
   là où le seul padding la laissait à 19 px au doigt dans un texte réduit —
   celui d'une glose ou d'une note, où se trouvent justement la plupart des
   appels. */
.mot > .terme.appel {
  display: inline-flex; align-items: center; justify-content: center;
  margin-left: 0.25em; padding: 0.2em; font-size: 0.95em; line-height: 1;
  min-width: 1.5rem; min-height: 1.5rem;
  color: var(--texte-doux); border-bottom: none; vertical-align: -0.1em;
}
.mot > .terme:hover, .mot > .terme[aria-expanded="true"] { color: var(--accent); }
.mot > .terme[aria-expanded="true"] { border-bottom-style: solid; }
.mot > .bulle {
  display: block; position: absolute; left: 0; top: calc(100% + 0.4rem);
  z-index: 5; width: max(14rem, min(22rem, 70vw));
  background: var(--fond-carte); color: var(--texte);
  border: 1px solid var(--trait-champ); border-radius: 6px;
  box-shadow: 0 6px 22px rgba(0, 0, 0, 0.14);
  padding: 0.6rem 0.8rem; font-size: 0.88rem; line-height: 1.45;
  /* Le texte de la bulle est un texte courant, quelle que soit la phrase qui
     porte le mot : sans cela une définition posée dans un chapeau en héritait
     la couleur et la taille. */
  font-weight: 400; font-style: normal; text-align: left; white-space: normal;
}
.mot > .bulle[hidden] { display: none; }
.etiquette-fiabilite {
  display: inline-block; font-size: 0.78rem; letter-spacing: 0.04em;
  text-transform: uppercase; padding: 0.15rem 0.5rem; border-radius: 3px;
  background: var(--fond-appui); color: var(--texte-doux);
}
/* Graphiques : du SVG écrit à la main, dont seules les couleurs et les tailles
   de texte sont ici. Le tracé lui-même est dans `graphique()`. */
.graphique { margin: 1.3rem 0 1.7rem; position: relative; }
.graphique svg { display: block; width: 100%; height: auto; overflow: visible; }
/* La figure se parcourt au clavier : les flèches y déplacent l'année lue. Le
   contour du focus est celui de tout le site, posé sur la figure entière parce
   que c'est elle qui reçoit les touches. */
.graphique:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px;
                           border-radius: 4px; }
/* Le trait vertical de l'année lue, et les points posés sur chaque courbe. Ils
   sont dessinés par `index.html` dans le `<g class="survol">` que le tracé
   laisse vide : rien de tout cela n'est dans le HTML servi, et la page reste
   lisible sans une ligne de script. */
.graphique .survol .guide { stroke: var(--texte-doux); stroke-width: 1;
                            stroke-dasharray: 2 3; }
.graphique .survol .point { stroke: var(--fond-carte); stroke-width: 2; }
/* La lecture de l'année survolée. Elle flotte au-dessus du tracé, du côté où il
   reste de la place : `index.html` bascule `.a-droite` quand le pointeur passe
   la moitié du cadre, sans quoi la boîte sortirait de l'écran sur la fin de la
   série — c'est-à-dire là où l'on regarde le plus. */
.graphique .lecture {
  position: absolute; top: 0.2rem; left: 0; z-index: 4; pointer-events: none;
  min-width: 11rem; max-width: 19rem;
  background: var(--fond-carte); border: 1px solid var(--trait-champ);
  border-radius: 6px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 0.5rem 0.7rem; font-size: 0.85rem; line-height: 1.4;
}
.graphique .lecture[hidden] { display: none; }
.graphique .lecture.a-droite { left: auto; right: 0; }
.graphique .lecture .annee { font-weight: 600; display: block;
                             margin-bottom: 0.25rem; }
.graphique .lecture ul { list-style: none; margin: 0; padding: 0; }
/* Les libellés sont raccourcis par `index.html`, mais « Ce qui sortirait en
   comptes notionnels dès 2026 » reste long : la ligne passe à la ligne plutôt
   que de sortir de la boîte. */
.graphique .lecture li { display: flex; align-items: baseline; gap: 0.4rem;
                         margin-bottom: 0.1rem; }
.graphique .lecture .valeur { margin-left: auto; padding-left: 0.7rem;
                              white-space: nowrap;
                              font-variant-numeric: tabular-nums; }
/* L'aide qui dit que les flèches marchent. Elle n'apparaît qu'au focus clavier :
   à la souris, elle n'apprendrait rien et prendrait une ligne. */
.graphique .aide-clavier {
  font-size: 0.8rem; color: var(--texte-doux); margin: 0.3rem 0 0;
  visibility: hidden;
}
.graphique:focus-visible .aide-clavier { visibility: visible; }
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
/* Le ruban entre deux courbes : vert quand la première passe au-dessus, rouge
   quand elle passe dessous. Il est peint sous les courbes, assez pâle pour les
   laisser lisibles, assez franc pour se voir d'un coup d'œil — c'est lui qui
   dit, sans un mot, s'il rentre plus qu'il ne sort. */
.graphique .ecart { stroke: none; }
.graphique .ecart.plus { fill: var(--prospectif-employeur); opacity: 0.22; }
.graphique .ecart.moins { fill: var(--retroactif); opacity: 0.22; }
/* Ses deux pastilles de légende, accolées : une seule couleur ne dirait que la
   moitié de ce que le ruban montre. */
.pastille.ecart-plus { background: var(--prospectif-employeur); opacity: 0.45; }
.pastille.ecart-moins { background: var(--retroactif); opacity: 0.45;
                        margin-left: -0.15rem; }
.graphique .graduation {
  fill: var(--texte-doux); font-family: inherit; font-size: 12px;
  font-variant-numeric: tabular-nums;
}
/* Le tableau des points du graphique. Il se range juste sous son tracé, et non
   à la distance qui sépare deux paragraphes : c'est la même figure, dite
   autrement. Déplié, il est borné en hauteur — cent onze lignes avalent un
   écran entier —, et ses en-têtes de colonne restent visibles pendant qu'on le
   parcourt : sans cela, la colonne lue se perd dès la dixième ligne. */
.donnees-graphique { margin: -1.4rem 0 1.7rem; }
.donnees-graphique .defilant { max-height: 24rem; overflow-y: auto; }
.donnees-graphique table { font-size: 0.88rem; }
/* Lignes serrées : à l'interligne des autres tableaux, huit années tenaient
   dans la boîte, sur soixante-six. Le double y tient maintenant, ce qui est la
   différence entre consulter une série et la faire défiler. */
.donnees-graphique th, .donnees-graphique td { padding: 0.22rem 0.6rem; }
.donnees-graphique thead th {
  position: sticky; top: 0; background: var(--fond);
  box-shadow: inset 0 -1px 0 var(--trait);
}
.donnees-graphique caption { padding-bottom: 0.35rem; }
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
  /* L'intitulé reprend sa hauteur de texte. En colonne, `flex: 1 1 14rem` ne
     réserve plus une largeur mais une HAUTEUR : chaque scénario portait donc
     224 px de vide entre son titre et son montant, six fois de suite, et le
     premier chiffre de la page tombait sous la ligne de flottaison. */
  .scenario .titre { flex: 0 1 auto; max-width: 100%; }
  /* Les deux montants passent sous l'intitulé, alignés à gauche comme lui :
     côte à côte tant qu'ils tiennent, l'un sous l'autre sinon.

     Ils ne tenaient pas toujours, et la page n'avait aucun moyen de le savoir
     à l'avance : elle ignore la police que le téléphone substitue à la sienne
     — aucun des empattements demandés n'existe sur Android, et le serif de
     remplacement est plus large —, comme elle ignore le grossissement du texte
     que le système applique par-dessus. Une somme qui ne se coupe pas dans une
     rangée qui ne se replie pas : « par mois, en euros de 2039 » sortait de la
     carte, et emportait la page entière dans un défilement horizontal.

     Trois règles le tiennent, quelle que soit la police et quel que soit le
     grossissement : les libellés se replient, les sommes jamais — un montant
     coupé en deux lignes ne se lit plus —, et la rangée passe à la ligne quand
     même cela ne suffit pas. */
  .scenario .montant { justify-content: flex-start; flex-wrap: wrap;
                       column-gap: 0.9rem; row-gap: 0.3rem; max-width: 100%; }
  .scenario .chiffre { align-items: flex-start; white-space: normal;
                       min-width: 0; max-width: 100%; }
  .scenario .chiffre .somme, .scenario .chiffre .annuel { white-space: nowrap; }
  /* Le trait qui sépare les deux montants ne sépare plus rien dès qu'ils
     passent l'un sous l'autre, et aucun sélecteur ne dit qu'une rangée s'est
     repliée : il ne s'affiche donc sur aucun téléphone. Les deux libellés
     disent lequel est lequel, et la taille dit lequel prime. */
  .scenario .depart { padding-left: 0; border-left: none; }
  /* Les tableaux du détail portent jusqu'à six colonnes, et un téléphone leur
     donne 358 points : chaque cellule y tombait sur trois lignes de deux mots.
     Un demi-point de moins et des marges plus serrées leur rendent un
     cinquième de leur hauteur, et font tenir une colonne de plus avant que la
     zone ne défile. */
  table { font-size: 0.88rem; }
  th, td { padding: 0.4rem 0.45rem; }
  /* Le retrait d'une section repliée coûte 26 points de largeur à ce qu'elle
     contient : de quoi couper une colonne de chiffres. Il reste marqué, en
     tenant sur le quart de la place. */
  details.section > .dedans { padding-left: 0.6rem; }
  .fiches { grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr)); }
  /* Les trois chiffres d'ouverture se mettent les uns sous les autres plutôt
     que de se serrer à trois de front : à 8 rem de large, « 422 Md € » se
     coupait en deux. */
  .fiches.reperes { grid-template-columns: 1fr; }
  .fiches.reperes .fiche .valeur { font-size: 1.6rem; }
  section.cle { padding: 1rem 1rem 0.8rem; }
  /* La bulle du glossaire quitte le fil du texte et se pose en bas de l'écran,
     sur toute la largeur. Deux raisons. Une boîte flottante ancrée sur un mot
     qui peut se trouver au bord de l'écran en déborderait ; et une boîte posée
     DANS le fil coupait la phrase en deux, laissant le point qui suit le mot
     orphelin sur sa propre ligne. Fixée en bas, elle ne déplace rien et reste
     dans la vue quel que soit l'endroit où l'on a touché. */
  .mot { position: static; }
  .mot > .bulle {
    position: fixed; left: 0.75rem; right: 0.75rem; bottom: 0.75rem;
    top: auto; width: auto; max-width: none; z-index: 20;
    font-size: 0.95rem; padding: 0.9rem 1rem;
  }
  form .grille { gap: 0.9rem; }
  /* Le SVG se réduit avec la page : ses textes, exprimés en unités du viewBox,
     se réduiraient d'autant et deviendraient illisibles. On les grossit donc
     dans le repère pour qu'ils gardent leur taille à l'écran. Vingt-quatre et
     non vingt : sur un écran de 375 points, le tracé est réduit de moitié, et
     vingt unités y faisaient neuf pixels — sous le plancher de lisibilité. */
  .graphique .graduation { font-size: 24px; }
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
  /* Ni la lecture au survol — il n'y a pas de pointeur sur du papier —, ni le
     bouton qui compose une image : la page imprimée EST déjà l'image. */
  .graphique .lecture, .graphique .aide-clavier, section.cle > .partage {
    display: none;
  }
  body { background: #fff; color: #000; font-size: 11pt; }
  .defilant { overflow: visible; }
  .carte, .note, table, .graphique, .scenario, section.cle { break-inside: avoid; }
  /* Le mot du glossaire s'imprime comme le reste de la phrase : ni bouton, ni
     soulignement pointillé, qui ne renverraient sur le papier à rien qu'on
     puisse ouvrir. Sa définition ne s'imprime pas : sur une page de chiffres
     elle ferait une incise de trois lignes au milieu d'un paragraphe. */
  .mot > .terme { border-bottom: none; }
  .mot > .bulle { display: none; }
  a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.85em; }
}
"""

DEPOT = "https://github.com/g-pliberal/retraitecomptenotionelle"

#: Ce qui signe une carte exportée en image. Une image quittant le site n'a plus
#: ni barre d'adresse ni pied de page : sans ces deux lignes, elle circule sans
#: dire d'où elle vient ni qui l'a produite, et le premier qui la republie en
#: devient la source.
SIGNATURE = "@pliberal"
SIGNATURE_SITE = "Parti libéral français — le simulateur de retraite"

LIENS = (
    ("/", "Programme"),
    ("/simuler", "Simuler"),
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
  <h1><a href="{lien('/')}">{icone('trending-up')}<span>Retraite à comptes notionnels</span></a></h1>
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
  d'aucune caisse et ne vaut ni relevé de carrière, ni estimation de vos droits.
  Seule votre caisse fait foi
  (<a href="https://www.info-retraite.fr/">info-retraite.fr</a>).</p>
  <p>Modèle ouvert, code et données sur <a href="{DEPOT}">GitHub</a> (code sous licence
  Apache 2.0, infographies et textes sous
  <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr">CC BY-SA 4.0</a>).
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
          type_: str = "text", complement: str = "", **attributs: str) -> str:
    """Un champ, son libellé, son aide courte et, s'il en faut, sa bulle.

    ``aide`` tient en une ligne sous le libellé : c'est ce qu'il faut savoir
    pour remplir le champ. ``complement`` est tout le reste — la raison, la
    nuance, la source —, qui s'ouvre sous un point d'interrogation.
    """
    supplement = "".join(
        f' {cle.rstrip("_").replace("_", "-")}="{escape(str(val))}"'
        for cle, val in attributs.items()
    )
    aide_html = f'<span class="aide">{escape(aide)}</span>' if aide else ""
    appel = bulle(f"{libelle} : en savoir plus", complement) if complement else ""
    return (
        f'<div><label for="{nom}">{escape(libelle)}{appel}{aide_html}</label>'
        f'<input type="{type_}" id="{nom}" name="{nom}" '
        f'value="{escape(str(valeur))}"{supplement}></div>'
    )


def champ_date(nom: str, libelle: str, valeur: str, aide: str = "",
               calcul: str = "", complement: str = "", **attributs: str) -> str:
    """Une date, saisie au calendrier du navigateur.

    ``type="date"`` et non ``type="month"`` : le modèle ne descend pas sous le
    mois, et « month » serait donc le champ juste — mais Firefox et Safari ne
    savent pas l'ouvrir, ils le rendent en texte brut où il faut écrire
    « 1975-03 » à la main. « date » ouvre le même calendrier partout, et le
    navigateur l'écrit dans la langue du lecteur : « 15/03/1975 » ici.

    Le jour ne sert à rien au calcul, qui compte en mois : celui de la
    naissance est gardé tel qu'il est saisi, parce qu'une date de naissance
    est une date et non un mois ; ceux des dates de carrière sont ramenés au
    premier du mois, où le droit place toute prise d'effet.

    ``calcul`` est ce que la date vaut en âge — « soit 64 ans et 7 mois » : ce
    que disaient les champs d'âge qu'elle remplace. Il est écrit au rendu et
    refait à chaque frappe par le script de la page ; ``aria-describedby`` le
    rattache au champ, faute de quoi il ne serait lu par personne.
    """
    supplement = "".join(
        f' {cle.rstrip("_").replace("_", "-")}="{escape(str(val))}"'
        for cle, val in attributs.items()
    )
    aide_html = f'<span class="aide">{escape(aide)}</span>' if aide else ""
    appel = bulle(f"{libelle} : en savoir plus", complement) if complement else ""
    decrit = f' aria-describedby="{nom}-calcul"' if calcul else ""
    calcul_html = (
        f'<span class="calcul" id="{nom}-calcul" aria-live="polite">'
        f"{escape(calcul)}</span>" if calcul else ""
    )
    return (
        f'<div><label for="{nom}">{escape(libelle)}{appel}{aide_html}</label>'
        f'<input type="date" id="{nom}" name="{nom}" '
        f'value="{escape(str(valeur))}"{decrit}{supplement}>{calcul_html}</div>'
    )


def zone(nom: str, libelle: str, valeur: str, aide: str = "",
         lignes: int = 8, **attributs: str) -> str:
    """Un champ de plusieurs lignes — le relevé de carrière, et lui seul.

    Une ligne par année : un ``<input>`` en donnerait une seule, où le relevé
    se replierait en un ruban illisible. Le contenu est ÉCHAPPÉ comme partout
    ailleurs, et posé sans espace autour : un ``<textarea>`` rend tout ce qu'il
    contient, jusqu'au retour à la ligne qui suivrait la balise ouvrante.
    """
    supplement = "".join(
        f' {cle.rstrip("_").replace("_", "-")}="{escape(str(val))}"'
        for cle, val in attributs.items()
    )
    aide_html = f'<span class="aide">{escape(aide)}</span>' if aide else ""
    return (
        f'<div><label for="{nom}">{escape(libelle)}{aide_html}</label>'
        f'<textarea id="{nom}" name="{nom}" rows="{lignes}"{supplement}>'
        f'{escape(str(valeur))}</textarea></div>'
    )


def cache(nom: str, valeur: str) -> str:
    """Un champ que le formulaire porte sans le montrer.

    Sert à ce que le formulaire renvoie un réglage qui ne se change pas dans le
    formulaire mais par un lien — l'unité de saisie des salaires : la changer
    convertit les montants, ce qu'un menu HTML ne sait pas faire.
    """
    return f'<input type="hidden" name="{nom}" value="{escape(str(valeur))}">'


def liste(nom: str, libelle: str, options: list[tuple],
          selection: str, aide: str = "", complement: str = "",
          **attributs: str) -> str:
    """Un menu déroulant.

    Une option est ``(code, texte)``, ou ``(code, texte, disponible)``, ou
    ``(code, texte, disponible, attributs)``. Une option indisponible est
    rendue ``disabled`` — grisée, et impossible à choisir — SAUF si elle est
    la sélection : un navigateur n'envoie pas la valeur d'une option choisie
    mais désactivée, et la saisie repartirait sur le statut par défaut sans
    que rien ne le dise. Le refus, lui, se fait au calcul.
    """
    supplement = "".join(
        f' {cle.rstrip("_").replace("_", "-")}="{escape(str(val))}"'
        for cle, val in attributs.items()
    )
    choix = []
    for option in options:
        code, texte = option[0], option[1]
        disponible = option[2] if len(option) > 2 else True
        propres = "".join(
            f' {cle}="{escape(str(val))}"'
            for cle, val in (option[3] if len(option) > 3 else {}).items()
        )
        choix.append(
            f'<option value="{escape(code)}"'
            + (" selected" if code == selection else "")
            + ("" if disponible or code == selection else " disabled")
            + propres
            + f">{escape(texte)}</option>"
        )
    choix = "".join(choix)
    aide_html = f'<span class="aide">{escape(aide)}</span>' if aide else ""
    appel = bulle(f"{libelle} : en savoir plus", complement) if complement else ""
    return (
        f'<div><label for="{nom}">{escape(libelle)}{appel}{aide_html}</label>'
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


def fiche(etiquette: str, valeur: str, precision: str = "") -> str:
    """Un chiffre, ce qu'il mesure, et au besoin la phrase qui le situe.

    ``precision`` est du HTML : elle porte parfois un lien ou un mot du
    glossaire. Elle est facultative, et l'immense majorité des fiches du site
    s'en passent — elle n'existe que pour les trois chiffres d'ouverture de la
    page Coût, où « 422 milliards » ne veut rien dire tant qu'on n'a pas dit
    « en un an, pour 17 millions de retraités ».
    """
    suite = f'<div class="precision">{precision}</div>' if precision else ""
    return (
        f'<div class="fiche"><div class="valeur">{valeur}</div>'
        f'<div class="etiquette">{escape(etiquette)}</div>{suite}</div>'
    )


#: Les pictogrammes du site, et rien qu'eux.
#:
#: Ils viennent tous de Lucide 1.46.0, sous licence ISC : une seule grille —
#: 24 × 24, trait de 2, extrémités et jointures arrondies —, si bien qu'ils
#: tiennent ensemble à toutes les tailles. Le site n'affichait jusque-là aucun
#: dessin : un emoji en guise d'icône de page, un chevron tracé à coups de
#: bordures CSS, le triangle que chaque navigateur donne à ses ``<details>``, un
#: point d'interrogation en caractère. Trois dessins, trois grilles, trois
#: épaisseurs, et un emoji dont le rendu change avec le système.
#:
#: Le tracé est écrit ICI, et non chargé : le portage JavaScript n'utilise
#: aucune bibliothèque, et la page ne demande aucune ressource tierce — c'est
#: ce que les mentions légales promettent. Les originaux sont recopiés sans
#: retouche dans ``moteur/icones/``, et un test vérifie que cette table dit
#: exactement ce qu'ils disent, des deux côtés du portage.
#:
#: Les clés sont les noms de Lucide, en anglais comme les fichiers : c'est ce
#: qui permet de retrouver l'original d'un coup d'œil, et au test de l'ouvrir.
ICONES = {
    "chevron-down": '<path d="m6 9 6 6 6-6" />',
    "circle-help": '<circle cx="12" cy="12" r="10" />'
                   '<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />'
                   '<path d="M12 17h.01" />',
    "download": '<path d="M12 15V3" />'
                '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />'
                '<path d="m7 10 5 5 5-5" />',
    "trending-up": '<path d="M16 7h6v6" /><path d="m22 7-8.5 8.5-5-5L2 17" />',
    "triangle-alert":
        '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 '
        '0 0 0 1.73-3" /><path d="M12 9v4" /><path d="M12 17h.01" />',
}

#: L'enveloppe commune : c'est elle qui fait la grille, et elle ne varie pas
#: d'un pictogramme à l'autre. ``currentColor`` les met à la couleur du texte
#: qui les porte, et ``1em`` à sa taille : un pictogramme suit son voisin.
ENVELOPPE_ICONE = (
    'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"'
)


def icone(nom: str, titre: str = "") -> str:
    """Un pictogramme de la bibliothèque, écrit dans la page.

    Sans ``titre``, il est DÉCORATIF : le texte à côté dit déjà ce qu'il dit, et
    le répéter ferait entendre deux fois la même chose à une synthèse vocale.
    Avec ``titre``, il porte à lui seul une information — un avertissement, un
    état — et devient une image nommée.
    """
    if nom not in ICONES:
        raise KeyError(f"pictogramme inconnu : {nom}")
    if titre:
        return (f'<svg class="icone" {ENVELOPPE_ICONE} role="img">'
                f"<title>{escape(titre)}</title>{ICONES[nom]}</svg>")
    return (f'<svg class="icone" {ENVELOPPE_ICONE} aria-hidden="true" '
            f'focusable="false">{ICONES[nom]}</svg>')


def sommaire(texte: str) -> str:
    """Le résumé d'un dépliant, chevron compris.

    Tous les dépliants du site passent par ici : c'est ce qui leur donne le même
    chevron, au même endroit, tournant dans le même sens. Le marqueur du
    navigateur est masqué en CSS — il n'a pas deux fois la même forme sur deux
    moteurs, et aucune taille commune avec le reste.
    """
    return f"<summary>{icone('chevron-down')}<span>{texte}</span></summary>"


def mot(terme: str, definition: str) -> str:
    """Un mot de jargon, et sa définition dépliable sur place.

    Le site s'adresse à des gens qui n'ont pas fait d'économie. « Part du PIB »,
    « cotisation », « répartition » sont pour eux des mots opaques, et les
    définir dans le corps du texte l'allonge d'autant pour tous les autres. La
    définition est donc posée SOUS le mot, et ne s'ouvre que si on la demande.

    Ce n'est PAS un attribut ``title`` : une infobulle de survol ne s'ouvre ni
    au clavier, ni au doigt, ni sous une synthèse vocale, et un test du dépôt
    l'interdit d'ailleurs sur tout le site.

    Ce n'est pas non plus un ``<details>``, et il a fallu s'y reprendre à deux
    fois pour le comprendre : ``<details>`` fait partie des balises dont
    l'analyseur HTML FERME un ``<p>`` ouvert. Un mot du glossaire posé au milieu
    d'une phrase coupait donc le paragraphe en deux, et la fin de la phrase
    tombait à la ligne, hors du paragraphe. Un ``<button>`` est du contenu de
    phrase : il ne ferme rien, et il porte en plus le bon état — ``aria-expanded``
    dit si la définition est ouverte, ce qu'un dépliant bricolé ne dirait pas.
    Le basculement est dans ``index.html``, en écoute déléguée : le contenu de
    la page est remplacé en bloc à chaque rendu, et un écouteur posé sur chaque
    mot disparaîtrait avec lui.
    """
    return (
        f'<span class="mot"><button type="button" class="terme" '
        f'aria-expanded="false">{escape(terme)}</button>'
        f'<span class="bulle" role="note" hidden>{escape(definition)}</span></span>'
    )


def bulle(sujet: str, texte: str) -> str:
    """Un complément d'information, sous un point d'interrogation.

    Même mécanique que :func:`mot` — un bouton, une bulle, le basculement en
    écoute déléguée dans ``index.html`` —, mais l'ancre n'est pas un mot de la
    phrase : c'est un appel, posé après un titre ou un libellé de champ. Ce qui
    est nécessaire pour remplir un champ ou lire un chiffre reste écrit ; ce qui
    explique, nuance ou justifie tient ici, et ne s'ouvre que si on le demande.

    ``sujet`` nomme le bouton pour qui ne voit pas le point d'interrogation :
    c'est son seul nom accessible. ``texte`` est du HTML, mais du HTML de
    PHRASE — la bulle est un ``<span>``, où un ``<p>`` ne serait pas valide.
    """
    return (
        f'<span class="mot"><button type="button" class="terme appel" '
        f'aria-expanded="false" aria-label="{escape(sujet)}">'
        f"{icone('circle-help')}</button>"
        f'<span class="bulle" role="note" hidden>{texte}</span></span>'
    )


def points(entrees: list[tuple[str, str]]) -> str:
    """Quelques idées, une par bloc, titre puis phrase.

    C'est la forme que prend une proposition quand elle doit se lire en dix
    secondes : quatre blocs de deux lignes, tous de même poids, à côté les uns
    des autres. Une liste à puces dirait la même chose, mais elle se lit de haut
    en bas et donne au premier point une importance que les autres n'ont pas.

    Les titres sont de vrais ``<h3>``, et non des paragraphes en gras : c'est par
    eux qu'une synthèse vocale parcourt une page, et quatre propositions qui
    n'apparaîtraient pas dans ce plan seraient, pour elle, quatre paragraphes de
    plus. ``texte`` est du HTML — il porte des mots du glossaire et des liens.
    """
    if not entrees:
        return ""
    corps = "".join(
        f'<div class="point"><h3>{escape(titre)}</h3><p>{texte}</p></div>'
        for titre, texte in entrees
    )
    return f'<div class="points">{corps}</div>'


def depliant(titre: str, corps: str) -> str:
    """Une section repliée : son titre se lit, son contenu s'ouvre si on veut.

    Le temps du lecteur n'est pas gratuit. Tout ce qu'une page doit pouvoir
    justifier — le détail d'un tableau, le périmètre d'une source, ce que le
    calcul ne sait pas faire — doit être là, sans quoi la page n'est pas
    honnête ; mais rien n'oblige à le lui faire traverser pour atteindre le
    résultat. Un dépliant met les deux exigences d'accord : le titre annonce ce
    qu'il y a dedans, et c'est le lecteur qui décide.
    """
    return (
        f'<details class="section">{sommaire(escape(titre))}'
        f'<div class="dedans">{corps}</div></details>'
    )


def cle(question: str, reponse: str, corps: str, source: str = "") -> str:
    """Une question, sa réponse en une phrase, et l'image qui la montre.

    C'est l'unité de lecture de la page Coût, et elle est faite pour deux
    lecteurs à la fois. Celui qui n'a pas le temps lit la question et la
    réponse, et s'arrête là : deux lignes lui ont donné le résultat. Celui qui
    veut voir descend d'un cran et trouve le tracé, puis ses chiffres.

    La carte est encadrée pour une troisième raison : elle doit se découper.
    Une capture d'écran de ce bloc porte la question, la réponse, le graphique
    et sa source — elle se comprend hors du site, ce qu'un graphique nu ne fait
    jamais.

    ``reponse`` et ``source`` sont du HTML : elles portent des mises en
    évidence, des liens et des mots du glossaire. ``question`` est du texte.
    """
    fin = f'<p class="source">{source}</p>' if source else ""
    # Le bouton n'est pas un ornement : c'est lui qui fait de la carte autre
    # chose qu'un bloc de page. Il compose, dans le navigateur, une image qui
    # porte la question, la réponse, le tracé, sa source et la signature du
    # compte — et rien d'autre à faire pour la poster. Le comportement est dans
    # `index.html`, en écoute déléguée ; sans lui, le bouton ne ferait rien, et
    # c'est pourquoi un test tient l'accord entre les deux.
    #
    # Il n'apparaît que si la carte porte un TRACÉ : c'est lui que l'image
    # compose, et une carte qui n'en a pas — celle qui porte un tableau, ou une
    # liste — donnerait un bouton qui échoue. Le savoir se lit dans le corps de
    # la carte plutôt que de se déclarer en paramètre : un appelant n'a pas à
    # redire ce que son propre contenu dit déjà.
    partage = (
        '<p class="partage"><button type="button" class="partager">'
        f"{icone('download')}<span>Télécharger l'image</span></button></p>"
        if '<figure class="graphique"' in corps else ""
    )
    return (
        f'<section class="cle"><h3>{escape(question)}</h3>'
        f'<p class="reponse">{reponse}</p>{corps}{fin}{partage}</section>'
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

#: Pas admissibles de l'axe des abscisses, du plus fin au plus large. Ce sont
#: des durées qu'un lecteur reconnaît : on gradue de dix ans en dix ans, ou de
#: vingt, jamais de treize.
PAS_GRADUATIONS_X = (10, 20, 25, 50, 100)

#: Au-delà, les étiquettes se chevauchent sur un écran de téléphone, où le tracé
#: est réduit de moitié et ses textes grossis pour rester lisibles. Huit : c'est
#: ce que porte une plage de soixante-six ans graduée par décennies, celle qui
#: tenait déjà.
GRADUATIONS_X_MAXIMUM = 8

#: Écart minimal, en années, entre une décennie graduée et une borne de l'axe.
#: Les bornes sont graduées d'office — ce sont elles qui datent la série —, et
#: une décennie trop proche de l'une d'elles ne fait que chevaucher son
#: étiquette. Six ans : « 2020 » et « 2024 » ne tiennent pas côte à côte sur
#: l'écran d'un téléphone, où les textes du repère sont grossis.
ECART_MINIMAL_GRADUATIONS = 6

#: Écart vertical minimal, en unités du repère, entre deux étiquettes posées au
#: bout des courbes. Les couleurs des six scénarios ne suffisent pas à les
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
    """Graduations rondes comprises dans la plage, plus les deux bornes.

    La décennie est le pas naturel, et il suffit tant que la plage est courte.
    Cent onze ans en donneraient douze, plus les deux bornes : sur l'écran d'un
    téléphone, où le tracé est réduit de moitié et ses textes grossis d'autant,
    les étiquettes se chevauchent. Le pas s'élargit donc jusqu'à ce que le
    compte tienne, en s'arrêtant à des valeurs qu'un lecteur reconnaît — vingt,
    vingt-cinq, cinquante ans —, jamais à un pas calculé qui tomberait sur 1963
    et 1994.
    """
    pas = next(
        (candidat for candidat in PAS_GRADUATIONS_X
         if sum(1 for a in range(premiere, derniere + 1) if a % candidat == 0)
         <= GRADUATIONS_X_MAXIMUM),
        PAS_GRADUATIONS_X[-1],
    )
    annees = [a for a in range(premiere, derniere + 1) if a % pas == 0]
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


def _aires_ecart(haute: Serie, basse: Serie, annees: tuple[int, ...],
                 sommet: float) -> str:
    """Le ruban entre deux courbes, coloré selon celle qui est au-dessus.

    C'est ce qui fait qu'un graphique de ressources et de dépenses se lit sans
    savoir lire un graphique : l'écart entre les deux courbes n'est plus à
    mesurer à l'œil, il est peint. Vert quand il rentre plus qu'il ne sort,
    rouge quand c'est l'inverse.

    Le ruban change donc de couleur en cours de route, et il change de couleur
    À L'ENDROIT EXACT où les courbes se croisent — pas à l'année suivante. Le
    croisement est interpolé linéairement sur le segment, exactement comme le
    tracé lui-même interpole entre deux points, si bien que le changement de
    teinte tombe sur l'intersection dessinée. Les segments de même signe qui se
    suivent forment un seul polygone : sans ce regroupement, soixante-neuf
    quadrilatères se toucheraient bord à bord et leurs jointures se verraient.

    Deux séries peuvent ne pas couvrir la même plage — le graphique de tête en
    porte une qui remonte à 1959 et deux qui commencent en 2002. Le ruban se
    peint alors sur la SEULE PLAGE CONTINUE où les deux sont définies, et il se
    tait si l'une d'elles a un trou À L'INTÉRIEUR de cette plage : un ruban
    interpolé par-dessus une année manquante affirmerait un écart que personne
    n'a mesuré.
    """
    if len(haute.valeurs) != len(annees) or len(basse.valeurs) != len(annees):
        return ""
    communs = [rang for rang in range(len(annees))
               if haute.valeurs[rang] is not None and basse.valeurs[rang] is not None]
    if len(communs) < 2:
        return ""
    if communs != list(range(communs[0], communs[-1] + 1)):
        return ""
    # Les abscisses restent celles du graphique ENTIER : c'est le cadre qui les
    # fixe, pas la plage du ruban. Ses bornes sont donc retenues avant que la
    # plage ne soit restreinte.
    premiere, derniere = annees[0], annees[-1]
    annees = tuple(annees[rang] for rang in communs)
    hautes = [haute.valeurs[rang] for rang in communs]
    basses = [basse.valeurs[rang] for rang in communs]

    def point(annee: int, dessus: float, dessous: float) -> tuple[float, float, float]:
        return (_abscisse(annee, premiere, derniere),
                _ordonnee(dessus, sommet), _ordonnee(dessous, sommet))

    # La chaîne des sommets du ruban : les années, plus les croisements qui
    # tombent entre deux d'entre elles. `signes` porte le signe de l'écart sur
    # chaque intervalle, et compte donc un élément de moins.
    chaine = [point(annees[0], hautes[0], basses[0])]
    signes: list[int] = []
    for rang in range(1, len(annees)):
        avant = hautes[rang - 1] - basses[rang - 1]
        apres = hautes[rang] - basses[rang]
        courant = point(annees[rang], hautes[rang], basses[rang])
        if avant * apres < 0.0:
            part = avant / (avant - apres)
            precedent = chaine[-1]
            croisement = (
                precedent[0] + part * (courant[0] - precedent[0]),
                precedent[1] + part * (courant[1] - precedent[1]),
                precedent[2] + part * (courant[2] - precedent[2]),
            )
            # Au croisement les deux courbes se touchent : le ruban y est
            # d'épaisseur nulle, et ses deux bords doivent porter la MÊME
            # ordonnée. L'interpolation des deux les y amène au même point à
            # l'arrondi près ; on impose le dessus aux deux pour que le
            # polygone se referme exactement.
            chaine.append((croisement[0], croisement[1], croisement[1]))
            signes.append(1 if avant > 0.0 else -1)
            chaine.append(courant)
            signes.append(1 if apres > 0.0 else -1)
            continue
        chaine.append(courant)
        somme = avant + apres
        signes.append(1 if somme > 0.0 else (-1 if somme < 0.0 else 0))

    morceaux = []
    debut = 0
    while debut < len(signes):
        fin = debut
        while fin + 1 < len(signes) and signes[fin + 1] == signes[debut]:
            fin += 1
        if signes[debut] != 0:
            bornes = chaine[debut:fin + 2]
            aller = " ".join(
                f"{'M' if rang == 0 else 'L'}{nombre_brut(x)} {nombre_brut(dessus)}"
                for rang, (x, dessus, _) in enumerate(bornes)
            )
            retour = " ".join(
                f"L{nombre_brut(x)} {nombre_brut(dessous)}"
                for x, _, dessous in reversed(bornes)
            )
            teinte = "plus" if signes[debut] > 0 else "moins"
            morceaux.append(
                f'<path class="ecart {teinte}" d="{aller} {retour} Z"/>'
            )
        debut = fin + 1
    return "".join(morceaux)


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
    sépare pas les six scénarios. Les étiquettes sont écartées les unes des
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
              etiquettes: tuple[str, ...] = (),
              nom_abscisse: str = "Année",
              ecart: tuple[int, int] | None = None,
              libelle_ecart: str = "",
              decimales_donnees: int | None = None) -> str:
    """Graphique en courbes, ou en bandes empilées si ``empile``.

    ``titre`` n'est pas affiché : il est le texte alternatif du SVG, c'est-à-dire
    ce que lit une synthèse vocale. Ce que voit l'œil est dans la légende et
    dans la phrase qui précède le graphique.

    ``repere`` marque une année d'un trait vertical. Il sert à dire où
    l'observation s'arrête et où la projection commence — une frontière qu'un
    graphique doit montrer, faute de quoi il donne à une hypothèse l'apparence
    d'une mesure.

    ``nom_abscisse`` nomme ce que porte l'axe horizontal — une année, sauf pour
    la trajectoire d'un retraité, qui se lit en âges. Ce nom sert au tableau de
    données : une colonne intitulée « Année » pour une suite d'âges serait un
    contresens, et c'est la seule chose que le tracé ne dit pas de lui-même.

    ``decimales_donnees`` sépare la précision des CHIFFRES de celle de l'AXE.
    Elles n'ont pas le même travail : l'axe gradue, et cinq nombres ronds s'y
    lisent mieux que cinq nombres à virgule ; les chiffres, eux, sont ce qu'on
    vient chercher quand on survole une année, et un axe qui monte à 20 ne doit
    pas faire lire « 14 » là où la série dit 14,1 — c'est justement l'écart
    entre deux courbes qui se perdrait. Sans elle, les deux précisions restent
    liées, comme partout ailleurs sur le site.

    ``ecart`` désigne deux séries par leur rang et peint le ruban qui les
    sépare : vert là où la première passe au-dessus de la seconde, rouge là où
    elle passe dessous. C'est ce qui rend lisible, sans savoir lire un
    graphique, la seule chose qui compte entre des recettes et des dépenses —
    laquelle des deux l'emporte, et de combien. ``libelle_ecart`` en dit un mot
    dans la légende, faute de quoi la couleur serait seule à porter le sens.
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
    # Le ruban d'abord : il est un fond, et une courbe posée par-dessus reste
    # visible là où les deux se croisent.
    if ecart is not None and len(series) > max(ecart):
        traces.append(_aires_ecart(series[ecart[0]], series[ecart[1]],
                                   annees, sommet))
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
    legende_html = _legende(series, libelle_ecart) if legende else ""
    etiquettes_html = (
        _etiquettes_de_fin(series, annees, sommet, etiquettes) if etiquettes else ""
    )
    # Ce dont la lecture au survol a besoin, et rien de plus.
    #
    # `data-gauche` et `data-droite` sont les abscisses du premier et du dernier
    # point, en unités du repère : de quoi retrouver, d'une position de pointeur,
    # le rang de l'année visée. Les VALEURS, elles, ne sont pas redites ici —
    # elles sont déjà dans le tableau de points que `donnees_du_graphique` pose
    # juste dessous, mises en forme exactement comme la page les écrit. Les
    # réécrire en attribut ferait deux vérités là où il en faut une, et les
    # flottants de Python et de JavaScript ne s'écrivent pas pareil.
    #
    # La figure est focusable et porte un `role="group"` : les flèches y
    # parcourent les années, ce qu'une image ne saurait pas faire. La lecture
    # sort dans une région `aria-live`, faute de quoi elle ne serait qu'un
    # dessin de plus.
    return (
        f'<figure class="graphique" tabindex="0" role="group" '
        f'aria-label="{escape(titre)}" '
        f'data-gauche="{gauche}" data-droite="{droite}">'
        f'<svg viewBox="0 0 {LARGEUR_TRACE} {HAUTEUR_TRACE}" role="img" '
        f'aria-label="{escape(titre)}">'
        f"{''.join(lignes)}{''.join(traces)}"
        f'<line class="axe" x1="{gauche}" y1="{base}" x2="{droite}" y2="{base}"/>'
        f"{repere_html}{unite_html}{etiquettes_html}"
        f'<g class="survol"></g></svg>'
        f'<div class="lecture" role="status" aria-live="polite" hidden></div>'
        f"{legende_html}"
        '<p class="aide-clavier">Flèches gauche et droite : parcourir les '
        "années. Échap : quitter.</p></figure>"
        + donnees_du_graphique(
            titre, annees, series, unite,
            decimales if decimales_donnees is None else decimales_donnees,
            nom_abscisse)
    )


def donnees_du_graphique(titre: str, annees: tuple[int, ...],
                         series: tuple[Serie, ...], unite: str = "",
                         decimales: int = 0, nom_abscisse: str = "Année") -> str:
    """Les chiffres du graphique, année par année.

    Un tracé est une image : ce que dit son ``aria-label`` — de quoi il parle,
    sur quelle plage — ne remplace pas ce qu'il montre. Le RGAA demande pour une
    image complexe une description détaillée ; pour une courbe, la description
    détaillée EST le tableau de ses points.

    Il est produit ici, dans la fonction qui trace, et à partir des mêmes séries
    : aucun graphique ne peut être livré sans ses chiffres, et le tableau ne
    peut pas s'écarter de la courbe. Les valeurs sont celles de chaque série,
    non le cumul, y compris pour un graphique en bandes empilées — c'est ce
    qu'on lit dans une colonne, et le cumul s'additionne de tête.

    Replié, parce que cent onze lignes couperaient la page en deux. Dépliable,
    parce que c'est ce qui rend le graphique lisible sans le voir — et parce
    qu'un lecteur qui veut le chiffre exact d'une année le trouve là, et nulle
    part ailleurs.
    """
    if not annees or not series:
        return ""
    en_tete = escape(unite) if unite else ""
    entetes = [nom_abscisse] + [
        serie.libelle + (f" ({en_tete})" if en_tete else "") for serie in series
    ]
    lignes = [
        [str(annee)] + [
            nombre(serie.valeurs[rang], decimales)
            if rang < len(serie.valeurs) and serie.valeurs[rang] is not None
            else "—"
            for serie in series
        ]
        for rang, annee in enumerate(annees)
    ]
    grille = tableau(
        entetes, lignes, [""] + ["nombre" for _ in series],
        titre=titre, entete_de_ligne=True,
    )
    pas = nom_abscisse.lower()
    return (
        '<details class="donnees-graphique">'
        + sommaire(f"Les chiffres de ce graphique, {pas} par {pas} "
                   f"({len(annees)} lignes)")
        + f"{grille}</details>"
    )


def _legende(series: tuple[Serie, ...], libelle_ecart: str = "") -> str:
    """Légende du graphique, posée en ``<figcaption>``.

    Ce n'est pas un ornement : le SVG est annoncé comme une image, et la légende
    est la seule chose qui dise, en texte, ce que chaque couleur représente.
    Dans la figure, elle en devient le nom accessible ; hors d'elle, elle
    n'était qu'une liste flottant sous un dessin.

    Le ruban d'écart y prend une entrée de plus, à deux pastilles : sans elle,
    le rouge et le vert du fond ne voudraient rien dire pour qui ne les a pas
    devinés.
    """
    entrees = "".join(
        f'<li><span class="pastille" style="background:{serie.couleur}"></span>'
        f"<span>{escape(serie.libelle)}"
        + (f' <span class="discret">{escape(serie.glose)}</span>' if serie.glose else "")
        + "</span></li>"
        for serie in series
    )
    if libelle_ecart:
        entrees += (
            '<li><span class="pastille ecart-plus"></span>'
            '<span class="pastille ecart-moins"></span>'
            f"<span>{escape(libelle_ecart)}</span></li>"
        )
    return f'<figcaption><ul class="legende">{entrees}</ul></figcaption>'
