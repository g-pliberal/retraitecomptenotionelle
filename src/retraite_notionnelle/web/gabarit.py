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
/* La page est un outil du site partiliberalfrancais.fr, servi sous /retraite/.
   Elle ne charge rien de ce site — ni feuille, ni police, ni script — et ne lui
   ressemble plus : c'est une RUPTURE assumée, décidée en septembre 2026. Le
   site parent est bleu-vert clair et sage ; celui-ci est une affiche politique
   — fond vert profond, titres massifs en capitales, or pour ce qui compte,
   crème pour ce qu'on doit lire de près. La raison est dans ce que la page
   doit faire : un programme se retient, et un tableau de bord ne se retient
   pas. Les variables ci-dessous sont le seul point de contact : un hôte qui
   voudrait ajuster une couleur les redéfinit dans une feuille chargée après
   celle-ci, et n'a besoin de connaître ni un sélecteur, ni un fichier. Leurs
   noms sont donc stables, et ceux d'avant la refonte ont été conservés même
   quand leur valeur a changé du tout au tout. */

/* Les deux polices de l'affiche, servies par le dépôt et non par un tiers.
   Les charger chez Google aurait coûté la seule promesse que cette page fait
   à qui la remplit — « tout se calcule dans votre navigateur, rien n'est
   envoyé » —, puisqu'une requête de police emporte l'adresse IP du lecteur.
   Elles sont donc dans `moteur/polices/`, sous licence OFL, avec les deux
   sous-ensembles dont le français a besoin : `latin` pour l'essentiel,
   `latin-ext` pour les œ, les ÿ et les guillemets qu'il traîne. Voir
   `moteur/polices/README.md`.

   `font-display: swap` : le texte s'affiche tout de suite dans la pile du
   système, et se recompose quand la police arrive. Un titre invisible pendant
   trois secondes sur un réseau lent serait pire que le même titre dans une
   autre police. */
@font-face {
  font-family: "Public Sans"; font-style: normal; font-weight: 100 900;
  font-display: swap; src: url(polices/public-sans-latin.woff2) format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA,
    U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193,
    U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: "Public Sans"; font-style: normal; font-weight: 100 900;
  font-display: swap; src: url(polices/public-sans-latin-ext.woff2) format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF,
    U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020,
    U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
}
@font-face {
  font-family: "Instrument Serif"; font-style: normal; font-weight: 400;
  font-display: swap; src: url(polices/instrument-serif-latin.woff2) format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA,
    U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193,
    U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: "Instrument Serif"; font-style: normal; font-weight: 400;
  font-display: swap; src: url(polices/instrument-serif-latin-ext.woff2) format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF,
    U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020,
    U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
}

:root {
  /* Un seul thème, et c'est voulu. L'affiche EST l'identité : la décliner en
     clair donnerait deux sites qui ne disent pas la même chose, et le vert
     profond n'est pas un habit de nuit qu'on quitte le matin. `color-scheme`
     est donc figé sur `dark`, ce qui donne aussi aux champs, aux menus
     déroulants et aux barres de défilement du navigateur le rendu sombre qui
     va avec — sans quoi un `<select>` s'ouvrirait en blanc au milieu. */
  color-scheme: dark;
  /* Le vert profond de l'affiche, et le ton juste au-dessus qui sert à
     détacher un bloc sans introduire de couleur. */
  --fond: #0b3d3a;
  --fond-carte: #0f4a46;
  --fond-appui: #0f4a46;
  /* Le crème porte 12,9:1 sur le fond, et le crème atténué 7,1:1 : au-dessus
     du plancher de 4,5:1 même pour le petit texte, ce que la relecture
     d'accessibilité de septembre 2026 exigeait explicitement. */
  --texte: #f4efe4;
  --texte-doux: #c3d8d4;
  /* Une troisième teinte, pour les légendes et les réserves — 5,4:1, réservée
     aux textes d'au moins 15 px. */
  --texte-tres-doux: #a7c3bf;
  --trait: #2f6360;
  /* Bordure des CHAMPS, distincte du filet décoratif : un contour de champ est
     ce qui dit où l'on peut écrire, et doit donc atteindre 3:1 sur les deux
     fonds qu'il sépare (WCAG 2.1, 1.4.11). Le filet `--trait` plafonne à
     1,76:1 — c'est voulu, il ne porte aucune information —, et cette teinte
     est mesurée : 4,12:1 sur le fond, 3,44:1 sur la carte. Elle sert aussi le
     bord des boutons creux et des onglets de grille, qui sont des composants
     eux aussi. Le premier essai, #4b7d79, tombait à 2,59:1 et 2,16:1 : un
     contour qu'on devine plutôt qu'on ne le voit. */
  --trait-champ: #6fa09c;
  /* L'accent est l'or. Il tient 9,4:1 sur le fond, et porte du vert profond
     lisible sur un bouton plein — c'est le contraste inverse, 9,4:1 lui
     aussi. Il remplace le bleu-vert d'avant la refonte sans changer de nom :
     tout ce qui écrivait `var(--accent)` continue de dire « ce qui compte ». */
  --accent: #e9c53d;
  --accent-doux: #14514c;
  --or: #e9c53d;
  /* Le crème des panneaux qu'on doit lire de près — le formulaire, l'appel au
     simulateur, les cartes à publier. Une affiche entièrement sombre fatigue
     dès qu'il faut remplir six champs ; le crème dit « ici, on travaille ». */
  --creme: #f4efe4;
  --sur-creme: #0b3d3a;
  --sur-creme-doux: #2a4a47;
  --sur-creme-accent: #0b6167;
  --creme-trait: #c9c2b4;
  /* Le bandeau de tête reprend le fond de la page : la rupture est totale, il
     n'y a plus de bande d'une autre couleur en haut. Les noms restent, pour
     les feuilles qui les surchargeaient. */
  --bandeau: #0b3d3a;
  --bandeau-texte: #f4efe4;
  --bandeau-doux: #c3d8d4;
  --bandeau-vif: #e9c53d;
  /* LES QUATRE SYSTÈMES COMPARÉS, et c'est le nombre qui fait leur qualité.
     À six teintes, la séparation sous deutéranopie plafonnait à ΔE 8,6 : aucun
     choix de couleurs n'y changeait rien, six catégories ne se distinguent pas
     toutes pour un œil qui confond le rouge et le vert. À quatre, la contrainte
     se relâche d'un coup, et cette palette tient :

       * ΔE ≥ 18,6 entre toutes les paires en vision normale ;
       * ΔE ≥ 15,5 sous deutéranopie, ≥ 15,2 sous protanopie — au-dessus du
         plancher de 15, donc séparées pour tout le monde, et non plus
         seulement pour ceux qui voient les six couleurs ;
       * 4,8:1 au moins sur le vert profond, chroma ≥ 0,115 (aucune ne lit
         gris), et une bande de clarté étroite pour qu'aucune courbe ne paraisse
         plus importante qu'une autre.

     La couleur n'est pas seule pour autant — les tracés gardent leurs motifs,
     les barres leur intitulé, les écarts leur signe —, mais elle suffit
     désormais, ce qui n'était pas le cas avant.

     La proposition libérale est en or : c'est l'accent de l'affiche, et la
     seule couleur que l'œil trouve en premier. C'est fait pour. */
  --actuel: #76a2ff;
  --retroactif: #57e7fe;
  --retroactif-employeur: #e98b97;
  --liberal: #e9c53d;
  --alerte: #f0b849;
  /* Ce qui manque et ce qui reste, sur le graphique du coût. Opaques, et non
     translucides : deux aplats transparents superposés sur le vert profond
     donnaient un brun qui ne figurait dans aucune légende, et un rouge
     translucide y devenait un gris sale. Peints SOUS les courbes, ils ne
     cachent rien. */
  --manque: #e8807f;
  --reste: #8ac44a;
  /* Palette des graphiques : neuf teintes, assez distinctes pour se suivre
     empilées, assez proches pour ne pas jurer avec l'affiche. Toutes tiennent
     au moins 4,5:1 sur le vert profond. */
  --serie-1: #f4efe4;
  --serie-2: #ff852d;
  --serie-3: #61bee6;
  --serie-4: #fd84b2;
  --serie-5: #5fd3c4;
  --serie-6: #e9c53d;
  --serie-7: #2ebb6b;
  --serie-8: #d9a98c;
  --serie-9: #b7c6c3;
  /* La marge latérale, fluide : 18 px sur un téléphone, 40 px au large. Elle
     est ici parce que huit blocs s'y alignent, et qu'ils doivent s'aligner au
     pixel — le bandeau de tête, l'affiche, le bandeau crème, les engagements. */
  --marge: clamp(1.125rem, 5vw, 2.5rem);
  /* La largeur de l'affiche. Plus large que les 60 rem d'avant : un titre de
     97 px a besoin de place, et les grilles à deux colonnes aussi. Le texte
     courant, lui, reste borné par `.chapeau` et par `p` (voir plus bas) — une
     ligne de 80 rem ne se lit pas. */
  --largeur: 80rem;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--fond);
  color: var(--texte);
  font-family: "Public Sans", system-ui, -apple-system, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  /* En `rem` et non en pixels : une taille en pixels ignore la préférence de
     taille de police du navigateur, sur laquelle comptent ceux qui l'ont
     agrandie une fois pour toutes. 1,0625rem vaut les 17px d'origine quand la
     préférence n'a pas été touchée. */
  font-size: 1.0625rem;
  line-height: 1.6;
  /* La page ne déborde jamais latéralement, quoi qu'on y mette : une carte de
     1200 px à publier, un tableau de huit colonnes. Ce sont leurs cadres qui
     défilent, pas le document. */
  overflow-x: hidden;
}
main { max-width: var(--largeur); margin: 0 auto; padding: 0 var(--marge); }
/* Lien d'évitement : premier élément parcouru au clavier, invisible tant qu'il
   n'a pas le focus. Sans lui, atteindre le contenu depuis la barre d'adresse
   impose de traverser les huit onglets de l'en-tête à chaque page (WCAG 2.4.1).
   Il n'est pas caché par `display:none`, qui le sortirait de l'ordre de
   tabulation : il est simplement remonté hors de l'écran. */
.evitement {
  position: absolute; left: 0.5rem; top: -4rem; z-index: 30;
  background: var(--or); color: var(--fond);
  border: 1px solid var(--or); border-radius: 0 0 4px 4px;
  padding: 0.5rem 0.9rem; font-size: 0.92rem; font-weight: 700;
  text-decoration: none; transition: top 0.15s;
}
.evitement:focus { top: 0; }
/* `<main>` reçoit le focus au changement de page (voir index.html) : sans quoi
   le clavier repartirait du haut du document à chaque calcul. Il ne porte pas
   de contour pour autant — ce n'est pas un élément interactif, et le cerner
   tout entier n'apprendrait rien. */
main:focus { outline: none; }

/* Le bandeau : le même vert que la page, séparé par un simple filet, et collé
   en haut. Collé parce que la navigation est devenue une barre d'onglets de
   huit entrées : sur les pages longues — Coût, Données —, la reperdre au
   premier défilement obligeait à remonter de six écrans pour changer de page.
   Il porte le carré d'or et le nom du parti, puis les onglets. */
