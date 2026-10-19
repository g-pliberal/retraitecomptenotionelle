# Étape 5, troisième partie : la grille et les exemples du bilan figé passent le pont

**La demande.** La suite de l'étape 5, sans la grille du coût ni `memoire.py`,
qu'une autre session touchait cette nuit : la grille et les exemples du bilan
figé (`_bilan`, `scripts/construire_donnees.py`), faits par le portage comme
la grille des agrégats l'a été la veille. La demande nommait
`bilan_compte.py` ; il n'a pas de jumeau, et ne simule rien que le coût ne
lui donne : la paire du bilan est `donnees/bilan.py` et `moteur/js/bilan.js`,
dont la fabrique écrit la table, `data/derive/equilibre.json`.

**Ce que le bilan simulait en Python.** Deux lectures : la grille des cas
types (`calculer_cas_types`), dont `castypes.ecarts_medians` tire les trois
médianes que l'accueil cite ; et les trois carrières d'exemple de « Pourquoi
changer », des saisies du site (`saisieRisque`) que `Contexte.simuler`
simulait, dont `donnees/bilan.exemple_de` gardait la fiche de paie, le
passage aux euros constants et deux pensions. Le reste du bilan est le coût :
le solde, et l'engagement acquis (`calculer_engagements`), qui lit la grille
du coût (`_pensionnes`).

**Le pont, deux lectures de plus.** `carrieres` rend aussi, de chaque case, la
pension totale et la rente des points volontaires de chaque scénario, et,
pour qui est déjà parti, ce que le système actuel et chaque scénario lui
servent aujourd'hui (`aujourd_hui`), sinon rien. Une lecture nouvelle,
`saisies`, simule une saisie comme le site (`Contexte.simuler`) et en rend la
fiche de paie de l'année de référence sous le droit en vigueur, le passage
aux euros constants et la pension de chaque scénario demandé.
`tests/test_pont.py` exige les deux au bit près du moteur Python, sur des
cases à venir et déjà parties, et sur deux saisies.

**La fabrique branchée.** `ecarts_medians` et `exemple_de` lisent ce que le
pont rend, au lieu d'une `Comparaison` Python ; le Python fixe toujours l'âge
de chaque case et écarte ce que le droit écarte (`cases_de_la_grille`). Le
paquet provisoire sur lequel node calcule se bâtit une fois, sans bilan ni
agrégats, pour les deux tables : la simulation d'une carrière ne lit ni l'un
ni l'autre.

**Les six conditions, pour ces lectures.** Les données : chaque nombre sous le
type que le Python lui donne (`test_pont.py`). L'identité :
`construire_donnees.py --verifier` rend les quatre fichiers à l'octet, et le
test des exemples (`test_cout.py`) et le contrôle des écarts médians
(`test_affirmations.py`) exigent désormais l'égalité exacte au moteur Python,
au lieu de 10⁻⁹ et 10⁻¹². Le budget : la grille, de 4,3 s par le Python à
1,7 s (0,5 s de cases en Python, 1,2 s par le pont) ; les exemples, de 0,7 à
0,4 s, la lecture du site comprise ; le paquet provisoire, 1,9 s, ne se bâtit
pas une fois de plus. La mémoire : relue, celle de la fabrique ne prenait de
`pages.js` que les systèmes montrés, quand la fabrique y lit aussi la saisie
des exemples, le classement comparé et quatre autres déclarations ; une
retouche de l'une d'elles ne refaisait pas le paquet en local, GitHub seul le
refaisant. Chacune entre désormais dans l'empreinte du paquet, avec les
constantes que `saisieRisque` nomme (`fabrique.EXTRAITS`,
`tests/test_fabrique.py`). Sans node, le pont s'arrête (`PontIndisponible`).
Aucune dépendance nouvelle.

**Tests.** 2 842 rapides, puis 2 853 sur la tête de `main` rattrapée, la
mémoire comprise ; le pont, la fabrique,
la libm, la carte des jumeaux, les niveaux, l'outillage, les confrontations
légères et `test_agregats.py`, 489 ; le test des exemples figés et le
contrôle de l'ordre de grandeur de la baisse ; `construire_donnees.py
--verifier` : « paquet à jour ».

**Ce qui suit.** La grille du coût, sous les conventions du COR, dont les
carrières se déforment en Python (`primes_projetees`, l'entrée tardive) et
doivent passer en données, et avec elle l'engagement acquis du bilan ;
`memoire.py` s'indexera alors sur le portage. Le test des références et le
retrait de `cycle_de_vie.py` l'attendent.
