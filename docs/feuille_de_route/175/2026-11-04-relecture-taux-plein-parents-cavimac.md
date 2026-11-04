# Relecture du taux plein des parents de trois enfants à la CAVIMAC

File R-M4c de la sixième vague, le 4 novembre 2026 : relecture indépendante des commits
8eef32f et a45e7e5 (file M4, note
`2026-11-03-taux-plein-parents-de-trois-enfants-cavimac.md`), « le taux plein à 65 ans des
parents de trois enfants à la CAVIMAC et aux points d'avant 1973 ». Je n'ai rien repris de
M4 ni de ma mémoire. L'index de la DILA a été récupéré dans la session : LEGI à jour au
3 novembre 2026 après l'incrément LEGI_20261103-214151, JORF à jour au 3 novembre. Chaque
texte a été ouvert dans sa rédaction en vigueur aux dates qui comptent. Le barème du
minimum de la Cnav a été relu par son API le jour même. Les 68 fragments cités entre « »
dans les entrées de la fiche `taux_plein_a_soixante_cinq_ans`, dont les 16 que M4 ajoute,
ont été cherchés par un script dans le texte de l'index. Deux fragments altérés à dessein
(« soixante-six ans », « 1,30 % ») y sont bien signalés absents. Chaque valeur attendue a
été refaite par un calcul qui n'appelle pas le modèle. Je n'ai rien modifié : ni règle, ni
donnée, ni test, ni fiche.

**Verdict : conforme, avec trois écarts faibles, de preuve ou de forme, sans effet sur
aucune valeur servie.** Le renvoi de L. 382-27 à L. 351-8 et le II de l'article 3 du
décret n° 73-937 portent bien la mesure aux cultes et aux points d'avant 1973. La
correction des deux années d'avant la naissance suit le décret n° 2011-620 et ne déplace
que les cultes d'avant 1979. Je refais toutes les valeurs à la main, et les deux moteurs
les rendent. Ce que les textes ne tranchent pas est déclaré, et les deux écarts de
R-M4-bis sont corrigés.

## 1. Les sources, mot pour mot

- **L. 382-27** (LEGIARTI000019959668, du 19 décembre 2008 au 1er septembre 2023, en vigueur
  aux effets de 2011 à 2023) : « Les personnes qui exercent ou qui ont exercé des activités
  mentionnées à l'article L. 382-15 reçoivent une pension de vieillesse dans les conditions
  définies aux articles [...] L. 351-8 à L. 351-13 », puis « Les prestations afférentes
  aux périodes d'assurance antérieures au 1er janvier 1998 sont indiquées dans les
  conditions législatives et réglementaires en vigueur au 31 décembre 1997 sous réserve
  d'adaptation par décret ». La citation de la fiche est exacte, « indiquées » compris :
  c'est le mot de l'index. Conforme.
- **Le renvoi couvre-t-il le cas ?** Oui. Le IV de l'article 20 de la loi n° 2010-1330
  (LEGIARTI000023023835) est la mesure des parents : « l'âge mentionné au 1° dudit article
  est fixé à soixante-cinq ans pour les assurés nés entre le 1er juillet 1951 et le 31
  décembre 1955 inclus ». L'article dit aussi : « Le présent article est applicable dans
  tous les régimes obligatoires de retraite auxquels s'appliquent les dispositions de
  l'article L. 351-8 du code de la sécurité sociale ». L. 382-27 applique L. 351-8 aux
  cultes. Conforme.
- **R. 351-27** (LEGIARTI000024113020, du 3 juin 2011 au 1er septembre 2023) : « Pour
  l'application du deuxième alinéa de l'article L. 351-1 et de l'article L. 351-8 » ; la
  minoration se compte jusqu'au « soixante-cinquième anniversaire » de qui remplit les
  conditions « au III ou IV de l'article 20 » ; « 1,25 % pour l'assuré né après 1952 ».
  Conforme. *Écart faible de forme, dans la note de M4 seulement* : son tableau cite
  « le III ou IV de l'article 20 », quand le texte porte « au III ou IV ». La fiche et le
  test ne le citent pas.
