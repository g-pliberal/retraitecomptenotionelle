# Étape 9, suite de la huitième partie : le minimum de la réversion de la SNCF, 54 % du minimum de pension

**La demande.** Lot 3 de la vague des 17 et 18 octobre 2026, lancée par la
session d'orchestration : le premier point du bloc « Reprise » de la huitième
partie (`2026-10-13-etape-9-maladie-des-regimes-speciaux.md`), les minima de
la réversion de la SNCF (articles 18 et 23 de son règlement), que la note
« réversion de la SNCF » (`2026-10-18-etape-9-reversion-de-la-sncf.md`)
laissait. Les pages ne sont pas touchées : une autre session les tient.

**Ce que disent les textes, lus le jour même dans l'index LEGI, mis à jour
le 18 octobre.**

- *L'article 18 du décret n° 2008-639*, le même dans ses trois rédactions :
  « Lorsque la pension de l'agent a été portée au montant du minimum de
  pension prévu à l'article 15, la pension de réversion est portée à 51,3 %
  de ce montant au 1er juillet 2008, à 52,7 % de ce montant au 1er juillet
  2009 et à 54 % de ce montant au 1er juillet 2010. Lorsque la pension de
  l'agent est supérieure au montant du minimum de pension prévu à l'article
  15, la pension de réversion ne peut être inférieure à celle qui résulterait
  de l'application de l'alinéa précédent. » La pension « totale à servir »
  est ensuite partagée entre les ayants droit (article 20), et « majorée[s]
  dans les conditions fixées à l'article 16 », 10 % de la pension pour trois
  enfants (article 16).
- *L'article 15, IV* : « 3 367,02 € par trimestre à compter du 1er juillet
  2008 et [...] 3 379,38 € par trimestre à compter du 1er décembre 2008 »,
  révisés « pour tenir compte d'éventuelles augmentations générales de
  salaire » du second semestre de 2008 (article 36, c, pour les pensions) ;
  depuis le 18 mai 2015, « 1 215,64 euros par mois à partir du 1er octobre
  2014 », que les quatre rédactions suivantes gardent ; la condition du
  taux plein (I) et le plafond des pensions de droit direct (IV) n'y entrent
  que le 1er janvier 2017. Le minimum « est revalorisé dans les
  conditions définies à l'article 30 », « du taux et à la date prévus pour
  les fonctionnaires de l'Etat » : ceux de L. 161-23-1 (article 35, III, pour
  le 1er avril 2009).
- *L'article 23* : « Les pensions de réversion des personnes seules âgées
  d'au moins 55 ans et de moins de 65 ans ne peuvent être inférieures au
  montant de l'allocation de solidarité aux personnes âgées mentionnée à
  l'article L. 815-9 », allocation qui « n'est due que si le total de cette
  allocation et des ressources personnelles de l'intéressé [...] n'excède
  pas des plafonds fixés par décret » (L. 815-9).
- *La caisse* (CPRP, « La pension de réversion — régime spécial », relue le
  18 octobre) : le minimum « égal à 54 % du montant du minimum de pension de
  salarié », sans montant ; les réversions de 55 à 65 ans portées, le cas
  échéant, « au montant de l'allocation de solidarité aux personnes âgées
  (ASPA) », « sous conditions de ressources », qu'elle ne détaille pas. Aucun
  montant du minimum de pension d'une autre année que 2008 et 2014 n'a été
  trouvé publié, ni par la caisse, ni dans la fiche du COR sur la caisse
  (juillet 2024).

**Ce qui est fait.**

- *La série* `data/reference/legislation/minimum_pension_sncf.csv` : les deux
  ancres que le texte écrit, 13 517,52 € par an en 2008, 14 587,68 € en 2014,
  `haute`. Entre elles et depuis, le modèle revalorise le minimum par les
  coefficients des pensions (article 30), au taux de 1 % en 2020, celui des
  pensions de 2 000 € par mois au plus : 15 866,53 € en 2023,
  17 228,69 € en 2026.
