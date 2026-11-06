# Relecture de E11 (la Cipav de `surcote_par_age_seul` relue au Journal officiel, les écarts de R-E11 repris)

File R-E12, le 6 novembre 2026 (action 130, vague 11, sur Opus) : relecture indépendante,
contre les sources, du commit 50154a0 de la session E11 (`surcote_par_age_seul`,
`decret_2026_418_liberaux`, `tests/test_sections_liberales.py`, le bloc « Reprise » de
l'action 130 ; note `2026-11-06-e11-surcote-par-age-seul.md`). Ni règle, ni donnée, ni
test n'est modifié.

**Méthode.** Les index de la DILA récupérés puis mis à jour : JORF au 6 novembre 2026
(incrément 20261106-002608, 518 516 documents), LEGI au 5 novembre
(LEGI_20261105-214938). Les arrêtés lus en entier dans l'index, les articles de LEGI par
leur identifiant. Les « Statuts Cipav au 01/01/2023 » retéléchargés de la caisse
(`https://www.lacipav.fr/sites/default/files/2023-04/Statuts%20CIPAV_1janvier2023.pdf`,
25 pages, SHA-256 e5034d618178585fdae444ec690247ef83c7e94d7e9ca741682fb98562093790, le
même fichier que E11), lus par `pdftotext`. Les moteurs : `servi_et_refait`
(`tests/outils_pont.py`), qui confronte le portage et le moteur Python, un espion posé
hors du dépôt sur `retraite_notionnelle.droit.acquerir.acquerir`, qui somme
`Droits.cotisations` de `cipav_complementaire` année par année ; les réglages de E11
(`profil` plat, `euros` 2026, `enfants` 0, `sexe` F, `salaire` 2, `debut` 22, `statut`
`profession_liberale`, le reste de `tests/test_complementaires_liberales_a_leur_age.py`),
l'âge de départ en `liquidation` et `liquidation_mois` ; sous les deux jeux de
présomptions.

**En bref.** Les citations, les montants et les relevés de E11 tiennent, au centime,
dans les deux moteurs et sous `PRESOMPTIONS_DECALEES=1`. Aucun arrêté ne manque à sa
liste. Trois écarts : la citation de l'arrêté du 3 octobre 2006 est tronquée d'une
réserve qui pèse sur 2007 (moyen) ; le test du décret ne garde pas sa propre table
(mineur) ; le bloc « Reprise » dit six régimes à lire quand il en reste sept (mineur).

## 1. Avant 2023 : l'article 3.15 relu par différence

### 1.1 Les arrêtés de la période : aucun ne manque

Recherche sans borne de réponses, dans la table de l'index JORF : (a) au titre, de 1975
à 2026, tout texte qui nomme « architecte », « CIPAV » ou « interprofessionnelle de
prévoyance » avec « statut », « complémentaire » ou « régime » (84 textes) ; (b) au
texte, de 2006 à 2026, tout arrêté ou décret qui nomme la CIPAV (« cipav »,
« c.i.p.a.v ») avec « statut », ou « article 3.15 », ou « prorogation » avec la caisse,
ou dont le titre porte une « section professionnelle » ou les « professions libérales »
avec « statut ». Depuis le 3 octobre 2006, les arrêtés des statuts de la Cipav sont ceux
de E11, ni plus ni moins : 3 octobre 2006 (JORFARTI000002050100), 17 décembre 2007,
3 décembre 2010, 6 juillet 2012, 7 octobre 2014, 18 décembre 2015, 19 janvier 2016,
3 août 2017, 22 juin 2020, 16 mars 2021, 16 décembre 2021, 20 mars 2023, 27 décembre
2023, 4 et 17 septembre 2025 ; s'y ajoute celui du 8 décembre 2006, qui n'approuve que
les statuts du « régime invalidité-décès ». Deux décrets, que E11 ne cite pas, ont été
ouverts : le n° 2022-1746 (JORFTEXT000046847137), qui réforme le décret n° 79-262 et ne
dit rien du report ni de l'article 3.15 ; le n° 2026-239 (JORFTEXT000053748618), qui
approuve les « statuts types des sections professionnelles », en vigueur le 1er juillet
2026, et ne porte que leur gouvernance (« liquidation » n'y vise que le régime de
base ; ni report, ni prorogation). Dans le texte de chacun des quinze arrêtés,
« 3.15 » ne paraît que deux fois : décembre 2021, 19°, et mars 2023, 17°. Conforme.
Limite, que E11 ne dit pas : l'index ne garde que le champ social (« filtre
thématique ») ; un arrêté classé ailleurs lui échapperait, ce que rien n'indique.

