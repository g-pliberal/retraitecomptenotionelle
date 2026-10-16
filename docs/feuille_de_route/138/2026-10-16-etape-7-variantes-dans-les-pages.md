# Étape 7, cinquième partie : les hypothèses d'espérance de vie basse et haute dans les pages

**La demande.** Vague du 16 octobre 2026, session 1 : le point 1 de « Ce qui
reste » de la quatrième partie (note du 14 octobre) — la page Coût sous les
deux variantes, et les pages du simulateur (« Ce qui devrait s'écrire dans
les pages », note du 13 octobre). La fécondité, les migrations et la
mortalité différentielle n'en étaient pas.

**Ce qui est fait.**

- *Le champ de saisie* `esperance_vie` (`centrale`, `basse`, `haute`,
  centrale par défaut), dans les deux saisies (`saisie.py`, `saisie.js`) :
  lu parmi `HYPOTHESES_ESPERANCE_VIE`, écrit dans `hypothese_esperance_vie`,
  rangé dans `CLES_MODELISATION` avec son libellé dans
  `LIBELLES_MODELISATION` (`pages.js`). L'adresse ne le réécrit qu'écarté de
  la centrale : les adresses d'avant lui restent celles qu'elles étaient, au
  caractère près.
- *Le contrôle des réglages*, sous le scénario macroéconomique, « systèmes 2
  à 6 seulement », avec sa bulle. Le budget de mots du formulaire vierge ne
  bouge pas : les réglages sont repliés.
- *`courbeDeSurvie`* lit la mortalité du simulateur de la simulation
  (`comparaison.parametres`), non plus celle du simulateur par défaut : sous
  une variante, la courbe et la part encore en vie que la page cite sont
  celles du diviseur.
- *Ce que l'hypothèse pèse* (`poidsEsperanceVie`) : le dépliant des
  résultats rejoue la carrière sous les trois hypothèses et dit la pension
  mensuelle du système 2 sous chacune, même quand la carrière est tout
  entière observée, le diviseur lisant des quotients à venir. Pour un salarié
  né en 1975, parti en 2039 : 784,73, 734,46 et 679,36 € par mois, 15,5 %
  d'amplitude ; le système 1 ne bouge pas (vérifié au Python).
- *La page Coût* reste calculée sous la centrale (action 150), et porte une
  section de plus, « Si l'on vit plus ou moins longtemps » (`cout-esperance-vie`,
  au plan) : la dépense du bilan en 2050 et 2070, le solde en 2070 et le solde
  moyen 2026-2070 des quatre systèmes, sous les trois hypothèses, et ce que la
  variante déplace de la dépense à l'horizon (système actuel −1,25 et
  +1,31 point, proposition −0,04 et −0,01). Le tableau se lit d'une table
  figée par le Python, `esperance_vie` d'`agregats.json`
  (`figer_esperance_vie`, `EsperanceVieFigee` des deux côtés, le coût de
  chaque variante tiré de `memoire.cout`) ; le paquet passe à la version 22.
  La dépense est celle du bilan (`SoldeAnnuel.depense`), dont le solde est
  tiré, plutôt que celle de la trajectoire : les deux colonnes se lisent
  ensemble, à deux centièmes près des chiffres de la note du 14 octobre.
- *Les tests* : la table contre le modèle sous chaque hypothèse, les deux
  lecteurs, le refus d'une lecture absente (`test_agregats.py`) ; le plan de
  Coût et ses cinq tableaux de systèmes (`test_web_revues.py`). *Les
  témoins* : deux simulations (`esperance_vie_basse`, `_haute`), une page
  (`simuler_esperance_vie_haute`).

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les variantes de fécondité et de migration* de la page Coût, que le
   registre demande avec les mêmes figures du COR : les classeurs
   `11_fec_haute.xlsx` à `16_smi_bas.xlsx` de l'INSEE. Une fois là, le
   tableau de la page Coût se généralise (une table par composante), et le
   réglage du simulateur n'a pas à les suivre : elles ne touchent pas le
   diviseur.
2. *La mortalité différentielle* des cas types, *les départs qui suivent
   l'espérance de vie*, *la queue observée* de 85 à 98 ans, *2025* sous la
   loi seule : inchangés.
3. *À décider par le propriétaire* : si le rapport de dépendance sous chaque
   variante (0,568, 0,619, 0,673 en 2070) doit aussi s'écrire sur la page ;
   il n'y est pas.
