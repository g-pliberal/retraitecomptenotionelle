# 4. Régimes incomplets, et de combien

Un régime « incomplet » n’est pas un régime absent : les <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=modelise|partiel)-->74<!--/--> régimes du catalogue
calculent tous une pension. Ce qui manque est, chaque fois, un ÉTAGE ou un
BARÈME qu'aucune source publique ne donne en série. Le tableau dit lequel, ce
qui le remplace, et **dans quel sens** l'approximation joue — car un modèle dont
on ignore le sens de l'erreur ne se corrige pas dans la tête du lecteur.

| Régime | Ce qui manque | Ce qui le remplace | Sens et ordre de grandeur |
|---|---|---|---|
| Professions libérales (CNAVPL) | la SECTION B du complémentaire des notaires, dont les bornes de classes ne sont publiées nulle part ; le volet CAPITALISÉ de la CAVP ; le complémentaire de la CAVOM d'avant 2016, qui prélevait par classes et dont la grille n'est nulle part ; le montant de la cotisation FORFAITAIRE du régime de base d'avant 2004 — qui ne commande plus la pension, seulement le flux versé au compte notionnel | le régime de base, en points plafonnés à <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2025.points_maximum)-->557<!--/-->, PLUS le complémentaire de la section : les DIX sections en ont un maintenant — CARMF, CARCDSF, CNBF, CAVEC, CAVP (volet réparti), CARPIMKO, CARPV, CAVOM (depuis 2016), CAVAMAC, CPRN (section C), et la Cipav pour le statut générique | **sous-estime** la pension d'un notaire de près de quatre dixièmes de son complémentaire, et celle d'un officier ministériel de tout son complémentaire d'avant 2016. Pour la CAVAMAC et la CPRN, l'assiette elle-même est reconstituée par un FACTEUR moyen — commissions, produits de l'office — et ne décrit aucun assuré en particulier |
| Marins (ENIM) | les salaires forfaitaires d'avant 2008, que les textes de l'index ne chiffrent pas ; la CATÉGORIE du marin, que le décret définit par le métier et qu'une carrière saisie ne porte pas, et la catégorie MOYENNE des trente-six derniers mois qui fait le salaire de référence (R. 11) ; le décompte des services au semestre (R. 12) ; la pension d'invalidité, seule exception au plafond de vingt-cinq annuités qui ne soit pas servie | la grille des vingt forfaits lue au Journal officiel depuis 2008, la catégorie la plus proche du revenu — convention nommée —, et la grille de 2008 ramenée par le salaire moyen avant ; le plafond de vingt-cinq annuités avant cinquante-cinq ans est porté | **estimé** avant 2008, la grille de 2008 étant ramenée par le salaire moyen ; l'écart de catégorie et de décompte tient à une catégorie et à un trimestre au plus ; la levée du plafond à cinquante-deux ans et demi pour trente-sept annuités et demie est servie depuis le 22 septembre 2026 |
| Avocats (CNBF) | la progression de la cotisation forfaitaire sur les cinq premières années (au barème 2026, <!--chiffre:illustration()-->363<!--/--> € la première, <!--chiffre:valeur(data/reference/regimes/cnbf.yaml:periodes.debut=2004.cotisation_forfaitaire_euros)-->1 510<!--/--> € à partir de la sixième) ; la contribution équivalente aux droits de plaidoirie ; les tranches de la grille complémentaire d'avant 2019 | la cotisation proportionnelle de <!--chiffre:valeur(data/reference/regimes/cnbf.yaml:periodes.debut=2004.taux_cotisation_retraite*100)-->3,00<!--/--> % ET le forfait à sa valeur de croisière, <!--chiffre:valeur(data/reference/regimes/cnbf.yaml:periodes.debut=2004.cotisation_forfaitaire_euros)-->1 510<!--/--> € ; les années d'avant 2019 restent au rendement instantané | **surestime de <!--chiffre:illustration()-->4 586<!--/--> € sur une carrière**, au barème 2026, le flux des cinq premières années, contre près de <!--chiffre:illustration()-->70 000<!--/--> € qui manquaient quand le forfait n'était pas porté du tout. Sans effet sur la pension actuelle, qui est forfaitaire |
| Non-salariés agricoles | les points gratuits de la RCO des conjoints, aides familiaux et collaborateurs — <!--chiffre:illustration()-->66<!--/--> par an pour leurs années d'avant 2011, dans la limite de <!--chiffre:illustration()-->17<!--/--> ans —, le modèle ne connaissant que le statut de chef ; le barème de points du régime de base AVANT 1990, l'article qui l'écrit ne l'ouvrant qu'à cette date — ses années entrent aussi dans la moyenne de la réforme de 2026 —, et, dans cette réforme, le revenu des années cotisées au minimum, que la loi déduit des cotisations | le barème en points de 1990 à aujourd'hui, la retraite forfaitaire et la RCO, tous trois lus dans le code rural, avec les points gratuits des chefs d'exploitation pour leurs années d'avant 2003 ; le rendement instantané pour les années d'avant 1990, et l'équivalent en points de ce rendement dans la moyenne de 2026 ; le plancher de six cents SMIC horaires pour le revenu des années depuis 2016 | **sous-estime** la pension des carrières de conjoint et d'aide familial, qui sont précisément les plus modestes du régime |
| Régimes spéciaux résiduels | des paramètres certifiés — mais plus des textes : l'Opéra, la Comédie-Française, la SEITA, les clercs de notaires, la Banque de France, le fonds spécial des ouvriers de l'État et le personnel navigant ont leurs décrets lus VERSION PAR VERSION dans la base LEGI, et passent au niveau `moyenne`. Restent au niveau `estimee` les mines — dont dix-huit millésimes sont interpolés entre deux valeurs sourcées —, les marins, le port autonome de Strasbourg et les chemins de fer secondaires | pour les quatre derniers, les textes fondateurs sans recontrôle ; le port de Strasbourg n'a rien dans LEGI que des décrets de compensation, son règlement de retraite étant un acte de l'établissement | **indéterminé** pour ces quatre-là, et c'est le seul cas où le dépôt ne sait pas dire le sens. Ces régimes portent peu d'assurés ; leur poids dans les agrégats est faible |

**Ce qui a été refermé depuis la version précédente de ce tableau.** Le régime
de base des avocats était rangé ici comme « à scinder » : il l'est, et sa
pension ne dépend plus du revenu. La complémentaire agricole y figurait sans
valeur de point : elle en a une, certifiée de 2005 à 2024, tirée du code rural.
Le régime de base des professions libérales y figurait sans barème : il a le
sien, plafonné en points comme la caisse le publie. La grille des classes de
son étage d'avant 2004 y figurait aussi : **elle n'était pas la bonne
question** — la pension d'avant 2004 ne dépend d'aucune classe, et la section sur
le régime de base des libéraux d'avant 2004, plus bas, dit pourquoi.

**Pourquoi ce qui reste ne se referme pas de la même façon.** Les limites
refermées cette année l'ont toutes été par un changement de CLÉ D'ENTRÉE — un
numéro d'article plutôt qu'un mot, un IDBANK plutôt qu'une page, un lecteur de
format écrit à la main. Ce qui subsiste ci-dessus n'est pas d'une autre
difficulté technique : ce sont des barèmes que personne ne publie sous aucune
forme, ni en série, ni en texte réglementaire, ni en PDF. Les chercher encore
supposerait de les reconstituer à partir de cas individuels, ce qui produirait
un chiffre plus précis d'apparence et pas davantage de vérité.

Le catalogue compte **<!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire?couverture=modelise|partiel)-->74<!--/--> régimes**, actuels et disparus. Il est structurellement
extensible : ajouter un régime consiste à écrire une fiche YAML conforme à
`data/reference/regimes/_schema.yaml`, sans toucher au moteur.

## Les régimes qui manquent encore, et ce qui bloque chacun

