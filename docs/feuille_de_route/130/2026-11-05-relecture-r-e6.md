# Relecture de E5 et des chiffres d'E4-bis

File R-E6 de la vague 11, le 5 novembre 2026 : relecture indépendante, contre les sources, du
commit 5f6196d de la session E5 (la CPRN lue au droit : `cprn_ages_decote_enfants`, note
`2026-11-05-carte-des-fiches-cprn-lue-au-droit.md`) et des chiffres neufs du commit 0cf9e77 de
la session E4-bis (`cavp_minoration_deux_pentes`, `carpimko_ages_2015` ; note
`2026-11-05-e4-bis-corrections-de-r-e5.md`). Ni règle, ni donnée, ni test n'est modifié.

**Méthode.** `veille_droit.py` (rien de neuf à la base de la Cnav), `docs/veille_droit.md` ;
les index de la DILA récupérés (`dila_index.py --recuperer` : JORF à jour au 3 novembre 2026,
LEGI au 2 novembre). La liste des textes, par requêtes directes sur la base de l'index, sans
borne ni limite : « notaires » et « notariat » au titre, « section professionnelle des
notaires », « CPRN » et « retraite des notaires » au corps, 282 textes triés un à un. Chaque
citation des versions, découpée à ses « [...] », guillemets ôtés et espaces ramenées, cherchée
par un script écrit pour cette relecture dans le texte de l'index qu'elle nomme ; le script
échoue sur des citations altérées exprès. LEGI lu par `dila_cherche.py --num` et `--le`. Chaque
cas des deux notes rejoué par `servi_et_refait` (`tests/outils_pont.py` : le portage servi, le
moteur Python refait au bit près), sur la requête du formulaire, puis sous
`PRESOMPTIONS_DECALEES=1`. Chaque égalité écrite refaite au centime, en décimal, à partir des
valeurs écrites, puis des valeurs servies non arrondies.

## Le verdict

- **E5 : conforme pour l'essentiel.** Les douze citations sont exactes, les dates justes, les six
  versions fidèles au texte ; chaque coefficient et chaque montant est celui des deux moteurs,
  présomptions décalées ou non ; l'erreur du passage de 2024 est prouvée, la lecture contraire
  intenable ; les deux non-tranchés sont fondés ; les 30 % par enfant sont bien hors du modèle ;
  la date d'effet au mois civil est bien celle du modèle. Trois écarts **faibles** : la liste
  des textes manque trois arrêtés (1963, 1964, 2001), et cinq textes, non trois, sont au seul
  Bulletin officiel ; deux phrases du raisonnement de l'âge d'avant 2014 sont inexactes, sans
  que le non-tranché tombe ; deux égalités ne tombent pas juste au centime sur le papier
  (16 999,675 et 17 269,50). Une précision : les « 1 079,34 € par an de trop » ne valent que
  dans la règle du modèle, servir chaque caisse dès son ouverture.
- **E4-bis : les chiffres sont exacts** — 246,61 €, 136,90 €, 205,35 €, 1 263,99 € —, rendus
  par les deux moteurs ; les citations neuves exactes ; les arrêtés de 1956 et de 1989 bien
  nommés ; les deux non-tranchés fondés. **L'écart d'un centime est confirmé**, et il en a un
  second (5 544,34 pour 5 544,33) : gravité faible, aucun montant final ne change.

## A. E5, la CPRN

### La liste des textes : trois arrêtés manquent, et deux textes au Bulletin officiel (faible)

De 1945 à 2026, l'index porte, outre ceux que la fiche nomme, trois approbations de
modifications du règlement :

- l'arrêté du 2 août 1963, « APPROBATION DE MODIFICATIONS APPORTEES AU REGLEMENT DE LA SECTION
  PROFESSIONNELLE DES NOTAIRES » (JORFTEXT000000437564, JO du 15 août 1963), titre seul ;
- l'arrêté du 20 novembre 1964, « APPROBATION DES MODIFICATIONS APPORTEES A L'ART. 8 ET DE
  L'ADJONCTION DES ART. 20-BIS,50 A 55 DU REGLEMENT DE LA SECTION PROFESSIONNELLE DES NOTAIRES »
  (JORFTEXT000000620399, JO du 1er décembre 1964), titre seul ;
- l'arrêté du 21 février 2001 (JORFTEXT000000753863, JO du 24 février 2001) : « sont approuvées
  telles qu'elles sont annexées (1) au présent arrêté les modifications apportées au règlement
  de la section professionnelle des notaires relatives au régime d'assurance vieillesse
  complémentaire (art. 30, 36, 39, 40, 41 et 47) » (JORFARTI000002396641), « (1) Cet arrêté
  accompagné de ses annexes paraîtra dans un prochain Bulletin officiel » (JORFARTI000001924450).

