# Les complémentaires au modèle : chaque caisse projetée jusqu'à l'épuisement de ses réserves

**Reprise, au 7 novembre 2026.** L'étape 1 est faite : chaque complémentaire
est projetée de 2026 à 2070 sous les décisions 36 à 48 et 67
(`integration_complementaires.py`, ses tests et trois fichiers de données).
L'ordre d'intégration : la complémentaire agricole en 2026, l'Agirc-Arrco en
2032, la CNBF en 2042, l'Ircantec en 2055 ; les indépendants, les libéraux et
les navigants, jamais avant 2070. Restent quatre questions au propriétaire
(« Ce qui reste au propriétaire »), puis l'étape 2, le moteur d'une carrière,
`moteur/js/` d'abord, dans une session neuve, quand celle du chantier 5 aura
quitté le moteur ; puis l'étape 3, le coût et le site (« Le plan »).

*Le 7 novembre 2026, une session du modèle ouvre le portage des décisions du
chantier 6 de `docs/feuille_de_route_programme.md` (décisions 36 à 43, 47 et
48), sur la note `186/2026-11-07-complementaires-etude.md`. Cette étape-ci est
la première des trois : la projection caisse par caisse, en Python, côté
données et coût. Elle a lu le classeur des compléments du rapport du COR de
juin 2024, le tableau 2.3 de son rapport de juin 2026, le Chiffr'Agirc-Arrco
2026, la fiche CNBF du COR et l'article L. 723-3 du code de la sécurité
sociale (index LEGI de la DILA, à jour au 2 novembre 2026). Le propriétaire a
tranché en cours d'étape la lecture des droits sur les alcools (décision 67).*

## L'essentiel : l'ordre que le modèle calcule

Une caisse rejoint le régime général l'année où ses réserves passent sous zéro
(décision 37). En part de PIB, chaque année, ses réserves suivent la
trajectoire que le COR projette à législation inchangée, moins ce que les
décisions lui retirent ; elles partent de leur niveau de fin 2025. Les montants
en euros sont ces parts multipliées par le PIB de 2025, 2 991 Md€ : des euros
de 2025, à peu près.

| Caisse | Réserves fin 2025 | Ce que les décisions lui retirent en 2026 | Intégration |
|---|---:|---|---:|
| Complémentaire des exploitants agricoles (RCO) | 0,4 Md€ (4 mois) | ses droits sur les alcools, 0,56 Md€ (décisions 12 et 67) | **2026** |
| Agirc-Arrco | 113,6 Md€ (14 mois) | la CEG et la CET, 19,2 Md€ (décision 36) | **2032** |
| Complémentaire des avocats (CNBF) | 2,2 Md€ (85 mois) | rien | **2042** |
| Ircantec | 19,2 Md€ (50 mois) | rien | **2055** |
| Complémentaire des indépendants (RCI) | 23,4 Md€ (107 mois) | rien | après 2070 |
| Sections complémentaires des libéraux (dix, consolidées) | 39,0 Md€ (71 mois) | rien | après 2070 |
| Personnel navigant (CRPNPAC) | 5,1 Md€ (70 mois) | rien | après 2070 |

Sources : réserves, COR, rapport annuel de juin 2026, tableau 2.3, p. 100
(publié ; [dépôt, reserves_regimes.csv](../../../data/reference/regimes/reserves_regimes.csv)) ;
le reste, à côté (le module et ses tests).

**L'Agirc-Arrco, année par année** (à côté) : 113,6 Md€ fin 2025, 95,9 fin
2026, 77,4 fin 2027, 59,2 fin 2028, 40,6 fin 2029, 21,7 fin 2030, **2,5 fin
2031** — moins de deux semaines de pensions —, − 16,8 fin 2032. Elle dure six ans, comme la
note d'étude l'estimait (« cinq à six ans et demi »). L'année 2032 tient à
quelques milliards : une hypothèse un peu plus sombre la ferait tomber fin 2031.
**Avec ses seules réserves techniques**, 92,1 Md€, le fonds de roulement mis à
part pour payer les pensions du mois, elle rejoint le régime général **en
2030**. L'année de son intégration, ses pensions coûtent 101 Md€ et ses
recettes, sans CEG ni CET, 82 : le régime général reprend un déficit de 19 Md€,
avant que ses cotisants ne passent à 18 %.

