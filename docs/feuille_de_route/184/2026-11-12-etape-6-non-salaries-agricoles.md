# Étape 6, lot des non-salariés agricoles : treize rédactions lues, une qui change une règle

Le lot est fini le 12 novembre 2026 : ses sept fiches n'ont plus de rédaction
en vigueur ou à venir qu'elles n'aient lue. La consigne est la note
`2026-11-11-etape-6-passe-de-lecture.md`. Rien n'est porté au modèle : ni
`src/` ni `moteur/` ne sont touchés.

## Ce qui change une règle

Une seule rédaction, à écrire par l'étape que le propriétaire décidera.

- **D. 732-165 du code rural, I** (rédaction du décret n° 2024-688 du 5 juillet
  2024, LEGIARTI000049904700), **pour les cotisations des périodes courant
  depuis le 1er janvier 2026.** La cotisation de retraite complémentaire du
  chef d'exploitation a deux parts : 4 % de l'assiette relevée à 1 820 SMIC,
  comme avant, et une seconde part sur l'assiette, au taux qui croît avec
  elle — 1 % × A / (0,4 plafond) sous 40 % du plafond de la sécurité sociale,
  de 1 % à 1,3 % jusqu'à 60 %, de 1,3 % à 1,8 % jusqu'au plafond, de 1,8 % à
  3 % jusqu'à deux plafonds, 3 % au-delà. D. 732-155, que la fiche avait lu,
  tire depuis 2026 les points de « la cotisation acquittée », P = C /
  [(1 820 SMIC × T) / N], T étant le taux de 4 % et N 133 : la seconde part
  achète donc des points. Le moteur garde, pour les années depuis 2026, 4 % et
  133 points par 1 820 SMIC de revenu (`data/reference/regimes/msa_rco.yaml`,
  période ouverte en 2018). Posé à la main, à un plafond de revenu en 2026,
  48 060 € : la cotisation est de 5,8 %, 2 787,48 €, et non de 1 922,40 € ; les
  points, environ 424, et non 292. Sont touchés les points de complémentaire
  du scénario 1 pour les années depuis 2026, et la cotisation que reçoit le
  compte des scénarios rétroactifs. La MSA applique la seconde part (« COTISATION
  RCO COMPLEMENTAIRE », barème de 2026, lu) ; son barème ne dit rien des points :
  l'arrondi et l'année cotisée au prorata restent à lire. Le collaborateur et
  l'aide familial ne changent pas (4 % de 1 200 SMIC, 88 points). La fiche
  `assiette_minimale_agricole` le dit sous `sources.a_relire`, et range la
  rédaction sous `textes_a_rattacher`.

## Ce que chaque rédaction a reçu

Treize rédactions, dix-neuf lectures, toutes du code rural sauf la dernière.

| Rédaction | En vigueur | Fiche | Statut |
|---|---|---|---|
| L. 732-54-2 (LEGIARTI000051289516) | 2026-01-01 | `pension_majoree_reference` | citée par la version de 2026 |
| | | `majoration_retraite_proportionnelle` | sans effet |
| D. 732-109 (LEGIARTI000053365675) | 2026-01-01 | `pension_majoree_reference` | citée par la version de 2026 |
| L. 732-54-1 (LEGIARTI000051289521) | 2026-01-01 | les deux mêmes | sans effet : seule la note change |
| D. 732-115 (LEGIARTI000053365746) | 2026-01-01 | `majoration_retraite_proportionnelle` | sans effet |
| L. 732-54-4 (LEGIARTI000051289509) | 2026-01-01 | `majoration_retraite_proportionnelle` | sans effet |
| L. 732-41 (LEGIARTI000051289494) | 2026-01-01 | `majoration_retraite_proportionnelle` | sans effet |
| D. 732-166-5 (LEGIARTI000053365825) | 2026-01-01 | `complement_differentiel_rco` | citée par la version de 2026 |
| D. 732-76 (LEGIARTI000054059256) | 2026-05-09 | `retraite_proportionnelle_msa` | sans effet |
| D. 732-77 (LEGIARTI000053365517) | 2026-01-01 | `retraite_proportionnelle_msa`, `cotisation_vieillesse_agricole_avant_2003` | sans effet |
| R. 732-69 (LEGIARTI000053337682) | 2026-01-01 | `retraite_proportionnelle_msa`, `pension_non_salaries_agricoles_2026` | sans effet |
| L. 731-42 (LEGIARTI000051284150) | 2025-02-28 | les deux mêmes | à rattacher |
| décret n° 2005-368, article 3 (LEGIARTI000006240373) | 2007-01-20 | les deux mêmes | sans effet |
| D. 732-165 (LEGIARTI000049904700) | 2024-07-07 | `assiette_minimale_agricole` | à rattacher : change une règle |

