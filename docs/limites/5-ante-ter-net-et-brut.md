# 5 ante ter. Le net et le brut : ce que la bascule suppose

Le simulateur se lit entièrement en brut ou entièrement en net, saisie comprise,
en brut par défaut. Quatre réserves, dont la première commande tout le reste.

**1. Le taux de CSG d'une pension suit le revenu fiscal du foyer, présumé
quand il n'est pas dit.** L'article L. 136-8 le fait dépendre du revenu fiscal de référence du
foyer, perçu l'avant-dernière année, et en tire quatre cas pour une part de
quotient familial (montants 2026, revalorisés chaque année sur les prix) :
exonéré jusqu'à <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=exonéré.revenu_fiscal_maximum)-->13 048<!--/--> €, <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux réduit.taux*100)-->3,80<!--/--> % jusqu'à <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux réduit.revenu_fiscal_maximum)-->17 057<!--/--> €, <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux médian.taux*100)-->6,60<!--/--> % sous <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux médian.revenu_fiscal_maximum)-->26 472<!--/--> €,
<!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.bareme_csg.libelle=taux plein.taux*100)-->8,30<!--/--> % dès ce seuil. Le simulateur lit ce revenu dans un champ facultatif ; sans lui,
il le présume fait des seules pensions du foyer — celle du système 1 et les
ressources du conjoint déclaré —, abattues de <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.abattement_pensions.taux*100)-->10<!--/--> %. Le foyer compte une part,
deux avec un conjoint. Au taux plein, la CSG fait <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.csg_taux_plein*100)-->8,30<!--/--> %, la CRDS
<!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.crds*100)-->0,50<!--/--> % et la CASA <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.casa*100)-->0,30<!--/--> %, soit **<!--chiffre:mesure(prelevement_pension)-->9,10<!--/--> %** ;
la CRDS suit la CSG hors de l'exonération, la CASA et la cotisation maladie
ne jouent qu'aux deux derniers taux, et l'allocataire de l'ASPA n'est prélevé
de rien. Une pension de <!--chiffre:illustration()-->660<!--/--> € par mois, seule ressource d'une personne
seule, n'est ainsi pas prélevée, comme le droit le veut.

Quatre choses restent approchées : une seule année de revenu, si bien que le
lissage par l'antépénultième année ne joue pas ; ni les demi-parts des
enfants à charge, des invalides ou des parents isolés ; les seuils de la
métropole partout ; et la majoration d'un quart de part, que la caisse
arrondit à l'euro (instruction de la DSS du 11 décembre 2025) et le dépôt
non, d'où un euro de revenu fiscal au seuil du taux réduit. Les cinq
systèmes notionnels gardent le taux de la
personne au système 1, et la page le dit sous la clé de lecture.

**2. La cotisation maladie des pensions est comptée au système 1, et les cinq
autres gardent le taux qui en résulte.** Trois ont survécu, réduites, à la
hausse de la CSG de 1998 : <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.maladie_complementaire.taux*100)-->1<!--/--> % sur ce que servent les complémentaires de
salariés (L. 131-2, 1° ; D. 242-8), et non sur la base ; <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.maladie_regimes_speciaux.serie=maladie_sncf_sous_plafond.taux*100)-->0,70<!--/--> % de la
pension de la SNCF sous un plafond, rien au-delà (décret n° 2007-1056, art. 7,
IV) ; <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.maladie_regimes_speciaux.serie=maladie_mines.taux*100)-->0,50<!--/--> % de celle des mines et de ses avantages accessoires, sans
plafond (décret n° 46-2769, art. 91). Toutes trois épargnent la majoration pour
enfants — le texte le dit des complémentaires et des mines (art. 139 et 141),
le dépôt le présume à la SNCF — et suivent la tranche de CSG du foyer
(D. 242-9 ; R. 711-15). Le plafond de la SNCF, fixé à <!--chiffre:tenu(test_le_plafond_de_la_sncf_est_celui_du_texte_revalorise)-->5 128<!--/--> € par trimestre
au 14 novembre 2010, est réduit de moitié pour une réversion et revalorisé
« dans les mêmes conditions que les pensions » (VII). La caisse ne publie pas
le plafond revalorisé : le dépôt le calcule, <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.maladie_regimes_speciaux.serie=maladie_sncf_sous_plafond.plafond_annuel)-->25 582<!--/--> € par an en <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.maladie_regimes_speciaux.serie=maladie_sncf_sous_plafond.annee)-->2026<!--/-->, et celui
de l'année suivante attend la revalorisation de son 1er janvier. D'une
revalorisation par tranches, comme celle de 2020, il retient la tranche d'une
pension mensuelle de la taille du plafond : une lecture qu'aucune source ne
confirme, le texte revalorisant un plafond, non la pension d'un assuré. Les
autres régimes dont la maladie est lue n'en prélèvent plus, hors la CAMIEG
(ci-dessous) ; celle des pensions de la SEITA, du port de Strasbourg, des
marins, des cultes, des assemblées et du Conseil économique, social et
environnemental n'est pas lue, ni aujourd'hui ni dans l'histoire, et le dépôt
n'y prélève rien. La cotisation des complémentaires laisse l'Ircec et l'Arrco
des cultes, à relire. Les scénarios notionnels n'ont qu'un compte, sans base ni
complémentaire : ils appliquent à la pension de chacun son taux du système 1.
C'est une hypothèse, que la page dit — la réforme ne change pas les
prélèvements —, et le net y garde les rapports du brut.

