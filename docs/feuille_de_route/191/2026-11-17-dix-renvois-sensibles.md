# Les dix renvois qui peuvent changer un résultat, relus au texte

Le 17 novembre 2026. La note de décision 0009 compte, parmi les 96 renvois
des fichiers de régime aux deux fiches d'âge (`age_legal_par_generation`,
`age_annulation_decote`), dix dont la date de bascule peut changer un
résultat, et demande de les relire en premier. Cette note les relit contre
le texte, et contre lui seul : l'index JORF et LEGI de la DILA
(`scripts/fetch/dila_cherche.py`, à jour au 16 novembre 2026). Aucune règle,
aucun fichier de `moteur/js/` n'est touché. Les corrections sont proposées,
et attendent l'accord du propriétaire.

## Le bilan

| Régime | Renvoi | Date du dépôt | Date du texte | Verdict |
|---|---|---|---|---|
| Banque de France | âge d'ouverture | 1er janvier 2008 | 1er avril 2007 | faux |
| Banque de France | âge du taux plein | 1er janvier 2008 | table propre, décote dès le 1er janvier 2009 | faux, et le renvoi lui-même |
| CNBF | âge d'ouverture | 1er janvier 2004 | 1er janvier 2004 | juste |
| Cavimac | âge d'ouverture | 1er janvier 2007 | 20 décembre 2005 et 2 novembre 2006 | faux, déjà déclaré |
| Fonction publique d'État | âge du taux plein | 1er janvier 2004 | 1er janvier 2004 | juste |
| CNRACL | âge du taux plein | 1er janvier 2004 | 1er janvier 2004 | juste |
| FSPOEIE | âge du taux plein | 1er janvier 2004 | 1er janvier 2004 | juste |
| CRPCEN | âge d'ouverture | 1er janvier 2025 | 1er janvier 2025 | juste |
| Commerçants d'avant 1973 | âge d'ouverture | 1er janvier 2013 | 7 octobre 2012 | faux, déjà déclaré |
| Artisans d'avant 1973 | âge d'ouverture | 1er janvier 2013 | 7 octobre 2012 | faux, déjà déclaré |

Cinq sont justes, cinq sont faux. Parmi les faux, l'un cache une erreur
plus lourde que sa date : la décote de la Banque de France n'est pas celle
de la fonction publique. Trois autres étaient déjà déclarés dans les notes
des fiches, coupés à l'année.

## Banque de France : l'âge d'ouverture

**Ce que dit le dépôt.** `banque_de_france.yaml` garde 55 ans jusqu'au
31 décembre 2007, et renvoie à l'âge légal à compter de 2008.

**Le texte.** Décret n° 2007-262 du 27 février 2007, article 1er
(JORFARTI000001483411) : « Le régime de retraite des agents titulaires de
la Banque de France est fixé à compter du 1er avril 2007 par le règlement
annexé au présent décret. » Règlement annexé, article 26 a
(LEGIARTI000006778516) : la liquidation intervient si l'agent a atteint
« au moins l'âge de soixante ans ; ou au moins l'âge de cinquante-cinq ans
s'il appartient à l'une des catégories dont la nomenclature est fixée par
délibération du conseil général ». Aucune disposition transitoire ne garde
55 ans au sédentaire : l'article 68 n'abaisse l'âge qu'aux carrières longues,
à compter du 1er janvier 2008.

**Verdict.** Faux : la bascule est le 1er avril 2007, non le 1er janvier
2008. La fiche le savait (« Il entre en vigueur au printemps 2007 »), et
l'avait coupé à l'année.

**Effet.** Un agent sédentaire de 55 à 59 ans dont la pension prend effet
d'avril à décembre 2007 part dans le modèle, et ne le pouvait pas. La valeur
d'avant, 55 ans, reste non relue : l'index ne porte pas le règlement annexé
au décret n° 68-300.

**Correction proposée.** Dater le renvoi au 1er avril 2007 quand les
versions se datent au jour (phase 6 de la note 0009). D'ici là, la coupure
à l'année se discute : passer la période de 2008 à 2007 donne raison à neuf
mois sur douze au lieu de trois.

