# Relecture de E13 : les écarts de R-E13, et la CARMF, l'ASV et la CARPIMKO de `surcote_par_age_seul` en versions (R-E14)

File E, relecture R-E14, le 6 novembre 2026 (action 130, vague 11, sur Opus), du commit
1a6013d (E13, session `session_01FVFLAkKh9yrU8HP6hycaZ8`), de sa note
`130/2026-11-06-e13-surcote-par-age-seul.md`, de ce qu'il a écrit dans
`data/reference/regles/surcote_par_age_seul.yaml` et du bloc « Reprise » de l'action 130.
Rien n'est modifié : ni règle, ni donnée, ni test.

**Verdict.** Les trois erreurs neuves et le point non tranché sont justes : chaque
citation se retrouve mot pour mot, chaque montant au centime, et les deux moteurs servent,
sous les deux jeux de présomptions, ce que E13 écrit. Les versions de la CARMF, de l'ASV et
de la CARPIMKO sont bien coupées, et leurs listes d'arrêtés sont complètes. **Un écart
moyen** : la liste des arrêtés qui modifient les statuts de 1979 de la Cipav, présentée
comme complète, en manque trois, dont un qui modifie l'article 17. Deux écarts mineurs et
une remarque. Aucun montant servi ni déclaré ne bouge. Le tout repart à E14.

**Méthode.** Index de la DILA récupérés ce jour : JORF à jour du 3 novembre 2026, LEGI du
2 novembre. Recherches au titre, par `dila_cherche.py` puis en SQL, sans borne de réponses
(`titre` normalisé, sur toute la table `doc`). Pour les arrêtés, les annexes lues
(`JORFARTI` du même titre et de la même date). Cas posés dans les deux moteurs par
`servi_et_refait` (`tests/outils_pont.py`), avec les réglages de E11 (`profil` plat, `euros`
2026, `enfants` 0, `sexe` F, `salaire` 2, `debut` 22), sous le jeu ordinaire puis sous
`PRESOMPTIONS_DECALEES=1`, dans un script hors du dépôt. La date d'effet du modèle est le
premier jour du mois où l'âge de liquidation est atteint, compté depuis `origine_des_ages`
(`src/retraite_notionnelle/calendrier.py`, `carriere.py`, `date_de_l_age`). Une date
« lendemain de la publication » repose sur l'article 1er du code civil, qui n'est pas à
l'index (déjà relevé par R-E2, § 7) et n'est pas relu ici.

## 1. Les erreurs neuves et le point non tranché (section 3 de E13)

**(1) CARMF et ASV, du 1er janvier au 29 mars 2017 : conforme.**
- Texte. Arrêté du 30 novembre 2016, annexe, 1° (JORFARTI000033521562, JO du 4 décembre
  2016), article 15 : « A compter du 1er janvier 2017, pour bénéficier de l'ouverture des
  droits à la retraite complémentaire, le médecin doit simultanément : « 1. Etre âgé de
  l'âge prévu au premier alinéa de l'article L. 351-1 du code de la sécurité sociale. « Si
  le médecin demande à bénéficier de la retraite complémentaire après cet âge, il est
  fait application d'un coefficient de majoration de 1,25 % par trimestre séparant le
  premier jour du trimestre civil suivant celui où le médecin atteint cet âge de la date
  d'effet de la retraite. » Arrêté du 1er décembre 2016, annexe, 3° (JORFARTI000033538061),
  article 12 de l'ASV : « 1° Etre âgé de l'âge prévu au 1er alinéa de l'article L. 351-1
  du code de la sécurité sociale, « Si le médecin demande à bénéficier des prestations
  supplémentaires de vieillesse après cet âge, il est fait application d'un coefficient
  de majoration de 1,25 % par trimestre séparant […] ». Article 2 de chacun
  (JORFARTI000033521558, JORFARTI000033538057) : « Le présent arrêté entre en vigueur au
  1er janvier 2017. » Arrêté du 22 mars 2017, annexe (JORFARTI000034298521, JO du 29 mars
  2017) : « I. - A l'article 15 […] les mots : « après cet âge » sont remplacés par les
  mots : « après l'âge de 62 ans » ; II. - A l'article 12 […] ». Ses articles 1er
  (JORFARTI000034298518) et 2 (JORFARTI000034298519, « chargé de l'exécution du présent
  arrêté ») ne fixent aucune date.
