# 5 ter. La trajectoire projetée : ce qu'elle suppose, et ce qu'elle vaut

La seconde moitié de la page **Coût** projette les six systèmes de 2025 à 2070.
Rien n'y est certifié, rien ne peut l'être, et le lecteur doit savoir sur quoi
chaque chiffre repose. La dépense du système actuel, elle, n'est pas du modèle :
c'est celle que le COR projette dans son dernier rapport, à la part de PIB près
(`test_la_trajectoire_du_systeme_actuel_est_celle_du_cor`) ; les autres systèmes
en sont tirés par le rapport de masses du modèle.

**Ce qui n'est pas de nous.** La démographie est celle du scénario central des
projections de population 2026 de l'INSEE : effectifs par âge de 1962 à 2070,
observés jusqu'en 2023. C'est cette source qui fixe l'horizon de la page — 2070
et pas 2080 — et non une préférence du dépôt. L'INSEE publie seize autres
scénarios ; leur écart mesurerait l'incertitude démographique, que cette page ne
montre pas. Les hypothèses macroéconomiques sont celles du COR, déjà décrites
dans `data/reference/macro/hypotheses_projection.yaml`.

**Ce qui est de nous, et qui se discute.** Le PIB projeté suit le rythme nominal
du COR — <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.pib_nominal*100)-->2,45<!--/--> % par an dans le scénario de référence — **composé avec sa
trajectoire d'emploi**, qui recule de <!--chiffre:mesure(emploi_projete)-->−6<!--/--> % d'ici 2070. C'est la convention que
`hypotheses_projection.yaml` énonce pour tout le dépôt (« le PIB nominal suit la
même convention que la masse salariale »), et c'est la même série que lit
l'indexation des comptes : la page n'a plus de PIB à elle.

Elle en avait un jusqu'au 20 septembre 2026, et c'était le paramètre le plus
discutable de la section : le rythme du COR corrigé par la **population des
20-64 ans**, qui recule de 10 % là où son emploi recule de 6 %. Ce proxy avait
été posé contre une hypothèse d'emploi constant, qui aurait prêté à la France de
2070 douze pour cent d'actifs qu'aucune projection ne lui donne ; l'hypothèse a
disparu le même mois (action 46), le proxy lui a survécu quelques jours, et le
dépôt a porté pendant ce temps TROIS PIB projetés — celui-ci, celui de
l'indexation, et celui qu'implique le compte du COR. Une part de PIB dont le
dénominateur n'est pas celui du reste du dépôt ne se compare à rien. La
substitution rend 1,05 point : la trajectoire 2070 passe de 19,4 à **18,35 %**,
et c'est du dénominateur seul — aucune pension ne bouge.

**Ce que la substitution laisse ouvert.** Le PIB reste UNIQUE PAR ANNÉE, commun
aux six systèmes. C'est ce qui rend les six courbes comparables, et c'est aussi
une hypothèse : la trajectoire d'emploi ne s'applique qu'aux systèmes 2 à 6
(action 46, « un emploi qui bouge sous la réforme, pas sous le droit constant »),
alors que le PIB qu'elle produit sert de dénominateur aux six. Un système qui
déplacerait réellement l'emploi déplacerait son propre dénominateur, et la page
ne sait pas le montrer.

**Ce qui n'est pas modélisé.** Le taux de couverture est supposé constant : le
modèle compte des générations, non des cotisants, et suppose que la même
proportion de chacune perçoit une pension et que la carrière type ne change pas.
Un recul de l'âge effectif de départ, une carrière plus longue ou plus hachée
déplaceraient la trajectoire. Aucune règle de pilotage n'est appliquée non plus :
un système notionnel réel porte un coefficient d'équilibre qui ajusterait toutes
ses pensions par un même facteur — commun, donc sans effet sur les écarts entre
carrières, mais avec effet sur les courbes de cette page. Ce coefficient est
désormais CALCULÉ, section « Le solde, et non le coût » de la même page, à
partir des ressources que le COR publie ; il n'est toujours pas appliqué, et le
§ 5 dit ce que cette distinction coûte.