- **R. 351-6** (LEGIARTI000006749349, du 27 avril 2007 au 1er janvier 2026) : la durée
  maximum est « celle prévue au troisième alinéa de l'article L. 351-1 ». **Décret
  n° 2010-1734, article 9** (LEGIARTI000023383430) : « 165 trimestres pour les assurés nés
  en 1953 et 1954 ». Conforme.
- **Décret n° 2006-1325, article 2** (LEGIARTI000023397816, pour les pensions prenant effet
  à compter du 1er juillet 2011, sans rédaction plus récente dans l'index ; avant elle,
  LEGIARTI000006256155 et LEGIARTI000021763033). Les quatre fragments cités (I ; II ; V ;
  e) sont exacts. Le II minore la pension d'avant l'âge par « le coefficient de minoration
  fixé au 2° du I et au II de l'article R. 351-27 ». Le III réduit le maximum « au prorata
  du rapport entre sa durée d'assurance et cette durée maximale » de R. 351-6. Le V et le
  V bis majorent la fraction d'avant 1998 de qui « remplissent les conditions prévues à
  l'article D. 721-6 » ou a la durée du I. Le V bis vise « le minimum de pension, non
  majoré », au prorata des trimestres d'avant 1979. Conforme. Le V vise, lui, « le minimum
  de pension majoré au titre des périodes ayant donné lieu à cotisations ». Le modèle ne
  prend ce minimum majoré qu'à 120 trimestres cotisés, comme la caisse. C'est une
  approximation déjà déclarée par la fiche `cultes_fractions_de_pension`
  (« suppose cent vingt trimestres cotisés tous régimes, comme la caisse l'écrit ») ; M4
  la renvoie à la file des cultes.
- **D. 721-6 du code de 1985** (LEGIARTI000006738898, du 21 décembre 1985 au 26 février
  2004, celle du 31 décembre 1997) : « fixé à soixante-cinq ans ». Conforme.
- **D. 721-11 du code de 1985** (LEGIARTI000006739120, du 13 novembre 1988 au 21 juin
  1998) : la citation est exacte. *Écart faible de preuve.* L'article ne dit pas « sans
  cotisation » : il dit que les périodes d'avant 1979 « sont prises en compte », sous
  réserve d'être « à jour de ses cotisations personnelles ». Que rien n'ait été cotisé
  pour elles, d'autres textes le disent. L. 721-6 du code de 1985 (LEGIARTI000006744307)
  renvoie à un décret « les conditions dans lesquelles les périodes d'activité antérieures
  à la création du régime seront prises en compte ». L. 721-3, dans ses rédactions de 1985
  à 2005 (LEGIARTI000006744302 à LEGIARTI000006744305), finance le régime par des
  « cotisations forfaitaires à la charge des assurés », puis des « cotisations à la charge
  des assurés ». La fiche et le test prouvent les cotisations de 1979 et après par L.
  382-25 (LEGIARTI000006742803), dont la rédaction ne date que du 20 décembre 2005. Sa
  citation est exacte, mais la rédaction de L. 721-3 en vigueur de 1979 à 1997 est la
  preuve de ce temps-là. La conclusion tient.
- **Décret n° 73-937, article 3** (LEGIARTI000026474703, du 7 octobre 2012 au 1er septembre
  2023). Son II vise-t-il bien la mesure des parents ? Oui. Il compte la minoration
  jusqu'au « soixante-cinquième anniversaire s'ils remplissent les conditions prévues aux
  1° bis ou 1° ter de l'article L. 351-8 ou aux III ou IV de l'article 20 de la loi
  n° 2010-1330 », et le IV de l'article 20 est la mesure des parents. Il ajoute « Le plus
  petit de ces deux nombres est pris en considération » et « 1,25 % pour l'assuré né après
  1952 ». La rédaction précédente, LEGIARTI000006765819 (du 19 février 2004 au 7 octobre
  2012), comptait la minoration jusqu'au soixante-cinquième anniversaire de tous ; M4 la
  lit à l'année, et la fiche le déclare. Conforme.
- **Décret n° 2011-620, article 2** (LEGIARTI000024111672) : « Pour l'application du IV des
  articles 20 et 21 » ; huit trimestres au plus après la naissance ; huit au moins « au
  titre des deux années précédant l'année de la naissance », où « sont pris en compte les
  trimestres validés en contrepartie de cotisations à la charge de l'assuré ou au titre de
  périodes d'arrêt maladie, de maternité, de chômage, de formation ou de rééducation
  professionnelle » ; « huit trimestres » d'activité professionnelle. La notice
  (JORFTEXT000024110091) énumère ses « Publics concernés » sans les cultes. Aucun document
  du décret, dans l'index JORF, ne contient « culte », « cultes », « congrégation » ni
  « religieuses ». Conforme.
- **Les ouvriers de l'État** (décret n° 72-154, article 4) : la seconde phrase citée est
  celle de LEGIARTI000006769790 (du 16 décembre 1987 au 27 novembre 2004), que l'entrée
  annonce par « puis ». Elle y est mot pour mot. Conforme.
- **Le minimum** : le barème « Montant minimum de la retraite personnelle » de la Cnav, relu
  par son API le 4 novembre 2026, porte « 01/10/2017 7 615,94 € 634,66 € 8 322,13 €
  693,51 € Circulaire Cnav 2017/32 du 26/09/2017 », puis la ligne du 01/01/2019. Le minimum
  vaut donc 7 615,94 € à l'effet du 1er avril 2018. Conforme.

## 2. Les autres régimes

Le changement passe l'emploi des deux années d'avant la naissance par `ligne_cotisee`
(`ligneCotisee`), qui l'écarte dans deux cas.

- *L'année que tous ses régimes valident sans cotisation*
  (`Affiliations.validee_sans_cotisation`). Dans `affiliations.yaml`, seules les périodes
  des cultes d'avant 1979 ont `services_passes` sur tous leurs régimes (`cavimac`). Les
  périodes calédoniennes (1958-1960, 1961-1994) et de Saint-Pierre (1987) n'y mettent que
  leur complémentaire : elles restent cotisées.
- *La ligne qui n'est pas `cotise`*, c'est-à-dire sans revenu, ou exonérée. Dans
  `carriere.py`, `cotise` vaut pour tout emploi, et seule l'exonération des indépendants
  d'outre-mer (L. 756-3, « l'année ne lui ouvre aucun droit ») le retire. Une telle année
  n'est pas « en contrepartie de cotisations », et le texte l'écarte aussi.