**Cette liste est désormais dérivée d'un fichier.** Elle ne l'était pas, et
c'était une limite en soi : aucune source du dépôt n'énumérait les régimes
français — la série DREES agrège en treize systèmes, le panorama du COR est un
document saisi à la main, et les portails officiels ne servent pas de liste
exploitable —, si bien qu'un régime pouvait manquer à la liste des manquants.
[`data/reference/regimes/inventaire.yaml`](../data/reference/regimes/inventaire.yaml)
énumère maintenant TOUS les régimes obligatoires, vivants, disparus ou hors
champ — <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire)-->108<!--/--> lignes, ancrées sur `R. 711-1`, `D. 643-1`, `L. 921-1` et le
programme 195 des lois de finances, chacune avec son texte fondateur et, quand
l'index DILA du dépôt le porte, son identifiant —, et dit pour chacun s'il est
modélisé, partiel, à modéliser ou hors champ. `tests/test_donnees.py` impose
que l'inventaire et le catalogue coïncident sur les régimes calculés ; la page
« Données » du site l'affiche ; [`docs/regimes.md`](regimes.md) le commente,
famille par famille. Ce qui suit est l'histoire de la façon dont les fiches
sont entrées, et reste vrai ; la liste à jour de ce qui manque est là-bas.

**Ce que l'inventaire a fait apparaître**, que la liste de mémoire ne portait
pas : le régime d'allocation viagère des gérants de débits de tabac (décret
du 30 octobre 1963, géré par la Caisse des dépôts), le régime additionnel des
enseignants du privé sous contrat (décret n° 2005-1233), les deux
complémentaires d'Organic d'avant le NRIC — conjoints de commerçants
(`D. 635-35-1`) et entrepreneurs du bâtiment (loi n° 70-13) —, les régimes
RACD et RACL de l'IRCEC, les régimes professionnels intégrés à l'Agirc-Arrco
(banques, organismes de sécurité sociale, caisses d'épargne, CCI, CAMARCA),
l'affiliation des élus locaux à l'Ircantec dès 1973 (loi n° 72-1201) et non
1992, le régime micro-social, l'ASV des conventionnés, et cinq régimes
d'outre-mer. Et trois régimes fermés dont on ne savait plus s'ils avaient
existé, retrouvés dans l'index : le régime spécial du Crédit foncier de France
(transféré au régime général au 1er janvier 1989, décret n° 89-157), la caisse
des régies ferroviaires d'outre-mer (décret n° 58-1090, puis transfert à
l'État en 1993), et le régime de l'ORTF. Une relecture de septembre 2026
contre l'arrêté du 22 juillet 2003 relatif à l'échantillon interrégimes de
cotisants, qui énumère les organismes de tous les régimes obligatoires, a
ajouté quatre caisses fermées — la CREA des professions de l'enseignement
fondue dans la Cipav en 2004, la Caisse de retraites de la France d'outre-mer,
les caisses des fonctionnaires d'Algérie, du Maroc et de Tunisie, la CRFM des
agents publics de Mayotte —, les non-salariés de Mayotte à la caisse de
sécurité sociale de Mayotte et le personnel au sol d'Air France aux régimes
professionnels intégrés, puis une ligne pour les élus des assemblées de
Polynésie française et de Nouvelle-Calédonie, dont la loi organique de 1999
confie le régime de retraite aux assemblées elles-mêmes ; voir
[`docs/regimes.md`](regimes.md).

### Ce que JORF et LEGI ne contiennent pas

Le dépôt embarque, par l'index de `scripts/fetch/dila_index.py`, deux bases de
la DILA filtrées sur le champ social. Pour l'histoire des règles de chaque
régime — l'étape qui suit l'inventaire —, il faut savoir ce qu'elles ne
donnent pas, afin de ne pas le chercher deux fois :

1. **Tout ce qui précède 1947.** Le dump JORF commence en 1947. Les lois de
   1910, de 1928 et 1930, de 1941, les ordonnances de 1945, la loi de 1909 sur
   les retraites des cheminots, celle de 1894 sur les mines et celle de 1937
   sur les clercs de notaires ne s'y trouvent que par les textes postérieurs
   qui les citent. Elles sont sur Gallica, en images.
2. **De 1947 à 1989, le texte intégral manque souvent.** Le JORF ancien n'est
   dans le dump que par sa notice ou son titre — constaté sur 1950 et sur
   1985-1986 —, et certains tableaux ne sont que des images (1994-1995). C'est
   la période où les règles des régimes se sont fixées : 1945, 1971, 1982,
   1983. Le « JO numérisé » en fac-similé de Légifrance n'est pas en open
   data.
3. **LEGI ne remonte pas avant la codification de 1985** pour les états
   datés des articles ; les versions antérieures des décrets des régimes
   spéciaux — statut des IEG de 1946, règlement SNCF de 1954 — n'y sont pas.
4. **Les accords de l'Agirc et de l'Arrco** — 1947, 1961, 2017 — et leurs
   annexes ne sont ni dans le JORF, qui n'a les avis d'extension que depuis
   les années 2000, ni dans KALI. La fédération est la seule source.
5. **Les règlements des caisses** — sections de la CNAVPL, CNBF, IRCEC, CRPN,
   port autonome de Strasbourg, Banque de France, CCI — : le JORF porte
   l'arrêté d'approbation, rarement son annexe.
6. **Les circulaires** de la Cnav et le BOSS ne sont pas dans JORF ni LEGI ;
   celles de la revalorisation des salaires sont récupérées à part.
7. **Les régimes des assemblées et des collectivités du Pacifique** relèvent
   de textes qui ne paraissent pas au Journal officiel.

Ce qu'il ne manque pas : le filtre thématique de l'index est assez large —
« retrait », « pension », « cotis », « invalidit »… — pour retenir les textes de
tous les régimes de l'inventaire ; les recherches qui ont établi la liste y
ont trouvé le décret du Crédit foncier, celui de Mayotte, l'arrêté des débits
de tabac, la loi des maires et adjoints, sans reconstruire l'index.

**Le régime des cultes, lui, est entré**, et c'est le seul du lot que le code
spécifie entièrement — sans lui donner un seul chiffre propre :

* l'**assiette** : R. 382-89 et R. 382-90 égalent la base forfaitaire, pour
  l'assuré comme pour sa congrégation, à « la valeur horaire du salaire
  minimum de croissance en vigueur, multipliée par le nombre légal d'heures de
  travail mensuel » ;
* les **taux** : les mêmes articles les égalent à ceux du régime général,
  respectivement part salarié et part employeur ;
* la **pension** : L. 382-27 la sert « dans les conditions définies aux
  articles L. 351-1 à L. 351-1-3 […] L. 351-8 à L. 351-13 », c'est-à-dire aux
  règles du régime général.

La fiche ne porte donc aucune valeur qui lui soit propre, et un test relit les
deux fiches année par année pour interdire qu'elle dérive de celle du régime
général. Il a fallu un drapeau au moteur, `assiette_forfaitaire` : un ministre
du culte n'a pas de salaire dont on prélèverait une fraction, l'assiette EST le
forfait, là où `assiette_plancher` ne relevait que les assiettes trop basses.

**Ce que la fiche des cultes approxime.** Le passage du forfait de <!--chiffre:illustration()-->169<!--/--> à <!--chiffre:mesure(constante?de=retraite_notionnelle.saisie&nom=HEURES_SMIC_PAR_MOIS)-->151,67<!--/--> heures mensuelles est daté de 2002, ce
que la clause transitoire de R. 382-89 rend probable sans l'écrire ; et la
garantie mensuelle de rémunération qui, du 1<sup>er</sup> janvier 2002 au
30 juin 2005, s'ajoutait à cette base n'est pas modélisée — ces quatre années
sous-estiment donc la cotisation. La pension se calcule en deux fractions,
comme la caisse le fait (fiche `cultes_fractions_de_pension`) : celle des
périodes d'après 1997 aux règles du régime général, sur un salaire annuel moyen
fait du forfait ; celle des périodes antérieures au 1<sup>er</sup> janvier
1998 aux règles d'avant, le maximum de la pension « Cavimac » au prorata de la
durée — les années d'activité cultuelle d'avant 1979, que la caisse valide
gratuitement, comprises —, à soixante-cinq ans jusqu'en 2006, puis portée au
minimum contributif au taux plein et décotée sinon. Restent approchés : 2006,
où la fraction d'après 1997 s'ouvre à l'âge légal dix mois avant l'autre, et
que le modèle laisse toute l'année à soixante-cinq ans ; le taux plein du
régime général pour les majorations, que le décret n° 2006-1325 laisse à
soixante-cinq ans ; le maximum de 1982, 1984 et 1986, estimé. Cela ne touche
que le scénario 1 ; les comptes notionnels, eux, ne lisent que des
cotisations — celles de 1979 à 1997, que des arrêtés fixaient chaque année en
montants forfaitaires, prises aux taux du régime général sur le forfait du
SMIC.

**Les autres, et le mur devant chacun** : voir la couverture « à modéliser »
de l'inventaire, qui porte pour chacun ce qui bloque.

## Un rendement unique là où il faudrait une série

La fiche CARPIMKO met en lumière une approximation qui vaut pour TOUS les
régimes convertis par `rendements_points.csv` : le moteur applique **un seul
rendement, celui de l'année de liquidation**, aux cotisations revalorisées de
toute la carrière. Or le rendement de la CARPIMKO tombe de <!--chiffre:cellule(data/reference/regimes/rendements_points.csv:rendement*100?regime=carpimko_complementaire&debut=2010)-->13,10<!--/--> % en 2010 à
<!--chiffre:cellule(data/reference/regimes/rendements_points.csv:rendement*100?regime=carpimko_complementaire&debut=2025)-->7,36<!--/--> % en 2025. Une infirmière qui liquide en 2027 voit donc ses cotisations de
2010 converties au rendement de 2025 au lieu du leur, à peine plus de la moitié :
sa complémentaire ressort très en deçà de ce que l'accumulation année par année
en donnerait — d'un tiers, quand cette section a été écrite.

Le chemin exact existe déjà dans le moteur — `valeurs_point.csv`, qui accumule
des points année par année —, et la CARPIMKO a de quoi l'emprunter : son prix
du point implicite est le forfait divisé par 8, et il donne les mêmes points que
la part proportionnelle divisée par 22. Ce qui manque n'est pas la donnée mais
le raccordement : `valeurs_point.csv` est un fichier CERTIFIÉ, dont le journal
verrouille le nombre de lignes par niveau, et y verser des valeurs demande un
contrôle dans `verifier_donnees.py` — donc un récupérateur pour la valeur de
service, que la caisse publie en PDF depuis 2010.

**Au-delà du dernier barème publié, l'Agirc-Arrco achète ses points au salaire
de référence que ses accords indexent sur le salaire moyen** : celui du modèle,
<!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.salaire_moyen_nominal*100)-->2,45<!--/--> % par an au scénario de référence quand les prix montent de <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.inflation*100)-->1,75<!--/--> %, avec
un an de retard (fiche `agirc_arrco_valeur_achat`,
`regimes/prolongement_points.csv`). Le rendement de son dernier barème, <!--chiffre:cellule(data/reference/regimes/rendements_points.csv:rendement*100?regime=agirc_arrco&debut=2027)-->5,61<!--/--> %,
qui ne sert plus que de filet, faisait suivre les prix au prix d'achat, que les
accords du 10 mai 2019 et du 5 octobre 2023 font évoluer « comme le salaire
annuel moyen des ressortissants du régime », et l'accord du 17 novembre 2017
« en fonction » de ce salaire. La complémentaire d'une carrière à trente ans du
départ en ressortait de près d'un dixième au-dessus de « Mon estimation
retraite », dont la retraite de base concordait à l'euro (feuille de route,
action 142). Deux écarts demeurent, que la fiche mesure. Le salaire moyen du
modèle n'est pas celui des ressortissants du régime, et il devance un peu le
prix d'achat que la page prête aux années à venir : la complémentaire passe
d'un peu au-dessus de la page à un peu au-dessous. Et la valeur de service suit
les prix, la convention de la page, quand l'annexe de l'accord du 5 octobre
2023 la projette de 2027 à 2037 au salaire moyen moins <!--chiffre:valeur(data/reference/regles/agirc_arrco_valeur_achat.yaml:versions.id=salaire_moyen_2023_2026.contenu.parametres.soutenabilite_valeur_service_projetee*100)-->1,16<!--/--> % :
aucune source ne tranche avant l'accord qui couvrira 2027 à 2030. Les autres
régimes en points gardent au-delà de leur dernier barème le rendement de ce
barème. Pour l'Ircantec, c'est sa règle : l'arrêté du 30 décembre 1970
(article 9 bis) renvoie au plan quadriennal du conseil d'administration, qui
revalorise chaque 1<sup>er</sup> janvier le salaire de référence et la valeur
de service comme les pensions de base, sur l'inflation ; à défaut de plan,
l'arrêté ferait croître le premier des cinq tiers de cette revalorisation, la
seconde des deux tiers. Les prix toujours, jamais les salaires (fiche
`ircantec_valeurs_point`).