**Ce que le pas de la grille laisse passer.** Une génération sur cinq est
simulée, et chacune représente les cinq classes d'âge qui l'entourent, décalées
d'un an à deux ans, chacune liquidant sa propre année. Une cohorte qui part
juste avant la bascule est donc représentée par une génération qui part juste
après, et hérite de son traitement : les courbes prospectives s'écartent de la
courbe actuelle d'un à deux dixièmes de pour cent avant même la bascule. Le
résidu est mesuré et un test le borne à un demi-point. La proposition, elle,
n'en hérite plus depuis le 28 septembre 2026 : une cohorte partie avant la
bascule y reçoit la pension du scénario dont elle part, sans mois au taux
unique ni pilier, et sa dépense égale celle du scénario 4 au centime chaque
année qui précède la bascule. Le pas commande le temps
de calcul de la page ; il ne doit pas commander la forme du résultat, et c'est
pourquoi les cinq cohortes ne basculent pas le même jour — sans quoi la
trajectoire avancerait par marches de cinq ans.

**Le contrôle externe, et ce qu'il dit.** Le COR projette la même grandeur avec
un modèle de population complet et une méthode qui n'a rien de commun avec
celle-ci : il trouve <!--chiffre:cellule(data/reference/macro/comptes_retraite.csv:part_pib*100?annee=2024&poste=depenses)-->13,9<!--/--> % du PIB en 2024 et **<!--chiffre:cellule(data/reference/macro/comptes_retraite.csv:part_pib*100?annee=2070&poste=depenses)-->15,3<!--/--> % en 2070** (rapport annuel
de juin 2026, champ « ensemble des régimes légalement obligatoires, y compris
FSV, hors RAFP »). Le modèle, laissé à lui-même — sa masse de pensions mise à
l'échelle de la dernière année publiée —, trouve <!--chiffre:mesure(part_pib?scenario=1&annee=2024)-->13,6<!--/--> % et **<!--chiffre:mesure(trajectoire_propre?annee=2070)-->14,80<!--/--> %**. Trois dixièmes de point
d'écart au départ — l'affaire du périmètre, la répartition obligatoire des
Comptes de la protection sociale n'étant pas exactement celle du COR — et
**un demi-point à l'arrivée, du même côté** : depuis l'étape 14 de l'action
147, la trajectoire propre croît un peu moins vite que celle du COR, surtout
au milieu de la période. Elle finissait un dixième sous lui à l'étape 13,
quatre dixièmes à l'étape 11, un point au-dessus jusqu'à l'étape 10, deux et
demi jusqu'à l'étape 8. C'est pourquoi, depuis le 5 octobre 2026, la page
ne prend plus au modèle la dépense du système actuel projetée : elle prend celle
du COR, année par année, et n'emprunte au modèle que le rapport de masses qui
en tire les autres systèmes (action 147). Le chiffre que le lecteur retrouve
dans le rapport du COR est donc celui qu'il lit sur la page ; l'écart, lui,
demeure dans le rapport, et les deux contrôles qui suivent le mesurent.

**Le contrôle interne : refaire le passé.** Au-delà de la dernière année
publiée, le coût du système actuel est la masse de pensions des cas types, mise
à l'échelle par l'ancrage qui la rend égale à la dépense de cette année-là. La
même formule, appliquée aux années publiées, devrait retrouver ce qui a été
dépensé (`Avenir.reconstitution`) ; elle s'en écarte de <!--chiffre:mesure(reconstitution?annee=2000)-->−14,5<!--/--> % en 2000, de
<!--chiffre:mesure(reconstitution?annee=2009)-->−16,3<!--/--> % en 2009 et de <!--chiffre:mesure(reconstitution?annee=2020)-->−3,8<!--/--> % en 2020, et de <!--chiffre:mesure(reconstitution?annee=1990)-->−23,8<!--/--> % en 1990. La masse du
modèle croît donc plus vite que la dépense réelle, et l'ancrage reporte cette
dérive sur l'avenir : c'est le symptôme le plus direct de l'écart au COR.
L'ancrage suppose, sans le vérifier, que l'écart des cas types au réel est le
même pour toutes les générations. Il ne suppose plus que la réversion garde sa
part de l'année d'ancrage : la base la porte chaque année à celle de la série
du COR que le dépôt porte, de
<!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2024)-->10,4<!--/--> % de la masse versée en 2024 à <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2070)-->5,7<!--/--> % en 2070, et à celle de 2010
avant, faute de série (`AvenirAnnuel.facteur_reversion`). Il ne garde plus non
plus la structure de la grille : les poids des cas types sont calés sur la
dépense que le COR donne à chacun de ses six groupes de régimes l'année où il
les publie tous, réversion comprise, faute de droits directs par groupe, et
tous les systèmes en héritent (`_poids_par_groupe`). Le RAFP, que le COR laisse
hors de son champ, n'est pas dans la pension du scénario 1, qui écarte les
régimes hors répartition. Un test tient le pire écart
depuis 2000 sous un cliquet, qui ne doit que descendre jusqu'à quelques pour
cent (`test_la_projection_refait_le_passe`) ; l'action 147 de la feuille de
route en est le chantier.