header.bandeau {
  border-bottom: 1px solid var(--trait);
  background: var(--fond);
  color: var(--bandeau-texte);
  padding: 1rem 0;
  margin-bottom: 0;
  position: sticky; top: 0; z-index: 20;
}
header.bandeau .interieur {
  max-width: var(--largeur); margin: 0 auto; padding: 0 var(--marge);
  display: flex; flex-wrap: wrap; gap: 0.75rem 1.5rem;
  align-items: center; justify-content: space-between;
}
.marque { display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.marque .retour {
  /* 24 px de haut au moins (WCAG 2.5.8) : à la seule hauteur de son texte, ce
     lien faisait 18 points, et c'est le premier qu'on touche en arrivant du
     site du parti. Le padding est vertical seulement, pour que le libellé
     reste aligné à gauche sur le nom du site, en dessous. */
  align-self: flex-start; display: inline-flex; align-items: center; gap: 0.35rem;
  min-height: 1.5rem; padding: 0.2rem 0;
  color: var(--texte-tres-doux); text-decoration: none;
  font-size: 0.8rem; letter-spacing: 0.06em; text-transform: uppercase;
  line-height: 1.4;
}
.marque .retour:hover { color: var(--bandeau-texte); }
.marque .retour .icone { width: 1em; height: 1em; }
/* Le nom du site, en capitales serrées, précédé du carré d'or : c'est la
   marque de l'affiche, et elle tient en douze pixels de côté. Le carré est
   décoratif — il est dessiné par le style, pas écrit dans le HTML, et aucune
   synthèse vocale n'a à l'annoncer. */
header.bandeau .nom {
  font-size: 0.9375rem; margin: 0; font-weight: 900;
  letter-spacing: 0.12em; text-transform: uppercase; line-height: 1;
}
header.bandeau .nom a {
  color: inherit; text-decoration: none;
  display: inline-flex; align-items: center; gap: 0.7rem;
}
header.bandeau .nom a::before {
  content: ""; flex: none; width: 0.75rem; height: 0.75rem; background: var(--or);
}
/* Le pictogramme du nom a cédé la place au carré : deux marques valent moins
   qu'une. Il reste dans le HTML pour les deux portages, et ne s'affiche pas. */
header.bandeau .nom .icone { display: none; }
/* Dans le cadre que le site parent ouvre sur sa page d'accueil — même
   origine, classe posée par lui sur `<body>` —, sa navigation est juste
   au-dessus, et le lien de retour ferait doublon. C'est la seule chose que la
   page sache de son hôte, et elle ne coûte rien s'il cesse de la poser. */
body.plf-embedded .marque .retour, body.plf-embedded footer .retour-site {
  display: none;
}
/* Les onglets. Ils ont remplacé les trois groupes étiquetés — « le programme,
   la preuve, la confiance » —, non parce que ces groupes disaient faux, mais
   parce que huit pages sous trois intertitres prenaient deux fois la hauteur
   du bandeau collé, et qu'un bandeau collé qui mange un quart de l'écran ne
   colle plus rien d'utile. L'étiquette de groupe subsiste dans le HTML, pour
   les synthèses vocales, et se lit à l'écran comme une simple pause. */
header.bandeau nav { display: flex; flex-wrap: wrap; gap: 0.35rem 0.25rem; }
nav .groupe { display: contents; }
/* L'étiquette de groupe : lue par les synthèses vocales, invisible à l'œil.
   `clip-path` plutôt que `display:none`, qui la retirerait aussi de l'arbre
   d'accessibilité — c'est-à-dire de la seule oreille qui l'entend encore. */
nav .etiquette {
  position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip-path: inset(50%); white-space: nowrap; border: 0;
}
/* `display: contents` ici AUSSI, et pas seulement sur le groupe : sinon
   chaque groupe reste un bloc, et la barre se replie par groupes — sur un
   téléphone, « Programme » occupait une rangée à lui seul, et les huit onglets
   en prenaient trois. Les liens sont les enfants directs du `<nav>`, et se
   replient un par un. */
nav .liens { display: contents; }
/* Un onglet. Cible tactile de 44 px de haut (WCAG 2.5.8), capitales serrées,
   et un filet sous chacun : c'est ce filet qui épaissit sur l'onglet courant.
   L'ACTIF NE SE SIGNALE PAS QUE PAR LA COULEUR — un fond d'or seul ne se voit
   ni en niveaux de gris, ni pour une vision basse, et ne s'annonce pas ; il
   porte donc un soulignement de 3 px ET `aria-current="page"`. */
nav a {
  color: var(--texte-doux); text-decoration: none;
  font-size: 0.875rem; font-weight: 700; letter-spacing: 0.04em;
  text-transform: uppercase;
  display: inline-flex; align-items: center; min-height: 2.75rem;
  padding: 0 0.7rem;
  border-bottom: 3px solid transparent;
}
nav a:hover { color: var(--bandeau-texte); border-bottom-color: var(--trait-champ); }
nav a[aria-current="page"] {
  color: var(--or); border-bottom-color: var(--or);
}

/* Les titres de l'affiche. Le premier de chaque page est massif, en capitales,
   très serré : c'est lui qu'on retient. Il est fluide — de 36 px sur un
   téléphone à 76 px au large — parce qu'une taille fixe de 76 px coupe
   « Programme » en trois sur 320 points. */
h1, h2, h3, h4 { text-wrap: balance; }
h1 {
  margin: 0;
  font-size: clamp(2.25rem, 5.5vw, 4.75rem); line-height: 0.95;
  font-weight: 900; letter-spacing: -0.04em; text-transform: uppercase;
}
/* L'accueil crie un peu plus fort que les autres pages : c'est la seule qui
   soit lue par quelqu'un qui n'a pas demandé à lire. */
.affiche h1 {
  font-size: clamp(2.5rem, 7vw, 6.0625rem); line-height: 0.92;
  letter-spacing: -0.045em;
}
h2 {
  font-size: clamp(1.75rem, 4vw, 2.5rem); line-height: 1;
  margin: 3rem 0 1rem; font-weight: 900;
  letter-spacing: -0.03em; text-transform: uppercase;
}
h3 { font-size: 1.25rem; margin: 2rem 0 0.5rem; font-weight: 700;
     letter-spacing: -0.01em; }
h4 { letter-spacing: -0.01em; }
/* Le titre en serif : celui d'un encadré, d'une carte crème, d'un bloc qui
   parle plutôt qu'il n'assène. Il coexiste avec les capitales sans les
   concurrencer, parce qu'il ne joue pas dans la même famille. */
.serif {
  font-family: "Instrument Serif", Georgia, "Times New Roman", serif;
  font-weight: 400; text-transform: none; letter-spacing: 0;
  line-height: 1.05;
}
p { margin: 0.7rem 0; max-width: 46rem; }
a { color: var(--accent); }
a:hover { opacity: 0.85; }
/* Le sur-titre d'une page : trois mots en or, en capitales espacées, au-dessus
   du titre. Il dit où l'on est, ce que le titre ne dit plus depuis qu'il est
   une phrase et non un intitulé. */
.surtitre {
  margin: 0 0 1rem; font-size: 0.975rem; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--or);
  line-height: 1;
}
/* Le chapeau : la phrase sous le titre, en serif, plus grande que le texte
   courant. C'est la seule chose que lira celui qui ne lit que deux lignes. */
.chapeau {
  font-family: "Instrument Serif", Georgia, "Times New Roman", serif;
  font-size: clamp(1.1875rem, 2vw, 1.625rem); line-height: 1.45;
  color: var(--texte-doux); max-width: 51rem; margin: 1.5rem 0 0;
}
/* L'affiche elle-même : le bloc de tête d'une page. Sur l'accueil, il tient
   tout le premier écran. */
.affiche { padding: 3rem 0 2.5rem; }
.affiche .chapeau { font-size: clamp(1.25rem, 2.4vw, 1.875rem); }
/* Ce qui, dans une phrase, porte le message. En or ET en demi-gras : l'or seul
   disparaît pour une vision basse ou un daltonisme fort, et l'emphase avec
   lui. Deux signaux valent mieux qu'un, et le gras ne coûte rien à personne. */
.cle-texte, strong.cle-texte { color: var(--or); font-weight: 600; }

.carte {
  background: var(--fond-carte); border: 1px solid var(--trait);
  border-radius: 4px; padding: 1.25rem 1.4rem; margin: 1.5rem 0;
}
.note {
  border-left: 3px solid var(--or); background: var(--fond-carte);
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
/* Le badge d'un scénario : « proposition » ou « contrefactuel », redit à côté
   de chaque tableau ce que le préambule a dit une fois. Petit, en capitales
   espacées, sans couleur porteuse de sens à elle seule : le mot suffit. */
.badge {
  display: inline-block; font-size: 0.68rem; letter-spacing: 0.06em;
  text-transform: uppercase; font-weight: 700; line-height: 1.4;
  padding: 0.05em 0.45em; border-radius: 3px; vertical-align: 0.15em;
  border: 1px solid var(--trait-champ); color: var(--texte-doux);
  white-space: nowrap;
}
.badge.proposition { color: var(--or); border-color: var(--or); }
/* Le point de vigilance : la réserve que la page fait sur elle-même, sortie de
   la prose et marquée comme un avertissement — c'est un gage de sérieux, pas
   une note de bas de page. */
.note.vigilance { border-left-color: var(--alerte); }
/* Le résumé en langage courant d'une page technique : trois ou quatre phrases
   avant le détail, dans le même encart qu'une note, un peu plus grand. */
.note.resume { font-size: 1rem; }
/* L'entrée de l'accueil : deux lignes qui disent que le site est un
   simulateur, et le bouton qui l'ouvre. */
.note.entree { font-size: 1rem; margin: 1.2rem 0; }
.note.entree p { margin: 0; }
.note.entree .actions { margin-top: 0.7rem; }
.discret { color: var(--texte-tres-doux); font-size: 0.9rem; }
/* -- le panneau crème -------------------------------------------------------

   Tout ce qu'on remplit ou qu'on emporte est posé sur du crème : le
   formulaire, l'appel au simulateur, les cartes à publier. C'est le seul
   endroit du site où le texte est sombre sur clair, et il faut donc y
   redéfinir les couleurs de tout ce qui peut s'y trouver — liens, champs,
   boutons, filets —, sans quoi un lien d'or sur du crème tomberait à 1,7:1. */
.creme {
  background: var(--creme); color: var(--sur-creme);
  border-radius: 4px; padding: clamp(1.25rem, 4vw, 2rem);
  margin: 1.5rem 0;
}
.creme h2, .creme h3, .creme .surtitre { color: inherit; }
.creme .surtitre { color: var(--sur-creme-accent); }
.creme a { color: var(--sur-creme-accent); }
.creme .discret, .creme .aide, .creme .calcul, .creme label {
  color: var(--sur-creme-doux);
}
.creme input, .creme select, .creme textarea {
  color: var(--sur-creme); background: #fff; border: 2px solid var(--sur-creme);
}
.creme :focus-visible { outline-color: var(--sur-creme); }
.creme input:focus, .creme select:focus, .creme textarea:focus {
  outline: 3px solid var(--sur-creme); outline-offset: 2px;
}
.creme button, .creme a.bouton {
  background: var(--sur-creme); color: var(--or); border-color: var(--sur-creme);
}
.creme table th, .creme table td { border-bottom-color: var(--creme-trait); }
.creme thead th { color: var(--sur-creme-doux); }

/* Le bandeau du simulateur, sur l'accueil : le formulaire court, en crème,
   juste sous le titre. C'est la preuve mise à hauteur de la promesse — on la
   voit sans défiler, ce qui était tout le reproche fait à l'ancienne page. */
.simulateur-court .tete {
  display: flex; justify-content: space-between; align-items: baseline;
  gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1.125rem;
}
.simulateur-court .tete h2 {
  margin: 0; font-size: clamp(1.5rem, 3vw, 2.125rem);
}
.simulateur-court .tete .etiquette {
  font-size: 0.75rem; font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--sur-creme-accent);
}
/* Les champs et le bouton sur une seule rangée tant qu'ils tiennent. Le bouton
   ne se coupe jamais : c'est la seule chose de la rangée qu'on vient chercher. */
.simulateur-court .grille {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(10.625rem, 100%), 1fr));
  gap: 1rem; align-items: end;
}
.simulateur-court .grille button { white-space: nowrap; }

/* -- les engagements --------------------------------------------------------

   Les quatre chiffres du programme, en section à part : fond d'un ton
   au-dessus, filet d'or en tête, numérotés 01 à 04. La numérotation les fait
   lire comme une liste d'engagements et non comme quatre statistiques
   orphelines, ce qu'elles étaient tant qu'elles n'avaient ni titre ni rang.

   DEUX PAR LIGNE, ET JAMAIS TROIS. La largeur minimale d'une colonne vaut 45 %
   du bloc : trois colonnes ne peuvent donc plus tenir, quelle que soit la
   largeur de l'écran. C'est une correction demandée deux fois — à trois
   colonnes, la quatrième carte tombait seule sur sa ligne, et « on avait le
   cul entre deux chaises ». */
.engagements {
  margin: 4rem 0 0; background: var(--fond-carte);
  border-top: 4px solid var(--or);
}
.engagements .grille {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(max(20rem, 45%), 100%), 1fr));
  gap: 0; padding: 0.5rem clamp(1.25rem, 4vw, 2rem) 2.25rem;
  /* Le filet de séparation est porté par les cartes, et non par le fond du
     conteneur : un fond qui sert de trait laisse un rectangle vert vide dès
     qu'une rangée est incomplète, et c'est exactement ce qu'on a vu. Ce qui
     dépasse au bord est coupé. */
  overflow: hidden;
}
.engagements .engagement {
  padding: 1.75rem 1.5rem 0 0; display: grid; gap: 1rem; align-content: start;
}
/* La deuxième colonne porte son filet à GAUCHE : à droite, il pendrait dans le
   vide au bord du bloc. */
.engagements .engagement:nth-child(even) {
  padding: 1.75rem 1.5rem 0; box-shadow: -1px 0 0 var(--trait);
}
.engagements .rang {
  font-size: 0.9375rem; font-weight: 700; letter-spacing: 0.16em;
  color: var(--texte-doux); line-height: 1;
}
/* Le chiffre. Fluide, et sans `nowrap` : « 1 compte » ne doit pas pouvoir
   franchir sa colonne, et un chiffre coupé vaut mieux qu'une page qui déborde. */
.engagements .chiffre {
  font-size: clamp(2.375rem, 8vw, 3.75rem); line-height: 0.9;
  font-weight: 900; letter-spacing: -0.05em; color: var(--or);
}
/* La promesse, en serif, en crème plein contraste, séparée par un filet. C'est
   elle qui porte le message, et c'est elle qui se perdait quand les cartes
   n'avaient que deux niveaux. */
