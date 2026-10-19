# L'année du décès du chef d'exploitation, cotisée au prorata depuis 2009

Le reste que les notes du 18 octobre
(`2026-10-18-ce-que-l-exploitant-verse-au-compte.md`,
`2026-10-18-statut-au-1er-janvier.md`) avaient trouvé en chemin : l'année du
décès du chef d'exploitation, que le modèle comptait entière, comme celle où
il cesse.

**La règle, lue.** Code rural, L. 731-10-1 (LEGIARTI000019950453), créé par
l'article 18 de la loi n° 2008-1330 (JORFARTI000019943089), qui ne date pas son
application, en vigueur le 19 décembre 2008 : « En cas de décès du chef
d'exploitation ou d'entreprise agricole, les cotisations mentionnées au premier
alinéa dues au titre de l'année au cours de laquelle est survenu le décès sont
calculées au prorata de la fraction de l'année considérée comprise entre le
1er janvier et la date du décès. Toutefois, le conjoint survivant peut opter
pour le calcul des cotisations d'assurance vieillesse prévu au premier
alinéa. » D. 731-57-1 (article 1er du décret n° 2009-1236,
JORFARTI000021158799) : la caisse informe le conjoint de l'option, à demander
« dans les douze mois qui suivent le décès ». La pratique : la réponse à la
question écrite n° 10883 (JO du 3 février 2026, page 928), « en cas de décès du
chef d'exploitation ou d'entreprise agricole responsable du paiement d'une ou
de plusieurs cotisations, celles-ci sont calculées au prorata de la durée
effective d'activité, pour tenir compte de la situation des héritiers ou du
conjoint survivant » ; celle à la question n° 96453 (2016) laisse au conjoint
l'annualité des cotisations vieillesse « afin de préserver les avantages
prévus actuellement en matière de retraite ». Ni l'une ni l'autre, ni aucune
page de la MSA trouvée, ne disent les trimestres et les points d'une année au
prorata : la MSA de Corse n'affiche que le titre d'un article, « Le prorata des
cotisations en cas de décès du chef d'exploitation ».

**Ce qui est fait.** `Carriere._statuts_au_1er_janvier`
(`statutsAu1erJanvier`) : dans la carrière arrêtée au décès, que lit la
pension que le défunt « eût obtenue » (`Carriere.au_deces`), l'année de la
date d'effet ne se cotise plus entière quand le statut du 1er janvier est
celui du chef ; elle garde ses mois, comme celle de R. 731-83, et ses
trimestres, ses points et ce que le compte en reçoit sont ceux d'une année au
prorata. Depuis les cotisations de 2009
(`COTISATIONS_AU_PRORATA_DU_DECES_DEPUIS`) : un décès des treize derniers
jours de 2008 en cotise au moins 354 jours sur 366, et l'année entière en est
plus près que les neuf mois de la carrière arrêtée au 1er octobre. Le
collaborateur, dont le décès n'est pas celui du chef, garde l'année entière,
comme le défunt d'avant 2009. Un test, dans les deux moteurs
(`test_simulateur.py`,
`test_l_annee_du_deces_du_chef_d_exploitation_se_cotise_au_prorata`) : le chef
de 1990 à 12 000 € par an, mort le 15 août 2024, sa carrière arrêtée au
1er juillet, cotise six mois de 2024, et non douze, deux trimestres et non
quatre, 9,5 points de proportionnelle (les 19 du 2° de R. 732-71 pour ses
6 000 €, comptés pour six mois) et non 30, et garde les 133 de la RCO ; mort en
août 2005, il cotise l'année entière, comme le collaborateur mort en août 2024
(16 et 88 points). Les fiches taux_plein_et_proratisation,
retraite_proportionnelle_msa et assiette_minimale_agricole le disent.

**La classe.** L'annualité, et son exception au décès, ne sont que du régime
agricole : les autres régimes gardent déjà les mois de l'année du décès, le
plafond des indépendants se réduisant au prorata de leur affiliation
(R. 613-17). Le prorata court jusqu'au décès, la carrière arrêtée jusqu'au
premier jour du trimestre civil du décès (exposé de la Cnav, « Retraite de
l'assuré décédé »), pour tous les régimes : mort le 15 août, le chef cotise six
mois, et non sept et demi ; mort en mars, rien de l'année, comme avant.

**Ce qui bouge.** Rien dans les fichiers fabriqués : après `regenerer.py`,
aucun des 887 témoins de simulation ni des 79 rendus de pages ne bouge
(`resumer_temoins.py`), aucun témoin ne portant le décès d'un non-salarié
agricole, et les agrégats restent les mêmes. Le paquet du site, que le commit
de D. 634-5 avait laissé périmé, a été refait pour mesurer, sans être commité :
GitHub refait les fichiers.

**Restes, trouvés en chemin.** L'option du conjoint survivant, que le modèle
ne lit pas : la saisie pourrait la porter, à la session des pages. L'année du
décès qui porte deux statuts, chef au 1er janvier puis collaborateur : ses
deux lignes gardent leurs mois, quand le statut du 1er janvier devrait la
cotiser seul jusqu'au décès. La proportionnelle d'une année au prorata lit le
barème de R. 732-71, écrit pour une année, sur le revenu de ses mois : 19
points pour 6 000 €, comptés pour six mois, quand les 30 des 12 000 € de
l'année, comptés pour six mois, en feraient 15 ; de même à l'année de
R. 731-83.

**Ce qui attend le propriétaire.** La question déjà posée des années cotisées
au prorata (R. 731-83), dont l'année du décès est désormais : leurs trimestres
et leurs points, que la MSA seule peut dire. Et une convention : le modèle
applique le prorata, la règle de L. 731-10-1, et non l'option que le conjoint
survivant peut prendre pour l'année entière ; à garder, ou à renverser.