## Banque de France : l'âge du taux plein, et la décote

**Ce que dit le dépôt.** De 2008 à 2022, la fiche renvoie à
`age_annulation_decote` et au barème `decote_fonction_publique` : la limite
d'âge de 65 à 67 ans, diminuée des trimestres de la table de la fonction
publique, et son coefficient, lus à l'année où le droit s'ouvre. La note de
la période le dit : « L'âge d'annulation de la décote reste celui de la
fonction publique, non relu. »

**Le texte.** Règlement annexé au décret n° 2007-262, article 32 (1,25 %
par trimestre, âge d'annulation à la limite d'âge du grade) « sous réserve
des dispositions transitoires de l'article 70 » ; article 70, rédaction
d'origine (LEGIARTI000006778516) : « Jusqu'au 30 juin 2022, sont fixés comme
indiqué dans le tableau suivant : 1° Le taux du coefficient de minoration
[…] ; 2° L'âge auquel s'annule le coefficient de minoration ». Le tableau,
par période où l'agent est susceptible de liquider : « Jusqu'au 31 décembre
2008. Sans objet » ; « Du 1er janvier 2009 au 30 juin 2009. 0,125 % 61 ans
56 ans » ; « Du 1er janvier 2011 au 30 juin 2011. 0,375 % 62 ans 57 ans » ;
« Du 1er janvier 2015 au 30 juin 2015. 0,875 % 63 ans 58 ans » ; jusqu'à
« Du 1er juillet 2021 au 30 juin 2022. 1,250 % 64 ans et 3 trimestres 59 ans
et 3 trimestres ». Dans la rédaction du 9 mai 2012 (LEGIARTI000025882187),
le tableau se lit par période de naissance. LEGI porte treize rédactions du
règlement en vigueur de 2007 à 2025 ; celles qui récrivent l'article 70
restent à relever une à une.

**Verdict.** Faux, et pas seulement la date. Le règlement de la Banque de
France a sa propre montée en charge, décalée de trois ans sur celle de la
fonction publique, avec des âges écrits en clair et une colonne pour les
catégories à 55 ans. Le renvoi à la table de la fonction publique n'est pas
le droit du régime.

**Effet.** Un agent né en 1948, parti à 60 ans en 2008 avec trois trimestres
de moins que la durée requise, subit dans le modèle la décote de la fonction
publique de 2008, 0,375 % par trimestre, soit 1,125 % ; le règlement ne lui
en oppose aucune. Parti au premier semestre 2009 dans la même situation, il
subit 0,5 % par trimestre au lieu de 0,125 %. L'écart court jusqu'en 2022 et
touche aussi l'âge où la décote s'annule.

**Correction proposée.** Une fiche de la décote de la Banque de France, ses
versions lues dans les rédactions de l'article 70 que LEGI date, d'avril
2007 à juin 2022, et la fiche du
régime qui y renvoie de 2009 à juin 2022 au lieu de la fonction publique.
C'est une règle du scénario 1, qui déplace des résultats : une étape à elle,
sur Fable 5.2, le test tiré du tableau d'abord.

## CNBF : l'âge d'ouverture

**Ce que dit le dépôt.** 65 ans jusqu'en 2003, l'âge légal dès 2004.

**Le texte.** Code de la sécurité sociale, article L. 723-10-1, en vigueur
au 1er janvier 2004 (LEGIARTI000006744100) : « La liquidation de la pension
peut être demandée à partir de l'âge prévu au premier alinéa de l'article
L. 351-1. » Le décret d'application, n° 2004-1449 du 23 décembre 2004, est
rétroactif, article 4, I (JORFARTI000001653736) : ses dispositions sur la
pension de base « entrent en vigueur le 1er janvier 2004 ». Avant, R. 723-30
(LEGIARTI000006752415) : le droit est acquis à l'avocat qui « a atteint
l'âge de soixante-cinq ans ».

