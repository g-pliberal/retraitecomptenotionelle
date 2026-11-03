# Le coût sous un modèle modifié, quatrième sous-étape : le stock à l'âge légal, une règle du compte sous un paramètre facultatif, l'étude par le portage

**La demande.** La sous-étape 4 du plan
(`2026-11-02-le-cout-sous-un-modele-modifie.md`), une par session : le stock
à l'âge légal, que `scripts/stock_age_legal.py` chiffrait en remplaçant
`ScenarioNotionnel.retroactif` et `_droits_acquis` le temps d'un calcul, sous
`pont.par_le_jumeau()`. Le plan : une règle du compte, sous un paramètre
facultatif dont le défaut laisse tout identique, le JavaScript d'abord, son
jumeau ensuite, puis l'étude et ses cas types par le pont. La décision du
propriétaire, du 2 novembre 2026, tient : le JavaScript pour ce que le
visiteur utilise ; les grands totaux fabriqués en Python et lus au paquet
(notes de décision 0005 et 0006).

**La règle, en JavaScript d'abord.** `stock_age_legal` (`PARAMETRES_DEFAUT`,
`StockAgeLegal`, `moteur/js/config.js`), `null` par défaut, qui ne touche
rien. Sous `droit_commun` et `tout_droit`, `retroactif` prend son diviseur à
l'âge de référence (`age_reference_fixe`, 65 ans) pour une pension liquidée
avant la bascule, à l'âge légal ou après mais avant lui (`_ageDuDiviseur`) ;
l'âge légal est celui de la génération dans le droit que le scénario 1
applique, ou, sous `tout_droit`, celui que le droit de l'assuré lui ouvrait
(`ageOuvertureDroit`, par `_ageLegal`). Sous `acquis`, `_droitsAcquis`
convertit les droits acquis à l'âge légal de la génération quand il est plus
bas que l'âge de conversion. Le compte, l'écart d'âge et la fiabilité ne
changent pas ; un nom que le moteur ne connaît pas arrête le simulateur.
C'est ce que calculaient les deux remplacements de l'étude, à une nuance
près : la population de mortalité est celle du chemin du moteur (`resoudre`,
`populationPourPension`), et non celle de la carrière seule ; les deux ne
diffèrent que sous le rattachement par la pension, que l'étude ne pose pas.

**Le jumeau.** `StockAgeLegal` et `Parametres.stock_age_legal` (`config.py`),
`ScenarioNotionnel._age_legal`, `_age_du_diviseur`, `retroactif` et
`_droits_acquis`, ligne pour ligne.

**La demande au pont.** `pont.carrieres` porte les paramètres d'une étude
(`parametres`), que le portage applique (`simulateurSous`) ; sans eux, les
réglages de référence, comme avant. Elle rend de plus la pension de l'étalon
et de chaque scénario, hors du pilier, en euros constants
(`pensions_euros_constants`), ce que l'étude lit de ses cas types.
`grille_du_cout` portait déjà tous les paramètres : le coût sous la règle n'y
a rien changé.

**L'étude.** `StockALAgeLegal` part, et l'étude n'ouvre plus
`pont.par_le_jumeau()` : une variante est la règle que le moteur applique
(`parametres_de`) ; le coût se calcule sous elle par le portage, gardé par la
mémoire des calculs, puisque le modèle reste intact ; les cas types se datent
et se simulent par le portage (`cases_de_la_grille`, puis `pont.carrieres`,
dans `pensions_des_cas`).

**Ce qui ne change pas.** La sortie du script, avant (le jumeau, les deux
méthodes remplacées) et après (le portage, la règle dans la demande) : le
tableau imprimé identique à l'octet, et le `--json` aussi, au champ `touches`
près ; 2 min 51 s avant, 1 min 18 s après. L'écart que l'accueil cite
(`cout_diviseur_age_legal`, que `scripts/mesures_accueil.py` tire de l'étude)
ne bouge donc pas. Le paquet, les témoins et les agrégats ne lisent pas la
règle, que leur défaut laisse à `null`.

**Ce qui part.** Le compte « N couples touchés », sur la sortie d'erreur, et
le champ `touches` du `--json` : ils comptaient les appels du moteur Python
que la variante touchait (396 sous `droit_commun`, 729 sous `tout_droit`, 282
sous `acquis`), que le portage ne compte pas ; aucun lecteur ne les lisait.

**Tests.** Vus rouges d'abord : les six essais de
`tests/js/stock-age-legal.test.js` (un salarié né en 1950, parti à 60 ans en
2010, l'âge légal de sa génération : son compte divisé au diviseur de 65 ans ;
un agent de conduite de la SNCF né en 1960, parti à 52 ans : le droit commun
le laisse au diviseur de son âge, son propre droit, qui lui ouvrait 50 ans, le
relève ; rien après la bascule, ni à 65 ans et au-delà ; un actif né en 1970,
ses droits acquis convertis à 64 ans ; le défaut ; un nom inconnu) ;
`test_les_parametres_passent_en_donnees_sous_les_noms_du_portage` et
`test_le_stock_a_l_age_legal_passe_au_portage_dans_la_demande_au_bit_pres_du_jumeau`
(`tests/test_pont.py`), le jumeau au bit près sous les trois variantes ;
`test_le_pont_rend_au_bit_pres_ce_que_le_moteur_python_simule`, les pensions
en euros constants ; `test_chaque_variante_est_une_regle_du_moteur` et
`test_les_cas_types_passent_par_le_portage_au_bit_pres_du_jumeau`
(`tests/test_stock_age_legal.py`), le moteur Python interdit de calcul. Puis
`test_le_cout_sous_la_regle_du_stock_simule_sa_grille_par_le_portage`, au bit
près du jumeau sous `droit_commun` et `acquis` ; les tests de l'étude, de
l'outillage et de la proposition prospective ; `-m rapide`, les tests de la
zone et les confrontations légères.

**Hors de ma file.** Deux tests rouges sur `main`, sans mes changements, que
je n'ai pas touchés. `test_le_moteur_python_refait_chaque_temoin`
(`tests/test_pont.py`) : 671 écarts sur ce que les retraités touchent
aujourd'hui (`coefficient_majoration`, `mensuel_decembre_2019`,
`coefficients_notionnels`), mesurés sur `203a549` ; les témoins attendent que
GitHub les refasse après les envois des autres files.
`test_journal_de_certification_est_lisible` (`tests/test_verification.py`) :
`data/derive/certification.json` date du 3 novembre les grilles de la
territoriale et de l'hospitalière, quand son dernier passage reste au
2 novembre (file B, action 158, `203a549`).

**Ce qui reste.** Les sous-étapes 5 et 6 du plan, une par session : le régime
unique par barème, en paramètre de la demande ; puis le levier
`pont.par_le_jumeau()` réservé aux confrontations, dont
`scripts/solde_fusion.py` est la dernière étude à l'ouvrir.