- L'âge. L. 351-1, version du 11 novembre 2010 (LEGIARTI000023035688) : « à partir de
  l'âge mentionné à l'article L. 161-17-2 » ; L. 161-17-2 au 1er janvier 2017
  (LEGIARTI000025014605) ; D. 161-2-1-9 au 1er janvier 2017 (LEGIARTI000025089933, du
  31 décembre 2011 au 1er septembre 2023) : « 1° Soixante ans pour les assurés nés avant
  le 1er juillet 1951 ; […] 3° Soixante ans et neuf mois pour les assurés nés en 1952 ».
- Lecture contraire. 62 ans dès janvier n'a d'appui dans aucun texte : l'arrêté du
  22 mars 2017 ne se donne aucun effet antérieur. Intenable : l'erreur est à bon droit
  déclarée. Ce que la caisse a servi ce trimestre-là n'est pas lu, E13 le dit.
- Calcul. Née le 10 mars 1952 : 60 ans et 9 mois le 10 décembre 2012 (4e trimestre),
  décompte du 1er janvier 2013 au 1er janvier 2017, 16 trimestres, avant le palier
  (65 ans le 10 mars 2017, palier au 1er avril 2017) : 1 + 16 × 0,0125 = 1,20. Le modèle :
  62 ans au 1er avril 2014 (origine avril 1952), 33 mois, 11 trimestres : 1,1375. Servi
  (liquidation 64,75 ans, effet au 1er janvier 2017) : CARMF 12 364,012485712103 €,
  « coefficient de majoration 1.1375 » ; ASV 15 894,810120208112 €. 12 364,0125 / 1,1375
  = 10 869,4615 ; × 0,0625 = **679,34 €** ; 15 894,8101 / 1,1375 = 13 973,4594 ; × 0,0625
  = **873,34 €**. Née le 10 mars 1948 (liquidation 68,75 ans) : texte, 60 ans le 10 mars
  2008, 20 trimestres à 1,25 % du 1er avril 2008 au 1er avril 2013, 15 à 0,75 % jusqu'au
  1er janvier 2017 : 1,3625 ; modèle, 12 (du 1er avril 2010) et 15 : 1,2625 ; servi
  « 1.2625 », CARMF 14 503,908958712109 €, ASV 18 610,457008500212 € ; / 1,2625 × 0,10 =
  **1 148,82 €** et **1 474,10 €**. Tout se retrouve au centime, dans les deux moteurs,
  sous les deux jeux.

**(2) CARMF et ASV, depuis 2017, le médecin né le premier jour d'un trimestre : conforme.**
- Texte : celui du (1), « le premier jour du trimestre civil suivant celui où le médecin
  atteint cet âge » ; même phrase au 22 mars 2017 et au règlement du 10 juillet 2026,
  article 2 (JORFARTI000054435859 : « après l'âge de 62 ans, il est fait application d'un
  coefficient de majoration de 1,25 % par trimestre, séparant le premier jour du
  trimestre civil suivant celui où le médecin atteint cet âge de la date d'effet de la
  retraite »).
- Lecture contraire : que le médecin né le 1er janvier atteigne 62 ans au trimestre
  précédent. Intenable : il les a le 1er janvier, au premier trimestre. Erreur à bon droit.
- Calcul. Né le 1er janvier 1958, pension au 1er janvier 2025 : texte, du 1er avril 2020,
  12 trimestres à 1,25 % jusqu'au 1er avril 2023, 7 à 0,75 % : 1 + 0,15 + 0,0525 = 1,2025 ;
  modèle, du 1er janvier 2020, 12 et 8 : 1,21. Servi « 1.2100 » : CARMF
  16 116,028855738974 €, ASV 19 267,202481654105 € ; / 1,21 × 0,0075 = **99,89 €** et
  **119,42 €**. Né le 2 janvier (liquidation 66,917 ans, effet au 1er janvier 2025) :
  « 1.2025 », 16 016,136114897616 € et 19 147,77767288352 € ; les différences servies sont
  99,89 € et 119,42 €, les mêmes. Essai de plus : né le 1er avril 1958, même date d'effet,
  le modèle sert 1,2025 (CARMF 16 016,14 €, ASV 19 040,61 €), le texte 1,195 (du 1er juillet
  2020 : 12 à 1,25 %, 6 à 0,75 %) ; né le 2 avril, le modèle sert 1,195 : l'erreur vaut
  bien pour chaque trimestre (99,89 € et 118,76 €).

