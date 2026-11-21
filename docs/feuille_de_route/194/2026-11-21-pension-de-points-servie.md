# La pension de points servie après le dernier barème ne baisse plus

Action 194, suite des pistes du balayage
(`2026-11-21-pistes-du-balayage.md`, seconde erreur).

`PensionServie.coefficient` (`moteur/js/revalorisation.js`) menait une
pension de points par le rapport de la valeur du point à l'échéance à celle du
départ, arrêté à la dernière valeur publiée, puis par la revalorisation
générale. Un départ postérieur à cette valeur prenait au numérateur la valeur
publiée (Ircantec, 0,56053 € en 2026) et au dénominateur la valeur projetée du
départ (0,570339 € en 2027) : −1,7 % en 2027, −45 % en 2060.

La correction : quand l'année du départ suit la dernière valeur publiée, la
pension n'est menée que par la revalorisation générale publiée, du départ à
l'échéance — la règle qui vaut déjà, au-delà du dernier barème, pour une
pension liquidée avant (« un au-delà », `coefficient_historique`). Aucune
valeur du point antérieure au départ n'entre plus au rapport. Le jumeau Python
passe par le pont : rien à y porter.

Test : `test_la_pension_de_points_servie_apres_le_dernier_bareme_ne_baisse_pas`
(février et mai de 2027, 2040, 2060 au même coefficient ; de 2030 à 2035,
aucune baisse). Vu rouge à 0,983.

Ce qui bouge : un témoin de simulation sur 937, `limite_age_contractuel`
(scénario 1, l'Ircantec servie au-delà de la limite d'âge) : la part de
l'Ircantec, 273,30 € par mois, passe à 282,94 € (+3,5 %) ; aucune autre
pension ne bouge, sur aucun scénario ; une page, `simuler_limite_d_age_contractuel`.