### 1.2 La reconstitution : sûre pour le texte, une réserve pour 2007

**Le texte de l'article est sûr.** Trois indices du seul Journal officiel, en plus de
ceux de E11 :
- la numérotation « 3.x » vaut dès 2006 : « L'article 3.8 de la troisième partie des
  statuts annexés à l'arrêté du 3 octobre 2006 susvisé est complété comme suit »
  (17 décembre 2007, JORFARTI000017751528) ;
- l'article 3.16 est déjà, en 2010, celui de la liquidation en un versement : « A
  l'article 3.16, il est ajouté un alinéa ainsi rédigé : « Toutefois, si le nombre de
  points acquis est inférieur à 2, la pension est liquidée par un versement forfaitaire
  unique égal à dix fois ce montant. » » (3 décembre 2010, JORFARTI000023217553),
  l'alinéa que l'arrêté du 27 décembre 2023 retouche encore à l'article 3.16 (« Au
  dernier alinéa, les mots : « le nombre de points acquis est inférieur à 180 » sont
  remplacés », JORFARTI000048880676) ; l'article 3.15 n'a donc pas changé de rang ;
- l'alinéa de la restriction se lit au Journal officiel même : le 17°, a), de 2023 ôte
  « , telles qu'elles sont définies à l'article 3.6 » du « dernier alinéa », un pluriel
  féminin qui ne peut se rapporter à « année entière de prorogation », au singulier, du
  deuxième ; et son b) parle de « la détermination des trente années de cotisation ».