UN PIÈGE DÉCOUVERT EN CHEMIN, et refermé par un test. La table des tranches
d'assiette existe DEUX FOIS — `BORNES_ASSIETTE` dans `donnees/regimes.py` et
dans `moteur/js/regimes.js` —, parce que le portage ne lit pas le Python. La
tranche `tranche_1_3_pass` ajoutée pour la Cipav n'avait été écrite que d'un
côté : le JavaScript retombait sur `[0, null]`, c'est-à-dire SANS PLAFOND, et
cotisait 39 146 € là où le modèle en cotisait 19 356. Aucune erreur n'était
levée ; seule la comparaison des témoins l'a vu. Un test compare désormais les
deux tables.

## Le simulateur doit être juste à tout âge : où il ne l'est pas encore

Une fiche de régime porte des PÉRIODES, et chaque période un jeu de règles. Un
régime dont la fiche n'a qu'une période applique donc les mêmes règles à toute
son histoire — et comme les fiches sont écrites à partir des paramètres
d'aujourd'hui, c'est le droit de 2026 qu'elles appliquent à 1950. Le tableau
ci-dessous compte, pour chaque régime, le nombre d'ANNÉES par jeu de règles
distinct. Plus le nombre est grand, moins l'histoire du régime est dans le
modèle :

