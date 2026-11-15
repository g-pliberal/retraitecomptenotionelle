# Les cultes et les services passés à la façade : deux règles des cultes, le maximum de leur pension, et un constructeur du compte bâti sous d'autres paramètres

Seizième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-periodes-assimilees-a-la-facade.md`, « Ce qui reste », 1,
premier tiret. Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Deux fichiers quittent `FICHIERS`**, leurs tests inchangés hors de leurs
imports et de leur fixture : `test_cultes.py` (9 tests) et
`test_services_passes.py` (5). Aucun n'a de test marqué
`sur_le_moteur_python` ; ni l'un ni l'autre n'entre dans `RESTES`. Le
dernier test de `test_cultes.py` reste une confrontation par
`droit_et_refait`, sur une carrière que la façade bâtit.

**Le module `droit.cultes`** se sert par la façade (`facade.cultes`) :
`durees`, sur les durées du relevé, que le portage refait de leur carrière,
et `part_de_l_ecart`. Une règle qui reçoit des durées sans recevoir de
carrière les reçoit avec la leur (`_demander_la_regle`). Le portage écrit
`DureesDesCultes` en casse de chameau, et tient en champ `avant1998`, une
propriété du Python (`HORS_DU_TYPE`). **La table `maximum_des_cultes`**
sert `valeur`.

**Un constructeur du compte bâti à la main** (`facade.ConstructeurCompte`,
sous les arguments de celui du Python) : des séries, du catalogue, des
affiliations et de l'indexation d'un simulateur de la façade — l'indexation
n'y est qu'une marque, qui ne se lit pas —, sous d'autres paramètres, c'est
le constructeur du simulateur du portage sous ceux-là. Des données d'un
autre simulateur, ou des paramètres qui les feraient autres
(`REGLAGES_DES_DONNEES` : la racine, la projection, l'emploi, les
conventions du COR, les trois réglages de l'indexation), sont refusés.

## Ce qui est mesuré

**Les tests.** Trois tests neufs dans `tests/test_facade.py`, vus rouges :
la part de l'écart du V du décret n° 2006-1325 et les trois fractions du
ministre né en 1940 (76, 76, 76) ; le maximum des arrêtés de 1990
(19 650 F) ; les cotisations des arrêtés de 1990 sous les deux conventions
(6 210 F, 7 210 F), et les refus. **Contre le jumeau**
(`tests/test_facade_jumeau.py`) : les deux règles, sur six appels ; la
table, sur quatre années ; le constructeur bâti sous trois autres réglages,
cotisations et compte entier, sur deux carrières. `-m rapide` (5 156),
`test_facade.py`, `test_facade_jumeau.py`, `test_pont.py`,
`test_fichiers_sur_le_moteur_python.py` et les deux fichiers : verts.

## Ce qui reste

1. Les fichiers du relevé que la façade ne sert pas encore :
   `test_chomage_complementaires.py`, `test_minima_agricoles.py`,
   `test_sections_liberales.py`, `test_temps_partiel.py`,
   `test_releve_lu.py`, `test_revenu_des_points.py`, `test_referents.py`,
   `test_oracle.py` : des règles hors de la façade
   (`ouvrir.fin_indemnisation`, `releve.points_de_l_annee`,
   `releve.revenu_des_points`, l'échéancier, des tables du scénario).
   `test_cultes_au_droit.py` et `test_cultes_smic_du_mois.py` y trouveront
   déjà le module des cultes.
2. Puis `completer.points_rco_de_chef` ; les 37 tests marqués de
   `test_simulateur.py`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
