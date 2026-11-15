# Les accords Agirc-Arrco dans la liste des textes

**La demande, le 15 novembre 2026.** Le propriétaire : « On peut ajouter les
accords agirc-arrco en parallèle ? » C'est le reste que laissaient l'étape 5
(`2026-11-11-etape-5-kali-dans-l-index.md`) et le bilan de la passe.

**Ce qui a été vérifié d'abord.** Ces accords, conclus entre partenaires
sociaux, ne sont pas dans LEGI, mais ils sont dans KALI, la base des
conventions collectives, que l'index du dépôt tient depuis le 11 novembre.
Chaque article de KALI y porte le titre de l'accord qui le range
(`convention`) : trois accords nationaux interprofessionnels portent le
régime, celui du 17 novembre 2017, qui le fonde (282 rédactions, avec ses
avenants n° 1 à 31 et les délibérations de son conseil), celui du 10 mai 2019
(25) et celui du 5 octobre 2023 (12). Les accords de l'Agirc (14 mars 1947)
et de l'Arrco (8 décembre 1961) n'y sont pas. Les accords de branche qui
nomment l'Agirc, pour la prévoyance des cadres, ont un numéro de convention
et sont écartés.

**Ce qui a été fait.** Chaque comportement par son test, vu rouge puis vert,
dans `tests/test_textes.py`.

- `perimetre.yaml` déclare une liste `accords`, chaque accord sous le titre
  que KALI lui donne et avec son pourquoi.
- `scripts/textes.py` : `selection_kali()` apporte tous les articles rangés
  sous un accord déclaré, chaque texte sous sa clé datée (`ani_2017_11_17`,
  `avenant_2024_12_18_n23` : quatre avenants du même jour se distinguent par
  leur numéro) ; un texte déjà inscrit garde la sienne. `--inscrire` lit
  l'index de KALI s'il est là (`--index-kali` pour un autre chemin) ; absent,
  il le dit, garde les rédactions de KALI telles quelles et la date de leur
  dernière lecture dans `inscription.yaml` (`kali:`).
- `noyau/textes.py` : une fiche donne son statut à une rédaction de KALI par
  son identifiant `KALIARTI…`, comme à un article de loi par son `LEGIARTI…`,
  et le contrôle de la liste admet l'un et l'autre.
- L'inscription, sur l'index de KALI à jour au 10 novembre 2026 à 21 h 31 :
  319 rédactions de 42 textes, toutes « à examiner », 54 sans numéro
  d'article (préambules, annexes, signataires). Le cliquet n'a pas bougé.
  L'inscription a aussi apporté 68 rédactions de LEGI que des fiches citent
  depuis le 11 novembre : elles n'ont pas été gardées, GitHub les inscrit le
  lundi 16.
- `docs/veille_droit.md` le dit.

**Les limites.** Aucune fiche ne cite encore un article de KALI : elles
citent l'accord entier (`KALITEXT…`). Les 319 rédactions restent donc « à
examiner » tant que les fiches de la retraite complémentaire ne les
rattachent pas. Le mot à mot de `--non-lues` ne lit que LEGI.

**Ce qui reste, et qui revient au propriétaire.**

- Que GitHub relise KALI chaque lundi : l'inscription tourne dans la course
  de LEGI, qui n'a pas l'index de KALI. La lui donner touche
  `.github/workflows/index-dila.yml`, une garde, qu'une session ne modifie
  qu'avec l'accord du propriétaire, demandé avant.
- Rattacher ces rédactions aux fiches de la retraite complémentaire, article
  par article.