Et l'arrêté du 16 décembre 1996, que la fiche nomme parmi ceux dont l'index n'a que le titre,
porte deux articles, dont « Nota. - L'arrêté du 16 décembre 1996 sera publié intégralement au
Bulletin officiel no 97-03 » (JORFARTI000002135074). Les textes au seul Bulletin officiel sont
donc cinq — 1980, avril 1983, 1990, 1996 (no 97-03), 2001 —, quand l'hypothèse de
`reglement_d_avant_2005`, son approximation, son « à relire » et la note disent « Trois ».
Aucun ne se lit : la version reste supposée, aucun chiffre ne bouge. Hors de l'âge, deux décrets
du même genre que ceux que la fiche range sans effet ne sont pas nommés : le n° 83-519 (la
classe d'office, article 2 du décret n° 49-578) et le n° 2001-179 (sept classes de cotisation
et leurs points).

Depuis 2004, la liste est complète : la mention de 2004, 2008, 2013, 2017, 2023, 2026, et rien
après le 17 juillet 2026 ; le seul rectificatif des arrêtés du 10 juillet 2026
(JORFARTI000054642802) vise les médecins.

### Les citations, les dates, le droit commun : exacts

Les douze citations des versions se trouvent, morceau par morceau, dans le texte qu'elles
nomment. Publications : 4 février 2005, 8 mars 2008, 27 décembre 2013, 21 juin 2017,
28 décembre 2023, 17 juillet 2026 ; l'arrêté de 2013 « prend effet au 1er janvier 2014 », celui
de 2023 « entrent en vigueur le 1er janvier 2024 » ; ceux de 2008, 2017 et 2026 ne fixent pas de
date (l'article 2 de 2026 : « Le présent arrêté sera publié au Journal officiel de la République
française. »), d'où le lendemain : 9 mars 2008, 22 juin 2017, 18 juillet 2026. Le décret
n° 2026-418, article 2, 6°, a), se lit tel que cité, la citation s'arrêtant avant « après avis
de la Caisse nationale d'assurance vieillesse des professions libérales », sans en changer le
sens ; son article 30 : « Le présent décret entre en vigueur le 1 er juillet 2026. » Au code :
D. 161-2-1-9 (LEGIARTI000025089933), « Soixante et un ans et sept mois pour les assurés nés en
1954 », et depuis le 1er septembre 2023 (LEGIARTI000047634502), « Soixante-deux ans pour les
assurés nés entre le 1er janvier 1955 et le 31 août 1961 inclus » ; L. 161-17-2
(LEGIARTI000051289659) fixe au premier alinéa « soixante-quatre ans », et L. 351-8, 1°
(LEGIARTI000047452736, LEGIARTI000051289852), « l'âge prévu au premier alinéa de l'article
L. 161-17-2 augmenté de trois années » : 67 ans pour toute génération.

### Les cas : refaits à la main, rendus par les deux moteurs

| Cas | À la main | Les deux moteurs |
|---|---|---|
| né le 10/03/1954, 62 ans | 61 a 7 m + 24 mois : le 10/10/2017, pension le 1/11/2017 ; taux plein le 10/10/2022 ; 4 a 11 m 9 j, 20 trimestres | ouverture 2017-11-01, 0,7500 |
| né le 10/03/1950, 67 ans, le 1/04/2017 | 2 a 22 j après 65 ans, 8 × 0,5 % | 1,0400 |
| né le 10/03/1957, 68 ans, le 1/04/2025 | 1 a 22 j après 67 ans, 4 × 1 % | 1,0400 |
| né le 10/03/1956, 62 ans | 64 ans, le 1/04/2020 ; 4 a 11 m 9 j avant 69 ans | ouverture 2020-04-01, 0,7500 |
| né le 10/03/1961, 62 ans | 64 ans, le 1/04/2025 ; 2 a 11 m 9 j avant 67 ans, 12 trimestres | ouverture 2025-04-01, 0,8500, 14 679,08 € de 2025 |
| né le 10/09/1953, 61 ans, le 1/10/2014 | 3 a 11 m 9 j avant 65 ans, 16 trimestres entamés | 0,8000, 8 395,6229 € |
| né le 10/03/1948, 60 ans, le 1/04/2008 | 8 trimestres manquants selon le modèle (version supposée), 8 × 1,25 % | 0,9000, 6 979,8307 € |
| né le 10/03/1961, 64 ans, le 1/04/2025 | 12 trimestres | 0,8500, 15 449,4026 € |