Ni le salarié, ni le fonctionnaire, ni l'indépendant qui cotise ne bougent donc. Les tests
des fonctionnaires, des salariés agricoles, des artisans et des commerçants du même
fichier passent, et leurs valeurs (66,25 ; 65 ; 70,3125 % ; 46,875 % ; 47,5 % ; 44,375 %)
n'ont pas changé. Conforme.

## 3. Les valeurs refaites à la main

- *Cultes de bout en bout*. L'assurée est née le 15 mars 1953, salariée de 1971 à 1975 (20
  trimestres), ministre du culte de 1980 à 1987 (32 trimestres) et de 2005 à 2017 (52). Ses
  enfants sont nés en avril 1976, juin 1978 et juin 1980, et sa pension prend effet le 1er
  avril 2018. Pour l'enfant de 1976 : 8 trimestres cotisés en 1974 et 1975 ; 0 de 1976 à
  1978, au plus 8 ; 20 trimestres d'activité, au moins 8. Elle n'a aucun trimestre entre
  son effet et son soixante-cinquième anniversaire (le 15 mars 2018) : **50 %**. Avant
  1998, ses 32 trimestres sont tous cotisés de 1979 à 1997. Elle compte 104 trimestres
  cotisés, moins de 120, donc le minimum non majoré de la lecture déclarée. Le maximum
  au prorata, plus 100 % de l'écart au prorata, donne 7 615,94 × 32 / 165 = 243 710,08 /
  165 = **1 477,03 €**. Conforme.
