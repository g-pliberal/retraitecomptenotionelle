# Le coût sous un modèle modifié, cinquième sous-étape : le régime unique par barème, une règle du compte sous un paramètre facultatif, l'étude par le portage

**La demande.** La sous-étape 5 du plan
(`2026-11-02-le-cout-sous-un-modele-modifie.md`), une par session : le
régime unique par barème, que `scripts/solde_fusion.py` chiffrait en
remplaçant `ConstructeurCompte.taux_unifie` le temps d'un calcul, et en
enveloppant `cout._simulations_en_python` pour garder le compte du scénario 4
de chaque case, sous `pont.par_le_jumeau()`. Le plan : le barème en paramètre
facultatif de la demande, et non en couche, dont il toucherait le contrat
(annexe C) ; lu par `tauxUnifie`, son jumeau ensuite ; et la demande au pont
qui rend, pour un scénario nommé, les lignes du compte de chaque case. Les
fonctions du coût restent en Python. La décision du propriétaire, du
2 novembre 2026, tient : le JavaScript pour ce que le visiteur utilise ; les
grands totaux fabriqués en Python et lus au paquet (notes de décision 0005 et
0006).

**La règle, en JavaScript d'abord.** `bareme_regime_unique`
(`PARAMETRES_DEFAUT`, `moteur/js/config.js`), `null` par défaut, qui laisse
le taux du régime fusionné ; sinon, une suite de tranches `[haute, taux,
tauxSalarie]`, la borne haute en plafonds annuels de la Sécurité sociale,
`null` pour la dernière, sans plafond. `tauxUnifie` (`moteur/js/compte.js`)
en tire, après la bascule et sous les taux historiques, le taux total et la
part de l'assuré (`tauxDuBareme`), sur le revenu de l'année ramené à douze
mois : le plafond se proratise aux mois travaillés, comme celui de
l'assiette. Le reste de la règle ne change pas : qui n'a pas d'employeur
cotise seul, au taux total ; sous la part salariale, ou pour un auteur, le
compte ne reçoit que la part de l'assuré ; le taux uniforme du scénario 6
n'y est pas soumis. Un barème mal formé — sans tranche, aux bornes qui ne
croissent pas, sans plafond ailleurs qu'en dernier, une part de l'assuré hors
de zéro au taux de sa tranche — arrête le simulateur (`verifierBareme`).
C'est ce que calculait le remplacement de l'étude, à une nuance près : il
oubliait les auteurs, qui ne paient que la part salariale
(`part_salariale_seule`), et que la grille du coût ne compte pas.

**Le jumeau.** `Parametres.bareme_regime_unique` (`config.py`),
`taux_du_bareme`, `verifier_bareme` et `ConstructeurCompte.taux_unifie`
(`moteur/compte.py`), ligne pour ligne ; le compte du jumeau se bâtissant à
la demande, un barème mal formé l'arrête à son premier usage.

**La demande au pont.** Le barème passe au portage dans les paramètres de la
demande (`parametres_en_donnees`), et en revient sous les types du Python
(`parametres_des_donnees`). `pont.grille_du_cout` porte de plus `comptes`,
les scénarios dont chaque case rend les lignes du compte : ce qu'il porte,
année par année, et sur quels revenus (`lignesDuCompte` de `pont.mjs`, son
jumeau `cout._lignes_du_compte`). Sans `comptes`, la réponse est celle
d'avant, une entrée `comptes` vide en plus. `cout._simulations` le transmet.

**L'étude.** `scripts/solde_fusion.py` ne remplace plus de méthode du moteur
ni n'ouvre `pont.par_le_jumeau()` : une hypothèse est le barème que le moteur
applique (`parametres_de`), et A n'en pose aucun. `RegimeUniqueVariante` ne
remplace plus que des fonctions du coût — `_pensionnes`, qui garde le compte
du scénario 4 en demandant `comptes` à `_simulations`, `_rapports_recettes`,
`SoldeAnnuel.ressources_de`, `_tva_affectee` et `CLES_RECETTES` —, et
n'ouvre plus que `memoire.modele_modifie()` : la mémoire se tait, le portage
calcule. Ses barèmes restent ceux qu'il lit dans le catalogue
(`hypotheses`).

**Ce qui ne change pas.** La sortie du script, avant (le jumeau, le taux
remplacé, sur `df968e6`) et après (le portage, le barème dans la demande) :
le tableau imprimé et le `--json` identiques à l'octet ; 3 min 9 s avant,
1 min 40 s après. Les deux mesures que l'accueil cite (`taux_regime_unique`
et `cout_18_pour_cent`, que `scripts/mesures_accueil.py` tire de l'étude) ne
bougent donc pas. Le paquet, les témoins et les agrégats ne lisent pas le
barème, que leur défaut laisse à `null`. Plus aucune étude n'ouvre
`pont.par_le_jumeau()` : seules les confrontations l'ouvrent encore, ce que
disent sa docstring et `src/CLAUDE.md`. Dans `README.md`, le chiffre ancré
du poids du moteur compressé passe de 909 à 910 Ko
(`scripts/verifier_prose.py --corriger`).

**Ce qui part.** `RegimeUniqueVariante._taux_unifie`, l'enveloppe de
`cout._simulations_en_python` qui gardait les comptes en remplaçant
`Simulateur.simuler`, et la copie de `taux_du_bareme` dans l'étude.

**Tests.** Vus rouges d'abord : les sept essais de
`tests/js/bareme-regime-unique.test.js` (le défaut ; le découpage aux
tranches, posé à la main sur des taux qui s'écrivent juste en binaire ; le
salarié et son employeur ; l'année incomplète ; l'artisan, sans employeur ;
rien avant la bascule, ni au taux uniforme du scénario 6 ; un barème mal
formé) ; `test_les_parametres_passent_en_donnees_sous_les_noms_du_portage` et
`test_le_bareme_du_regime_unique_passe_au_portage_dans_la_demande_au_bit_pres_du_jumeau`
(`tests/test_pont.py`), le jumeau au bit près sous deux barèmes ;
`test_les_lignes_du_compte_d_un_scenario_passent_le_pont_sous_un_bareme` ;
`test_les_contextes_qui_remplacent_le_modele_font_taire_la_memoire`
(`tests/test_outillage.py`), l'étude au portage ;
`test_chaque_hypothese_est_un_bareme_du_moteur` et
`test_la_grille_se_simule_par_le_portage_au_bit_pres_du_jumeau`
(`tests/test_solde_fusion.py`), le moteur Python interdit de calcul.
`test_le_bareme_par_tranches_se_lit_tranche_par_tranche` lit le barème B par
le moteur, et `test_le_contexte_rend_ses_attributs` les seules fonctions du
coût. Puis `-m rapide`, les essais JavaScript, les tests de l'étude, de
l'outillage, du pont, de la proposition prospective et du stock à l'âge
légal, et les confrontations légères.

**Ce qui reste.** La sous-étape 6 du plan, dans une session neuve : le levier
`pont.par_le_jumeau()` réservé aux confrontations, qu'un test tienne, et qui
parte avec la dernière paire qu'il confronte ; puis les retraits.