**Le contrôle par la décomposition du COR : les retraités se suivent, la
pension moyenne non.** La masse des pensions de droit direct est un nombre de
retraités multiplié par une pension moyenne. Le COR publie les deux facteurs —
le rythme des effectifs de retraités sous-période par sous-période (tableau
2.1 du rapport de juin 2026) et la pension moyenne de l'ensemble des retraités
rapportée au revenu d'activité moyen (figure 2.3), que le dépôt porte depuis
le 5 octobre 2026 dans `decomposition_depense_retraite.csv` et
`croissance_depense_retraite.csv` —, et le modèle compte les siens
(`Avenir.decomposition`). De 2025 à 2070, le COR compte
<!--chiffre:mesure(decomposition?facteur=retraites&de=2025&a=2070&source=cor)-->27,6<!--/--> % de
retraités de plus, le modèle
<!--chiffre:mesure(decomposition?facteur=retraites&de=2025&a=2070)-->26,2<!--/--> % : ce n'est pas par
les têtes que la trajectoire s'écarte. La pension moyenne relative, elle, recule
de <!--chiffre:mesure(decomposition?facteur=pension_relative&de=2025&a=2070&source=cor)-->−17,2<!--/--> %
chez le COR et de
<!--chiffre:mesure(decomposition?facteur=pension_relative&de=2025&a=2070)-->−15,0<!--/--> % seulement
dans le modèle ; et sur le passé, de 2005 à 2025, elle a crû de
<!--chiffre:mesure(decomposition?facteur=pension_relative&de=2005&a=2025&source=cor)-->8,9<!--/--> %
quand le modèle la fait croître de
<!--chiffre:mesure(decomposition?facteur=pension_relative&de=2005&a=2025)-->15,4<!--/--> %. L'écart
de 2070 et celui de la reconstitution sont donc un seul et même défaut : la
pension que la grille sert à chaque retraité progresse, d'une génération à
l'autre, plus vite que la pension moyenne réelle. Deux tests le tiennent,
`test_la_projection_compte_les_retraites_du_cor` et, sous un cliquet,
`test_la_pension_moyenne_relative_s_ecarte_de_celle_du_cor`.

