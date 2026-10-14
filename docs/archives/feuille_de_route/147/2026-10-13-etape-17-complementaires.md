# Étape 17, le privé sous le COR au milieu de la période : un écart de têtes à l'Agirc-Arrco, que la grille ne peut pas suivre

**Le 13 octobre 2026 : rien ne change dans le modèle. Les complémentaires
finissent 6,3 % sous le COR en 2050 et 7,3 % en 2055 et 2060. Ce n'est pas la
pension par tête de l'Agirc-Arrco, que la grille fait reculer moins que le
COR, mais ses retraités : le classeur par régime du COR en compte 44,6 % de
plus en 2050 qu'en 2025, la grille 25,0 %. Aucune pondération n'y fait rien,
mesuré ; il y faut des carrières dont la part passée au privé change d'une
génération à l'autre, c'est-à-dire la grille, que tient l'action 152. Une
sonde dit désormais l'écart, et la limite 5 ter le porte.**

- *Mesuré d'abord*, sous les réglages de la page (`memoire.cout`, Python 3.11),
  l'écart au COR de la dépense de chaque groupe, réversion comprise, depuis
  2025, et la dérive :

  | | 2030 | 2035 | 2040 | 2045 | 2050 | 2055 | 2060 | 2065 | 2070 |
  |---|---|---|---|---|---|---|---|---|---|
  | LURA | +1,1 | −1,5 | −0,6 | −1,7 | −2,0 | −2,0 | −1,4 | −1,5 | +0,2 |
  | complémentaires | +1,1 | −2,6 | −2,8 | −4,5 | −6,3 | −7,3 | −7,3 | −6,2 | −4,6 |
  | non-salariés de base | +0,1 | +6,5 | +9,0 | +8,3 | +6,4 | +2,6 | −2,0 | −5,0 | −5,3 |
  | FPE | +5,0 | +6,2 | +8,9 | +8,5 | +11,5 | +15,5 | +20,2 | +24,9 | +24,8 |
  | CNRACL | −3,3 | −3,6 | −3,6 | −5,0 | −4,6 | −4,3 | −2,8 | −1,4 | +1,5 |
  | régimes spéciaux | −1,4 | −4,4 | −4,9 | −5,4 | −3,0 | −4,1 | −6,0 | −18,7 | −34,6 |
  | dérive | 1,012 | 0,991 | 0,997 | 0,984 | 0,980 | 0,979 | 0,986 | 0,990 | 1,004 |

  Les complémentaires pèsent près de trois dixièmes de la dépense : leurs six
  points font 1,8 des deux de la dérive de 2050 (0,979 au 6 octobre), la FPE
  au-dessus et LURA au-dessous se compensant.
- *Le classeur de 2024 et le rapport de 2026 ne disent pas la même chose.*
  Le classeur par régime du COR (`scripts/fetch/cor_regimes.py`, relu ce
  jour : 53 232 valeurs, 37 blocs, non gardé) fait baisser la dépense des
  complémentaires de 2025 à 2050, ×0,961 en part de PIB, quand la figure 2.6
  du rapport de juin 2026 la fait monter, ×1,033 ; LURA, ×1,122 contre ×1,175.
  Le modèle donne ×0,968 aux complémentaires : à 0,8 % du classeur, 6,3 %
  sous le rapport. Régime par régime, de 2025 à 2050, le modèle (le
  classeur) : Agirc-Arrco ×0,915 (×0,936), Ircantec ×1,156 (×1,365), RCI
  ×1,303 (×1,439), complémentaire des libéraux ×1,425 (×0,901), MSA ×0,745
  (×0,606). L'exercice de 2026 relève les complémentaires de 7,5 % en 2050 et
  LURA de 4,7 % ; le modèle en suit les hypothèses économiques et le pilotage
  de l'Agirc-Arrco (étape 4), et reste pourtant au niveau du classeur.