**(3) CARPIMKO, du 3 octobre au 31 décembre 2015 : conforme, réserve comprise ; une
remarque.**
- Texte. Arrêté du 31 juillet 2015, annexe, 4° (JORFARTI000031255547, JO du 2 octobre 2015) :
  « Article 12 ter « Lorsque la liquidation de la retraite est ajournée au-delà de l'âge
  auquel elle aurait pu être liquidée sans abattement, les assurés peuvent bénéficier
  d'une majoration de leur pension. « Cette majoration est égale à 1,25 % par trimestre
  civil entier d'ajournement postérieur à l'âge du taux plein dans la limite de vingt
  trimestres. » ; article 12 quater, 1° : « GÉNÉRATION 1955 ET ANTÉRIEURE […] Age prévu à
  l'article 11.1 65 ans ». Ses articles 1er (JORFARTI000031255544) et 2
  (JORFARTI000031255545) ne fixent aucune date, ni l'annexe (« compter du » n'y désigne
  que des générations ; ni « vigueur » ni « 2015 » ni « 2016 »).
- Calcul. Né le 10 mars 1949, pension au 1er novembre 2015 (liquidation 66,5833 ans) :
  servi 5 298,186050419041 €, « cotisations revalorisées 47,991 € × rendement 11.04% »,
  sans coefficient, dans les deux moteurs ; six trimestres civils entiers d'avril 2014 à
  septembre 2015 : 5 298,1861 × 0,075 = **397,36 €**. Exact.
- Réserve. Le règlement du 10 juillet 2026, article 7 (JORFARTI000054435915) : « La date
  d'entrée en jouissance de la retraite est fixée au premier jour du trimestre civil qui
  suit la demande ». Si la règle était la même en 2015 (article de 1996 à 2026 non lu),
  aucune pension ne prend effet du 3 octobre au 31 décembre 2015 et l'erreur n'a pas de
  cas. E13 le dit ; l'écart de date est bien déclaré dans `carpimko_ages_2015`. Conforme.
- Remarque (mineure, pour E14). « Au moins 397,36 € » est vrai, mais loin du cas posé. Au
  1er janvier 2016, le modèle sert à la même assurée « coefficient de majoration 1.2250 »
  (6 529,68 €), soit 18 trimestres comptés depuis l'âge où la durée est atteinte
  (`surcote_depuis_la_duree`), entre mai et juillet 2011. C'est la lecture qu'il applique
  au même article 12 ter. Sous elle, au 1er novembre 2015, le texte compte 16 ou
  17 trimestres civils entiers : 5 298,1861 × 0,20 = 1 059,64 € ou × 0,2125 = 1 125,86 €
  par an, toujours sous la réserve. À écrire comme valeur du cas posé.

**Point non tranché, CARPIMKO, depuis le 3 octobre 2015 : conforme.** « Trimestre civil
entier d'ajournement postérieur à l'âge du taux plein » : le trimestre qui commence le
jour même où l'âge, ou la durée, est atteint, peut se lire « postérieur » ou non. Les deux
lectures se tiennent, c'est bien un point non tranché. Né le 1er janvier 1950, pension au
1er janvier 2017 : servi « 1.2250 », 6 707,963609618014 € ; né le 2 janvier, « 1.2125 »,
6 639,515001356604 € ; 6 707,9636 / 1,225 × 1,2125 = 6 639,5150 ; écart 0 € ou
**68,45 €** par an. Exact, dans les deux moteurs, sous les deux jeux.

## 2. Les versions (section 2 de E13, et la fiche)

**Bornes : conforme.** Dix versions, contiguës : `avant_2007` [—, 2007-01-01],
`cipav_2007` [2007-01-01, 2008-01-01], `cipav_de_2008` [2008-01-01, 2015-10-03],
`carpimko_octobre_2015` [2015-10-03, 2017-01-01], `carmf_asv_2017`
[2017-01-01, 2017-03-30], `carmf_asv_mars_2017` [2017-03-30, 2022-01-01], `cipav_2022`,
`cipav_2023_a_juin_2026`, `cipav_depuis_juillet_2026` [2026-07-01, 2026-07-18],
`reglements_de_2026` [2026-07-18, —]. Les 3 octobre 2015, 30 mars 2017 et 18 juillet 2026
sont les lendemains de publications sans date d'effet (articles 1er et 2 des arrêtés du
31 juillet 2015, du 22 mars 2017 et des deux du 10 juillet 2026, JORFARTI000054435856,
-857, -912, -913 ; aucune date d'effet dans les règlements eux-mêmes).

