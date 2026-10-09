# Étape 9, quatrième partie : les prélèvements de chaque année, les primes sur la fiche de paie, le net du scénario 6

**La demande.** Le propriétaire, le 9 octobre 2026, après la troisième partie :
« Résous les limites ». Celles qu'elle laissait : les pensions et les salaires
nets des seuls prélèvements de 2026, quelle que soit leur année ; le revenu net
du scénario 6 lu sur la fiche de paie du droit en vigueur, quand le site prend
celle de la proposition ; la fiche de paie du site, qui prélevait la retenue
pour pension sur les primes d'un fonctionnaire.

**Ce que disent les références, lues le jour même.**

- *Les barèmes de l'IPP* (`baremes.ipp.eu`, en CSV). La CSG des pensions :
  1,1 % en février 1991, 2,4 % en juillet 1993, 3,4 % en 1997, 6,2 % en 1998,
  6,6 % en 2005, 8,3 % en 2018 ; un taux réduit de 1 % en 1997, de 3,8 % depuis
  1998 ; un taux médian de 6,6 % depuis 2019. La CRDS, 0,5 % depuis le
  1er février 1996 ; la CASA, 0,3 % depuis le 1er avril 2013. La cotisation
  maladie des pensions : 1 % pour le régime général et 2 % pour les
  complémentaires au 1er juillet 1980, 1,4 et 2,4 % en 1987, 2,6 et 3,6 % en
  1996, 2,8 et 3,8 % en 1997, rien et 1 % depuis 1998, quand la CSG monte des
  mêmes 2,8 points. Pour les salaires : la CSG d'activité et son abattement ;
  la maladie salariale du privé, 5,5 % en 1980, 6,8 % en 1991, 0,75 % en 1998,
  supprimée en 2018 ; le veuvage, 0,1 % de 1981 à juin 2004 ; l'assurance
  chômage salariale, née en 1959, 2,4 % de 2003 à 2017, 0,95 % de janvier à
  septembre 2018, rien ensuite ; la maladie des agents de l'État et des
  collectivités, jusqu'en 1997 ; la contribution exceptionnelle de solidarité
  des agents publics, 1 % de 1982 à 2017. Chaque ligne d'un barème est une
  photographie des taux en vigueur : une cellule vide après une valeur dit une
  suppression, même quand la ligne en porte d'autres.
- *TRAJECTOiRE* (commit `0963b57`, lu sans être copié : EUPL) :
  `calculeRemuNette` et `calculePensionNette` prélèvent ces taux à leur année,
  la pension au taux de sa catégorie de CSG, la maladie de 1 % sur
  l'Agirc-Arrco quelle que soit la catégorie.
- *La saisie du site* : le revenu d'un fonctionnaire est sa rémunération
  entière, et sa « part de primes » l'assiette de la RAFP ;
  `PeriodeRegime.part_du_revenu` réserve au traitement l'assiette
  `hors_primes` de la pension civile et de la CNRACL, pour le compte comme pour
  le scénario 1. La fiche de paie l'ignorait.

**Ce qui est fait.**

- *Les primes sur la fiche de paie* (`remuneration.bloc_droit_en_vigueur` et son
  jumeau `blocDroitEnVigueur`) : un régime d'assiette `hors_primes` n'y prélève
  que la part hors primes, salarié et employeur, et la conversion du net saisi
  en brut suit la part de primes de la saisie. Sur la page de la RAFP, la
  retenue passe de 432,25 à 345,80 € par mois, le net de 3 090,75 à
  3 177,20 €, et ce que la proposition ajoute de 1 139 à 1 053 € ; dans le
  README, la fonctionnaire de l'exemple gagne +33,1 % de traitement net au lieu
  de +36,9 %, le militaire +38,3 % de solde au lieu de +42,2 %. La limite 5 ter
  de la fiche de paie est récrite, avec son procès-verbal.
- *L'histoire des prélèvements* : `scripts/fetch/ipp_prelevements_sociaux.py`
  écrit `legislation/prelevements_historiques.yaml`, 164 marches, chacune avec
  la référence que l'IPP cite ; `donnees/prelevements_historiques.py` la lit,
  mois par mois, une année qui change de taux prélevant la moyenne de ses mois.
  Au manifeste : `ipp_prelevements_sociaux`.
