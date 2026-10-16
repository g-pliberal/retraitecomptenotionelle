# Mon-entreprise et les API publiques : vingt lignes, rien qui contredise le dépôt

**Le 16 octobre 2026 : vingt lignes réservées (85a2174), puis dépouillées.**
Ce sont les sept de mon-entreprise (la bibliothèque, le dépôt du code, l'API
et quatre simulateurs : le comparateur des statuts, l'indépendant,
l'auto-entrepreneur, l'artiste-auteur) et les treize API publiques sondées le
5 octobre (les cubes du SRE, Gallica, six sites WordPress de caisses, deux
Drupal servis en JSON, deux jeux de la DREES, Légifrance par PISTE). Sept
passent à `epuise`, onze à `explore`, deux restent `a_explorer`.

- *Mon-entreprise : déjà lu, et inchangé.* Les trois modèles publicodes
  (`modele-social`, `modele-ti`, `modele-as`) ont leur entrée au registre,
  lue le 4 octobre au commit `05cb5be`. Le dépôt, recloné au commit `77836ae`
  du 15 octobre, n'a changé aucune règle depuis : `git diff` vide sur les
  modèles et l'API ; ses 36 commits touchent la Lodeom, le comparateur et
  l'intégration continue. Les écarts du registre tiennent.
- *Ses taux de 2026, relus contre le dépôt : tout concorde.* Vieillesse
  plafonnée 6,90 + 8,55 %, déplafonnée 0,40 + 2,11 %, Agirc-Arrco, CEG, CET,
  PSS 4 005 € : ceux de `taux_cotisation_annuels.csv` (certifiés sur D. 242-4)
  et d'`agirc_arrco.yaml`. Indépendants (`modele-ti`) : 17,87 % sous le
  plafond et 0,72 % au-delà, le barème de D. 633-3 que le dépôt écrit
  17,15 % + 0,72 % sur la totalité ; RCI 8,1 et 9,1 %, comme `rci.yaml`.
  Micro-social : taux globaux et parts de base de
  `legislation/micro_social.yaml`. Seul écart, déjà au registre : Mayotte
  (5,54 + 9,90 %, sans déplafonnée, son propre plafond), que le dépôt traite
  comme la métropole (138.18).
- *Les simulateurs et l'API n'ont pas été saisis.* Chacun évalue un modèle
  dont le code est lu ; une saisie rejouerait ce code. Aucun lot n'est
  proposé au propriétaire ; s'il veut des exemples signés de l'Urssaf, le
  simulateur de l'indépendant (trimestres et points) serait le seul à
  demander.
- *Les cubes du SRE sont le jaune en CSV.* Le stock civil de 2025 rend
  1 656 399 pensions et 2 478 € par mois, les valeurs d'A-1 que le dépôt
  tient de l'édition 2027 ; les pensions moyennes de 2016 à 2025 sont celles
  d'A-4, à l'euro ; les effectifs d'A-3 à quelques dizaines près. Les cubes
  ne portent que des sommes, à diviser par l'effectif. Rien n'entre ; les
  cubes par génération attendent une population (138.14).
- *La DREES.* Le minimum vieillesse 2024 : 754 460 allocataires de l'ASV ou
  de l'Aspa, 4 586 millions d'euros, 253 de plus au premier étage ; les
  Comptes de la protection sociale, au dépôt, en portent 4 941 (2 % de
  plus). Les quantiles du taux de remplacement (premières années pleines de
  2012 à 2020) décrivent une population appariée aux revenus fiscaux, non des
  cas types : pour 138.14.
- *Les sites des caisses.* Les WordPress refusent l'agent par défaut de curl
  et servent celui des scripts du dépôt. Depuis les lots de septembre, rien
  de réglementaire n'a été publié : formulaires, bulletins, organigrammes.
  Les règlements qu'ils servent en PDF (CAVOM au 1er juillet 2026, textes de
  la CAVAMAC, statuts de la CPRN et de la CNAVPL) ne sont pas cités au dépôt,
  qui lit les mêmes règles par leurs arrêtés au Journal officiel ou dans
  LEGI. Le guide 2026 de la CPRN confirme sa fiche sans la compléter : les
  bornes des classes B ne sont toujours publiées nulle part. Les Drupal :
  aucune page de l'Ircantec n'a bougé depuis sa lecture ; deux de la Cipav
  oui, dont `cipav_cotiser` (13 octobre), qui donne maintenant le seuil de
  2 792 € par trimestre de l'auto-entrepreneur, celui du dépôt.
- *Ce qui bloque.* Gallica, ouvert le 5 octobre, répond maintenant 403
  derrière Cloudflare : la ligne passe à `navigateur`. L'API de Légifrance
  attend toujours un compte PISTE du propriétaire.
- *Fichiers.* `data/sources_a_explorer.yaml`, cette note et l'entrée du
  journal de veille. Ni fiche, ni témoin, ni page : le scénario 1 n'est pas
  touché.