| Régime | Couverture | Jeux de règles | Années par jeu | Coupures de texte non reflétées | Réformes non portées |
|---|---|---|---|---|---|
| `port_strasbourg` | 1930-2026 | 1 | 97 | 0 | 0 |
| `marins` | 1930-2026 | 1 | 97 | 2 | 0 |
| `sncf` | 1930-2033 | 16 | 79 | 1 | 0 |
| `ratp` | 1930-2033 | 16 | 79 | 3 | 0 |
| `assemblees_parlementaires` | 1930-2030 | 22 | 79 | 0 | 0 |
| `banque_de_france` | 1930-2026 | 16 | 78 | 0 | 0 |
| `opera_de_paris` | 1930-2026 | 4 | 72 | 4 | 0 |
| `crpcen` | 1937-2026 | 16 | 71 | 0 | 0 |
| `fonctionnaires_pacifique` | 1959-2029 | 8 | 65 | 0 | 0 |
| `cafat_nouvelle_caledonie` | 1958-2026 | 5 | 65 | 0 | 0 |
| `comedie_francaise` | 1930-2026 | 4 | 63 | 1 | 0 |
| `cnbf` | 1948-2026 | 2 | 56 | 2 | 0 |
| `cps_polynesie` | 1968-2026 | 2 | 55 | 0 | 0 |
| `cnavpl` | 1949-2026 | 8 | 55 | 9 | 0 |
| `cavec_complementaire` | 1953-2026 | 5 | 55 | 0 | 0 |
| `ircec_racl` | 1962-2026 | 3 | 52 | 1 | 0 |
| `ircec_raap` | 1962-2026 | 6 | 52 | 1 | 0 |
| `ircec_racd` | 1964-2026 | 3 | 50 | 2 | 0 |
| `seita` | 1935-2026 | 8 | 49 | 0 | 0 |
| `cese_membres` | 1957-2026 | 14 | 48 | 0 | 0 |
| `carcdsf_complementaire` | 1949-2026 | 22 | 48 | 0 | 0 |
| `regimes_professionnels_integres` | 1947-1993 | 1 | 47 | 0 | 0 |
| `mines` | 1930-2026 | 22 | 44 | 1 | 0 |
| `cnbf_complementaire` | 1979-2026 | 2 | 40 | 0 | 0 |
| `cnracl` | 1945-2026 | 19 | 39 | 11 | 0 |
| `ieg` | 1946-2026 | 15 | 38 | 3 | 0 |
| `gerants_debits_tabac` | 1963-2026 | 2 | 37 | 10 | 0 |
| `cavom_complementaire` | 1979-2026 | 2 | 37 | 5 | 0 |
| `wallis_et_futuna` | 1975-2026 | 13 | 34 | 0 | 0 |
| `msa_non_salaries` | 1952-2026 | 7 | 34 | 13 | 0 |
| `cipav_complementaire` | 1979-2026 | 5 | 34 | 1 | 0 |
| `crpnpac_tranche_2` | 1963-2026 | 4 | 32 | 0 | 0 |
| `crpnpac` | 1963-2026 | 4 | 32 | 5 | 0 |
| `cps_polynesie_tranche_b` | 1995-2026 | 1 | 32 | 0 | 0 |
| `cavp_complementaire` | 1949-2026 | 8 | 29 | 2 | 0 |
| `chemins_fer_secondaires` | 1930-1954 | 1 | 25 | 0 | 0 |
| `organic` | 1949-2006 | 15 | 24 | 0 | 0 |
| `msa_rco` | 2003-2026 | 1 | 24 | 24 | 0 |
| `cancava` | 1949-2006 | 15 | 24 | 0 | 0 |
| `cprn_complementaire` | 1949-2026 | 10 | 22 | 2 | 0 |
| `cavamac_complementaire` | 1968-2026 | 8 | 22 | 5 | 0 |
| `ipacte` | 1951-1970 | 1 | 20 | 0 | 0 |
| `fspoeie` | 1930-2026 | 21 | 20 | 2 | 0 |
| `fonction_publique_etat` | 1948-2026 | 20 | 20 | 2 | 0 |
| `pensions_civiles_1853` | 1930-1948 | 1 | 19 | 0 | 0 |
| `ircantec` | 1971-2026 | 16 | 17 | 6 | 0 |
| `rafp` | 2005-2026 | 2 | 16 | 6 | 0 |
| `assurances_sociales` | 1930-1945 | 1 | 16 | 0 | 0 |
| `carpv_complementaire` | 1950-2026 | 10 | 15 | 0 | 0 |
| `organic_conjoints_batiment` | 1973-2003 | 4 | 13 | 0 | 0 |
| `asv_conventionnes` | 1972-2026 | 21 | 13 | 10 | 0 |
| `agirc` | 1947-2018 | 24 | 13 | 0 | 0 |
| `regime_general` | 1945-2026 | 33 | 12 | 0 | 0 |
| `rco_artisans` | 1979-2012 | 10 | 12 | 2 | 0 |
| `rci` | 2013-2026 | 2 | 12 | 2 | 0 |
| `msa_salaries` | 1945-2026 | 35 | 12 | 0 | 0 |
| `carpimko_complementaire` | 1984-2026 | 27 | 12 | 0 | 0 |
| `arrco` | 1961-2018 | 18 | 12 | 1 | 0 |
| `igrante` | 1960-1970 | 1 | 11 | 0 | 0 |
| `enseignants_prive_additionnel` | 2005-2026 | 6 | 11 | 1 | 0 |
| `cssm_mayotte` | 1987-2036 | 37 | 11 | 0 | 0 |
| `arrco_tranche_2_entreprises_nouvelles` | 1997-2018 | 6 | 11 | 0 | 0 |
| `arrco_tranche_2` | 1961-2018 | 22 | 9 | 0 | 0 |
| `nric` | 2004-2012 | 2 | 8 | 3 | 0 |
| `cavimac` | 1979-2026 | 22 | 8 | 0 | 0 |
| `carmf_complementaire` | 1949-2026 | 62 | 8 | 1 | 0 |
| `cps_saint_pierre_et_miquelon` | 1987-2037 | 37 | 7 | 0 | 0 |
| `agirc_entreprises_nouvelles` | 1981-2018 | 17 | 7 | 0 | 0 |
| `unirs` | 1957-1961 | 1 | 5 | 0 | 0 |
| `avts` | 1941-1945 | 1 | 5 | 0 | 0 |
| `agirc_arrco` | 2019-2026 | 2 | 5 | 0 | 0 |
| `rsi` | 2006-2018 | 7 | 4 | 1 | 0 |
| `rsi` | 2006-2018 | 2 | 10 | 4 | 0 |
| `arrco_tranche_2` | 1961-2018 | 22 | 9 | 0 | 0 |
| `nric` | 2004-2012 | 2 | 8 | 3 | 0 |
| `carmf_complementaire` | 1949-2026 | 62 | 8 | 1 | 0 |
| `agirc_entreprises_nouvelles` | 1981-2018 | 17 | 7 | 0 | 0 |
| `unirs` | 1957-1961 | 1 | 5 | 0 | 0 |
| `avts` | 1941-1945 | 1 | 5 | 0 | 0 |
| `agirc_arrco` | 2019-2026 | 2 | 5 | 0 | 0 |

**Ce tableau n'est plus écrit à la main** : c'est la sortie de
`python scripts/calendrier_regimes.py --carte`, relevée après les tranches B1
à B5d de la campagne « les règles à travers l'histoire » (voir
[`regimes.md`](regimes.md), journal de la campagne). Les deux dernières
colonnes viennent de l'index LEGI et du calendrier des réformes
(`legislation/reformes.yaml`) : une « coupure de texte non reflétée » est une
version d'un article pivot (`regimes/pivots.yaml`) qui commence une année où
aucune période de la fiche ne commence — un endroit où lire, pas un verdict,
car beaucoup de versions ne changent qu'un renvoi ; une « réforme non portée »
est un manque, et le test `test_toute_reforme_est_coupee_absorbee_ou_declaree`
impose qu'il n'y en ait aucune. Les deux premières lignes restent ce qui
résiste : le port autonome de Strasbourg, dont le règlement de retraite est un
acte de l'établissement et non un texte publié, et les marins, dont la formule
est stable depuis 1968 — vérifiée article par article —, et dont la grille des
salaires forfaitaires, lue au Journal officiel depuis 2008, ne demande pas de
période de plus : elle est une table annuelle, que la fiche lit à part.

Le nombre n'est pas à lui seul un verdict : un régime dont les règles n'ont pas
bougé mérite une seule période. Mais il
dit où chercher, et ce qu'on y trouve est parfois gros : le régime des salariés
agricoles portait une période pour quatre-vingt-seize ans, avec les paramètres de
2023 — un salarié agricole parti en 1980 se voyait opposer 172 trimestres au lieu
de 150 et calculer sur ses vingt-cinq meilleures années au lieu de dix.

**Les témoins ne le voyaient pas, et c'est le second enseignement.** Le balayage
par statut ne connaissait qu'une génération, née en 1975 : il ne visitait que les
périodes RÉCENTES de chaque fiche. Corriger le régime agricole n'a déplacé aucun
témoin. Chaque statut est donc désormais simulé à QUATRE générations — née en
1925, qui liquide vers 1990 ; née en 1935, qui liquide vers 1999, sous la durée
requise de 150 ou 160 trimestres et les dix meilleures années ; née en 1955, qui
liquide vers 2019 ; née en 1975, qui liquide après la réforme de 2023. Le fichier
de témoins passe de 138 à 250 cas, et une correction d'histoire s'y voit
maintenant. La génération 1925 est la dernière venue, et pour une raison
précise : les tables par génération ne répondent pas toutes en deçà de 1934, et
le défaut que cela cachait est raconté plus bas.

Ce qui a été refermé de cette façon jusqu'ici : le régime des salariés agricoles
(aligné sur le régime général, ses huit périodes reprises une à une), les régimes
alignés des artisans et des commerçants depuis 1973, le fonds spécial des
ouvriers de l'État (aligné sur le code des pensions, six périodes), la Banque de
France (alignée depuis 2007, quatre périodes) et la caisse des clercs de notaire
(trois périodes au lieu d'une depuis 2009, et le barème de décote de la fonction
publique que son décret lui donne) ; la durée requise de l'Opéra et de la
Comédie-Française ; les bornes d'âge de la RATP et des IEG, qui étaient celles de
2017 dès 2009 ; et la clause du grand-père des régimes fermés.

**Trois manières de se tromper, et elles reviennent.** La première est la fiche
d'un régime ALIGNÉ qui ne suit pas l'histoire de son modèle : on la corrige en
recopiant les périodes du régime général ou du code des pensions, ce qui est sûr
parce que l'alignement est une règle de droit. La deuxième est la période
OUVERTE — `fin: null` — qui porte les paramètres du jour : elle applique le droit
d'aujourd'hui à toute la période qu'elle couvre, et c'est ainsi qu'un agent de la
Banque de France parti en 2009 se voyait opposer l'âge de 2023. La troisième est
la réforme qui ne touche pas tout en même temps : celle de 2008 ne relève les
bornes d'âge des régimes spéciaux qu'à partir de 2017, et sa décote n'existe pas
avant le 1er juillet 2010 — elle monte ensuite en charge jusqu'en 2024, quand les
fiches la servaient pleine dès 2009.

## Ce que vaut une série qu'on ne peut pas certifier

