# La part de TVA gardée sortie du partage des impôts abandonnés

*Le 21 novembre 2026, une session corrige un double compte que la relecture
critique du dépôt avait signalé, sans le vérifier, dans un autre fil.*

**Le défaut.** `restitution.py` et son portage `restitution.js` coupaient
en deux le poste « impôts et taxes affectés » du COR en entier : 64,0 Md€ en
2026. Or ce poste compte la TVA reversée à l'Agirc-Arrco (tableau 2.2 du
rapport du COR de 2026). La proposition garde cette TVA (décision 79), et
`cout.py` la lui rend à compter de la bascule, sur la ligne
`impots_tva_gardee`. La recette de 10,9 Md€ était donc à la fois gardée par
la retraite et partagée entre les salaires et la dette.

**La décision.** Le 21 novembre 2026, le propriétaire a choisi de partager
moitié pour les salaires, moitié pour la dette, ce qui est vraiment
abandonné. Il a écarté deux autres options : garder 32 Md€ aux salaires et
réduire la part de la dette, ou garder 32 et 32 en faisant payer l'écart par
le budget de l'État.

**Ce qui change, en 2026, au PIB de 2025.**

| | Avant | Après |
|---|---|---|
| Vraiment abandonné | 64,0 Md€ | 53,1 Md€ |
| Rendu aux salaires | 32,0 | 26,6 |
| dont taxe sur les salaires et forfait social | 17,8 | 17,8 |
| Baisse de la CSG d'activité | 1,12 point | 0,69 point |
| Dette éteinte | 32,0 | 26,6 |

Prenons l'exemple de l'agent non titulaire de la page Simuler. Sous la
proposition, son net augmentait de 151 € par mois ; il augmente maintenant de
134 €. Le gain net de la sonde du pont passe de 25,5 % à 24,9 %. Les pensions
et le coût ne bougent pas.

**Le code.**
- La part gardée se retranche du poste avant le partage, à compter de la
  bascule. Le réglage `tva_des_retraites_gardee` la commande.
- Cette part est rapportée au PIB que le coût projette, c'est-à-dire celui
  de 2025 que fait croître la variation nominale. Elle égale ainsi au bit
  près le `tva_gardee` du solde.
- Le paquet porte cette part, de 2024 à 2027, pour le portage.
- Les deux impôts supprimés restent une part du poste brut.
- La fiche de paie passe la bascule et le réglage, dans les deux langages.
- L'accueil affiche une décimale dès qu'une part est gardée, comme la
  relecture l'a demandé, afin que 53,1 = 26,6 + 26,6.

**Ce qui reste ouvert.** La contribution tarifaire d'acheminement (1,7 Md€),
que le poste compte aussi, doit-elle sortir du partage ? C'est au
propriétaire d'en décider ; la question lui est soumise à part.
