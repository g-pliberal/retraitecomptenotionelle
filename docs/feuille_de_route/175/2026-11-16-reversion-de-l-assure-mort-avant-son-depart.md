# Étape 6, à part : la réversion d'un assuré mort avant son départ, aux règles de la date d'effet (écart lourd n° 2, corrigé)

Le cinquième écart lourd des circulaires, confirmé au texte et seulement déclaré
par `2026-11-16-correction-des-cinq-ecarts-lourds.md` (§ 2), est corrigé dans les
deux moteurs, à la demande du propriétaire, comme étape à part. La session a tourné
sur Opus, Fable n'étant pas disponible : le coordinateur a dit de continuer ainsi.

## La règle

Décret n° 45-0179, article 81 b, version du 30 décembre 1973 (LEGIARTI000006760626),
puis R. 353-3, version du 21 décembre 1985 au 25 août 2004 (LEGIARTI000006749406) :
« Dans le cas où l'assuré n'était pas titulaire d'une pension de vieillesse ou d'une
rente à la date de son décès, il est fait application, pour déterminer le montant de
la pension principale servant de base au calcul de la pension de réversion des
dispositions en vigueur à la date d'effet de cette dernière pension. » La fiche
`reversion` le porte par un paramètre, `pension_eue_aux_regles_de_la_date_d_effet:
"1974-01-01"`, dans les quatre versions qui couvrent 1973 à juin 2004
(`avant_juillet_1974`, `avant_1982`, `taux_52`, `taux_54`) : la règle vaut quand la
date d'effet de la réversion tombe à partir de ce jour.

## Le moteur

- `dateDesReglesDeLaPensionEue` (`droit/reversion.js`, jumeau
  `date_des_regles_de_la_pension_eue`) : la première date d'effet de la réversion du
  régime général, quand sa version porte le paramètre ; `null` sinon.
- `Carriere.arreteeAuDeces(date, liquideeLe)` : liquidée plus tard, la carrière
  arrêtée au décès perd ses lignes d'après le premier jour du trimestre civil du
  décès, et la ligne de cette année ses mois d'après (revenus au prorata) : la durée
  reste celle du décès, le taux celui de l'inaptitude (`au_deces`), l'âge plus élevé
  ne joue pas.
- `Echeancier._pensionsEuesAuDeces` liquide deux fois quand la règle vaut : au décès,
  comme avant, puis à la date d'effet de la réversion (`liquidation_regles_deces_*`
  au journal). Les régimes de la fiche `reversion` — le régime général et les
  régimes alignés — prennent la seconde, ramenée aux montants de l'année du décès
  par la revalorisation des pensions qui les sépare (`revalorisationsPensions.generale`),
  majoration pour enfants, minimum, maximum, durées et majorations forfaitaires
  compris ; les complémentaires gardent la première. `_lirePensionsEues` lit l'une et
  l'autre.

## L'effet

Le salarié né en 1913, mort en février 1972, dont la veuve née en janvier 1921 a sa
réversion le 1er février 1976 : sa pension principale passe de 1 025 € à 1 232 €
aux montants de 1972, + 20 %, par le salaire annuel moyen des dix meilleures années
(règle de 1976) et non des dix dernières (règle de 1972). Le cas de la fiche, 150
trimestres au lieu de 128, ne se bâtit pas par la saisie, qui ne porte au régime
général que les années depuis 1945 : 108 trimestres pour cet assuré, sous les deux
plafonds. Aucun des 933 témoins de simulation ne bouge ; un témoin de plus,
`reversion_deces_avant_le_depart_regles_de_l_effet`, confronte le jumeau Python, au
vert. Tests : `test_la_pension_eue_prend_les_regles_de_la_date_d_effet_de_la_reversion`,
`test_avant_1974_la_pension_eue_reste_celle_du_deces`.

## Ce qui reste

La fonction publique et les régimes spéciaux, que R. 353-3 ne vise pas, liquident
toujours au décès. La caisse prend les règles de la date d'effet pour une part de la
pension depuis juillet 2004 (circulaire Cnav n° 2005-17, § 211 à 213) : écart encore
déclaré dans la fiche. L'exposé « Retraite de l'assuré décédé » a changé de date à la
base de la Cnav (10 novembre 2026), à relire.