Deux séries de taux ne se certifieront pas, et il fallait dire mieux que « pas
certifiées ». Le régime général d'avant 1982, que la base LEGI ne date pas ; et
les complémentaires du privé, dont les taux ne sont dans aucun texte
réglementaire. Les deux venaient d'OpenFisca-France.

**OpenFisca n'est pas la source.** Il transcrit les barèmes de l'Institut des
politiques publiques, qui sont l'amont — la page qui précède l'écrivait déjà,
pour dire que l'IPP « ne commence pas plus tôt que lui ». C'était vrai, et à
côté de la question : ce que l'IPP a et qu'OpenFisca perd en route, ce sont deux
colonnes. `reference` nomme le texte de chaque marche ; `official_journal_date`
donne sa publication. `scripts/fetch/ipp_taux_cotisation.py` les lit, et
`verifier_donnees.py` en tire trois constats à chaque exécution.

**Un : la confrontation vérifie une copie, pas une lecture.** Les soixante
années du régime général sont confrontées à l'IPP, et un écart y est une erreur
de recopie d'OpenFisca — non un désaccord entre deux témoins. Le contrôle le dit
dans ses propres mots, pour que personne ne prenne son « OK » pour une seconde
source. Il en a déjà trouvé une : OpenFisca servait 0,1 % de part salariale
déplafonnée **dès le 1er janvier 2004** quand elle naît le 1er juillet. La cause
était la même que celle du filtre de l'année, et au même endroit : l'exception
« année d'ouverture » s'appliquait à chaque composante au lieu de la seule année
où la série commence.

**Deux : la chronologie, elle, se vérifie.** Pour chaque marche, le récupérateur
cherche dans l'index JORF le texte que l'IPP nomme, au numéro et à la date
annoncés. **Trente-cinq des trente-six marches de la CNAV y sont** ; la seule qui
manque est le décret n° 70-680 du 30 juillet 1970, absent de l'index. Une valeur
transcrite reste une valeur transcrite, mais la DATE de chaque marche est
désormais vérifiée contre le *Journal officiel* — et c'est la date dont dépend
la règle du 1er janvier, celle qui déplaçait six années à elle seule.

**Trois : les complémentaires ne se certifieront pas, et c'est l'IPP qui le
dit.** Pour l'Agirc, l'Arrco et le régime unifié, il laisse lui-même la colonne
du *Journal officiel* VIDE sur ses vingt-cinq marches, et cite « Convention
AGIRC du 14 mars 1947 », « Accords ARRCO du 12 novembre 1986 »,
« Lettre-circulaire ARRCO 82-28 ». Ces taux sont fixés par accord collectif ; le
*Journal officiel* n'en publie que l'**avis d'extension**, qui renvoie au
Bulletin officiel Conventions collectives sans jamais écrire le chiffre — on
peut le lire dans la base, avis par avis, de 2006 à 2015. La fédération
Agirc-Arrco publie la compilation de ses valeurs de point, que le dépôt lit déjà,
mais aucun historique de taux : sa page « Paramètres » n'affiche que l'année
courante, et ses circulaires ne remontent qu'à 2003. La démonstration est
mécanique, et c'est ce qui la rend utile : si l'IPP se met un jour à remplir
cette colonne, le contrôle le dira.

**Et il a trouvé ce que personne ne cherchait.** Sur 1967-1981, le récupérateur
demande au JORF les décrets qui annoncent dans leur titre des taux de cotisation
du régime général, et compte ceux qu'aucune marche ne rejoint. Il en reste **un**,
et il est lourd : le **décret n° 79-650 du 30 juillet 1979** a relevé « à titre
exceptionnel, par dérogation aux dispositions du décret n° 78-1213 » les taux du
régime général « du 01-08 au 31-12-1979 et du 01-01-1980 au 31-01-1981 ». La
fenêtre couvre **deux premiers janvier**, 1980 et 1981. Ni l'IPP ni OpenFisca ne
la portent, et le dépôt en a conclu que les taux servis pour ces deux années
étaient **trop bas**, d'un montant que la notice n'écrit pas — elle ne nomme
même aucun risque, et le décret lui-même a disparu de LEGI avec sa date
d'expiration.

## La réforme agricole de 2026 est calculée, et ce qui en reste approché

L'article 87 de la loi n° 2025-199 du 28 février 2025 de financement de la
sécurité sociale réécrit `L. 732-24` : pour les pensions prenant effet à compter
du **1er janvier 2026**, la retraite de base des non-salariés agricoles n'est
plus la somme d'un forfait et de points de carrière entière, mais un calcul sur
les **vingt-cinq meilleures années** — de revenus à partir de 2016, de points
avant, les revenus n'étant pas connus plus tôt. Un dispositif transitoire
recalcule en 2028 les pensions liquidées en 2026 et 2027, au bénéfice de
l'assuré. Ses décrets ont paru au Journal officiel du 31 décembre 2025
(n° 2025-1409 et n° 2025-1410).

Le modèle la calcule (`liquider.pension_des_non_salaries_agricoles`, fiche
`pension_non_salaries_agricoles_2026`) : le revenu annuel moyen des meilleures
années depuis 2016, au taux et au prorata du régime général ; la retraite
forfaitaire au prorata de la seule durée d'avant 2016 ; la moyenne des points
des meilleures années d'avant 2016, arrondie à l'entier, multipliée par le
nombre de ces années ; les vingt-cinq années réparties entre régimes et entre
les deux périodes par `R. 173-3-2` ; la pension bornée à la moitié du plafond ;
et, pour les pensions de 2026 et 2027, la plus forte du calcul provisoire et du
recalcul. Le salaire annuel moyen des régimes alignés d'un ancien exploitant
ne retient que la part des années que la répartition leur laisse. Le modèle
rend l'exemple de la MSA : six, treize et six années, et une moyenne de trente et un
points multipliée par vingt-deux années.

Ce qui reste approché, et dans quel sens. Les années d'avant 1990, dont le
barème de points n'est pas lu, entrent dans la moyenne par l'équivalent en
points de leur rendement, qui les laisse sous les années du barème et hors des
meilleures. Le revenu des années cotisées au minimum, que la loi déduit des
cotisations acquittées, est porté au plancher de six cents SMIC horaires. Les
durées que `R. 173-3-2` arrête au 31 décembre de l'année d'effet sont celles de
la date d'effet. Les majorations de points de 1952 à 1972, les rachats et les
conjoints collaborateurs manquent, comme avant la réforme.

## La part patronale du public, et ce qu'on n'en sait pas

Les scénarios 4 et 5 ajoutent à la part salariale ce que verse l'employeur. Pour
un salarié du privé, la fiche du régime le porte — `part_salariale` en donne la
répartition, recoupée à OpenFisca année par année. Pour un agent public, elle
n'est dans aucune fiche : le modèle la lit dans
`legislation/contribution_employeur_public.csv`, qui couvre aujourd'hui huit
régimes, mais aucun sur toute sa durée. Partout ailleurs, la part patronale est
**estimée** par l'effort d'un salarié du privé de la même année — jamais laissée
à zéro, qui ferait retomber les scénarios 4 et 5 sur les 2 et 3 sans le dire —
la fiabilité de l'année retombe à `estimee`, et le nombre d'années concernées
est affiché sous la simulation.

| Régime | Couvert | Découvert | Ce qui manque |
|---|---|---|---|
| Fonction publique d'État | 1995-2026 | 1930-1994 | rien à retrouver : l'État ne versait aucune cotisation, les pensions étaient payées sur crédits budgétaires, et le plus ancien chiffrage a posteriori — le jaune « pensions » — s'arrête à 1995 ; ses militaires ont leur taux propre, appelé depuis 2006, dans `contribution_employeur_militaires.csv` |
| CNRACL | 1948-2028 | 1945-1947 | le décret fondateur date du 19 septembre 1947 ; la convention « taux au 1er janvier » fait donc commencer la série en 1948 |
| SNCF | 1992-2018 | 1930-1991, 2019- | avant 1992, aucun texte de la base LEGI ne porte le taux ; après 2018, le décret cesse de chiffrer la composante T2, qui évolue par formule |
| RATP | 2007-2025 | 1930-2006, 2026- | rien à retrouver : avant l'adossement de 2006, la RATP payait les pensions sans qu'aucun texte fixe un taux, exactement comme l'État avant son compte d'affectation spéciale ; après 2025, la série n'a pas encore sa ligne, et le dernier taux est reconduit au niveau `estimee` |
| IEG | 2005-2020 | 1946-2004, 2021- | avant 2005, EDF et GDF payaient les pensions directement ; après 2020, l'arrêté du 29 décembre 2021 remplace la fixation annuelle par une formule que la caisse applique sans la publier |
| Mines | 1984-2026 | 1930-1983 | la base LEGI ne garde aucune version de l'article 52 du décret de 1946 avant le 1er janvier 1984 |
| Opéra de Paris, Comédie-Française | 1992-2026 | 1930-1991 | même mur : les versions datées du décret qui fixe ces taux commencent au 1er juillet 1991 |
| FSPOEIE, marins, CRPCEN, Banque de France, port de Strasbourg, SEITA, chemins de fer secondaires | rien | tout | aucune série de taux employeur trouvée sous une forme exploitable. Pour ces sept régimes, la part patronale des scénarios 4 et 5 est celle d'un salarié du privé de la même année, et le modèle le dit |

