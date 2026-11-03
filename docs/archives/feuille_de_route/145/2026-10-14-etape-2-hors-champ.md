# Étape 2, deuxième partie : le Crédit foncier, l'ORTF et la CRFOM, lus et mis en fiches

**Le 14 octobre 2026 : trois fiches de règles pour les trois régimes hors champ
dont des assurés vivent encore — `credit_foncier_transfert_1989`,
`ortf_position_speciale_1974`, `crfom_regime_du_decret_1950` —, toutes
`pas_encore_modelisee`, et leurs lignes d'inventaire corrigées. Aucun moteur,
aucun chiffre ne bouge. La lecture change ce que l'inventaire disait de deux
d'entre eux : le Crédit foncier a un texte de transfert, lu, qui fixe la règle
de tous ses anciens agents depuis 1989 ; l'ORTF n'a jamais eu de régime de
base propre, seulement la position spéciale de ses agents les plus âgés.**

Demande du propriétaire, pour la session de nuit : « action 145, étape 2, les
régimes hors champ dont des assurés vivent encore — le Crédit foncier, l'ORTF,
la CRFOM —, documentés, non calculés, comme les huit fiches déjà faites de
l'étape ».

- *La méthode.* L'index LEGI et JORF du dépôt, mis à jour au 13 et au 14
  octobre, lu article par article ; les analyses du Journal officiel pour ce
  que LEGI ne porte pas. Rien hors de l'index.
- *Le Crédit foncier.* La loi n° 89-18 (article 13) met fin au régime spécial
  d'assurance invalidité et vieillesse au 1er janvier 1989 ; le décret
  n° 89-157, lu dans ses quinze articles, en fait le premier des trois
  transferts au régime général que l'étape 1 avait trouvés (Compagnie générale
  des eaux en 1991, CCI de Roubaix en 1998) : une rente du régime général de
  50 % du « salaire plafond moyen » de 1988 pour cent cinquante trimestres
  validés depuis le 1er juillet 1930, en cent-cinquantièmes au-dessous ; une
  pension d'invalidité de 30 ou 50 % de ce plafond ; des rentes différées pour
  les droits non liquidés, servies aux conditions du régime général. Le reste
  des droits est une retraite d'entreprise, la caisse de retraites du Crédit
  foncier (CRCFF), dont les provisions passent en 2009 à trois assureurs. Le
  barème du régime d'avant 1989 (décret du 6 août 1931) n'est pas dans l'index.
- *L'ORTF.* Ses agents relevaient du régime général et de l'IGRANTE (arrêté du
  5 décembre 1961), puis de l'Ircantec ; ses fonctionnaires détachés, du code
  des pensions civiles et militaires. Son seul droit propre est la position
  spéciale de l'article 30 de la loi n° 74-696 : les agents de soixante ans au
  31 décembre 1974, et ceux de cinquante-cinq ans à leur demande, reçoivent
  jusqu'à leur limite d'âge une rémunération égale aux pensions qu'ils auraient
  eues en y travaillant. Ce que l'État leur verse depuis, les « allocations
  supplémentaires de retraite », est une ligne du compte Pensions (532 000 € en
  2011, 58 000 € en 2026), dont la Cnav porte le solde depuis la loi de
  financement pour 2024 (L. 134-3, k). La fiche est bornée par la génération :
  née en 1919 ou avant.
- *La CRFOM.* La caisse intercoloniale de 1924 (article 71, lu) puis le décret
  n° 50-461 du 21 avril 1950, absent de l'index, connu par les textes qui le
  citent ; le maintien au régime de 1950 à l'intégration dans un corps (décret
  n° 59-1379, article 41, cité par R*2 du code des pensions civiles et
  militaires), la renonciation de 1966 ; puis l'affiliation d'office au code des
  pensions civiles et militaires au 1er janvier 1976, avec la limite d'âge du
  cadre et les bonifications de services hors d'Europe de l'article 9 (loi
  n° 75-1278, article 73).
- *Ce que le modèle ne fait pas.* Rien qu'il ne faisait déjà, puisque les trois
  régimes sont hors champ, mais trois écarts que la lecture nomme : les anciens
  agents du Crédit foncier entrés avant 1989 sont simulés au régime général sur
  toute leur carrière, quand leurs années d'avant 1989 valent une rente
  forfaitaire ; les derniers tributaires de la CRFOM, au code des pensions sans
  leur limite d'âge ni leurs bonifications ; les agents de l'ORTF en position
  spéciale ne sont pas simulés, ce qui ne touche que des personnes nées avant
  1920. Aucun statut ne porte ces carrières : au propriétaire de dire si le
  premier vaut un statut, comme ceux de la Compagnie générale des eaux et de la
  CCI de Roubaix, que l'étape 1 a laissés à modéliser.
- *Une observation sur le gabarit des transferts.* La rente pleine de la
  Compagnie générale des eaux (64 650 F en 1991) est voisine de la moitié du
  plafond annuel de 1990 ; celle de la CCI de Roubaix (62 150 F en 1998) est
  nettement en deçà de la moitié du plafond de 1997. La fiche du Crédit foncier
  le note à relire, sans rien en déduire.
- *Les tests.* Deux rédactions de la liste de contrôle des textes prennent un
  statut (R*2 du code des pensions civiles et militaires, article 6 du décret
  n° 53-711) : le cliquet descend à 9 774. `textes.py --inscrire`, lancé,
  aurait fait entrer trente-huit textes et un millier de rédactions « à
  examiner », pour l'essentiel ceux que citent les fiches du 13 octobre, que
  l'inscription n'avait pas pris : laissé à une session seule sur la liste, pour
  ne pas croiser dix-sept sessions sur le même fichier. `docs/regimes.md` est refait par son script.
  `test_carte.py`, `test_textes.py`, `test_donnees.py` et la suite rapide
  passent.
- *Ce qui devrait s'écrire dans les pages*, pour la session qui les tient :
  rien en dur ; la page Données lit les lignes d'inventaire corrigées.
- *Ce qui reste de l'étape 2.* L'outre-mer, le personnel navigant et les
  assemblées, à la fin de l'action 121 ; puis les limites de l'étape
  (`docs/limites/4-regimes-incomplets.md`), une fois, à sa fin.
