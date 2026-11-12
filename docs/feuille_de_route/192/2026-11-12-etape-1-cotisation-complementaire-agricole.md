# Étape 1 : la cotisation de retraite complémentaire du chef d'exploitation agricole, depuis 2026

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot des non-salariés agricoles l'a lu
(`184/2026-11-12-etape-6-non-salaries-agricoles.md`, « Ce qui change une règle
») : article D. 732-165, I, du code rural, rédaction du décret n° 2024-688 du
5 juillet 2024 (LEGIARTI000049904700), cotisations des périodes courant depuis
le 1er janvier 2026 ; article D. 732-155 pour les points, P = C / [(1 820 SMIC
× 4 %) / 133]. Posé à la main par ce lot, à revérifier : à un plafond de
revenu en 2026 (48 060 €), 2 787,48 € de cotisation et non 1 922,40 €, environ
424 points et non 292. Collaborateur et aide familial inchangés. La fiche
`assiette_minimale_agricole` le déclare (`textes_a_rattacher`,
`sources.a_relire`).

**Ce qu'il y a à faire.**

1. Relire les deux articles dans l'index, et le barème 2026 de la MSA ; lever
   l'arrondi des points et le cas de l'année incomplète, ou dire ce qui reste
   ouvert.

2. Le test, vu rouge : la cotisation et les points d'un chef d'exploitation en
   2026, à deux niveaux de revenu au moins, valeurs posées à la main.

3. La règle, dans le modèle et son portage, datée du 1er janvier 2026 ; les
   années d'avant ne bougent pas.

4. La fiche, ses versions et ses sources ; la limite, s'il en reste une.

**Fini quand** le scénario 1 sert les points de 2026 que le texte donne, que
la cotisation versée au compte des scénarios rétroactifs suit, et que la fiche
ne déclare plus cet écart.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.

**Ce qui a été fait, le 12 novembre 2026.** L'étape est close : le scénario 1
sert les points de 2026 que le texte donne, et le compte du droit en vigueur
reçoit la cotisation des deux parts.

- *Lu.* D. 732-165 (LEGIARTI000049904700) et D. 732-155 (LEGIARTI000049904715)
  dans l'index LEGI à jour au 11 novembre 2026, sans rédaction postérieure ;
  L. 732-56, dont le premier alinéa du I nomme seul le chef d'exploitation ;
  L. 732-59 et L. 732-60-1, qui laissent les taux à un arrêté ou, à défaut, au
  décret — aucun arrêté ni décret postérieur dans l'index JORF ; les articles
  5 et 6 du décret n° 2024-688. Le barème de 2026 de la MSA, lu par le lot de
  l'action 184, applique les deux parts et ne dit rien des points.
- *Le test, vu rouge* (`tests/test_simulateur.py`,
  `test_la_cotisation_de_rco_du_chef_a_deux_parts_depuis_2026`) : cinq
  revenus, un par pente du taux, posés à la main au SMIC de 12,02 € et au
  plafond de 48 060 € — 12 000 € : 949,96 € et 144,39 points ; 25 000 € :
  1 295,07 € et 196,84 points ; un plafond : 2 787,48 € et 423,67 points ; un
  plafond et demi : 4 613,76 € et 701,25 points ; deux plafonds et demi :
  8 410,50 € et 1 278,31 points. Le compte rendait 875,06 € au premier. Un
  second test garde 2025 (1 922,40 € et 295,63 points à 48 060 €) et le
  collaborateur de 2026 (576,96 € et 88 points).
- *La règle.* Le taux de la seconde part est affine par morceaux : de zéro à
  l'origine, il passe par 1 % à 40 % du plafond, 1,3 % à 60 %, 1,8 % au
  plafond, 3 % à deux plafonds, et y reste. Ses seuils et ses taux sont dans
  une fiche neuve, `cotisation_rco_agricole_2026`, à deux versions que choisit
  l'année de la cotisation ; les deux moteurs la lisent par le paquet
  (`secondePartDeRco` dans `moteur/js/droit/acquerir.js`, `seconde_part_de_rco`
  dans son jumeau). La part porte sur l'assiette d'avant le minimum. Les points
  qu'elle achète, 133 × la part / (1 820 SMIC × 4 %), s'ajoutent à ceux de la
  première ; le compte l'ajoute à sa cotisation. Ni période coupée dans
  `msa_rco.yaml`, ni champ de plus au schéma des régimes : c'est le chemin de
  l'action 191, les règles lues dans les versions des fiches.
- *Les fiches.* `assiette_minimale_agricole` ne déclare plus l'écart : sa
  question ouverte est levée, la rédaction de D. 732-165 quitte ses textes à
  rattacher, que la version de 2026 de la fiche neuve cite. Le cliquet des
  textes baisse d'un cran, à 9 233.
- *Ce qui bouge.* Trois témoins sur 932, les exploitants qui cotisent encore
  en 2026 : leur pension du scénario 1 monte de 0,78 % à 2,63 %. Les scénarios
  de la proposition ne bougent pas : leur compte bascule au 1er janvier 2026
  (`annee_bascule`), et dès cette année le régime fusionné prélève à son taux,
  sans seconde part. La seconde part n'entre donc que dans le compte du droit
  en vigueur sans bascule, celui que le test lit et que lisent les indicateurs
  du cycle de vie. Le jumeau Python refait les témoins au bit près.

**Ce qui reste ouvert**, déclaré dans la fiche neuve (`approximations`,
`sources.a_relire`), et que cette étape n'a pas tranché.

- *L'arrondi des points.* Le texte n'en dit rien, le barème de la MSA non
  plus ; le modèle garde les décimales, comme avant 2026.
- *L'année cotisée au prorata* — celle du décès du chef, celle de R. 731-83.
  Depuis 2026 les points sont ceux de « la cotisation acquittée » : lu à la
  lettre, une telle année n'aurait que les points de ses mois. Le modèle en
  garde au chef ceux d'une année, seconde part comprise, comme avant. La
  pratique de la MSA n'est pas lue ; c'est au propriétaire de dire si le modèle
  suit la lettre sans elle.
- *Le préretraité, l'assuré volontaire et le chef invalide* cotisent 4 % de
  1 820 SMIC sans seconde part (D. 732-165, II) ; le modèle ne les distingue
  pas du chef.
- *L'assiette de 2026* (L. 731-14 dans sa rédaction de 2026, la moyenne
  triennale) : le modèle prend le revenu de la ligne, pour les deux parts.