La figure 2.7 du COR dit où, régime par régime. La pension moyenne relative de
la Cnav y varie de
<!--chiffre:mesure(decomposition?facteur=pension_relative&groupe=cnav&de=2025&a=2070&source=cor)-->0,3<!--/--> %
de 2025 à 2070 ; celle de l'Agirc-Arrco de
<!--chiffre:mesure(decomposition?facteur=pension_relative&groupe=agirc_arrco&de=2025&a=2070&source=cor)-->−41,9<!--/--> %,
celle de la fonction publique d'État de
<!--chiffre:mesure(decomposition?facteur=pension_relative&groupe=fpe&de=2025&a=2070&source=cor)-->−37,1<!--/--> %.
Deux conventions que le COR écrit y concourent, et le modèle les suit depuis
l'étape 4 de l'action 147 (`conventions_points` et `traitement_indiciaire`
de `macro/hypotheses_projection.yaml`) : à l'Agirc-Arrco, une valeur de
service qui suit le salaire moyen minoré d'un coefficient de soutenabilité de
2027 à 2037, puis un rendement stabilisé, valeur de service et valeur d'achat
suivant le salaire moyen sous un coefficient moindre (rapport de juin 2026,
partie 1, chapitre 2, « Le pilotage de l'Agirc-Arrco ») — à la liquidation
comme pour les pensions servies que la page Coût revalorise ; dans la fonction
publique, un traitement indiciaire qui décroche du salaire moyen jusqu'en 2037,
et une part des primes qui croît d'autant (annexe méthodologique, note 40),
quand la pension se calcule sur le seul traitement indiciaire. Il ne les suit
que pour la page Coût (`Parametres.conventions_cor`) : le simulateur individuel
et la page Cas types comptent les points de l'Agirc-Arrco à leur valeur
d'aujourd'hui, revalorisée comme les prix, la convention de « Mon estimation
retraite », et gardent la part des primes de chaque carrière ; une bulle, à côté
des chiffres de chaque page, dit laquelle s'applique. La seconde ne vaut que pour
les cas types, dont le modèle garde la rémunération totale :
le décrochage du salaire total des fonctionnaires en 2026 et 2027, que la même
note écrit, n'y est pas. Depuis l'étape 9 de l'action 147, elle porte aussi le
décrochage déjà fait : le traitement indiciaire moyen rapporté au revenu moyen
d'activité, que la figure 1.14 du même rapport publie de 2019 à 2024, le
premier point reconduit avant lui, quand le point
d'indice a perdu le tiers de sa valeur sur le salaire moyen depuis 2000 : le
décrochage d'avant 2019 manque encore. La même étape fait suivre aux caisses
de la fonction publique, au-delà de la dernière enquête de la DREES, les
retraités que le COR leur projette, rapportés à ceux de tous les régimes
(`EffectifsRetraites.CAISSES_PROJETEES`) : reconduire la répartition de 2024
faisait croître les retraités de l'État comme ceux de tous les régimes, quand
le COR les tient stables. La Cnav du modèle suit celle du COR ; la fonction publique
de l'État du modèle recule de
<!--chiffre:mesure(decomposition?facteur=pension_relative&groupe=fpe&de=2025&a=2070)-->−36,4<!--/--> %,
moins que la sienne, et l'Agirc-Arrco de
<!--chiffre:mesure(decomposition?facteur=pension_relative&groupe=agirc_arrco&de=2025&a=2070)-->−31,7<!--/--> %.
Ce qui reste de ce dernier écart tient aux têtes : le COR fait croître les
retraités de l'Agirc-Arrco plus vite que ceux de la Cnav, ce que la grille,
dont chaque carrière du privé a les deux, ne peut pas faire. La dépense des
complémentaires, elle, suit celle du COR depuis l'étape 10 de l'action 147 :
la page Coût y compte la cotisation et les points de l'Agirc-Arrco au taux
moyen des entreprises, comme les cas types du COR, quand les fiches portent le
taux minimal de l'accord, que le taux moyen dépasse d'un tiers sur la tranche 1
et des trois quarts sur la tranche B avant 1994
(`regimes/taux_moyens_agirc_arrco.csv`, de TRAJECTOiRE). Le simulateur
individuel garde le taux minimal, le seul que la caisse oppose à toute
entreprise ; le choix reste au propriétaire (registre des modèles, 138.13).

**Les carrières que la grille ne connaît pas (action 147, étape 11).** La
grille sert à chaque retraité qu'elle compte la pension d'une carrière
française complète, commencée au même âge à chaque génération. Deux
corrections, sous les mêmes conventions de projection, en rapprochent la page
du COR. *Les arrivées tardives.* La pyramide de l'INSEE compte des résidents,
et une génération y gagne, après ses études, des personnes arrivées en France
adultes, à la carrière française courte : le COR attribue à « l'arrivée de
nombreux retraités issus du solde migratoire et dont la pension serait plus
faible » une part du recul de sa pension moyenne (rapport de juin 2026,
partie 2, chapitre 1). Le classeur de l'INSEE que lit déjà la pyramide en
donne la mesure, génération par génération — sa population au 1er janvier
suivant, moins celle de l'année, plus ses décès de l'année, observée jusqu'en
2022, selon l'hypothèse de solde migratoire ensuite —, et
`macro/arrivees_tardives.csv` en tire ce qui manque à la pension d'une
génération, chaque arrivée travaillant en France la part de carrière que son
âge lui laisse : <!--chiffre:cellule(data/reference/macro/arrivees_tardives.csv:valeur*100?generation=1950&mesure=manque)-->3,2<!--/--> % pour la génération 1950,
<!--chiffre:cellule(data/reference/macro/arrivees_tardives.csv:valeur*100?generation=2000&mesure=manque)-->5,6<!--/--> % pour celle de 2000. La masse de chaque génération en est
multipliée, dans tous les systèmes, et non ses têtes (`Pensionne.completude`).
C'est une borne basse : la pension y est proportionnelle aux années — l'EIR de
2020 donne aux retraités nés à l'étranger une pension plus courte que leur
durée —, et le solde est net des départs. *L'entrée tardive des
fonctionnaires.* « Les fonctionnaires entrent dans la vie active en moyenne un
à trois ans avant d'entrer dans le régime de la FPE » (annexe méthodologique,
d'après l'EIC 2013), et la durée retenue pour la proratisation baisse
d'environ six ans d'ici la génération 2000 (même rapport, note 69) : le
fonctionnaire sédentaire commence sa carrière contractuel, deux ans pour la
génération 1962, huit pour la génération 2000, et sa pension se partage entre
l'État, le régime général et l'Ircantec, au même âge de départ
(`entree_fonction_publique` de `macro/hypotheses_projection.yaml`). Ce que ces
deux corrections ne portaient pas : les carrières incomplètes des natifs, entrés
plus tard dans la vie active sous une durée requise qui s'allonge. Portées à
la masse, elles faisaient passer la trajectoire propre nettement sous celle du
COR au milieu de la période, où la grille servait au privé une dépense sous la
sienne. Elles attendaient ce qui faisait ce défaut-là (feuille de route,
action 147, étape 11). Ce n'était pas le salaire moyen du modèle (étape 12) :
celui des cas types du COR est un revenu par tête, non-salariés compris, qui
croît moins vite depuis 2000 ; en rendre la croissance aux salaires anciens
creuserait l'écart au lieu de le combler, le stock des retraités d'aujourd'hui
en profitant plus que les départs à venir.

