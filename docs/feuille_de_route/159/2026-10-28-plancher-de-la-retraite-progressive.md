# Étape 9, le plancher de la retraite progressive : la pension complète comparée à la provisoire surcote parentale comprise

**La demande.** La vague du 28 octobre 2026 : le propriétaire lance une session
par tâche qui se mène sans lui ; celle-ci reprend le troisième point de « Ce
qui reste » de la note du 23 octobre (`2026-10-23-quatre-restes-surcote-parentale.md`),
« la même classe d'erreur, ailleurs » : la pension complète que le plancher de
la retraite progressive relève portait ensuite la surcote parentale, calculée
sur le montant relevé. Lire si la caisse la calcule sur la pension d'avant le
plancher et, si oui, corriger les deux moteurs. Scénario 1, sur Opus, après
`python scripts/veille_droit.py` ; l'index LEGI mis à jour au 27 octobre 2026.

## Ce que les textes et la caisse disent

- **D. 161-2-24-7** (LEGIARTI000047959215, depuis le 1er septembre 2023), comme
  D. 351-15 depuis 2006 : la pension complète « est liquidée dans les
  conditions de droit commun. Toutefois, elle ne peut être inférieure au montant
  entier ayant servi de base au calcul de la fraction », revalorisé. Le texte
  borne la pension liquidée ; il ne dit rien de la surcote.
- **La Cnav compare deux sommes et sert la plus élevée.** Sa dernière circulaire
  sur la retraite progressive, 2018/31 du 21 décembre 2018, 8.2 : « Pour
  déterminer le montant le plus élevé, il convient de comparer : le montant
  entier ayant servi de base au calcul de la fraction de retraite, revalorisé,
  soit : le montant calculé, éventuellement majoré du minimum ou ramené au
  maximum ; la majoration pour enfants (10 %) ; la surcote ; la majoration de
  retraite des assurés handicapés ; à la somme de ces éléments calculés à la
  date d'effet de la retraite définitive. » De même 2006/66 (92) et 2011/14
  (62) ; l'exposé « Retraite définitive », modifié le 24 octobre 2025, cite
  toujours 2018/31 : « les droits de l'assuré sont réexaminés (y compris la
  surcote) ». Aucune circulaire n'a suivi la réforme de 2023 sur ce point.
- **La surcote parentale est la surcote de L. 351-1-2** : sa rédaction de 2025
  (LEGIARTI000051289776) abaisse d'un an « l'âge mentionné au premier alinéa de
  l'article L. 351-1-2 » ; celle de 2023 ouvrait « une majoration de pension
  dans les mêmes conditions ». Elle entre donc dans la somme de la pension
  complète, calculée sur la pension d'avant le plancher, et le plancher, quand
  il l'emporte, l'efface — non comme le minimum contributif, auquel D. 351-2-1
  l'ajoute, mais comme le minimum garanti du code des pensions.

## Ce qui a changé

- **Les deux moteurs** (`droit/completer.py`, `droit/completer.js`) : le
  plancher se compare à la pension qui porte sa surcote parentale ; quand il
  l'emporte, la pension vaut la provisoire, sans surcote parentale, et son
  détail dit le montant comparé (« 27,256.65 € avec la surcote parentale, porté
  à la pension provisoire revalorisée par + 2,297.94 € »). La pension que le
  coefficient majore se lit par une seule fonction, `avant_la_surcote`
  (`avantLaSurcote`), pour le plancher et pour la surcote. Mesuré sur la mère de
  deux enfants née le 1er janvier 1969, partie à 64 ans à 27 256,65 € par an
  dont 1 297,94 € de surcote parentale : sa provisoire posée 1 000 € au-dessus,
  le module servait 29 669,49 € au lieu de 28 256,65 € ; posée à 99 % de la
  pension complète, 28 333,29 € au lieu de 27 256,65 €. La correction vaut pour
  les trois régimes qui ont et le plancher et la surcote parentale : le régime
  général, les salariés agricoles, les libéraux.
- **Le test d'abord**, dans `tests/test_retraite_progressive.py` : la mère, sa
  provisoire posée entre la pension complète et la même sans surcote parentale,
  puis au-dessus ; et la confrontation des deux moteurs sur les mêmes cas,
  la pension provisoire posée des deux côtés par un module JavaScript en ligne.
- **La classe, pas le cas** : les autres planchers de l'étape qui complète ne la
  relèvent pas. Le minimum garanti est corrigé depuis le 23 octobre ; le minimum
  contributif suit D. 351-2-1 ; le minimum de pension de la SNCF n'a pas de
  surcote parentale, que seuls le régime général, la MSA salariés, la CNAVPL et
  les trois régimes du code des pensions servent ; le plancher de la pension
  substituée, l'AVTS, est sous le minimum contributif d'une carrière complète au
  régime général, durée pleine que la surcote parentale exige, et celui de la
  pension d'invalidité d'avant 1983 ne voit pas de pension de 2023 — une
  carrière partagée entre régimes n'y a pas été mesurée.
- **Les fiches** : `surcote_parentale`, lue le 28 octobre, perd sa question sur
  la retraite progressive ; `retraite_progressive` gagne la lecture des
  circulaires de la Cnav et précise son écart sur les majorations, que la caisse
  met des deux côtés de la comparaison et le modèle après elle, sans effet tant
  que les deux pensions la portent au même taux. `docs/methodologie.md` le dit.

Ce que la correction déplace : rien. Aucun des 909 témoins de simulation n'a de
plancher qui lie, ni aucune des soixante-douze mères de 1966 et de 1969, à trois
salaires et trois quotités, que la session a balayées : la pension complète
dépasse toujours la provisoire revalorisée, le salaire de référence se
revalorisant comme les pensions. Aucune page n'en dit rien ; rien n'est dû à une
session des pages.

## Ce qui reste

- **Le plancher compté deux fois au total contributif**, trouvé en chemin, hors
  de la tâche, et laissé : quand l'assuré a des trimestres d'enfants, de l'AVPF
  ou des points gratuits, `liquider` prend son total contributif à la
  liquidation d'essai qui neutralise les avantages non contributifs ; celle-ci
  reçoit les mêmes pensions provisoires, et son plancher, qui lie plus souvent
  sur une pension plus basse, y entre déjà, avant que `complements.plancher` s'y
  ajoute (`droit/liquidation.py`, `total_contributif += complements.plancher`).
  La mère, sa provisoire 1 000 € au-dessus : 37 559,25 € servis, 39 857,19 € de
  total contributif, la majoration de durée mesurée à − 2 297,94 € ; à 99 % de
  sa pension, où son propre plancher ne lie pas, 36 286,69 € de contributif pour
  36 559,25 € servis, et − 1 025,37 €. Aucun témoin n'en est touché. Ce que la
  liquidation d'essai doit garder du plancher est un choix de mesure à faire
  avant de le coder.
- **La circulaire Cnav de la surcote parentale**, quand elle paraîtra.
- Ce qui reste de l'action attend le propriétaire : la DREES refaite par le
  modèle (étape 8), l'indexation du stock du scénario 1 (étape 4), les cas
  types de l'étape 5, et sa clôture.
