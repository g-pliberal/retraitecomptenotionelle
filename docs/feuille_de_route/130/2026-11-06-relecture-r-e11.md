# Relecture de E10 (le décret n° 2026-418 lu au droit, trois erreurs neuves, les écarts de R-E10 repris)

File R-E11, le 6 novembre 2026 (action 130, vague 11, sur Opus) : relecture indépendante,
contre les sources, du commit 7801413 de la session E10 (`decret_2026_418_liberaux`,
`data/reference/textes/perimetre.yaml`, `tests/test_sections_liberales.py`, le bloc
« Reprise » de l'action 130 ; note `2026-11-06-e10-decret-2026-418.md`). Ni règle, ni
donnée, ni test n'est modifié.

**Méthode.** Les index de la DILA récupérés : JORF à jour du 3 novembre 2026 (incrément
20261103-002311, 518 291 documents), LEGI du 2 novembre (20261102-213929, 327 817).
Chaque texte rouvert par `dila_cherche.py --texte`, les articles de LEGI par `--num …
--titre … [--le]` ; les textes modificatifs cherchés par mots, titre et numéro, sans borne
atteinte. Les 28 passages que la fiche cite entre guillemets, contrôlés un à un : chacun
est mot pour mot dans le document JORF ou LEGI qu'elle nomme. Les pensions : servies par
le portage et refaites par le moteur Python (`servi_et_refait`), sous les deux jeux ; les
cotisations revalorisées année par année, relevées dans `Droits.cotisations` du moteur
Python par un espion posé sur `acquerir` pendant l'essai, sans rien écrire au dépôt
(deux entrées par an à la Cipav, sommées). Réglages de E10 : `profil` plat, `euros` 2026,
`enfants` 0, `sexe` F, `salaire` 2, les autres ceux de
`tests/test_complementaires_liberales_a_leur_age.py`. Sous `PRESOMPTIONS_DECALEES=1`, les
six pensions et toutes les cotisations de chaque année sont identiques au centime. Lus en
plus : les statuts de la Cipav « au 01/01/2023 » publiés par la caisse, que le dépôt cite
déjà (`surcote_par_age_seul.yaml`, ligne 391 ; le PDF lu le 6 novembre 2026, SHA-256
e5034d618178585fdae444ec690247ef83c7e94d7e9ca741682fb98562093790).

**Verdict.** Les trois erreurs neuves sont **confirmées** : texte, date d'effet, ce que
le modèle sert et chaque montant, refaits au centime ; la lecture contraire est intenable.
Les reprises (a), (c) et (d), la forme de la fiche, la classe A de la CAVEC et le cliquet
sont **conformes**. **Un écart moyen** : la règle de la Cipav d'avant le 1er juillet 2026,
laissée non tranchée (b), est tranchée par les statuts que la caisse publie, depuis le
1er janvier 2023 au moins ; l'erreur s'étend aux pensions de ces années, au moins
537,96 € par an au cas posé. **Trois écarts faibles** : le test ajouté ne tient pas ce que
son nom dit ; les déclarations de la CARMF taisent deux facultés (le rachat des trimestres
dispensés, la cotisation volontaire après 75 ans) ; le renvoi à la question 22 omet les
textes du décret d'avant 2026 qui en sont le point de départ. Un candidat neuf.

## 1. Les trois erreurs neuves

La date d'effet, pour les trois : décret n° 2026-418 du 29 mai 2026 (JORF du 31 mai 2026,
JORFTEXT000054153355), article 30 (JORFARTI000054153813) : « Le présent décret entre en
vigueur le 1 er juillet 2026. » ; LEGI le reprend sous chaque article qu'il écrit :
« Conformément à l'article 30 du décret n° 2026-418 du 29 mai 2026, ces dispositions,
dans leur rédaction issue dudit décret, entrent en vigueur le 1er juillet 2026. » Aucune
disposition transitoire ne vise ces articles. Les trois sont des règles de **cotisation**
(l'étape « acquérir ») qui ôtent les **points** (« ne donnent pas lieu à acquisition de
points » ; « la suppression … des droits correspondants ») : le modèle fait payer la
cotisation et crédite ses points ; ce que E10 chiffre, et que cette relecture refait, est
la pension servie de trop. Le versant cotisation (2027, à la CARMF : 0,118 ×
87 370,5656 = 10 309,7267 € payés de trop l'année même, en euros de 2026 ; à la CARCDSF,
6 284,06 €) n'est pas chiffré par E10 au-delà de ce contrôle : à dire à la correction,
si une autre sortie lit ces cotisations.

