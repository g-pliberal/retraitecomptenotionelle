# La complémentaire de la Cipav se compte en points depuis 1979

Le 20 novembre 2026, sur le constat de la relecture des régimes du même jour
(rang 2, les complémentaires des libéraux), après la CARMF, et selon la règle
du propriétaire (« on corrige tout ce qui est faux »).

**Lu.** Le décret n° 79-262, qui tient lieu de règlement. Article 5-2
(décret n° 2026-418, article 20, JORFARTI000054153655) : « Le montant de la
pension est égal au produit du nombre de points acquis […] par la valeur de
service du point ». Article 2, rédaction par rédaction : la classe 1 porte
attribution de quatre points et la classe 10 de quarante jusqu'en 2012
(LEGIARTI000006767473), la classe A de 36 points de 2013 à 2022
(LEGIARTI000026892951), puis la cotisation divisée par le coût d'acquisition
du point (LEGIARTI000054168526). Le décret n° 2012-1522
(JORFTEXT000026863128). Les fiches pratiques de la caisse de 2018, 2024 et
2026.

**Le moteur** portait chaque cotisation aux prix de l'année du départ et
appliquait au tout le rendement de cette seule année, 6,10 %. La classe 1 a
coûté 311 € en 1984 et 1 156 € en 2012 pour les mêmes quarante points
d'aujourd'hui : une année de 1984 servie en 2026 valait 42,65 € au moteur,
115,60 € au texte.

**Corrigé.** `scripts/fetch/cipav_points.py` saisit le prix du point de
chaque année — la cotisation de la classe de référence, lue dans
`classes_cotisation_epoques.yaml`, divisée par quarante jusqu'en 2012 et par
36 ensuite, puis le coût d'acquisition — et la valeur de service depuis 2011 ;
`verifier_donnees.py` les verse dans `valeurs_point.csv` par deux
certifications, `moyenne` pour ce qu'un texte ou la caisse donne, `estimee`
pour le reste. Une ligne du moteur change : la majoration du report, que la
Cipav limite aux trente premières années, mesurait sa part sur les
cotisations servies au rendement ; elle la mesure aussi sur les points
(`premieresAnneesMajorees`, `liquider.js`).

**Ce qui bouge.** Trois années en classe 1 puis A (2000, 2012, 2014), prises
à 67 ans en 2026 : (40 + 40 + 36) × 2,89 € = 335,24 €, contre 230,29 €. Né en
1959, libéral de 1984 à janvier 2026 au revenu moyen, parti à 67 ans :
6 265,98 € deviennent 9 416,95 € (3 258,46 points × 2,89 €). Dix-huit
témoins de simulation bougent, de + 2,99 % (`micro_entrepreneur_cipav`) à
+ 28,16 % (`statut_profession_liberale_1945`) de pension totale, aucun à la
baisse. Les deux tests du report sont reposés à la main, en points, sur un
libéral toujours dans la classe la plus haute.

**Le libéral type du coût, ramené dans le même envoi.** La grille du coût
n'a qu'un libéral, servi par la Cipav. À 2,5 fois le salaire moyen il cotisait
dans la classe la plus haute, et la correction le portait à 3 750 € par mois
en 2024, 1,16 fois les carrières complètes du COR (3 220 €) : il passe à 1,5
salaire moyen, 2 302 €, 0,715 fois (`castypes.py` ; mesures du fil du coût,
`2026-11-20-liberal-type-du-cout.md` dans les fichiers du projet). Les deux
changements ne tiennent qu'ensemble : à 1,5 sans les points, il tombait à
0,49. Le contrôle de la garantie est remesuré : son facteur passe de 0,7365
à 0,7224, la garantie de 36,42 à 37,20 milliards d'euros courants de 2024,
le système actuel servant plus aux libéraux par euro cotisé. La Drees donne
1 369 € par mois aux régimes libéraux, carrières courtes comprises : le cas
type reste une carrière complète.

**Deux réserves, écrites dans la fiche.** La conversion de 2013 — les points
d'avant multipliés par dix, le point passé de 25,47 € à 2,60 € — et les
valeurs de service de 2011 à 2014 ne sont lues que chez deux tiers qui citent
la caisse (Neovia, Toutsurmesfinances) ; le décret de 2012 dit seulement la
réforme « sans impact pour les points attribués au titre des périodes
antérieures ». Et aucun exemple officiel ne part d'une carrière : la caisse
publie « 7 500 points × 2,63 = 19 725 € » et, pour une année, « 72,13 points »
pour 3 418,75 € en 2026, que le test du micro-entrepreneur rejoue.

**Reste.** La valeur de service d'avant 2011 : une pension prise avant cette
date lit celle de 2011 ramenée par les prix. Les bornes de revenu des classes
d'avant 2012, convention de la fiche. Le micro-entrepreneur d'avant 2023, à
qui le modèle donne des points au prorata de sa cotisation, quand l'article 2
attachait alors les points à la classe : non tranché. La minoration « par
année » de l'article 5-1, que le moteur compte par trimestre. Le versement
forfaitaire unique, la réversion, le taux plein avant l'âge légal des II à IV
de L. 643-3, non confrontés. Les huit autres complémentaires servies par un
rendement (note du projet, relecture des régimes, section 8).