- *La fiche* `reversion_sncf` : la part du minimum de pension que garde la
  réversion (`part_du_minimum_de_pension`), 0,54 à la version
  `conjoints_2008`, et ses deux taux de passage en versions d'exception,
  `minimum_2008` (51,3 %, réversions prenant effet du 1er juillet 2008 au
  30 juin 2009) et `minimum_2009` (52,7 %, jusqu'au 30 juin 2010) ; aucune à
  la version `avant_2008`, dont aucun montant n'est lu. Les rédactions de
  l'article 15 et de l'article 30 y sont citées : le cliquet des rédactions
  sans statut descend à 9 687.
- *Le modèle* (`droit/reversion.py`, puis `reversion.js`) :
  `_minimum_de_pension` (`minimumDePension`) rend la part du minimum de
  l'année des montants quand la pension de l'agent l'atteint ; la branche de
  la SNCF porte la réversion entière à ce minimum avant de la partager (motif
  `minimum`, champ `minimum`, part faite), et sa majoration pour enfants en
  garde le taux sur le montant relevé. `Reversions.minimum_pension_sncf` lit
  la série, que le paquet porte (`minimum_pension_sncf`) ; le paquet passe à
  la version 25 des deux côtés.
- *Les tests* : `test_reversion.py`, neuf cas posés à la main sur le texte
  — au-dessus du minimum, à son montant, sous lui, revalorisé de 1,001 en
  octobre 2015, les taux de 2008 et de 2009, avant juillet 2008 — et le
  partage avec un précédent conjoint, majoration comprise ; un témoin de
  simulation, `reversion_agent_sncf_minimum`. Le portage, rejoué sur les
  quatre témoins de la SNCF avec le paquet refait, rend leurs 822 valeurs au
  bit près, et les 883 témoins par `node --test` ; sur quinze décès de 2008
  à 2016, où jouent les taux de passage, il suit le Python à 3e-15 près.

**Ce que montrent les mesures.** L'agent du témoin neuf, né en 1958, parti à
57 ans à 55 % du salaire moyen, trois enfants, mort en mai 2023, avait une
pension de 16 107 € par an en euros de 2023, au-dessus du minimum de
15 867 € : sa réversion passe de 8 859 € à 9 425 €, 8 568 € de minimum et
857 € de majoration. La réversion ne bouge que pour les pensions qui
dépassent le minimum de moins de 8 % ; celles des autres témoins de la SNCF
gardent leur montant, et leur ligne dit le minimum garanti, 8 568 €. Sur les
883 témoins, aucune pension ne bouge, ni aucun rendu de page, ni les agrégats
de la page Coût.

**Ce qui reste**, une session par point :

1. *Le minimum de pension de l'agent* (article 15, I et IV), que le modèle ne
   porte pas : une fiche à naître, et ses conditions — toute pension
   d'ancienneté jusqu'en 2016 ; depuis le 1er janvier 2017 (décret
   n° 2011-291, article 18), sauf pour l'agent qui avait atteint son âge de
   liquidation avant, la durée du taux plein, l'âge d'annulation de la
   décote ou les liquidations du II de l'article 3 et des articles 4 et 5, et
   le total des pensions de droit direct, toutes liquidées, sous un plafond
   (IV). Il fera jouer de lui-même le minimum de la réversion de la pension
   qu'il relève.
2. *L'article 23*, au propriétaire (ci-dessous).
3. *Inchangés* : le plafond de 2027 ; la limite 5 ante ter (2), en fin
   d'étape ; la CNBF et la Cipav dans la fiche de paie ; les décrets qu'aucune
   marche ne rejoint ; la majoration pour trois enfants de la réversion du
   régime général hors de la cotisation du non-résident (note « réversion de
   la SNCF », « Trouvé en chemin ») ; au propriétaire, les décrets des
   exploitants de 1980 à 1989, au fac-similé.

**Au propriétaire : l'ASPA de l'article 23.** Le texte porte la réversion de
la personne seule de 55 à 64 ans au montant de l'ASPA « mentionnée à
l'article L. 815-9 », la caisse « sous conditions de ressources », sans dire
lesquelles. Deux choix l'attendent avant la moindre ligne. *Les ressources* :
la lecture différentielle — la réversion portée à l'ASPA d'une personne
seule moins ses autres ressources, comme l'allocation de L. 815-9, sur les
ressources que le survivant déclare —, que je recommande, ou le plancher
entier sous le plafond, ou une source à demander à la caisse. *La ligne*,
qui ne montre qu'un montant, à sa date d'effet : le plancher n'y joue que si
le survivant a de 55 à 64 ans ce jour-là, ou il s'écrit à part, daté, à 55
ans, comme la majoration de 11,1 % du régime général, et finit à 65 ans.

**Pour la session des pages.** La ligne de la SNCF portée au minimum dit
« portée au minimum de la réversion » (`MOTIFS_DE_REVERSION`), à juste
titre ; mais sa majoration n'y est plus « la moitié de la vôtre »
(`MAJORATION_REVERSEE`) : elle garde le taux de la vôtre, sur le montant de
la réversion relevée. Une retouche de `pages.js`, avec son test, quand
`ligne.motif === "minimum"`.