### 1.1 La CARMF, les deux premières années d'exercice : conforme

**Le texte.** Article 3, 5° (JORFARTI000054153420), qui remplace l'article 4 du décret
n° 49-579 (LEGIARTI000054168136, depuis le 1er juillet 2026) : « Art. 4. - I. - Tout
médecin obligatoirement affilié à la caisse est dispensé du paiement de la cotisation
afférente au présent régime pendant les deux premières années d'exercice de la profession
libérale si cet exercice débute alors qu'il n'a pas atteint l'âge de 40 ans. » ; 6°,
article 4-1 (LEGIARTI000054168116) : « II. -Les cotisations ou fractions de cotisations
ayant fait l'objet d'une dispense au titre des I à III de l'article 4 ne donnent pas lieu
à acquisition de points. » Citations de E10 exactes.

**Le modèle.** `carmf_complementaire.yaml`, période de 2026 (ligne 1382) : `assiette:
plafonnee_3_5_pass`, `taux_cotisation_retraite: 0.1180`. Le code n'a d'autre dispense que
celle du RSA (L. 613-11 : `droit/acquerir.py`, lignes 794 à 800 ;
`moteur/js/droit/acquerir.js`, lignes 632 à 637). Essai : née le 1er janvier 2001,
`medecin_liberal`, début à 26 ans (1er janvier 2027), pension à 67 ans : les deux moteurs
servent 53 701,26 € (« cotisations revalorisées 990,652 € × rendement 4.48% × coefficient
de majoration 1.2100 ») ; cotisations revalorisées de 2027, 20 997,0503 €, de 2028,
21 141,5017 € (non nulles : le modèle fait cotiser ces deux années).

**À la main.** 20 997,0503 + 21 141,5017 = 42 138,5520 ; × 0,04 = 1 685,5421 ; × 0,0048
= 202,2650 ; 1 887,8071 ; × 0,21 = 396,4395 ; 1 887,8071 + 396,4395 = **2 284,2466 €**,
2 284,25 € par an de trop. Le total : 990 651,9421 × 0,0448 × 1,21 = 53 701,2605. Le
début au 1er janvier rend les deux lectures des « deux premières années » (24 mois, ou
deux années civiles) identiques : 2027 et 2028.

**La lecture contraire.** Intenable : « est dispensé », quand le III du même article dit
« peut être accordée sur demande » ; et, sans points, par le 4-1, II. **Écart faible** :
la déclaration tait la faculté de l'article 4-2, I : « un point par trimestre […] ou
trimestres ayant donné lieu à dispense dans les conditions prévues au I de l'article 4 »
peuvent être rachetés. Une faculté sur demande, que le modèle ne porte pas : l'erreur
tient, mais la correction doit la nommer.

### 1.2 La CARMF, passé le semestre des 75 ans : conforme

**Le texte.** Même article 4, II : « Tout médecin qui continue d'exercer en qualité de non
salarié est exempté du versement de la cotisation à partir du premier jour du semestre
civil qui suit son soixante-quinzième anniversaire. » ; sans points par le 4-1, II, qui
vise « les I à III ». Citation exacte.