.engagements .promesse {
  font-family: "Instrument Serif", Georgia, "Times New Roman", serif;
  font-size: 1.5625rem; line-height: 1.25; color: var(--texte);
  border-top: 1px solid var(--trait); padding-top: 1rem;
}
/* Le détail technique : 18 px et non 15, et une teinte éclaircie. « C'est
   illisible pour certaines personnes » — le petit texte du programme est
   précisément celui qu'on lit en plein jour sur un téléphone. */
.engagements .detail {
  font-size: 1.125rem; line-height: 1.6; color: var(--texte-doux);
}

/* -- les trois gestes -------------------------------------------------------

   Comment le calcul marche, en trois lignes numérotées. Le chiffre est énorme
   et l'interligne serré : à taille de texte courant, les trois gestes se
   lisaient comme une note de bas de page à côté du tableau qui leur fait
   face, alors qu'ils pèsent autant. */
ol.gestes {
  margin: 0; padding: 0; list-style: none; display: grid; gap: 0;
  font-size: 1.5rem; line-height: 1.45; color: var(--texte-doux);
  border-top: 1px solid var(--trait);
}
ol.gestes > li {
  display: grid; grid-template-columns: 4rem 1fr; gap: 1.125rem;
  padding: 0.8rem 0; border-bottom: 1px solid var(--trait);
  align-items: baseline;
}
ol.gestes > li > .rang {
  font-size: 3.125rem; line-height: 0.85; font-weight: 900;
  letter-spacing: -0.05em; color: var(--or);
}
ol.gestes > li strong { color: var(--texte); font-weight: 700; }

/* L'encadré d'or : un bloc qui se détache sans changer de fond. Il porte ce
   qui mérite d'être lu à part — le tableau du plancher, un repère, une mise en
   garde argumentée. */
.encadre {
  border: 2px solid var(--or); padding: clamp(1.25rem, 4vw, 2rem);
  margin: 1.5rem 0;
}
.encadre > :first-child { margin-top: 0; }
.encadre > :last-child { margin-bottom: 0; }
/* Deux colonnes de même poids, qui se mettent l'une sous l'autre quand la
   place manque. C'est la mise en page de l'accueil sous les engagements, et
   celle de la Trajectoire sous son graphique. */
.paire {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(23.75rem, 100%), 1fr));
  gap: clamp(1.75rem, 4vw, 3rem); margin: 3.5rem 0; align-items: start;
}

form .grille {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(15rem, 100%), 1fr));
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
/* Le libellé d'un champ : 15 px, casse normale, demi-gras. PAS de capitales
   espacées à 12 px, si joli que ce fût : les capitales et le corps réduit sont
   deux handicaps qui se cumulent, notamment pour les dyslexiques. */
label {
  display: block; font-size: 0.9375rem; font-weight: 600; line-height: 1.2;
  color: var(--texte); margin-bottom: 0.4rem;
}
/* Pas d'`opacity` ici : elle ferait tomber l'aide sous le plancher de 4,5:1
   des textes courants (WCAG 1.4.3). La couleur pleine et la taille suffisent à
   la distinguer du libellé. */
label .aide {
  display: block; font-size: 0.875rem; font-weight: 400;
  color: var(--texte-doux);
}
/* Ce qu'une date saisie vaut en âge, sous le champ qui la porte : « soit
   64 ans et 7 mois ». Le calendrier a remplacé les champs d'âge ; cette ligne
   rend l'âge qu'ils disaient, et la page le recalcule à chaque frappe. */
.calcul {
  display: block; font-size: 0.875rem; color: var(--texte-doux);
  margin-top: 0.3rem;
}
input, select, textarea {
  width: 100%; padding: 0.7rem 0.75rem; font: inherit; font-size: 1rem;
  color: var(--texte); background: var(--fond); border: 2px solid var(--trait-champ);
  border-radius: 0;
}
/* Le relevé de carrière se lit en colonnes : une police à chasse fixe aligne
   les années les unes sous les autres, et une faute de frappe s'y voit. Le
   redimensionnement reste vertical — l'élargir déborderait de la carte. */
textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.88rem; line-height: 1.45; resize: vertical;
}
/* Un seul indicateur de focus pour tout ce qui se parcourt au clavier — champs,
   liens, onglets, boutons, dépliants, tableaux défilants. Il manquait tout
   entier avant la refonte, et c'était le défaut d'accessibilité le plus
   pénalisant du site : au clavier, on ne savait pas où l'on était. Trois
   pixels d'or, décalés de trois, sur fond sombre ; du vert profond dans les
   panneaux crème, où l'or se perdrait. */
:focus-visible {
  outline: 3px solid var(--or); outline-offset: 3px; border-radius: 0;
}
input:focus, select:focus, textarea:focus {
  outline: 3px solid var(--or); outline-offset: 2px;
}
/* Le bouton de l'affiche : or plein, vert profond dessus, capitales, carré.
   Rien d'arrondi — une affiche n'arrondit pas ses angles. */
button {
  font: inherit; font-size: 1rem; font-weight: 900;
  letter-spacing: 0.02em; text-transform: uppercase;
  padding: 1rem 1.5rem; min-height: 3rem; cursor: pointer;
  color: var(--fond); background: var(--or);
  border: 2px solid var(--or); border-radius: 0;
}
button:hover { opacity: 0.88; }
.actions { display: flex; flex-wrap: wrap; gap: 0.75rem 1.4rem; align-items: center;
           margin: 1.5rem 0 0; }
/* Un lien qui a le poids d'un bouton : il ouvre le simulateur, c'est-à-dire
   la seule chose que la page Coût invite à faire. Il reste un lien — il mène à
   une autre adresse, se copie et s'ouvre dans un onglet —, seul son habit
   change. */
a.bouton {
  display: inline-flex; align-items: center; min-height: 3rem;
  text-decoration: none;
  color: var(--fond); background: var(--or);
  border: 2px solid var(--or); border-radius: 0;
  padding: 0.85rem 1.5rem; font-size: 1rem; font-weight: 900;
  letter-spacing: 0.02em; text-transform: uppercase;
}
a.bouton:hover { opacity: 0.88; }
p.discret > a:only-child, p.actions > a:not(.bouton) {
  display: inline-flex; align-items: center; min-height: 1.5rem;
}
/* Le bouton secondaire : même taille, même cible tactile, mais creux. Il porte
   ce qu'on peut faire, et non ce qu'on est venu faire. */
button.second, a.bouton.second {
  background: transparent; color: var(--texte); border-color: var(--trait-champ);
  font-weight: 700; text-transform: none; letter-spacing: 0;
}
button.second:hover, a.bouton.second:hover { border-color: var(--or); opacity: 1; }
/* Les métiers de la carrière : une boîte par métier, la dernière en pointillé
   parce qu'elle n'en décrit encore aucun — c'est celle qui sert à en ajouter. */
.metiers { display: grid; gap: 0.9rem; margin: 0.9rem 0 0; }
.metier {
  border: 1px solid var(--creme-trait); border-radius: 4px; padding: 0.9rem 1rem;
  /* `<fieldset>` porte des marges et un padding propres à chaque navigateur. */
  margin: 0; min-width: 0;
}
.metier.facultatif { border-style: dashed; }
/* Le rang du métier est la LÉGENDE du groupe : « Revenu brut mensuel » est le
   même libellé dans les deux blocs, et seule cette légende dit lequel on
   remplit — à l'œil comme à l'oreille (WCAG 3.3.2). */
.metier > .rang {
  margin: 0; padding: 0 0.35rem; font-size: 0.78rem; letter-spacing: 0.05em;
  text-transform: uppercase; color: var(--sur-creme-doux); font-weight: 700;
}
/* Les pictogrammes. Un seul jeu — Lucide, grille de 24, trait de 2 —, une
   seule règle : ils prennent la taille et la couleur du texte qui les porte. */
.icone {
  width: 1.05em; height: 1.05em; flex: none; vertical-align: -0.16em;
}
details { margin-top: 1.25rem; }
/* Le résumé d'un dépliant porte SON chevron, et non celui du navigateur : le
   marqueur natif n'a ni la même forme ni la même taille d'un moteur à l'autre,
   et ne suit aucune de nos grilles. Il est donc masqué partout, une fois. */
summary {
  cursor: pointer; color: var(--texte-doux); font-size: 0.95rem;
  display: flex; align-items: center; gap: 0.45rem; list-style: none;
  min-height: 2.75rem;
}
summary::-webkit-details-marker { display: none; }
summary::marker { content: ""; }
summary > .icone { color: var(--or); transition: transform 0.15s; }
details[open] > summary > .icone { transform: rotate(180deg); }
summary:hover { color: var(--texte); }
details > .grille { margin-top: 1rem; }
/* Une section repliée. Son titre a le poids d'un intertitre, parce qu'il en
   tient lieu : c'est lui qu'on parcourt pour savoir ce que la page contient
   encore. Les sections se suivent sans espace entre elles, séparées par un
   filet, pour qu'une pile de dix se lise comme un sommaire. */
details.section { margin: 0; border-top: 1px solid var(--trait); }
details.section:last-of-type { border-bottom: 1px solid var(--trait); }
details.section > summary {
  color: var(--texte); font-size: 1.0625rem; font-weight: 700;
  padding: 0.85rem 0.2rem; gap: 0.6rem;
}
details.section > summary:hover { color: var(--or); }
details.section > .dedans { padding: 0 0 1.2rem 1.65rem; }
details.section > .dedans > :first-child { margin-top: 0; }
details.section > .dedans > h4 {
  font-size: 1rem; font-weight: 700; margin: 1.5rem 0 0.4rem;
}
/* Un tableau plus large que l'écran défile horizontalement. La zone qui défile
   doit pouvoir recevoir le focus, sinon elle est inatteignable au clavier chez
   les moteurs qui ne rendent pas focusables les boîtes défilantes (WCAG 2.1.1)
   : le HTML lui donne `tabindex="0"`, et le style rend ce focus visible.
   L'inertie tactile est celle d'iOS, sans laquelle le défilement y est sec. */
.defilant { overflow-x: auto; -webkit-overflow-scrolling: touch; }
/* Et il le DIT. Rien n'indiquait qu'il restait des colonnes à droite : une
   ombre portée au bord droit apparaît tant qu'il y a quelque chose à atteindre,
   et disparaît en bout de course. `scroll-timeline` n'étant pas encore
   partout, l'ombre est peinte en fond attaché — la technique de Roman Komarov,
   qui ne demande pas une ligne de script. */
.defilant {
  background:
    linear-gradient(to right, var(--fond) 30%, rgba(11, 61, 58, 0)) left center,
    linear-gradient(to left, var(--fond) 30%, rgba(11, 61, 58, 0)) right center,
    radial-gradient(farthest-side at 0 50%, rgba(0, 0, 0, 0.4), transparent) left center,
    radial-gradient(farthest-side at 100% 50%, rgba(0, 0, 0, 0.4), transparent) right center;
  background-repeat: no-repeat;
  background-size: 2.5rem 100%, 2.5rem 100%, 0.9rem 100%, 0.9rem 100%;
  background-attachment: local, local, scroll, scroll;
}
table { border-collapse: collapse; width: 100%; font-size: 1rem; }
/* Le titre du tableau, énoncé par les synthèses vocales avant son contenu et
   lu à l'écran comme l'intitulé de la grille. */
caption {
  caption-side: top; text-align: left; font-size: 0.9rem;
  color: var(--texte-doux); padding: 0 0 0.5rem;
}
tbody th { font-weight: 700; }
th, td { text-align: right; padding: 0.7rem 0.6rem; border-bottom: 1px solid var(--trait); }
th:first-child, td:first-child { text-align: left; }
thead th {
  font-size: 0.875rem; color: var(--texte-doux); font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  border-bottom: 2px solid var(--or);
}
tbody tr:last-child td { border-bottom: none; }
td.nombre, th.nombre { font-variant-numeric: tabular-nums; }
/* Une colonne de PHRASES, et non de nombres : elle se lit alignée à gauche,
   comme tout texte. */
td.texte, th.texte { text-align: left; }
/* L'en-tête d'une colonne triable est un bouton : il hérite de la police et
   de la couleur de l'en-tête, et seul le trait pointillé le signale — comme
   un mot du glossaire. Le sens du tri se lit dans `aria-sort`, et une flèche
   le redit à l'œil. */
th > .tri {
  /* `min-height: 0` défait la cible de 48 px des boutons de l'affiche, qui
     déformerait l'en-tête du tableau ; 24 px restent le plancher tactile, et
     le padding vertical les donne sans écarter les colonnes. */
  font: inherit; color: inherit; background: none; border: none;
  padding: 0.25rem 0; min-height: 1.5rem;
  text-transform: inherit; letter-spacing: inherit;
  cursor: pointer; border-bottom: 1px dotted currentColor;
}
th > .tri:hover { color: var(--or); }
th[aria-sort="ascending"] > .tri::after { content: " \\2191"; }
th[aria-sort="descending"] > .tri::after { content: " \\2193"; }
/* Les filtres d'un tableau : un champ de recherche et deux menus, sur une
   ligne, et le compte de ce qui reste en dessous. */
.filtres {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(12rem, 100%), 1fr));
  gap: 0.8rem 1.2rem; margin: 1rem 0 0.5rem;
}
.filtres + .compte { margin: 0.2rem 0 0.8rem; }
tbody tr[hidden] { display: none; }
/* Le plan d'une page longue : ce qu'elle contient, en une liste de liens qui
   se parcourt du regard avant de lire. */
