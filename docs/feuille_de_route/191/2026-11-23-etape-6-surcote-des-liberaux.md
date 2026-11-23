# Le passage au jour : la surcote de la base des libéraux, trimestre par trimestre

**La demande.** Suite de l'étape 6 de la séparation des axes (note de décision
0009) : la base des libéraux servait 1,25 % à tous les trimestres de surcote
des pensions de 2024 et après, quand R. 643-8 garde 0,75 % à ceux d'avant le
1er septembre 2023. Sur Opus 5.5, relue sur Fable 5.2 dans un contexte neuf.

**Ce que disent les textes**, lus dans l'index LEGI à jour au 23 novembre
2026. R. 643-8, rédaction du 1er janvier 2004 (LEGIARTI000006751834) : la
majoration vaut « au titre des périodes d'activité ayant donné lieu à
cotisations […] accomplies à compter du 1er janvier 2004 après l'âge prévu au
premier alinéa de l'article L. 351-1 et au-delà de la limite mentionnée au
deuxième alinéa du même article », à 0,75 % par trimestre. Rédaction du
décret n° 2023-799 (LEGIARTI000047985850), pour les pensions prenant effet
depuis le 1er septembre 2023 (article 7, II) : « 0,75 % par trimestre
accompli avant le 1er septembre 2023 et […] 1,25 % par trimestre accompli à
compter de la même date ». Le texte ne dit rien du trimestre civil de juillet
à septembre 2023, que la date coupe. L'exemple chiffré de la CARMF
(diapositives de septembre 2023 : « Soit pour 2023 : 3 x 0,75 % + 1 x 1,25 %
= 3,50 % ») et le guide 2024 de la CNAVPL (page 31) le comptent à 0,75 %. La
recherche est dans le dossier du projet,
`architecture/separation-des-axes/etape-6/surcote-des-liberaux-2023/`.

**Ce que le dépôt faisait.** La branche en points du moteur (`surcotePoints`,
mode `regime_general`) multipliait le nombre de trimestres par le taux plat
de la ligne de l'année du départ : 0,75 % jusqu'en 2023, 1,25 % depuis 2024,
à tous les trimestres. Elle comptait en outre les trimestres cotisés de
l'année entière de l'âge légal, y compris ceux d'avant l'anniversaire et
d'avant la durée requise.

**Corrigé.** Une fiche `cnavpl_surcote`, en deux versions (2004 et 2023), et
trois lignes `cnavpl` dans `legislation/surcote_baremes.csv` : 0,75 % jusqu'au
trimestre de juillet 2023 compris, ce trimestre en fiabilité moyenne au barème, que la branche en points ne remonte pas encore au résultat, 1,25 %
depuis celui d'octobre 2023. Les quatre lignes de liquidation de 2004 et
après renvoient `surcote_bareme` à la fiche. Le moteur, quand la période a un
barème, date les trimestres par `coefficientSurcoteDatee`, la règle de la
branche en annuités : trimestres civils depuis celui qui suit l'âge légal ou
le mois qui suit la durée requise, que R. 643-8 dit dans les mêmes mots que
L. 351-1-2.

**Exemples**, posés à la main (`tests/test_sections_liberales.py`). Un
libéral né en décembre 1960, entré à vingt ans : parti le 1er janvier 2024,
quatre trimestres de 2023, 3,5 % au lieu de 6,25 % ; le 1er janvier 2025, huit
trimestres, 8,5 % au lieu de 11,25 % ; le 1er octobre 2023, 2,25 % au lieu de
3 % ; le 1er janvier 2023, rien au lieu de 0,75 %. Sur une base de 13 000 €
avant surcote, partie en 2025, 357,50 € de moins par an.

**Les cas témoins.** Deux sur 935 bougent, les agents généraux d'assurance
nés en 1960 et partis à 69 ans : −0,81 % et −0,88 % de la pension totale
(base × 1,2925 au lieu de 1,3125, et × 1,1925 au lieu de 1,2125). Deux tests
suivent : la médecin née en 1951 partie à 76 ans et demi (base × 1,2475 au
lieu de 1,2875, 17 713,16 €) ; la libérale née le 1er janvier 1969 partie à
66 ans, qui a sept trimestres de surcote et non huit.

**Les compteurs.** Les valeurs de repli restent à 370, les renvois sans texte
à 286 : la série nouvelle cite R. 643-8. Les rédactions sans statut baissent
de 9 151 à 9 150.

**Relu sur Fable 5.2, dans un contexte neuf.** La relecture confirme le texte,
les bornes du barème, le compte des trimestres et les valeurs des tests, et
que seule la base des libéraux est touchée. Elle corrige un chiffre de cette
note (6,25 %, non 5 %), une citation du guide, et rattache la réforme de 2023
à la fiche nouvelle (`absorbee_par: [surcote_bareme]`) : les réformes à
classer passent de 87 à 86.

**Laissé.** Le trimestre de juillet à septembre 2023 reste à confirmer par une
instruction de la CNAVPL ou une notification de pension de 2024. Né le
premier d'un mois de début de trimestre, l'assuré voit sa surcote courir du
trimestre suivant son anniversaire, comme au régime général dans le moteur ;
si l'âge est atteint la veille, comme pour la date d'effet, il en aurait un
de plus, ici comme au régime général. La MSA des non-salariés (D. 732-42)
garde le taux plat et le compte à l'année de l'âge légal, la même erreur de
classe, à lire avec son texte.