Sous `PRESOMPTIONS_DECALEES=1`, les mêmes dates, coefficients et montants.

### Le passage de 2024 : l'erreur est prouvée ; une précision

L'arrêté du 29 novembre 2023, lu en entier (article 1er, article 2, annexe, I à IV), n'a aucune
disposition transitoire : ni « pensions prenant effet », ni réserve pour qui a cessé d'exercer
avant ; « Les dispositions du présent arrêté entrent en vigueur le 1er janvier 2024. »
L'article 19 de 2017, qu'il ne touche pas, fixe le droit « au premier jour du mois civil qui suit
la date de fin d'exercice ou la date souhaitée par l'affilié ». La lecture contraire — l'âge des
statuts du jour de la cessation — n'a pas de texte : elle est intenable, l'erreur bien
déclarée. Le 1er janvier 2024, né le 10 mars 1961, à 62 ans, 9 mois et 22 jours ; 4 ans, 2 mois
et 9 jours avant 67 ans : 17 trimestres entamés, 0,7875 ; 16 entiers, 0,80. Les montants sont
exacts (voir plus bas les centimes). **Précision** : la liquidation au 1er avril 2025, à 0,85,
reste une « date souhaitée » que les statuts permettent ; ce que le modèle a de faux est la date
d'ouverture, quinze mois tenus fermés. Les « 1 079,34 € par an de trop » comparent deux dates de
liquidation et ne valent que dans sa règle, servir chaque caisse dès son ouverture. Les quinze
mois sont comptés aux valeurs de 2025, comme la note le dit.

### L'âge d'avant 2014 : le non-tranché est fondé ; deux phrases à reprendre (faible)

1. « le premier alinéa de l'article 15, le seul que l'arrêté de 2013 laisse voir, n'excepte que
   l'inapte » (approximation de `statuts_de_2005`) : l'arrêté ne laisse pas voir l'ancien
   alinéa, il le récrit — « le dixième alinéa est ainsi rédigé : « Toutefois, le conseil
   d'administration peut accorder [...] » ». Ce qu'on lit est sa rédaction de 2014 ; que
   l'ancien visât l'inapte se déduit des onzième et douzième alinéas, que l'arrêté modifie par
   mots (« d'un médecin agréé par la caisse », « 2° Une attestation du président de la
   chambre »). De même, « L'article 16 est ainsi rédigé » : l'ancien article 16, non lu, a pu
   porter une liquidation anticipée. La lecture du modèle en reçoit un appui que la fiche ne
   nomme pas.
2. « rien ne dit que la phrase date de 2005 » (même approximation ; l'hypothèse : « ni rien qui
   dise si ces phrases datent de 2005 ») : de l'arrêté du 28 décembre 2004 à celui du
   16 décembre 2013, l'index ne porte qu'une approbation de modifications de ces statuts, celle
   du 27 février 2008, qui ne récrit que l'article 20 (« L'article 20 des statuts annexés à
   l'arrêté du 28 décembre 2004 susvisé est rédigé comme suit »). Sauf une modification que le
   Journal officiel n'aurait pas mentionnée, la phrase de l'article 14 est celle des statuts de
   2005, et la seconde lecture vaut, si elle vaut, depuis le 1er janvier 2005.

Ni l'une ni l'autre ne tranche : le texte de 2005 reste à lire. Les montants sont exacts :
5 × 6 979,83 = 34 899,15 € ; 6 979,83 / 0,90 = 7 755,37 €, 775,54 € de plus.

### Le trimestre entamé, les 30 %, la date d'effet : conformes