**Les arrêtés de la CARMF et de l'ASV, 2016 à 2026 : complets, conformes.** Relevé SQL au
titre (« médecins » avec « statut » ou « règlement », ou « carmf ») : 30 novembre,
1er et 21 décembre 2016 ; 22 mars, 18 septembre et 20 novembre 2017 ; 20 août et
20 décembre 2018 ; 5 octobre 2020 ; 5 mars 2021 ; 6 et 21 février 2024 ; 7 janvier 2025 ;
10 juillet 2026, son rectificatif du 8 août 2026, et 21 septembre 2026. Annexes lues :
21 décembre 2016, « A l'article 15, les cinquième, sixième, septième et huitième alinéas
sont remplacés » (l'inaptitude) ; octobre 2020, l'article 12 modifié est celui de
l'invalidité-décès (section « II. - Les statuts du régime complémentaire d'assurance
invalidité-décès ») ; mars 2021, l'invalidité-décès et l'article 40 des statuts généraux ;
21 février 2024, « A compter du 1er janvier 2017, » supprimé aux articles 15 et 12 ;
janvier 2025, à l'ASV, « Au deuxième alinéa de l'article 15, le mot : « 60 » est remplacé
par le mot : « soixante-deux » », la réversion ; au complémentaire, les articles 10, 36,
42 bis, 66 et un titre VII : rien sur la majoration. Le rectificatif du 8 août 2026
(JORFARTI000054642802) ne touche que l'article 6.

**Les arrêtés de la CARPIMKO, 2013 à 2026 : complets, conformes.** Relevé SQL (« auxiliaires
médicaux » ou « carpimko », avec « statut » ou « règlement ») : 29 avril et 4 juillet 2014,
31 juillet 2015, 3 février 2016, 13 juillet 2017, 20 août 2018, 23 mai 2019, 18 juin 2020,
20 juin 2022, 27 décembre 2023, 14 juin et 19 novembre 2024, 14 novembre 2025,
10 juillet 2026. Annexes lues à « 12 ter », « ajourn », « surcote », « 1,25 % » : seul celui
du 27 décembre 2023 (JORFARTI000048880643) y touche : « 4° Dans l'intitulé précédant
l'article 12 ter, le mot : « Surcote » est remplacé par les mots : « Majoration de la
pension » ; 5° L'article 12 ter est complété par un alinéa […] « Le montant de la pension
des assurés ayant eu au moins trois enfants est majoré de 10 % ». Ses 2° et 3° récrivent
les âges des articles 11 et 12, non la règle de l'article 12 ter. Le règlement du
10 juillet 2026, article 5 (JORFARTI000054435915), reprend les deux phrases mot pour mot.

**Ce que la fiche dit servir : conforme, essayé dans les deux moteurs, sous les deux jeux.**
- Limite des 70 ans : né le 10 mars 1945, pension au 1er janvier 2018 (72,75 ans) : de
  62 ans (1er avril 2007) à 65 ans (1er avril 2010), 12 × 1,25 %, puis jusqu'au 1er avril
  2015 (70 ans), 20 × 0,75 % : 1,30. Servi « 1.3000 » (CARMF 15 837,69 €, ASV 20 026,95 €).
  Né le 10 mars 1952, pension au 1er juillet 2026 : 1,30, servi « 1.3000 ».
- Vingt trimestres, CARPIMKO : mêmes assurés, servi « 1.2500 » (7 081,86 € et 6 810,04 €).
- 62 ans depuis le 30 mars 2017 : né le 10 mars 1952, pension au 1er avril 2017 : 12
  trimestres du 1er avril 2014, palier au 1er avril 2017 : 1,15 ; servi « 1.1500 ».
- Rien avant 2017 à la CARMF : né le 10 mars 1948, pension au 1er octobre 2016, servi sans
  coefficient (13 311,96 €, ASV 17 104,63 €).
- Citations de `carmf_asv_2017`, `carmf_asv_mars_2017`, `carpimko_octobre_2015` et
  `reglements_de_2026` : identiques aux annexes lues.

**Écart mineur (B).** La fiche (`reglements_de_2026`, hypothèse) et la note (section 2)
écrivent : « l'arrêté du 21 septembre 2026 ne modifie que l'article 5 du règlement de la
CARMF ». Son article (JORFARTI000054888279) modifie l'article 5 (deuxième alinéa), l'article
25 et l'article 28 du règlement du complémentaire, l'article 4 de celui de
l'invalidité-décès, et l'article 3 de celui des prestations complémentaires (l'ASV) :
« e) Au dernier alinéa de l'article 3 du règlement du régime de prestations
complémentaires de vieillesse […] la référence : « 161-22- » est remplacée par la
référence : « L. 161-22 » ». Aucun ne touche l'article 2, celui de la majoration : la
conclusion tient, la phrase est inexacte.

