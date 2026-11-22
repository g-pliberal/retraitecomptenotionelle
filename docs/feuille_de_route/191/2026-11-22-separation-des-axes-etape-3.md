# Le moteur lit les paramètres d'un régime par axe : la liquidation à sa date, la cotisation à son année

**Reprise, au 22 novembre 2026.** Le moteur JavaScript lit les
paramètres d'un régime par axe : la liquidation, la structure et le servi en
vigueur à une date (`Regime.aLaDate`), la cotisation d'une année, tranche par
tranche (`Regime.deLAnnee`). Le paquet porte encore des périodes, dont
`moteur/js/axes.js` refait les blocs au chargement. Aucun résultat n'a bougé.
Reste au moteur, en une session : la caisse des membres du CESE, qui pèse
chaque annuité par la durée requise de la période qui l'a acquise et lit donc
encore les périodes (`annuitesAuTauxDeLeurAnnee`) ; ce poids devient un champ
de cotisation propre à la caisse. Viennent ensuite le Python, le paquet, le
pont et les tests, puis le retrait des périodes. Les données restent gelées.
Par quoi commencer : la caisse du CESE. L'oracle est sous
`architecture/separation-des-axes/oracle/`, dans les fichiers du projet.

**La demande.** Le propriétaire a choisi, le 22 novembre 2026, de séparer
complètement les deux axes des fichiers de régime. L'étape 2 a fait des
quatre blocs la source, et des périodes une vue que le chargeur refait.
Cette session mène la première des deux sessions de l'étape 3 : le moteur lit
les blocs au lieu de la vue, sans qu'aucun résultat bouge. Sur Opus 5.5 ;
Fable 5.2 étant indisponible jusqu'au 25 novembre, la relecture s'est faite
sur Opus, dans un contexte neuf.

**Ce qui est fait.** `moteur/js/axes.js` range chaque champ dans sa famille,
comme `donnees/axes.py`, et refait des périodes du paquet les quatre blocs :
une ligne de cotisation par période, dans leur ordre ; des lignes au jour pour
la liquidation, la structure et le servi, chaque intervalle prenant la
première période qui le liquide. C'est un pont du gel : il part quand le
paquet portera les blocs. `Regime.aLaDate(jour)` assemble la ligne de
liquidation, la structure et la ligne servie de ce jour, et la première
tranche de la cotisation de son année, que la liquidation lit pour le salaire
de référence et le barème des points ; `Regime.deLAnnee(annee)` assemble,
pour chaque tranche de l'année, sa cotisation et la liquidation de son
1er janvier. Une même combinaison de lignes rend le même objet.

Les choix de période sont passés par eux. `periodeDeLiquidation` lit la
date d'effet (après la dernière année d'un régime, le 1er décembre de
celle-ci), et `derniereAnnee` la dernière ligne de cotisation. Les douze
lectures à l'année prennent chacune une date : le 1er janvier pour la durée
des fonctionnaires d'une année, celle du droit ouvert avant la table de 2003,
l'âge du taux plein gardé à l'ouverture (« la période en vigueur l'année
où »), la pension d'invalidité (« formé au 1er janvier de cette année »), le
type de calcul d'une chaîne d'absorption et le barème des points revalorisé ;
mars 1983, le dernier mois d'avant l'ordonnance, pour le taux acquis au
31 mars 1983 ; la date d'effet pour l'ouverture des complémentaires sans
leur base (`departs.js`). La cotisation d'une année, ses tranches, vient de
`deLAnnee` (acquisition, compte notionnel, rémunération, fusion, assiette des
cultes, contributions d'équilibre). Les points gratuits et la famille d'un
régime à l'étranger se lisent sur la liquidation et la structure.
`ouvertureDe` compare les règles d'un mois à l'autre par leurs lignes de
liquidation, de structure et de servi, et non plus par l'identité d'une
période, que la cotisation changeait aussi. La garde de `dureeRequise` qui
comparait le début de deux périodes est partie : la période du droit ouvert
avant 2004 et celle d'une liquidation au barème de la fonction publique,
qui commence en 2004, ne coïncident jamais. Le pont rend au Python le rang de
la période qui liquide le jour que le moteur lit (`jourDeLiquidation`).

**Vérifié.** Les 934 témoins, refaits après chaque lot et après la
relecture, sont identiques. L'oracle, refait, est identique à celui du gel.
`tests/js/axes.test.js` confronte, à chaque 1er du mois de 1900 à 2070 et
pour les deux catalogues (taux minimal et taux moyen de l'Agirc-Arrco),
`aLaDate` à la période qui liquide, et `deLAnnee` aux périodes de l'année,
toutes familles, nuls compris. Seules diffèrent la liquidation au 1er janvier
de treize couples d'un régime et d'une année, ceux que l'amendement
annonçait : le test les nomme, et aucune lecture du moteur ne les atteint
aujourd'hui (la fusion de 1946 à 2070 est identique).

**Relu sur Opus, dans un contexte neuf.** La relecture a trouvé une lecture
de l'âge du taux plein gardé à l'ouverture passée au mois d'ouverture, quand
son texte dit l'année : aux IEG, une ouverture de juillet à décembre 2008
aurait pris la règle de juillet 2008. Elle se lit au 1er janvier. Elle a
trouvé aussi la comparaison d'`ouvertureDe` que la cotisation déclenchait, le
test qui ne regardait ni la cotisation lue à la liquidation, ni les autres
familles des tranches, ni les nuls : tout est repris.

**Ce qui reste.** La caisse des membres du CESE (`liquider.js`,
`annuitesAuTauxDeLeurAnnee`) lit encore les périodes ; l'amendement en fait un
champ de cotisation propre, ce qui touche son fichier et le chargeur.
La page Avantages compte les périodes qui déclarent la réversion
(`pages.js`) : le chiffre affiché bougerait si l'on comptait des lignes, à
trancher au retrait des périodes. `Regime.periode`, `periodesActives` et
`periodeALEffet` ne servent plus qu'au pont et aux tests, et leurs jumeaux
Python sont déclarés gardés : ils partent avec le Python. Le plafond des
trimestres des mines se lit sur la liquidation du 1er janvier de l'année, non
sur celle de la pension comme l'amendement le veut ; les valeurs sont les
mêmes. Les objets assemblés n'ont ni `debut` ni `fin` : deux messages
d'erreur ont perdu l'année.