.plan {
  background: var(--fond-carte); border-left: 3px solid var(--or);
  padding: 0.85rem 1.1rem; margin: 1.5rem 0; font-size: 0.95rem;
}
.plan .etiquette {
  margin: 0 0 0.35rem; font-size: 0.78rem; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--texte-doux); font-weight: 700;
}
.plan ol {
  margin: 0; padding: 0; list-style: none;
  display: flex; flex-wrap: wrap; gap: 0.25rem 1.1rem;
}
.plan a { color: var(--texte); text-decoration: none;
          border-bottom: 1px solid var(--trait-champ); }
.plan a:hover { color: var(--or); border-bottom-color: var(--or); }
/* Les onglets d'une grille : des boutons radio, dont le libellé fait
   l'onglet. Le clavier les parcourt aux flèches, comme tout groupe de radios,
   et le panneau suit sans une ligne de script : `:has()` lit lequel est
   coché. Là où `:has()` n'existe pas, le premier panneau reste visible et les
   autres restent repliés — la page dit moins, mais ne dit rien de faux. */
.onglets { border: none; padding: 0; margin: 1.25rem 0 0.75rem;
           display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }
.onglets legend { float: left; font-size: 0.9rem; color: var(--texte-doux);
                  padding: 0; margin-right: 0.4rem; }
.onglets input {
  position: absolute; width: 1px; height: 1px; margin: 0; opacity: 0;
  overflow: hidden; clip-path: inset(50%);
}
.onglets label {
  display: inline-flex; align-items: center; min-height: 2.75rem;
  margin: 0; font-size: 0.9375rem; font-weight: 600; color: var(--texte);
  padding: 0 1rem; border: 2px solid var(--trait-champ);
  border-radius: 0; cursor: pointer;
}
.onglets input:checked + label {
  background: var(--or); color: var(--fond); border-color: var(--or);
  font-weight: 700;
}
.onglets input:focus-visible + label { outline: 3px solid var(--or); outline-offset: 3px; }
.onglets label:hover { border-color: var(--or); }
.panneaux > .panneau[hidden] { display: none; }
.onglets:has(input:checked) ~ .panneaux > .panneau { display: none; }
.onglets:has(#grille-notionnel_liberal:checked) ~ .panneaux > .panneau[data-onglet="notionnel_liberal"],
.onglets:has(#grille-notionnel_retroactif:checked) ~ .panneaux > .panneau[data-onglet="notionnel_retroactif"],
.onglets:has(#grille-notionnel_retroactif_employeur:checked) ~ .panneaux > .panneau[data-onglet="notionnel_retroactif_employeur"] {
  display: block;
}
/* Un résultat de simulation : l'intitulé, le montant, l'écart, et la barre qui
   donne une forme au montant. Les quatre se suivent, séparés d'un filet, sur
   le fond de la page — pas dans des cartes, qui auraient fait quatre objets là
   où il faut une comparaison. */
.scenario { margin: 0; padding: 1.125rem 0; border-bottom: 1px solid var(--trait); }
.scenario:first-of-type { border-top: 1px solid var(--trait); }
/* Le bloc des montants passe sous l'intitulé D'UN SEUL TENANT quand la place
   manque : c'est l'entête qui se replie, pas le montant. */
.scenario .entete { display: flex; justify-content: space-between; gap: 0.2rem 1rem;
                    align-items: baseline; flex-wrap: wrap; }
.scenario .titre { flex: 1 1 14rem; font-size: 1.0625rem; font-weight: 700; }
/* Un montant par scénario : le pouvoir d'achat de l'année de référence, et lui
   seul. La somme nominale du mois du départ l'accompagnait, en retrait derrière
   un filet ; elle donnait deux nombres à lire là où la comparaison n'en demande
   qu'un. */
.scenario .montant { display: flex; justify-content: flex-end; align-items: baseline;
                     gap: 1.1rem; flex-wrap: nowrap; margin-left: auto;
                     font-variant-numeric: tabular-nums; }
.scenario .chiffre { display: flex; flex-direction: column; align-items: flex-end;
                     white-space: nowrap; }
.scenario .chiffre .somme { line-height: 1.2; }
.scenario .chiffre .unite { font-size: 0.8rem; color: var(--texte-doux); }
.scenario .principal .somme {
  font-size: 1.875rem; font-weight: 900; letter-spacing: -0.03em;
}
.scenario .montant .annuel { color: var(--texte-doux); font-size: 0.85rem; }
/* Le salaire net, à gauche de la pension et DE LA MÊME TAILLE QU'ELLE.
   Deux grandeurs de nature différente se touchent ici — ce qu'on touche en
   travaillant, ce qu'on touchera à la retraite —, et elles comptent autant
   l'une que l'autre : une réforme des retraites se juge sur les deux. Elles
   étaient d'abord écrites à deux tailles, la pension dominant le salaire ;
   le salaire s'y perdait, et c'est précisément lui que personne ne chiffre.

   Ce qui les distingue n'est donc plus la taille mais l'étiquette, et un
   filet vertical qui les sépare — le même idiome que la frise de repères des
   pages Coût et Avantages. */
.scenario .salaire { align-items: flex-end; padding-right: 1.1rem;
                     box-shadow: 1px 0 0 var(--trait); }
.scenario .salaire .somme {
  font-size: 1.875rem; font-weight: 900; letter-spacing: -0.03em;
}
.scenario .salaire .unite { white-space: nowrap; text-align: right; }
/* L'écart n'est écrit que là où il y en a un — donc sur la seule proposition —
   et dans la couleur d'accent, qui ne sert nulle part ailleurs dans ce bloc. */
.scenario .salaire .ecart { font-size: 0.95rem; font-weight: 700;
                            color: var(--accent); white-space: nowrap; }
@media (max-width: 48rem) {
  /* Deux grands nombres ne tiennent pas côte à côte sous 768 px : ils passent
     l'un sous l'autre, le filet vertical devient horizontal, et les étiquettes
     repassent à gauche avec eux. */
  .scenario .montant { flex-wrap: wrap; justify-content: flex-start;
                       gap: 0.4rem 1.1rem; }
  .scenario .salaire { align-items: flex-start; padding-right: 0;
                       padding-bottom: 0.4rem; box-shadow: none;
                       border-bottom: 1px solid var(--trait); flex: 1 0 100%; }
  .scenario .salaire .unite { text-align: left; }
}
/* La glose sous un scénario : en sans-serif 16 px, et non en serif fin 15 px.
   C'était le texte le plus fatigant du site — à cette taille, un serif fin est
   un obstacle de plus. */
.scenario .glose {
  font-size: 1rem; line-height: 1.5; color: var(--texte-doux); margin-top: 0.35rem;
  max-width: 46rem;
}
/* La barre. Elle ne s'ajoute à rien : elle donne une forme aux montants déjà
   écrits, dans la même ligne. Celle de la proposition libérale est plus épaisse
   que les autres — c'est elle que l'œil trouve en premier, sans qu'on ait à
   l'écrire. */
.barre { height: 14px; background: var(--fond-carte); margin-top: 0.75rem;
         display: flex; align-items: center; }
.barre > span { display: block; height: 10px; }
.barre.actuel > span { background: var(--actuel); }
.barre.retroactif > span { background: var(--retroactif); }
.barre.retroactif-employeur > span { background: var(--retroactif-employeur); }
.barre.liberal > span { background: var(--liberal); height: 14px; }
/* Le pilier capitalisé, dans la barre de la proposition : la même couleur,
   hachurée. Même système, autre nature — un capital placé, pas une pension
   mutualisée. Une seconde teinte l'aurait rangé ailleurs ; une hachure dit
   « ceci n'est pas de la répartition » sans quitter la famille, et se voit
   aussi en noir et blanc et sous une deutéranopie. */
.barre.liberal > span.capitalise {
  background: repeating-linear-gradient(135deg, var(--liberal) 0 3px,
                                        var(--fond-carte) 3px 6px);
}
/* De quoi le montant de la proposition est fait, sous le chiffre et aligné sur
   lui : le total se lit d'abord, sa composition juste après. Sur un téléphone,
   la ligne repasse à gauche avec le reste du bloc.

   Elle ne s'appelle PAS « partage », et c'est délibéré : cette classe-là est
   déjà celle de la barre de boutons de partage, qui porte un filet or de 3 px
   sur toute la largeur. Un nom repris ailleurs a tiré ce filet en travers du
   bloc de la proposition, entre le montant et sa barre — une ligne jaune
   continue que rien n'expliquait. */
.scenario .composition {
  display: block; text-align: right; font-size: 0.9rem;
  color: var(--texte-doux); margin-top: 0.2rem;
}
@media (max-width: 40rem) { .scenario .composition { text-align: left; } }
.fiches { display: grid;
          grid-template-columns: repeat(auto-fit, minmax(min(11rem, 100%), 1fr));
          gap: 1rem; }
.fiche .valeur { font-size: 1.25rem; font-variant-numeric: tabular-nums;
                 font-weight: 700; }
.fiche .etiquette { font-size: 0.85rem; color: var(--texte-doux); }
.fiche .precision { font-size: 0.85rem; color: var(--texte-doux); margin-top: 0.3rem; }
/* Les trois chiffres d'ouverture d'une page : ce sont eux qu'on emporte si on
   ne lit rien d'autre, et ils doivent donc se lire de loin, avant le texte.
   L'étiquette passe AU-DESSUS du nombre — on lit « ce qui rentre » puis
   « 417 Md € », dans cet ordre, et non un nombre dont on cherche le sens.

   Comme les engagements, la frise porte ses filets sur les cartes et coupe ce
   qui dépasse : un fond servant de trait laissait un rectangle vide dès que la
   dernière rangée était incomplète. */
.fiches.reperes {
  gap: 0; margin: 2rem 0;
  grid-template-columns: repeat(auto-fit, minmax(min(13.75rem, 100%), 1fr));
  border-top: 1px solid var(--trait); border-bottom: 1px solid var(--trait);
  overflow: hidden;
}
.fiches.reperes .fiche {
  background: none; border: 0; border-radius: 0;
  padding: 1.25rem 1.25rem 1.25rem 0;
  box-shadow: 1px 0 0 var(--trait);
  display: flex; flex-direction: column;
}
.fiches.reperes .fiche .valeur {
  font-size: clamp(1.75rem, 4vw, 2.5rem); line-height: 1.05; font-weight: 900;
  letter-spacing: -0.04em; color: var(--or); order: 2;
}
.fiches.reperes .fiche .etiquette {
  order: 1; font-size: 0.8125rem; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--texte-doux); margin-bottom: 0.4rem;
}
.fiches.reperes .fiche .precision { order: 3; margin-top: 0.4rem; }
/* Quelques idées, une par bloc. Elles se lisent côte à côte, de même poids :
   c'est ce qui les distingue d'une liste, où la première l'emporte. */
.points { display: grid;
          grid-template-columns: repeat(auto-fit, minmax(min(20rem, 100%), 1fr));
          gap: 1.5rem; margin: 2rem 0; }
.points .point { border-top: 3px solid var(--or); padding: 1rem 0 0; }
.points .point > h3 {
  margin: 0 0 0.4rem; font-size: 1.25rem; font-weight: 900;
  letter-spacing: -0.02em; text-transform: uppercase;
}
.points .point > p { margin: 0; font-size: 1rem; color: var(--texte-doux); }

/* Une question, sa réponse, le tracé qui la montre. Encadrée pour se découper :
   une capture de ce bloc se comprend hors du site, et c'est exactement ce qu'on
   en fait depuis que chaque carte porte sa barre de partage. */
section.cle {
  background: var(--fond-carte); border: 0; border-top: 3px solid var(--or);
  border-radius: 0; padding: 1.5rem clamp(1.25rem, 3vw, 1.75rem) 1.25rem;
  margin: 2.5rem 0;
}
section.cle > h3 {
  margin: 0; font-size: clamp(1.375rem, 3vw, 1.75rem); font-weight: 900;
  letter-spacing: -0.03em; text-transform: uppercase;
}
section.cle > .reponse {
  font-size: 1.1875rem; line-height: 1.5; max-width: 46rem; margin: 0.5rem 0 0.2rem;
  color: var(--texte-doux);
}
section.cle > .source {
  font-size: 0.875rem; color: var(--texte-tres-doux); margin: 0.2rem 0 0;
}
/* -- la barre de partage ----------------------------------------------------

   Elle est SOUS LE RÉSULTAT — sous le graphique qu'on vient de lire, sous la
   carte qu'on vient de voir —, et non dans une page « Partager » que personne
   ne trouve. Elle est écrite UNE fois et sert aux deux : c'est pourquoi ses
   sélecteurs ne nomment plus la carte qui la porte.

   Deux gestes, et non trois. Publier sur X, télécharger l'image et copier le
   texte demandaient de choisir avant d'agir, et chacun des trois était
   incomplet. Le premier bouton fait maintenant le tout ; le second reste
   parce qu'un ordinateur ne sait ouvrir qu'un seul réseau avec un message
   déjà écrit. */
.partage {
  margin: 1.25rem 0 0; padding-top: 1.125rem;
  border-top: 3px solid var(--or);
  display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;
}
/* Les deux boutons partagent la cible tactile de 48 px. Le premier est plein —
   c'est celui qu'on vient chercher —, le second creux. */
.partage > .partager,
.partage > .partager-x {
  font: inherit; font-size: 0.9375rem; cursor: pointer;
  min-height: 3rem; padding: 0.85rem 1.125rem;
  border-radius: 0; display: inline-flex; align-items: center; gap: 0.5rem;
}
.partage > .partager {
  font-weight: 900; letter-spacing: 0.04em; text-transform: uppercase;
  color: var(--fond); background: var(--or); border: 2px solid var(--or);
}
.partage > .partager-x {
  font-weight: 700; color: var(--texte); background: transparent;
  border: 2px solid var(--trait-champ);
}
.partage > .partager:hover { opacity: 0.88; }
.partage > .partager-x:hover { border-color: var(--or); }
.partage > .partager[disabled] { opacity: 0.6; cursor: progress; }
/* Le compte rendu du geste — « image enregistrée, texte copié ». Il s'écrivait
   dans le libellé du bouton, ce qui changeait sous le doigt la cible qu'on
   venait de toucher, et faisait disparaître le pictogramme ; il est ici, à
   côté, et son `role="status"` le fait annoncer sans qu'on ait à y revenir. */
.partage > .etat {
  font-size: 0.9375rem; line-height: 1.35; color: var(--texte-doux);
  min-width: 0; flex: 1 1 8rem;
}
.partage > .etat:empty { display: none; }
/* Le repli du presse-papiers : quand le navigateur refuse la copie, le texte
   s'affiche dans un champ sélectionnable plutôt que d'annoncer un succès qui
   n'a pas eu lieu. Il prend toute la largeur, sous les boutons, et ne s'efface
   pas tout seul — c'est au lecteur de le refermer. */
.partage > .repli {
  flex: 1 1 100%; margin: 0; font-family: inherit; font-size: 0.9375rem;
  background: var(--fond); color: var(--texte); border: 2px solid var(--or);
}
.partage > .repli[hidden] { display: none; }
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
  border-bottom: 1px dotted var(--or); border-radius: 0;
  padding: 0; margin: 0; min-height: 0; cursor: help;
  text-transform: inherit; letter-spacing: inherit;
}
/* L'appel d'une bulle : un point d'interrogation, et non un mot souligné. La
   cible tactile fait au moins 24 px de côté (WCAG 2.5.8). */
