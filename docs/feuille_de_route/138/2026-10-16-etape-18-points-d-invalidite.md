# Étape 18, quatrième partie : les points d'invalidité des artisans et des commerçants

**La demande.** La session n° 4 de la vague du 16 octobre 2026 : « action 138,
étape 18 : les points d'incapacité des artisans et des commerçants (RCI), lus à
la source et calculés dans les deux moteurs ». Le conjoint collaborateur, les
dispenses de l'assiette minimale, la Lodeom et les classes d'avant 1973 restent
à d'autres sessions. `pages.js`, la saisie, `castypes.py` et `cout.py` n'ont pas
été touchés ; la liste des textes non plus (`textes.py --inscrire`).

**Ce que faisait le dépôt.** Une année `invalidite` d'un artisan ou d'un
commerçant validait ses trimestres au régime de base, mais n'ouvrait rien à sa
complémentaire : la ligne n'a de familles cotisantes que celle des salariés.
Le registre ne nommait que les 400 points d'incapacité de la CNAVPL (libéraux),
coupés le 14 octobre.

**Ce que disent les textes**, lus le jour même dans l'index JORF du dépôt (le
règlement du RCI est un arrêté, absent de LEGI).

- *Le RCI, depuis 2013.* Article 9 du règlement (arrêté du 9 février 2012) :
  « pour chaque mensualité de pension d'invalidité ou d'incapacité au métier,
  que cette prestation soit ou non versée », le quotient, « établi à la
  seconde décimale », des points cotisés « au plus tard à la date d'arrêt du
  compte » de la pension par les « mois civils entiers d'activité » arrêtés à
  la même date. L'arrêté du 19 juin 2024 précise la pension (totale et
  définitive, ou d'incapacité partielle, du régime de L. 632-1) et les mois
  (ceux qui ont « donné lieu à appel de ces cotisations »), et ajoute : « Si
  l'assuré n'a pu acquérir aucun point cotisé […], il lui est octroyé deux
  points gratuits par mois d'invalidité. » Les arrêtés de 2025 et de 2026
  n'y touchent pas.
- *Avant 2013.* L'annexe 1, 3, du même règlement reprend les deux anciens :
  l'artisan avait, par trimestre de pension, seize points s'il n'avait rien
  cotisé à la RCO, sinon le quotient au centième de ses points depuis 1979 par
  ses trimestres cotisés ; le commerçant, deux points par mois.
- *Le financement.* Le régime d'invalidité-décès verse au RCI le nombre de ces
  points fois le revenu de référence (article 47 de ses règlements de 2018,
  2023 et 2026 ; R. 635-10 de 2013).

**Ce qui est fait.** Un champ de période, `points_invalidite` (`par`,
`proportionnels`, `forfait`, `forfait_depuis`), déclaré au schéma des fiches et
porté par la première tranche du RCI, chaque période de la RCO des artisans et
du NRIC ; `PointsInvalidite` dans `donnees/regimes.py`, transmis au paquet
seulement là. `acquerir.points_d_invalidite`, et son jumeau
`pointsDInvalidite`, créditent au régime de la ligne d'invalidité, l'année de
la ligne, le quotient (ou le forfait) fois ses mois retenus. Le compte de la
pension s'arrête au 1er janvier de la première année de la suite d'années
d'invalidité ; les points cotisés sont ceux du régime et de ceux qu'il reprend
(au coefficient de fusion : 0,2778 pour la RCO des artisans, 1 pour le NRIC),
les mois ceux des lignes cotisées que ces régimes couvrent. Le compte
notionnel n'en porte rien. Fiche `points_invalidite_independants`,
`transcrite` : aucun exemple chiffré publié. Sept tests dans
`tests/test_independants.py`, dont la comparaison des deux moteurs sur trois
invalides.

**Ce que montrent les mesures** (scénario 1, salaire moyen, départ à 62 ans).

- Artisan né en 1962, à son compte depuis 1984, invalide de 2016 à 2023 :
  10,38 points par mois ; pension RCI de 538 € à 1 712 € par an, quand
  l'artisan resté actif en a 2 047 €.
- Commerçant né en 1958, invalide de 2008 à 2019 : NRIC de 554 € à 686 €
  (24 points par an), RCI de 14 € à 985 €.
- Artisan né en 1955, invalide de 1995 à 2016 : RCO de 1 933 € à 4 107 €,
  RCI de 15 € à 498 €.

**Conventions déclarées** dans la fiche : l'année comme unité (les mois d'une
ligne ne sont pas datés ; le forfait couvre la moitié de 2024) ; toute ligne
`invalidite` de l'indépendant vaut pension de son régime d'invalidité ; le
commerçant commence avec le NRIC, en 2004.

**Ce qui reste** de l'étape, une session par point : le conjoint
collaborateur ; les dispenses de l'assiette minimale ; la Lodeom ; au
fac-similé, les classes d'avant 1973. Pour ce point-ci, à relire : les
règlements d'origine (arrêtés du 15 décembre 1978 et du 17 décembre 2004),
qu'aucun index ne porte ; un exemple chiffré de la caisse ; ce que « points
cotisés » compte des points repris en 2013 — le dépôt les y met, à leur
coefficient. Les 400 points de la CNAVPL (libéraux) restent coupés.