**Les régimes qui se ferment (action 147, étape 13).** C'était la
composition. Au-delà de la dernière enquête de la DREES, chaque caisse
gardait sa part des retraités de 2024, hormis celles de la fonction publique :
les exploitants agricoles, dont le COR divise les retraités par deux d'ici
2050, la SNCF, fermée aux recrutements depuis 2020, et les IEG, depuis
septembre 2023, gardaient la leur jusqu'en 2070, et les poids, normalisés, en
privaient le salariat privé. Ces trois caisses suivent désormais, comme
celles de la fonction publique, les retraités que le COR leur projette, et ce
qu'elles perdent, les autres caisses de la grille se le partagent au prorata
de leur effectif de 2024 (`EffectifsRetraites.CAISSES_PROJETEES`,
`CAISSES_DE_LA_GRILLE`) : LURA suit le COR à deux points près jusqu'en 2060, et
les non-salariés, qui doublaient sa dépense, ne s'en écartent plus que d'un
dixième au plus. Pas la Cnav, l'Ircantec, le RCI ni la CNAVPL, dont le COR
multiplie les retraités plus vite que les personnes, à mesure que les
polypensionnés se multiplient. La même étape compare la dépense de chaque
groupe réversion comprise des deux côtés : le modèle n'en comptait que les
droits directs, quand la réversion recule dans la dépense du COR, ce qui lui
prêtait deux points de plus en 2050. Il reste aux complémentaires quelques
points de dépense sous le COR au milieu de la période : les polypensionnés,
qu'une grille de carrières à un seul régime ne représente pas — le
fonctionnaire ou l'indépendant passé par le privé, le contractuel de la
fonction publique, dont le COR fait croître les retraités de l'Ircantec bien
plus vite que les personnes —, quand la complémentaire des libéraux croît,
elle, plus vite que la sienne. La grille par pas de cinq générations, enfin,
place mal les changements d'âge de la réforme de 2023, et les années de
l'ancrage et du calage en font partie : une grille annuelle, qui a ses propres
creux, ne déplace l'écart que d'un point et demi en 2050, pour quatre fois
plus de calcul ; la grille reste à cinq ans.