.mot > .terme.appel {
  display: inline-flex; align-items: center; justify-content: center;
  margin-left: 0.25em; padding: 0.2em; font-size: 0.95em; line-height: 1;
  min-width: 1.5rem; min-height: 1.5rem;
  color: var(--texte-doux); border-bottom: none; vertical-align: -0.1em;
}
.mot > .terme:hover, .mot > .terme[aria-expanded="true"] { color: var(--or); }
.mot > .terme[aria-expanded="true"] { border-bottom-style: solid; }
.mot > .bulle {
  display: block; position: absolute; left: 0; top: calc(100% + 0.4rem);
  z-index: 25; width: max(14rem, min(22rem, 70vw));
  background: var(--fond-carte); color: var(--texte);
  border: 2px solid var(--or); border-radius: 0;
  box-shadow: 0 8px 26px rgba(0, 0, 0, 0.45);
  padding: 0.7rem 0.9rem; font-size: 0.9375rem; line-height: 1.45;
  /* Le texte de la bulle est un texte courant, quelle que soit la phrase qui
     porte le mot : sans cela une définition posée dans un chapeau en héritait
     la couleur, la taille et les capitales. */
  font-weight: 400; font-style: normal; text-align: left; white-space: normal;
  font-family: "Public Sans", system-ui, sans-serif; text-transform: none;
  letter-spacing: 0;
}
.mot > .bulle[hidden] { display: none; }
.etiquette-fiabilite {
  display: inline-block; font-size: 0.8rem; letter-spacing: 0.06em;
  text-transform: uppercase; font-weight: 700; padding: 0.15rem 0.5rem;
  border-radius: 0; background: var(--fond); border: 1px solid var(--trait-champ);
  color: var(--texte-doux);
}
/* Graphiques : du SVG écrit à la main, dont seules les couleurs et les tailles
   de texte sont ici. Le tracé lui-même est dans `graphique()`. */
.graphique { margin: 1.5rem 0 1.75rem; position: relative; }
.graphique svg { display: block; width: 100%; height: auto; overflow: visible;
                 touch-action: pan-y; }
/* La figure se parcourt au clavier : les flèches y déplacent l'année lue. */
.graphique:focus-visible { outline: 3px solid var(--or); outline-offset: 4px; }
/* La signature, en haut à gauche du cadre. N'importe quelle capture d'écran
   emporte donc le compte, sans rien demander au lecteur — et c'est ce qui fait
   qu'un graphique republié reste attribué. */
.graphique .signature {
  fill: var(--or); font-family: inherit; font-size: 15px; font-weight: 700;
}
/* Le trait vertical de l'année lue, et les points posés sur chaque courbe. Ils
   sont dessinés par `index.html` dans le `<g class="survol">` que le tracé
   laisse vide : rien de tout cela n'est dans le HTML servi, et la page reste
   lisible sans une ligne de script. */
.graphique .survol .guide { stroke: var(--texte); stroke-width: 1; }
.graphique .survol .point { stroke-width: 3; fill: var(--fond); }
/* La lecture de l'année survolée. Elle N'EST PLUS une infobulle flottante :
   posée dans le cadre, elle recouvrait forcément des courbes, quelle que soit
   son ancre, et sortait du bord en fin de série — c'est-à-dire là où l'on
   regarde le plus. C'est maintenant une bande de hauteur fixe sous le tracé,
   qui ne peut par construction recouvrir ni déborder de rien.

   Chaque cellule porte son étiquette, sa valeur dans la couleur de sa courbe,
   et un complément. Les trois rangées ont une hauteur IMPOSÉE, et
   l'alignement se fait par le haut : sans cela, la cellule qui porte une
   fourchette remontait son chiffre, et les valeurs ne partaient plus du même
   y. */
.graphique .lecture {
  margin-top: 0.75rem; border-top: 3px solid var(--or); padding-top: 0.75rem;
  display: grid; grid-auto-flow: column; grid-auto-columns: 1fr;
  align-items: start;
}
.graphique .lecture[hidden] { display: none; }
.graphique .lecture > * {
  padding: 0 0.9rem; box-shadow: 1px 0 0 var(--trait);
  display: grid; grid-template-rows: 2.375rem 2.625rem 1.125rem;
  align-content: start;
}
.graphique .lecture > :first-child { padding-left: 0; }
.graphique .lecture > :last-child { box-shadow: none; padding-right: 0; }
.graphique .lecture .etiquette {
  font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--texte-tres-doux); line-height: 1.2;
}
.graphique .lecture .valeur {
  font-size: 1.625rem; font-weight: 900; letter-spacing: -0.03em;
  line-height: 1; font-variant-numeric: tabular-nums; align-self: center;
}
.graphique .lecture .complement {
  font-size: 0.8125rem; color: var(--texte-tres-doux); line-height: 1.2;
}
.graphique .lecture .annee .valeur { color: var(--or); }
/* L'aide qui dit que les flèches marchent. Elle n'apparaît qu'au focus clavier :
   à la souris, elle n'apprendrait rien et prendrait une ligne. */
.graphique .aide-clavier {
  font-size: 0.85rem; color: var(--texte-tres-doux); margin: 0.4rem 0 0;
  visibility: hidden;
}
.graphique:focus-visible .aide-clavier { visibility: visible; }
.graphique .grille { stroke: var(--trait); stroke-width: 1; }
.graphique .axe { stroke: var(--trait-champ); stroke-width: 1; }
.graphique .repere {
  stroke: var(--texte-tres-doux); stroke-width: 1; stroke-dasharray: 3 4;
}
.graphique .courbe {
  fill: none; stroke-width: 3;
  stroke-linejoin: round; stroke-linecap: round;
}
.graphique .bande { stroke: none; }
/* Le ruban entre deux courbes : vert quand la première passe au-dessus, rose
   quand elle passe dessous. OPAQUE, et peint sous les courbes. Translucide, il
   virait au gris-brun sale sur le vert profond — « il y a un problème sur la
   couleur rouge » —, et deux aplats superposés produisaient une troisième
   couleur qui ne figurait dans aucune légende. */
.graphique .ecart { stroke: none; }
.graphique .ecart.plus { fill: var(--reste); }
.graphique .ecart.moins { fill: var(--manque); }
/* Ses deux pastilles de légende, accolées : une seule couleur ne dirait que la
   moitié de ce que le ruban montre. Elles portent exactement la couleur
   peinte — sans opacité, puisque le ruban n'en a plus. */
.pastille.ecart-plus { background: var(--reste); }
.pastille.ecart-moins { background: var(--manque); margin-left: -0.15rem; }
/* L'étiquette posée au bout d'une courbe, qui lui donne son nom dans le cadre :
   plus besoin de faire l'aller-retour avec la légende pour savoir laquelle est
   laquelle. Le halo de fond, tracé sous le glyphe, lui garde son contraste
   quand elle passe sur une aire rose ou verte. */
.graphique .etiquette-serie {
  font-family: inherit; font-size: 15px; font-weight: 800;
  paint-order: stroke; stroke: var(--fond); stroke-width: 6px;
  stroke-linejoin: round;
}
.graphique .graduation {
  fill: var(--texte-tres-doux); font-family: inherit; font-size: 13px;
  font-weight: 600; font-variant-numeric: tabular-nums;
}
/* Le tableau des points du graphique. Il se range juste sous son tracé, et non
   à la distance qui sépare deux paragraphes : c'est la même figure, dite
   autrement. Déplié, il est borné en hauteur, et ses en-têtes de colonne
   restent visibles pendant qu'on le parcourt. */
.donnees-graphique { margin: -1.4rem 0 1.7rem; }
.donnees-graphique .defilant { max-height: 24rem; overflow-y: auto; }
.donnees-graphique table { font-size: 0.9rem; }
.donnees-graphique th, .donnees-graphique td { padding: 0.25rem 0.6rem; }
.donnees-graphique thead th {
  position: sticky; top: 0; background: var(--fond-carte);
  box-shadow: inset 0 -2px 0 var(--or);
}
.donnees-graphique caption { padding-bottom: 0.35rem; }
ul.legende {
  list-style: none; margin: 0.75rem 0 0; padding: 0;
  display: flex; flex-wrap: wrap; gap: 0.4rem 1.5rem; font-size: 0.9375rem;
}
ul.legende li { display: flex; align-items: baseline; gap: 0.45rem; }
.pastille {
  display: inline-block; flex: none;
  width: 0.75rem; height: 0.75rem; border-radius: 0;
}
/* Ce qu'un tableau ne peut pas porter dans ses cellules sans devenir illisible
   — la phrase qui explique une ligne. */
dl.gloses { margin: 0.8rem 0 0; font-size: 0.95rem; }
dl.gloses dt { font-weight: 700; margin-top: 0.7rem; }
dl.gloses dd { margin: 0.15rem 0 0; padding: 0; color: var(--texte-doux); }
ul.serree { margin: 0.5rem 0; padding-left: 1.2rem; max-width: 46rem; }
ul.serree li { margin: 0.3rem 0; }

/* -- les cartes à publier ---------------------------------------------------

   1200 × 675, la boîte de X et de LinkedIn. Ce qui s'affiche ici n'est plus
   l'image : c'est son APERÇU. La carte a longtemps été rendue à sa taille
   réelle dans un cadre qui défilait, parce qu'il fallait la capturer à l'écran
   pour l'avoir ; elle se télécharge maintenant d'un bouton, composée sur une
   toile aux vraies dimensions, et l'aperçu n'a plus qu'à ressembler à ce qu'on
   emportera. Il se réduit donc avec sa colonne, dans le rapport exact de 16/9.

   Toutes les longueurs de la carte sont en `cqw` — centièmes de la largeur du
   cadre —, c'est-à-dire la valeur en pixels du modèle divisée par douze. C'est
   la seule façon d'obtenir une réduction FIDÈLE : l'`em` aurait fallu composer
   les tailles les unes dans les autres, et les marges d'une ligne de 52 px ne
   se disent pas dans la même unité que celles d'une ligne de 28. Une valeur en
   pixels précède chaque taille de police, pour un navigateur qui ne connaîtrait
   pas les requêtes de conteneur : la carte y sera petite, jamais illisible. */
