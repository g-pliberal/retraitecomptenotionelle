# Correction de la ligne 5 de la file : la CARMF dispense sans points les deux premières années d'exercice

Cinquième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index LEGI** (à jour du 11 novembre 2026). Décret n° 49-579,
article 4, dans la rédaction de l'article 3 du décret n° 2026-418, en vigueur le
1er juillet 2026 (LEGIARTI000054168136 ; article 30 du décret, LEGIARTI000054157413 :
« Le présent décret entre en vigueur le 1 er juillet 2026 », sans disposition
transitoire) : « I. - Tout médecin obligatoirement affilié à la caisse est dispensé du
paiement de la cotisation afférente au présent régime pendant les deux premières années
d'exercice de la profession libérale si cet exercice débute alors qu'il n'a pas atteint
l'âge de 40 ans. » Article 4-1, II (LEGIARTI000054168116) : « Les cotisations ou
fractions de cotisations ayant fait l'objet d'une dispense au titre des I à III de
l'article 4 ne donnent pas lieu à acquisition de points. » Article 2
(LEGIARTI000054168125) : la cotisation reste annuelle, en pourcentage du revenu sous
3,5 plafonds. Le texte tranche ce que la ligne dit : la dispense est de droit, et sans
points. La rédaction d'avant (LEGIARTI000050865157, jusqu'au 1er juillet 2026) renvoyait
aux statuts : « Des dispenses de cotisations peuvent être accordée […] aux
professionnels âgés de moins de quarante ans lors de leur affiliation, dans les
conditions prévues par les statuts ».

**Le test d'abord** (`tests/test_sections_sante.py`), vu rouge sur le cas posé
(53 701,26 € servis), puis, pour le compte, sur les 10 309,73 € portés en 2027 :

- `test_la_carmf_dispense_sans_points_les_deux_premieres_annees_d_exercice`, trois cas
  par la requête du formulaire, servis par le portage et refaits au bit près par le
  moteur Python (`servi_et_refait`) : la médecin du cas posé ; celle qui s'installe le
  jour de ses 40 ans, à qui rien n'est dispensé ; celle qui s'installe en 2025, dont les
  deux premières années précèdent ce que la fiche dispense ;
- `test_la_dispense_de_la_carmf_retire_2_284_euros_a_la_medecin_de_26_ans` ;
- `test_le_compte_ne_porte_pas_la_cotisation_que_la_carmf_dispense`, par la lecture du
  compte au pont, refaite par le moteur Python (`droit_et_refait`).

**L'effet au cas posé** : née le 1er janvier 2001, médecin libérale au double du salaire
moyen, installée le 1er janvier 2027 à 26 ans, pension à 67 ans, euros de 2026. Avant :
990 651,9421 € de cotisations revalorisées × 0,0448 × 1,21 = 53 701,26 € par an. Les
cotisations revalorisées de 2027 et de 2028, 20 997,0503 + 21 141,5017 = 42 138,5520 €,
ne sont pas dues : 948 513,3901 × 0,0448 = 42 493,3999 ; × 1,21 = **51 417,01 € par an**,
2 284,25 € de moins. La base (31 726,78 €) et l'ASV (44 511,19 €), que l'article ne vise
pas, ne bougent pas. Au compte notionnel, 10 309,73 € en 2027 et 10 562,32 € en 2028
(euros courants) ne sont plus portés.

**La correction.** Un paramètre de période, `dispense_de_debut`
(`regimes/_schema.yaml`, `PeriodeRegime`, le paquet par `construire_donnees.py`) : le
nombre d'années dispensées, l'âge que l'affilié ne doit pas avoir atteint quand
l'exercice débute, la première année de cotisation que la fiche dispense. La période de
2026 de `carmf_complementaire.yaml` le porte : `{annees: 2, avant_l_age: 40, depuis:
2027}`. `dispenseDeDebut` (`moteur/js/droit/acquerir.js`) et son jumeau
`dispense_de_debut` le lisent : l'exercice débute au mois de la première entrée dans un
statut que le régime affilie (secteur 1 ou secteur 2 : passer de l'un à l'autre ne le
recommence pas) ; la ligne est dispensée si son année est l'une des deux premières
années civiles depuis ce début, et si l'affilié n'a pas 40 ans au premier jour du mois
du début. `acquerir` saute alors la période, sans cotisation ni points ; le compte
(`ConstructeurCompte`, `moteur/js/compte.js` et `moteur/compte.py`) la saute de même,
puisqu'il « porte ce qui a été versé », sauf sous le taux commun de la proposition, où
le régime ne fait que délimiter l'assiette. Dans la fiche `decret_2026_418_liberaux`,
l'erreur n'est plus déclarée : elle est racontée au champ `effet`.

**Ce que la correction déplace.** Aucun témoin de simulation, aucune page : aucun
témoin ne porte de médecin installé depuis 2027. Le paquet porte le paramètre de plus.
`regenerer.py --verifier` : tout est à jour.

**Ce que la correction laisse, déclaré dans la fiche** (`sources.a_relire`).

- Les cotisations de 2026 et d'avant ne sont pas dispensées : avant le 1er juillet
  2026, la dispense tenait aux statuts, non lus (question 22). Le médecin installé en
  2025 ou en 2026 cotise au modèle toute l'année 2026, quand le second semestre au moins
  en est dispensé.
- « Les deux premières années d'exercice » : vingt-quatre mois, ou deux années civiles ?
  Le texte ne le dit pas. Le modèle dispense l'année civile du début et la suivante, que
  les deux lectures dispensent ; pour un début en cours d'année, la troisième année
  cotise en entier, quand ses premiers mois seraient dispensés sous la lecture des
  vingt-quatre mois.
- L'exercice libéral d'une autre profession, avant celui de médecin, n'est pas compté.
- Le rachat des trimestres dispensés (article 4-2, I), sur demande, n'est pas porté.

**La classe, pour les lignes suivantes.** Le paramètre sert tel quel à une dispense
totale d'une autre section. La ligne 6, la part proportionnelle des deux premières
années de la caisse des dentistes, n'est dispensée que d'une part de la cotisation, le
forfait restant dû : elle demandera de dire quelle part. La ligne 7, l'exemption passé
75 ans, est une autre condition.

**Vérifié** : `python -m pytest -m rapide`, `-m site`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py`, `test_sections_sante.py`,
`test_sections_liberales.py`, `test_sections_juridiques.py`, `test_pcv_sante.py`,
`test_carte.py`, `test_donnees.py`, `tests/js/moteur.test.js`, verts.
