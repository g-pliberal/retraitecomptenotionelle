# Étape 3, cinquième partie : la pension des cas types en 2024, contrôlée sur Ancetre par régime principal

**La demande.** Session du 16 octobre 2026, la n° 11 de quatorze, lancée
pendant que le propriétaire dort : « action 138, étape 3, les contrôles
d'Ancetre, puis de l'EACR : la pension par régime principal », point 4 de
« Ce qui reste » de la première partie (`ancetre`, `legiretraite`, `pablo` au
registre), en commençant par Ancetre. La session 1 tenait les pages : rien
n'est écrit dans `pages.js` ni la saisie, ni dans `cout.py`.

**La source.** Le tableau 3.2 du rapport annuel du COR de juin 2026 (p. 161 ;
« Sources : Drees, EACR, modèle Ancètre »), lu au classeur de la partie 3,
feuille « Tab 3.2 » (`scripts/fetch/cor_pension_regime_principal.py`, témoin
`tests/temoins/cor_pension_regime_principal_2026.json`, `data/sources.yaml`,
`cor_pension_regime_principal`) : la pension brute moyenne de droit direct,
tous régimes, majoration pour trois enfants comprise, selon le régime où le
retraité a fait plus de la moitié de sa carrière ; tous les retraités, puis
les seules carrières complètes ; ensemble, femmes, hommes. Le titre de la
feuille dit « fin 2023 », son champ « vivants au 31 décembre 2024 » : le
champ fait foi, comme pour le tableau 2.11 du même rapport, dont le titre est
aussi resté celui de 2025.

**La mesure** (`retraite_notionnelle.controle_ancetre`,
`scripts/controle_ancetre.py`). Chaque cas type de la grille de la page Coût
sert en 2024 la pension de ses cohortes déjà parties, revalorisée comme les
masses la revalorisent (`coefficient_servi`) et portée à leur complétude,
chacune pesée de son effectif vivant : le scénario 1, en euros de 2024, par
mois. Les cas types se rangent sous le régime principal de leur caisse —
l'artisan au régime général, où la SSI est depuis 2020 ; le contractuel
aussi, l'Ircantec n'étant que sa complémentaire ; la SNCF et les IEG aux
régimes spéciaux — et s'y moyennent au poids que la page leur donne. La grille
et les poids sont ceux de `memoire.cout`, que la mémoire des calculs garde :
seize secondes sans elle. Rien n'entre dans un chiffre de la page ; le module,
que seule la fabrique calcule, n'a pas de jumeau JavaScript.

**Ce qu'il trouve**, le 16 octobre 2026, en euros par mois :

| Régime principal | Grille | Ancetre, carrières complètes | Écart | Ancetre, tous | Écart |
|---|---:|---:|---:|---:|---:|
| Ensemble | 2 043 | 2 100 | −3 % | 1 750 | +17 % |
| CNRACL | 1 538 | 2 010 | −23 % | 1 860 | −17 % |
| FPE civils | 2 403 | 2 750 | −13 % | 2 570 | −6 % |
| FPE militaires | 1 687 | 2 920 | −42 % | 2 260 | −25 % |
| MSA non-salariés | 885 | 1 040 | −15 % | 970 | −9 % |
| Professions libérales | 2 289 | 3 220 | −29 % | 2 840 | −19 % |
| Régime général | 2 138 | 2 020 | +6 % | 1 610 | +33 % |
| Régimes spéciaux | 2 406 | 2 970 | −19 % | 2 740 | −12 % |

1. *Le niveau d'ensemble tient.* La grille ne porte que des carrières
   entières, sauf la carrière interrompue : la colonne qui se compare est
   celle des carrières complètes, et l'ensemble y est à 3 %. Celle de tous les
   retraités dit ce que les carrières courtes, que la grille n'a pas, retirent
   à la moyenne : 17 %.
2. *Le régime général est bien représenté* par ses quatre carrières du privé,
   l'artisan et le contractuel (+6 %), le cadre à 4 009 € compensant le SMIC
   à 1 061 €.
3. *Chaque régime qu'un seul cas type représente est au-dessous du sien*, de
   13 % (civils de l'État) à 42 % (militaires) : le cas type est une carrière
   modeste de son régime — la catégorie B, l'aide-soignant de la CNRACL, le
   militaire du rang, un libéral à la Cipav — quand Ancetre moyenne tous ses
   retraités, officiers, catégories A, médecins compris. Aucune règle n'y
   paraît fausse.
4. *Ce que cela fait à la page.* Les poids des cas types sont recalés sur la
   dépense de chaque groupe du COR (`_poids_par_groupe`, action 147, étape 8) :
   les masses par groupe sont donc justes, et un cas type trop modeste pèse
   plus de têtes que son régime n'a de retraités — de l'ordre de l'écart
   ci-dessus. Ce qui compte des têtes, non des euros, en hérite : la garantie
   vieillesse, l'effet retour, la part des retraités à la garantie. C'est le
   « biais de l'individu moyen » que Pablo chiffre pour l'État (registre,
   `pablo`, coupé), ici approché régime par régime ; la population de l'étape
   14 le corrigera.

**Le test** (`tests/test_controle_ancetre.py`, niveau `controle`, le témoin
et la mesure en `rapide`) tient le témoin, chaque caisse de la grille sous un
régime principal (un cas type neuf entre au contrôle ou fait lever), la
mesure sur une grille d'essai, puis l'ensemble à moins d'un dixième des
carrières complètes, le régime général aussi, et chaque autre régime entre
−45 et −10 % : un écart qui change de sens dit qu'une règle ou une donnée a
bougé.

**Au registre.** Le point d'`ancetre` « la pension par régime principal »,
coupé le 14 octobre, passe `repris`, au chantier 138.3, avec sa
vérification ; le témoin rejoint son `manifeste`. Le point de `pablo` sur le
biais de l'individu moyen reste coupé : le contrôle l'approche sans le
mesurer comme Pablo, sur une population.

**Ce qui reste**, de ce point 4 :

1. *Les tables H, B et C de l'EACR* (`legiretraite`, point coupé le
   14 octobre, à confronter) : les conditions de liquidation (taux plein,
   décote, surcote) en flux et en stock, les liquidants par âge et durée, les
   droits directs par âge. Le second classeur de la DREES, que
   `scripts/fetch/drees_eacr.py` lit déjà pour la feuille E-Minima ; ses
   feuilles font de 40 à 125 Mo de XML, à ne lire qu'une à une
   (`feuilles(..., noms=...)`). La table C, rapportée à la population de
   l'INSEE âge par âge, donnerait la couverture que `cout.py` suppose
   constante (limite n° 2) : elle touche au point 5, la couverture, qu'une
   autre session mène.
2. *Le tableau 3.2 par sexe*, que le témoin porte déjà, contre la carrière
   interrompue et les mères de `scenarios_meres.py`.