.cadre-carte {
  container-type: inline-size;
  background: var(--fond-carte); padding: 0.5rem; min-width: 0;
}
.carte-partage {
  aspect-ratio: 1200 / 675; box-sizing: border-box;
  background: var(--fond); color: var(--texte); padding: 4.667cqw;
  display: flex; flex-direction: column; justify-content: space-between;
  font-family: "Public Sans", system-ui, sans-serif;
}
.carte-partage.claire { background: var(--creme); color: var(--sur-creme); }
.carte-partage .surtitre {
  margin: 0; font-size: 13px; font-size: 2.167cqw; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--or);
  line-height: 1;
}
.carte-partage.claire .surtitre { color: var(--sur-creme-accent); }
.carte-partage .chiffre {
  font-size: 75px; font-size: 12.5cqw; line-height: 0.85; font-weight: 900;
  letter-spacing: -0.05em; color: var(--or);
}
/* Le déficit : un chiffre qui s'écrit en toutes lettres — « 2,4 points de
   PIB » —, donc plus long, donc plus petit, et de la couleur de l'aire du
   graphique qui le montre. */
.carte-partage.deficit .chiffre { font-size: 56px; font-size: 9.333cqw;
                                  color: var(--manque); }
/* L'appel au simulateur ne porte pas un chiffre mais une question : elle se
   pose en serif, sur la carte claire, et la phrase dessous prend le poids que
   le chiffre avait. */
.carte-partage.appel .chiffre {
  font-family: "Instrument Serif", Georgia, serif;
  font-size: 48px; font-size: 8cqw; line-height: 0.95; font-weight: 400;
  letter-spacing: 0; color: inherit;
}
.carte-partage.appel .phrase {
  font-family: "Public Sans", system-ui, sans-serif;
  font-size: 20px; font-size: 3.333cqw; line-height: 1.3; font-weight: 700;
}
.carte-partage .phrase {
  margin-top: 1.833cqw; font-family: "Instrument Serif", Georgia, serif;
  font-size: 26px; font-size: 4.333cqw; line-height: 1.12; color: var(--texte);
}
.carte-partage.claire .phrase { color: var(--sur-creme); }
.carte-partage .detail {
  margin-top: 1.667cqw; max-width: 83.333cqw;
  font-size: 14px; font-size: 2.333cqw; line-height: 1.45;
  color: var(--texte-doux);
}
.carte-partage.claire .detail { color: var(--sur-creme-doux); }
/* Le pied : le compte et l'adresse. C'est lui qui fait qu'une image republiée
   dit encore d'où elle vient — et il est doublé, dans l'image téléchargée, par
   un filigrane posé en travers du cadre. */
.carte-partage .pied {
  display: flex; justify-content: space-between; align-items: baseline;
  gap: 2cqw; border-top: 1px solid var(--trait); padding-top: 2.167cqw;
  font-size: 16px; font-size: 2.667cqw; font-weight: 700;
}
.carte-partage.claire .pied { border-top-color: var(--creme-trait); }
.carte-partage .pied .compte { color: var(--or); }
.carte-partage.claire .pied .compte { color: var(--sur-creme-accent); }
.carte-partage .pied .adresse {
  color: var(--texte-tres-doux); font-weight: 400;
  font-size: 13px; font-size: 2.167cqw;
}
.carte-partage.claire .pied .adresse { color: var(--sur-creme-doux); }
/* Les figures de la page Partager. Deux par ligne dès qu'il y a la place : les
   cartes se comparent, et une seule colonne en faisait une page à dérouler.
   `min(100%, …)` borne la piste sur les écrans étroits, où une largeur
   minimale plus large que la page déborderait. */
.cartes { display: grid; gap: 2.25rem; margin-top: 1.75rem;
          grid-template-columns: repeat(auto-fit, minmax(min(100%, 32rem), 1fr)); }
.cartes > figure { margin: 0; min-width: 0; }
/* La légende NOMME la carte, et se lit avant elle : c'est ce qui permet de
   choisir laquelle publier sans les regarder toutes. */
.cartes > figure > figcaption {
  margin: 0 0 0.6rem; font-size: 0.875rem; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--texte-tres-doux);
}

footer {
  width: calc(100% - 2 * var(--marge)); max-width: calc(var(--largeur) - 2 * var(--marge));
  margin: 4rem auto 0; padding: 1.5rem 0 5rem;
  border-top: 1px solid var(--trait);
  font-size: 0.9rem; color: var(--texte-tres-doux);
}
footer a { color: var(--or); }
.erreur {
  border-left: 3px solid var(--manque); background: var(--fond-carte);
  padding: 0.85rem 1.1rem; margin: 1.5rem 0;
}
pre.json {
  background: var(--fond-carte); border: 1px solid var(--trait); border-radius: 0;
  padding: 0.9rem 1.1rem; overflow-x: auto; max-height: 26rem; overflow-y: auto;
  font-size: 0.85rem; line-height: 1.45;
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
.chargement { text-align: center; padding: 4rem 1rem; color: var(--texte-doux); }
.chargement .jauge {
  height: 6px; width: min(24rem, 80%); margin: 1.5rem auto 0;
  background: var(--fond-carte); overflow: hidden;
}
.chargement .jauge > span {
  display: block; height: 100%; width: 30%; background: var(--or);
  animation: glisse 1.4s ease-in-out infinite;
}
@keyframes glisse {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(333%); }
}
body.calcul-en-cours main { opacity: 0.45; transition: opacity 0.2s; }
/* Ce qui n'est lu que par les synthèses vocales : la description d'un
   graphique, l'annonce d'un changement de page. */
.hors-ecran {
  position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip-path: inset(50%); white-space: nowrap; border: 0;
}

/* Téléphone. Tout ce qui est fluide s'est déjà réduit tout seul ; ne restent
   ici que les choses qui doivent CHANGER DE FORME — une rangée qui passe en
   colonne, une bande de lecture qui ne peut plus tenir cinq cellules de front. */
