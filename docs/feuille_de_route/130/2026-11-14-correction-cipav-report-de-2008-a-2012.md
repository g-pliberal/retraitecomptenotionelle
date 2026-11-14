# Correction de la ligne 15 de la file : la Cipav majore le report depuis le 1er janvier 2008

Quinzième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026). Les statuts de 2006 de
la Cipav ne sont qu'au Bulletin officiel ; leur article 3.15 se relit par différence,
comme la fiche `surcote_par_age_seul` le fait (version `cipav_de_2008`). Arrêté du
3 octobre 2006 (JORFARTI000002050100) : l'arrêté de 1979 « est abrogé à compter du
1er janvier 2007, à l'exception de l'article 16 et de l'article 17, alinéa 2, qui seront
abrogés le 1er janvier 2008 ». Arrêté du 16 décembre 2021, annexe, 19°
(JORFARTI000044554134) : « Au premier alinéa de l'article 3.15, les mots : « âgé de
65 ans » sont remplacés ». Arrêté du 20 mars 2023, annexe, 17° (JORFARTI000047334800) :
« Au dernier alinéa, les mots : « , telles qu'elles sont définies à l'article 3.6 » sont
supprimés ». De 2006 à 2013, l'index ne rend aucun autre arrêté qui touche la troisième
partie des statuts (celui du 6 juillet 2012 porte sur l'invalidité-décès). Le texte
tranche ce que la ligne dit : depuis le 1er janvier 2008, 5 % par année entière de
report après 65 ans, d'un à cinq ans, avec trente années d'affiliation, sur les points
des trente premières années de cotisation.

**L'erreur.** Les périodes de 1979 à 2012 de `cipav_complementaire.yaml` portaient
`surcote_par_trimestre: null` : le modèle ne majorait rien avant 2013.

**Le test d'abord** (`tests/test_sections_liberales.py`,
`test_la_cipav_majore_le_report_depuis_2008_dans_les_deux_moteurs`), vu rouge
(9 791,17 € servis pour 10 210,60 € attendus). Libérale de la Cipav au double du
salaire moyen depuis 22 ans, un an entier de report, les cotisations revalorisées
étant celles de la note `2026-11-06-e11-surcote-par-age-seul.md` :

| née le | pension au | années au régime | calcul | servi avant | servi depuis |
|---|---|---|---|---|---|
| 10 mars 1945 | 1er janvier 2012 | 33, majorées de 1979 à 2008 | 157 922,1741 × 0,062 + 0,0031 × 135 298,4577 | 9 791,17 € | 10 210,60 € |
| 10 mars 1942 | 1er janvier 2009 | 30, toutes majorées | coefficient 1,05 | sans majoration | 1,0500 |
| 10 mars 1940 | 1er janvier 2007 | 28 | l'année 2007, hors de la file | sans majoration | sans majoration |

L'effet au cas posé : 419,43 € par an de plus. La ligne annonçait « au moins
215,43 € » : ce plancher comptait les trente années depuis l'entrée à la caisse, en
1967 ; la ligne 14 a lu que le régime est institué « A compter du 1er janvier 1979 »
(décret n° 79-262, article 1er) : 1979 y est une année entière, et les trente années
vont de 1979 à 2008, comme le modèle les compte depuis. Le test passe par `servi_et_refait` : le moteur Python refait chaque cas au bit
près.

**Le code : aucun.** La période de 2000 à 2012 du régime est coupée en 2008 ; celle de
2008 à 2012 porte les sept paramètres de la période de 2013 (`surcote_par_trimestre:
0.0125`, pas de quatre trimestres, vingt au plus, depuis 65 ans, cent vingt trimestres
au régime, `surcote_premieres_annees: 30`). Les deux moteurs la lisent au paquet.

**Ce que la correction déplace.** Aucun des 933 témoins de simulation ; un rendu de
page, `avantages`, où le compte des avantages que les fiches déclarent passe de 967 à
968 (une période de plus). Fabriqués refaits, que les tests lisent : le paquet, les
témoins, et la page `avantages/index.html` (`construire_pages.py`), que la suite rapide
réclamait.

**L'envoi.** Un rebasage à la main sur la ligne 22 de l'autre file, arrivée entre-temps :
seul le paquet `moteur/donnees.json` se chevauchait, refait par son script.

**Les fiches.** `surcote_par_age_seul` : l'erreur passe à l'histoire (`effet`,
`sources.a_relire`), et son approximation devient le point que le texte ne tranche
pas. `decret_2026_418_liberaux`, les notes de `cipav_complementaire.yaml` et
`docs/limites/3-systeme-actuel.md` disent la règle servie depuis 2008.

**Ce qui reste.** Les « trente années d'affiliation » : le modèle les compte au régime
complémentaire, depuis 1979, et ne majore pas une pension de 2008, qui n'en a que
vingt-neuf ; comptées depuis l'entrée à la caisse, elle le serait (née le 10 mars 1941,
pension au 1er janvier 2008 : 7 528,93 € servis, 376,45 € par an de plus sous cette
lecture). Les dispositions transitoires de 2006, non lues, peuvent borner les points
majorés. L'année 2007 et les statuts d'avant restent hors de la file. Deux tests de
`tests/test_donnees.py` étaient rouges avant cette correction, sans elle : l'inventaire
des régimes et `docs/regimes.md` ne suivaient pas une note de la CARCDSF que l'autre
file a récrite ; refaits par leurs scripts (`construire_inventaire.py`,
`construire_regimes_md.py`), dans un commit à part. Le bloc « Reprise » de l'action
130 n'est pas récrit : la file dit où elle en est.
