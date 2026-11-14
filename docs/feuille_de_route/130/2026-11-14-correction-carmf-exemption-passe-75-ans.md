# Correction de la ligne 7 de la file : la CARMF exempte sans points passé le semestre des 75 ans

Septième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index LEGI** (à jour du 13 novembre 2026). Décret n° 49-579,
article 4, II, dans la rédaction de l'article 3 du décret n° 2026-418, en vigueur le
1er juillet 2026 (LEGIARTI000054168136) : « Tout médecin qui continue d'exercer en
qualité de non salarié est exempté du versement de la cotisation à partir du premier
jour du semestre civil qui suit son soixante-quinzième anniversaire. » Article 4-1, II
(LEGIARTI000054168116) : « Les cotisations ou fractions de cotisations ayant fait
l'objet d'une dispense au titre des I à III de l'article 4 ne donnent pas lieu à
acquisition de points. » Le texte tranche ce que la ligne dit : l'exemption est de
droit, et sans points. Il ne tranche pas le partage de l'année où elle commence : la
cotisation est annuelle (article 2, LEGIARTI000054168125), le IV du même article parle
d'une « cotisation semestrielle », et l'article 3 (LEGIARTI000054168139) renvoie son
versement aux statuts, non lus.

**Le test d'abord** (`tests/test_sections_sante.py`), vu rouge sur le cas posé
(18 895,60 € servis), puis, pour le compte, sur les 5 154,86 € portés en 2027 :

- `test_la_carmf_exempte_sans_points_passe_le_semestre_des_75_ans`, trois cas par la
  requête du formulaire, servis par le portage et refaits au bit près par le moteur
  Python (`servi_et_refait`) : la médecin du cas posé ; celle qui a 75 ans le 1er juillet
  2026, exemptée du 1er janvier 2027 ; celle qui a 75 ans le 1er janvier 2027 et part le
  1er juillet, à qui rien n'est exempté ;
- `test_l_exemption_de_la_carmf_retire_300_euros_a_la_medecin_de_76_ans` ;
- `test_le_compte_ne_porte_pas_la_cotisation_que_la_carmf_exempte_passe_75_ans`, par la
  lecture du compte au pont, refaite par le moteur Python (`droit_et_refait`).

**L'effet au cas posé** : née le 1er janvier 1951, médecin libérale au double du salaire
moyen depuis ses 30 ans, pension à 76 ans et 6 mois (1er juillet 2027), euros de 2026.
Avant : 324 443,6335 € de cotisations revalorisées × 0,0448 × 1,30 = 18 895,60 € par an.
Le semestre de 2027, 5 154,8634 € (0,118 × 87 370,5656 / 2), n'est pas dû :
319 288,7701 × 0,0448 = 14 304,1369 ; × 1,30 = **18 595,38 € par an**, 300,22 € de
moins. La base (18 281,12 €) et l'ASV (22 383,12 €), que l'article ne vise pas, ne
bougent pas. Au compte notionnel, les 5 154,86 € de 2027 ne sont plus portés.

**La correction.** Un paramètre de période, `exemption_passe_l_age`
(`regimes/_schema.yaml`, `PeriodeRegime`, le paquet par `construire_donnees.py`) :
l'âge, et la première année de cotisation que la fiche exempte. La période de 2026 de
`carmf_complementaire.yaml` le porte : `{age: 75, depuis: 2027}`. Le semestre qui suit
l'anniversaire s'ouvre le 1er juillet de son année ou le 1er janvier de la suivante :
`exemptionPasseLAge` (`moteur/js/droit/acquerir.js`) et son jumeau
`exemption_passe_l_age` exemptent les années civiles d'après celle des 75 ans, que
toute lecture exempte. `acquerir` saute alors la période, sans cotisation ni points ; le
compte (`ConstructeurCompte`, `moteur/js/compte.js` et `moteur/compte.py`) la saute de
même, sauf sous le taux commun de la proposition, où le régime ne fait que délimiter
l'assiette. Dans la fiche `decret_2026_418_liberaux`, l'erreur n'est plus déclarée :
elle est racontée au champ `effet`.

**Ce que la correction déplace.** Aucun témoin de simulation, aucune page : aucun
témoin ne porte de médecin en exercice après 75 ans. Le paquet porte le paramètre de
plus. Un test voisin a dû changer d'assuré : `test_la_fiche_preleve_ce_que_le_compte_recoit`
(`tests/test_fiche_des_liberaux.py`) comparait la fiche de paie, qui ne connaît pas
l'âge, au compte d'un assuré né en 1935, médecin jusqu'en 2029 ; né en 1954, il n'a
75 ans qu'en 2029, et rien ne lui est exempté dans les années comparées.

**Ce que la correction laisse, déclaré dans la fiche** (`sources.a_relire`).

- Le second semestre de l'année d'un anniversaire tombé au premier semestre reste
  cotisé, faute de texte sur le partage de la cotisation au semestre : au cas posé, la
  moitié des 10 239,2845 € de 2026, 298,17 € par an de trop encore si elle se partage
  (598,39 € en tout, le chiffre haut de la note `2026-11-06-e10-decret-2026-418.md`).
- Les cotisations de 2026 et d'avant ne sont pas exemptées : avant le 1er juillet 2026,
  l'article 4 ne disait rien de l'exemption, et ni l'index LEGI ni celui du JORF ne la
  portent avant le décret n° 2026-418 ; les statuts d'alors ne sont pas lus (question 22).
- La cotisation volontaire de l'article 4-3, passé cet âge, n'est pas portée.
- La fiche de paie du site, qui ne connaît ni l'âge ni le début d'exercice, prélève la
  cotisation du médecin que rien ne dispense.

**La classe.** Cherchée aux deux index : aucune autre section ne porte d'exemption de
la retraite complémentaire passé un âge ; le même décret l'écrit pour l'invalidité-décès
des médecins (décret n° 55-1390, article 2-2), que le modèle ne calcule pas.

**Vérifié** : `python -m pytest -m rapide`, `-m site`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py`, `test_sections_sante.py`,
`test_sections_liberales.py`, `test_sections_juridiques.py`, `test_pcv_sante.py`,
`test_fiche_des_liberaux.py`, `test_carte.py`, `test_donnees.py`, les essais de
`tests/js/`, verts ; `regenerer.py --verifier` : témoins, pages et tableaux à jour.
