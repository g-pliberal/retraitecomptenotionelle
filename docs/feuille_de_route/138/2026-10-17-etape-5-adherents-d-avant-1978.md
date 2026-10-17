# Étape 5, huitième partie : l'abattement des adhérents d'avant 1978, lu aux lois de 1974 et de 1977, et celui des professions libérales de 1978 à 1983

**La demande.** Le point 3 de « Ce qui reste » de
`2026-10-16-etape-5-benefice-des-independants.md` : l'abattement des
adhérents d'avant 1978, dans sa rédaction d'origine, la loi de finances
rectificative pour 1974, que l'index n'a pas. Ni les décisions du
propriétaire (l'effet retour dans le solde, les trois sur le bénéfice), ni
l'impôt au site.

**Où les textes se lisent.** L'index du JORF n'a de la loi n° 74-1114 que sa
notice, ni Légifrance ni Gallica ne servent la session (403), mais le Sénat
sert en PDF les textes définitifs qu'il a adoptés : celui de la loi de
finances rectificative pour 1974 (`senat.fr/leg/1974-1975/ta1974_1975_0078.pdf`,
20 décembre 1974) et celui de la loi de finances pour 1978
(`senat.fr/leg/1977-1978/ta1977_1978_0053.pdf`, 16 décembre 1977), et le
rapport général de sa commission des finances sur ce dernier projet (n° 88,
tome II, `senat.fr/rap/1977-1978/i1977_1978_0088_02.pdf`). L'index LEGI a le
reste : les décrets n° 75-911 et n° 77-1519, les rédactions de l'article 158.

**Ce que disent les textes.**

- *De 1976, 10 %.* La loi n° 74-1114 (art. 1er, III) : les adhérents d'un
  centre de gestion agréé « placés sous un régime réel d'imposition et dont le
  chiffre d'affaires ou de recettes n'excède pas le double des limites prévues
  pour l'application du régime forfaitaire, bénéficient d'un abattement de
  10 % sur leur bénéfice imposable », sans seuil ni limite. Les centres ne
  s'agréent qu'après le décret n° 75-911 du 6 octobre 1975, qui réserve
  l'abattement à qui a été adhérent « pendant toute la durée des exercices
  concernés », ou dont l'exercice était ouvert depuis moins de trois mois à
  l'agrément ou à l'adhésion (art. 17, LEGIARTI000006323772) : l'exercice de
  l'année 1975 n'y entre pas, celui de 1976 le premier. Le rapport du Sénat
  compte, en novembre 1977, 144 centres et quelque 10 000 adhérents qui
  bénéficieraient de l'abattement.
- *En 1977, 20 %.* La loi n° 77-1467 (art. 7, II) porte le taux « de 10 % à
  20 %, sauf pour la fraction du bénéfice qui excède la limite de 150 000 F
  prévue à l'article 6 », et « aucun abattement n'est appliqué sur la
  fraction du bénéfice qui excède une fois et demie la limite de la dernière
  tranche du barème » ; son article 1er, III, applique aux revenus de 1977
  ce qui ne porte pas de date, et le rapport chiffre la mesure « en
  reversements de l'année 1978 ». La dernière tranche du barème de son article
  2, écrit pour deux parts, commence à 238 200 F : la limite est de 357 300 F,
  quand celle des salaires, que l'article 158, 5, a arrondit à la dizaine de
  milliers de francs supérieure, est de 360 000 F. La loi de finances pour
  1979 fixe les deux à 360 000 F pour les revenus de 1978 et de 1979 (art. 11,
  LEGIARTI000006273141). L'article 7, I, triple les limites de chiffre
  d'affaires.
- *Les professions libérales, de 1978.* La loi de finances pour 1977
  (art. 64) étend l'abattement aux adhérents des associations agréées des
  professions libérales, que le décret n° 77-1519 du 31 décembre 1977 fait
  agréer, en voulant l'adhésion de toute l'année, ou depuis moins de trois mois
  après son début (art. 16, LEGIARTI000006323746) : la première année est 1978.
  Le 4 ter de l'article 158 leur donne alors 20 %, aux mêmes seuils et limites
  que le 4 bis, de sa rédaction du 1er juillet 1979 (LEGIARTI000006307959,
  « pour l'imposition des revenus de 1978 et de 1979 ») à celle du 22 mars
  1984 (LEGIARTI000006307963, revenus de 1983) ; la rédaction du 15 juillet
  1985 le fond dans le 4 bis (« 4 ter. (Sans objet) »). La partie précédente
  ne les faisait entrer qu'aux revenus de 1984, faute d'avoir lu le 4 ter :
  c'est corrigé.

**Ce qui est fait.**

- `impot_revenu.py` : l'abattement des adhérents commence aux revenus de 1976
  (`PREMIERE_ANNEE_ABATTEMENT_ADHERENTS`), à 10 % du bénéfice
  (`TAUX_ABATTEMENT_DE_1974`) ; en 1977, 20 % jusqu'à 150 000 F et 10 %
  jusqu'à 357 300 F (`SEUIL_ET_LIMITE_DE_1977`) ; le bénéfice non commercial
  dès 1978 (`PREMIERE_ANNEE_ABATTEMENT_BNC`). La remarque sur l'adhérent
  d'avant 1978 disparaît, et le `HORS_CHAMP` dit les limites de chiffre
  d'affaires ou de recettes de 1976 à 1982.
- Le portage : `impot-revenu.js`, de même ; la grille du portage gagne les
  années 1976 et 1977, et vérifie que l'abattement y joue pour l'artisan, et
  de 1978 à 1983 pour le libéral.
- Les tests : `test_l_adherent_d_avant_1978` (1975, 1976, 1977, les bénéfices
  agricoles, la limite de 1977, les bénéfices non commerciaux de 1976 à 1983),
  vu rouge avant le code ; celui des années suivantes perd ses deux assertions
  d'avant 1984.

**Ce que montrent les mesures.** Un artisan célibataire au salaire moyen, son
bénéfice imposable pris à 80 % : 3 118 F d'abattement en 1976, son impôt
passant de 5 822 à 4 715 F, et 6 951 F en 1977 (de 6 749 à 4 288 F). Un
libéral à une fois et demie le salaire moyen : 11 678 F en 1978 (de 15 556 à
10 888 F), 20 823 F en 1983 (de 29 999 à 21 113 F). Au cycle de vie, sous le
barème projeté sur les prix : l'artisan né en 1952, entré à 22 ans, parti à
62, paie 362 € au lieu de 580 € en 1977, son taux d'annuité passe de 51,62 à
51,50 % ; la libérale née en 1952, entrée à 26 ans, à une fois et demie le
revenu moyen, 1 401 € au lieu de 2 201 € en 1983, et son taux d'annuité de
25,65 à 25,41 % ; leurs rendements ne bougent pas au millième. Seules
bougent les carrières qui ont un bénéfice de 1976 à 1983 : les cas types nés
en 1970 de la partie précédente, non.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'effet retour dans le solde* : au propriétaire.
2. *Les trois décisions sur le bénéfice* : au propriétaire. La troisième,
   la limite d'après 1979 prise à celle des salaires, s'éclaire de ce que la
   loi de 1977 en distingue les deux, de 357 300 et 360 000 F, sans arrondi
   pour les adhérents.
3. *L'impôt au site*, et l'affichage de l'effet retour : à la session des
   pages.
4. *Les revenus non salariés de la prime pour l'emploi*, de 2000 à 2015.
5. *L'année de revenus de l'imposition de la majoration pour enfants*, au
   texte de la loi de finances pour 2014.
6. *Les règles d'avant 1981 sans texte lu* : les textes définitifs du Sénat
   en donnent sans doute les lois de finances, comme ici.
