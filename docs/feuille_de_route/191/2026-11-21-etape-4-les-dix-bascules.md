# Étape 4 de la note 0009, première session : les dix renvois qui peuvent changer un résultat

**Reprise, au 21 novembre 2026.** Les dix renvois d'un régime aux fiches
d'âge que la note 0009 désignait sont rangés : huit citent le texte qui les
fait, au jour où leur période commence à liquider ; celui de la Banque de
France à l'âge légal, qu'aucun texte ne faisait avant 2025, est parti, et
revient cité en 2025 ; celui de la Banque de France à l'âge du taux plein
est parti, l'âge lu dans le règlement (note du même jour sur ce taux
plein). Un contrôle Z3 vérifie chaque renvoi cité. Aucun témoin n'a
bougé. Point d'arrêt : le propriétaire décide de la suite de l'étape 4
sur le compte qui clôt cette note ; ne pas l'ouvrir avant.

Le 21 novembre 2026, l'après-midi, sur Opus 5.5, au choix du propriétaire
(relecture sur Fable avant l'envoi). Sur l'accord du propriétaire pour les
dix bascules seules (« Faisons ça »).

## Les dix, et ce qui en est fait

Les dix sont ceux de la relecture du 17 novembre
(`2026-11-17-dix-renvois-sensibles.md`) ; ses cinq dates fausses avaient été
corrigées le 19 (`2026-11-19-quatre-dates-au-jour.md`, et les fiches de la
décote et de la surcote de la Banque de France). Restait le rangement : citer,
dater au jour, ôter le repli.

| Régime | Renvoi | Depuis | Texte cité | Fait |
|---|---|---|---|---|
| CNBF | âge d'ouverture | 1er janvier 2004 | L. 723-10-1, LEGIARTI000006744100 | cité |
| Cavimac | âge d'ouverture | 2 novembre 2006 | décret n° 2006-1325, art. 2, JORFARTI000001085913 | cité |
| État | âge du taux plein | 1er janvier 2004 | loi n° 2003-775, art. 66, JORFARTI000002020831 | cité |
| CNRACL | âge du taux plein | 1er janvier 2004 | décret n° 2003-1306, art. 65, LEGIARTI000006400937 | cité |
| FSPOEIE | âge du taux plein | 1er janvier 2004 | décret n° 2004-1056, art. 50, LEGIARTI000006781529 | cité |
| CRPCEN | âge d'ouverture | 1er janvier 2025 | décret n° 90-1215, art. 84, LEGIARTI000047910068 | cité |
| Commerçants d'avant 1973 | âge d'ouverture | 7 octobre 2012 | décret n° 73-937, art. 3, LEGIARTI000026474703 | cité |
| Artisans d'avant 1973 | âge d'ouverture | 7 octobre 2012 | le même | cité |
| Banque de France | âge d'ouverture | 1er janvier 2025 | règlement, art. 26 a, LEGIARTI000047909725 | parti de 2008 à 2022, cité en 2025 |
| Banque de France | âge du taux plein | — | — | parti, l'article 70 lu le même jour |

**La Banque de France, l'âge d'ouverture.** De 2008 à 2022, ses périodes
renvoyaient à `age_legal_par_generation`. Aucune rédaction du règlement ne le
fait avant celle du 1er janvier 2025, la seule de l'index LEGI où
« 161-17-2 » paraisse : l'article 26 a écrit soixante ans, puis l'article 72
sa table, que la fiche porte (`age_table: banque_de_france`) et qui masquait
toujours le renvoi. Treize lignes ôtées, et treize valeurs de repli avec
elles ; une sonde du moteur sur 5 772 carrières (nés de 1895 à 2005, départs
de 50 à 75 ans) ne voit aucun âge changer.

**La Banque de France, l'âge du taux plein.** Le renvoi à
`age_annulation_decote` court de 2008 à aujourd'hui et le moteur le lit :
l'agent né en juillet 1951 parti en 2009 a un âge du taux plein de 65 ans et
4 mois, celui du régime général. La décote, depuis le 19 novembre, lit l'âge
de l'article 70 du règlement (61 ans en 2009) ; mais les autres lectures de
`ageTauxPlein` dans `liquider.js` et `acquerir.js` gardent l'âge du régime
général, et n'ont pas été relevées une à une. Ce n'est pas le droit du règlement : une correction
qui déplace des résultats, son test tiré de l'article 70, chaque lecture à
relire. Non faite ici.

**Quatre citations datent la bascule sans dire la règle mot pour mot**
(remarque de la relecture sur Fable, le 21 novembre). Pour l'État, la CNRACL
et le FSPOEIE, le texte cité est le tableau transitoire, qui fixe le jour
(1er janvier 2004) mais s'arrête au 31 décembre 2019 et parle de « limite
d'âge » diminuée de trimestres. La règle permanente est ailleurs, et elle
parle de la limite d'âge du grade, non de l'âge du régime général : L. 14, I
du code des pensions civiles et militaires (LEGIARTI000006362704), l'article
20 du décret n° 2003-1306 (LEGIARTI000006400883), l'article 16 du décret
n° 2004-1056 (LEGIARTI000006781485, « soixante-cinq ans ou soixante ans »
pour l'emploi insalubre). Le renvoi à `age_annulation_decote` coïncide avec
la limite d'âge du sédentaire ; il n'est pas ce texte. Pour la Cavimac, le
décret n° 2006-1325 écrit « soixante ans », non l'âge légal : le renvoi le
rend tant que l'âge légal vaut soixante ans, et ce qui le fait ensuite est
L. 382-27 (loi n° 2005-1579, article 75). Le champ ne porte qu'un texte par
renvoi : il garde celui qui date la bascule, et la note dit le reste.

## Les valeurs de repli ne sont pas mortes

La sonde a cherché, période par période des neuf régimes, si une valeur de
repli change un âge ou une durée quand on la remplace : jamais. Mais le
régime fusionné de la proposition (`fusion.js`, l. 120 à 130) prend le
maximum des `age_ouverture`, `age_taux_plein` et `duree_requise_trimestres`
écrits dans les périodes, sans lire les renvois, et le chargeur Python les
exige (`regimes.py`, l. 2238). Ôter les replis demande donc d'abord que la
fusion lise les âges par les renvois : du code, qui déplace le régime
fusionné. La note 0009 le voulait ; il reste à faire, hors des dix.

## Le contrôle Z3

`questions.des_renvois_des_regimes` pose une propriété par renvoi cité, sur
tous les régimes : la période qui ouvre le renvoi liquide depuis le jour
cité, celle d'avant jusqu'à la veille, et une seule période liquide chaque
jour jusqu'à la fin du renvoi. Treize propriétés, toutes prouvées, dont deux
hors d'un cas attendu : l'ASV des auxiliaires médicaux cite le règlement de
juillet 2026 et l'applique depuis 1975, présomption déjà déclarée, désormais
inscrite à `proprietes_attendues.yaml`. Test :
`test_un_renvoi_de_regime_qui_ne_vaut_pas_au_jour_qu_il_cite_est_une_surprise`.

## Ce qui a bougé

Aucun des 937 témoins de simulation, aucune des 86 pages. Cliquets : valeurs
de repli 1 442 → 1 429 ; renvois sans texte 306 → 296.

## Le coût, et ce que le reste demanderait

Une session de deux heures et demie environ, un commit. Par régime : le
rangement d'un renvoi déjà relu au texte coûte quelques minutes (citer,
vérifier le jour) ; un renvoi qui se révèle ne pas être le texte coûte une
recherche dans l'index (la Banque de France, une demi-heure) ; une correction
est une étape à elle. La relecture du 17 novembre avait fait l'essentiel :
sans elle, compter une heure par renvoi.

Le reste de l'étape 4 : 296 renvois sans texte, la plupart jamais relus, et
1 429 valeurs de repli, qu'aucun ne peut ôter avant la fusion. À trancher par
le propriétaire : le budget des 296 renvois (par poids dans les résultats,
comme la note le dit), et la fusion par les renvois. L'âge du taux plein de
la Banque de France est corrigé le même jour.
