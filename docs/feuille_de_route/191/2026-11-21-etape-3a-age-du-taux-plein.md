# Étape 3 de la note 0009, première session : l'âge du taux plein lu dans les versions de sa fiche

**Reprise, au 21 novembre 2026.** L'âge du taux plein se lit dans les cinq
versions de sa fiche, comme l'âge légal : le moteur ne lit plus de table par
génération. Les résultats ne bougent pas, sauf l'assuré né avant 1930, corrigé
au texte. Restent à l'étape 3, chacune dans une session neuve : la durée
requise, la carrière longue, la surcote. Deux questions attendent le
propriétaire, à la fin de cette note : l'âge opposé, après le 1er septembre
2023, à l'assuré né avant 1955 ; le minimum du parent de trois enfants, resté
dans le code. Commencer par lire la note de l'étape suivante dans le résumé
de la note de décision 0009.

Le 21 novembre 2026, la nuit, sur Opus 5.5, au choix du propriétaire, et non
sur Fable 5.2 que le dépôt règle pour le scénario 1 : un agent sur Fable 5.2
a été consulté sur la question de la date (voir plus bas). Trois commits de
code, un de documentation ; trente fichiers ; deux heures environ.

**La fiche** (`age_annulation_decote.yaml`). Cinq versions, choisies à la
date d'effet de la pension.

- Avant le 1er avril 1983, pas de règle commune (âge nul) : la période du
  régime garde sa valeur. Supposée.
- Du 1er avril 1983 (ordonnance n° 82-270, article 9) au 21 décembre 1985 :
  soixante-cinq ans. Supposée, aucun texte d'application relu.
- Du 21 décembre 1985 au 1er juillet 2011 : R. 351-27, « fixé à soixante-cinq
  ans ». Lue.
- Du 1er juillet 2011 (loi n° 2010-1330, article 118) : un renvoi, l'âge de
  L. 161-17-2 plus cinq ans.
- Du 1er septembre 2023 (loi n° 2023-270) : un renvoi, l'âge du premier
  alinéa de L. 161-17-2 plus trois ans. Ce premier alinéa dit soixante-quatre
  ans : les versions de 2023 et de 2025 de l'âge légal portent la valeur
  `age_du_premier_alinea`. C'est le piège du brief : le moteur ne lit pas
  l'âge légal de chaque génération plus trois.

Un renvoi se résout au paquet (`renvois` de chaque version, en mois) et au
moteur (`valeurDuRenvoi`, `AgesAnnulationDecote`, dans `regimes.js`). Une
couche qui garderait l'âge légal d'avant 2023 sans l'âge du taux plein est
refusée et nomme les deux fiches (`controler_les_renvois`) : la couche
`sans_la_reforme_de_2023` remplace donc aussi cette fiche. La table
`age_annulation_decote.csv` devient une vue fabriquée des versions, que la
certification relit.

**L'âge de la personne.** Le moteur oppose à la pension l'âge que l'assuré
atteint, sous la version qui vaut quand il l'atteint, compté de son jour de
naissance (`ageDuTauxPleinDeLaPension`, `commun.js`), sauf avant le 1er avril
1983 où la période du régime décide.

**La correction.** Les assurés nés avant 1930 n'avaient pas de ligne : un
régime qui renvoie à la règle commune lisait la valeur de sa période,
soixante-sept ans à la Carpimko de 1987. Auxiliaire médical né le 10 mai
1925, parti en 1990 à soixante-cinq ans : 6 780,38 euros par an, coefficient
d'anticipation de 0,9875 ; désormais 6 786,20 euros.

**Ce qui ne bouge pas.** Les 937 témoins de simulation et les 86 de pages,
identiques hors ce cas. 5 472 âges recalculés (trois droits, générations 1900
à 1975 de mois en mois, deux jours de naissance) : aucun écart à l'ancienne
table. Le coût bouge de 0,09 % au plus (équilibre). Les 469 périodes de
régime qui renvoient à la fiche gardent leur valeur écrite, que 59 lisent
encore avant 1983 : l'étape 4 les ôtera.

**Questions au propriétaire.**

1. Né avant 1955, pension prenant effet après le 1er septembre 2023, à
   soixante-huit ans passés : le moteur garde l'âge atteint (66 ans et 2 mois
   pour 1953), comme les statuts de 2017 de la CARCDSF l'écrivent génération
   par génération. La lettre de L. 351-8 à la date d'effet dirait 67 ans.
   L'agent sur Fable 5.2 penchait pour 67 ; la session garde l'âge atteint,
   qui ne change aucun résultat. Chirurgien-dentiste né le 1er janvier 1953,
   parti le 1er janvier 2024 : coefficient 1,19 gardé, 1,15 sous l'autre
   lecture.
2. L'âge du parent de trois enfants (minimum avec 65 ans) reste dans le code
   d'`ouvrir.ageTauxPlein` : le contrat des fiches ne sait pas dire cette
   relation.

Non fait : un exemple chiffré de la Cnav de 2011 pour la version « plus cinq »,
dont le rectificatif demande une seconde lecture.
