# Les écarts de R-E12 repris, et la Cipav de `surcote_par_age_seul` écrite en versions (E12)

File E12, le 6 novembre 2026 (action 130, vague 11, sur Opus), après E11 (50154a0) et
sa relecture R-E12 (2c2f7c6). Aucun taux ni aucune valeur servie ne change ; aucune
erreur n'est corrigée.

**Méthode.** Index de la DILA récupérés et mis à jour : JORF au 6 novembre 2026
(JORF_20261106-002608), LEGI au 5 novembre (LEGI_20261105-214938). Les moteurs : le cas
posé par `servi_et_refait` (`tests/outils_pont.py`), qui confronte le portage et le
moteur Python, et un espion posé hors du dépôt sur
`retraite_notionnelle.droit.acquerir.acquerir`, qui somme les cotisations revalorisées
de `cipav_complementaire` année par année ; les réglages de E11 (`profil` plat, `euros`
2026, `enfants` 0, `sexe` F, `salaire` 2, `debut` 22, `statut` `profession_liberale`),
`liquidation` 66 et `liquidation_mois` 9. Contrôle : le cas de 2012 de E11 redonne au
centime 157 922,1741 €, 135 298,4577 € de 1979 à 2008 et 1 533,6360 € en 1979.

## 1. La réserve de l'arrêté du 3 octobre 2006 (écart moyen de R-E12)

Relu en entier dans l'index (JORFARTI000002050100, Journal officiel du 13 octobre 2006) :
« sont approuvées les modifications apportées aux statuts […] (art. 2.7 et 2.21 de la
seconde partie « règlement intérieur », troisième partie « Régime de retraite
complémentaire », ainsi que les dispositions transitoires). L'arrêté du 21 mars 1979
portant approbation des statuts de la section professionnelle des architectes, agréés en
architecture, ingénieurs, techniciens, experts et conseils et relatif au régime
d'assurance vieillesse complémentaire est abrogé à compter du 1er janvier 2007, à
l'exception de l'article 16 et de l'article 17, alinéa 2, qui seront abrogés le
1er janvier 2008. » L'arrêté du 21 mars 1979 n'est pas dans l'index : « 21 mars 1979 »
y rend 106 documents, dont les décrets n° 79-262 et 79-263, aucun arrêté de statuts ;
« transitoires » avec « architectes » ou « cipav », de 2006 à 2009, ne rend que l'arrêté
de 2006. Les dispositions transitoires et les articles 16 et 17, alinéa 2, de 1979 sont
au seul Bulletin officiel : question 22.

Écrit dans `surcote_par_age_seul` (`sources.a_relire`, l'article de la Cipav récrit ;
une lecture ajoutée ; `effet`) et dans `decret_2026_418_liberaux` (`sources.a_relire`) :
l'article 3.15 vaut sûrement depuis le 1er janvier 2008 ; en 2007, un point non tranché.

**Le décompte des trente années, une lecture de plus.** R-E12 (1.3) nomme un quatrième
décompte, depuis l'affiliation à la caisse, et dit qu'il « ne retire rien » à l'« au
moins » de E11. C'est vrai de l'erreur de 2013 à 2022, où le modèle majore trop ; non de
celle de 2008 à 2012, où il ne majore rien : ce décompte réduit ce qu'il sert en moins.
Chiffré ci-dessous.

**De 2008 à 2012, erreur déclarée, sous une réserve.** Le cas de E11 : née le 10 mars
1945, libérale depuis mars 1967, pension au 1er janvier 2012, un an entier de report
(65 ans le 10 mars 2010). Le modèle sert 157 922,1741 × 0,062 = 9 791,17 €, sans
majoration. Relevé neuf : de 1979 à 1996, 69 492,8927 €. Depuis l'affiliation, les
trente années vont de 1967 à 1996 : 69 492,8927 × 0,003 = 208,4787 ; × 0,0001 = 6,9493 ;
0,0031 × 69 492,8927 = **215,43 €** par an servis en moins. Sous les trois décomptes de
la première année du régime, 419,43, 437,33 et 442,09 € (E11, R-E12). Au moins 215,43 €,
au moins 419,43 € sous les trois décomptes de la première année ; la réserve : les
dispositions transitoires de 2006, non lues, peuvent borner les points majorés.

**En 2007, point non tranché.** Cas neuf : née le 10 mars 1940, libérale depuis mars
1962, pension au 1er janvier 2007 (66 ans et 9 mois ; 65 ans le 10 mars 2005 : un an
entier). Servi dans les deux moteurs : 6 947,955483 € (« cotisations revalorisées
112,064 € × rendement 6.20% », sans coefficient). Relevés : de 1979 (1 410,1318 €) à
2006, 28 années, 112 063,7981 € ; de 1980 à 2006, 110 653,6663 € ; de 1979 à 1991,
43 931,5488 €. À la main : 112 063,7981 × 0,06 = 6 723,8279 ; × 0,002 = 224,1276 ;
6 947,9555 €. Lecture A, l'article 3.15 dès le 1er janvier 2007 : 112 063,7981 × 0,003 =
336,1914 ; × 0,0001 = 11,2064 ; **347,40 €** par an servis en moins (décomptes de 1979 à
2008 et de 1979 à 2009, qui prennent les 28 années) ; 110 653,6663 × 0,003 = 331,9610 ;
× 0,0001 = 11,0654 ; **343,03 €** (de 1980 à 2009) ; depuis l'affiliation, de 1962 à
1991 : 43 931,5488 × 0,003 = 131,7946 ; × 0,0001 = 4,3932 ; **136,19 €**. Lecture B, les
articles 16 et 17, alinéa 2, de 1979, ou les dispositions transitoires, règlent l'année
2007 : non lus ; s'ils ne majorent rien, le modèle sert juste, **0 €**.

