# Étape 5, sixième partie : le test des références lit le portage, sur le paquet du jour

**La demande.** La suite de l'étape 5 : le test des références
(`tests/test_cycle_de_vie_references.py`), à faire lire au portage du cycle de
vie au lieu de son jumeau Python. Pas encore le retrait de `cycle_de_vie.py`,
qui suit.

**Ce que le portage avait déjà.** La première partie de l'étape le croyait
sans les régimes un à un ni le coût. Il les a : le compte de chaque année,
régime par régime (`par_regime`), celui de la seule part salariale
(`constructeurDe`), les contributions d'équilibre, la valeur de service
convenue de l'Agirc-Arrco (`RevalorisationServie.coefficientPoints`, ce que
`coefficient_actuel` du coût fait jouer), la saisie du site et l'impôt. Ne
manquaient qu'un programme qui les fasse tourner pour le test, et un paquet à
jour.

**Le programme.** `tests/js/cycle-de-vie-references.mjs`, une lecture par
question : les indicateurs d'une saisie sous les conventions nommées ; le
rendement de la génération 2000 régime par régime ; ce que le test tire de
chaque carrière de TRAJECTOiRE ; le salarié de l'OCDE, avant et après impôt ;
les diviseurs, les âges d'équilibre et l'âge cible de l'ETK ; l'âge de décès
du COR et la part de vie. Le Python résout les carrières des références — la
saisie, les options d'un cas type et l'âge où le pilote le fait partir, celles
de l'OCDE — et ce qu'elles publient : la pension nette de TRAJECTOiRE, ses
taux moyens de l'Arrco. La majoration finlandaise passe mois par mois, d'une
seule définition, la sienne. Le test ne nomme plus le cycle de vie Python :
`python scripts/jumeaux.py cycle_de_vie` compte sept fichiers de tests qui le
lisent, et plus celui-ci.

**Le paquet du jour.** Le premier passage, sur `moteur/donnees.json`, a fait
voir ce qu'un paquet en retard coûte. `c2e5452` (action 138, étape 14) a ôté
un champ à la règle de chaque motif d'interruption, dans la fabrique et dans
le portage, sans refaire le paquet : le portage y lisait, au rang où il attend
que l'Unédic verse les complémentaires, le plafond des réputés cotisés de
l'ancien format, et le chômeur du cas type n° 3 du COR perdait les cotisations
de ses années indemnisées. Aucune assertion ne lisait ses cotisations : le
test passait. Il lit donc le paquet des données du jour
(`pont.paquet_des_donnees`), comme le coût. Le même retard fait échouer sur la
tête de `main`, sans ce changement,
`test_simulateur.py::test_le_portage_lit_la_redaction_a_la_date_d_effet` ; la
fabrique de GitHub refait le paquet.

**Mesuré.** Une sonde de cette session, qui n'est pas un test, a confronté au
jumeau Python les 4 267 nombres que rendent ces lectures : tous identiques au
bit sur le paquet du jour ; sur celui du dépôt, 80 différaient, ceux des cinq
générations du cas type n° 3. Le temps : 8,2 s en série, 10 s sur quatre
cœurs, où chaque processus bâtit son paquet du jour, contre 7,6 s. Sous les
présomptions décalées, 18 des 21 tests se taisent, comme toute confrontation
au portage ; les trois qui restent au Python passent.

**Tests.** Le test des références, vu rouge, le programme manquant, puis
vert : 21. Le cycle de vie, sa concordance, son script, le pont, la fabrique,
l'outillage et les contributions d'équilibre : 195. Et 2 932 rapides, avec
l'échec antérieur dit plus haut.

**Ce qui suit.** Le retrait de `cycle_de_vie.py` : ses sept fichiers de tests
(`python scripts/jumeaux.py cycle_de_vie`), dont la concordance, qui part avec
lui, et ses propres tests, qui passent au portage.