@media (max-width: 48rem) {
  /* La bande de lecture du graphique passe en deux colonnes : cinq cellules de
     front sur 390 points donnaient 70 points chacune, soit un chiffre de
     26 px coupé en deux. */
  .graphique .lecture {
    grid-auto-flow: row; grid-template-columns: 1fr 1fr;
    gap: 0.75rem 0;
  }
  .graphique .lecture > * { grid-template-rows: auto auto auto; }
  .graphique .lecture > :nth-child(odd) { padding-left: 0; }
  .graphique .lecture > :nth-child(even) { box-shadow: none; padding-right: 0; }
}
@media (max-width: 34rem) {
  body { font-size: 1rem; }
  header.bandeau { padding: 0.75rem 0; }
  /* Le nom prend toute la largeur et les onglets passent dessous : côte à
     côte, les deux se partageaient 358 points et le nom se coupait en deux. */
  .marque { flex: 1 1 100%; }
  header.bandeau nav { width: 100%; }
  /* Le bandeau ne colle plus : à huit onglets sur deux rangées, il mangeait un
     tiers de la hauteur d'un téléphone, et c'est cette hauteur qu'on vient
     chercher. */
  header.bandeau { position: static; }
  nav a { padding: 0 0.5rem; font-size: 0.8125rem; }
  .affiche { padding: 2rem 0 1.5rem; }
  .scenario .entete { flex-direction: column; gap: 0.15rem; }
  /* L'intitulé reprend sa hauteur de texte. En colonne, `flex: 1 1 14rem` ne
     réserve plus une largeur mais une HAUTEUR : chaque scénario portait donc
     224 px de vide entre son titre et son montant. */
  .scenario .titre { flex: 0 1 auto; max-width: 100%; }
  /* Le montant passe sous l'intitulé, aligné à gauche comme lui : `margin-left:
     auto` le poussait à droite de l'écran dès qu'il fut seul, et il flottait au
     milieu du vide. Les libellés se replient, les sommes jamais — un montant
     coupé en deux lignes ne se lit plus —, et la rangée passe à la ligne quand
     même cela ne suffit pas. */
  .scenario .montant { justify-content: flex-start; flex-wrap: wrap;
                       column-gap: 0.9rem; row-gap: 0.3rem; max-width: 100%;
                       margin-left: 0; }
  .scenario .chiffre { align-items: flex-start; white-space: normal;
                       min-width: 0; max-width: 100%; }
  .scenario .chiffre .somme, .scenario .chiffre .annuel { white-space: nowrap; }
  /* Les tableaux du détail portent jusqu'à six colonnes, et un téléphone leur
     donne 358 points : un demi-point de moins et des marges plus serrées leur
     rendent un cinquième de leur hauteur. */
  table { font-size: 0.9rem; }
  th, td { padding: 0.5rem 0.45rem; }
  /* Le retrait d'une section repliée coûte 26 points de largeur à ce qu'elle
     contient : de quoi couper une colonne de chiffres. */
  details.section > .dedans { padding-left: 0.6rem; }
  /* Les engagements et les frises passent à une colonne, et leurs filets
     verticaux deviennent horizontaux : un filet à gauche ne sépare plus rien
     quand tout est empilé. */
  .engagements .grille { grid-template-columns: 1fr; }
  .engagements .engagement,
  .engagements .engagement:nth-child(even) {
    padding: 1.5rem 0 0; box-shadow: none; border-top: 1px solid var(--trait);
  }
  .engagements .engagement:first-child { border-top: 0; }
  .fiches { grid-template-columns: 1fr; }
  .fiches.reperes { grid-template-columns: 1fr; }
  .fiches.reperes .fiche {
    padding: 1rem 0; box-shadow: none; border-top: 1px solid var(--trait);
  }
  .fiches.reperes .fiche:first-child { border-top: 0; }
  ol.gestes { font-size: 1.25rem; }
  ol.gestes > li { grid-template-columns: 3rem 1fr; gap: 0.875rem; }
  ol.gestes > li > .rang { font-size: 2.5rem; }
  .paire { gap: 2rem; margin: 2.5rem 0; }
  section.cle { padding: 1.25rem 1rem 1rem; }
  /* Chaque bouton de partage prend sa ligne : deux de front sur 358 points se
     serraient sous la cible tactile de 44 px. */
  .partage > .partager,
  .partage > .partager-x { flex: 1 1 100%; justify-content: center; }
  .partage > .etat { flex: 1 1 100%; }
  /* La bulle du glossaire quitte le fil du texte et se pose en bas de l'écran,
     sur toute la largeur. Une boîte flottante ancrée sur un mot qui peut se
     trouver au bord de l'écran en déborderait ; et une boîte posée DANS le fil
     coupait la phrase en deux. Fixée en bas, elle ne déplace rien et reste
     dans la vue quel que soit l'endroit où l'on a touché. */
  .mot { position: static; }
  .mot > .bulle {
    position: fixed; left: 0.75rem; right: 0.75rem; bottom: 0.75rem;
    top: auto; width: auto; max-width: none; z-index: 30;
    font-size: 1rem; padding: 0.9rem 1rem;
  }
  form .grille { gap: 0.9rem; }
  /* Le SVG se réduit avec la page : ses textes, exprimés en unités du viewBox,
     se réduiraient d'autant et deviendraient illisibles. On les grossit donc
     dans le repère pour qu'ils gardent leur taille à l'écran. Sur un écran de
     375 points, le tracé est réduit de moitié, et treize unités y feraient six
     pixels — très en dessous du plancher de lisibilité. */
  .graphique .graduation { font-size: 24px; }
  .graphique .etiquette-serie { font-size: 26px; stroke-width: 8px; }
  .graphique .signature { font-size: 26px; }
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

/* Impression : le lecteur qui imprime une simulation veut les chiffres, et il
   les veut en noir sur blanc — une affiche vert profond pleine page coûterait
   une cartouche pour ne rien dire de plus. Tout est donc reteinté à
   l'impression, par les variables : c'est le seul endroit où elles servent
   deux fois. */
@media print {
  :root {
    --fond: #fff; --fond-carte: #fff; --fond-appui: #fff;
    --texte: #000; --texte-doux: #333; --texte-tres-doux: #444;
    --trait: #999; --trait-champ: #666;
    --accent: #000; --or: #000; --creme: #fff; --sur-creme: #000;
    --sur-creme-doux: #333; --sur-creme-accent: #000; --creme-trait: #999;
  }
  header.bandeau nav, .evitement, .marque .retour { display: none; }
  header.bandeau {
    background: #fff; color: #000; border-bottom: 1px solid #000;
    margin-bottom: 1rem; position: static;
  }
  /* Ni la lecture au survol — il n'y a pas de pointeur sur du papier —, ni les
     boutons de partage : la page imprimée EST déjà l'image. */
  .graphique .lecture, .graphique .aide-clavier, section.cle > .partage {
    display: none;
  }
  body { background: #fff; color: #000; font-size: 11pt; overflow-x: visible; }
  /* Les capitales massives de l'affiche redeviennent des titres : à 76 px sur
     du papier, un titre mange le tiers de la première page. */
  h1 { font-size: 20pt; }
  h2 { font-size: 15pt; }
  .chapeau, .affiche .chapeau { font-size: 12pt; }
  .defilant { overflow: visible; background: none; }
  .carte, .note, table, .graphique, .scenario, section.cle, .encadre {
    break-inside: avoid;
  }
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

#: Le site dont cette page est un outil. Il la sert sous ``/retraite/`` ; elle
#: ne charge rien de lui, et n'y renvoie que par ce lien — en tête, pour qui
#: cherche d'où l'on vient, et en pied, pour qui a tout lu.
SITE_PARENT = "https://partiliberalfrancais.fr/"

#: Ce qui signe une carte exportée en image. Une image quittant le site n'a plus
#: ni barre d'adresse ni pied de page : sans ces deux lignes, elle circule sans
#: dire d'où elle vient ni qui l'a produite, et le premier qui la republie en
#: devient la source.
SIGNATURE = "@pliberal"
SIGNATURE_SITE = "Parti libéral français — le simulateur de retraite"

#: L'adresse qu'une image emporte. Celle du site parent, et non celle de GitHub
#: Pages : c'est là que le lecteur d'un post doit atterrir. Elle vaut pour les
#: cartes de la page Partager comme pour les images composées sous un
#: graphique — une image qui circule sans adresse ne ramène personne.
ADRESSE_SITE = "partiliberalfrancais.fr/#simulateur"

#: La navigation, par FONCTION et non par page : le message, la preuve, la
#: confiance. Six liens à la file ne disaient pas où aller après le programme ;
#: trois groupes le disent — ce qu'on propose, ce qui le montre, ce qui permet
#: de le croire. ``LIENS`` en est la liste à plat, pour qui n'a besoin que des
#: pages.
#:
#: Depuis la refonte en affiche, les étiquettes de groupe ne se VOIENT plus :
#: huit pages sous trois intertitres prenaient deux fois la hauteur du bandeau,
#: qui est désormais collé en haut. Elles restent DITES aux synthèses vocales,
#: qui les lisent comme la structure du menu — c'est le style qui les sort de
#: l'écran, pas ce fichier, et la classification reste vraie.
GROUPES_NAVIGATION = (
    ("Le programme", (("/", "Programme"),)),
    ("La preuve", (("/simuler", "Simuler"), ("/trajectoire", "Trajectoire"),
                   ("/cas-types", "Cas types"), ("/cout", "Coût"),
                   ("/avantages", "Avantages"))),
    ("La confiance", (("/methode", "Méthode"), ("/donnees", "Données"))),
    # Partager n'est ni une preuve ni une garantie : c'est ce qu'on fait APRÈS
    # avoir lu. La barre de partage de chaque graphique y renvoie déjà sans
    # passer par ici ; la page tient la liste complète des cartes, pour qui les
    # veut toutes.
    ("Faire connaître", (("/partager", "Partager"),)),
)

LIENS = tuple(lien_ for _, liens in GROUPES_NAVIGATION for lien_ in liens)


def lien(chemin: str, ancre: str = "") -> str:
    """Adresse d'une page interne.

    Le site tient dans une seule page : la navigation passe par l'ancre de
    l'adresse (``#/cas-types``). L'ancre de section, elle, ne peut pas s'y
    ajouter — la place est prise — et n'est acceptée que pour que les appels
    disent vers quoi ils pointent.
    """
    return "#" + chemin


def navigation(chemin_actif: str = "/") -> str:
    """Les liens du bandeau, par groupe : une étiquette, puis les pages.

    L'étiquette est du texte, lu par tout le monde — pas un ``aria-label``
    qu'une synthèse vocale serait seule à entendre. Elle est petite, et se
    lit comme un intertitre de menu.
    """
    def liens_du_groupe(liens: tuple) -> str:
        return "".join(
            f'<a href="{lien(chemin)}"'
            + (' aria-current="page"' if chemin == chemin_actif else "")
            + f">{escape(libelle)}</a>"
            for chemin, libelle in liens
        )
    return "".join(
        f'<span class="groupe"><span class="etiquette">{escape(etiquette)}</span>'
        f'<span class="liens">{liens_du_groupe(liens)}</span></span>'
        for etiquette, liens in GROUPES_NAVIGATION
    )


def entete(chemin_actif: str = "/") -> str:
    """Bandeau de tête, précédé du lien d'évitement.

    Le lien d'évitement est le premier élément parcouru au clavier. Le repère de
    navigation porte un nom : une page peut en compter plusieurs, et « navigation »
    tout court ne dit pas laquelle on parcourt.

    Le nom du site N'EST PLUS un ``<h1>``. Il l'a été tant que les pages
    ouvraient sur un ``<h2>`` ; depuis la refonte en affiche, chaque page porte
    son propre titre, énorme et en capitales, et c'est LUI le ``<h1>`` — ce qui
    est à la fois ce que la maquette montre et ce que la sémantique veut : un
    document a un titre, et « Retraite à comptes notionnels » est le nom du
    site, répété à l'identique sur huit pages. Il reste un lien vers l'accueil,
    dans une ``<p>`` que le style compose en petites capitales.
    """
    return f"""<a class="evitement" href="#contenu">Aller au contenu</a>
<header class="bandeau"><div class="interieur">
  <div class="marque">
    <a class="retour" href="{SITE_PARENT}" target="_top">{icone('arrow-left')}<span>Parti libéral français</span></a>
    <p class="nom"><a href="{lien('/')}">{icone('trending-up')}<span>Retraite à comptes notionnels</span></a></p>
  </div>
  <nav aria-label="Navigation principale">{navigation(chemin_actif)}</nav>
</div></header>"""


def affiche(surtitre: str, titre: str, chapeau: str) -> str:
    """Le bloc de tête d'une page : sur-titre, titre massif, chapeau.

    C'est l'unité qui fait de chaque page une affiche, et elle est la même
    partout pour que les huit se reconnaissent comme un seul site.

    - le SUR-TITRE, deux ou trois mots en or et en capitales, dit où l'on est.
      Le titre ne le dit plus : c'est devenu une phrase, et une phrase ne se
      repère pas dans une barre d'onglets ;
    - le TITRE est le ``<h1>`` de la page — le seul, depuis que le nom du site
      a cédé la place. Il est mis en capitales PAR LE STYLE, jamais dans le
      texte : certaines synthèses vocales épellent lettre à lettre un mot écrit
      en majuscules, et le titre d'une page n'a pas à s'entendre « P.R.O.G. » ;
    - le CHAPEAU, en serif, est la seule chose que lira celui qui ne lit que
      deux lignes.

    ``titre`` et ``chapeau`` sont du HTML : ils portent les passages en or, les
    liens et les mots du glossaire. ``surtitre`` est du texte.
    """
    return (
        f'<div class="affiche"><p class="surtitre">{escape(surtitre)}</p>'
        f'<h1>{titre}</h1><p class="chapeau">{chapeau}</p></div>'
    )


def pied() -> str:
    """Pied de page.

    Il porte ce que le lecteur doit savoir avant de citer un chiffre : d'où
    vient le modèle, sous quelle licence, en quelle unité il compte, et qu'il ne
    vaut pas relevé de carrière.

    Il ne porte AUCUNE mention légale. Le site qui accueille le simulateur —
    partiliberalfrancais.fr — édite et héberge la page ; l'identification de
    l'éditeur, la politique de données personnelles et la déclaration
    d'accessibilité sont les siennes, et deux déclarations concurrentes valent
    moins qu'une.
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
  <p class="retour-site">Un outil du <a href="{SITE_PARENT}" target="_top">Parti libéral français</a>.</p>
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

    Une entrée ``(libelle, [options])`` — dont le second élément est une LISTE
    et non un texte — est un groupe : ses options sont rendues sous un
    ``<optgroup>`` qui porte ce libellé. C'est ce qui rend un menu de soixante
    statuts parcourable : on cherche « SNCF » sous « Régimes spéciaux », et
    non dans une colonne de soixante lignes. Un groupe et des options nues
    peuvent se suivre dans le même menu.
    """
    supplement = "".join(
        f' {cle.rstrip("_").replace("_", "-")}="{escape(str(val))}"'
        for cle, val in attributs.items()
    )

    def option_html(option: tuple) -> str:
        code, texte = option[0], option[1]
        disponible = option[2] if len(option) > 2 else True
        propres = "".join(
            f' {cle}="{escape(str(val))}"'
            for cle, val in (option[3] if len(option) > 3 else {}).items()
        )
        return (
            f'<option value="{escape(code)}"'
            + (" selected" if code == selection else "")
            + ("" if disponible or code == selection else " disabled")
            + propres
            + f">{escape(texte)}</option>"
        )

    choix = []
    for option in options:
        if isinstance(option[1], list):
            choix.append(
                f'<optgroup label="{escape(option[0])}">'
                + "".join(option_html(membre) for membre in option[1])
                + "</optgroup>"
            )
        else:
            choix.append(option_html(option))
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
            entete_de_ligne: bool = False,
            attributs_lignes: list[dict[str, str]] | None = None,
            triable: bool = False, identifiant: str = "") -> str:
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

    ``attributs_lignes`` pose sur chaque ``<tr>`` les attributs donnés — des
    ``data-`` que le filtre de la page lit pour montrer ou cacher la ligne.
    ``triable`` fait de chaque en-tête de colonne un bouton : le script
    d'``index.html`` trie alors les lignes sur cette colonne, et l'en-tête dit
    par ``aria-sort`` dans quel sens. Sans script, le bouton ne fait rien et le
    tableau se lit dans l'ordre où il est écrit. ``identifiant`` nomme la
    grille pour que ses filtres la désignent.
    """
    classes = classes_colonnes or ["" for _ in entetes]
    tete = "".join(
        f'<th class="{cls}" scope="col">'
        + (f'<button type="button" class="tri" data-colonne="{rang}">'
           f"{escape(intitule)}</button>" if triable else escape(intitule))
        + "</th>"
        for rang, (intitule, cls) in enumerate(zip(entetes, classes))
    )
    attributs = attributs_lignes or [{} for _ in lignes]

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
        "<tr"
        + "".join(f' {cle}="{escape(str(val))}"' for cle, val in propres.items())
        + ">" + "".join(
            _cellule(cellule, cls, rang == 0)
            for rang, (cellule, cls) in enumerate(zip(ligne, classes))
        ) + "</tr>"
        for ligne, propres in zip(lignes, attributs)
    )
    legende = f"<caption>{escape(titre)}</caption>" if titre else ""
    nom = f' role="region" aria-label="{escape(titre)}"' if titre else ""
    cible = f' id="{escape(identifiant)}"' if identifiant else ""
    return (
        f'<div class="defilant" tabindex="0"{nom}><table{cible}>{legende}'
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


def fiche(etiquette: str, valeur: str, precision: str = "",
          definition: str = "") -> str:
    """Un chiffre, ce qu'il mesure, et au besoin la phrase qui le situe.

    ``precision`` est du HTML : elle porte parfois un lien ou un mot du
    glossaire. Elle est facultative, et l'immense majorité des fiches du site
    s'en passent — elle n'existe que pour les trois chiffres d'ouverture de la
    page Coût, où « 422 milliards » ne veut rien dire tant qu'on n'a pas dit
    « en un an, pour 17 millions de retraités ».

    ``definition`` fait de l'étiquette un mot du glossaire : « coefficient de
    conversion » ou « capital notionnel » sont des termes de spécialiste, et
    une fiche qui les affiche sans les définir laisse le lecteur devant un
    chiffre dont il ne sait pas ce qu'il mesure. La définition s'ouvre sous
    l'étiquette, comme partout ailleurs sur le site.
    """
    suite = f'<div class="precision">{precision}</div>' if precision else ""
    nom = mot(etiquette, definition) if definition else escape(etiquette)
    return (
        f'<div class="fiche"><div class="valeur">{valeur}</div>'
        f'<div class="etiquette">{nom}</div>{suite}</div>'
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
#: aucune bibliothèque, et la page ne demande aucune ressource tierce — un test
#: du dépôt l'exige. Les originaux sont recopiés sans
#: retouche dans ``moteur/icones/``, et un test vérifie que cette table dit
#: exactement ce qu'ils disent, des deux côtés du portage.
#:
#: Les clés sont les noms de Lucide, en anglais comme les fichiers : c'est ce
#: qui permet de retrouver l'original d'un coup d'œil, et au test de l'ouvrir.
ICONES = {
    "arrow-left": '<path d="m12 19-7-7 7-7" /><path d="M19 12H5" />',
    "chevron-down": '<path d="m6 9 6 6 6-6" />',
    "circle-help": '<circle cx="12" cy="12" r="10" />'
                   '<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />'
                   '<path d="M12 17h.01" />',
    "download": '<path d="M12 15V3" />'
                '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />'
                '<path d="m7 10 5 5 5-5" />',
    "share-2": '<circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" />'
               '<circle cx="18" cy="19" r="3" />'
               '<line x1="8.59" x2="15.42" y1="13.51" y2="17.49" />'
               '<line x1="15.41" x2="8.59" y1="6.51" y2="10.49" />',
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


#: Le glossaire du site : un mot de spécialiste, sa définition en une ou deux
#: phrases de français courant, sans renvoi obligé vers la page Méthode.
#:
#: Il existe pour qu'un terme soit défini UNE fois et de la même façon partout
#: où il reparaît — « répartition » se définissait en deux endroits, avec deux
#: textes. Un mot qui manque ici ne peut pas être posé par :func:`terme`, et
#: le portage JavaScript porte la même table, entrée pour entrée, ce que les
#: témoins des pages vérifient.
#:
#: Aucun chiffre qui bouge n'y figure : un plafond, une durée requise ou un
#: taux de décote écrit ici dériverait sans que rien ne le recoupe.
GLOSSAIRE = {
    "compte notionnel":
        "Un compte virtuel à votre nom, où chaque cotisation versée est "
        "inscrite. Au départ en retraite, le total est divisé par le nombre "
        "d'années qu'il vous reste à vivre en moyenne : c'est la pension. Rien "
        "n'est placé — c'est toujours la répartition, mais la règle de calcul "
        "change.",
    "répartition":
        "Les cotisations d'aujourd'hui paient les pensions d'aujourd'hui. Rien "
        "n'est mis de côté : chaque euro prélevé sur une fiche de paie est "
        "reversé aussitôt à un retraité.",
    "part du PIB":
        "Le PIB, c'est tout ce que la France produit en un an. En « part du "
        "PIB », on demande : sur 100 € produits, combien vont aux retraites ? "
        "C'est la seule façon de comparer 1959 et 2070, l'euro n'ayant pas la "
        "même valeur.",
    "trimestres":
        "L'unité dans laquelle le système actuel compte une carrière : quatre "
        "par année pleine, et un trimestre est acquis dès qu'on a gagné dans "
        "l'année l'équivalent de 150 heures au SMIC. Il en faut un nombre fixé "
        "par génération pour partir sans décote.",
    "durée d'assurance":
        "Le nombre de trimestres qu'une carrière a validés, cotisés ou non : "
        "c'est elle que le système actuel compare à la durée exigée de votre "
        "génération pour servir la pension entière.",
    "décote":
        "La réduction appliquée à toute la pension quand on part avant "
        "d'avoir la durée exigée, tant qu'on n'a pas atteint l'âge du taux "
        "plein. Elle se compte par trimestre manquant.",
    "surcote":
        "La majoration accordée pour chaque trimestre travaillé au-delà de "
        "l'âge légal, une fois la durée exigée atteinte.",
    "taux plein":
        "Le taux de pension entier, sans décote : on l'obtient avec la durée "
        "exigée, ou à l'âge où la décote s'annule quelle que soit la durée.",
    "salaire de référence":
        "Le salaire sur lequel le système actuel calcule la pension : la "
        "moyenne des 25 meilleures années au régime général, le dernier "
        "traitement dans la fonction publique.",
    "table de conversion":
        "La table qui dit combien d'années il reste à vivre, en moyenne, à un "
        "retraité de votre génération à l'âge du départ. Unisexe : la même "
        "pour les femmes et les hommes, bien qu'elles vivent plus longtemps — "
        "un choix de non-discrimination, comme dans le système actuel.",
    "taux de remplacement":
        "La première pension rapportée au dernier revenu d'activité : 60 % "
        "veut dire que la pension vaut 60 % de ce que vous gagniez juste avant "
        "de partir. Ici, un brut sur un brut.",
    "assiette déplafonnée":
        "L'assiette est la part du revenu sur laquelle on cotise. Déplafonnée "
        ": on cotise sur tout le revenu, sans le plafond au-delà duquel le "
        "régime général cesse de compter.",
    "statut d'affiliation":
        "Ce que vous êtes aux yeux des caisses — salarié du privé, "
        "fonctionnaire, artisan, agent de la SNCF… — et qui décide à quels "
        "régimes vous cotisez, donc à quel taux et sous quelle règle. Vous ne "
        "choisissez pas vos régimes : ils découlent de ce statut.",
    "âge de référence":
        "L'âge auquel la pension du régime général est servie entière quelle "
        "que soit la durée cotisée. Le simulateur ne s'en sert que pour "
        "convertir en capital les droits acquis avant la bascule, dans les "
        "scénarios 3 et 5 : partir avant, c'est convertir ces droits comme si "
        "l'on partait à cet âge.",
    "coefficient de conversion":
        "Le nombre par lequel le capital du compte est divisé pour obtenir la "
        "pension annuelle : le nombre d'années qu'il reste à vivre en moyenne "
        "à votre âge de départ, corrigé de la revalorisation à venir des "
        "pensions. Plus on part tard, plus il est petit, plus la pension est "
        "forte.",
    "capital notionnel":
        "Le total du compte au jour du départ : toutes les cotisations "
        "inscrites, revalorisées année après année. Virtuel : aucune somme "
        "n'est placée, le chiffre ne sert qu'au calcul de la pension.",
    "coefficient d'équilibre":
        "Le facteur commun qui, chaque année, ramènerait toutes les pensions "
        "à ce que les cotisations permettent de payer : au-dessus de 1 il en "
        "reste, en dessous il en manque. Le modèle le calcule mais ne "
        "l'applique pas aux pensions affichées.",
    "part patronale":
        "La cotisation que l'employeur verse pour vous, en plus de celle "
        "retenue sur votre salaire. Elle ne figure pas sur le net, mais elle "
        "est bien prélevée sur votre travail.",
    "indexation":
        "La règle qui revalorise chaque année le compte, puis la pension : sur "
        "les prix, sur les salaires, sur la masse des salaires… Le choix pèse "
        "lourd sur quarante ans de carrière.",
    "garantie vieillesse":
        "Le plancher de la proposition : à partir de 65 ans, ce qui manque "
        "pour l'atteindre est versé, payé par l'impôt. Il regarde votre seule "
        "pension, jamais celle du conjoint.",
    "coût du travail":
        "Ce que votre emploi coûte à votre employeur : votre salaire brut, "
        "plus les cotisations qu'il verse par-dessus, moins l'allègement dont "
        "il bénéficie sur les bas salaires. C'est le montant qui ne change pas "
        "quand on déplace une cotisation.",
}


def terme(mot_affiche: str, cle: str = "") -> str:
    """Un mot du glossaire, tel qu'il se lit dans la phrase.

    ``mot_affiche`` est le mot tel que la phrase l'écrit — au pluriel, avec
    sa majuscule —, ``cle`` l'entrée du glossaire quand elle s'écrit autrement
    : ``terme("trimestres manquants", "trimestres")``. Sans clé, le mot est sa
    propre entrée. Un mot absent du glossaire est une faute de programme, pas
    un mot sans définition : il vaut mieux échouer au rendu que livrer un
    bouton qui n'ouvre rien.
    """
    return mot(mot_affiche, GLOSSAIRE[cle or mot_affiche])


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


def depliant(titre: str, corps: str, identifiant: str = "") -> str:
    """Une section repliée : son titre se lit, son contenu s'ouvre si on veut.

    Le temps du lecteur n'est pas gratuit. Tout ce qu'une page doit pouvoir
    justifier — le détail d'un tableau, le périmètre d'une source, ce que le
    calcul ne sait pas faire — doit être là, sans quoi la page n'est pas
    honnête ; mais rien n'oblige à le lui faire traverser pour atteindre le
    résultat. Un dépliant met les deux exigences d'accord : le titre annonce ce
    qu'il y a dedans, et c'est le lecteur qui décide.

    ``identifiant`` le rend joignable depuis le plan de la page (:func:`plan`)
    : le lien du plan l'ouvre et y fait défiler. Sans identifiant, le dépliant
    n'est pas dans le plan — c'est le cas des sections d'une page courte, qui
    n'en a pas.
    """
    cible = f' id="{escape(identifiant)}"' if identifiant else ""
    return (
        f'<details class="section"{cible}>{sommaire(escape(titre))}'
        f'<div class="dedans">{corps}</div></details>'
    )


#: Ce qu'un plan de page sait retrouver : un dépliant identifié et son titre,
#: ou une carte identifiée et sa question. Les deux formes dans une seule
#: expression, pour que le plan les liste dans l'ordre de la page.
_SECTION_DU_PLAN = re.compile(
    r'<details class="section" id="([^"]+)"><summary>.*?<span>(.*?)</span></summary>'
    r'|<section class="cle" id="([^"]+)" tabindex="-1"><h3>(.*?)</h3>'
)


def plan(corps: str, chemin: str, etiquette: str = "Dans cette page") -> str:
    """Le sommaire d'une page longue, DÉDUIT de ses sections.

    Il n'est pas écrit à la main : il est lu dans le HTML déjà rendu, où
    chaque dépliant identifié porte son titre. C'est ce qui garantit qu'il ne
    peut pas dériver — un titre changé, une section ajoutée, et le plan suit
    sans qu'on y pense —, et c'est aussi ce qui le rend identique des deux
    côtés du portage : les deux lisent le même HTML.

    Les liens ne touchent pas à l'adresse. Ici l'adresse EST la route
    (``#/cout``), et un ``href="#une-section"`` renverrait le lecteur à
    l'accueil ; le lien porte donc la route de la page, qui ne change rien, et
    ``data-vers`` désigne la section. Le script d'``index.html`` l'ouvre, y
    pose le focus et y fait défiler — c'est le mécanisme du lien d'évitement,
    étendu au corps de la page. Sans script, le lien ne fait rien, et le
    plan reste ce qu'il est : la liste de ce que la page contient.

    Une page sans section identifiée n'a pas de plan : le vide, plutôt qu'une
    liste vide.
    """
    entrees = [
        (depliant_id or carte_id, titre_depliant or titre_carte)
        for depliant_id, titre_depliant, carte_id, titre_carte
        in _SECTION_DU_PLAN.findall(corps)
    ]
    if not entrees:
        return ""
    liens = "".join(
        f'<li><a href="{lien(chemin)}" data-vers="{identifiant}">{titre}</a></li>'
        for identifiant, titre in entrees
    )
    return (
        f'<nav class="plan" aria-label="{escape(etiquette)}">'
        f'<p class="etiquette">{escape(etiquette)}</p><ol>{liens}</ol></nav>'
    )


def barre_partage() -> str:
    """Les deux gestes du partage, sous une carte ou sous une image à publier.

    Une seule écriture pour les deux endroits où l'on partage — la carte d'un
    graphique et la carte de la page Partager. Elles n'avaient rien en commun :
    l'une posait trois boutons, l'autre demandait une capture d'écran. Le
    lecteur ne voit plus qu'un geste, au même endroit, avec le même libellé.

    Le comportement est dans ``index.html``, en écoute déléguée sur ces classes.
    """
    return (
        '<p class="partage">'
        '<button type="button" class="partager">'
        f"{icone('share-2')}<span>Partager</span></button>"
        '<button type="button" class="partager-x">Publier sur X</button>'
        '<span class="etat" role="status"></span>'
        '<textarea class="repli" hidden readonly rows="3"'
        ' aria-label="Texte à copier à la main"></textarea></p>'
    )


def cle(question: str, reponse: str, corps: str, source: str = "",
        identifiant: str = "") -> str:
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
    # La barre de partage n'est pas un ornement : c'est elle qui fait de la
    # carte autre chose qu'un bloc de page. Elle est SOUS LE RÉSULTAT, et non
    # dans une page « Partager » à part — celle-ci existe toujours, mais « pas
    # grand monde ne va l'utiliser à part les militants qui savent qu'elle
    # existe ». Le partage doit être là où l'on regarde le graphique.
    #
    # DEUX boutons, et non trois. Elle en a porté trois — publier sur X,
    # télécharger l'image, copier le texte —, ce qui demandait au militant de
    # choisir un geste avant d'en faire un seul, et laissait chacun des trois
    # incomplet : l'image sans le message, le message sans l'image. Le premier
    # bouton fait maintenant le tout — il compose l'image ET le message, ouvre
    # la feuille de partage du système quand il y en a une, et à défaut
    # enregistre l'image en mettant le message dans le presse-papiers. Le
    # second reste parce que sur un ordinateur, X est le seul réseau qu'on
    # puisse ouvrir avec un message déjà écrit.
    #
    # Le comportement des deux est dans `index.html`, en écoute déléguée, et
    # il est le MÊME que celui des cartes de la page Partager : un seul jeu de
    # classes, un seul code. Sans lui, les boutons ne feraient rien, et c'est
    # pourquoi un test tient l'accord entre les deux fichiers, bouton par
    # bouton.
    #
    # Le `<span class="etat">` porte le compte rendu — « image enregistrée,
    # texte copié » —, et il est un `role="status"` : le dire dans le libellé
    # du bouton, comme avant, changeait sous le doigt la cible qu'on venait de
    # toucher. Le `<textarea>` est le repli du presse-papiers : quand le
    # navigateur refuse la copie, le texte s'y affiche, sélectionnable, plutôt
    # que d'annoncer un succès qui n'a pas eu lieu. Les deux sont vides et
    # masqués tant qu'on n'en a pas besoin.
    #
    # La barre n'apparaît que si la carte porte un TRACÉ : c'est lui que
    # l'image compose, et une carte qui n'en a pas — celle qui porte un
    # tableau, ou une liste — donnerait un bouton qui échoue. Le savoir se lit
    # dans le corps de la carte plutôt que de se déclarer en paramètre : un
    # appelant n'a pas à redire ce que son propre contenu dit déjà.
    partage = barre_partage() if '<figure class="graphique"' in corps else ""
    # Identifiée, la carte est joignable depuis le plan de la page ; le
    # `tabindex` lui permet de recevoir le focus quand on y arrive par lui.
    cible = f' id="{escape(identifiant)}" tabindex="-1"' if identifiant else ""
    return (
        f'<section class="cle"{cible}><h3>{escape(question)}</h3>'
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
