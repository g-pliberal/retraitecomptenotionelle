# Le coût sous un modèle modifié, troisième sous-étape : la proposition prospective en univers, calculée par le portage, ses chiffres à l'octet

**La demande.** La sous-étape suivante du plan
(`2026-11-02-le-cout-sous-un-modele-modifie.md`), une par session : la
proposition prospective, `scripts/proposition_prospective.py`, écrite en
données et calculée par le portage. La décision du propriétaire, du
2 novembre 2026, tient : le JavaScript pour ce que le visiteur utilise ; les
grands totaux, le coût compris, fabriqués en Python et lus au paquet (notes
de décision 0005 et 0006).

**La règle, en JavaScript d'abord.** Une transition ouvre le compte à la
bascule ; quand l'univers ajoute la garantie, `calculerUnivers` sert sur ce
compte le pilier capitalisé, puis la garantie vieillesse, qui regarde les
deux étages (`avecLePilierEtLaGarantie`, que `liberal` appelle désormais
après le compte rétroactif). Une pension liquidée avant la bascule garde sa
pension du droit en vigueur, et la garantie la complète aussi : « la
garantie valant aussi pour le stock », dit l'étude. C'est ce que son
remplacement de `ScenarioNotionnel.liberal` calculait.

**Le jumeau.** `Simulateur.calculer_univers` et
`ScenarioNotionnel.avec_le_pilier_et_la_garantie`, ligne pour ligne ;
`calcul_notionnel` ne refuse plus le pilier ni la garantie sur un compte
ouvert à la bascule, et refuse toujours le pilier sans la garantie.

**La variante en données.** `data/reference/variantes/notionnel_liberal_prospectif.yaml`,
sous le contrat d'univers d'aujourd'hui (C.4), sans rien y ajouter : la pile
du scénario 5, puis les couches que le scénario 6 pose sur la part
patronale, `[droit_reel, contributif_seul, valorisation_des_droits_acquis,
comptes_notionnels, part_patronale, taux_unique, capitalisation_obligatoire,
garantie_vieillesse, age_legal_de_la_proposition]`, des couches qui
existent ; le numéro 6. Elle n'est pas un scénario du site et n'entre pas au
paquet (`noyau/univers.VARIANTES`).

**La demande au pont.** `Simulateur(parametres, variantes={clé: univers})`
met une variante à la place de l'univers de même clé, et la garde sous les
conventions de la projection ; `univers_de_la_demande` en rend le calcul
sous la forme du paquet (`CalculNotionnel.donnees`). `grille_du_cout` et
`carrieres` le portent (`univers`) : le portage bâtit son simulateur sur le
paquet où ce calcul remplace celui du scénario 6 (`simulateurSous`), et
refuse une clé qui n'y nomme aucun univers de la proposition. `carrieres`
rend de plus l'écart hors du pilier (`ecarts`, `variation`), ce que l'étude
lit de ses cas types. Le coût passe au pont les variantes de son simulateur
(`cout._simulations`).

**L'étude.** `PropositionProspective` ne remplace plus de méthode du moteur
ni ne s'ouvre sous `pont.par_le_jumeau()` : elle n'étend plus que
`cout.CLES_PROSPECTIVES`, une fonction du coût, qui reste en Python, sous
`memoire.modele_modifie()`. `simulateur(parametres)` bâtit le simulateur de
l'étude ; son coût et ses cas types passent par le portage
(`cases_de_la_grille`, puis `pont.carrieres`), sous les réglages de
référence, les seuls que le pont leur applique, ce qu'une garde exige.

**Ce qui ne change pas.** La sortie du script, avant (le jumeau, `liberal`
remplacé) et après (le portage, la variante dans la demande) : identique à
l'octet, le tableau imprimé comme le `--json` entier, toutes les lectures des
six systèmes des deux variantes à pleine précision ; une minute 55 avant,
une minute 7 après. `chiffrage_plf.py --verifier` : à jour. Le paquet, les
témoins et les agrégats ne lisent pas la variante.

**Tests.** Vus rouges d'abord : les deux essais de `tests/js/univers.test.js`
(un actif né en 1985, parti à 65 ans : ses droits figés, 18 % après la
bascule, le pilier dès 2026, la garantie qui regarde les deux étages ; une
courte carrière partie à 65 ans en 2010 : 8 507 €, minimum vieillesse
compris, sous le plancher de 9 697 €, 1 050 € par mois en euros de 2026
ramenés aux prix de 2010, que la garantie complète), lancés par pytest ;
`test_la_proposition_prospective_est_le_scenario_5_a_18_pour_cent`,
`test_une_variante_tient_la_place_de_son_univers_le_temps_d_une_etude` et le
test des refus (`tests/test_univers.py`) ;
`test_le_pont_rend_au_bit_pres_ce_que_le_moteur_python_simule` (l'écart hors
du pilier), `test_une_variante_passe_au_portage_dans_la_demande_au_bit_pres_du_jumeau`
et `test_le_cout_d_une_variante_simule_sa_grille_par_le_portage`
(`tests/test_pont.py`), au bit près du jumeau sous `par_le_jumeau()`, et
autre chose que le scénario 6, avant comme après la bascule ; puis
`test_le_contexte_rend_ses_attributs`, `test_le_stock_est_intact…` par le pont
(`tests/test_proposition_prospective.py`) et
`test_les_contextes_qui_remplacent_le_modele_font_taire_la_memoire`
(`tests/test_outillage.py`). Puis `-m rapide` (3 590), et les tests de la
zone et les confrontations légères (581).

**Hors de ma file.** Le texte de l'action 130 (`docs/feuille_de_route.md`,
« La variante prospective de la proposition […] remplace encore une méthode
le temps d'un calcul. Le moteur ne sert ni le pilier ni la garantie sur un
compte ouvert à la bascule ») ne dit plus vrai : le moteur les sert, et la
variante est un univers, que le site ne montre pas. Je n'y ai pas touché.

**Ce qui reste.** Les sous-étapes 4 à 6 du plan, une par session : le stock à
l'âge légal, le régime unique par barème, puis le levier
`pont.par_le_jumeau()` réservé aux confrontations.