**Le modèle et l'essai.** Née le 1er janvier 1951, `medecin_liberal`, début à 30 ans,
pension à 76 ans et 6 mois (1er juillet 2027) : les deux moteurs servent 18 895,60 €
(« cotisations revalorisées 324,444 € × rendement 4.48% × coefficient de majoration
1.3000 ») ; 2026, 10 239,2845 € ; 2027, 5 154,8634 € (le semestre d'avant le départ).
Soixante-quinze ans le 1er janvier 2026 ; le semestre qui suit s'ouvre le 1er juillet
2026, le jour même de l'entrée en vigueur.

**À la main.** 5 154,8634 × 0,04 = 206,1945 ; × 0,0048 = 24,7433 ; 230,9379 ; × 1,3 =
**300,2192 €** ; si 2026 se partage au semestre : 10 239,2845 / 2 = 5 119,6423 ;
+ 5 154,8634 = 10 274,5057 ; × 0,0448 = 460,2979 ; × 1,3 = **598,3872 €**. Les deux
montants de E10 sont exacts ; « au moins 300,22 € » tient sous les deux lectures du
second semestre de 2026, que le texte ne tranche pas (la cotisation est annuelle ; le IV
du même article parle de « cotisation semestrielle ») : bien déclaré.

**La lecture contraire.** Intenable : « est exempté », sans demande. **Même écart
faible** : l'article 4-3 ouvre une faculté que la déclaration tait : « Tout médecin qui
continue d'exercer en qualité de non salarié et qui n'est plus tenu de cotiser à titre
obligatoire, à partir du premier jour du semestre civil qui suit son
soixante-quinzième anniversaire, peut continuer à cotiser volontairement, quel que soit
son âge. » Le modèle sert ce qu'aurait le médecin qui choisit de cotiser ; il simule
l'assuré obligatoire : l'erreur tient.

### 1.3 La CARCDSF, la part proportionnelle des deux premières années : conforme

**Le texte.** Article 5, 2° (JORFARTI000054153467), articles 3-1 et 3-5 du décret
n° 50-28 (LEGIARTI000054168193 et LEGIARTI000054168184, depuis le 1er juillet 2026) :
« Les nouveaux affiliés sont dispensés de la cotisation proportionnelle au titre des deux
premières années civiles de leur exercice et peuvent, sur demande écrite, bénéficier
également d'une dispense de la cotisation forfaitaire. » ; « Les dispenses ou réductions
partielles mentionnées aux articles 3-1 à 3-4 entraînent respectivement la suppression ou
la réduction des droits correspondants. » L'article 2 (LEGIARTI000054168195) : « b) Une
cotisation proportionnelle […] L'assiette de cette cotisation est comprise entre 65 % du
plafond annuel […] et cinq fois ce même plafond. » Citations exactes.

**Le modèle et l'essai.** `carcdsf_complementaire.yaml`, période de 2026 (ligne 636) :
`assiette: tranche_065_5_pass`, `taux_cotisation_retraite: 0.1135`,
`cotisation_forfaitaire_euros: 3210.6`. Née le 1er janvier 2001,
`chirurgien_dentiste_ou_sage_femme`, début à 26 ans, pension à 67 ans : 52 158,40 €
(« cotisations revalorisées 876,612 € × rendement 5.95% ») ; 2027, 19 451,5034 € ; 2028,
19 539,5506 €. La forfaitaire seule, relevée à part : la même carrière à 0,5 salaire
moyen, sous 0,65 plafond, cotise 6 653,2180 € en 2027 et en 2028.

**À la main.** 19 451,5034 − 6 653,2180 = 12 798,2854 ; 19 539,5506 − 6 653,2180 =
12 886,3326 ; somme 25 684,6180 ; × 0,06 = 1 541,0771 ; × 0,0005 = 12,8423 ;
**1 528,2348 €**, 1 528,23 € par an de trop. Contrôle : le revenu de 2027 que la carrière
porte, 87 370,5656 €, et le plafond de 2027 du modèle, 49 237,47 €, lus dans le moteur
Python ; le facteur qui revalorise 2027 à la CARMF, 20 997,0503 / (0,118 × 87 370,5656)
= 2,036625, rend à la CARCDSF 12 798,2854 / (0,1135 × 2,036625) = 55 366,2099 =
87 370,5656 − 0,65 × 49 237,47 : la part proportionnelle est bien celle de la tranche.

**La lecture contraire.** Intenable : « sont dispensés », quand la forfaitaire ne l'est
que « sur demande écrite ». Le rachat (3-7) est une faculté, que la fiche nomme.

### 1.4 Avant le 1er juillet 2026 : les textes que la question 22 doit partir

**Écart faible.** E10 écrit des dispenses d'avant 2026 : « E10 ne les a pas cherchées au
Journal officiel : point non lu ». Le décret lui-même en parlait, dans LEGI. Décret
n° 49-579, article 4, du 27 août 1996 au 30 décembre 2024 (LEGIARTI000006781644) puis
jusqu'au 1er juillet 2026 (LEGIARTI000050865157) : « Des dispenses de cotisations peuvent
être accordée aux adhérents impécunieux et aux professionnels âgés de moins de quarante
ans lors de leur affiliation, dans les conditions prévues par les statuts mentionnés à
l'article 5 du présent décret. » Décret n° 50-28, article 2, du 14 novembre 2025 au
1er juillet 2026 (LEGIARTI000052567910) : « Les statuts fixent les conditions dans
lesquelles des exonérations, des dispenses, des réductions ou des reports de cotisations
peuvent être accordés dans les premières années d'activité professionnelle » ; depuis
1981 au moins, « dans les premières années d'activité professionnelle ou en cas
d'infortune » (LEGIARTI000006760429). Le principe était au décret, ses conditions aux
statuts : avant le 1er juillet 2026, le point reste non tranché, comme E10 le dit, mais la
question 22 a son point de départ. Rien sur l'exemption après 75 ans dans ces rédactions.

## 2. Les quatre écarts de R-E10 repris

**(a) Les trente années de la Cipav : conforme.** Le texte (article 20,
JORFARTI000054153655), relu : « Le compte de points qui est alors établi est majoré de 5%
par année entière de prorogation. « Cette majoration s'applique uniquement aux points
acquis au titre des trente premières années de cotisation à la CIPAV. « Pour la
détermination des trente années de cotisation, les années au titre desquelles l'affilié a
obtenu une exonération ou une réduction de cotisation sont prises en compte. » Essais :
née le 10 mars 1959, `profession_liberale`, début à 22 ans ; à 68 ans et 3 mois et à 72
ans et 3 mois, les deux moteurs servent 24 000,52 € et 35 074,52 €
(374 715,4414 × 0,061 × 1,05 ; 459 993,6709 × 0,061 × 1,25). Majoration servie :
374 715,4414 × 0,00305 = 1 142,8821 ; 459 993,6709 × 0,01525 = 7 014,9035. Les trois
sommes, relevées année par année :

| les trente années | un an : somme | × 0,00305 | de trop | cinq ans : somme | × 0,01525 | de trop |
|---|---|---|---|---|---|---|
| 1981 à 2010 | 184 754,1840 | 563,5003 | 579,38 | 198 030,4407 | 3 019,9642 | 3 994,94 |
| 1982 à 2011 | 190 880,0248 | 582,1841 | 560,70 | 204 596,4784 | 3 120,0963 | 3 894,81 |
| 1981 à 2011 | 194 651,6538 | 593,6875 | 549,19 | 208 639,1330 | 3 181,7468 | 3 833,16 |

Tout est exact au centime. La troisième lecture (31 années civiles) garde le plus de
points ; une lecture au prorata de 2011 tomberait entre la première et elle : 549,19 € et
3 833,16 € sont bien la borne basse. Les statuts de 2023 (ci-dessous) ne disent rien de
plus du décompte d'une première année partielle : ce point reste non tranché, et sa
déclaration conforme à la règle de rigueur.

**(b) La règle d'avant le 1er juillet 2026 : écart moyen.** E10 la dit non tranchée,
faute de l'article 3.15 des statuts, « qu'au Bulletin officiel » (et R-E10 avant lui :
« seul le Bulletin officiel tranche »). Or le dépôt cite depuis le 27 septembre 2026 les
statuts que la caisse publie (`surcote_par_age_seul.yaml`, lignes 382 à 392, « Statuts
Cipav au 01/01/2023 »), dont il ne recopiait que le premier alinéa. Relus en entier,
article 3.15 : « L'adhérent qui a atteint l'âge prévu au deuxième alinéa du 1° de
l'article 3.13 et comptant un minimum de trente années d'affiliation à la C•I•P•A•V, peut
différer la date d'entrée en jouissance de la pension de retraite complémentaire de 1 à 5
ans. Le compte de points qui est alors établi est majoré de 5% par année entière de
prorogation. Cette majoration s'applique uniquement aux points acquis au titre des trente
premières années de cotisation à la C•I•P•A•V. Pour la détermination des trente années de
cotisation, les années au titre desquelles l'adhérent a obtenu une exonération ou une
réduction de cotisation sont prises en compte. » C'est, mot pour mot, l'article 5-2, II,
du décret n° 79-262 dans la rédaction de 2026, à « adhérent » et aux renvois près ; le
décret se dit d'ailleurs une « mise en cohérence » qui « substitue aux statuts de ces
régimes des règlements » (sa notice).

Le Journal officiel le corrobore. L'arrêté du 20 mars 2023 (JORFARTI000047334800, 17°),
« applicable aux cotisations et aux prestations dues au titre des périodes courant à
compter du 1er janvier 2023 » (article 2, JORFARTI000047334796), ôte du « dernier alinéa »
les mots « , telles qu'elles sont définies à l'article 3.6 » et ajoute l'alinéa sur « la
détermination des trente années de cotisation » : le dernier alinéa d'alors est donc
« Cette majoration s'applique uniquement… », et « trente années de cotisation » n'est pas
la condition (« trente années d'affiliation »). Depuis, aucun arrêté publié ne touche
l'article 3.15 : la recherche `"3.15" AND ("architectes" OR "CIPAV")` depuis 2007 ne rend
que celui de 2023 et celui du 16 décembre 2021 (JORFARTI000044554134, 19° : « Au premier
alinéa de l'article 3.15, les mots : « âgé de 65 ans » sont remplacés par les mots :
« qui a atteint l'âge prévu au deuxième alinéa du 1° de l'article 3.13, » », en vigueur le
1er janvier 2022, que E10 ne cite pas ; sans effet sur la portée) ; l'arrêté du
27 décembre 2023 (JORFTEXT000048880667) nomme les articles 3.6, 3.13, 3.14, 3.16 et 3.19,
non 3.15, et ceux de septembre 2025 les statuts généraux.

**La lecture contraire est intenable** pour les pensions qui prennent effet du 1er
janvier 2023 au 30 juin 2026 : il faudrait que la caisse publie un texte de ses statuts
autre que celui que l'arrêté approuve, ce que rien n'indique et que l'arrêté de 2023
dément. Au cas de E10 (née le 10 mars 1957, pension au 1er janvier 2026, un an entier de
report au-delà de 67 ans), refait : servis 22 677,41 € par les deux moteurs (« cotisations
revalorisées 354,058 € × rendement 6.10% × coefficient de majoration 1.0500 ») ;
354 057,8613 × 0,00305 = 1 079,8765 € de majoration ; 1979 à 2008, 168 552,9726 ×
0,00305 = 514,0866 €, **565,79 €** de trop ; 1980 à 2009, 176 081,2970 × 0,00305 =
537,0480 €, **542,83 €** ; 1979 à 2009, 177 676,4629 × 0,00305 = 541,9132 €,
**537,96 €** : l'erreur, au moins 537,96 € par an. Avant 2023, probable — l'alinéa
existait déjà, puisque l'arrêté de 2023 en ôte des mots, et le Guide pratique de 2019 de
la caisse, cité par la même fiche, l'écrit — mais la date d'où il vaut reste à borner :
les statuts de 2006 et les arrêtés qui ne paraissent au Journal officiel que par mention
sont au seul Bulletin officiel (`138/2026-11-05-la-file-des-fac-similes.md`). Gravité :
moyenne ; l'erreur était déclarée, sa période ne l'est pas, et le modèle, rétroactif, sert
déjà ces pensions. Le bloc « Reprise » de l'action 130 (« avant, un point non tranché,
question 22 ») et `sources.a_relire` de la fiche portent la lecture à reprendre.

**(c) Les seize décrets : conforme.** L'index JORF compte 33 documents au titre du décret :
le texte et 32 documents d'articles, la fin de l'article 18 à part (« art. 8 »,
JORFARTI000054153640). Chaque article s'ouvre sur « Le décret du <date> susvisé » ou
« Le décret n° … susvisé » ; rapporté au visa de même date : 2, n° 49-578 ; 3, n° 49-579 ;
4, n° 49-580 ; 5, n° 50-28 ; 6, n° 50-1318 ; 7, n° 51-310 ; 8, n° 53-506 ; 9,
n° 55-1390 ; 10, n° 60-664 ; 11, n° 61-1488 ; 12, n° 65-1139 ; 13, n° 67-1169 ; 14,
n° 68-884 ; 15, n° 70-803 ; 16, n° 72-968 ; 17, n° 74-526 ; 18, n° 75-891 ; 19,
n° 78-283 ; 20, n° 79-262 ; 21, n° 79-263 ; 22, n° 79-265 ; 23, n° 81-755 ; 24,
n° 81-1046 ; 25, n° 84-143 ; 26, n° 84-254 ; 27, n° 2003-1273 ; 28, n° 2016-1991. Tous
justes, et les seize de E10 avec eux. Les quatorze identifiants LEGI que la fiche cite
sont chacun l'article qu'elle dit (50-1318, art. 2 ; 53-506, art. 2 ; 67-1169, art. 4 ;
72-968, art. 2 ; 75-891, art. 7-2 et 6 ; 78-283, art. 2 ; 79-265, art. 2 et 5 ;
81-1046, art. 2 ; 84-143, art. 2 et 5 ; 84-254, art. 2 ; D. 641-6), en vigueur au
1er juillet 2026 (D. 641-6 jusque-là), et chacun est cité par la fiche de règle qu'elle
nomme (`cotisation_par_classes_liberales`, `cavamac_minoration_age_seul`,
`asv_medecins_points`, `asv_medecins_ajustement`, `asv_autres_professions_de_sante`,
`cavom_assiette_2016`, `cavom_ages_minoration`, `carpimko_assiette_2026`,
`carpimko_ages_2015`) ; les sept fiches dites à version `reglement_de_2026` en ont une, qui
cite le décret.

**(d) L'article 13 : conforme.** « Lorsqu'un adhérent cesse ses fonctions, il a la
faculté de verser, en plus de la cotisation normale de l'exercice, une cotisation
supplémentaire de fin de carrière. » : une faculté ; citation exacte, comme celle du
prorata.

## 3. La forme de la fiche

**Le renvoi, hors de `LUES_AU_DROIT` : conforme.** Les deux citations de l'architecture
sont exactes (§ 6.1, ligne 889 ; § 6.6, ligne 1043, la gras ôté). `carte.manques()` rend
74 fiches et 420 manques, dont six à `decret_2026_418_liberaux` (`dates_qui_decident`,
`domaine`, `ecrit`, `etape`, `lit`, `versions`) : les remplir ferait d'un texte un
dispositif. Laisser la fiche hors de la liste, et la forme d'une fiche de texte au
propriétaire, est à bon droit. Les comptes de l'`effet` tiennent : quinze articles pour
quinze régimes calculés (les quinze des `regimes`), douze pour les régimes non calculés,
quatre sans règle, 31 en tout.

**Le test : écart faible.**
`test_chaque_article_du_decret_2026_418_est_rapporte_a_la_fiche_de_sa_regle` tient ce que
sa docstring dit — chaque document d'article nommé par une lecture, chaque nom entre
accents graves une fiche, une version ou une clé d'un fichier de régime —, non ce que son
nom dit. Éprouvé en mémoire, la fiche altérée sans rien écrire : l'article 10 ôté, rouge ;
un nom de fiche mal écrit, rouge ; l'article 5 (CARCDSF) renvoyé à
`carpv_minoration_age_seul`, **vert** ; un nom de fiche remplacé par `assiette`, clé d'un
régime, **vert**. Le rattachement de chaque article à sa fiche n'est tenu que par cette
relecture. À la « -bis » : renommer le test, ou lui donner la table attendue (article,
décret, fiches).

## 4. La classe A de la CAVEC, le cliquet, le bloc « Reprise »

**La CAVEC : conforme.** `classes_cotisation_epoques.yaml`, `cavec_complementaire` :
`classe_de_debut: {debut: 2019, fin: null, rang: 0, annees: 1}` ; la grille va de A à H
depuis 2008 (rang 0, la classe A) ; le moteur la lit (`moteur/js/regimes.js`, ligne 3253 ;
`donnees/regimes.py`, ligne 1483). Le texte de 2026, article 2 du décret n° 53-506
(LEGIARTI000054168240) : « Sauf option pour la classe B, l'affilié est inscrit d'office en
classe A pour sa première année civile d'exercice. » La ligne qui la disait non portée
était fausse ; la corriger était juste. De même, la CARPV : la grille commence à la
classe B (rang 0).

**Le cliquet : conforme.** 9 312 → 9 307 (H6, dbf6104) → 9 306 (E10) : il ne fait que
décroître ; `test_la_liste_du_depot_tient_et_son_cliquet_est_juste` est vert, le compte est
donc bien 9 306. D. 641-6 (LEGIARTI000006738107, du 1er janvier 2004 au 1er juillet
2026) : « L'arrêté prévu à l'article L. 641-5 est pris par le ministre chargé de la
sécurité sociale, après avis de la Caisse nationale d'assurance vieillesse des professions
libérales. » Une procédure : sans effet, à bon droit.

**Le bloc « Reprise » : conforme, à une phrase près.** Ses chiffres sont ceux de la note
(549,19 € ; 2 284,25 € ; 300,22 € ; 1 528,23 € ; 74 fiches, 420 manques) ; il porte
« avant, un point non tranché, question 22 », que l'écart (b) contredit.

## 5. Un candidat neuf, hors de la tâche

**La CARCDSF, l'affiliation au trimestre suivant.** Article 2 du décret n° 50-28, dans la
rédaction du 1er juillet 2026 : « L'affiliation ou la radiation prend effet au premier
jour du trimestre civil suivant le début ou la fin de l'activité professionnelle. » Le
modèle fait cotiser l'année 2027 entière (19 451,5034 €, au niveau de 2028) d'une activité
commencée le 1er janvier 2027. Si « suivant » exclut le trimestre qui s'ouvre le jour même,
l'affiliation date du 1er avril 2027 ; le texte ne le tranche pas, ni ne dit si la
forfaitaire se proratise. Non chiffré ; à lire avec le prorata au trimestre de la CARPV,
candidat de E10.

## Tests

Les tests de la zone (`test_sections_liberales.py`, `test_carte.py`, `test_textes.py`,
`test_regle_de_chacun.py`) : 98 verts ; sous `PRESOMPTIONS_DECALEES=1`, 97 verts et un
sauté (« le portage lit ses présomptions dans le paquet, que la mesure ne décale pas »).
`python -m pytest -m rapide`, sur deux processus : 4 575 verts, 9 sautés (archives de la
DREES absentes de `data/brut/`), 11 rouges, tous de `test_pages_en_dossier.py`, les pages
que GitHub refait.

## Ce qui repart en « -bis »

- **(b), moyen** : déclarer l'erreur de la Cipav pour les pensions qui prennent effet du
  1er janvier 2023 au 30 juin 2026, au moins 537,96 € par an au cas posé (565,79 €,
  542,83 € ou 537,96 € selon le décompte), sur l'article 3.15 des statuts au 1er janvier
  2023 et l'arrêté du 20 mars 2023 ; citer l'arrêté du 16 décembre 2021 ; la date d'avant
  2023 au Bulletin officiel ; récrire en conséquence `sources.a_relire` et la « Reprise ».
- **Le test, faible** : le renommer, ou lui faire tenir la table article, décret, fiches.
- **Les déclarations de la CARMF, faible** : nommer le rachat des trimestres dispensés
  (4-2, I) et la cotisation volontaire après 75 ans (4-3).
- **La question 22, faible** : partir de l'article 4 du décret n° 49-579 (1996 à 2026) et
  de l'article 2 du décret n° 50-28 (les dispenses « dans les premières années d'activité
  professionnelle », aux statuts).
- **Candidat** : l'affiliation de la CARCDSF au trimestre suivant.
