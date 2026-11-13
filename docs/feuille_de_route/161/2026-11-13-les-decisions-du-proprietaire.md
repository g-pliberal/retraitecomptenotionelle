# Les décisions du propriétaire du 13 novembre 2026 : le § 3 du README, la dernière année publiée d'un point, le relevé des périodes assimilées

**Ce qui est décidé.** La session exposait au propriétaire les questions
relevées dans `2026-11-13-les-regles-du-droit-a-la-facade.md`, « Ce qui
attend le propriétaire ». Il a répondu : « Je prends tes recommandations ».
La note de décision 0008
(`docs/decisions/0008-les-arbitrages-du-13-novembre.md`) les porte, avec
leurs raisons.

1. *Le § 3 du README* : le tableau reste à l'octet, mis en forme par la
   fabrique à partir de ce que le pont rend ; l'appel Python cède sa place à
   l'adresse du simulateur du site.
2. *La dernière année publiée d'un point* : demandée au pont, l'exemplaire
   Python retiré.
3. *Le défaut du relevé* : les périodes assimilées auront leurs lignes, avec
   leur fiche et leur version, après le retrait du moteur Python.

**Ce que la session lit de plus dans sa réponse.** Quatre des six petites
questions portaient une proposition : le code mort du portage retiré en une
session, hors les six fonctions réservées ; la liste de la clôture et son
test écrits avant le retrait ; le filtre de `jumeaux.py --couverture` élargi
aux tests qui passent par le pont ; l'option `--cas-types` gardée. La
session les tient pour prises avec les autres. C'est sa lecture : le
propriétaire ne les a pas nommées.

**Ce qui reste ouvert.**

- La phrase à afficher quand « Mon estimation retraite » ne se chiffre pas :
  les mots sont au propriétaire (`2026-11-12-le-pilote-les-erreurs-tues.md`).
- La moyenne de l'étude de la fusion, par période ou par régime
  (`2026-11-12-les-lignes-du-portage-sans-test.md`, point 4).
- Non exposées au propriétaire, faute d'urgence : lequel fait foi pour une
  fonction tenue des données, et les calculs qui restent des deux côtés
  (`2026-11-12-question-4-la-cloture.md`, points 3 et 4) ; les neuf
  fonctions que seuls des tests atteignent (`2026-11-12-le-code-mort.md`,
  point 2) ; les tests que le pont ne sait pas servir
  (`2026-11-12-les-lignes-du-portage-sans-test.md`, point 3).

**L'ordre de la suite**, une étape par session. Les trois premières sont
courtes et ne dépendent pas l'une de l'autre ; celles qui écrivent dans le
pont se mènent une à la fois.

| étape | ce qu'elle fait | sa consigne |
|---|---|---|
| la dernière année publiée d'un point | le portage exporte sa fonction, le pont la sert, la classe du coût la demande d'un lot | `2026-11-12-la-revalorisation-servie-dans-un-module-du-cout.md`, « Les quatre tables », voie 1 |
| le § 3 du README | la mise en forme du tableau passe à la fabrique, l'adresse du site remplace l'appel | `2026-11-12-lot-a-les-sondes-par-le-pont.md`, seconde voie |
| le code mort | une quarantaine d'unités du portage, moins de 200 lignes | `2026-11-12-le-code-mort.md` |
| les tests | les autres règles de `droit/` à la façade, puis les autres fichiers | `2026-11-13-les-regles-du-droit-a-la-facade.md`, « Ce qui reste » |
| les études | `scenarios_meres.py`, `cout_avantages.py --par-carriere`, puis deux non instruites | note de la question 3 |
| la liste de la clôture | les fonctions gardées des deux côtés, et leur test | note de la question 4 |
| le retrait | les règles du moteur Python, d'un bloc | inventaire du 9 novembre |
| les périodes assimilées | leurs lignes au relevé, en JavaScript seul | `2026-11-12-les-lignes-du-portage-sans-test.md`, « Le défaut » |

Aucun code ne change dans ce commit : la note de décision, cette note, le
bloc « Reprise » de l'action et celui de l'étape des lignes sans test.
