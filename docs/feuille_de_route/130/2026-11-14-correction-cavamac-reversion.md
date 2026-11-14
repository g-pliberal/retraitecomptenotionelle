# Correction de la ligne 30 de la file : la réversion de la CAVAMAC servie

Trentième et dernière ligne de la file `2026-11-13-corrections-decidees.md`, décidée par
le propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index du Journal officiel** (à jour du 11 novembre 2026). Statuts de
2011, articles 18 et 21 à 25 (arrêté du 23 juin 2011, JORFARTI000024270173, en vigueur le
1er juillet) ; règlement de 2026, articles 11 à 14 (arrêté du 10 juillet 2026,
JORFARTI000054436046, en vigueur le 18 juillet). Les deux disent la même règle : le
conjoint survivant « âgé d'au moins 65 ans », « marié depuis deux ans au moins au moment
du décès de l'adhérent ou qu'un enfant au moins, né ou à naître, soit issu de leur
union », a droit « à une pension de réversion calculée sur soixante pour cent (60 %) des
points de retraite acquis par l'adhérent décédé », qui « n'est pas minoré[e] par le
coefficient de minoration » et « bénéficie du coefficient de prorogation » ; « Le conjoint
divorcé est assimilé à un conjoint survivant », et le partage se fait « au prorata de la
durée respective de chaque mariage », « arrondie au nombre de mois inférieur ». Rien n'y
retire la réversion au survivant remarié. L'arrêté du 28 mars 2014 (JORFARTI000028814573)
la fait partir au premier jour du mois, et non plus du trimestre civil, qui suit le
décès ; ceux du 4 août 2023 et du 8 juillet 2025 n'y changent rien que le modèle serve.
La caisse le confirme (« La pension de réversion », lue le 14 novembre 2026) : « sans
condition de ressources », « Le remariage du bénéficiaire ne suspend pas le versement »,
« 60 % de vos points acquis », à quoi « s'ajoutent éventuellement : la majoration pour
enfants de 10 % » et celle du départ après le taux plein. Aucun exemple chiffré publié.
Le texte tranche ce que la ligne dit.

**Le test d'abord** (`tests/test_reversion.py`, section « la complémentaire des agents
généraux d'assurance »), vu rouge sur le premier cas posé (taux nul, motif `non_portee`).
Posés à la main, sur les pensions des lignes 27 et 28 : 60 % × 14 984,97 = 8 990,98 € et,
prorogation de 10 % comprise, 60 % × 26 068,01 = 15 640,81 €, au premier jour du mois qui
suit le décès ; la survivante née le 10 mars 1960, servie le 1er avril 2025 ; deux ans de
mariage, ou un enfant ; le remariage et le pacte civil, qui ne retirent rien ; les deux
tiers à la survivante de 240 mois devant une précédente de 120, remariée ou non ; la
majoration, 60 % × 14 984,97 × 1,10 = 9 890,08 € ; rien pour un décès du 30 juin 2011.
Puis l'agent général du formulaire (né le 1er juin 1950, parti à 67 ans, mort en juin
2020), seul, avec trois enfants et marié en 2019 : servi par le portage, refait au bit
près par le moteur Python (`servi_et_refait`).

**L'effet aux cas posés** : 8 990,98 € par an au lieu de rien, et 15 640,81 € au second.

**La correction.** Une fiche, `reversion_cavamac`, trois versions sur la date du décès :
avant le 1er juillet 2011, non portée (les statuts d'avant sont au Bulletin officiel) ;
puis les deux textes, aux mêmes paramètres. Les deux moteurs la lisent
(`Reversions.FICHES`) par la branche qui sert la CARCDSF, sans une ligne de code de plus :
60 %, 65 ans, deux ans de mariage, les précédents conjoints tous admis au partage, aucune
perte au remariage, la majoration pour enfants reversée. Dans la fiche
`cavamac_minoration_age_seul`, l'erreur n'est plus déclarée : elle est à l'historique.

**Ce que la correction déplace.** Aucun témoin de simulation, aucune page. Le paquet
porte la fiche de plus.

**Ce que la correction laisse, déclaré dans la fiche `reversion_cavamac`.**

- **La minoration du défunt n'est pas retirée.** Le moteur reverse 60 % de la pension
  servie, quand le texte reverse 60 % des points sans la minoration du départ anticipé :
  le conjoint de l'agent parti avant son taux plein est servi trop bas, de 25 % au plus
  (6 743,24 € au lieu de 8 990,98 € au cas posé). La pension ne dit pas son coefficient à
  la réversion ; le lui faire dire touche le résultat des deux moteurs et le pont, plus
  qu'une ligne de la file. C'est la suite à décider.
- Le seuil de 1 500 points, sous lequel la caisse verse un capital, n'est pas lu.
- La version se choisit au décès : rien pour un décès d'avant le 1er juillet 2011.
- Tout enfant déclaré lève la condition de mariage ; les précédents conjoints partagent
  sans que leur âge ni leurs deux ans de mariage soient vérifiés.
- La date d'effet au mois, quand le texte dit le trimestre civil de juillet 2011 à mars
  2014, et le mois du décès pour l'adhérent mort avant sa retraite.

**Vu en passant, non suivi.** Au formulaire, la retraite complémentaire de l'agent n'est
pas la même au centime avec trois enfants (12 554,53 € contre 12 642,15 €), avant sa
majoration : le test lit la réversion sur la pension du cas. La cause n'est pas cherchée.

**Un rouge réparé à part.** L'essai JavaScript de la majoration de la CARCDSF
(`tests/js/moteur.test.js`) attendait encore 1,10 pour le dentiste né en janvier 1957
parti à 69 ans, quand la ligne 24 a fait compter sept trimestres civils entiers, 1,0875,
ce que dit le test Python : la suite complète, qui lance ces essais, aurait rougi. Corrigé
dans un commit à lui, envoyé avant la correction.

**La classe.** La réversion de la CAVEC, de la CARPV et des autres sections reste non
portée, comme celle des prestations complémentaires de vieillesse : la file ne les nomme
pas. Chacune n'est qu'une fiche à écrire, si son texte tient dans ces paramètres.

**Vérifié** : `python -m pytest -m rapide`, `test_reversion.py`, `test_carte.py`,
`test_sections_sante.py`, `test_sections_liberales.py`, `test_pont.py`, `test_donnees.py`,
les confrontations légères (`test_oracle.py`, `test_destinie.py`,
`test_estimation_officielle.py`, `test_verification.py`), les essais de `tests/js/`, verts.
