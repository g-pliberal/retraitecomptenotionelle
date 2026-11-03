# Étape 9, suite : l'assiette du RCO et du NRCO, écrite dans les deux moteurs

**Le 3 novembre 2026, ce qui est fait.** Le propriétaire a décidé le même jour
de corriger le modèle, et non de déclarer une limite. Chaque texte que cite la
note de la lecture (`2026-11-03-etape-9-assiette-du-rco-des-artisans.md`) a
été relu dans l'index LEGI à jour du 2 novembre et dans l'index du JORF à jour
du 3, à sa version en vigueur ; les citations mot pour mot sont dans la fiche
`assiette_rco_independants`, lue au droit (`LUES_AU_DROIT`). Quatre commits sur
`main`, chacun son test vu rouge d'abord, dans le portage puis dans son jumeau :

1. *L'avant-dernière année du RCO des artisans* (f716130). Jusqu'aux
   cotisations de 2008, la cotisation est « assise sur les revenus
   professionnels non-salariés de l'avant-dernière année civile », « dans la
   limite d'un plafond égal à trois fois celui [...] en vigueur dans l'année
   où la cotisation est due » (décret n° 78-351, article 3, I ; D. 635-4 ;
   D. 635-2), sans ajustement (article 5, IV, qui ne rend applicables que les
   articles 12 à 14, 16 et 18 du décret n° 73-76) ; depuis les revenus de 2009,
   régularisée sur le revenu de l'année (décret n° 2008-1427, article 1er). Le
   conjoint collaborateur reste sur « le revenu retenu [...] pour le calcul de
   sa cotisation d'assurance vieillesse de base », sans régularisation
   (D. 635-10-2) : sans cette exception, la première version du commit ôtait
   29 % de la pension du témoin du conjoint d'artisan né en 1945. Une table du
   statut au décalage, `assiette_annee_de_revenu`.
2. *Les deux premières années de l'artisan* (f63fec0) : « le tiers du plafond
   visé au premier alinéa du I », puis « la moitié dudit plafond » (article 3,
   II ; D. 635-4 ; D. 635-7, « au tiers du plafond mentionné à l'article
   L. 241-3 » depuis 2004), jusqu'au décret n° 2011-2038 (article 3, II, 1°),
   qui les supprime en 2012. Le plafond est celui de la sécurité sociale, non
   l'assiette maximale : le III assied la cotisation de l'aide familial « sur
   un revenu égal au tiers du plafond visé au premier alinéa du I », et la
   caisse la calcule « sur le tiers du plafond de la sécurité sociale »
   (exposé « Rachat aide familial »). `assiette_de_debut`, les diviseurs du
   plafond ; les périodes de 2010 à 2012 du RCO coupées au 1er janvier 2012.
3. *Le NRCO des commerçants* (93906ff) : « La cotisation annuelle au régime
   complémentaire obligatoire d'assurance vieillesse est assise sur les revenus
   de l'avant-dernière année » (D. 635-2, rédaction du 24 août 2004), le
   régime que gère chaque caisse « chacune en ce qui la concerne »
   (D. 635-1) ; le gérant de débit de tabac, qui y cotise comme commerçant,
   aussi. Le décalage ne joue qu'une fois l'exercice ouvert depuis deux ans :
   le commerçant qui commence cotise sur « les revenus forfaitaires mentionnés
   au sixième alinéa de l'article L. 131-6 » (D. 635-10), dix-huit puis
   vingt-sept fois la base mensuelle des allocations familiales (R. 242-16),
   que L. 131-6 dit calculées « à titre provisionnel » puis régularisées ; le
   modèle, qui n'a pas cette base, garde le revenu de ses deux premières
   années, ce que donnerait la régularisation. Approximation déclarée.
4. *La cotisation additionnelle de 1985 à 1996* (1aa23ce) : « est due en sus
   [...] une cotisation additionnelle fixée à 0,10 p. 100 » (article 5, I,
   rédaction du 1er janvier 1985), et les points sont tirés de « la cotisation
   prévue à l'article 5-I, 1er alinéa » (article 6, I, même rédaction ;
   D. 635-7 de 1985) ; la caisse : « Cette cotisation n'etait pas génératrice
   de droit ». Une donnée : `taux_calcul_points` à 4,40 % sur la période de
   1985 à 1996, que les deux moteurs lisent déjà. La note de la période de
   1979 à 1984 cite désormais l'article 5, lu dans LEGI (LEGIARTI000006766105).

