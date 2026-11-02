# Le coût sous un modèle modifié : le relevé, le plan, et le jumeau séparé de la mémoire

**La demande.** Qu'aucun calcul publié ou vérifié n'ait plus besoin du
moteur Python parce qu'il remplace une fonction du modèle le temps d'un
calcul. Au 2 novembre 2026, `pont.par_le_portage` renvoyait au moteur Python
sous `memoire.modele_modifie()`, sous les tests qui prennent `monkeypatch`,
et sur des données d'ailleurs. La règle est celle de la note de décision
0006 : ce qui remplace une règle du moteur s'écrit en données que le portage
lit, une couche ou un paramètre de la demande au pont ; ce qui remplace une
fonction du coût peut rester en Python. La méthode : le relevé, puis un plan
par sous-étapes, chacune avec son test vu rouge et son commit ; les témoins,
les agrégats et le paquet identiques à l'octet, et les chiffres des études
les mêmes. Cette session fait le relevé, le plan et la première sous-étape.

**Le relevé, les trois études.** Chacune s'ouvrait sous
`memoire.modele_modifie()`, le coût et sa grille calculés par le jumeau.

- `scripts/solde_fusion.py` (`RegimeUniqueVariante`) remplace une règle du
  moteur, `ConstructeurCompte.taux_unifie` : sous les hypothèses B, C et D,
  le taux du régime unique après la bascule devient un barème par tranches de
  plafond de la Sécurité sociale (`taux_du_bareme`, sur le revenu annualisé ;
  sans employeur, tout au taux salarié). Il capte aussi, en enveloppant
  `cout._simulations_en_python`, les cotisations et les revenus du compte du
  scénario 4 de chaque case, que `pont.grille_du_cout` ne rend pas. Le reste
  est du coût, qui reste en Python : `_pensionnes`, `_rapports_recettes`,
  `SoldeAnnuel.ressources_de` et `_tva_affectee`, `CLES_RECETTES`. Lecteurs :
  `scripts/mesures_accueil.py`, qui écrit à l'accueil (`MESURES_BLOCAGES`
  de `moteur/js/pages.js`) `taux_regime_unique` et `cout_18_pour_cent` ; les
  neuf tests de `tests/test_solde_fusion.py`. Son `--json` n'a pas de
  lecteur.
- `scripts/proposition_prospective.py` (`PropositionProspective`) remplace
  `ScenarioNotionnel.liberal` par le compte ouvert à la bascule
  (`prospectif`, sous les neutralisations de l'univers du scénario 5), puis
  le pilier capitalisé et la garantie vieillesse : la pile de couches que le
  moteur refuse aujourd'hui (`scenarios/univers.py`, « ni le pilier ni la
  garantie sur un compte ouvert à la bascule »). Du coût : `CLES_PROSPECTIVES`
  étendu au scénario 6. Il simule aussi, sous son contexte, sept cas types à
  quatre générations par le simulateur Python (`calculer_cas_types`).
  Lecteurs : `scripts/chiffrage_plf.py`, qui partage son coût et écrit la
  colonne « Prospective » de `docs/chiffrage_plf.md` ; `mesures_accueil.py`,
  `solde_moyen_prospectif` ; les cinq tests de
  `tests/test_proposition_prospective.py`, et celui des contextes de
  `tests/test_outillage.py`.
- `scripts/stock_age_legal.py` (`StockALAgeLegal`) remplace
  `ScenarioNotionnel.retroactif` — sous `droit_commun` et `tout_droit`, la
  pension liquidée avant la bascule, à l'âge légal ou après mais avant l'âge
  de référence, au diviseur de l'âge de référence — et
  `ScenarioNotionnel._droits_acquis` — sous `acquis`, les droits acquis des
  scénarios prospectifs convertis à l'âge légal de la génération quand il est
  plus bas. Il simule aussi huit couples cas type et génération par le
  simulateur Python. Lecteurs : `mesures_accueil.py`,
  `cout_diviseur_age_legal` ; les six tests de `tests/test_stock_age_legal.py`.

Aucune de ces valeurs n'est un chiffre ancré : l'accueil les tient de
`mesures_accueil.py`, que GitHub refait à chaque fabrique.

**Le relevé, les tests.** Mesuré en faisant tourner, sous un greffon hors du
dépôt, les 147 tests qui prennent `monkeypatch` : 17 atteignaient
l'aiguillage et y étaient renvoyés au Python.

- Six confrontations, qui ouvraient `memoire.modele_modifie()` pour faire
  refaire au jumeau ce que le portage calcule (`tests/test_pont.py`,
  `tests/test_grille_large.py`), et un test de l'aiguillage. Sans
  `monkeypatch`, une septième confrontation,
  `test_le_portage_bat_toute_la_grille_du_cout_comme_le_python`
  (`tests/test_cout.py`), et le second test de l'aiguillage l'ouvraient
  aussi.
- Dix tests qui ne remplacent rien de ce que le portage calcule — la grille
  du coût des avantages (`avantages.CAS_TYPES`, `generations`), la survie
  des pensionnés (`cout.Pensionne.survie`), la revalorisation du stock que le
  coût lit (`RevalorisationServie.coefficient_stock`), neuf constantes de
  `scripts/grille_large.py`, qui décrivent au portage les carrières de la
  grille élargie —, renvoyés au Python par la seule fixture `monkeypatch` de
  `tests/conftest.py`. La contre-épreuve, le portage forcé : les dix passent.