**Ces taux sont ceux de l'employeur, non ceux de l'équilibre**, et c'est une
convention qui se défend mais qui se paie. Trois de ces régimes reçoivent aussi
de l'État une contribution que la série ne porte pas, parce qu'elle n'est pas
une cotisation d'employeur : les droits spécifiques de la RATP jusqu'à 45 000
agents, « une cotisation correspondant à <!--chiffre:illustration()-->22<!--/--> % des salaires » plus un complément
d'équilibre pour les mines — près de trois fois ce que verse l'exploitant —, la
subvention de l'Opéra. Pour la SNCF d'après 2007, la somme T1 + T2 laisse de
même dehors la subvention d'équilibre. La ligne de l'État est la seule exception
du tableau : son taux EST un taux d'équilibre. Un agent minier et un
fonctionnaire d'État ne sont donc pas mesurés à la même aune, et la différence
joue contre le mineur.

**Et ce taux d'équilibre paie plus que la retraite de l'agent.** La Cour des
comptes le décompose dans sa communication du 22 septembre 2026 sur les
retraites des fonctionnaires de l'État (tableau n° 15, recopié ligne à ligne
dans `legislation/contribution_etat_retraite_seule.csv`) : des <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2025&regime=fonction_publique_etat)-->78,28<!--/--> % appelés
en 2025 pour un civil, elle ne garde que <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=civils&poste=retraite_stricto_sensu)-->44,1<!--/--> % pour la retraite au sens
strict ; le reste finance l'invalidité avant soixante-deux ans, les majorations
pour enfants, les départs anticipés des emplois classés et, pour <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*-100?population=civils&poste=desequilibre_demographique)-->35,3<!--/-->
points, le déséquilibre démographique du régime. Pour un militaire, dont
l'employeur paie <!--chiffre:cellule(data/reference/legislation/contribution_employeur_militaires.csv:taux*100?annee=2025)-->126,07<!--/--> %, elle garde <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=militaires&poste=retraite_stricto_sensu)-->51,2<!--/--> %. Créditer au compte le taux entier,
comme le scénario 4, et le 6 jusqu'à la bascule, le faisaient jusqu'au
24 septembre 2026, c'était porter au compte d'un fonctionnaire d'État ce que
son employeur verse pour d'autres. Le militaire, lui, recevait jusqu'au même
jour le taux des civils, moins que ce que le sien verse : son taux propre, lu
dans les décrets qui le fixent, est dans
`legislation/contribution_employeur_militaires.csv` — <!--chiffre:cellule(data/reference/legislation/contribution_employeur_militaires.csv:taux*100?annee=2006)-->100<!--/--> % en 2006,
<!--chiffre:cellule(data/reference/legislation/contribution_employeur_militaires.csv:taux*100?annee=2013)-->126,07<!--/--> % depuis 2013.

**Le compte ne reçoit donc, par défaut, que la part de la Cour**
(`contribution_etat=retraite_seule`) : ce qui n'est pas contributif se finance
par l'impôt, non par le compte. Dans les options du site, « Contribution de
l'État portée au compte » rétablit le taux entier. L'année que la Cour a
mesurée, le compte reçoit ses deux taux ; les autres années, la même
proportion du taux versé à sa population — <!--chiffre:mesure(retraite_seule)-->56,3<!--/--> % pour un civil,
<!--chiffre:mesure(retraite_seule?militaire=1)-->40,6<!--/--> % pour un militaire, soit <!--chiffre:mesure(retraite_seule?militaire=1&annee=2020)-->51,2<!--/--> % chaque année depuis 2013, son taux
n'ayant pas bougé —, et c'est une hypothèse, que le résultat qualifie
d'`estimee`. Pourquoi une proportion
plutôt qu'un taux fixe : le rapport n'éclaire qu'une autre année, 2020, où le
taux était de <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2020&regime=fonction_publique_etat)-->74,28<!--/--> % ; la proportion y donne <!--chiffre:mesure(retraite_seule?annee=2020)-->41,8<!--/--> %, un taux fixe <!--chiffre:cellule(data/reference/legislation/contribution_etat_retraite_seule.csv:taux*100?population=civils&poste=retraite_stricto_sensu)-->44,1<!--/-->, et
la Cour — qui impute cinq points de l'écart avec l'Institut des politiques
publiques à la seule différence d'année (annexe n° 6) — environ <!--chiffre:illustration()-->39<!--/-->.
Ce que ce choix déplace est considérable. Sous le taux entier, la fonctionnaire
de l'exemple du README, née en 1975, aurait <!--chiffre:mesure(ecart?exemple=fonctionnaire&scenario=4&contribution_etat=entiere)-->+41,6<!--/--> % d'écart au système
actuel dans le scénario 4 ; sous la part de la Cour, <!--chiffre:mesure(ecart?exemple=fonctionnaire&scenario=4)-->−3,6<!--/--> %. Dans la
proposition, <!--chiffre:mesure(ecart?exemple=fonctionnaire&scenario=6&contribution_etat=entiere)-->+41,5<!--/--> % deviennent <!--chiffre:mesure(ecart?exemple=fonctionnaire&scenario=6)-->−5,6<!--/--> %, et le solde moyen de la proposition
passe de <!--chiffre:mesure(solde_moyen?scenario=6&contribution_etat=entiere)-->−1,47<!--/--> % à <!--chiffre:mesure(solde_moyen?scenario=6)-->−0,90<!--/--> % du PIB, de <!--chiffre:mesure(solde_moyen?scenario=6&en=milliards&contribution_etat=entiere)-->−44<!--/--> à <!--chiffre:mesure(solde_moyen?scenario=6&en=milliards)-->−27<!--/--> milliards
d'euros par an, parce que les droits qu'elle reprend à la bascule étaient
gonflés de ce qui payait d'autres pensions. Le privé, la CNRACL, le scénario 1
et la part salariale ne bougent pas, ni les années d'avant 1995, où le compte
reçoit déjà l'effort d'un salarié du privé. Un point reste ouvert, que
l'action 129 de la feuille de route détaille : une série mesurée année par
année, plutôt qu'une proportion prêtée à trente ans de taux.

**Ce que les documents budgétaires ajoutent, et ce qu'ils n'ajoutent pas.** Les
projets annuels de performances annexés au PLF 2026 — programmes 195, 197 et
198 —, lus le 20 septembre 2026 et saisis dans
`regimes/pap_regimes_subventionnes.csv`, donnent ce taux d'équilibre que la
série laisse dehors : la subvention rapportée aux pensions servies vaut 0,60 à
0,64 à la SNCF et 0,58 à 0,62 à la RATP, chaque année de 2012 à 2023 ; pour les
marins, la subvention inscrite pour 2026 couvre les trois quarts de la dépense
de pensions prévue. Ils ne donnent en revanche aucun TAUX employeur : les
cotisations reçues de la RATP y sont en millions d'euros, salariés et
employeur confondus, et l'ENIM n'y a que sa subvention. Le tableau ci-dessus
ne bouge donc pas — il compte des séries de taux —, et la ligne « rien /
tout » des sept régimes non plus. Depuis le 1er janvier 2025, ces crédits ne
vont d'ailleurs plus aux régimes : la CNAV les équilibre en dernier ressort et
l'État la compense, net de la compensation démographique et des cotisations
que la fermeture a portées au régime général et à l'Agirc-Arrco, si bien que
les crédits 2026 ne se comparent pas à la subvention d'avant.

Trois conséquences à garder en tête.