- *Les pensions nettes de chaque année* (`cycle_de_vie.prelevements_par_annee`,
  `Convention.prelevements`) : au taux plein de CSG, la maladie du régime
  général sur sa part de la pension, celle des complémentaires sur la leur ;
  rien avant le 1er juillet 1980.
- *Les salaires nets de chaque année* (`revenus_nets`) : la fiche de paie de
  l'année, ramenée aux prélèvements hors retraite de son année, et aux
  contributions d'équilibre de son année au lieu de la CEG et de la CET
  (`contributions_equilibre.part_salariale_annualisee`). Le rapport du net au
  brut du salarié du privé au salaire moyen : 0,872 en 1980, 0,789 en 1995,
  0,778 en 2017, 0,786 en 2018, 0,790 en 2024 ; d'un fonctionnaire à un
  cinquième de primes : 0,914, 0,844, 0,830, 0,820, 0,816.
- *Le scénario 6* : de la bascule au départ, son revenu net est celui que laisse
  la fiche de paie de la proposition, son rapport du net au brut appliqué au
  revenu de l'année, comme `contexte.Montants`.
- *Les tests* : `tests/test_prelevements_historiques.py` (rapide, 8 cas : la
  dernière marche de chaque série est le barème du site, les marches et les
  suppressions connues, la moyenne des mois, le net de l'année courante égal à
  la fiche) ; deux cas dans `tests/test_remuneration.py`, un dans
  `tests/test_cycle_de_vie.py` ; la confrontation à TRAJECTOiRE, récrite.
- *Le registre* : le point de l'IPP, repris ; celui de TRAJECTOiRE, à jour.

**Ce que montrent les confrontations.**

- *TRAJECTOiRE.* Chaque net aux prélèvements de son année, son taux de
  remplacement net se retrouve à 1,5 % près sur 70 des 75 cas du témoin en
  euros constants, à 2 % près en salaire moyen. Les quatorze départs d'avant
  2018, qui s'écartaient de 1,2 à 3,7 %, sont à 0,996 à 1,001 fois le sien ; le
  policier (cas 8), à 0,985 à 0,997 fois, concorde aussi : l'écart tenait aux
  taux de l'année, non à l'indemnité de sujétions spéciales. Reste déclarée
  l'aide-soignante (cas 9, 0,945 à 0,985 fois), dont TRAJECTOiRE assied une
  retenue sur la prime spéciale de sujétion ; le cas 3, chômé avant son
  départ, ne se compare qu'en euros constants.
- *Le rendement interne réel net* du salarié au salaire moyen gagne 0,06 point
  pour la génération 1940, partie en 2000, 0,02 pour 1950, rien à partir de
  1960 ; celui du cas type n° 2 du COR, 0,01 point pour 1955, rien ensuite :
  l'écart au COR des générations 1963 à 1970 ne tient pas aux prélèvements.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'écart au COR du rendement des générations 1963 à 1970*, commun au régime
   général et à l'Agirc-Arrco : les projections du dépôt d'abord — le salaire
   moyen, la valeur de service —, puis les carrières.
2. *L'âge d'équilibre* : l'ETK, le simulateur de pilotage.
3. *Le portage et l'affichage*, avec l'étape 10 : les jumeaux JavaScript de
   `cycle_de_vie.py`, de `prelevements_historiques.py` et de
   `contributions_equilibre.py`.
4. *La génération 1941*, aux données.
5. *Hors de l'étape* : la prime spéciale de sujétion des aides-soignants dans
   l'assiette de la retenue, à la session des données ; la maladie des
   pensions des régimes de base autres que le régime général, que l'IPP
   n'écrit pas ; le taux de CSG d'une pension selon le revenu fiscal du
   foyer, que la convention du taux plein écarte ; l'indemnité compensatrice
   de la hausse de la CSG des agents publics depuis 2018, et la cotisation de
   la RAFP, absentes de la fiche ; les prélèvements hors retraite d'un
   indépendant avant l'année courante ; l'ancrage des marches de l'IPP au
   Journal officiel, avec l'index de la DILA.