**Les valeurs des tests, posées à la main** (`tests/test_independants.py`) :
points = assiette × taux / revenu de référence de l'exercice
(`valeurs_point.csv`), plafonds de `plafond_securite_sociale.csv`.

| Cas | Assiette | Taux | Référence | Points |
|---|---|---|---|---|
| artisan depuis 1977, 1979 | revenu de 1977, 5 000 € | 4,40 % | 0,893351 | 246,2638 |
| 1980 | revenu de 1978, 6 000 € | 4,40 % | 1,003115 | 263,1802 |
| 1981 | revenu de 1979, 7 000 € | 4,40 % | 1,137270 | 270,8240 |
| 1982 | revenu de 1980, 40 000 €, borné à 3 × 12 504 € | 4,40 % | 1,282096 | 1 287,3669 |
| 1983 | revenu de 1981, 9 000 € | 4,40 % | 1,410153 | 280,8206 |
| 1984 | revenu de 1982, 10 000 € | 4,40 % | 1,544309 | 284,9171 |
| artisan depuis 2002, 2004 | revenu de 2002, 20 000 € | 6,70 % | 3,882 | 345,1829 |
| 2005 | revenu de 2003, 21 000 € | 7 % | 4,104 | 358,1871 |
| 2006 | revenu de 2004, 22 000 € | 7 % | 4,145 | 371,5320 |
| 2007 | revenu de 2005, 23 000 € | 7 % | 4,145 | 388,4198 |
| 2008 | revenu de 2006, 24 000 € | 7 % | 4,207 | 399,3344 |
| 2009 | revenu de 2009, 27 000 € | 7,1 % | 4,5 | 426,0000 |
| conjoint d'artisan, 2007 | 32 184 / 3 € | 7 % | 4,145 | 181,1725 |
| 2008 | 33 276 / 3 € | 7 % | 4,207 | 184,5591 |
| 2009 | 34 308 / 3 € | 7,1 % | 4,5 | 180,4347 |
| artisan installé en 1980, 1980 | 9 165 / 3 € | 4,40 % | 1,003115 | 134,0026 |
| 1981 | 10 482 / 2 € | 4,40 % | 1,137270 | 202,7698 |
| 1982 | revenu de 1980, 10 000 € | 4,40 % | 1,282096 | 343,1880 |
| installé en 2008, 2008 | 33 276 / 3 € | 7 % | 4,207 | 184,5591 |
| 2009 | 34 308 / 2 € | 7,1 % | 4,5 | 270,6520 |
| installé en 2011, 2011 | 35 352 / 3 € | 7,2 % | 4,79053 | 177,1094 |
| 2012 | revenu de 2012, 32 000 € | 7,2 % | 4,89113 | 471,0568 |
| reprise en 1998, 1998 | 25 776 / 3 € | 5,30 % | 2,878237 | 158,2135 |
| 1999 | 26 471 / 2 € | 5,70 % | 3,103862 | 243,0596 |
| 2000 | revenu de 1998, 20 000 € | 6 % | 3,282227 | 365,6054 |
| commerçant depuis 2001, 2004 | revenu de 2002, 16 000 € | 4 % | 13,89 | 46,0763 |
| 2005 | revenu de 2003, 17 000 € | 6,5 % | 14,112 | 78,3022 |
| 2006 | revenu de 2004, 18 000 € | 6,5 % | 14,389 | 81,3121 |
| 2007 | revenu de 2005, 19 000 € | 6,5 % | 14,648 | 84,3119 |
| 2008 | revenu de 2006, 20 000 € | 6,5 % | 14,809 | 87,7845 |
| 2009 | revenu de 2009, 23 000 € | 6,5 % | 15,3 | 97,7124 |
| artisan à 10 000 € depuis 1983, 1985 | 10 000 € | 4,40 % (et non 4,50) | 1,655596 | 265,7653 |
| 1996 | 10 000 € | 4,40 % | 2,344666 | 187,6600 |
| 1997 | 10 000 € | 4,90 % | 2,661760 | 184,0887 |

