# Étape 8, dix-septième partie : la PMR et le plafond d'après août 2023 des pensions prises avant septembre 2023

**Le 19 octobre 2026, la demande.** Le reste suivant, dans l'ordre du bloc
« Reprise » : les montants d'après août 2023 des pensions prises avant
septembre 2023, que la table n'avait pas, point 1 de « Ce qui reste » de la
note « révision de la PMR ». Session 17 de la troisième salve de la vague du
19 octobre ; ni la durée de chef reconstituée (D. 732-110, III), qui suit, ni
un montant que seule la MSA publierait.

**Ce que dit le droit** (journal de veille du 19 octobre, index LEGI à jour
au 18 octobre, index JORF au 11 octobre).

- *La PMR* : « Pour les personnes dont la pension de retraite servie à titre
  personnel a pris effet avant le 1er septembre 2023, le montant minimum
  annuel PMRmax est revalorisé aux mêmes dates et dans les mêmes conditions
  que celles prévues pour les pensions de vieillesse de base par l'article
  L. 161-23-1 » (D. 732-111, rédactions de 2023 et de 2026).
- *Le plafond, lu aux décrets qui écrivent D. 732-113* : deux alinéas en
  2009, le montant, puis « Le montant du plafond est revalorisé aux mêmes
  dates et dans les mêmes conditions que celles prévues pour les pensions de
  vieillesse de base » (décret n° 2009-173) ; 2010 et 2021 ne touchent que le
  premier ; le décret n° 2023-754 (article 1er, 2°) remplace « le premier
  alinéa » par le I, 11 533,02 € au 1er janvier 2023, et ajoute un II dont la
  phrase du SMIC est le second alinéa ; le décret n° 2025-1410 modifie « le
  premier alinéa du II ». Le second alinéa de 2009 reste donc au I : la
  phrase du SMIC ne vaut pas pour lui. La consolidation de LEGI omet cet
  alinéa depuis 2023 et range la phrase du SMIC après le III.
- *Le minimum du plafond* : « au moins égal à celui de l'allocation de
  solidarité aux personnes âgées » (L. 732-54-3). Revalorisé comme les
  pensions, le I reste l'ASPA d'une personne seule ; mené par le SMIC depuis
  janvier 2023, il tomberait sous elle, 12 300,52 € en 2026 pour 12 523,14 €
  sur la série du SMIC du modèle.

**Ce qui a été cherché**, un montant servi après août 2023 : le guide MSA
« Préparer sa retraite » d'octobre 2023 (le plafond « aligné sur le montant
de l'Allocation de solidarité aux personnes âgées (Aspa) servi pour une
personne seule, soit 961,08 euros par mois ») ; la question écrite n° 1975 de
la XVIIe législature (JO du 12 novembre 2024), le seuil « porté au montant de
l'allocation de solidarité aux personnes âgées (ASPA), soit 1 012,02 euros au
1er janvier 2024 », que la réponse du ministère (JO du 1er avril 2025) ne
dément pas ; les tableaux de bord des retraites des non-salariés au
31 décembre 2023, 2024 et 2025 et les Chiffres utiles de 2026, qui n'écrivent
aucun montant d'après 2022. Le site de la DREES ne répond pas.

**Ce qui est fait.**

- *La série* : `FINS` de `scripts/fetch/dila_legi_pension_majoree.py` porte
  `pmr_chef`, `plafond` et `plafond_depuis_septembre_2023` jusqu'au dernier
  barème : 9 446,31, 9 654,12 et 9 741,00 € de PMR en janvier 2024, 2025 et
  2026 ; 12 144,27, 12 411,44 et 12 523,14 € de plafond, l'ASPA de chaque
  année ; le plafond du II, que relisent les révisions de 2026 des pensions
  prises de septembre 2023 à 2025, 13 285,31 € en janvier et 13 605,47 € en
  juin 2026. Huit lignes de plus, `moyenne`.
- *Au-delà du dernier barème* : la PMR et le plafond d'une pension prise
  avant septembre 2023 suivent les prix, comme les pensions de base que le
  modèle revalorise ainsi (`PMR_SUR_LES_PRIX`, `scenarios/actuel.py`, et son
  jumeau de `moteur/js/regimes.js`) ; les autres mesures, le SMIC, comme
  avant.
- *La fiche* `pension_majoree_reference` : D. 732-111 et D. 732-113 de 2023
  cités par la version de 2022, la lecture des décrets et celle des montants
  cherchés, l'écart récrit.
- *Les tests* (`tests/test_minima_agricoles.py`) : la série, posée à la main
  depuis les textes ; le montant de décembre 2026 et celui de 2030, sur les
  prix et sur le SMIC ; une septième révision confrontée aux deux moteurs, la
  veuve de 2023 menée jusqu'en 2030.

**Les mesures.** La PMR entière de décembre 2026, 9 741,00 € au lieu des
9 567,86 € que le SMIC faisait de janvier 2023 ; le plafond, 12 523,14 € au
lieu de 12 300,52 € ; celui du II, 13 605,47 € depuis juin 2026 au lieu de
13 285,16 €. En 2030, sur les hypothèses du modèle, 10 440,98 € de PMR au lieu
de 10 879,90 €.

**Ce qui reste**, de l'étape, dans l'ordre :

1. La durée de chef reconstituée de D. 732-110, III.
2. Ce que la réversion déclarée permet de servir aux plans de 1997 à 2008
   (D. 732-118, D. 732-116, D. 732-147), point 4 de la note « réversion du
   régime ».
3. À la fin de l'étape, la fiche `complement_differentiel_rco`.
4. Chaque janvier, la série à porter jusqu'au nouveau barème (`FINS`).
5. Inchangés : les points 2 et 3 de « Ce qui reste » de la note « points des
   conjoints » ; au propriétaire, le montant de la MSA pour 2015 à 2017 et
   2019, depuis un poste qui atteint l'archive du web, et les seize points
   d'une année de conjoint d'avant 1999 ; et, s'il le juge utile, demander à
   la MSA le plafond qu'elle sert depuis 2024 aux pensions prises avant
   septembre 2023, que seuls les décrets disent.