**Les années passées prennent la cotisation de leur date.** L'histoire des
prélèvements, que lisent les indicateurs de cycle de vie, la prend à ses textes,
lus au Journal officiel ou repris des barèmes de l'IPP, pour chaque régime de
base calculé : le régime général, la
fonction publique, les indépendants, les exploitants agricoles, les régimes
spéciaux placés sous le régime général pour la maladie — l'Opéra de Paris, la
Comédie-Française, les chemins de fer secondaires, qui ont leur propre taux
avant soixante ans —, les IEG, la SNCF, la RATP, la Banque de France, la CRPCEN
et les mines. Une série naît à son premier texte lu, et rien n'est prélevé
avant. Quatre conventions la simplifient : un taux par tranches, ou borné par
un plafond, est celui d'une pension sous le premier plafond, sauf à la SNCF
depuis 2010 ; le taux est plein, sans les exonérations des retraités non
imposables ni la réduction de l'exploitant soigné par un autre régime ; il
s'applique aux pensions dues à sa date, sauf quand le texte en dit une autre ;
un âge se compte au premier jour du mois. Les textes ne disent pas les taux que
les conseils de la SNCF, de la RATP et de la Banque de France fixaient avant
1991, où rien n'est donc prélevé, ni les plafonds de la SNCF de 1991 à 2010,
hors 1996. Aux mines, les taux d'avant 1998 épargnent la majoration pour
enfants, que le texte d'alors n'exceptait pas ; l'écart n'est pas mesuré.

**Restent hors du calcul** la cotisation supplémentaire du régime local
d'Alsace-Moselle, et la cotisation d'équilibre que le retraité des IEG qui
compte quinze ans de services paie, sur sa pension et sa réversion, au régime
complémentaire d'assurance maladie que gère la CAMIEG : deux et quart pour cent
depuis 2023 (décret n° 2020-1689 ; page « Prélèvements » de la CNIEG, lue le
5 octobre 2026). Ce n'est pas l'assurance maladie de base, mais un complément
que le statut national rend obligatoire (art. 23, § 8) : du droit, par décret,
quand la fiche de paie laisse la mutuelle d'entreprise d'un salarié, qui ne
l'est pas. Qui réside hors de France ne doit ni CSG, ni CRDS, ni CASA ; si la
France prend en charge ses soins, il doit une cotisation maladie sur la base du
régime général et sur la complémentaire, et la sienne à la SNCF et aux mines
(fiche `cotisation_maladie_des_non_residents`), mais aucune sur les majorations
pour enfants (L. 131-2, 1°) : ni sur celle du défunt qu'une réversion reprend,
ni sur celles dont le régime général majore la réversion du survivant, pour
trois enfants et pour enfant à charge. Ce qu'une révision ou la limite de cumul
retire à cette réversion, la carte de la réversion le nette encore comme si la
part de la majoration pour trois enfants payait la cotisation : le modèle ne
l'en sépare pas. Ne sont lus ni les conventions bilatérales qui rendraient la
France seule compétente hors de l'Union, ni ce que les autres régimes
prélèvent sur sa pension.