**Verdict.** Juste. **Effet** : aucun. À noter pour la fiche : le III du
même article garde les règles d'avant à l'avocat qui avait 169 trimestres
au 31 décembre 2003 et continue d'exercer, si elles lui sont plus
favorables ; le dépôt ne le porte pas.

## Cavimac : l'âge d'ouverture

**Ce que dit le dépôt.** 65 ans toute l'année 2006, l'âge légal dès 2007 ;
la note de la période 2006 dit déjà les deux dates, et le choix de couper à
l'année.

**Le texte.** Jusqu'au 20 décembre 2005, L. 721-5 renvoie l'âge au décret
(LEGIARTI000006744052), et D. 721-6 le fixe « à soixante-cinq ans »
(LEGIARTI000006738899). La loi n° 2005-1579 du 19 décembre 2005, article 75
(JORFARTI000002070677), récrit l'article, devenu L. 382-27 : la pension est
servie « dans les conditions définies aux articles L. 351-1 à L. 351-1-3 »,
l'âge légal donc, pour les périodes d'après 1997 ; les prestations des
périodes d'avant restent « dans les conditions […] en vigueur au
31 décembre 1997 sous réserve d'adaptation par décret ». Le décret
n° 2006-1325 du 31 octobre 2006, article 2, I (JORFARTI000001085913),
abaisse celles-ci « à soixante ans » pour qui a la durée requise, et le II
les sert décotées aux autres. Publié au Journal officiel du 1er novembre
2006, sans date propre, il entre en vigueur le lendemain.

**Verdict.** Faux, en deux marches : les périodes d'après 1997 au
20 décembre 2005, celles d'avant au 2 novembre 2006 (le dépôt écrit « à
compter du 1er novembre 2006 »). La date déclarée du dépôt, le 1er janvier
2007, est en retard d'un an sur la première.

**Effet.** Un ministre du culte de 60 à 64 ans qui a sa durée et part en
2006 n'a rien dans le modèle ; la loi lui sert la fraction d'après 1997 dès
janvier 2006, et l'autre dès décembre 2006.

**Correction proposée.** Au jour, deux renvois : le 21 décembre 2005 pour
la fraction d'après 1997 (le dépôt lit déjà les deux fractions,
`fractions_des_cultes`), le 2 novembre 2006 pour celle d'avant. À l'année,
la période de 2006 renverrait mieux à l'âge légal qu'à 65 ans : la fraction
d'après 1997 y a droit toute l'année.

## Fonction publique d'État, CNRACL, FSPOEIE : l'âge du taux plein

**Ce que dit le dépôt.** 60 ans jusqu'en 2003 ; dès 2004, le renvoi à la
limite d'âge par génération et le barème `decote_fonction_publique`, qui ne
porte aucune ligne avant 2006.