- **Le trimestre entamé** : ni 2014 (« par trimestre séparant l'âge de l'affilié à la date de
  liquidation de l'âge du taux plein »), ni 2017, ni 2026 ne disent comment compter le trimestre
  incomplet, à la différence de la CARPIMKO (« Tout trimestre incomplet par rapport à l'âge de
  liquidation est considéré comme un trimestre d'anticipation »). Non-tranché fondé ;
  8 395,62 / 0,80 × 0,8125 = 8 526,80 €, 131,18 € de plus.
- **Les 30 % par enfant** : les rédactions de 2008, 2017 et 2026 citées sont exactes ; « droits
  contributifs [...] à l'exclusion de toute majoration, surcote ou accessoire de pension »
  (2026) ne dit rien de la décote : non-tranché fondé. 15 449,40 / 0,85 = 18 175,76 € ; 30 %,
  5 452,73 € ; 30 % de 15 449,40, 4 634,82 €.
- **La date d'effet** : 2017 et 2026, « au premier jour du mois civil qui suit la date de fin
  d'exercice ou la date souhaitée » ; le modèle sert au premier du mois qui suit l'âge
  (1er novembre 2017, 1er avril 2020, 1er avril 2025). Aucun écart, 0 €.

### Deux égalités au centime (faible)

- « 13 599,74 × 15 / 12 = 16 999,67 € » : 13 599,74 × 15 / 12 = 16 999,675, qui s'arrondit à
  16 999,68 au demi supérieur ; 16 999,67 est l'arrondi de la chaîne sans arrondi
  intermédiaire, 14 679,08 / 0,85 × 0,7875 × 15 / 12 = 16 999,6699. C'est le chiffre de tête
  de l'erreur déclarée (fiche, note, message de commit, bloc « Reprise »).
- « 13 815,60 €, 17 269,51 € » : 13 815,60 × 15 / 12 = 17 269,50 ; 17 269,51 est l'arrondi de
  la chaîne, 17 269,5059.

Toutes les autres égalités d'E5 tombent juste sur le papier : 13 599,74 ; 1 079,34 ; 13 815,60 ;
863,48 ; 8 526,80 ; 131,18 ; 34 899,15 ; 7 755,37 ; 775,54 ; 18 175,76 ; 5 452,73 ; 4 634,82.

## B. E4-bis, les chiffres neufs

### CAVP, la majoration des nés jusqu'au 30 juin 1951 : non-tranché fondé, 246,61 € exact

L'annexe de l'arrêté du 23 juin 2011 (JORFARTI000024270214), aux statuts du régime
complémentaire, article 12 modifié : « Cette majoration est égale à 0,5 % par trimestre. De
façon transitoire : ― les affiliés nés jusqu'au 31 décembre 1952 peuvent bénéficier d'une
majoration de leur pension de retraite dans les mêmes conditions, mais uniquement jusqu'à l'âge
permettant d'obtenir une retraite entière augmenté d'un an », l'âge étant « 65 ans pour les
affiliés nés jusqu'au 31 décembre 1952 ». Le tableau annexé à l'article 15 : « 1. Pour les
assurés nés avant le 30 juin 1951 inclus [...] 65 0,00 % Pas de majoration de pension pour un
départ après 65 ans » ; « 2. Pour les assurés nés entre le 1er juillet 1951 et le 31 décembre
1952 inclus [...] 66 2,00 % Pas de majoration de pension pour un départ après 66 ans ». Le
règlement de 2026 (JORFARTI000054436087) : « les affiliés nés avant le 30 juin 1951 inclus ne
bénéficient pas d'une majoration de leur pension de retraite pour un départ après 65 ans ». La
contradiction de 2011 à 2026 est réelle. Le tableau, qui sépare exprès les deux cohortes, est
un argument pour sa lecture que la note ne cite pas ; l'article 12, qui crée la majoration,
nomme les nés jusqu'en 1952 sans exception. Aucune n'est intenable : non-tranché fondé.
Né le 10 mars 1950 : 65 ans le 10 mars 2015, 66 ans le 10 mars 2016, quatre trimestres au
1er avril 2016, 2 % ; les deux moteurs servent 12 330,5476 € sans majoration ;
12 330,55 × 1,02 = 12 577,16 €, 246,61 € de plus.

### CAVP, les arrêtés de 1956 et 1989 : conformes

« Arrêté du 17 septembre 1956 APPROBATION DE DISPOSITIONS STATUTAIRES COMPLETANT LE REGLEMENT
DE LA SECTION PROFESSIONNELLE DES PHARMACIENS » (JORFTEXT000000281088), titre seul ; l'arrêté du
6 avril 1989 (JORFTEXT000000318409) : « L'ARRETE SERA PUBLIE INTEGRALEMENT AU BULLETIN OFFICIEL
DU MINISTERE DE LA SOLIDARITE,DE LA SANTE ET DE LA PROTECTION SOCIALE N0 8920. » Les résumés de
1977 (« MODIFICATION DES ART. 16, 2, 6 BIS ET 10 DES STATUTS. ») et de 1988 (« ENTREE EN
VIGUEUR: 01-01-1989. ») sont exacts.

### CARPIMKO, « Âge du taux plein » : citée, non-tranché fondé

L'annexe de l'arrêté du 27 décembre 2023 (JORFARTI000048880643, JO du 9 janvier 2024, en vigueur
le 10), 6° : « L'article 12 quater est remplacé [...] Âge du taux plein 65 ans 65 ans 4 mois 65
ans 8 mois 66 ans 66 ans 4 mois 66 ans 8 mois 67 ans » ; le règlement de 2026
(JORFARTI000054435915), article 6, « Age du taux plein », article 5, ses deux phrases, article
4, « l'âge du taux plein sans condition » ; 2015 (JORFARTI000031255547), « Age prévu à
l'article 11.1 » : tout se trouve. Le même règlement donne le taux plein avant l'âge de la table
(article 3, 2) : « avant l'âge mentionné au 1 au profit des assurés remplissant les conditions
[...] sans abattement »), nomme « Age du taux plein » la ligne de la table et dit « sans
condition » quand il la vise à l'article 4 : l'expression porte les deux sens. Non-tranché
fondé. Né le 10 novembre 1959, à 67 ans : 66 ans et 4 mois le 10 mars 2026, deux trimestres
civils entiers (avril à septembre) avant le 1er décembre 2026, 1,025 ; les deux moteurs servent
7 022,1918 €, 1,25 ; 7 022,19 / 1,25 × 1,025 = 5 758,20 €, 1 263,99 €.

### CARPIMKO, 136,90 € et 205,35 € : exacts ; l'écart d'un centime confirmé, et un second (faible)

Né le 10 décembre 1954, entré à 20 ans, à 62 ans : les deux moteurs, les deux modes de
présomptions, servent 5 681,234486 €, 1,0375.

| Égalité écrite | Sur le papier | Du montant servi |
|---|---|---|
| 5 681,23 / 1,0375 = 5 475,89 | 5 475,8843 → **5 475,88** | 5 475,8887 → 5 475,89 |
| 5 681,23 / 1,0375 × 1,0125 = 5 544,34 | 5 544,3335 → **5 544,33** | 5 544,3373 → 5 544,34 |
| 205,35 € | 5 681,23 − 5 475,88 = 205,35 ; mais 5 681,23 − 5 475,89 = 205,34 | 205,3458 → 205,35 |
| 136,90 € | 5 681,23 − 5 544,33 = 136,90 ; mais 5 681,23 − 5 544,34 = 136,89 | 136,8972 → 136,90 |

Les deux montants sont exacts, par les deux chemins. Les intermédiaires 5 475,89 et 5 544,34
sont ceux du montant non arrondi, écrits après un dividende arrondi : sur le papier, un centime
d'écart, et des différences qui ne tombent pas. « 205,35 € suppose 5 475,88 » n'est vrai que sur
le papier : 205,35 est aussi l'arrondi de la différence sans arrondi. Les lieux :
`carpimko_ages_2015`, approximations de l'âge de la génération 1955 (« 5 475,89 € sans
coefficient », « 5 544,34 € ») et de la majoration avant l'âge légal (« 5 681,23 / 1,0375 ×
1,0125 = 5 544,34 € », « 5 681,23 / 1,0375 = 5 475,89 € ») ; la note d'E4-bis, « Les calculs ».
4 818,78 € et 862,45 € tombent juste des deux façons.