**Le régime d'une pension suit l'entrée dans le statut.** Un statut fermé aux
nouveaux entrants — la SNCF, la RATP, la Banque de France, les IEG, la CRPCEN,
les mines — garde son régime, et la retenue de sa fiche de paie, à qui y est
entré avant la fermeture ; entré après, l'assuré relève du régime général et de
sa complémentaire, dont la pension paie le <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.maladie_complementaire.taux*100)-->1<!--/--> %. La carrière date l'entrée
dans le statut du début du premier métier qui l'exerce, ou, sur un relevé, de
la première année d'emploi qui le nomme. Le clerc de notaire et l'agent des IEG
recrutés avant le 1er septembre 2023 qui quittent le statut et y reviennent ne
gardent leur régime que si leur affiliation s'est maintenue (loi n° 2023-1250,
art. 15) : <!--chiffre:valeur(data/reference/legislation/affiliations.yaml:affiliations.agent_ieg.periodes.debut=1946.maintien)-->dix<!--/--> ans au plus après une suspension ou une rupture antérieure,
quelle qu'en soit la cause ; un mois ou un an après une rupture postérieure,
selon qu'elle vient du salarié ou de l'employeur, ou jusqu'à la reprise d'une
activité affiliée ailleurs, si elle vient avant ; pendant les congés que deux décrets énumèrent
(n° 2025-799 et 2025-761). Le modèle ne connaît la carrière qu'à l'année, et ne
voit ni le contrat ni le congé : la fiche `maintien_affiliation_crpcen_ieg` en
déclare les présomptions. Le départ se date de la fin de sa dernière année
d'emploi sous le statut, le retour de janvier : un départ et un retour qui ne
laissent entre eux aucune année civile entière ne rompent rien, et une année
entière dépasse le mois comme l'an. Une année d'interruption déclarée sous le
statut le suspend, sauf le chômage et la préretraite, qui supposent le contrat
rompu : l'inactivité, les études et le service sont présumés l'un des congés
des listes, quand un congé hors liste romprait l'affiliation. Une année passée
sous un autre statut rompt toujours : la mobilité de cinq ans au plus hors des
IEG et le congé de création d'entreprise, qui maintiennent l'affiliation pendant
que l'assuré travaille ailleurs, ne se voient pas. Le maintien de <!--chiffre:valeur(data/reference/legislation/affiliations.yaml:affiliations.agent_ieg.periodes.debut=1946.maintien)-->dix<!--/--> ans
se lit à la lettre, quoi qu'il s'y passe, et une rupture postérieure survenue
pendant une suspension antérieure, que le texte ne règle pas, ne le coupe pas.
Une pension prise de septembre à décembre 2023 suit la rédaction de 2024, sans
effet à l'année. L'effet des autres présomptions n'est pas mesuré : aucune
carrière des témoins ne revient au statut.

**Au propriétaire, quatre points**, que le dépôt laisse ouverts sans rien en
appliquer. *La CAMIEG* : la pension nette d'un retraité des IEG perd-elle sa
cotisation d'équilibre, comme celle d'un agent de la SNCF perd la sienne ?
*L'écrêtement du minimum de pension de la SNCF* (décret n° 2008-639, art. 15,
IV) : depuis le 22 octobre 2023, le texte borne le total des pensions de droit
direct au montant d'un décret de L. 17 du code des pensions civiles, qui n'a
jamais paru, « ou, si celui-ci est plus élevé, [au] montant du minimum » ;
faute du décret, le modèle n'écrête rien, quand l'autre lecture borne ce total
au minimum lui-même et réduit le minimum de qui touche une autre pension —
question à poser à la caisse. *L'ASPA de l'article 23* du même décret, qui porte
la réversion du survivant seul de cinquante-cinq à soixante-quatre ans au
montant de l'allocation de solidarité aux personnes âgées : la caisse la dit
« sous conditions de ressources », que ni elle ni le texte ne détaillent, et le
modèle ne la porte pas ; restent à choisir la lecture des ressources —
différentielle, comme l'allocation, ou le plancher entier sous le plafond, à
moins de la demander à la caisse — et la ligne qui la montrerait, qui ne dit
qu'un montant à sa date d'effet. *Des textes au fac-similé du Journal officiel*,
que l'index de la DILA ne garde qu'en notice, à lire depuis un poste : les
décrets annuels de la protection sociale des exploitants de 1980 à 1989 et de
1993, les arrêtés des mines du 27 octobre 1972 et du 30 juin 1987, la
cotisation des chemins de fer secondaires de 1952 à 1954, la réduction du taux
maladie du décret n° 67-803 de 1968 à 1977, les barèmes A du décret n° 82-1105
de 1988 à 1991 et les décrets de 1987 sur la valeur du point, qui diraient le
seuil de la contribution de solidarité ; la liste entière est dans les notes de
l'étape 9 de l'action 138.

