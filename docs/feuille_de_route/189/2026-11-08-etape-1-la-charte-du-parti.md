# Étape 1 : la charte du parti

**Ce qui est fait.** Le site quitte l'affiche vert profond de septembre 2026
pour la charte du site « Fonction publique : les chiffres » du parti
(`g-pliberal/Nombre-de-fonctionnaires`, `assets/css/style.css`), que le
propriétaire trouvait « beaucoup plus [au] style du parti ».

- **Les couleurs** (`moteur/style.css`, `:root`) : la page claire (`--fond`
  gris-vert très clair, cartes blanches), le texte pétrole presque noir, le
  turquoise sombre des liens, le safran qui décore et ne s'écrit plus sur le
  clair (`--or-texte`, `--sur-or`, `--focus`). Les noms des variables n'ont
  pas changé : c'est la surface publique de la feuille.
- **Les zones pétrole** : le bandeau de tête, l'affiche de chaque page — une
  bande d'un bord à l'autre de l'écran, par une ombre portée et un
  découpage, qui n'élargit pas la page — et les cartes à publier
  redéfinissent les mêmes variables pour elles.
- **Le bandeau** (`entete`, `moteur/js/gabarit.js`) : le logo du parti
  (`moteur/logo-plf.svg`, repris de son site), son nom, `NOM_DU_PARTI`, et
  celui du site dessous ; les onglets en pastilles, l'onglet courant plein de
  safran.
- **Les polices** : Jost, la police des titres du parti, remplace Instrument
  Serif (supprimée), pour les titres, les chiffres clés et le nom du parti ;
  Public Sans reste au texte. Le titre passe de 88 à 56 points au large.
- **Les cartes** : les quatre engagements de l'accueil, les chiffres
  d'ouverture, les questions de la page Coût, les points, le plan d'une page
  longue deviennent des cartes blanches arrondies au filet de safran ; les
  intitulés en capitales noires de l'affiche passent en casse de phrase.
- **Les graphiques** : les quatre systèmes gardent leurs familles de
  teintes — aujourd'hui en bleu, les comptes rétroactifs en cyan et en
  grenat, la proposition en or assombri —, mesurées par
  `test_la_palette_des_scenarios_reste_lisible`, dont la bande de clarté est
  désormais celle du fond clair ; les neuf séries, refaites pour le blanc.
- **L'image d'aperçu** (`scripts/fabriquer_apercu.py`, `moteur/apercu.png`) :
  fond pétrole, logo et nom du parti, titre en Jost.

**Les tests.** `test_chaque_page_porte_la_charte_du_parti`
(`tests/test_ecrans.py`, mesuré par `tests/js/ecrans.mjs`) et
`test_l_image_d_apercu_porte_la_charte_du_parti`, vus rouges d'abord. Les
contrôles d'écran déjà là tiennent la refonte : contraste de chaque texte sur
son fond, rien qui déborde, aucun grand vide, l'échelle de l'accueil.

**Ce qui reste.** Le second reproche du propriétaire, un site « très
compliqué à comprendre pour l'électeur », tient au texte plus qu'au style :
c'est l'étape 2. Le panneau « Affichage » du site du parti (thème sombre,
police très lisible, taille du texte) n'est pas repris.