- *Ce qui manque : des têtes, non une pension par tête.* L'Agirc-Arrco, de
  2025 à chaque année ; le COR de 2026 n'en publie que le rapport des
  cotisants aux retraités (figure 2.7), ses retraités s'en tirent par les
  cotisants du classeur (« 2026 » ci-dessous) ; `f` est la part de la pension
  moyenne que la grille sert à l'Agirc-Arrco que les retraités qui lui
  manquent devraient toucher pour que la dépense suive (classeur, 2026) :

  | | têtes, modèle | classeur 2024 | 2026 | pension relative, modèle | COR 2026 | `f` |
  |---|---|---|---|---|---|---|
  | 2030 | 1,068 | 1,109 | 1,146 | 0,942 | 0,937 | 0,86 ; 0,93 |
  | 2040 | 1,164 | 1,308 | 1,320 | 0,846 | 0,816 | 0,68 ; 0,70 |
  | 2050 | 1,250 | 1,446 | 1,492 | 0,769 | 0,729 | 0,62 ; 0,68 |
  | 2060 | 1,322 | 1,544 | 1,667 | 0,715 | 0,654 | 0,41 ; 0,59 |
  | 2070 | 1,402 | 1,646 | 1,878 | 0,683 | 0,581 | −0,01 ; 0,41 |

  La part des retraités qui touchent une pension de l'Agirc-Arrco passe de
  74 % en 2024 (DREES : 12,80 millions sur 17,30) à 92 % en 2050 (classeur,
  rapporté aux personnes du rapport de 2026), celle de la Cnav de 85 % à 92 %.
  Dans la grille, chaque carrière du privé a les deux régimes et aucune autre
  n'a l'Agirc-Arrco : la part reste celle d'aujourd'hui. Le passé ne le
  montrait pas : de 2010 à 2025, les têtes de l'Agirc-Arrco croissent de 29 %
  dans le modèle, de 32 % au COR ; la dépense du modèle, elle, de 28 % en part
  de PIB, celle du classeur de 5 % — l'affaire du deuxième point de la
  reprise, le passé.
- *Ce que `f` dit.* Au début de la période, les retraités qui manquent
  devraient toucher presque une pension moyenne : des carrières du privé
  presque entières, non des passages. Vraisemblablement les femmes des
  générations de l'après-guerre, dont les années validées sans cotisation —
  l'assurance vieillesse des parents au foyer, les majorations pour enfants —
  comptent à la Cnav et non à l'Agirc-Arrco (EIR 2020 : 28 années cotisées
  pour 36 validées chez les femmes, 35 pour 40 chez les hommes), quand la
  complétude de l'étape 14, une durée validée, pèse les deux régimes de la
  même façon. Ensuite `f` baisse : des passages de plus en plus courts, ceux
  des polypensionnés. L'hypothèse n'est pas mesurée : le dépôt n'a pas la
  durée cotisée par génération.
- *Essayé, hors du dépôt, et écarté* (complémentaires et LURA en 2050, dérive
  de 2050 et de 2070) :
  (a) la Cnav prolongée par le COR (`CAISSES_PROJETEES`) : −6,1 et −1,6 %,
  0,982 et 1,005 ; (b) l'Ircantec : −7,8 et −2,2 %, 0,974 et 0,993 ;
  (c) le contractuel, l'artisan et le libéral en polypensionnés — trente,
  vingt et dix années de salariat du privé avant leur régime
  (`grille_large.elargi(cas, avant=…)`) : −8,1 %, têtes de l'Agirc-Arrco
  ×1,255 ; (d) les mêmes, l'Ircantec, le RCI et la CNAVPL prolongés par le
  COR : −7,4 %, têtes ×1,236, non-salariés de base +24,7 % ; (e) les deux
  fonctionnaires avec dix années de salariat du privé : −7,7 %, et la dépense
  de la FPE +25,4 %, le calage de 2025 relevant leur coefficient. Pourquoi :
  les poids sont des parts de PERSONNES, et le COR compte un polypensionné
  dans chacun de ses régimes ; les têtes de l'Agirc-Arrco de la grille ne
  croissent qu'avec la part de personnes des carrières qui l'ont, que ces
  conventions ne relèvent pas, ou qu'elles prennent au privé. Et peser la
  seule part Agirc-Arrco d'une carrière ferait comparer au rapport de masses
  deux populations, les systèmes notionnels gardant les carrières entières.
  Fermer l'écart de têtes avec des carrières du privé entières le
  dépasserait, de ce que la pension par tête de la grille passe celle du
  COR : 5 % environ sur l'Agirc-Arrco en 2050.
