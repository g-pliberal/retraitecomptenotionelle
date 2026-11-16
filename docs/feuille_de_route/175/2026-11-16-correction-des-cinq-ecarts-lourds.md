# Étape 6, à part : les cinq écarts lourds du récapitulatif des circulaires, vérifiés au texte ; quatre corrigés, un déclaré

Le récapitulatif des écarts des circulaires
(`2026-11-16-etape-6-circulaires-recapitulatif-des-ecarts.md`) classe cinq écarts
lourds à corriger d'abord. Le propriétaire a demandé de les corriger, par la même
méthode que la correction précédente (`2026-11-16-correction-carriere-longue-et-cumul-avant-2009.md`) :
chercher au texte primaire ce qui confirme ou infirme chaque écart, ne corriger que
ce qui est confirmé, vérifier pour quels régimes la règle vaut, mesurer, citer. Les
textes ont été lus dans l'index de la DILA à jour au 16 novembre 2026. La session a
tourné sur Opus, Fable n'étant pas disponible : le propriétaire a dit de continuer
ainsi. La note 0009 étant encore en essai, les fiches gardent leur forme.

## 1. Mayotte : les salaires d'avant septembre 2023 revalorisés de 10 %

**Confirmé.** Loi n° 2023-270, article 19, III (LEGIARTI000047447830) : « Les
salaires portés au compte avant le 1er septembre 2023 servant au calcul du salaire
annuel de base mentionné au deuxième alinéa de l'article 12 de l'ordonnance
n° 2002-411 [...] sont revalorisés à titre exceptionnel pour les pensions prenant
effet à compter du 1er septembre 2023 » ; décret n° 2023-966, article 2, III
(LEGIARTI000048237957) : « revalorisés de 10 % ». La circulaire Cnav n° 2024/5 (relue
en PDF le 16 novembre) garde l'écrêtement au plafond de la caisse après la
revalorisation et ne valide aucun trimestre de plus. **Régimes** : le régime mahorais
seul (article 12 de l'ordonnance), salariés et non-salariés.

**Le modèle, après.** `revalorisationExceptionnelleDeMayotte`
(`moteur/js/droit/liquider.js`, et son jumeau Python) multiplie par 1,1 le salaire
de chaque année d'avant 2023, avant l'écrêtement au plafond de la caisse, pour une
pension prenant effet depuis le 1er septembre 2023. **Approximation déclarée** dans
`mayotte_pension_de_base.yaml` : le modèle n'a que le salaire de l'année, et
revalorise celui de 2023 pour huit douzièmes ; l'exemple de la circulaire (2 350 € en
2023, écrêtés à 2 394 €) en sort le même.

**Effet.** Les trois témoins de Mayotte du scénario 1 qui bougent montent de 2,35 % à
5,79 % ; la salariée du test, à 8 000 € par an de 2010 à 2024 partie en 2025, voit son
salaire annuel moyen passer de 9 073 € à 9 797 €.

## 2. La réversion d'un assuré mort avant son départ : confirmé, non corrigé

**Confirmé.** Décret n° 45-0179, article 81 b, version du 30 décembre 1973
(LEGIARTI000006760626), puis R. 353-3, version du 21 décembre 1985 au 25 août 2004
(LEGIARTI000006749406) : « Dans le cas où l'assuré n'était pas titulaire d'une
pension de vieillesse ou d'une rente à la date de son décès, il est fait
application, pour déterminer le montant de la pension principale servant de base au
calcul de la pension de réversion des dispositions en vigueur à la date d'effet de
cette dernière pension. » Depuis le 25 août 2004, R. 353-3 renvoie aux règles des
assurés qui atteignent soixante ans l'année du décès, puis cinquante-sept ans depuis
le 3 juin 2011 (LEGIARTI000024113043) : ces deux époques sont déjà déclarées dans la
fiche `reversion`.

