# Étape 8, seconde partie : la figure 3B lue sur ses tracés, certifiée, et ministère par ministère sur la page Coût

**La demande.** Le propriétaire, le 14 octobre 2026 : « fin de l'étape 8
action 159 ». Ce qui restait au premier point de la première partie : la
figure 3B en entier, par un fichier de données certifié contre le texte du
jaune, puis sur la page Coût.

Le document est celui de l'étape 1 (`sre_jaune_pensions_2027`), tiré de la
branche `jaune-2027` dans le répertoire de travail de la session, son
empreinte vérifiée. Les pages citées sont celles du PDF.

## Les tracés, lus par le dépôt

La première partie avait lu la figure par `pdftocairo -svg`, hors des
dépendances du dépôt. Le lecteur PDF du dépôt la lit désormais lui-même, en
Python seul, et rend les mêmes parts au dixième de point.

- **`lecture_pdf.aplats_de_page`** rend les rectangles qu'une page remplit ou
  trace, en points de la feuille, avec leur peinture : une couleur, ou un
  motif hachuré nommé par la page. La page se trouve par l'arbre des pages :
  les lectures de texte numérotent les flux dans l'ordre du fichier, 265 pour
  250 pages, et la page 24 y est la 23e. Son `/Contents` désigne un objet qui
  n'est qu'un tableau de trois flux, dont le premier ramène la feuille à
  99,88 % de sa taille ; la matrice courante, que `q` et `Q` sauvent et
  rendent, porte chaque point. Une courbe n'est pas un rectangle, et une
  découpe ne peint rien : la barre qu'elle rogne garde sa longueur entière.
  Un document fabriqué à la main le tient (`tests/test_lecture_pdf.py`).
- **`scripts/fetch/sre_jaune_ministeres.py`** lit la figure. L'échelle se
  prend sur l'axe, non sur les barres : le trait de 0 % et ses dix
  graduations, dont la dernière est posée un vingtième de point trop à gauche,
  d'où un pas pris sur leur médiane. Le producteur pose ses points sur une
  grille de 0,12 point, un six-centième de pouce, 2 100 pas sur l'axe : chaque
  part se lit à un vingtième de point près. Les cinq peintures — trois motifs,
  P631, P633 et P635, puis un bleu et un gris — se rattachent à leurs parts
  par l'empilement : chaque part commence où finit la précédente, à un pas
  près, ce qui admet aussi les segments d'épaisseur minimale des derniers
  ministères. Les libellés se confrontent au texte de la page sur leurs seules
  lettres sans accent, la police n'ayant pas toutes les accentuées, et la
  légende dans son ordre. `sre_jaune_pensions.py` l'appelle pour l'édition
  2027 et écrit la table « 3B » dans son JSON.

## Ce que le texte en dit

Vingt-deux chiffres du texte se confrontent à la lecture
(`CHIFFRES_DU_TEXTE`) : la synthèse (page 7) et l'éditorial (page 10), 32 % et
28,5 milliards pour l'Éducation nationale, 30 % pour l'Intérieur ; les
figures B et B bis (pages 11 et 12), leurs milliards, leurs parts et ce que
les pensions prennent de la masse salariale, 34 et 41 % ; la lecture de la
figure (page 24), 28, 4, 63 et 5 % ; les deux derniers ministères sous 1 % ;
la Justice et l'Éducation nationale aux bornes de « entre 18 et 28 % »
(page 25). Tout tombe dans l'arrondi du texte, à un pas du tracé près — le T2
CAS de l'Intérieur, 27,00 %, au bord de 9,3 milliards sur 34,2 —, sauf deux
points, déclarés (`INCOHERENCES_3B`, à part de la liste des référents, dont un
test tient le compte) :

- **la barre de l'Enseignement supérieur fait 119,1 % de l'axe** : son reste
  des dépenses, 98,4 %, compte aussi les 19,1 points de son T3 CAS, versés
  sur des crédits de fonctionnement, et le cadre du graphique la rogne à
  100 % ;
- **la borne basse de « entre 20 % et 32 % »**, page 25, ajoute les parts
  arrondies de la Justice, 18 et 2 %, quand la figure en trace 20,9.

## Le fichier certifié

`data/reference/macro/credits_ministeres.csv` porte les soixante-neuf parts —
quatre par ministère, et le T3 CAS de l'Enseignement supérieur —, au niveau
`certifiee`, telles que la figure les trace, sous la clé (année des crédits,
ministère, part). Six décimales, celles du lecteur : un premier arrondi au
dix-millième faisait d'une part de 1,048 point une de 1,05, que la page
montrait à 1,1. Le manifeste le range sous `sre_jaune_pensions_2027`, et
`memoire.HORS_DU_MODELE` l'écarte de l'empreinte : aucun calcul ne le lit.
Le contrôle du fichier contre le texte se rejoue sans le PDF
(`tests/test_sre_jaune_ministeres.py`).

## Sur la page Coût

Le dépliant « D'où vient l'argent, poste par poste » finit sur les dix-sept
ministères, du plus au moins versé au compte « Pensions » : la contribution
de l'État (T2 et T3 CAS), la retenue des agents, leur somme, et les autres
dépenses de personnel, qui montrent ce que le document affirme — plus un
ministère emploie de personnel, plus il verse. Sous le dixième de point, la
case dit « < 0,1 % ». Le reste des dépenses n'y est pas : il est le
complément des autres colonnes, et celui de l'Enseignement supérieur est la
part fausse. Une note dit les 19,1 points des opérateurs de l'Enseignement
supérieur, et l'absence de la Santé et des Transports.

La page lit le paquet, dont la version passe à 20 des deux côtés : le
lecteur `donnees/credits_ministeres.py` et son jumeau
`moteur/js/credits-ministeres.js`, préchargé par `index.html`. Un test de
`test_web.py` exige que les deux rangent et somment de même, et que chaque
case soit celle du fichier. La phrase de la première partie, au glossaire du
même dépliant, ne change pas ; le paragraphe du tableau ne revendique que ce
que la lecture retrouve, les parts de l'Éducation nationale et de l'Intérieur.

## Ce qui reste

1. *L'expérience de la DREES refaite par le modèle*, sur la page : au
   propriétaire de dire s'il la veut, et sous quelle forme (première partie,
   « Ce que le modèle en dit »).
2. *Le taux de remplacement de la DREES* reste cité, non confronté, pour les
   raisons de la première partie.
3. L'étape close, aucune étape de l'action ne tient plus de bloc « Reprise » :
   l'action peut se clore, sa section et ses notes passant aux archives, dans
   une session à elle, une fois le premier point tranché.
