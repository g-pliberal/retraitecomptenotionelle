# Étape 17, huitième partie : la pension maximale du régime général

**Le 8 octobre 2026, la demande.** Le propriétaire : « Reste de l'étape 17 : la
pension maximale du régime général, les taux pleins de L. 351-8, puis les
majorations pour enfants à charge et pour conjoint à charge. » La première :
le dépôt ne bornait aucune pension du régime général, avant 1983 ni après, quand
OpenFisca-France-Pension la borne à la moitié du plafond (registre, chantier
138.17), et la fiche `decote_avant_1983` laissait la question ouverte depuis le
27 septembre.

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre ;
fiche `pension_maximale_regime_general`).

- *Aucun article du code ne l'écrit* : ni R. 351-27, ni R. 351-29, ni la surcote
  de D. 351-1-4. La fiche F21552 de service-public cite l'arrêté du 9 octobre
  1986, en vigueur, dont l'article 2 interdit à la revalorisation de « porter
  une pension ou une rente de vieillesse à une somme supérieure à 50% du
  plafond », pourcentage « majoré de 1,25% par trimestre d'ajournement » pour
  les liquidations d'après soixante-cinq ans et d'avant le 1er avril 1983, et
  « compte tenu des coefficients de majoration acquis » pour qui avait passé
  soixante-cinq ans à cette date ; l'arrêté du 8 janvier 1986 dit de même.
- *De 1972 à 1974*, l'article 72-1 du décret de 1945 renvoie le maximum à un
  arrêté, celui du 28 janvier 1972, que la circulaire Cnav n° 2/72 transcrit :
  44 %, 46 % puis 48 % du plafond, majorés de 1,10, 1,15 et 1,20 % par trimestre
  d'ajournement — le maximum suit le taux, au même coefficient.
- *Le barème de la Cnav*, « Montant maximum de la retraite personnelle », lu par
  son API : 92 dates de 1949 à 2026, 40 % du plafond jusqu'en 1971, 50 % depuis
  1975, au franc près les années où le plafond ne change pas. Il porte en 1965
  la valeur de 1966 : le plafond de 1965, certifié au Journal officiel, en donne
  une autre.
- *La surcote* : en 2004, la Cnav ne ramenait pas au maximum la pension surcotée
  (circulaire n° 2004-37) ; depuis la lettre ministérielle du 1er septembre
  2006, elle ramène au maximum la pension calculée, puis y applique la surcote,
  qui le passe (circulaire n° 2007-5), pensions en cours comprises.
  OpenFisca-France-Pension calcule la surcote sur la pension non bornée.

**Ce qui est fait.**

- *La fiche*, cinq versions lues par les deux moteurs à la date d'effet :
  aucun maximum avant 1949 ; 40 % du plafond, supposée sur le barème ; l'arrêté
  du 28 janvier 1972 ; 50 % de 1975 à 1985, supposée sur le barème et la
  circulaire n° 22/83 ; les arrêtés de 1986. Le maximum se compte sur le plafond
  de l'année de la date d'effet, la moyenne de ses deux semestres de 1982 à
  1996 (approximation déclarée), et non sur le barème, qu'un test confronte.
- *Le modèle* (`droit/liquider.py`, son jumeau) : `pension_maximale` ; la
  pension calculée ramenée au maximum que multiplie le coefficient de
  l'ajournement d'avant 1983, du taux acquis au 31 mars 1983 ou de la surcote,
  la formule le disant ; `taux_acquis_l_emporte` compare les deux pensions de
  la circulaire n° 22/83 chacune ramenée à son maximum ; la pension entière que
  la majoration des assurés handicapés ne passe pas est bornée aussi (D. 351-1-5,
  II).
- *L'exemple* : le deuxième cas de la circulaire n° 22/83 se rejoue au plafond
  — 55 % du plafond, les 48 906 F de la circulaire —, le salaire du témoin, 1,06
  plafond, passant le maximum comme le sien ; le troisième reste un écart connu,
  son salaire de 1,7 plafond ne se reconstruisant pas, et un test le tranche
  avec les chiffres de la circulaire.
- *Les tests* : `test_pension_maximale.py`, le barème à trente dates, les trois
  cas de la circulaire n° 22/83, l'ajournement de 1982 et le taux acquis de
  1983, les deux moteurs ; le test de la loi Boulin passe sous le maximum, qui
  ramenait sa mère de huit enfants au salaire moyen de 1973 à 1975.

**Les mesures.** Le maximum mord quand le salaire annuel moyen passe le
plafond de l'année : de 1973 à 1990 pour une carrière au plafond ou au-dessus
du salaire moyen, les salaires portés au compte s'étant revalorisés plus vite
que le plafond — 1,14 plafond pour un cadre parti en 1985, 1,09 en 1990 —, et
plus guère après 1995, 0,94 plafond. Un témoin bouge, aux scénarios 1, 3 et 5 : le cadre né en 1926,
deux salaires moyens, préretraité du FNE de 1982 à 1985 et parti à soixante ans
en 1986, dont le salaire annuel moyen de 1,11 plafond est ramené à 8 552,50 €,
−5,95 %. La dépense de 1990 que la grille reconstitue s'écarte de −24,1 % au
lieu de −24,0 %, celle de 2000 de −14,7 au lieu de −14,6 ; l'écart du scénario
2 au passé, de −79,1 % au lieu de −79,2. Le portage concorde sur les 763
témoins.

**Ce qui reste.**

1. *Les autres régimes* : le maximum des salariés agricoles, que leurs textes
   nomment, celui des artisans et des commerçants, et celui de la pension unique
   des régimes alignés qu'un autre que le régime général liquide.
2. *Les textes de 1949 à 1974* : la loi n° 49-244, article 2, que la base de la
   Cnav cite, et les décrets du barème ; si le maximum suivait l'ajournement
   avant 1972, que la fiche suppose.
3. *Les arrérages* : le maximum bornait aussi, avant 1987, la pension
   revalorisée ; le modèle ne borne que la pension liquidée.
4. *De l'étape 17, ensuite* : les taux pleins de L. 351-8, les majorations pour
   enfants à charge et pour conjoint à charge.