**La CNBF et l'Ircantec** ne perdent rien : elles suivent les déficits que le
COR leur projette déjà, à peine décalés par leurs réserves de fin 2025, un peu
plus hautes que les siennes. Le COR épuisait celles de la CNBF entière en 2047
et celles de l'Ircantec en 2053 ; la complémentaire des avocats seule, sans les
droits de plaidoirie qui financent sa base, s'épuise en 2042, et l'Ircantec,
qui part de 19,2 Md€ au lieu des 18,2 que le COR lui prêtait, en 2055.

**Les trois dernières tiennent jusqu'en 2070** : les libéraux et les navigants,
excédentaires après 2040 chez le COR, finissent avec 62 et 14 Md€ ; les
indépendants, en déficit à partir de 2040, ont encore 8,7 Md€ en 2070, et un
déficit de 0,9 Md€ par an qui les épuiserait vers 2080.

## Ce que cela change pour les assurés

- **Les exploitants agricoles** : leur complémentaire rejoint le régime
  général la première année, avec tous les autres régimes de base. Rien ne les
  distingue de ce que le modèle fait aujourd'hui : 18 %, leurs droits au compte
  notionnel, la garantie vieillesse.
- **Les salariés du privé** : ils versent 25,83 % sous le plafond jusqu'en
  2031 — le régime général et l'Agirc-Arrco, sans la CEG —, puis 18 % à partir
  de 2032. Leurs pensions Agirc-Arrco suivent les règles de la caisse jusqu'en
  2031 (décision 43), puis passent au compte notionnel avec la garantie, et à
  la baisse des décisions 2 et 3. La promesse « votre cotisation ne dépassera
  jamais 18 % » (décision 45) attend six ans pour eux.
- **Les avocats** gardent leur complémentaire jusqu'en 2042, **les
  contractuels du public** l'Ircantec jusqu'en 2055.
- **Les indépendants, les libéraux et les navigants** la gardent au-delà de
  2070 : un artisan verse 25,97 % sous le plafond, un médecin 20,53 %, un
  navigant 51,62 % (taux de 2026, note d'étude), tout l'horizon du modèle. La
  décision 12 voulait qu'elles rejoignent « ensuite » le régime général ; la
  règle de la décision 37, seule, ne les y fait jamais entrer.

## La méthode

**Les données** (dépôt) :
- [comptes_complementaires.csv](../../../data/reference/regimes/comptes_complementaires.csv) :
  dépenses, ressources, solde élargi et réserves de chaque complémentaire, en
  part de PIB, de 2010 à 2070, au scénario de référence du COR de juin 2024,
  tirés de son classeur et recontrôlés contre lui par
  `scripts/verifier_donnees.py` (la série `comptes_complementaires`, au niveau
  `haute`). Les ressources moins les dépenses font le solde élargi, au
  l'arrondi près ; les réserves de la CNBF s'y épuisent en 2047, comme la
  fiche du COR l'écrit.
- [reserves_regimes.csv](../../../data/reference/regimes/reserves_regimes.csv) :
  le tableau 2.3 du COR de juin 2026, caisse par caisse ; ses groupes somment à
  ses sous-totaux, 5,3, 15,7 et 202,9 Md€, et son total aux 223,9 Md€ que
  `reserves_retraite.csv` portait déjà. Le tableau est à la p. 100 du rapport,
  non à la p. 98 que la note d'étude citait (p. 98, son texte).
- [assiettes_agirc_arrco.csv](../../../data/reference/regimes/assiettes_agirc_arrco.csv) :
  les assiettes de l'Agirc-Arrco par tranche de 2018 à 2024 (Chiffr'Agirc-Arrco
  2026, p. 46), qui somment à leur total publié, le salaire moyen en
  équivalent temps plein (p. 24) et la part des cotisants sous le plafond
  (p. 32).

