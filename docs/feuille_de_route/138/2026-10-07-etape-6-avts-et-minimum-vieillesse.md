# Étape 6 : l'AVTS, le trimestre d'avant 1972 et le minimum vieillesse d'avant 2007

**Reprise, au 7 octobre 2026.** Fait : le trimestre de 1946 à 1971 au salaire
de R. 351-9 — 18 F, puis le quart de l'AVTS au 1er janvier —, dans les deux
moteurs, sur les barèmes de la Cnav (`cnav_avts.py`), qui redonnent aussi au
centime le seuil au SMIC du dépôt de 1972 à 2026. Reste, dans cet ordre : le
minimum vieillesse de 1956 à 2006 à deux étages, AVTS et allocation
supplémentaire sous son plafond, au lieu du montant de 2006 ramené sur les prix
(les séries sont déjà dans `data/brut/cnav_avts.json`) ; les décrets du Journal
officiel qui le certifient ; la pension minimum d'avant avril 1983 ; R. 732-70 ;
l'outre-mer. Détail : plus bas, « Ce qui reste ».

**La demande.** L'étape 6 de l'action : « L'AVTS et le minimum vieillesse
d'avant 2007, au Journal officiel : la validation de 1949 à 1971, la série du
minimum de 1956 à 2006, le trimestre des DOM. » Le registre y rangeait huit
points, chez les barèmes de l'IPP, OpenFisca-France, OpenFisca-France-Pension,
Destinie 2 et un calculateur ouvert (calcul-verification-pension-retraite) : le
dépôt validait quatre trimestres à toute année travaillée avant 1972, en
écrivant qu'« aucun seuil de montant n'existait » ; il ramenait sur les prix le
minimum vieillesse de 2006 (1 195 € en 1970 au lieu de 442 €) ; il ignorait le
seuil de l'outre-mer ; il mettait le forfait à la place de l'AVTS dans R. 732-70.

**Ce que dit le droit, lu le jour même** (journal de veille du 7 octobre).

- *R. 351-9*, en vigueur (LEGIARTI000053335598) : de 1949 à 1971, « autant de
  trimestres d'assurance que le salaire annuel […] représente de fois le montant
  trimestriel de l'allocation aux vieux travailleurs salariés au 1er janvier de
  l'année considérée, avec un maximum de quatre trimestres par année civile ;
  jusqu'au 31 décembre 1962, ce montant est celui des villes de plus de 5 000
  habitants ». Ses rédactions de 1985 et de 2014 portaient aussi les années
  d'avant : 18 F de 1946 à 1948 ; avant, la retenue — 0,15 F par trimestre de
  1936 à 1941, autant de fois 0,15 F de 1942 à 1945, soixante cotisations
  journalières de 1930 à 1935. Celle de 2026 commence en 1949. L'article 71 du
  décret n° 45-0179 disait la même chose en anciens francs.
- *Les montants* : aucun article en vigueur ne les écrit. Le barème de la Cnav
  « Allocation aux vieux travailleurs salariés […] - Montant » date chacun depuis
  la loi du 14 mars 1941 et cite la loi, puis le décret qui le fixe ; celui de
  l'allocation supplémentaire, depuis le 1er avril 1956, pour un et pour deux
  allocataires ; celui de son plafond de ressources, pour une personne seule et
  pour un couple. Le Journal officiel, dans l'index du dépôt, en porte le texte
  depuis 1990 (décrets n° 90-265 et 90-266 : « 14800 F par an à compter du
  1er janvier 1990 », « 19920 F ») et, de 1970 à 1989, des notices qui portent
  souvent le montant (n° 70-879 : « 1750FRS PAR AN » au 1er octobre 1970 ;
  n° 80-1159 : « 8500FRS PAR AN A COMPTER DU 01-01-1981 », « MINIMUM VIEILLESSE:
  17000FRS ») ; avant 1970, les lois et les décrets n'y ont que leur titre.

**Ce qui est fait.**

