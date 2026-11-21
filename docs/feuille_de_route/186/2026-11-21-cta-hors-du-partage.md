# La CTA sortie du partage des impôts abandonnés

*Le 21 novembre 2026, une session poursuit la correction de la TVA gardée
(`2026-11-21-tva-gardee-hors-du-partage.md`). Le propriétaire a tranché que
la CTA, supprimée par la décision 88, sort elle aussi du partage.*

**Le défaut.** Le poste « impôts et taxes affectés » du COR compte la
contribution tarifaire d'acheminement : la CNIEG l'enregistre sous cette
rubrique. La décision 88 la supprime, si bien que les ménages la retrouvent
sur leurs factures d'énergie. La partager entre les salaires et la dette la
promettait donc une seconde fois.

**Le montant.** Le dépôt n'en avait pas. Les comptes de l'exercice 2025 de la
CNIEG (section « Contribution tarifaire », p. 46) donnent la CTA recouvrée
sur l'exercice courant : 2 161,8 M€ en 2025, 1 911,3 M€ en 2024. Ces chiffres
forment `data/reference/macro/cta_ieg.csv`. Le compte du COR garde en 2026
la part de PIB de 2025 de son poste des impôts (2,14 % les deux années) : il
compte donc la CTA d'avant la baisse de taux du 1er février 2026, que la
délibération 2026-14 de la CRE fixe à 555 M€ par an. Le partage retranche la
CTA telle que le poste la compte, celle de 2025 en part de PIB, reconduite.
Sans cela, ces 555 M€, qui n'existent plus, seraient partagés : c'est ce que
la relecture a relevé sur une première version, qui ne retirait que 1,6 Md€.

**Ce qui change, en 2026, au PIB de 2025.**

| | Avec la TVA seule | Avec la CTA aussi |
|---|---|---|
| Poste du COR | 64,0 Md€ | 64,0 Md€ |
| TVA gardée | 10,9 | 10,9 |
| CTA, au compte du COR | partagée | 2,2 |
| Partagé | 53,1 | 51,0 |
| Rendu aux salaires, autant à la dette | 26,6 | 25,5 |
| Baisse de la CSG d'activité | 0,69 point | 0,60 point |

L'agent non titulaire de la page Simuler gagne +131 € net par mois au lieu
de +134 €. La sonde du pont passe de 24,9 % à 24,7 %. Les pensions et le coût
ne bougent pas.

**Le code.** On retrouve la règle de la TVA gardée : `CtaSupprimee` dans
`restitution.py`, et le paquet porte `comptes_retraite.cta_supprimee`, que
lit le portage. Sur la page Coût, la note perd une incise sur la dette pour
tenir son budget de mots dépliés.

**Ce qui reste.** Le compte du COR ne ventile pas la CTA : que son poste
la tienne au niveau de 2025 se déduit de sa part de PIB, constante, et non
d'une ligne publiée. La CTA du gaz, 483 M€ en 2025, est comprise.