Le PDF de la caisse suit l'arrêté de 2023 là où on peut le vérifier : ses articles 3.5,
3.8 et 3.12 portent « Supprimé. » (7°, 10°, 14° de l'arrêté) ; son article 3.6 n'a plus
que deux alinéas (8° : « Les trois derniers alinéas de l'article 3.6 sont supprimés ») ;
son article 3.4 est celui du 6°. Un seul écart de numérotation entre les arrêtés et la
caisse, sans effet sur l'article 3.15 : l'arrêté de 2010 écrit « Il est ajouté un
article 3.12 ainsi rédigé » (JORFARTI000023217549) quand un article 3.12 existe (« 9°
L'article 3.12 est remplacé par les dispositions suivantes : « La cotisation peut, sur
demande expresse de l'adhérent, être réduite », 18 décembre 2015, JORFARTI000031680320) ;
depuis 2017, le texte de 2010 est « l'article 3.12 bis » (22°, JORFARTI000035427394).

**La réserve que E11 tronque (écart moyen).** E11 cite de l'arrêté du 3 octobre 2006
qu'il approuve la « troisième partie « Régime de retraite complémentaire » » et que les
statuts de 1979 sont « abrogé[s] à compter du 1er janvier 2007 ». Le texte entier
(JORFARTI000002050100) : « sont approuvées les modifications apportées aux statuts […]
(art. 2.7 et 2.21 de la seconde partie « règlement intérieur », troisième partie
« Régime de retraite complémentaire », ainsi que les dispositions transitoires).
L'arrêté du 21 mars 1979 portant approbation des statuts de la section professionnelle
des architectes, agréés en architecture, ingénieurs, techniciens, experts et conseils
et relatif au régime d'assurance vieillesse complémentaire est abrogé à compter du
1er janvier 2007, à l'exception de l'article 16 et de l'article 17, alinéa 2, qui seront
abrogés le 1er janvier 2008. » Les dispositions transitoires de 2006 et les articles 16
et 17, alinéa 2, de 1979, en vigueur jusqu'au 1er janvier 2008, sont au seul Bulletin
officiel, non lus : ils peuvent régler le report en 2007, ou les points acquis avant
2007. Ni E11, ni la fiche ne le disent. Verdict : le texte de l'article 3.15 de 2007 à
2021 est sûr ; qu'il s'applique dès le 1er janvier 2007 est une lecture forte, non
prouvée ; « la lecture contraire supposerait un arrêté que le Journal officiel n'a pas
publié » est trop fort, puisque ce que l'arrêté de 2006 réserve est au Bulletin
officiel. Pour 2007, un point non tranché ; au-delà, une réserve à écrire (question 22).
Aucun montant posé n'en bouge.

### 1.3 Le décompte d'avant 2023 : bien déclaré ouvert

Ce que le Journal officiel montre de l'article 3.6 avant 2023 : le 16 mars 2021, 10°,
« a) Au premier alinéa, le mot : « demandé » est remplacé par le mot : « obtenu » ;
b) Au deuxième alinéa, le mot : « Cette » est remplacé par les mots : « Le montant de
sa » » ; le 16 décembre 2021, 17°, « Au troisième alinéa de l'article 3.6, les mots :
« son 65e anniversaire » sont remplacés » ; le 20 mars 2023, 8°, ses trois derniers
alinéas supprimés. Ses deux premiers sont ceux du PDF de 2023, « Cas particulier du
paiement de la cotisation après la liquidation » ; les trois autres, qui définissaient
les années, ne sont lus nulle part. E11 le déclare ouvert, dans sa note, la fiche et le
journal : conforme. Le bloc « Reprise » ne le dit pas (voir 5). Une lecture que E11 ne
chiffre pas, et qui ne retire rien à son « au moins » : compter les trente années depuis
l'affiliation à la caisse au régime de base (1971 au cas de 2016) borne les points
majorés plus tôt, et grossit l'écart.

### 1.4 Première erreur neuve, de 2013 à 2022 : conforme

Le modèle : `cipav_complementaire.yaml`, période 2013-2021, `surcote_par_trimestre:
0.0125`, `surcote_age_debut: 65`, `surcote_affiliation_minimale_trimestres: 120` ; ses
notes : « il majore TOUS les points et non ceux des trente premières années, ce que rien
dans le modèle ne distingue ». Essayé : née le 10 mars 1949, `liquidation` 66 et 9 mois,
départ servi en janvier 2016 dans les deux moteurs, 12 625,514345 € (« cotisations
revalorisées 193,940 € × rendement 6.20% × coefficient de majoration 1.0500 ») ;
relevés : 1979 à 2015, 37 années, 193 940,3125 € ; 1979, 1 558,2124 € ; 1979 à 2008,
137 466,6071 € ; 1980 à 2009, 143 335,1748 € ; 1979 à 2009, 144 893,3872 €. À la main :
0,05 × 0,062 = 0,0031. 193 940,3125 × 0,003 = 581,8209 ; × 0,0001 = 19,3940 ;
601,2150 € de majoration servie. 137 466,6071 × 0,0031 = 412,3998 + 13,7467 =
426,1465 ; 601,2150 − 426,1465 = 175,07 €. 143 335,1748 × 0,0031 = 430,0055 + 14,3335 =
444,3390 ; 156,88 €. 144 893,3872 × 0,0031 = 434,6802 + 14,4893 = 449,1695 ; 152,05 €.
Le texte, de 2007 à 2021 et en 2022 (où l'arrêté de 2023 ne situe pas les mots « ,
telles qu'elles sont définies à l'article 3.6 ») : « Cette majoration s'applique
uniquement aux points acquis » ; aucune lecture
contraire ne tient sous ce mot, et le Guide pratique 2019 de la caisse, cité par la
fiche, l'écrit. L'erreur tient : au moins 152,05 € par an.

### 1.5 Seconde erreur neuve, de 2007 à 2012 : conforme, sous la réserve de 1.2

Le modèle : périodes 1979-1999 et 2000-2012, `surcote_par_trimestre: null` ; ses notes :
« Aucun statut de la caisse ne date la règle dans l'index : elle est servie depuis 2013,
borne de période, et rien avant » : une borne de modèle, non un texte. Essayé : née le
10 mars 1945, départ servi en janvier 2012 dans les deux moteurs, 9 791,174793 €
(« cotisations revalorisées 157,922 € × rendement 6.20% », sans coefficient) ; relevés :
1979 à 2011, 157 922,1741 € ; 1979 à 2008, 135 298,4577 € ; 1980 à 2009,
141 074,4652 € ; 1979 à 2009, 142 608,1012 €. À la main : 157 922,1741 × 0,062 =
9 791,1748 ; 135 298,4577 × 0,003 = 405,8954 ; × 0,0001 = 13,5298 ; 419,43 € ;
141 074,4652 × 0,0031 = 423,2234 + 14,1074 = 437,33 € ; 142 608,1012 × 0,0031 =
427,8243 + 14,2608 = 442,09 €. Conditions : 65 ans le 10 mars 2010, un an entier ;
affiliée depuis 1967. L'erreur tient pour une pension de 2008 à 2012, sauf si les
dispositions transitoires de 2006 en disent autre chose ; pour 2007, non tranché
(1.2) : au moins 419,43 € par an servis en moins au cas posé.

## 2. La Cipav, du 1er janvier 2023 au 30 juin 2026 : conforme

Statuts au 1er janvier 2023 (PDF, même empreinte), article 3.15, quatre alinéas, mot pour
mot : « L'adhérent qui a atteint l'âge prévu au deuxième alinéa du 1° de l'article 3.13
et comptant un minimum de trente années d'affiliation à la C•I•P•A•V, peut différer la
date d'entrée en jouissance de la pension de retraite complémentaire de 1 à 5 ans. » ;
« Le compte de points qui est alors établi est majoré de 5% par année entière de
prorogation. » ; « Cette majoration s'applique uniquement aux points acquis au titre des
trente premières années de cotisation à la C•I•P•A•V. » ; « Pour la détermination des
trente années de cotisation, les années au titre desquelles l'adhérent a obtenu une
exonération ou une réduction de cotisation sont prises en compte. » Article 3.13, 1° :
« A taux plein : - à partir de l'âge du taux plein prévu au 1° de l'article L. 351-8 du
code de la sécurité sociale » ; que ce tiret soit le « deuxième alinéa du 1° », les
mêmes statuts le disent ailleurs (« l'âge du taux plein fixé au deuxième alinéa du 1°de
l'article 3.13 »). Arrêté du 20 mars 2023, 17° (JORFARTI000047334800) et article 2
(JORFARTI000047334796, « L'annexe au présent arrêté est applicable aux cotisations et
aux prestations dues au titre des périodes courant à compter du 1er janvier 2023. ») ;
arrêté du 16 décembre 2021, 19° (JORFARTI000044554134 : « Au premier alinéa de l'article
3.15, les mots : « âgé de 65 ans » sont remplacés par les mots : « qui a atteint l'âge
prévu au deuxième alinéa du 1° de l'article 3.13, » ») et article 2
(JORFARTI000044554130 : « Les modifications apportées aux statuts de la section
professionnelle mentionnée au 11° de l'article R. 641-1 du code de la sécurité sociale
entrent en vigueur le 1er janvier 2022. ») : citations exactes. L'arrêté du 27 décembre
2023 nomme 3.6, 3.13, 3.14, 3.16 et 3.19, non 3.15 : exact.

Essayé : née le 10 mars 1957, départ servi en janvier 2026 dans les deux moteurs,
22 677,406015 € ; relevés : 1979 à 2025, 47 années, 354 057,8613 € ; 1979,
1 595,1659 € ; 2009, 9 123,4904 € ; 1979 à 2008, 168 552,9726 € ; 1980 à 2009,
176 081,2970 € ; 1979 à 2009, 177 676,4629 €. À la main : 0,05 × 0,061 = 0,00305 ;
354 057,8613 × 0,003 = 1 062,1736 ; × 0,00005 = 17,7029 ; 1 079,8765 €.
168 552,9726 × 0,003 = 505,6589 ; × 0,00005 = 8,4276 ; 514,0866 ; 565,79 €.
176 081,2970 × 0,003 = 528,2439 ; × 0,00005 = 8,8041 ; 537,0480 ; 542,83 €.
177 676,4629 × 0,003 = 533,0294 ; × 0,00005 = 8,8838 ; 541,9132 ; 537,96 €. Conditions :
67 ans, l'âge du taux plein de la génération 1957, le 10 mars 2024 : un an entier au
1er janvier 2026. `sources.a_relire` de `decret_2026_418_liberaux` récrit à bon droit :
le texte et son arrêté disent « uniquement », et le PDF suit l'arrêté de 2023 partout où
on le recoupe (1.2).

## 3. Le test du décret : la table est juste ; le test ne garde pas sa table (mineur)

**La table, contre le décret.** Les 32 documents d'articles de l'index, et le texte
JORFTEXT000054153355 : chaque identifiant porte le numéro que la table lui donne ;
chaque article vise le décret que la table nomme, reconnu à sa date dans les visas
(« Le décret du 6 janvier 1950 », n° 50-28 ; « du 21 octobre 1950 », n° 50-1318 ;
« du 3 mars 1951 », n° 51-310, et ainsi de chacun des articles 2 à 28) ; l'article 1er
abroge D. 641-6 ;
29 à 31 ne modifient aucun texte (29 : « fixent au plus tard le 31 décembre 2026 les
critères de soutenabilité financière » ; 30 : l'entrée en vigueur ; 31 : l'exécution).
Le document étiqueté « 8 » (JORFARTI000054153640) suit bien l'article 18, qui finit sur
« 6° L'article 8 est remplacé par les dispositions suivantes : » et qu'il continue
(« Peuvent être exonérés de la cotisation au régime de prestations complémentaires de
vieillesse […] » puis 7° à 9°). Seul l'article 20 porte une majoration pour report
(« II. - L'affilié qui a atteint l'âge prévu au a du 1° de l'article 5-1 et comptant un
minimum de trente années d'affiliation à la CIPAV, peut différer la date d'entrée en
jouissance de la pension de retraite complémentaire de 1 à 5 ans. ») : la table ne
rapporte `surcote_par_age_seul` qu'à lui, à bon droit. Les autres fiches de la colonne,
déjà relues par R-E11, n'ont pas été refaites une à une.

**Le test, éprouvé** hors du dépôt, en mémoire : la table juste, vert ; l'article 5
rapporté à `carpv_minoration_age_seul`, rouge ; l'article 4 à « 49-579 », rouge ;
l'article 20 sans `surcote_par_age_seul`, rouge ; la fiche qui rapporte l'article 5 à
la CARPV, rouge ; `surcote_par_age_seul` remplacé par `assiette` dans la lecture de
l'article 20, rouge ; la lecture de l'article 4 qui nomme le n° 49-579, rouge ; la
lecture de l'article 10 ôtée de la fiche, rouge. Mais la table privée de son article 10,
vert ; la table réduite aux articles 1 et 2, vert : le test compare la fiche à la table,
non la table au décret, et rien n'y compte les 32 documents. « L'article 10 ôté, rouge »
(E11) n'est vrai que de la fiche. Écart mineur : une ligne retirée de la table ôte sa
garde sans rien rougir.

## 4. La CARMF et la question 22 : conforme

Dans LEGI, mot pour mot : décret n° 49-579, article 4-2, I (LEGIARTI000054168114, du
1er juillet 2026) : « un point par trimestre d'exercice en qualité de non salarié,
antérieur au 1 er juillet 1949 ou trimestre assimilé dans les conditions prévues à
l'article 4-4 ou trimestres ayant donné lieu à dispense dans les conditions prévues au I
de l'article 4 » (sous « Les points qui peuvent faire l'objet d'un rachat sont les
suivants ») ; article 4-3 (LEGIARTI000054168112) : « Tout médecin qui continue d'exercer
en qualité de non salarié et qui n'est plus tenu de cotiser à titre obligatoire, à
partir du premier jour du semestre civil qui suit son soixante-quinzième anniversaire,
peut continuer à cotiser volontairement, quel que soit son âge. » ; l'article 4, I, de
2026 (LEGIARTI000054168136) est bien la dispense des « deux premières années d'exercice »
avant 40 ans, et son II l'exemption après 75 ans. Article 4 d'avant : LEGIARTI000006781644
(27 août 1996 au 30 décembre 2024) et LEGIARTI000050865157 (jusqu'au 1er juillet 2026),
la phrase citée y est, à la lettre ; LEGI n'a pas de version antérieure à 1996. Décret
n° 50-28, article 2 : LEGIARTI000052567910 (14 novembre 2025 au 1er juillet 2026) et
LEGIARTI000006760429 (24 septembre 1981 au 4 août 1982), à la lettre. E11 n'en cite que
les deux bouts, sans rien dire du milieu ; la chaîne compte douze versions, et de 1995 à
1997 la phrase ne nomme que « des dispenses de cotisations ». Rien à reprendre.

## 5. La fiche et le bloc « Reprise »

`surcote_par_age_seul`, les 78 lignes de E11 : chaque citation et chaque identifiant
recoupés (1.1, 1.2, 2) ; le texte reconstitué de 2007 à 2021 est celui du PDF, les deux
modifications ôtées ; les dates, justes. La réserve de 1.2 y manque, comme dans la note.

Le bloc « Reprise » de l'action 130 : « restent ses six autres régimes (`lit`,
`versions`, `dates_qui_decident`) » ; or la fiche n'a encore ni `lit`, ni `versions`, ni
`dates_qui_decident` (aucune de ces clés), pour la Cipav pas plus que pour les autres, et
la note de E11 écrit elle-même « pour ses sept régimes ; la Cipav d'abord ». Écart
mineur : la session suivante pourrait sauter les versions de la Cipav. Le bloc écrit
aussi « 419,43 € servis en moins » sans « au moins », que la note et la fiche portent, et
ne nomme pas le décompte de l'article 3.6, ouvert.

## Tests

`tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` (seul le premier nomme `surcote_par_age_seul`) : 98
verts ; sous `PRESOMPTIONS_DECALEES=1`, 97 verts et un sauté, comme E11. La suite
rapide : voir le message du commit.

## Ce qui repart à E12

1. Écrire la réserve de l'arrêté du 3 octobre 2006 (« ainsi que les dispositions
   transitoires » ; les articles 16 et 17, alinéa 2, de 1979 « abrogés le 1er janvier
   2008 »), au Bulletin officiel (question 22), dans `surcote_par_age_seul` et
   `decret_2026_418_liberaux` ; la version de 2007 de la Cipav, non tranchée pour 2007.
2. Faire garder sa table au test du décret : les 32 documents, articles 1 à 31 et la
   fin de l'article 18.
3. Le bloc « Reprise » : les sept régimes, la Cipav d'abord ; « au moins 419,43 € » ;
   le décompte de l'article 3.6, ouvert.
4. Pour mémoire, sans effet : l'article 3.12 de 2010, devenu 3.12 bis sans arrêté publié.
