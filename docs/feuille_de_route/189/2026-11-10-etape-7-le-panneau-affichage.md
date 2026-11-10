# Étape 7 : le panneau « Affichage »

**D'où elle part.** Le propriétaire, le 9 novembre 2026, voulait que le site
« reprenne encore plus l'aspect » de son autre site, « Fonction publique : les
chiffres » (`g-pliberal/Nombre-de-fonctionnaires`), et avait retenu, de son
panneau « Affichage », la taille du texte, la police très lisible et
l'interligne, sans le thème sombre (note de l'étape 4). Le panneau s'y lit dans
`index.html` (`#options-affichage`), `assets/js/app.js` et
`assets/css/style.css` (`.options`, `.choix`, « Options d'affichage choisies
par le visiteur »).

**Ce qui est fait** (`moteur/js/gabarit.js`, `moteur/js/routeur.js`,
`moteur/page.html`, `moteur/style.css`).

- **Le bouton « Affichage »** du bandeau, à droite de la marque, au filet
  blanc, de 44 points : le pictogramme des réglages (`settings`, de Lucide)
  et le mot, que le téléphone ne laisse qu'aux synthèses vocales, comme celui
  du menu. La marque et le bouton partagent la première rangée, les onglets
  la suivante.
- **Le panneau** (`panneauAffichage`) : un dialogue, carte blanche arrondie
  sur le fond assombri, trois réglages en pastilles rondes dont la cochée est
  pleine de pétrole — la taille du texte (normale, grande, très grande), la
  police (standard, très lisible), l'espacement (normal, aéré) —, « Fermer »,
  « Rétablir les réglages par défaut », et une phrase : « Ces choix restent
  dans votre navigateur : rien n'en sort. » Il se ferme aussi par Échap et par
  un clic sur le fond. La page le porte hors de l'en-tête, que le routeur
  récrit à chaque rendu.
- **Les réglages** sont des attributs sur `<html>`, ceux du parti
  (`data-taille`, `data-police`, `data-interligne`), que la feuille de style
  lit. La taille grandit la racine dans la proportion du parti, de 17 points à
  20 puis à 24 : tout ce qui s'écrit en `rem` suit, titres et boutons compris.
  La police très lisible est Atkinson Hyperlegible, pour le texte et les
  titres (`moteur/polices/`, sous sa licence OFL). Le texte aéré prend
  l'interligne de 1,9 et l'espacement des lettres et des mots du parti.
- **La mémoire** : le stockage local du navigateur, sous
  `retraite-notionnelle.affichage`, à côté de la saisie du simulateur ; rien
  n'y reste quand tout est revenu au défaut. Un script d'en-tête de la page
  repose les réglages avant la première peinture, sur les neuf pages, et
  précharge alors la police très lisible ; le routeur les repose aussi, pour
  une politique de sécurité qui refuserait ce script.

**Ce qui s'écarte du site du parti, et pourquoi.**

- Pas de thème sombre : décision du propriétaire.
- Chez le parti, seul le texte courant grandit, ses titres restant en `rem`.
  Ici la racine grandit, et tout avec elle : les tailles du site sont une
  échelle en `rem`, et n'en grandir qu'un pas l'aurait écrasée — un intertitre
  de 26 points sur un téléphone sous un texte de 24.
- La colonne ne grandit pas avec le texte : sa largeur, sa marge et le retrait
  d'une carte de figure se comptent en `--point`, le rem d'avant le réglage.
  Sans cela, le texte agrandi rognait sa propre place, et un texte de tracé
  tombait à 10,5 pixels sur un téléphone.
- **Un texte de tracé ne grandit pas** : il suit son dessin, non le réglage, et
  reste entre 11 et 16 pixels (étape 6). Le faire grandir demanderait de
  redessiner chaque graphique par le moteur, pour une colonne plus étroite
  qu'aucun écran essayé.
- Sous un texte agrandi, le bandeau ne colle plus — ses onglets passent sur
  deux rangées — et les deux branches d'une bascule passent à la ligne.
- Une carte à publier garde ses polices et son espacement : c'est une image,
  la même chez tous.
- Le panneau s'intitule « Affichage », comme son bouton, et la police se dit
  « Très lisible », sans son nom.
- Sans JavaScript, le bouton est là et n'ouvre rien : la page ne porte qu'un
  style, et rien ne l'y cache.

**Les tests.** Dans `tests/test_ecrans.py`, joués dans Chromium à 390 et à
1 440 points par une course du pilote (`tests/js/ecrans.mjs`, qui sait
désormais noter des mesures en chemin et choisir son écran) :
`test_le_bandeau_ouvre_le_panneau_affichage`,
`test_chaque_reglage_de_l_affichage_s_applique_aussitot` et
`test_les_reglages_de_l_affichage_suivent_le_lecteur_sur_les_neuf_pages` —
réglées au plus fort, les neuf pages gardent les réglages, ne se décalent pas
en s'ouvrant, ne débordent pas en largeur, et leurs tracés restent lisibles.
Sans navigateur : le bouton, le panneau et ce qu'il affirme
(`tests/test_web.py`), le script d'en-tête et les règles que chaque page porte
(`tests/test_pages_en_dossier.py`). Vus rouges d'abord. Vérifié à l'écran à
1 280 et à 390 points, à côté du site du parti.

**Ce qui reste.** Rien de l'aspect : les étapes 4 à 7 sont faites. Les témoins
de pages et le paquet restent à GitHub, comme à l'étape 6.