**Plus une carrière publique est ancienne, moins le scénario 4 s'écarte du
scénario 2** — non parce que le financement d'alors ressemblait à celui du
privé, mais parce qu'on ne le connaît pas.

**Le repli n'est pas neutre, et il ne l'était pas dans le sens qu'on croyait.**
Là où la série manquait, le modèle prêtait au régime l'effort d'un salarié du
privé — de l'ordre de <!--chiffre:mesure(fiche?exemple=salaire_moyen&quoi=total)-->27,98<!--/--> % en 2026. Les taux lus sont tantôt plus élevés (la
RATP, <!--chiffre:valeur(data/reference/regimes/ratp.yaml:periodes.debut=2025.taux_cotisation_retraite*100)-->12,29<!--/--> % de retenue et <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2025&regime=ratp)-->19,13<!--/--> % d'employeur en 2025), tantôt bien
plus bas (les mines et leurs <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=mines)-->7,75<!--/--> %, l'Opéra et ses <!--chiffre:cellule(data/reference/legislation/contribution_employeur_public.csv:taux*100?annee=2026&regime=opera_de_paris)-->9,56<!--/--> %). Le repli
surestimait donc la part patronale des régimes à faible cotisation d'employeur
et la sous-estimait pour les régimes adossés : ce n'était ni un plancher ni un
plafond, mais un brouillage.

**Le scénario 5 ne voit presque jamais la contribution publique.** Il n'ouvre
son compte qu'à la bascule, et à compter de la bascule le régime unique remplace
tous les régimes : la part patronale y est celle du statut pivot privé, pas
celle d'un employeur public. Ce que le scénario 5 mesure après 2026 est donc la
répartition du régime unique, non le financement de la fonction publique — qui,
par construction, n'existe plus.

## Le scénario 6, et ce que sa garantie ne voit pas

Le scénario 6 — le scénario 4 jusqu'à la bascule, puis un taux unique de <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> %
pour tous, plus une garantie vieillesse individualisée, financée par l'impôt —
hérite des limites du scénario 4, part patronale inconnue du public comprise :
ce qui a été cotisé avant la bascule y est porté aux mêmes taux, et estimé là
où le 4 l'estime. Il en ajoute d'autres, que les paragraphes suivants
prennent une à une.

**La garantie est ouverte à <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans, et le modèle sert désormais ce qu'elle
doit à qui est parti plus tôt.** *Corrigé le 19 septembre 2026.* Avant <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans
on ne touche pas le minimum vieillesse ; à partir de <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans on le touche, même
si l'on a liquidé à <!--chiffre:illustration()-->62<!--/-->. Le complément est donc CALCULÉ dans tous les cas, et il
n'entre dans la pension affichée que lorsqu'il est dû dès le départ ; la page
de simulation dit l'année où il s'ouvre, et le montant qu'il vaudra.

**La garantie regarde l'ENSEMBLE de la pension obligatoire.** *Tranché le
19 septembre 2026 par le programme.* Les <!--chiffre:mesure(parametre?nom=taux_cotisation_liberal)-->18<!--/--> % de répartition et les <!--chiffre:mesure(parametre?nom=taux_capitalisation_obligatoire)-->5<!--/--> %
capitalisés sont comparés ensemble au plancher : une allocation différentielle
compte les ressources, non leur origine. La rente du pilier réduit donc le
complément euro pour euro, et c'est ce qui coûte le moins à l'impôt. Le modèle
laissait jusque-là cette rente hors du calcul, faute que la question — de
droit, pas de modèle — ait été tranchée.

**La garantie ne sert que les retraités qui résident en France.** *Corrigé
le 23 septembre 2026.* Elle remplace l'ASPA, qui exige une résidence stable et
régulière en France (article L. 815-1), et en garde la condition. L'enquête
sur laquelle son coût se chiffre compte aussi les retraités partis à
l'étranger — <!--chiffre:cellule(data/reference/macro/pensions_residence.csv:valeur?annee=2020&residence=etranger&indicateur=effectifs&sexe=ensemble)-->905<!--/--> milliers en 2020, dont la pension française moyenne est de
<!--chiffre:cellule(data/reference/macro/pensions_residence.csv:valeur?annee=2020&residence=etranger&indicateur=pension_droit_direct&sexe=ensemble)-->437<!--/--> € brut par mois, parce que leur carrière française a été courte : presque
tous sont sous le plancher. Le dépôt les servait, et le coût de la garantie
s'en trouvait gonflé d'un cinquième environ. Il les retire de la distribution
par la seule information que l'enquête publie sur eux — leur effectif et leurs
quantiles —, et vérifie que les déciles des résidents en France qui en
sortent sont ceux qu'elle publie. Ce qui reste d'approché : entre deux
quantiles, leur répartition est supposée uniforme. La simulation individuelle
applique la même condition depuis le 1er octobre 2026 : qui déclare résider
hors de France ne reçoit pas la garantie, au départ ni aujourd'hui.

**Les montants sont des euros de 2026, déflatés par les prix.** <!--chiffre:mesure(parametre?nom=garantie_vieillesse_mensuelle)-->800<!--/--> € et <!--chiffre:mesure(parametre?nom=allocation_isolement_mensuelle)-->250<!--/--> €
sont ceux de la proposition ; une liquidation de 1995 les reçoit ramenés par
l'indice des prix, comme l'ASPA entre deux ancres de son barème. Ce n'est
qu'une convention : rien ne dit qu'une garantie créée en 2026 aurait été
indexée sur les prix depuis 1941.

**Ce que la garantie coûte aujourd'hui, dans la trajectoire.** Le barème est
appliqué, année par année, à la distribution des pensions de l'échantillon
interrégimes de 2020, déplacée du facteur que la grille donne : la pension
moyenne que la garantie regarde, rapportée à celle du système actuel en 2020.
Ce facteur vaut <!--chiffre:mesure(garantie?annee=2020&quoi=facteur)-->0,61<!--/--> en 2020 et <!--chiffre:mesure(garantie?annee=2070&quoi=facteur)-->0,99<!--/--> en 2070. La garantie coûte
<!--chiffre:mesure(part_pib?scenario=garantie&annee=2026)-->0,47<!--/--> % du PIB en 2026 — <!--chiffre:mesure(cout_annee?scenario=garantie&annee=2026)-->14<!--/--> milliards d'euros de 2026, <!--chiffre:mesure(garantie?annee=2026&quoi=beneficiaires)-->2,8<!--/--> millions de
bénéficiaires — et <!--chiffre:mesure(part_pib?scenario=garantie&annee=2070)-->0,35<!--/--> % en 2070 — <!--chiffre:mesure(cout_annee?scenario=garantie&annee=2070)-->14<!--/--> milliards, <!--chiffre:mesure(garantie?annee=2070&quoi=beneficiaires)-->2,7<!--/--> millions —, soit
<!--chiffre:mesure(cumul_avenir?scenario=garantie)-->616<!--/--> milliards constants cumulés sur la projection ; le passé, où le même
déplacement est appliqué à rebours, en porte <!--chiffre:mesure(cumul_passe?scenario=garantie)-->1 408<!--/--> depuis 1959. Ces chiffres
sont bruts des reprises sur succession ; la sous-section qui suit dit comment
chacun a été établi.

Ce que cette méthode suppose, et qui reste une limite : la FORME de la
distribution est celle de 2020, déplacée sans être déformée, le passé comme
l'avenir ; le déplacement est proportionnel et uniforme, quand le scénario ne
déplace pas toutes les carrières du même rapport ; et les retraités de moins
de <!--chiffre:mesure(constante?de=retraite_notionnelle.scenarios.actuel&nom=MinimumVieillesse.AGE_OUVERTURE)-->65<!--/--> ans, qui attendent la garantie, sont supposés répartis comme les autres.
Une seule méthode sur toute la série, plutôt qu'une falaise entre deux.

**Ce que la garantie n'est plus : une dépense du compte des cotisants.** Elle
est financée par l'impôt, et elle a donc quitté la masse contributive du
scénario 6, où elle était comptée jusqu'ici. C'est la symétrie de ce que la
recette fait déjà — la CSG de solidarité sort des ressources —, et sans elle la
garantie aurait été payée deux fois : une fois par les cotisations, une fois
par le contribuable.

## L'âge légal de la proposition : ce que le report suppose

