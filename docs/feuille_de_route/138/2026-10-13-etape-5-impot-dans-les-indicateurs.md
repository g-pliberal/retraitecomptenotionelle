# Étape 5, troisième partie : l'impôt sur le revenu dans les indicateurs de cycle de vie

**La demande.** Le propriétaire, le 13 octobre 2026 : l'impôt sur le revenu
dans les indicateurs de cycle de vie, `impot_revenu.py` branché dans
`cycle_de_vie.py` (point 1 de « Ce qui reste » des deux premières parties).
Pas l'effet retour, qui viendra après l'action 147, maîtresse de la page Coût.
D'autres sessions tournant en parallèle, ne toucher ni à `castypes.py`, à
`cas_types_csp.yaml` et à `grille_large.py` (action 152), ni à `cout.py`
(action 147), ni aux pages ; ce qui devrait s'y écrire va ici.

**Ce que disent les textes, lus le jour même dans les index de la DILA.**

- *Le bénéfice d'un indépendant* n'est pas un salaire : il s'impose sans
  l'abattement de 10 %, et l'article 158, 7, 1° du code général des impôts le
  multiplie par 1,25 pour qui n'adhère pas à un organisme de gestion agréé, de
  sa rédaction du 31 décembre 2006 (LEGIARTI000006307988) à son abrogation au
  1er janvier 2024 (LEGIARTI000042978882). Le module de l'impôt ne le calcule
  pas (`HORS_CHAMP`).
- *La majoration pour enfants* : « les majorations de retraite ou de pension
  pour charges de famille » sont exonérées par l'article 81 du code dès 1950
  (2°, LEGIARTI000048121406), puis par son 2° ter, jusqu'à la version du
  1er janvier 2014 qui l'abroge (LEGIARTI000027518339, puis
  LEGIARTI000028416932). L'annexe de la loi de financement de la sécurité
  sociale pour 2014 en annonce « l'inclusion […] dans l'assiette de l'impôt
  sur le revenu » (JORFARTI000028372842) ; l'article de la loi de finances
  pour 2014 qui la fait, et l'année de revenus qu'il vise, ne sont dans aucun
  des deux index.

**Ce qui est fait.**

- *Le foyer* (`cycle_de_vie.foyer_de_l_annee`) : une personne seule, sans
  enfant à charge, comme l'OCDE calcule ses taux nets, qui a au 31 décembre
  l'âge de sa génération — l'abattement des personnes âgées s'ouvre à 65 ans.
- *L'impôt de chaque année* (`impots_par_annee`) : le foyer déclare le salaire
  imposable de l'année (`revenus_imposables`) et la part imposable de ce que
  la pension sert dans l'année (`parts_imposables_par_annee`, `Flux.servi`),
  au barème de l'année, projeté au-delà des revenus de 2025 sur les prix ou,
  comme l'OCDE, sur le salaire moyen. L'année du départ, il déclare les deux,
  et leur impôt se partage au prorata des deux revenus après leurs
  abattements de 10 %. Chaque année de retraite se compte vécue en entier.
- *Les flux* (`flux_des_systemes(…, impot=…)`, `avec_l_impot`) portent
  l'impôt de chaque année, les revenus nets qu'il laisse et le dernier revenu
  net d'une année entière d'impôt, déclaré comme celui d'un actif, sans
  l'abattement des personnes âgées (`dernier_revenu_apres_impot`).
- *La convention* (`Convention.impot`, `convention_apres_impot`) : la
  convention nette, du dépôt ou du COR, après impôt. Tous les indicateurs la
  prennent : la pension de chaque année perd l'impôt qu'elle supporte, les
  revenus le leur ; les cotisations restent brutes, l'impôt ne les atteignant
  pas (CGI, art. 83). Le patrimoine reste en années de dernier revenu brut.
- *Le taux de remplacement après impôt au départ* (`remplacement_apres_impot`,
  et `Depart.remplacements_apres_impot` au balayage des âges) : une année
  entière de la pension du premier mois, nette de ses prélèvements et de son
  impôt, sur une année entière du dernier revenu, nette des siens : le taux
  net de l'OCDE.
- *Le module de l'impôt* : `impot_aux_parametres`, l'impôt d'un foyer aux
  paramètres d'une année ; `BaremesImpotRevenu.chronique`, ceux d'un siècle
  en une passe, chaque année projetée partant de la précédente, et non plus
  de 2025 — un siècle de barèmes coûte 5 à 10 ms.
- *Le script* : `python scripts/cycle_de_vie.py --impot [prix|salaire_moyen]`,
  sur la grille ou, avec `--ages`, au balayage, colonne « Rimp » ; le taux
  d'annuité et le remplacement sur le cycle de vie s'y impriment désormais.
- *Les tests* : huit dans `tests/test_cycle_de_vie.py` (l'impôt de chaque
  année est celui du module pour le foyer qui la déclare ; le partage de
  l'année du départ ; la pension après impôt ; le sens de chaque indicateur ;
  le taux de remplacement après impôt ; le barème projeté sur le salaire
  moyen ; l'indépendant et l'exploitant ; la convention), un dans
  `tests/test_impot_revenu.py` (la chronique), deux contre l'OCDE dans
  `tests/test_cycle_de_vie_references.py`.

**Trois décisions de la session, à confirmer par le propriétaire.**

