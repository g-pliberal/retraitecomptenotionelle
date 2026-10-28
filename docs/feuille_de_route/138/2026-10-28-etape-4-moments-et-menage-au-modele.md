# Étape 4, suite des troisième et dix-septième parties : les moments que la ligne de la réversion a examinés, et si son plafond est celui du ménage, au modèle

**Le 28 octobre 2026, la demande.** La vague du jour, une session par tâche
qui se mène sans le propriétaire : au modèle, ce que deux notes du site ont vu
manquer à la ligne de la réversion, pour que la page le dise sans rien
recalculer — le point 2 du « Ce qui reste » de la note de la période et de son
moment (`2026-10-28-etape-4-periode-et-moment-au-site.md`) : retenues au décès,
ses ressources ne disent pas que la demande l'a été d'abord, refusée ; le point
2 de celle des révisions (`2026-10-28-etape-4-revisions-au-site.md`) : la ligne
ne dit pas si son plafond est celui du ménage. Les deux champs, dans les deux
moteurs, confrontés ; la page qui les dira viendra à une session du site.

**Ce qui est fait.**

- *Les moments examinés* (`moments_examines`) : ceux dont la version a examiné
  les ressources, dans l'ordre, jusqu'à celui qui a décidé
  (`ressources_examinees_au`), le dernier ; aucun de ceux qui le précèdent ne
  remplissait la condition. Avant juillet 2004, `["demande", "deces"]` quand la
  demande, présumée le mois qui précède la date d'effet, est refusée et que le
  décès ouvre la réversion, ou la ferme encore ; `["demande"]` quand elle
  l'ouvre ; `["deces"]` avant le 1er juillet 1974, qui n'examine que lui ;
  depuis juillet 2004, `["date_d_effet"]`, ses trois mois puis ses douze au
  même moment. Vide sans ce moment : sans plafond, et à la complémentaire des
  indépendants, qui ne le dit pas.
- *Le plafond du ménage* (`plafond_du_menage`) : le survivant vit en couple au
  jour que le plafond mesure, et les ressources de son nouveau conjoint
  s'ajoutent aux siennes — sous 1,6 fois le plafond d'une personne seule au
  régime général, sous le même à la complémentaire des indépendants. Non quand
  l'union se forme après la date d'effet, que la révision qui suit compte, ni
  avant juillet 2004. Le facteur du plafond n'y suffisait pas : celui de la
  complémentaire des indépendants vaut 1 pour un ménage aussi. Les deux
  fonctions qui choisissent le plafond (`_ressources_de_la_periode`,
  `_ressources_du_plafond`) rendent donc ce qu'elles ont choisi, et
  `_ressources_a_la_date_d_effet`, avec les moments, le transmet à la ligne.
- *Le portage* (`moteur/js/droit/reversion.js`) : les mêmes champs, aux mêmes
  endroits. Le paquet n'a rien de neuf à porter : les moments des versions
  (`ressources_examinees`) et leur facteur (`facteur_menage`) y sont déjà.
- *Les tests* (`test_reversion.py`), posés à la main depuis R. 353-1 et
  D. 353-1-1, vus rouges : la veuve de 1996 refusée à sa demande, que son décès
  ouvre ; celle que les douze mois de sa demande ouvrent ; la veuve de 1972, au
  décès seul ; la veuve de 2010, ses trois mois puis ses douze à la date
  d'effet ; le survivant de 2023 seul, pacsé sans dire les ressources de
  l'autre, puis avec elles ; le survivant remarié de 1999 ; celui de la
  complémentaire des indépendants, en concubinage en 2026, sous le même
  plafond ; le survivant de 2015 marié en mai 2018 ou en janvier 2021, après sa
  date d'effet. Les deux moteurs : `CAS_DE_LA_DEMANDE` dit les moments de ses
  trois cas, et `CAS_DU_MENAGE`, neuf, quatre cas — la veuve pacsée en 2023
  sans dire depuis quand, la même pacsée en janvier 2024, après sa date
  d'effet, la veuve de l'artisan en concubinage, la veuve remariée de 1999 —,
  chaque ligne qui a un plafond avec ce qu'elle doit dire.

**Les mesures.** `test_reversion.py` passe entier, 350 tests, dont les neuf
confrontations des deux moteurs ; les confrontations légères de la zone
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), 405. Sur les fichiers fabriqués de `main`, périmés
ici, la suite rapide échoue aux sept confrontations que les notes du jour
disent (le pont, les coupures au mois, la surcote parentale, le cycle de vie)
et à une huitième, `test_les_temoins_simulent_au_moteur_python_la_carriere_que_le_portage_batit`,
dont le témoin figé n'a pas encore les deux champs. Le paquet et les témoins
refaits ici, les huit passent, et seules échouent les pages toutes faites, à
refaire après eux, qui passent refaites ; sur ces fichiers, `-m site` passe,
et les confrontations du portage de `test_web.py`, carrières tirées au hasard
comprises — celle des témoins du portage se tait sur des témoins qu'on vient
de refaire. Des 47 témoins qui ont une réversion, aucun ne bouge hors des deux
champs : 136 lignes les portent, une au plafond du ménage, aucune dont la
demande soit refusée, d'où les cas posés à la main. Les fichiers fabriqués ne
sont pas commités : la fabrique de GitHub les refait.

**Ce qui reste.**

1. *Au site*, la page qui dit les deux champs, sans rien recalculer : la
   demande examinée d'abord, refusée, et la présomption qui la date, quand
   `moments_examines` porte la demande avant le décès ; « avec les ressources
   du ménage » au motif de la ligne écrêtée, seulement quand
   `plafond_du_menage`. Les pages n'ont pas été touchées.
2. *Au modèle*, vu en chemin : les révisions ne disent pas si leur plafond est
   celui du ménage. `_revisions` le sait, ce que les deux fonctions du plafond
   rendent désormais, et ne le garde pas ; la carte écrit « révisée sur […] de
   ressources par an » sans dire si celles du nouveau conjoint y sont. Un champ
   par révision le dirait, si la page le veut.
3. *Au propriétaire*, inchangé : les décrets agricoles de 1976 et 1977 ; le
   choix de la date de la demande ; le décès supposé avant l'enfant né après
   lui.