- *Le récupérateur* (`scripts/fetch/cnav_avts.py`) lit les quatre barèmes de la
  Cnav — AVTS, allocation supplémentaire, son plafond, salaire validant un
  trimestre — et écrit chaque montant daté, en euros, avec sa référence, et le
  montant en vigueur au 31 décembre de chaque année. Il refuse d'écrire si le
  barème des seuils ne redonne pas, de 1949 à 1971, le quart de l'AVTS au
  1er janvier au centime ; si, de 1972 à 2026, il n'est pas 200 puis 150 SMIC
  horaires du dépôt au centime — ce qui recontrôle le seuil que le modèle
  calcule depuis 1972 ; si un montant baisse ; si les décrets n° 70-879,
  80-1159, 90-265 et 90-266 et l'ancre de 2006 de D. 815-1 (7 323,48 €, la somme
  des deux étages) ne s'y retrouvent pas.
- *Le seuil de 1946 à 1971* entre dans `salaire_validant_trimestre_avant_1972.csv`,
  au niveau `haute`, certifié contre le récupérateur (`verifier_donnees.py`) ;
  le modèle (`DonneesMacro.trimestres_valides`) et son portage (`trimestresValides`)
  le lisent : 85 F en 1949, 180,95 F de 1956 à 1962 — les 800 F d'avril 1962 ne
  comptent qu'en 1963 —, 437,50 F en 1971. Neuf décimales d'euro, pour qu'un
  salaire qui tombe pile sur le seuil le valide. Avant 1946, quatre trimestres
  encore : la règle s'y lit sur la retenue.
- *La fiche* `trimestres_avant_1972`, `approchee` (l'outre-mer, et avant 1946),
  l'écart du salaire annuel moyen récrit, trois points du registre `repris`.
  Un test dans chaque moteur.
- *L'effet* : quatre trimestres demandaient de 9 à 14 % du salaire moyen, un
  seul de 2 à 3,5 % ; aucun des 737 témoins ne bouge.

**Ce que la vérification a trouvé.**

- Le barème des seuils porte 216 anciens francs pour 1946 ; le texte en écrit
  1 800 de 1946 à 1948. Le texte est retenu, l'écart déclaré par le récupérateur.
- Les deux barèmes de la Cnav qui portent le seuil de l'outre-mer
  (« Salaire validant un trimestre » et « AVTS - Validation des années de
  salariat ») intervertissent les colonnes des Antilles et de La Réunion de 1975
  à 1991. Le premier met La Réunion plus bas, comme OpenFisca et l'IPP ; à
  trancher au décret du SMIC de chaque département.
- Des notices du Journal officiel se trompent : celle du décret n° 82-1142 écrit
  10 300 F au 1er janvier 1983, moins que les 10 900 F de juillet 1982 (le barème :
  11 300 F) ; celle du n° 74-1126, le 1er avril 1975 pour une date du 1er janvier ;
  celle du n° 79-567, 1969 pour 1979 ; celle du n° 79-1057, le 1er septembre 1979
  quand le barème dit le 1er décembre. Une notice n'est pas le texte : elle ne
  certifie que ce qu'elle redit.
- Le montant pour deux allocataires baisse en 1992 : il était le double de celui
  d'un seul, il devient celui du ménage (décret n° 92-50).

**Ce qui reste.**

1. *Le minimum vieillesse de 1956 à 2006.* Avant l'ASPA, il tenait en deux
   étages : l'AVTS, ou ce qui en tenait lieu (la majoration de L. 814-2 portait
   une petite pension au même montant), et l'allocation supplémentaire, réduite
   de ce que les ressources dépassent son plafond — qui valait bien plus que la
   somme des deux étages dans les années 1960 et 1970 (4 500 F contre 3 000 F
   fin 1970). Le modèle sert une allocation différentielle jusqu'au montant de
   2006 ramené sur les prix : il faut la règle à deux étages, pour une personne
   seule, deux allocataires et un couple dont un seul l'est, dans les deux
   moteurs (`droit/foyer.py`), sur les séries du récupérateur.
2. *Le Journal officiel* : certifier chaque montant que le texte ou la notice
   redit, décret par décret, avec les rédactions de LEGI des décrets de 1981 à
   1985 (n° 81-1166, 82-561, 82-1142, 83-551, 84-92, 84-643, 84-1288, 85-784).
3. *La pension minimum d'avant le 1er avril 1983*, au montant de l'AVTS, que la
   fiche du minimum contributif renvoie ici.
4. *R. 732-70* : l'AVTS au lieu du forfait (`droit/acquerir.py`).
5. *L'outre-mer* : le seuil des Antilles, de la Guyane et de La Réunion, avec un
   champ de saisie, que la session du site posera.
