# Étape 4, deuxième partie : le maximum de la réversion du régime général

**Le 9 octobre 2026, la demande.** Le propriétaire : « Action 138, étape 4 : le
point suivant de « Ce qui reste » : le maximum (surcote en sus), puis le plafond
de ressources du ménage, puis la réversion d'un assuré mort avant son départ,
puis le partage entre ex-conjoints et le remariage. Ce sont les points de
Destinie 2 au chantier 138.4. Un seul point par session. » Le maximum, donc :
la fiche `reversion` le déclarait absent depuis le 28 septembre.

**Ce que dit le droit, lu le jour même** (journal de veille du 9 octobre ;
fiche `reversion`).

- *Le maximum* : « Le montant maximum de la pension principale de réversion
  [...] est égal à 52% du maximum qui était ou aurait été opposable à l'assuré
  décédé » (circulaire Cnav n° 120/82, § 4) ; 54 % depuis 1995, pour les
  réversions d'avant aussi (n° 3/95, § 13 et § 23). La caisse ne cite pour lui
  aucun article du code, seulement ses circulaires et le décret n° 94-1140, qui
  porte le taux à 54 % ; le maximum des pensions, lui, est celui des arrêtés de
  1986, que l'ajournement d'avant 1983 majore (fiche
  `pension_maximale_regime_general`).
- *La base* : la Cnav prend la pension du défunt « sans être comparé[e] au
  minimum et au maximum » (exposé « Montant - retraite de réversion ») ; elle la
  revalorise « sur le montant calculé », qu'elle compare au maximum « lors de
  chaque opération de revalorisation » — la pension « ramenée au maximum de
  62.040 F » de son exemple est menée entière, 63 000 F revalorisés (circulaire
  n° 105/90, § 1 et § 22) ; réduite pour ressources ou pour cumul, c'est le
  montant réduit qu'elle compare.
- *La surcote* : « 54% du droit générateur (éventuellement ramené au plafond
  maximum de retraite) non majoré par la surcote, auquel s'ajoute 54% du montant
  de la surcote [...]. Le total n'est pas ramené au maximum des retraites de
  réversion » (circulaire n° 2018-4, § 5), et son exemple de 2012 : 836,77 € par
  mois.
- *Le barème* de la Cnav, « Montant maximum de la retraite de réversion », lu
  par son API : 93 dates de 1949 à 2026, 12 976,20 € en 2026, chacune le taux de
  la réversion du maximum des pensions de sa date ; de 1982 à 1996, au plafond du
  semestre. Pour 1965, il compte sur le plafond de 1965, que le barème du
  maximum des pensions remplace par celui de 1966 : il donne raison au modèle
  (lecture divergente de la fiche `pension_maximale_regime_general`).

**Ce qui est fait.**

- *Le modèle* (`droit/reversion.py`, son jumeau) : la base de la réversion du
  régime général reprend ce que le maximum des pensions avait retiré de la
  pension, que `liquider` écrit (`PensionRegime.ecretement_du_maximum`), que
  l'échéancier mène au décès comme la pension et que des départs échelonnés
  ramènent comme elle ; après la réduction pour ressources, la réversion est
  ramenée à son maximum : le taux de la version, du maximum des pensions de sa
  date d'effet au plafond de l'année des montants (`maximum_des_pensions`, que
  `pension_maximale` lit désormais), multiplié par le coefficient de
  l'ajournement d'avant 1983 ou du taux acquis (`coefficient_du_maximum`), plus
  le taux de la surcote du défunt (`surcote`). La ligne dit le maximum,
  l'écrêtement repris et le motif « maximum », la carte du site aussi.
- *Les tests* : le barème de la Cnav à trente-trois dates, la pension d'avant le
  maximum, le maximum de 2022 que le plafond gelé fait mordre, la surcote qui le
  passe, l'ajournement de 1982, l'échéancier (`test_reversion.py`) ; l'exemple de
  la circulaire n° 2018-4, rejoué au centime (`exemples_officiels.yaml`) ; deux
  témoins de simulation, dans les deux moteurs : `reversion_maximum_des_pensions`
  et `reversion_au_maximum`.

**Les mesures.** Le changement ne touche que les réversions des pensions que le
maximum des pensions a ramenées, de 1973 à 1990 surtout, dont la base reprend
ce qu'il avait retiré, et celles que le plafond, quand il ne suit pas les
pensions, ramène à leur maximum. Aucune pension des six scénarios ne bouge, ni aucune des dix-neuf
réversions des témoins qui en portaient une, qui gagnent les deux champs ; la
page ne change pas. Le cadre parti à soixante-cinq ans en 1990, à cinq salaires
moyens, ramené de 10 547 € à 9 988,50 € : sa veuve recevrait en 2005 54 % de la
pension calculée, 7 459,73 € au lieu de 7 064,44 € (+5,6 %), sous le maximum de
8 151,84 € ; mort l'année de son départ, 52 % du maximum de l'année, 5 194,02 €
au lieu de 5 261,54 € (−1,3 %), la pension revalorisée en juillet passant le
maximum compté sur le plafond moyen. La réversion d'essai de ce cadre, cette
année, passe de 9 416,82 € à 9 943,73 € (+5,6 %). Le parti à soixante-dix ans
en 1982, mort en 1995 : 9 628,07 € au lieu de 8 316,36 € (+15,8 %), sa pension
calculée passant de 19 % celle que le maximum lui servait.

**Ce qui reste.**

1. *De l'étape 4, dans l'ordre* : le plafond du ménage ; la réversion d'un
   assuré mort avant son départ ; le partage entre ex-conjoints et le remariage
   — le maximum s'y réduit, comme le minimum, au prorata de la durée du mariage
   (circulaire n° 105/90, § 3) — ; L. 353-5 et D. 355-1.
2. *Du maximum* : sa comparaison à chaque revalorisation, quand le modèle
   suivra la réversion servie au-delà de l'année des montants ; le plafond du
   semestre de 1982 à 1996, que le dépôt n'a pas (le maximum du modèle est plus
   bas de 0,5 à 3,6 % au 31 décembre) ; le maximum des salariés agricoles et des
   indépendants, avec celui de leurs pensions.