**La règle des réserves, celle du COR** (à côté). Dans son classeur, les
réserves d'une année sont celles de la précédente, multipliées par un facteur
— un à partir de 2028, le même pour toutes les caisses de 2024 à 2027 (1,0189,
1,0137, 1,0098, 1,0071), propre à l'Ircantec —, plus le solde élargi, produits
financiers compris. Le module garde la règle et suit l'écart à la trajectoire
du COR : il croît de ce facteur et du rendement que le COR prête aux réserves
(ses produits de gestion et financiers divisés par les réserves de l'année
précédente, 3 % pour l'Agirc-Arrco, borné à 5 %, parce que la complémentaire
agricole y porterait 25 %, qui sont des produits de gestion), et perd chaque
année ce que les décisions coupent. Quand le COR épuise des réserves, il les
ramène à zéro et inscrit un « besoin de financement » : le module les prolonge
sous zéro par le solde. Les parts de financement du COR ne sont publiées qu'en
2023, 2030, 2040, 2050 et 2070 ; entre deux, il les interpole en ligne droite.

**Ce que la décision 36 retire à l'Agirc-Arrco** (à côté, testé à la main) :
sur les assiettes de 2024, la CEG rapporte 16 916 M€ (2,15 % de la tranche 1,
2,70 % de la tranche 2) et la CET 1 114 M€ (0,35 % des tranches 1 et 2 des
23,7 % de cotisants au-dessus du plafond, leur tranche 1 étant d'un plafond
chacun), en tout 18 030 M€, 19,18 % des 93 986 M€ qu'elle prélève sur les
salaires. Cette part s'applique à tout ce qu'elle reçoit au titre des salaires
chez le COR — cotisations, compensation des allègements, transferts de
l'Unédic, du FSV et des IEG, qui paient aussi la CEG — : 19,2 Md€ en 2026. La
compensation des allègements est gardée (décision 47), moins la part qui
couvrait la CEG, que ce calcul retire avec elle.

**Ce que la décision 12 retire aux autres** : leurs impôts et taxes affectés.
La complémentaire agricole perd ses droits sur les alcools, 48 % de ses
ressources en 2023, 53 % en 2030 chez le COR. La part que la loi lui donne est
passée à 28,89 % de l'accise (L. 732-58 du code rural, note d'étude) : elle en
perd sans doute un peu plus que le COR ne le dit, ce qui ne change pas l'année.
Le RCI perdait 0,6 % de ses ressources en 2023, rien ensuite.

