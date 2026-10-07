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

Trois choses restent approchées : une seule année de revenu, si bien que le
lissage par l'antépénultième année ne joue pas ; ni les demi-parts des
enfants à charge, des invalides ou des parents isolés ; les seuils de la
métropole partout. Les cinq systèmes notionnels gardent le taux de la
personne au système 1, et la page le dit sous la clé de lecture.

**2. La cotisation maladie de <!--chiffre:valeur(data/reference/legislation/prelevements_remuneration.yaml:pensions.maladie_complementaire.taux*100)-->1<!--/--> % sur la retraite complémentaire est comptée
au système 1, et les cinq autres gardent le taux qui en résulte.** Elle porte sur
ce que servent les complémentaires de salariés, majoration pour enfants exclue
(L. 131-2, 1° ; D. 242-8), et non sur la base. Les scénarios notionnels n'ont
qu'un compte, sans base ni complémentaire : ils appliquent à la pension de chacun
son taux du système 1. C'est une hypothèse, que la page dit — la réforme ne change
pas les prélèvements —, et le net y garde les rapports du brut. Restent hors du
calcul la cotisation supplémentaire du régime local d'Alsace-Moselle, et ce que les
régimes spéciaux, la fonction publique et les indépendants prélèvent par leurs
propres textes, qui ne sont pas lus — ainsi la cotisation de la CAMIEG, que le
retraité des IEG qui compte quinze ans de services paie sur sa pension et sa
réversion, au taux de deux et quart pour cent (page « Prélèvements » de la
CNIEG, lue le 5 octobre 2026). Qui réside hors de France ne doit ni CSG, ni
CRDS, ni CASA ; si la France prend en charge ses soins, il doit une cotisation
maladie sur la base du régime général et sur la complémentaire (fiche
`cotisation_maladie_des_non_residents`) ; les conventions bilatérales qui
rendraient la France seule compétente hors de l'Union ne sont pas lues.

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
pas une estimation, c'est l'inverse exact du calcul qui produit le net. Les
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