L'erreur de 2013 à 2022 n'en bouge pas : depuis l'affiliation (1971 au cas de 2016), les
trente années s'arrêtent en 2000, l'écart grossit ; au moins 152,05 € par an.

## 2. Le test du décret garde sa table (mineur)

`test_la_table_du_decret_2026_418_garde_ses_32_documents` : la table porte les numéros
1 à 31 et « 18, fin » juste après 18, des identifiants distincts et croissants, et seuls
29 à 31 sans texte. `test_la_table_du_decret_2026_418_est_celle_de_l_index_jorf`, sauté
sans l'index : ses 32 documents « Article DECRET » du décret sont ceux de la table, la
fin de l'article 18 étiquetée « 8 » (relevé ce jour : 32 documents et le
JORFTEXT000054153355). Vus : la ligne de l'article 10 ôtée, les deux rouges ; rétablie,
verts.

## 3. La fiche, écrite en versions pour la Cipav

`surcote_par_age_seul` reçoit `domaine` (`decote_surcote`), `lit`, `ecrit`,
`dates_qui_decident` (`liquidation.date_effet`), six versions et quatre approximations,
la Cipav seule :

| version | bornes | statut | ce qu'elle dit | le modèle |
|---|---|---|---|---|
| `cipav_avant_2007` | jusqu'au 31 décembre 2006 | supposée | rien (statuts de 1979, Bulletin officiel) | rien |
| `cipav_2007` | 2007 | supposée | non tranché, lectures A et B | rien |
| `cipav_de_2008_a_2021` | 2008 à 2021 | supposée, haute | 5 % par année entière après 65 ans, 1 à 5 ans, 30 ans d'affiliation, points des 30 premières années | rien jusqu'en 2012 ; tous les points dès 2013 |
| `cipav_2022` | 2022 | lue | la même, de l'âge du taux plein | tous les points |
| `cipav_2023_a_juin_2026` | 2023 au 30 juin 2026 | lue | la même, les années exonérées comptées | tous les points |
| `cipav_depuis_juillet_2026` | depuis le 1er juillet 2026 | lue | la même, au décret n° 79-262, art. 5-2, II | tous les points |

Textes relus ce jour : décret n° 79-262, article 5 (LEGIARTI000006767479, 1979 à 2004 ;
LEGIARTI000006767480, 2004 au 1er juillet 2026), articles 5-1 (LEGIARTI000054168518) et
5-2, II (LEGIARTI000054168515) ; arrêté du 16 décembre 2021, 19° et article 2 ; arrêté du
20 mars 2023, 17° et article 2 ; leurs dates de publication à l'index. La version de 2008
à 2021 reste supposée : le texte n'est pas lu, mais reconstitué par différence. Le modèle
sert chaque élément de la règle (taux, pas annuel, cinq ans, 65 ans puis l'âge du taux
plein, 120 trimestres), sauf la restriction aux trente premières années, qu'il ne sait
pas porter, et les années 2007 à 2012. Les textes de la Cipav sortent de
`textes_a_rattacher`, cités par les versions ; le cliquet des rédactions sans statut
passe de 9306 à 9305 (`data/reference/textes/perimetre.yaml`).

`tests/test_carte.py` admettrait déjà la fiche (aucun manque, aucun écart) ; elle
n'entre pas à `LUES_AU_DROIT` : six de ses sept régimes ne sont pas écrits en versions.

## Tests

`tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` : 100 verts ; sous `PRESOMPTIONS_DECALEES=1`, 99 verts et
un sauté. Suite rapide : 4 589 verts et 9 sautés ; sous `PRESOMPTIONS_DECALEES=1`, 4 384
verts et 214 sautés. Aucun autre fichier de tests ne lit les fichiers touchés. Le paquet,
reconstruit : inchangé.

## Ce qui reste

- `surcote_par_age_seul`, les six autres régimes en versions, chaque rédaction lue à la
  source : la CARMF et l'ASV, la CARPIMKO, la CAVEC, la CAVP, la CPRN. Les versions sont
  globales (le partage ne se joue que sur `liquidation.date_effet`) : chaque date d'un
  régime coupe celles de la Cipav. Pistes relevées dans les périodes du modèle, non
  vérifiées à la source : la CARPIMKO ne majore qu'en 2016, quand l'arrêté du 31 juillet
  2015 paraît le 2 octobre 2015 sans date d'effet ; la CAVP, en 2012, pour un arrêté du
  23 juin 2011 ; la CARMF et l'ASV comptent de 62 ans dès le 1er janvier 2017, quand
  l'arrêté qui écrit « 62 ans » est du 22 mars 2017.
- Puis `cotisation_par_classes_liberales`.
- Au propriétaire : les erreurs de la Cipav (2008 à 2012, 2013 à 2022, depuis 2023), 2007
  non tranché, la question 22 (statuts de 1979, de 2006, et leurs dispositions
  transitoires), le décompte de l'article 3.6.