**La CNBF** : le COR la projette d'un seul tenant, base et complémentaire. La
complémentaire en prend sa part des prestations, 55 % (ses 2,2 Md€ de réserves
font 85 mois, les 1,2 Md€ de la base 56 mois), et laisse les droits de
plaidoirie à la base, qu'ils financent : « les droits alloués aux avocats pour
la plaidoirie […] sont affectés au financement du régime d'assurance vieillesse
de base de la Caisse nationale des barreaux français » (L. 723-3 du code de la
sécurité sociale, dernière version de l'index LEGI). C'est une approximation :
la complémentaire a sans doute ses propres soldes, que le COR ne publie pas. Ses
réserves ont baissé de 7,4 % en 2025, celles de la base de 2,7 % (tableau 2.3) :
elle se porte moins bien que l'ensemble, ce que le retrait des droits de
plaidoirie rend.

## Les lectures faites, et ce qu'elles valent

- **Les droits sur les alcools** : la décision 48 dit « une complémentaire ne
  perd que la CEG et la CET » ; la décision 12 exclut tout impôt affecté, et la
  47 n'y fait exception que pour la compensation de l'Agirc-Arrco. Posée au
  propriétaire : « Elle les perd » (décision 67). L'autre lecture la laissait
  excédentaire jusqu'en 2070 ; le paramètre `impots_affectes_gardes` la refait.
- **Les pensions de l'Agirc-Arrco** jusqu'à son intégration suivent ses
  règles (décision 43) telles que le COR les projette : la convention de juin
  2024, qui la rend excédentaire dès la fin des années 2020. Une autre revalorisation
  avancerait ou reculerait 2032 ; aucune décision ne la fixe (au propriétaire).
- **Les pensions des complémentaires que l'État règle** — Ircantec, RCO,
  libéraux, RCI, CNBF, CRPNPAC — restent à leurs règles jusqu'à l'intégration :
  le module ne leur applique pas la baisse des décisions 2 et 3 avant. La leur
  appliquer dès la bascule baisserait leurs dépenses, et reculerait
  l'intégration de la CNBF et de l'Ircantec ; l'ordre des deux premières ne
  bougerait pas (au propriétaire).
- **Le RAFP** n'est pas projeté : provisionné à 146 % de ses engagements en
  valeur de marché fin 2025 (53,6 Md€ pour 36,9 Md€ d'engagements en valeur
  comptable ; COR, juin 2026, § 3.4), il ne s'épuise pas. Son sort, et celui
  des fonctionnaires qui y cotisent 10 % de leurs primes, est une question au
  propriétaire.
- **Les régimes de base qui ont des réserves** — la CNAVPL, 4,1 Md€, la base de
  la CNBF, 1,2, la CRPCEN, 2,3, la Banque de France, 13,4 — rejoignent le
  régime unique à la bascule, comme le modèle le fait déjà ; les décisions 36 à
  48 ne parlent que des complémentaires.
- **Les autres scénarios** ne bougent pas : ces règles valent pour le
  scénario 6 seul, par analogie avec la décision 28. Le module ne touche encore
  à aucun scénario.

## Ce que la note n'a pas établi

- Les masses viennent du COR de juin 2024, le seul millésime qui projette les
  caisses une à une ; le reste du dépôt tourne sur le COR de 2026. Les réserves
  de départ, elles, sont de fin 2025.
- Le produit de la CEG et de la CET n'est publié nulle part : il est calculé
  sur les assiettes et les taux. La CET suppose que chaque cotisant au-dessus du
  plafond y est toute l'année.
- La CNBF complémentaire est une part de la CNBF entière, non sa propre
  projection.
- Le rendement des réserves est celui que le COR leur prête, borné à 5 % : la
  valeur de marché des réserves de 2025, que le tableau 2.3 donne, peut s'écarter
  de leur valeur comptable.

## Le plan

1. **La projection caisse par caisse** — *faite le 7 novembre 2026*, cette
   note.
2. **Le moteur d'une carrière** (`moteur/js/` d'abord, puis son jumeau
   Python, au bit près des témoins) : au scénario 6, le taux de chaque année
   selon que la complémentaire de l'assuré est intégrée ou non — avant, ses
   cotisations d'aujourd'hui, la CEG et la CET ôtées ; après, les 18 % du
   régime unique —, et ses droits complémentaires gardés à leurs règles jusqu'à
   l'intégration, puis portés au compte notionnel avec la garantie vieillesse ;
   les planchers propres à la caisse gardés pour ses pensions servies tant
   qu'elle n'a pas rejoint le régime général, la garantie ensuite (décision 62,
   prise le même jour par la session des planchers).
   Les années d'intégration y entrent comme une donnée que la fabrique tire de
   cette projection (une table au paquet, par caisse), non comme un calcul du
   moteur. Le test d'abord : un salarié du privé à 25,83 % en 2031 et à 18 %
   en 2032. Une session neuve, quand celle du chantier 5 aura quitté le moteur
   (`list_sessions`).
3. **Le coût agrégé et le site** : au scénario 6, la masse des cotisations et
   des pensions de chaque caisse jusqu'à son intégration hors du solde du
   régime unique, puis dedans ; le déficit que le régime général reprend
   l'année de l'intégration (19 Md€ pour l'Agirc-Arrco) ; la page Coût, qui
   dit l'ordre et les années ; la promesse des 18 % avec sa condition.

## Ce qui reste au propriétaire

1. **Les indépendants, les libéraux et les navigants** ne rejoignent jamais le
   régime général avant 2070 : garder la règle de la décision 37 telle quelle,
   ou fixer une date butoir par la loi, à laquelle leurs réserves les
   suivraient ?
2. **La revalorisation des pensions de l'Agirc-Arrco** jusqu'en 2032 : la
   convention du COR (ses règles d'aujourd'hui), ou une autre ?
3. **La baisse des décisions 2 et 3** pour une complémentaire que l'État règle
   mais qui n'est pas intégrée : dès la bascule, ou à son intégration ?
4. **Les fonctionnaires et leur RAFP**, provisionné, qui ne s'épuise pas :
   intégré à la bascule avec la fonction publique, gardé à part, ou fermé ?