Aucun test ne remplace une fonction du moteur en passant par l'aiguillage ;
les 130 autres ne l'atteignent pas.

**Le relevé, les données d'ailleurs.** Un seul calcul :
`scripts/facteurs_depense.py --sans-suspension`, dont `reforme_entiere`
copie `data/` dans un dossier temporaire et y récrit
`age_ouverture_requis.csv` (générations 1964 à 1968) et
`duree_assurance_requise.csv` (1964, 1965), la réforme de 2023 sans la
suspension de 2026, l'univers de l'Ageing Report ; puis il calcule le coût et
les retraités par âge sur la copie. Lecteurs : les colonnes « sans la
suspension » du départage et son `--json` ; aucune sonde, aucun test, et
aucune étape de la fabrique. Le moteur connaît déjà ce droit,
`Parametres.droit_contrefactuel = "loi_2023_sans_suspension"` (action 138,
étape 10), qui change de plus les âges de la carrière longue : qu'il rende
les mêmes nombres que la copie reste à mesurer.

**Le plan.** Une sous-étape par session.

1. *Le jumeau séparé de la mémoire* — faite, ci-dessous.
2. *Les données d'ailleurs* : mesurer `droit_contrefactuel` contre la copie,
   colonne par colonne. Au bit près, la copie part et le paramètre la
   remplace, sans forme nouvelle ; sinon, le paquet se bâtit depuis la copie
   (`paquet_des_donnees` sur une autre racine), qui garde les nombres, ou le
   propriétaire choisit le contrefactuel, qui les change. Le test :
   `--sans-suspension` passe le portage, ses colonnes identiques.
3. *La proposition prospective en univers* : la pile du scénario 5 et des
   couches de la proposition, `[droit_reel, contributif_seul,
   valorisation_des_droits_acquis, comptes_notionnels, part_patronale,
   taux_unique, capitalisation_obligatoire, garantie_vieillesse,
   age_legal_de_la_proposition]`, des couches qui existent, sous le contrat
   d'univers d'aujourd'hui. Le moteur apprend à servir le pilier et la
   garantie sur un compte ouvert à la bascule, d'abord en JavaScript
   (`calculerUnivers`, `calculNotionnel`), son jumeau Python dans le même
   commit, au bit près. L'univers de la variante n'entre pas au paquet :
   rangé hors de `data/reference/univers/`, il passe au portage dans la
   demande, son calcul résolu à la place de celui du scénario 6 (la forme de
   `CalculNotionnel.donnees`). Les cas types de l'étude passent le pont ;
   `CLES_PROSPECTIVES` reste en Python.
4. *Le stock à l'âge légal* : une règle nouvelle du compte, la conversion du
   stock, sous un paramètre facultatif dont le défaut laisse tout identique
   (`droit_commun`, `tout_droit`, `acquis`) ; le JavaScript d'abord, son
   jumeau ensuite, puis l'étude et ses cas types par le pont.
5. *Le régime unique par barème* : le barème après la bascule, un paramètre
   facultatif (des tranches, le défaut au taux du régime fusionné), lu par
   `tauxUnifie`, son jumeau ensuite ; et la demande au pont qui rend, pour un
   scénario nommé, les lignes du compte de chaque case. Les fonctions du coût
   restent en Python. Une valeur structurée écrite en couche toucherait le
   contrat de la couche (annexe C) : à soumettre au propriétaire avant d'y
   écrire ; en paramètre de la demande, non.
6. *Le levier aux seules confrontations* : plus aucune étude n'ouvre
   `pont.par_le_jumeau()`, un test le tient, et le levier part avec la
   dernière paire qu'il confronte.

**La première sous-étape.** `pont.par_le_jumeau()`, un contexte, fait
calculer le jumeau et taire la mémoire des calculs ; `par_le_portage` ne
renvoie plus au Python que sous lui ou sur des données d'ailleurs.
`memoire.modele_modifie()` ne fait plus que taire la mémoire, et
`memoire.modele_intact`, que seul le pont lisait, part. Les trois études
ouvrent `par_le_jumeau()`, comme les sept confrontations ; la fixture
`monkeypatch` ne fait que taire la mémoire, et sa docstring dit qu'une
fonction du moteur remplacée par un test ne se voit pas du portage. Les dix
tests passent le portage. Refaite, la mesure ne trouve plus de renvoi au
Python que sous `par_le_jumeau()` et dans le test des données d'ailleurs.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun chiffre publié :
les études et la fabrique calculent par le même chemin qu'avant, le paquet,
les témoins et les agrégats ne passent par aucun des deux contextes.

**Tests.** Vus rouges d'abord, trois tests de `tests/test_pont.py` :
`test_sous_monkeypatch_le_cout_simule_sa_grille_par_le_portage` (le coût
calculait en Python, sans lever `PontIndisponible`),
`test_sur_des_donnees_d_ailleurs_le_cout_simule_sa_grille_en_python` (sous
`memoire.modele_modifie()`, `par_le_portage` disait non) et
`test_sous_le_jumeau_le_cout_simule_sa_grille_en_python` (le levier
n'existait pas) ; `test_les_contextes_qui_remplacent_le_modele_font_taire_la_memoire`
(`tests/test_outillage.py`) tient les trois études. Puis `-m rapide`, les
confrontations de la zone, `tests/test_pont.py`, `tests/test_outillage.py`,
les confrontations et les dix tests déplacés, et les tests des contextes des
trois études.
