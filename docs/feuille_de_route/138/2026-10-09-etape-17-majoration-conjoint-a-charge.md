# Étape 17, onzième partie : la majoration pour conjoint à charge

**Le 9 octobre 2026, la demande.** La dernière du reste de l'étape : la pension
du régime général prise avant 2011 est majorée quand le conjoint à charge a
soixante-cinq ans (L. 351-13). Les barèmes IPP et OpenFisca-France en portent
les montants (registre, chantier 138.17) ; le dépôt ne la servait pas, faute de
conjoint, que la saisie déclare pourtant depuis le 28 septembre.

**Ce que dit le droit, lu le jour même** (journal de veille du 9 octobre ;
fiche `majoration_conjoint_a_charge`).

- *Les conditions* (décret n° 45-0179, article 72-2, puis R. 351-31) : le
  conjoint a soixante-cinq ans, ou soixante s'il est inapte, ne bénéficie
  d'aucun avantage de vieillesse ou d'invalidité — sinon un complément
  différentiel —, et ses ressources, avec la majoration, ne passent pas le
  plafond de l'allocation aux vieux travailleurs salariés. Elle est due dès
  l'entrée en jouissance de la pension, sinon du mois qui suit celui où les
  conditions sont remplies (R. 351-33).
- *Le montant* : de 14 500 anciens francs par an au 1er juillet 1948 à 4 000 F au
  1er juillet 1976, puis 609,80 € depuis 2002, sans revalorisation (barème de la
  Cnav). Entière avant le 1er mars 1975 ; ensuite en 150es de la durée du régime
  général (circulaire n° 31/75 ; R. 351-32), puis sur la durée qui proratise la
  pension depuis le décret n° 2007-56 (circulaire n° 2007-31) ; entière pour la
  pension substituée à une pension d'invalidité.
- *La fin* : supprimée à compter du 1er janvier 2011 (loi n° 2010-1330, article
  51), maintenue à qui l'avait au 31 décembre 2010 ; la pension d'avant 2011 dont
  le droit s'ouvre depuis n'y a pas droit (circulaire n° 2011-9).

**Ce qui est fait.**

- *La fiche*, cinq versions : rien avant le barème de 1948, entière jusqu'en
  1975, en 150es, sur la durée de la pension depuis 2007, rien depuis 2011.
- *Le modèle* (`completer.majoration_pour_conjoint_a_charge`, son jumeau) : la
  majoration de la date d'effet s'ajoute à la pension du régime général, et ses
  étapes s'y écrivent (`PensionRegime.conjoint`) — elle s'ouvre souvent après le
  départ, aux soixante-cinq ans du conjoint, et ne se revalorise pas. La
  revalorisation sert, à chaque échéance, celle du jour, nominale, au lieu de
  celle du départ menée (`RegimeServi.conjoint`), et la réversion ne la lit pas.
  Le conjoint est celui que la saisie déclare, avec ses ressources, lues comme
  ses pensions, qui s'en retranchent ; sans ressources dites, rien.
- *L'inventaire des avantages* : la ligne, « absente » parce que le modèle
  n'avait pas de conjoint, est chiffrée ; le poste publié la tient.
- *Les tests* : `test_majoration_conjoint_a_charge.py`, neuf cas, dont les cinq
  versions, le prorata, le droit ouvert trop tard, l'ouverture aux soixante-cinq
  ans du conjoint, la majoration nominale et les deux moteurs ; deux témoins
  neufs de simulation.
- *La suite rouge* sur les taux pleins de L. 351-8 : le site ne préchargeait pas
  `droit/categories.js` ; réparé le 8 octobre.
- *La suite rouge* sur la majoration pour enfants à charge : le cas
  `reversion_jeune_deux_enfants` de Destinie 2, parti en 2018 avec deux enfants
  de neuf et douze ans, voit sa complémentaire majorée de 10 %, que Destinie ne
  sert pas ; l'écart est déclaré. La réversion de l'Agirc-Arrco ne reprend plus
  cette majoration du défunt : seule celle des enfants nés ou élevés est
  réversible (accord du 17 novembre 2017, article 109 ;
  `parts_de_la_majoration(..., a_charge=False)`).

**Les mesures.** Aucune carrière de la grille ni aucun témoin ne déclare de
conjoint avec ses ressources et une pension d'avant 2011 : aucune pension ne
bouge. Le salarié parti en 1995, dont le conjoint sans ressources a déjà
soixante-cinq ans, reçoit 609,80 € par an de plus au départ comme aujourd'hui ;
celui dont le conjoint ne les a qu'en juin 1997, à compter de juillet.

**Ce qui reste.**

1. *Le texte d'avant 1975*, dont l'index ne garde que des notices, et la
   majoration de 50 F du conjoint de moins de soixante-cinq ans, supprimée en
   1975.
2. *Le conjoint inapte*, dès soixante ans ; son décès et le divorce, qui
   l'arrêtent ; les ressources d'une autre nature qu'une pension, qui ne la
   réduisent pas sous le plafond : la saisie ne les porte pas.
3. *Les autres régimes* : les salariés agricoles, les artisans et les
   commerçants, dont les textes l'ont reprise.

**L'étape 17 est finie.** Ses onze parties sont dans leurs notes ; les limites
le disent (`docs/limites/ecarts-au-droit-positif.md`, `3-systeme-actuel.md`).
Leurs restes sont dans leurs notes, au chapitre « Ce qui reste ».