**Écart mineur (C).** La note (section 2) range parmi les arrêtés de la CARMF « juillet,
août, novembre et décembre 2018 ». L'index n'a, en 2018, que ceux du 20 août
(JORFTEXT000037352127) et du 20 décembre (JORFTEXT000037864937). La fiche, elle, écrit
« d'août et décembre 2018 », juste. La note est un récit : rien à récrire, l'erreur est
seulement relevée ici.

## 3. Les quatre écarts de R-E13 (section 1 de E13)

**Écart 1, les arrêtés qui modifient les statuts de 1979 : incomplet. Écart moyen (A).**
Les quatre que E13 cite sont exacts : 5 mai 1981 (JORFTEXT000000871027, titre seul, « (ART.
8,11 ET 17) ») ; 4 mai 1982 (JORFTEXT000000677739, titre « APPROBATION D'UNE MODIFICATION
APPORTEE AUX STATUTS », texte « CET ARRETE SERA INTEGRALEMENT PUBLIE AU BULLETIN OFFICIEL DU
MINISTERE DE LA SOLIDARITE NATIONALE. ») ; 17 juin 1985 (JORFTEXT000000840042, « APPROBATION
DES MODIFICATIONS APPORTEES AUX ART. 4,9,12,13,17,17-BIS ET 21 DES STATUTS ») ; 29 juillet
2003 (JORFARTI000001531753, « (art. 9, 11, 13, 15, 17 et 17 bis) », « sera publié
intégralement au Bulletin officiel n° 2003-35 »). Exacts aussi : 7 février 1980 (complémentaire,
art. 6, 8 et 10), 22 août 1986 (« ART. 11 ANNEXE 1 »), 28 décembre 2004 (« statuts (art.
7) », « prend effet le 1er janvier 2005 »), 18 mars 2005 (« statuts (art. 15) du régime
d'assurance vieillesse de base »), 3 octobre 2006.

Mais le relevé SQL des titres de 1979 à 2007 qui nomment les architectes et un statut ou un
régime, la « cipav » ou l'« interprofessionnelle de prévoyance », en donne trois de plus,
que ni la note ni la fiche ne nomment :
- **Arrêté du 9 mars 1987** (JORFTEXT000000321565, JO du 24 mars 1987 ; sa copie LEGI,
  LEGIARTI000006784842, que `data/reference/regimes/cipav_complementaire.yaml` cite déjà) :
  « architectes, agréés en architecture, ingénieurs, techniciens, experts et conseils
  (annexe n° 5, statuts du régime de retraite complémentaire : articles 8, 13, 17 et
  17 bis ; statuts du régime invalidité-décès [art. 12 et 19]). Nota. - L'arrêté du
  9 mars 1987 sera publié intégralement au Bulletin officiel du ministère des affaires
  sociales et de l'emploi. » **Il modifie l'article 17.**
- **Arrêté du 13 août 1987** (JORFTEXT000000475761, JO du 20 août 1987), titre : « […] DES
  REGIMES D'ASSURANCE VIEILLESSE ET INVALIDITE-DECES DES ARCHITECTES,AGREES EN
  ARCHITECTURE,INGENIEURS,TECHNICIENS,EXPERTS ET CONSEILS » ; texte vide à l'index :
  l'article n'est pas dit. Au fac-similé, non lu ici
  (`138/2026-11-05-la-file-des-fac-similes.md`).
- **Arrêté du 12 mai 2000** (JORFARTI000002418428, JO du 24 mai 2000) : « sont approuvées les
  modifications apportées aux statuts du régime de l'allocation vieillesse (art. 1er, 2,
  3, 5 et 18 bis) et aux statuts du régime d'assurance vieillesse complémentaire de la
  section professionnelle des architectes […] (art. 1er, 4, 4 bis, 11, 12 et 18) » ;
  publié au Bulletin officiel n° 2000/24 (JORFARTI000001635196). Ni l'article 16 ni le 17.