Le commerçant installé en 2005 a, en 2005 et 2006, les points de son revenu
de l'année (12 000 et 13 000 €), puis, en 2007 et 2008, ceux de ces mêmes
revenus ; le revenu de ses années 1985 et 1986, à l'artisan qui cesse en 1986,
ne change aucun point.

**Ce que la règle déplace.** Au portage, 31 des 929 témoins de simulation du
scénario 1 bougent, tous à la baisse, de 0,1 à 2,3 % de la pension, en médiane
1,2 % : les artisans et les commerçants dont une année tombe avant 2009.

*Corrigé le 3 novembre 2026, après la relecture R-M2*
(`2026-11-03-relecture-assiette-du-rco.md`, `2026-11-03-corrections-de-la-relecture-r-m2.md`) :
pas tous à la baisse, le forfait relevant l'artisane qui commence sous le tiers
du plafond (`dispense_rsa_releve_artisane`, 18 % de points du RCO de plus,
5,8 % de pension aux scénarios 3 et 5) ; et le conjoint collaborateur à
l'option cotise, de 2007 à 2012, sur la fraction du revenu du chef de
l'avant-dernière année, sa cotisation de base provisionnelle, que D. 635-10-2
ne régularise pas, et non sur celle de l'année, que le modèle lui prenait.

**Une autre décision du propriétaire, le 3 novembre 2026.** À Mayotte, en
2026, le modèle garde le décret : 150 € de cotisations par trimestre, et non
les 250 € du barème de la caisse, qui reste un écart déclaré
(`ECARTS_COTISATIONS_VALIDANTES_MAYOTTE`, et la fiche `mayotte_pension_de_base`,
qui le dit désormais).

**Ce qui reste, déclaré** (fiche `assiette_rco_independants`, ses
approximations ; `docs/limites/3-systeme-actuel.md`, « assiette de la
complémentaire des artisans et des commerçants »).

- *Le minimum de la cotisation*, « celui qui serait dû au titre d'un revenu
  égal au revenu minimum » du régime de base (article 3, I ; D. 635-4 ;
  D. 635-2 jusqu'en 2012), puis l'assiette du régime de base dès
  quatre-vingt-dix jours d'affiliation (LEGIARTI000025629861,
  LEGIARTI000025263548), 5,25 % du plafond en 2015 (LEGIARTI000030034575),
  plus rien en 2016 (LEGIARTI000031799392). La lecture de cette session ne
  l'établit pas dans toutes ses modalités — les rédactions de D. 633-2, le
  prorata de l'année incomplète, la condition de quatre-vingt-dix jours,
  D. 612-6, le micro-entrepreneur — : non écrit, comme le veut la consigne.
- *Le forfait du commerçant qui commence*, et celui de l'artisan de 2009 à
  2011 : régularisés ou non, aucun texte lu ne le dit.
- *La reprise d'activité* : le modèle tient pour un début d'exercice l'année
  qu'aucune année d'activité de la même affiliation ne précède, comme
  R. 242-16 le dit des cotisations de début d'activité ; le règlement du RCO de
  1978, que l'index ne porte pas, le dirait peut-être.
- *L'année incomplète* : le forfait et le revenu de l'avant-dernière année
  pris à proportion des mois de l'exercice, comme les bornes.

**La même erreur ailleurs** (`src/CLAUDE.md`, « la classe, pas le cas »), à
lire par les files qui en ont la charge, aucune n'étant de celle-ci : les
complémentaires des libéraux en cotisation proportionnelle, dont D. 642-3 assied
la cotisation de base sur l'avant-dernière année jusqu'en 2004 sans points
(`points_au_prorata_des_cotisations`, ses textes sans effet) : leurs statuts
ont-ils fait de même pour les points de la complémentaire ? Et les exploitants
agricoles : de quelle année est le revenu qui assied leurs points ? Ni l'un ni
l'autre n'a été lu ici.

Aucun fichier d'une autre file n'a été touché, hors des lignes de la règle dans
les fichiers partagés : `tests/test_carte.py` (`LUES_AU_DROIT`),
`scripts/construire_donnees.py` (deux champs de période),
`data/reference/textes/perimetre.yaml` (le cliquet, abaissé à 9 355).
