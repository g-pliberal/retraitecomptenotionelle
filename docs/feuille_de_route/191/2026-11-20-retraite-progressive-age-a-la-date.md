# La retraite progressive lit l'âge légal à la date de la demande

Le 20 novembre 2026, la session lève le doute que la note
`2026-11-19-etape-2-age-legal-le-moteur-lit-les-versions.md` laissait au
propriétaire, et que ses règles du même jour tranchent : ce qui s'écarte du
texte se corrige. L'étape s'est menée sur Fable 5.2.

**Lu**, par l'index LEGI. D. 161-2-24, du 1er septembre 2023 au 24 juillet
2025 (LEGIARTI000047961574) : l'âge de la retraite progressive « correspond à
l'âge défini par l'article L. 161-17-2 abaissé de deux ans ». L. 351-15, du
1er janvier 2022 au 1er septembre 2023 (LEGIARTI000044629917) : « l'âge prévu
au premier alinéa de l'article L. 351-1 diminué de deux années, sans pouvoir
être inférieur à soixante ans ». D. 161-2-1-9 : soixante-deux ans aux assurés
nés à compter de 1955 jusqu'au 1er septembre 2023 (LEGIARTI000025089933),
soixante-trois ans aux assurés nés en 1964 ensuite (LEGIARTI000047634502).

**Le défaut.** `progressive.ageMinimum` lisait l'âge légal de la personne,
celui de la version sous laquelle son droit à la retraite s'ouvrira. Une loi
postérieure à la demande refaisait ainsi le droit d'hier.

**La correction.** L'âge se lit dans la version de l'âge légal qui vaut à la
date d'effet de la demande (`agesOuverture.aLEffet`). Ni la fiche de l'âge
légal ni `regimes.js` ne bougent.

**Ce qui bouge**, salariée à 60 %, montants annuels :

| Née le | Demande au | Avant | Après |
|---|---|---|---|
| 15 mars 1962 | 1er avril 2022 | refusée, 60 ans et 6 mois exigés | ouverte à 60 ans, 8 509,98 € servis |
| 15 janvier 1964 | 1er novembre 2024 | ouverte à 60 ans et 9 mois, 9 635,58 € | refusée, 61 ans exigés |

Sont touchés les nés de septembre 1961 à 1963, pour une demande d'avant le
1er septembre 2023, et les nés de janvier à août 1964, pour une demande
d'avant le 1er septembre 2025. Un témoin bouge d'un champ :
`progressive_refusee_age`, âge exigé de 60,75 à 60, toujours refusée.

**Reste.** Les autres lecteurs de l'âge de la personne, à relire de même : la
substitution de la pension d'invalidité, la surcote depuis l'âge légal, la
bonification du cinquième. Aucun exemple publié de l'âge de la retraite
progressive par génération n'est au dépôt.
