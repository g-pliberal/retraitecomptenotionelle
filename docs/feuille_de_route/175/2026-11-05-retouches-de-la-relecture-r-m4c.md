# Retouches de la relecture R-M4c : D. 721-11 ne dit pas « sans cotisation », l'effet du point non tranché, « au III ou IV »

Vague 7, le 5 novembre 2026. La relecture R-M4c
(`2026-11-04-relecture-taux-plein-parents-cavimac.md`, commit beec286) trouve le
taux plein à 65 ans des parents de trois enfants à la CAVIMAC conforme, avec trois
écarts faibles, sans valeur servie qui change. Cette note les corrige. La fiche
`data/reference/regles/taux_plein_a_soixante_cinq_ans.yaml` change de texte ; aucune
valeur, aucune règle, aucune donnée, aucun test ne change.

**Les textes, rouverts pour cette note** : l'index LEGI, à jour au 4 novembre 2026
(`python scripts/fetch/dila_index.py legi --recuperer`, puis `--mettre-a-jour`, qui
applique l'incrément LEGI_20261104-214059), lu par `dila_cherche.py legi --num … --le …`.

## 1. D. 721-11 ne dit pas « sans cotisation »

Ce que D. 721-11 (LEGIARTI000006739120, du 13 novembre 1988 au 21 juin 1998, en
vigueur au 31 décembre 1997) dit, mot pour mot : « Sous réserve qu'à la date d'entrée en
jouissance de la pension l'assuré soit à jour de ses cotisations personnelles, sont
prises en compte pour l'ouverture du droit et le calcul de la pension, les périodes
d'exercice d'activités mentionnées à l'article L. 721-1 accomplies antérieurement au 1er
janvier 1979 en qualité de ministre d'un culte ou de membre d'une congrégation ou
collectivité religieuse […] lorsque ces périodes ne sont pas validées par un autre régime
obligatoire d'assurance vieillesse de base ». Il prend ces périodes en compte ; il ne dit
pas qu'elles le sont sans cotisation.

Les textes que la relecture désigne, lus ici dans l'index :

| texte | rédaction | ce qu'il dit, mot pour mot |
|---|---|---|
| L. 721-3 du code de la sécurité sociale (1985) | LEGIARTI000006744302, du 21 décembre 1985 au 23 juillet 1993 ; LEGIARTI000006744303, du 23 juillet 1993 au 23 décembre 1997 (celle du 31 décembre 1997) | « Le financement de la pension de vieillesse instituée par le présent chapitre est intégralement assuré : 1°) par des cotisations forfaitaires à la charge des assurés » (la seconde rédaction ajoute un 5°) |
| L. 721-6 (1985) | LEGIARTI000006744307, du 21 décembre 1985 au 23 décembre 1997 | « Un décret fixera le mode de calcul de la pension et les conditions dans lesquelles les périodes d'activité antérieures à la création du régime seront prises en compte pour le calcul de la pension. » |
| L. 382-25, I, 1° | LEGIARTI000006742803, du 20 décembre 2005 au 14 juin 2018 | « Des cotisations à la charge des assurés, assises sur une base forfaitaire » (déjà citée par la fiche) |

**Ce que ces textes prouvent, et ce qu'ils ne prouvent pas.** L. 721-3 prouve que, du
21 décembre 1985 au 23 décembre 1997, les cotisations forfaitaires des assurés
finançaient la pension ; L. 382-25 le prouve depuis le 20 décembre 2005 ; L. 721-6
renvoie à un décret la prise en compte des « périodes d'activité antérieures à la
création du régime ». Aucun de ces textes, ni D. 721-11, n'écrit que les années
d'avant 1979 n'ont pas été cotisées : c'est la lecture du modèle, que la fiche garde,
et dit comme telle. **L'index n'a aucune rédaction de L. 721-3 d'avant le 21 décembre
1985** (la première est celle du code de 1985) : les années 1979 à 1985 ne reposent, à
l'index, que sur la date de D. 721-11. La relecture écrit « la rédaction de L. 721-3 en
vigueur de 1979 à 1997 » : à l'index, c'est de 1985 à 1997.

**Dans la fiche** : la phrase du droit de la version de 2011 ne dit plus « sans
cotisation (D. 721-11) » ; l'écart de l'approximation de la CAVIMAC cite D. 721-11 mot
pour mot, dit qu'il ne porte pas « sans cotisation », cite L. 721-3 et L. 721-6, avec
L. 382-25, et dit le trou d'avant 1985 ; trois entrées citées s'ajoutent à la version
(LEGIARTI000006744302, LEGIARTI000006744303, LEGIARTI000006744307), chacune avec sa
citation, relue mot pour mot dans l'index ; une lecture du 5 novembre s'ajoute aux
`sources`, et une entrée à l'`historique`. Le cliquet des rédactions sans statut
(`data/reference/textes/perimetre.yaml`) passe de 9 334 à 9 332, comme
`tests/test_textes.py` le demande : deux des trois rédactions n'avaient aucun statut.

