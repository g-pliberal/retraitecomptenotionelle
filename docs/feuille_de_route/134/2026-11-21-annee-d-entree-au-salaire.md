# Les trimestres de l'année d'entrée, dits par le salaire

Le point 5 de l'action 134, que la question du propriétaire du 21 novembre
2026, « on compte bien les durées en jours ? », a fait relire. La règle 1 du
projet (20 novembre) le fait corriger sans attendre d'accord.

**Ce que faisait le moteur.** Toute ligne d'emploi validait ce que son revenu
vaut, au seuil de 200 heures de SMIC, de 150 depuis 2014, puis le bornait aux
trimestres civils de ses mois (`trimestresCivils(mois)`), et
`Carriere.trimestresEcoules` et `plafondTrimestres` le bornaient de nouveau.
Entré au SMIC à temps plein le 1er octobre 2015 : 4 372,60 € sous un seuil de
1 441,50 €, trois trimestres au texte, un au moteur.

**La règle, lue.** R. 351-9 CSS, ses trois rédactions (1985, 2014, 2026) :
« autant de trimestres que le salaire annuel [...] représente de fois » le
seuil, « avec un maximum de quatre trimestres par année civile », sans
condition de mois. De même aux salariés agricoles (R. 742-21 du code rural),
aux artisans et commerçants depuis 1973 (décret n° 73-937, article 2, puis
D. 634-1, qui leur applique R. 351-9). Les libéraux valident aussi au revenu
depuis 2004 (D. 643-3), mais à compter du trimestre civil qui suit le début
de l'activité (R. 643-1). Seule l'année
de la date d'effet s'arrête au dernier jour du trimestre civil qui la précède
(R. 351-1). Aucune note, limite ni décision ne posait le plafond par mois
volontairement : le journal de veille du 28 septembre 2026 et le point 5 de
l'action 134 le disaient déjà contraire au texte.

**Ce qui change.** `plafondDeLAnneeDEmploi` (`moteur/js/carriere.js`) borne
une année d'emploi à quatre trimestres dans les régimes où le revenu les dit,
que nomme la version de l'année de la fiche neuve `trimestres_au_revenu` (le
régime général et les salariés agricoles depuis 1946, les artisans et les
commerçants depuis 1973), aux trimestres civils
écoulés l'année du départ ; ailleurs — fonction publique, régimes spéciaux,
avant 1946, et les libéraux, dont l'affiliation ne court qu'au trimestre
civil suivant le début de l'activité (R. 643-1) —, toujours aux trimestres
civils de ses mois. Les deux bornes de
`Carriere` ne rognent plus une année antérieure au départ. Test :
`tests/js/mois.test.js`, « l'année d'entrée valide ce que son salaire vaut ».
Une soixantaine de tests construisaient leurs carrières sur l'ancienne borne
(entrée en cours d'année) : chacun a été déplacé, pour garder son chiffre et
sa règle, ou a reçu un attendu refait à la main, et la recherche de
`tests/test_oracle.py` essaie, quand aucun mois d'entrée ne rend le total
publié, une première année à temps partiel.

**Laissé.** Les périodes assimilées (R. 351-12 : 50 jours de chômage, 60 de
maladie font un trimestre), comptées aux trimestres civils de leurs mois ; la
seconde pension, aux mois ; l'année du décès d'un assuré qui n'a pas liquidé,
qu'aucun texte trouvé ne borne autrement ; l'interruption saisie d'un
parcours, aux mois ; un statut dont le régime de 2023 dépend de la date
d'entrée (Banque de France, RATP, IEG), aux mois cette année-là.