- *Le cas témoin, deux enfants*. L'âge de la génération 1953 est de 61 ans et 2 mois
  (D. 161-2-1-9, 4°, LEGIARTI000025089933), plus cinq ans (L. 351-8, 1°,
  LEGIARTI000028498855) : 66 ans et 2 mois, le 15 mai 2019. Du 1er avril 2018 au 15 mai
  2019, il y a 13 mois et 14 jours, soit 4,49 trimestres, arrondis à **5**. Il lui en
  manque 61 pour la durée (165 − 104). 50 % × (1 − 5 × 1,25 %) = **46,875 %**. Conforme.
- *Les années d'avant 1979*. Ministre du culte de 1973 à 1979, puis de 2000 à 2017 ;
  enfants nés en avril 1980, juin 1984 et juin 1986. Pour l'enfant de 1980 : 0 trimestre
  pour 1978, sans cotisation, et 4 pour 1979, soit 4, moins de 8. Pour ceux de 1984 et
  1986 : 0. Elle est donc à l'âge de la génération, **66 ans et 2 mois**. Le témoin,
  ministre du culte jusqu'en 1980, enfants nés en avril 1981, juin 1984 et juin 1986 :
  8 trimestres cotisés en 1979 et 1980 ; 0 de 1981 à 1983 ; 8 au moins d'activité avant ;
  **65 ans**. Conforme.
- *La ministre du culte de la saisie*. Au culte dès le 15 mars 1979 (« debut » 26), sans
  activité de 1982 à 1999, enfants nés en avril 1982, juin 1984 et juin 1986. Pour l'enfant
  de 1982 : 8 trimestres en 1980 et 1981 ; 0 de 1982 à 1984 ; 3 + 4 + 4 = 11 trimestres
  d'activité, sous la lecture déclarée. Elle obtient **50 %**. Avant 1998 : 7 615,94 × 11 =
  83 775,34, divisé par 165 = **507,73 €**. La décomposition donne le même total :
  4 635,65 × 11 / 165 = 309,04 €, plus (7 615,94 − 4 635,65) × 11 / 165 = 198,69 €.
  Conforme. Le modèle compte 3 trimestres en 1979 pour une activité commencée le 15 mars.
  M4 le dit « sous la lecture du modèle », et ce décompte est antérieur à son travail.
- *Les points d'avant 1973*. Pour l'assurée de `REQUETE`, artisane ou commerçante, il y a 0
  trimestre de son effet à son soixante-cinquième anniversaire : **aucun coefficient**. Pour
  le témoin, deux enfants : 5 trimestres jusqu'à 66 ans et 2 mois, moins que ceux qui lui
  manquent pour la durée. 1 − 5 × 1,25 % = **0,9375**. Conforme.
- *L'effet déclaré du point non tranché* : 4 635,65 × 11 / 165 × 0,9375 = **289,73 €**, et
  46,875 %. Le calcul est exact. *Écart faible de forme.* Ce chiffre est ce que le modèle
  servirait, non ce que le texte donnerait. À soixante-cinq ans, D. 721-6 alloue la
  fraction d'avant 1998 à tout assuré, et le V la majore, que la mesure des parents
  s'applique ou non. Par le texte, cette fraction resterait donc à 507,73 € ; seule celle
  d'après 1997 passerait à 46,875 %. L'effet écrit mêle l'écart déjà déclaré de
  `cultes_fractions_de_pension`, sans le dire.

## 4. Les deux moteurs