**Pourquoi la session ne l'a pas corrigé.** Le modèle liquide la pension que le défunt
« eût obtenue » au trimestre civil de son décès (`Carriere.arreteeAuDeces`,
`_pensionsEuesAuDeces` de l'échéancier), et compte toute la réversion aux montants de
l'année du décès, même quand l'âge requis reporte sa date d'effet (écart déjà déclaré).
Prendre les règles de la date d'effet demande de connaître cette date avant la
liquidation fictive, de liquider à cette date une carrière arrêtée au décès, sans
que l'âge plus élevé ne joue (la majoration d'ajournement d'avant 1983), et de
ramener la pension aux montants de l'année du décès : un remaniement de l'échéancier,
dans les deux moteurs, que la session n'a pas jugé sûr de mener ici. L'effet se
concentre sur les décès d'avant 1975 suivis d'une réversion plus tardive (le cas de la
note de 1974-1979 : − 14,7 %) ; entre 1975 et 2004, les règles qui changent entre le
décès et la réversion se lisent surtout à la génération, et l'écart y est faible. La
fiche `reversion` le déclare désormais, avec le texte et le cas.

## 3. Les exploitants agricoles de 1986 à 1989 : l'âge et la durée de la retraite forfaitaire

**Confirmé.** Article 1120-1 de l'ancien code rural, version du 8 janvier 1986
(LEGIARTI000006581005) : l'âge minimum « est fixé à à soixante-quatre ans à compter
du 1er janvier 1986, à soixante-trois ans à compter du 1er janvier 1987, à soixante-deux
ans à compter du 1er janvier 1988 et à soixante et un ans à compter du 1er janvier
1989 », soixante ans en 1990 ; les inaptes et les anciens combattants gardent soixante
ans (article 1120-2). Décret n° 80-808, article 1er, version du 14 mars 1986
(LEGIARTI000006769191) : la retraite forfaitaire entière pour « Trente-trois années et
demie, lorsque la retraite prend effet au cours de l'année 1986 », trente-quatre et
demie en 1987, trente-cinq et demie en 1988, trente-six et demie en 1989,
proportionnelle en deçà. La minoration s'annule toujours à trente-sept années et
demie tous régimes (article 1121). **Régimes** : les non-salariés agricoles seuls.

**Le modèle, après.** La période de 1986 à 1989 de `msa_non_salaries.yaml` devient
quatre périodes d'un an, chacune à son âge, 64 à 61 ans, et à sa durée de retraite
forfaitaire, 134 à 146 trimestres, par un champ neuf de la période,
`duree_proratisation_trimestres`, que lit `dureeProratisation` (et son jumeau) ; la
durée requise reste de 150 trimestres. **Approximation déclarée** dans la fiche : un
départ refusé lit l'âge minimum de l'année qu'il demande, non la première date où
l'assuré l'atteint (né en 1926, refusé à 60 ans en 1986, il lit 64 ans, quand un départ
à 62 ans en 1988 lui est ouvert ; le simulateur l'ouvre bien à 62 ans en 1988).

**Effet.** Aucun témoin de simulation ne part dans ces années ; le coût et les pages
qui l'agrègent bougent (paquet refait), les pages `cout` et `avantages` aussi. Un
exploitant né en 1926 qui demandait 60 ans en 1986 voit son départ refusé ; à 62 ans
en 1988 il l'obtient, comme au droit.

## 4. Le plafond de ressources de la réversion au SMIC de la date de la demande

**Confirmé, de juillet 1974 à juin 2004.** Décret n° 45-0179, article 81 a, version du
12 mars 1981 (LEGIARTI000006760629), puis R. 353-1, versions de 1985 et de 1990
(LEGIARTI000006749451, LEGIARTI000006749452) : le survivant « ne dispose pas, à la date
de la demande de pension de réversion, de ressources personnelles dépassant le montant
annuel du salaire minimum de croissance », « 2 080 fois » son taux horaire ; à défaut,
« à la date du décès ». Circulaire Cnav n° 2002/44 : 6,83 € × 2 080 à compter du
1er juillet 2002. Depuis juillet 2004, D. 353-1-1 (LEGIARTI000006736552) fixe le plafond
au SMIC « en vigueur au 1er janvier » : le modèle y était juste. Le récapitulatif
disait l'écart « jusqu'en 2009 » : il s'arrête en juin 2004. **Déjà déclaré** dans la
fiche `reversion`, comme la session de 2003 l'avait dit ; corrigé quand même, l'écart
étant sûr et la correction courte.

**Le modèle, après.** Pour une version qui examine la demande (`ressources_examinees`),
le plafond de chaque moment examiné, la demande ou le décès, est au SMIC en vigueur ce
mois-là (`smicHoraireEnVigueur`, `macro.js`, et son jumeau), quand ce mois tombe dans
l'année des montants ; au SMIC du 1er janvier sinon, faute de montants d'une autre
année. Toutes les fiches de réversion qui examinent la demande le suivent.

**Effet.** Aucun témoin ne bouge. La veuve du test, à 14 000 € par an, son mari mort
en août 2002 : sa réversion, refusée au plafond de janvier (13 873,60 €), est servie
sous celui d'août (14 206,40 €).

## 5. Le cumul des retraités anticipés d'avant le 1er juillet 2011

**Confirmé.** Loi n° 2010-1330, article 118, II (LEGIARTI000023024205) : ses articles
18 à 40, dont l'article 20 qui relève les âges de L. 351-1 et de L. 351-8, « sont
applicables aux pensions prenant effet à compter du 1er juillet 2011 ». L. 161-22
(LEGIARTI000022267321) ouvre le cumul intégral « A partir de l'âge prévu au 1° de
l'article L. 351-8 » ou de L. 351-1 avec la durée ; circulaires Cnav n° 2011/61 et
2012/27, point 33 : « Il convient de retenir les âges en vigueur à la date d'effet de
la retraite anticipée, c'est-à-dire 60 ans (âge légal) ou 65 ans ». **Régimes** :
L. 161-22 vaut pour le régime général, les salariés agricoles et les régimes spéciaux,
et L. 634-6 et L. 643-6 en reprennent les conditions ; L. 84 du code des pensions
renvoie aux mêmes âges pour le fonctionnaire, mais aucun texte lu ne dit ce que le
service des retraites de l'État faisait de ses retraités anticipés d'avant juillet
2011 : le fonctionnaire garde dans le modèle les âges de sa génération, comme à la
correction précédente.

**Le modèle, après.** Dans le calcul du cumul (`cumul.js`, `cumul.py`), une première
pension d'avant juillet 2011, sans pension de la fonction publique, cumule entièrement
à 60 ans avec la durée, à 65 ans sans elle.

**Effet.** Aucun témoin ne bouge. La retraitée du test, née en janvier 1953, partie en
carrière longue en février 2011, cumule entièrement dès sa reprise d'août 2013, et non
plus d'avril 2014 seulement.

## Ce qui reste

L'écart n° 2, à corriger par une étape à lui, qui remanie la liquidation fictive de
l'échéancier (voir plus haut). Ce que le service des retraites de l'État faisait du
cumul de ses retraités anticipés d'avant juillet 2011. La première date d'ouverture des
exploitants de 1986 à 1989, que le modèle n'affiche pas pour un départ refusé. Les
écarts moyens et étroits du récapitulatif.