- *Ce qui est fait.* La sonde `decomposition` dit les retraités d'un régime
  (`facteur=retraites&groupe=…`) : ses têtes dans le modèle, ceux du
  classeur par régime chez le COR (`CAISSES_DES_REGIMES_COR`,
  `mesures_prose.py`). La limite 5 ter porte un paragraphe de plus, ancré sur
  elle. Aucun calcul ne bouge, aucun témoin, aucun rendu de page.
- *Ce qui reste, à la grille* (l'action 152 tient `castypes.py` et
  `grille_large.py`) : des carrières dont la part passée au privé change
  d'une génération à l'autre. (1) La part cotisée des carrières des femmes
  des générations anciennes : une complétude par régime — cotisée pour
  l'Agirc-Arrco et les systèmes notionnels, validée pour la Cnav —, sur la
  durée cotisée par génération ; la DREES publie les caractéristiques de deux
  générations (« nés en 1950 », EIR 2016 ; « nés en 1953 », EIR 2020) et de
  deux stocks (EIR 2016 et 2020), dont il faut voir s'ils la portent, et la
  figure 3.23 du rapport de 2026, pension des femmes et des hommes par
  génération, servirait de contrôle. (2) Les polypensionnés des
  régimes statutaires et non salariés, génération par génération — l'EIR 2020
  en compte 68 % à la CNRACL, 42 % chez les civils de l'État, 33 % chez les
  militaires, la moitié dans les régimes spéciaux, 60 % chez les exploitants,
  82 % chez les libéraux. (3) Les poids de l'Ircantec, du RCI et de la
  CNAVPL, faits surtout de passages, que le COR fait croître de 82, 94 et
  111 % d'ici 2050 : la croissance des polypensionnés. Les années qui
  précèdent l'entrée du fonctionnaire (de deux à huit, étape 11), au privé
  plutôt que contractuelles, ne déplaceraient guère les complémentaires : les
  deux régimes y sont.
- *Pour les pages* (non écrit ici : une seule session les tient). La page
  Coût, au point « Le modèle compte des générations, non des personnes »,
  dit que les effectifs « sont ceux des caisses, où un polypensionné compte
  dans chacune des siennes ». Elle pourrait ajouter : « Et chaque carrière
  n'a qu'un régime principal : la part des retraités qui touchent une
  complémentaire du privé y reste celle d'aujourd'hui, quand le COR la fait
  monter. C'est ce qui laisse le privé quelques points sous le COR au milieu
  de la période », avec la dérive de 2050 (sonde `derive_cor?annee=2050`) ou
  les deux croissances de la limite 5 ter (sonde `decomposition`). Aucun
  chiffre de la page ne bouge.
- *Reproduire.* Les mesures lisent `memoire.cout(Parametres(), assiette=False,
  convention_recette=CONVENTION_RAPPORT)` et `Avenir.decomposition_groupes` ;
  le classeur, `data/brut/cor_regimes.json` après `cor_regimes.py`. Les
  variantes remplacent `Simulateur.effectifs` par
  `EffectifsRetraites(racine, projetees=…)` sous `memoire.modele_modifie()`,
  ou passent `cas_types=` à `memoire.cout`, déclinés par `grille_large.elargi`.