## 2. L'effet chiffré du point non tranché

La fiche écrivait, de l'effet, que la ministre du culte de la saisie serait « décotée de
5 trimestres : 46,875 % au lieu de 50 % après 1997, et, avant 1998, 4 635,65 × 11 / 165
× 0,9375 = 289,73 € ». Les deux premiers chiffres sont l'effet du point. Le troisième
est ce que le modèle servirait, non ce que le texte donnerait : à soixante-cinq ans,
D. 721-6 de 1997 alloue la fraction d'avant 1998 à tout assuré (« L'âge à partir duquel
est allouée la pension de vieillesse […] est fixé à soixante-cinq ans »), et le V du
décret n° 2006-1325, article 2, la majore, que la mesure des parents s'applique ou non ;
par le texte, cette fraction resterait à 7 615,94 × 11 / 165 = **507,73 €**, et seule la
fraction d'après 1997 passerait à 46,875 %. Le calcul de 289,73 € est exact (4 635,65 ×
11 / 165 = 309,04 ; × 0,9375 = 289,73), mais il mêle l'écart déjà déclaré de
`cultes_fractions_de_pension` (« le décret garde soixante-cinq ans (D. 721-6 de 1997)
pour la fraction d'avant 1998 »). **La fiche le dit maintenant** : 289,73 € au modèle,
507,73 € au texte de D. 721-6, et le reste à la file des cultes. Non tranché ici :
laquelle des deux valeurs la caisse sert à qui part avant l'âge de sa génération sans la
mesure des parents.

## 3. « Le III ou IV » est « au III ou IV »

La note de M4 (`2026-11-03-taux-plein-parents-de-trois-enfants-cavimac.md`, tableau des
textes, ligne de R. 351-27) écrit « le III ou IV de l'article 20 ». R. 351-27
(LEGIARTI000024113020, du 3 juin 2011 au 1er septembre 2023, relu ici) écrit : « s'ils
remplissent les conditions prévues au 1° bis ou 1° ter de l'article L. 351-8 ou **au** III
ou IV de l'article 20 de la loi n° 2010-1330 du 9 novembre 2010 portant réforme des
retraites ». La forme « le III ou IV » n'est dans aucun texte lu ; ni la fiche ni le test
ne la citent. La note de M4 est un récit et ne se récrit pas : un renvoi daté, à son
bout, vient ici.

## Signalé, non fait (code, test, donnée : hors de cette tâche)

La même lecture, « sans cotisation » ou « gratuitement » attribuée à D. 721-11, est
encore écrite dans des fichiers que cette tâche ne touche pas :

- `src/retraite_notionnelle/droit/categories.py` (l. 172 : « que la CAVIMAC prend en
  compte sans cotisation (D. 721-11 du code de 1985 ») et `droit/cultes.py` (l. 13 et 51 :
  « validées gratuitement (D. 721-11 ; décret n° 79-607, art. 42) ») : des commentaires ;
- `tests/test_taux_plein_a_soixante_cinq_ans.py` (l. 386 à 396, la docstring de
  `test_les_annees_cultuelles_d_avant_1979_ne_sont_pas_cotisees` : « sans qu'aucune
  cotisation l'ait portée (D. 721-11 du code de 1985 »), dont le nom et la valeur
  attendue ne changent pas ;
- `data/reference/legislation/affiliations.yaml` (l. 46 et 1297 à 1299) et la fiche
  `cultes_fractions_de_pension` (l. 7 : « gratuitement »). Le statut cite, pour « la
  CAVIMAC les valide gratuitement », la page de la CAVIMAC sur la retraite de base et la
  réponse ministérielle au Sénat du 16 janvier 2008, **non rouvertes ici** : si elles le
  disent, la preuve existe, mais ailleurs que dans D. 721-11 ; le décret n° 79-607,
  art. 42, qu'il cite aussi, n'a pas été relu non plus. À la file des cultes.

Aucun texte de droit nouveau n'est écrit en règle : l'entrée du journal de veille de
cette note (`data/reference/legislation/journal_de_veille/2026-11-05-action-175-retouches-de-la-relecture-r-m4c.yaml`)
dit les textes relus.