- `python -m pytest tests/test_taux_plein_a_soixante_cinq_ans.py
  tests/test_regle_de_chacun.py` : 25 tests réussis. Les tests neufs passent par
  `droit_et_refait` et `servi_et_refait`, donc les deux moteurs rendent ces valeurs.
- `python -m pytest -m rapide` : 4 374 tests réussis, 6 ignorés et 13 échecs, tous dans
  `test_pages_en_dossier.py` (les pages toutes faites, rouges en local dès que `main`
  bouge).
- `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 175 tests réussis, 205 ignorés
  et les mêmes 13 échecs de `test_pages_en_dossier.py`, rien d'autre.
- Les fichiers qui lisent les fichiers touchés (`grep -l` : `test_taux_plein_par_categorie`,
  `test_textes`, qui tient le cliquet, `test_agirc_arrco_au_droit`, `test_jumeaux`,
  `test_carte`, `test_donnees`, `test_invalidite`, `test_reversion`, `test_simulateur`),
  les tests des cultes et du minimum contributif (`test_cultes`, `test_cultes_au_droit`,
  `test_cultes_smic_du_mois`, `test_part_minimum_contributif`) et les confrontations
  légères (`test_oracle`, `test_destinie`, `test_estimation_officielle`,
  `test_verification`) : 1 439 tests réussis, 1 ignoré.
- `python scripts/construire_donnees.py`, puis `git status` : aucun fichier suivi ne
  change ; le paquet se refait à l'octet.

## 5. Ce que le texte ne tranche pas, et R-M4-bis

- *L'activité cultuelle comme « activité professionnelle »* du 2° et du 3° du IV : c'est
  déclaré dans l'approximation de la version de 2011, avec ses textes, la lecture du modèle
  et son effet. Le test `test_l_activite_cultuelle_compte_comme_l_emploi` l'épingle.
  Conforme, sauf l'écart faible du point 3 sur l'effet chiffré.
- *La fraction d'avant 1998 à 65 ans, hors des parents*, décotée par le modèle : c'est
  déclaré dans `cultes_fractions_de_pension` (« le décret garde soixante-cinq ans (D. 721-6
  de 1997) pour la fraction d'avant 1998 »). Le cas témoin épingle la lecture du modèle
  (« décote 0.9375 »). Conforme. Le texte (D. 721-6, et le V) contredit cette valeur pour
  les générations nées depuis 1951 ; elle reste à mesurer et à trancher par la file des
  cultes, comme M4 l'écrit.
- *R-M4-bis, écart 1* : la fiche (approximation des fonctionnaires, et entrée
  LEGIARTI000006646773) et les deux commentaires du test disent « quatorze semaines
  jusqu'au 30 septembre 1978 », puis « seize dès le 1er octobre 1978 », pour la salariée.
  L. 331-4 cite la rédaction de 1985 (LEGIARTI000006742546, « vingt-six ou de vingt-huit
  semaines »). Corrigé.
- *R-M4-bis, écart 2* : la fiche cite la loi n° 84-53, article 57, 5°
  (LEGIARTI000006366816), la loi n° 86-33, article 41, 5° (LEGIARTI000006695883) et le
  décret n° 72-154, article 4 (LEGIARTI000006769789, LEGIARTI000006769790). Chaque citation
  se trouve mot pour mot dans l'index. Corrigé.
- *Le cliquet* `redactions_sans_statut` est abaissé à 9 340 : `tests/test_textes.py` le
  tient (point 4).

## Ce qui reste

Les trois écarts faibles vont à une file du modèle, sans valeur à changer. Ils portent
sur l'effet écrit du point non tranché (point 3) et sur la preuve des cotisations des
cultes de 1979 à 1997, où il faut citer L. 721-3 du code de 1985 avec L. 382-25 (point 1).
Le troisième, la citation « le III ou IV », est dans une note, qui est un récit et ne se
récrit pas. La file des cultes garde ce que M4 lui laisse : la fraction d'avant 1998 à 65
ans hors des parents, et le minimum majoré du V. Aucune question ne bloque.