**Le texte.** Loi n° 2003-775, article 80 (JORFARTI000001145696) : « les
dispositions du présent titre entrent en vigueur le 1er janvier 2004 » ;
article 66, III (JORFARTI000002020831) : jusqu'au 31 décembre 2019, le
coefficient et « l'âge auquel s'annule le coefficient de minoration, exprimé
par rapport à la limite d'âge » suivent un tableau. La CNRACL : décret
n° 2003-1306, article 67 (« entrent en vigueur à compter du 1er janvier
2004 ») et article 65, III (LEGIARTI000006400937 : « Jusqu'en 2005 Sans
objet Sans objet »). Le FSPOEIE : décret n° 2004-1056, article 52 (« entrent
en vigueur au 1er janvier 2004 », JORFARTI000002058712) et article 50, III
(LEGIARTI000006781529 : « Jusqu'en 2005 Sans objet Sans objet »).

**Verdict.** Juste pour les trois. Le renvoi de 2004 ne décote rien en 2004
et 2005, puisque la table de la décote n'a pas de ligne avant 2006 ; le test
`test_la_decote_de_la_fonction_publique_est_celle_de_l_article_l14`
(`tests/test_simulateur.py`) le vérifie pour une liquidation de 2005.

**Effet.** Aucun.

## CRPCEN : l'âge d'ouverture

**Ce que dit le dépôt.** La table de 2011 jusqu'en 2024 ; dès 2025, la
table de 2023 et le renvoi à l'âge légal pour les nés à compter de 1970.

**Le texte.** Décret n° 90-1215, article 84, rédaction du décret
n° 2023-689 (LEGIARTI000047910068) : « Conformément au V de l'article 2 du
décret n° 2023-689 du 28 juillet 2023, ces dispositions s'appliquent aux
pensions prenant effet à compter du 1er janvier 2025. I.-1° Le droit à
pension est ouvert à partir de l'âge prévu à l'article L. 161-17-2 du code
de la sécurité sociale. L'âge […] s'applique aux assurés nés à compter du
1er janvier 1970. »

**Verdict.** Juste, au jour près. **Effet** : aucun.

## Artisans et commerçants d'avant 1973 : l'âge d'ouverture

**Ce que dit le dépôt.** `cancava_avant_1973.yaml` et
`organic_avant_1973.yaml` gardent 60 ans jusqu'en 2012 et renvoient à l'âge
légal dès 2013 ; la note de la période de 2004 dit que la rédaction suivante
« prend effet le 7 octobre 2012 », et que la fiche est « coupée à l'année ».

**Le texte.** Décret n° 73-937, article 3, rédaction du 19 février 2004 au
7 octobre 2012 (LEGIARTI000006765819) : les prestations « peuvent être
liquidées à compter de l'âge de soixante ans ». Le décret n° 2010-1734,
article 8, II (JORFARTI000023334346), applicable aux pensions prenant effet
à compter du 1er juillet 2011 (article 11), voulait y substituer l'âge de
L. 161-17-2, mais visait « l'article 1er du décret du 2 octobre 1973 », qui
ne porte pas ces mots (LEGIARTI000006765812). Le décret n° 2012-1129 du
4 octobre 2012, article 2, corrige la référence : « Au II de l'article 8 du
décret du 30 décembre 2010 susvisé, la référence à l'article 1er est
remplacée par la référence à l'article 3 » ; sa notice : « le texte entre en
vigueur le lendemain de sa publication », au Journal officiel du 6 octobre
2012. Rédaction du 7 octobre 2012 (LEGIARTI000026474703) : « à compter de
l'âge prévu par l'article L. 161-17-2 », et la décote jusqu'à l'âge de
L. 351-8, 1°, non plus jusqu'à 65 ans.

**Verdict.** Faux de trois mois : l'âge légal vaut pour les pensions qui
prennent effet après le 7 octobre 2012, soit dès le 1er novembre 2012. Un
point reste ouvert : le texte de 2010 voulait cet âge dès le 1er juillet
2011, et un règlement ne rétroagit pas ; ce que la caisse a appliqué entre
juillet 2011 et octobre 2012 ne se lit pas dans l'index. La date de LEGI,
le 7 octobre 2012, est la lecture retenue.

**Effet.** Un artisan ou un commerçant né en 1952, dont la pension prend
effet en novembre ou décembre 2012 avant 60 ans et 8 mois, liquide dans le
modèle sa part d'avant 1973 à 60 ans ; le texte la lui refuse, et décote
désormais jusqu'à l'âge d'annulation du régime général, non jusqu'à 65 ans.

**Correction proposée.** Dater le renvoi au 7 octobre 2012 quand les
versions se datent au jour. À l'année, garder 2013 : neuf mois sur douze
relèvent de l'ancienne rédaction.

## Ce qui attend l'accord du propriétaire

1. La décote de la Banque de France (sa fiche, de 2009 à juin 2022) : la
   correction la plus lourde, une étape à elle, sur Fable 5.2.
2. Les dates au jour des renvois faux : Banque de France au 1er avril
   2007, Cavimac au 21 décembre 2005 et au 2 novembre 2006, artisans et
   commerçants d'avant 1973 au 7 octobre 2012 — dans l'étape de la note 0009
   qui date les renvois.
3. D'ici là, deux coupures à l'année qui donneraient raison plus souvent :
   la Banque de France à 60 ans dès 2007, la Cavimac à l'âge légal dès 2006.