- *Les trois numéros réemployés.* Les décrets n° 2025-1409 et n° 2025-1410 ont
  abrogé R. 732-69 à D. 732-77 et rendu ces numéros à d'autres articles :
  R. 732-69 traite de l'inaptitude au travail, D. 732-76 et D. 732-77 du
  versement pour la retraite, que le modèle ne connaît pas. Le mot à mot de
  l'outil, qui compare deux articles sans rapport, n'y apprend rien : il a
  fallu lire les textes. Les règles d'avant — le barème des points au revenu
  cadastral, la majoration des points de 1952 à 1972 — restent celles des
  points d'avant 2016, par R. 732-66 et R. 732-67, que les fiches citent déjà.
  La rédaction de D. 732-76 du 1er janvier au 9 mai 2026 (LEGIARTI000053365504),
  qui ne diffère de la suivante que par sa note, est déclarée avec elle.
- *L'ancienne majoration.* La fiche `majoration_retraite_proportionnelle` est
  éteinte depuis 2009 : ses cinq rédactions de 2026 portent la pension majorée
  de référence, ou la réversion.
- *L. 732-41.* La loi n° 2025-199 en retire les trois alinéas de la pension de
  réversion du régime, et n'y laisse que le conjoint survivant qui continue
  l'exploitation. Le modèle ne connaît de cette réversion que celle que
  l'assuré déclare : aucune fiche n'en porte le calcul, et rien n'est à changer.
- *L. 731-42.* La rédaction de 2025 fonde la cotisation unique du chef et le
  forfait du collaborateur depuis 2026, que les deux fiches appliquaient déjà
  par D. 731-123 et D. 731-120.

## Ce que la lecture a corrigé

La version de septembre 2023 de `pension_majoree_reference` citait de
L. 732-54-2 (LEGIARTI000047453332) des mots qui sont ceux de la rédaction de
2026 : « revalorisé dans les conditions prévues au dernier alinéa de l'article
L. 351-10 ». Celle de 2023 écrit la règle en toutes lettres, « au 1er janvier
de chaque année, d'un taux au moins égal à l'évolution [...] du salaire
minimum de croissance ». Le dernier alinéa de L. 351-10 dit la même chose : le
montant ne bouge pas, la citation est remise à sa place.

## Le cliquet

Douze rédactions sans statut de moins : onze des treize rédactions du lot n'en
avaient aucun, et la rédaction intermédiaire de D. 732-76 non plus. Le compte
est refait après le lot de la fonction publique, poussé avant celui-ci : de
9 274 à 9 262.

## Deux pièges de l'outil, rencontrés

- Tout identifiant LEGIARTI écrit dans une entrée de `textes_sans_effet`, son
  motif compris, reçoit le statut « sans effet ». Citer dans un motif la
  rédaction précédente par son identifiant la déclare donc sans le vouloir :
  quatre l'étaient, dont une que la fiche applique, retirées avant le commit.
  Un motif nomme la rédaction de comparaison par sa date.
- Ce statut est global : une rédaction qu'une fiche déclare sans effet sur
  elle sort de la liste de toutes les fiches qui suivent le même article. Le
  lot l'a déclarée dans chacune. Un contrôle qui refuserait un identifiant
  étranger dans un motif, ou un statut tenu fiche par fiche, serait à décider.

## Ce qui reste

- La règle de D. 732-165, à écrire.
- Les rédactions passées que ces fiches n'ont pas lues, que la passe ne
  demandait pas : `python scripts/textes.py --non-lues <fiche> --toutes`.