**3. La rente du pilier capitalisé suit le barème des pensions**, et c'est une
convention : le dépôt la traite en rente viagère à titre GRATUIT, ce qu'elle est
quand la cotisation qui l'a constituée a été prélevée à la source et déduite —
le cas d'une cotisation obligatoire. Une rente à titre onéreux relèverait des
prélèvements sur revenus du patrimoine, à <!--chiffre:illustration()-->17,2<!--/--> % sur une fraction du montant qui
dépend de l'âge. La proposition ne tranche pas.

**3 bis. Le taux de remplacement suit le mode, et il MONTE en net.** Le modèle
le calcule brut sur brut. En mode net, le site le convertit — pension nette
rapportée au dernier revenu net —, sans quoi il serait le seul chiffre de la
page à parler l'autre langue. Le taux net dépasse alors le taux brut de
plusieurs points. Ce n'est pas
un artefact, c'est un fait du système français — une pension est prélevée de
<!--chiffre:mesure(prelevement_pension)-->9,1<!--/--> %, un salaire d'une vingtaine de points — et il est rarement montré. La
conversion emprunte le rapport net/brut de la DERNIÈRE fiche de paie de la
carrière, celle de l'année du départ, qui est l'année du dénominateur ; pour un
statut sans fiche de paie, le taux reste brut faute de pouvoir le netter
honnêtement.

**4. Ce qui reste brut, et le restera.** Un CAPITAL notionnel et une ASSIETTE de
cotisation n'ont pas de net : on ne « nette » pas un capital. Les tableaux de
détail — décomposition par régime, capital, cotisations versées, contribution de
l'employeur — restent donc en brut dans les deux modes, et c'est leur seule
lecture possible. La bascule ne gouverne que ce qu'on TOUCHE : le salaire et la
pension.

**Et un mot sur la saisie.** En mode net, le nombre tapé est un net mensuel que
le modèle convertit en brut en résolvant la fiche de paie du statut — ce n'est
pas une estimation, c'est l'inverse exact du calcul qui produit le net. Chaque
ligne remonte par la fiche de sa dernière année, sous l'entrée dans le statut
et les retours que la réserve 2 décrit, avec deux approximations. Sur un relevé,
la saisie ne voit pas le retour que seule la projection jusqu'au départ ferait,
après une interruption déclarée au-delà de sa dernière année : l'activité après
le départ remonte alors par la fiche d'avant. Une ligne qu'une interruption
déclarée coupe d'un retour remonte tout entière par la fiche de sa dernière
année : une ligne n'a qu'un revenu. Les
statuts que le modèle ne sait pas décrire — exploitant agricole, élu,
collectivités d'outre-mer — font exception : leur montant est lu tel quel, et le
formulaire l'affiche plutôt que de le taire.

**Et le format de l'estimation officielle.** Le brut est le défaut depuis le
4 octobre 2026 : c'est la langue de « Mon estimation retraite », celle des
chiffres que chacun connaît déjà. Sous les quatre montants, la page montre le
système 1 comme cette estimation le chiffre — le brut de chaque étage aux âges
de sa synthèse, au plus tôt, au taux plein et au taux plein automatique, le net
en second — et l'écart au total que le lecteur recopie de la sienne. Trois
réserves. Le net y est celui de la bascule, avec les réserves 1 et 2 : le net
aux prélèvements officiels est l'étape 2 de l'action 138. Les revenus à venir
suivent le salaire moyen du modèle, quand l'estimation officielle leur prête
« une évolution régulière », un peu plus rapide (action 142, étape 2) : à
carrière égale, une part de l'écart en vient. Et les âges sont ceux que le
droit oppose à la carrière SAISIE : une carrière reconstituée par ses métiers
n'a pas tout à fait les trimestres de la vraie, et un relevé déposé se
prolonge jusqu'au départ à partir du revenu de sa dernière année (§ 5, « Les
carrières réelles »), quand
l'estimation officielle part de celui qu'elle prête à la situation actuelle.
Le minimum vieillesse n'y entre pas, que l'estimation ne compte pas non plus.