1. *Le bénéfice d'un indépendant* (la question que laissait la deuxième
   partie) n'est pas imposé : ni l'abattement de 10 % ni la majoration de
   l'article 158, 7 ne sont au module. Ses revenus après impôt ne se
   calculent pas, ni ce qui s'y rapporte — taux d'annuité, remplacement sur
   le cycle de vie et au décès —, comme ceux d'un statut sans fiche de paie ;
   sa pension paie l'impôt, seule l'année du départ. L'artisan, la
   profession libérale et l'exploitant de la grille ont ainsi leur rendement
   et leur patrimoine après impôt, sans leurs taux rapportés aux revenus.
2. *La majoration pour enfants* s'impose à toute époque, faute de l'année que
   vise l'abrogation de son exonération ; elle ne touche que les pensions des
   parents de trois enfants, d'avant 2013 ou 2014, et aucun cas type de la
   grille (la carrière interrompue a deux enfants).
3. *Les années d'avant 1960*, sans barème lu, ne paient pas d'impôt : les
   deux premières années du smicard de la génération 1940, à 18 et 19 ans.

**Ce que montrent les mesures** (barème projeté sur les prix, convention
nette du dépôt). Le salarié au salaire moyen né en 1980, parti en 2044 : sa
pension perd 4,2 % de son brut chaque année de retraite à l'impôt, 5,2 %
l'année du départ, où elle s'ajoute à un mois de salaire ; son taux de
remplacement après impôt est de 72,7 % pour 59,1 % brut. Sur la grille, le
rendement réel du système actuel perd 0,11 à 0,20 point au salaire moyen (des
générations 1940 à 2000), 0,19 à 0,33 au fonctionnaire sédentaire, 0,40 à
0,56 au cadre, rien au smicard, dont la pension n'est pas imposable ; le taux
d'annuité monte, le salaire payant plus d'impôt que la pension (39,2 % au
lieu de 37,3 % au salaire moyen de 1970), sauf au smicard, dont la prime pour
l'emploi relevait le revenu de 2000 à 2015 (38,4 % au lieu de 39,1 %).
Un salarié moyen seul payait 10 à 12 % de son revenu imposable de 1975 à
1995, en francs comme en euros. L'impôt coûte 0,03 s à une carrière sous les
six systèmes.

**La confrontation à l'OCDE** (*Pensions at a Glance 2025*, salarié né en
2002, barème projeté sur le salaire moyen, l'OCDE tenant le système constant).
Sa pension brute — son taux brut fois le dernier revenu —, passée par les
prélèvements et l'impôt du dépôt, redonne son taux net à 0,4 point près :
69,6 % pour 70,0 % au salaire moyen, 59,2 % pour 58,9 % à deux fois. À la
moitié, ni pension ni salaire ne paient d'impôt, et le dépôt est 1,2 point
sous l'OCDE (64,9 % pour 66,1 %) : la pension y perd la CSG au taux plein,
quand un tel retraité ne la paierait pas — ce que l'OCDE ne fait pas non
plus, puisqu'elle trouverait alors plus de 70 %. Avec sa propre pension, le
dépôt donne 66,0, 66,8 et 54,3 % ; le rapport du net au brut est celui de
l'OCDE au salaire moyen (1,238 pour 1,237). Le patrimoine net de l'OCDE est
en années de salaire NET (14,3 pour 11,5 brut), et non brut comme le disait
l'en-tête de `cycle_de_vie.py`, corrigé : sa rente nette — patrimoine net sur
taux net — suit sa rente brute à 0,6 % près, celle du dépôt à 1,2 %, la
pension menée sur les prix descendant au fil de la retraite sous un barème
mené sur les salaires.

**Le registre.** Les points d'OpenFisca-France, d'Ines et d'EUROMOD (138.5)
disent que l'impôt entre dans les indicateurs, et restent `a_reprendre` pour
le net du site et l'effet retour ; celui de Typfallsmodellen (138.9), que le
taux de remplacement après impôt est fait, la pension par étage non ; les
deux des modèles de l'OCDE, que son taux net et son patrimoine net se
retrouvent — celui qui reproche au site son net sans impôt (138.2) reste
`a_reprendre`.

**Pour les pages** (la session du site, qui tient `pages.js` et `index.html`).
Le site affiche un net « avant impôt sur le revenu » (`pages.js`, près de la
ligne 2094). Il pourrait montrer, à côté du taux de remplacement net, le taux
après impôt d'une personne seule (`remplacement_apres_impot`), et, quand les
indicateurs de cycle de vie seront portés (étape 9, point 1), leur version
après impôt. Il faut d'abord le jumeau JavaScript de `impot_revenu.py` et de
`donnees/impot_revenu.py`, et le barème dans le paquet du site.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'effet retour de la page Coût*, après l'action 147 : l'ASPA, la CSG et
   l'impôt que les petites pensions des scénarios 2 à 5 ne paient plus.
2. *L'impôt au site*, avec son portage JavaScript (ci-dessus).
3. *Le bénéfice des indépendants* au module de l'impôt : la majoration de
   l'article 158, 7, et les règles d'avant 2006, à lire ; puis leurs revenus
   après impôt.
4. *Le taux de CSG d'une pension selon le revenu fiscal du foyer* (138.2), que
   le module donne désormais : l'écart à l'OCDE à la moitié du salaire moyen
   en dépend.
5. *L'année de revenus de l'imposition de la majoration pour enfants*, au
   texte de la loi de finances pour 2014.
6. *Les règles d'avant 1981 sans texte lu* (première partie, point 3).
