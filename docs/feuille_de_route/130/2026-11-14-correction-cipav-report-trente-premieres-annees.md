# Correction de la ligne 14 de la file : la Cipav ne majore pour report que les points des trente premières années

Quatorzième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu aux index JORF et LEGI** (à jour du 11 novembre 2026). Décret
n° 79-262, article 5-2, II, en vigueur le 1er juillet 2026 (LEGIARTI000054168515) :
« L'affilié qui a atteint l'âge prévu au a du 1° de l'article 5-1 et comptant un minimum
de trente années d'affiliation à la CIPAV, peut différer la date d'entrée en jouissance
de la pension de retraite complémentaire de 1 à 5 ans. Le compte de points qui est alors
établi est majoré de 5% par année entière de prorogation. Cette majoration s'applique
uniquement aux points acquis au titre des trente premières années de cotisation à la
CIPAV. Pour la détermination des trente années de cotisation, les années au titre
desquelles l'affilié a obtenu une exonération ou une réduction de cotisation sont prises
en compte. » Arrêté du 20 mars 2023, annexe, 17° (JORFARTI000047334800), qui montre le
même alinéa dans les statuts d'avant (article 3.15) ; la fiche `surcote_par_age_seul` le
relit par différence depuis 2008. Le texte tranche ce que la ligne dit : seuls ces
points se majorent. Il ne tranche pas le décompte d'une première année incomplète : le
propriétaire a retenu le plus favorable à l'affilié.

**Un fait neuf, lu ce jour.** Décret n° 79-262, article 1er, rédaction de 1979
(LEGIARTI000006767470) : « A compter du 1er janvier 1979, il est institué un régime
d'assurance vieillesse complémentaire obligatoire ». L'année 1979 est donc entière pour
l'affilié d'avant 1979. Les fiches chiffraient pour lui trois décomptes (de 1979 à 2008,
de 1980 à 2009, de 1979 à 2009), par analogie avec la première année partielle ; seul le
premier compte trente années. Le montant de la ligne, 152,05 €, supposait le troisième :
au cas posé de 2016, la correction retire 175,07 €.

**L'erreur.** Depuis 2013, le coefficient de majoration multipliait toute la pension de
la complémentaire de la Cipav.

**Le décompte servi.** Trente ans de date à date depuis la première cotisation au
régime, l'année où ils s'achèvent prise en entier : les trente premières années civiles
cotisées, et une de plus quand la première est partielle (la somme des fractions d'année
des lignes de la carrière qui cotisent au régime cette année-là est inférieure à un).
Une carrière qui n'a pas plus d'années garde son coefficient entier.

**Le test d'abord** (`tests/test_sections_liberales.py`,
`test_la_cipav_ne_majore_que_les_trente_premieres_annees_dans_les_deux_moteurs`), vu
rouge sur le premier cas (12 625,51 € servis pour 12 450,45 € attendus). Trois cas posés
à la main, libérale de la Cipav au double du salaire moyen depuis 22 ans, un an entier
de report, les cotisations revalorisées année par année étant celles des notes
`2026-11-06-e10-decret-2026-418.md` et `2026-11-06-e11-surcote-par-age-seul.md` :

| née le | pension au | années majorées | calcul | servi avant | servi depuis | de moins |
|---|---|---|---|---|---|---|
| 10 mars 1949 | 1er janvier 2016 | 1979 à 2008 | 193 940,3125 × 0,062 + 0,0031 × 137 466,6071 | 12 625,51 € | 12 450,45 € | 175,07 € |
| 10 mars 1957 | 1er janvier 2026 | 1979 à 2009 | 354 057,8613 × 0,061 + 0,00305 × 177 676,4629 | 22 677,41 € | 22 139,44 € | 537,96 € |
| 10 mars 1959 | 1er juillet 2027 | 1981 à 2011 | 374 715,4414 × 0,061 + 0,00305 × 194 651,6538 | 24 000,52 € | 23 451,33 € | 549,19 € |

Un contrôle : cotisante depuis le 10 mars 1985, pension au 1er janvier 2016, trente et
une années civiles dont la première partielle, toutes majorées, 1,0500 comme avant. Le
test passe par `servi_et_refait` : le moteur Python refait chaque cas au bit près.

**Le code.** Un paramètre de période, `surcote_premieres_annees: 30`, aux sept périodes
de `cipav_complementaire.yaml` qui majorent (depuis 2013), décrit au schéma, chargé par
`donnees/regimes.py`, écrit au paquet par `construire_donnees.py`. Dans
`liquider_chaque_regime`, des deux côtés : `premieres_annees_majorees` rend les
cotisations revalorisées des années majorées, et le coefficient devient 1 + (coefficient
− 1) × leur part dans le montant ; le coefficient affiché est celui de la pension
entière, et le détail nomme les années (« la majoration portant sur les seules
cotisations des 30 premières années, de 1979 à 2008 »).

**Ce que la correction déplace.** Aucun des 933 témoins de simulation ; un rendu de
page, `simuler_notionnel_plus_genereux` (libéral né en 1975, parti à 70 ans : 8 000 €
par an devenus 7 503 €). Suite rapide, tests de la zone et tests du site verts.

**Les fiches.** `surcote_par_age_seul` : l'erreur passe à l'histoire (`effet`,
`sources.a_relire`), et son écart devient le point que le texte ne tranche pas, servi au
plus favorable — sous les deux autres décomptes d'une première année partielle, le
modèle majore encore trop, de 4,87 € à 30,19 € par an aux cas posés. `decret_2026_418_liberaux`,
les notes de `cipav_complementaire.yaml` et `docs/limites/3-systeme-actuel.md` disent la
règle servie.

**Ce qui reste.** Le modèle ne compte ni les années cotisées avant 1979 au régime auquel
celui de 1979 se substitue (non lu), ni une année d'exonération sans cotisation. La
Cipav de 2008 à 2012, où le modèle ne majore rien, est la ligne 15 : elle reprendra ce
paramètre. Le bloc « Reprise » de l'action 130 n'est pas récrit : la file dit où elle
en est (règle des deux files de front).
