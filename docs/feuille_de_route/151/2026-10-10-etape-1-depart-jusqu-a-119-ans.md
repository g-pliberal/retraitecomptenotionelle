# Étape 1 : le départ jusqu'à 119 ans

**Le 10 octobre 2026 : la saisie accepte un départ jusqu'au dernier âge que
les tables de mortalité convertissent en rente.**

- *La borne.* `AGE_LIQUIDATION_MAXIMAL` (`saisie.py`, `saisie.js`) valait 75 ;
  elle vaut l'âge terminal des tables moins un, 119 ans, et se lit sur
  `AGE_TERMINAL` des deux côtés (`donnees/mortalite.py`, `mortalite.js`) : la
  saisie ne peut plus accepter un âge que la conversion refuserait. À 120 ans,
  nul ne survit plus, et le diviseur du compte notionnel est nul. Ce qui en
  dérive suit : la dernière année d'une carrière passe de 2095 à 2139, la
  longueur d'un relevé de 63 à 107 lignes (`RELEVE_MAXIMUM`, désormais
  calculée sur la borne), et la date d'une demande de pension par régime ou du
  début d'une pension étrangère, de 75 à 119 ans. Le calendrier du départ
  s'ouvre jusqu'à 119 ans, et le refus le dit : « de 40 à 119 ans ».
- *Ce qui ne suit pas.* Le lecteur de relevés (`web/releve_lu.py`,
  `releve-lu.js`) garde ses années, de 1914 à 2095 : un relevé n'écrit que des
  années vécues, et élargir la fenêtre ne ferait que prendre plus de nombres
  pour des millésimes. Son commentaire, qui les disait reprises de la saisie,
  le dit désormais.
- *Les deux moteurs.* Le Python calcule sans erreur des départs à 100, 110 et
  119 ans, pour six statuts et les générations 1900, 1950 et 2020 ; le site,
  rendu par node, une carrière née en janvier 2020 et partie en février 2139.
  Deux témoins de simulation naissent, `liquidation_90` et `liquidation_119`,
  et le portage les retrouve ; aucun autre ne bouge. Treize rendus de page
  changent, du seul fait des calendriers — leur date maximale et leur
  `data-age-max` — et du refus qui cite la borne.
- *Les tests.* `test_web_saisie.py` : au départ le plus tardif, le diviseur
  est encore positif pour la génération la plus ancienne comme pour la plus
  jeune, et nul un an plus tard ; le site simule le départ le plus tardif de
  la génération la plus jeune. Les refus qui supposaient 75 ans — un départ à
  90 ans, une demande de pension en 2036, une pension étrangère qui commence en
  2045 ou en 2051 — passent au-delà de la nouvelle borne, et se calculent sur
  elle.
- *Ce que les départs très tardifs atteignent pour la première fois.* Des
  règles du scénario 1 que rien ne visitait à ces âges, à relire au texte :
  - la limite d'âge des fonctionnaires, que le modèle n'applique pas : un
    fonctionnaire de l'État se simule en activité, surcote comprise, jusqu'à
    119 ans ;
  - la majoration de la CARMF complémentaire avant 2017, « 5 % par année
    pleine de différé » au-delà de 65 ans, que la fiche ne plafonne pas : un
    médecin né en 1900 et parti à 116 ans, en 2016, en compte cinquante et une
    années ; parti en 2017, sous le plafond de 70 ans de la retraite en temps
    choisi, sa pension complémentaire tombe de 43 255 à 13 879 € ;
  - le régime général d'une carrière née en 1900 : parti à 103 ans en 2003, au
    taux de 140 %, un salarié non cadre touche 38 946 € de pension de base ;
    parti en 2004, au même taux, 14 856 €.
- *Ce qui reste.* L'étape 2 : la limite d'âge des fonctionnaires et chacune de
  ses exceptions, texte en main (le plan de l'action) ; les deux règles
  ci-dessus, à la même occasion.