**Les carrières incomplètes des natifs (action 147, étape 14).** La grille
fait partir chacune de ses carrières au taux plein, avec la durée requise de
sa génération. Les retraités d'une génération résidant en France en ont
validé, en moyenne, ce que le COR publie, femmes et hommes (figure 3.22 du
rapport de juin 2026, l'EIR de 2020 pour les générations nées jusqu'en 1953,
TRAJECTOiRE au-delà ; `macro/duree_assurance_generations.csv`) : la
complétude de chaque génération est désormais cette durée, rapportée à sa
durée requise, et pèse ses masses, non ses têtes (`CarrieresIncompletes`).
Elle contient les arrivées tardives de l'étape 11 ; le reste est la part des
natifs, dont le profil est net — les femmes nées vers 1940, aux carrières
courtes, touchent moins que la grille, les générations de 1950 à 1965 un peu
plus, leurs durées dépassant la durée requise, et celles nées après 1975 de
moins en moins, entrées plus tard dans la vie active sous une durée requise
qui s'allonge. La figure 3.2 du même rapport, qui compte aussi les retraités
résidant à l'étranger, donne le même profil, et les mêmes résultats à trois
dixièmes près. C'est une borne, la pension y étant proportionnelle à la
durée : la décote coûte davantage, la complémentaire juste autant. Elle ôte au
modèle ce qu'il avait de trop à l'horizon ; au milieu de la période, où les
générations aux carrières longues de l'après-guerre cèdent la place, elle
l'abaisse d'un point, et le privé y reste sous le COR — les complémentaires
surtout, les polypensionnés manquant à la grille. Le passé, où vivaient les
générations aux carrières les plus courtes, en recule, et la reconstitution
avec lui.

**La fourchette, tant que l'écart dure (action 147, étape 3).** La page ne
prend plus au modèle la dépense du système actuel, mais elle lui prend
toujours le RAPPORT de masses qui en tire les autres systèmes, et ce rapport
porte l'écart. Deux lectures l'encadrent. Si l'écart est PARTAGÉ par toutes
les règles — une grille qui compte mal qui part, quand et avec quelle carrière
se trompe de la même façon sous chacune —, le rapport est juste : ce sont les
chiffres de la page. S'il est PROPRE au système actuel — une règle du droit en
vigueur que la grille sert autrement que le COR —, la masse des systèmes
notionnels est juste et seule celle du système actuel est fausse : le rapport
doit être multiplié par la dérive de l'année, la croissance de la masse du
modèle rapportée à celle de la dépense du COR depuis la première année
projetée, <!--chiffre:mesure(derive_cor?annee=2050)-->−2<!--/--> % en 2050, presque rien à l'horizon
(`rapport_derive`, `Cout.solde_derive`, `Cout.dette_derive`). La proposition coûte alors <!--chiffre:mesure(part_pib?scenario=6&annee=2070&borne=haute)-->8,2<!--/--> % du PIB en 2070
(<!--chiffre:mesure(part_pib?scenario=6&annee=2070)-->8,2<!--/--> dans la première lecture), son solde moyen 2026-2070 est de <!--chiffre:mesure(solde_moyen?scenario=6&borne=haute)-->−0,84<!--/--> %
(<!--chiffre:mesure(solde_moyen?scenario=6)-->−0,94<!--/-->), son coefficient d'équilibre de <!--chiffre:mesure(coefficient?scenario=6&borne=haute)-->1,00<!--/--> (<!--chiffre:mesure(coefficient?scenario=6)-->1,00<!--/-->), et sa dette en
2070 de <!--chiffre:mesure(dette?scenario=6&borne=haute)-->56<!--/--> % du PIB (<!--chiffre:mesure(dette?scenario=6)-->62<!--/-->). Le système actuel ne bouge dans aucune
des deux lectures, ni la garantie vieillesse, lue sur la distribution des
pensions. La page Coût donne les deux lectures côte à côte. La seconde a été la
borne haute de la proposition jusqu'à l'étape 11 de l'action 147 ; la dérive
passant sous un de 2031 à l'horizon, elle l'allège désormais, et la fourchette
est étroite.

Ce que le dépôt sait de la part qui revient à chaque lecture est mince, et il
faut le dire. Le COR attribue la baisse de sa pension moyenne relative à des
règles du droit en vigueur — l'indexation des droits sur les prix, la baisse
du rendement de l'Agirc-Arrco, la part des primes des fonctionnaires, une durée
requise qui s'allonge pour des carrières incomplètes —, qui tirent vers la
seconde lecture, et à des effets de population — l'âge des retraités, des
immigrés aux carrières françaises courtes —, qui tirent vers la première
(rapport de juin 2026, partie 2, chapitre 1). La page suit désormais ses
conventions de l'Agirc-Arrco et des primes, l'entrée tardive des
fonctionnaires, et porte à la masse les carrières courtes des arrivées
tardives : ce qui reste de l'écart est petit, et de signe changeant.