## Les tests

`python -m pytest -m rapide` : 4 506 réussis, 6 sautés ; sous `PRESOMPTIONS_DECALEES=1` : 4 301
réussis, 211 sautés ; `tests/test_sections_juridiques.py`, `test_sections_liberales.py`,
`test_sections_sante.py` et `test_carte.py`, en entier, tous niveaux : 139 réussis, dont les
deux tests neufs d'E5. Aucun rouge.

## Ce que la relecture laisse

- **À la file E**, une session de retouches, sans règle neuve : dans `cprn_ages_decote_enfants`,
  nommer les arrêtés du 2 août 1963, du 20 novembre 1964 et du 21 février 2001, dire cinq textes
  au seul Bulletin officiel (1996, no 97-03 ; 2001), et les ajouter au « à relire » ; reprendre
  les deux phrases de l'âge d'avant 2014 ; écrire 16 999,68 € et 17 269,50 €, ou dire la chaîne
  sans arrondi ; dire que les 1 079,34 € valent dans la règle du modèle. Dans
  `carpimko_ages_2015` et ses notes à venir, 5 475,88 et 5 544,33, ou le montant servi
  5 681,2345 nommé.
- **Au propriétaire** : rien de neuf. L'erreur et les non-tranchés de la CPRN, les non-tranchés
  de la CAVP et de la CARPIMKO, tels qu'E5 et E4-bis les déclarent, sont confirmés ; leurs
  montants sont exacts, au centime d'écriture près dit ici.