Ce qui est donc inexact : la note, « trois nomment l'article 17, un quatrième ne dit pas
l'article » (quatre le nomment, deux ne disent pas l'article) ; la fiche, `avant_2007`
(la liste des arrêtés), `cipav_2007` (« L'article 17 en vigueur en 2007 est celui de 1979
modifié par les arrêtés du 5 mai 1981 […], du 17 juin 1985 […] et du 29 juillet 2003 […],
et peut-être du 4 mai 1982 »), `cipav_de_2008` (« l'article 17 dans la rédaction des arrêtés
du 5 mai 1981, du 17 juin 1985 et du 29 juillet 2003 »), `sources` (« les arrêtés qui
modifient les statuts du complémentaire de 1979 à 2006 […] : 7 février 1980, 5 mai 1981,
4 mai 1982, 17 juin 1985, 22 août 1986, 29 juillet 2003, 28 décembre 2004, 3 octobre
2006 ») ; le bloc « Reprise » (« les arrêtés de 1981 à 2003 qui modifient l'article 17 de
1979 »). Gravité moyenne : une liste dite complète ne l'est pas, ce que R-E4 et R-E7
avaient déjà relevé ailleurs. Aucune valeur ne bouge : `avant_2007` reste supposée, 2007
non tranché, la question 22 ouverte : ceux du 9 mars 1987 et du 12 mai 2000 ne sont
publiés en entier qu'au Bulletin officiel, celui du 13 août 1987 n'a pas de texte à
l'index. À E14 : les ajouter partout où la liste est donnée.

**Écart 2, l'affiliation comptée depuis 1979 : conforme.** 1979 à 2006 : 28 années, pension
au 1er janvier 2007 ; 1979 à 2007 : 29, au 1er janvier 2008 ; 1979 à 2008 : 30, au
1er janvier 2009 ; 1979 à 2011 : 33, en 2012. Moins de trente : rien n'est dû, 0 €.
C'est une lecture parmi d'autres, et E13 l'écrit comme telle (« si les trente années […]
se comptent depuis la première année du régime »).

**Écart 3, le 18° de l'arrêté du 16 décembre 2021 : conforme.** JORFARTI000044554134 :
« 18° L'article 3.13 est remplacé par les dispositions suivantes : « La pension de retraite
complémentaire est liquidée, sur demande expresse formulée par voie dématérialisé ou, à
défaut, par courrier écrit adressé à la CIPAV, aux conditions suivantes : « 1° A taux
plein : « - à partir de l'âge du taux plein prévu au 1° de l'article L. 351-8 du code de
la sécurité sociale » : la citation de `cipav_2022` est exacte.

**Écart 4, l'ASV dans le bloc « Reprise » : conforme.** Le bloc nomme « la CARMF et l'ASV
(1er janvier et 30 mars 2017, 18 juillet 2026) » et leurs deux erreurs neuves.

## 4. Le bloc « Reprise » et « Ce qui reste »

Conformes, à l'écart (A) près : restent la CAVEC, la CAVP (« piste non vérifiée :
2011 ») et la CPRN, chaque rédaction lue à la source ; la fiche reste hors de
`LUES_AU_DROIT` (absente de la liste de `tests/test_carte.py`, ligne 252) ; puis
`cotisation_par_classes_liberales`. Les comptes du propriétaire passent, pour la CARPIMKO,
de « trois et trois » à « trois, une neuve […] et quatre », et, pour la CARMF, à « deux
neuves » avec l'ASV : c'est ce que la section 3 déclare. Non instruit ici, comme demandé.

## 5. Tests

`tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` : 100 verts au jeu ordinaire, 99 verts et un sauté sous
`PRESOMPTIONS_DECALEES=1`. Suite rapide : voir le message du commit.

## Pour E14

1. **(A, moyen)** Les arrêtés du 9 mars 1987 (articles 8, 13, 17 et 17 bis), du 13 août
   1987 (article non dit) et du 12 mai 2000 (articles 1er, 4, 4 bis, 11, 12 et 18),
   ajoutés partout où la fiche dresse la liste des arrêtés qui modifient les statuts de
   1979 (`avant_2007`, `cipav_2007`, `cipav_de_2008`, `sources`), et le bloc « Reprise ».
2. **(B, mineur)** `reglements_de_2026` : l'arrêté du 21 septembre 2026 modifie les
   articles 5, 25 et 28 du complémentaire, 4 de l'invalidité-décès, 3 de l'ASV, et aucun
   article 2.
3. **(D, remarque)** Erreur (3) de la CARPIMKO : écrire la valeur du cas posé sous la
   lecture que le modèle applique depuis 2016, 1 059,64 € ou 1 125,86 € par an, à côté du
   « au moins 397,36 € », sous la même réserve.
4. (C) n'appelle rien : la fiche est juste, et la note ne se récrit pas.