La proposition fixe l'âge légal de départ à <!--chiffre:mesure(parametre?nom=age_legal_liberal)-->65<!--/--> ans à compter de la
bascule (`Parametres.age_legal_liberal`). Qui serait parti plus tôt sous le
droit en vigueur liquide la pension du scénario 6 à cet âge ; qui partait à
cet âge ou après, et qui a liquidé avant la bascule, n'est pas touché. Le
modèle le calcule en PROLONGEANT la carrière jusqu'à l'âge légal
(`Carriere.prolongee`), et le report suppose cinq choses.

**La dernière année se prolonge.** Même statut, même nature de période, même
salaire relatif, avancé au rythme du salaire moyen. C'est une convention, et
elle est la même pour toutes les carrières, qu'elles viennent d'un profil,
d'un parcours ou d'un relevé : un relevé n'a pas de profil à prolonger. Elle
fait travailler l'agent de conduite, l'agent des IEG ou le militaire dans
leur statut jusqu'à l'âge légal, là où beaucoup en changeraient ; mais à
compter de la bascule tout le monde cotise au même taux unique sur le même
revenu, et c'est le revenu seul qui compte. C'est TOUTE la dernière année qui
se prolonge : l'activité principale et chaque activité cumulée qui court
encore au départ, chacune à son revenu — jusqu'au 23 septembre 2026, seule la
dernière ligne de l'année le faisait, et le salarié qui exerçait aussi en
libéral perdait son salaire pendant les années du report. Qui finissait sa
carrière au chômage la finit au chômage, et une carrière qui s'arrêtait avant
son départ ne gagne aucune année travaillée. Sur le site, un relevé n'en est
plus une : il se prolonge d'abord jusqu'à son départ, à la même convention
(§ 5, « Les carrières réelles »), et le report le poursuit ; qui y déclare
ses dernières années sans activité les finit sans activité.

**Le report est immédiat.** Toute liquidation qui prendrait effet à compter du
1<sup>er</sup> janvier de la bascule est portée à l'âge légal, sans montée en
charge par génération comme en ont eu les réformes de 2010 et de 2023. La
proposition n'en prévoit pas ; une montée en charge adoucirait les premières
années, au prix du solde.

**La moitié de ceux que le report fait attendre sont en emploi — par
défaut.** Sur la page Coût, la recette de la proposition est son taux
appliqué à l'assiette que le COR projette aux âges d'aujourd'hui ; le report
l'élargit du rapport des revenus d'activité de la grille sous les deux âges
(`SoldeAnnuel.facteur_assiette`). Or tous les seniors ne sont pas en emploi :
qui arrive à l'âge légal au chômage ou en invalidité ne cotise pas davantage,
et ce que l'assurance chômage ou l'invalidité lui verseraient pendant
l'attente n'est compté nulle part. Un paramètre le dit,
`Parametres.part_reportes_en_emploi`, <!--chiffre:mesure(parametre?nom=part_reportes_en_emploi)-->50<!--/--> % par défaut : chaque cohorte
reportée de la grille mêle ceux qui travaillent et cotisent jusqu'à l'âge
légal et ceux qui l'attendent sans activité, sans cotiser ni acquérir de
droits, et liquident au même âge ; ses recettes comme ses pensions sont celles
de ce mélange (`VoletLiberal.melange`). Il ne joue que sur la page Coût ; le
simulateur prolonge la situation de chacun.

La part est lue, depuis le 7 octobre 2026, dans les évaluations de la réforme
de 2010, qui a reculé l'âge légal de 60 à <!--chiffre:illustration()-->62<!--/--> ans : trois ont suivi ce que sont
devenus ceux qu'elle a fait attendre. La plus récente, sur l'échantillon
interrégimes de cotisants, trouve que « la moitié passe plus de temps en
emploi, et environ un quart reçoit une allocation chômage » (IPP, rapport
n° 61, novembre 2025, § 5.2.1) ; c'est aussi la convention du simulateur du
COR. Les deux autres l'encadrent : <!--chiffre:illustration()-->37<!--/--> % sur les données de la Cnav, qui
voient l'invalidité et la maladie (Rabaté et Rochut, document n° 11 de la
séance du COR du 19 octobre 2016), <!--chiffre:illustration()-->63<!--/--> % des hommes et <!--chiffre:illustration()-->73<!--/--> % des femmes sur
l'enquête Emploi, dont le champ écarte les invalides, les allocataires de
l'AAH et qui a fini ses études avant <!--chiffre:illustration()-->18<!--/--> ans (Insee Analyses n° 30, janvier
2017). Jusque-là, la page supposait que tous travaillaient : c'était un
plafond. Les trois portent sur le secteur privé et sur un report de 60 à
<!--chiffre:illustration()-->62<!--/--> ans ; un fonctionnaire que l'âge légal fait attendre garde son emploi, et
la proposition fait attendre jusqu'à <!--chiffre:mesure(parametre?nom=age_legal_liberal)-->65<!--/--> ans.

C'est de cette part que dépend l'essentiel de ce que l'âge légal fait au
solde. Le solde moyen de la proposition est de <!--chiffre:mesure(solde_moyen?scenario=6)-->−0,90<!--/--> point de PIB quand
la moitié des reportés travaillent, de <!--chiffre:mesure(solde_moyen?scenario=6&emploi_reportes=1)-->−0,75<!--/--> quand tous le font, de
<!--chiffre:mesure(solde_moyen?scenario=6&emploi_reportes=0)-->−1,05<!--/--> quand aucun, contre <!--chiffre:mesure(solde_moyen?scenario=6&age_legal=aucun)-->−1,25<!--/--> sans âge légal et <!--chiffre:mesure(solde_moyen?scenario=1)-->−1,13<!--/--> pour le système
actuel : sans emploi, le report n'épargne guère que des années de pension, et
sert ensuite des pensions plus fortes. Aucun impôt ne couvre ce qui reste —
la TVA à taux unique qui le faisait du 23 au 24 septembre 2026 est retirée —,
et le déficit s'accumule : la dette de la proposition en 2070 est de <!--chiffre:mesure(dette?scenario=6)-->59<!--/--> % du
PIB quand la moitié des reportés travaillent, de <!--chiffre:mesure(dette?scenario=6&emploi_reportes=1)-->49<!--/--> % quand tous le font,
de <!--chiffre:mesure(dette?scenario=6&emploi_reportes=0)-->70<!--/--> % quand aucun, contre <!--chiffre:mesure(dette?scenario=1)-->66<!--/--> % pour le système actuel et <!--chiffre:mesure(dette?scenario=6&age_legal=aucun)-->86<!--/--> % pour
la proposition sans âge légal. L'ampleur de son avantage sur le système actuel
tient donc à ce que les reportés travaillent. Elle serait bien moindre si le
compte d'un fonctionnaire d'État recevait le taux de l'État entier, et non sa
seule part « retraite » : la dette atteindrait alors
<!--chiffre:mesure(dette?scenario=6&emploi_reportes=0&contribution_etat=entiere)-->109<!--/--> % si aucun ne travaillait.

**Le PIB ne bouge pas.** Plus d'emploi ferait plus de production, et le modèle
garde le PIB que le COR projette aux âges d'aujourd'hui. Toutes les parts de
PIB de la proposition sont donc rapportées à un dénominateur un peu trop bas.

**La dépense et la recette se lisent en une marche.** La cascade de la page
Coût porte le taux unique et l'âge légal dans une seule marche, parce que le
modèle ne calcule pas la proposition sans l'un des deux ; elle le dit dans son
étiquette. Mesurer l'âge seul se fait en comparant le réglage par défaut à
`age_legal_liberal=None`.

Ce que le report n'est pas : une baisse de la pension mensuelle. Dans un compte
notionnel, partir plus tard ajoute des cotisations et raccourcit la retraite,
et les deux relèvent la pension ; ce qui se perd, ce sont les années de
pension d'avant l'âge légal. Et il ne relève rien pour qui partait déjà à cet
âge ou après, le compte n'ayant ni décote ni surcote à déplacer. La garantie
vieillesse, ouverte au même âge, est désormais due dès le départ à toute
liquidation que la proposition régit ; elle ne reste différée que pour les
départs antérieurs à la bascule, que le scénario 6 recalcule rétroactivement.

Les scénarios 2 à 5 gardent les âges du droit en vigueur : ils mesurent ce que
change le compte, à carrière égale, et un âge différent y mêlerait deux effets.
L'âge de référence des scénarios prospectifs suit l'âge légal
(`age_reference_fixe`, <!--chiffre:mesure(parametre?nom=age_reference_fixe)-->65<!--/--> ans) ; il
ne pèse que sur la conversion des droits acquis.
