# Étape 6 : `test_oracle.py` par le pont — les cinq familles d'OpenFisca et les régimes alignés au portage, le Python au bit près

**La demande.** Le 31 octobre 2026, le propriétaire ouvre la suite de
l'étape : les six premiers blocs de l'inventaire de `test_oracle.py` (note
`2026-10-31-etape-6-les-confrontations-par-le-pont.md`) — OpenFisca au régime
général, à la pension civile, à l'Arrco, à l'Agirc et à l'Ircantec, puis les
régimes alignés —, un bloc par commit, au vert, dans l'ordre du tableau.
Chaque bloc déclare au pont ce qu'il lit, le fait appeler par `pont.droit` au
lieu du jumeau, et garde le contrôle du Python au bit près ; chaque
déclaration est vue refusée, puis portée. Le septième bloc, les exemples
officiels, reste à la session suivante. **Sa décision**, sur la question que
la note précédente lui soumettait : garder, pour
`liquider.trimestres_de_decote`, « la relecture par `pont.relu_du_droit`
(sans toucher au jumeau Python) », qui rend un entier là où son annotation dit
un flottant. La mesure du régime général la suit : les trimestres de décote
s'y relisent en flottant, et le jumeau n'a pas bougé.

**Le contrôle du Python** (897dec6). `tests/outils_pont.py` gagne
`droit_et_refait`, le pont du droit dont chaque appel est refait par son
jumeau Python, comme `servi_et_refait` l'est du scénario 1. La table
`JUMEAUX_DU_DROIT` donne le jumeau de chaque fonction que le pont relit — ses
clés sont celles de `pont.LECTURES_DU_DROIT`, ce que son test vérifie. Ce
qu'il rend, relu sous le type que le pont déclare, doit s'écrire au bit près
comme ce que le portage a rendu sous Linux x86_64
(`TOLERANCE_DU_MOTEUR_PYTHON`), et un appel que le portage refuse, le jumeau
doit le refuser. Son test, vu rouge deux fois — absent, puis sans
comparaison —, le voit s'arrêter sur un ulp déplacé dans le jumeau du salaire
de référence. C'est le pont par défaut des mesures de `test_oracle.py` : chaque
appel qu'elles font est refait au Python. Chaque famille a de plus un test qui
la mesure par `pont.droit` seul, ses jumeaux Python empêchés de calculer
(`_sans_les_jumeaux`), vu rouge sur la mesure d'avant, remaniée d'abord sans
changer de moteur.

**Les mesures, une fois par module.** Chaque famille calcule ses profils en
une ou deux demandes groupées, dans une fixture du module (`nos_calculs`,
`nos_calculs_fonction_publique`, `nos_points_arrco`, `bareme_agirc`,
`nos_pensions_alignees`…), au lieu d'un calcul par profil et par test : le
fichier passe de 7,9 à 7,2 secondes, et ses six premiers blocs restent à
3,7 secondes en série, le Python refait compris.

**Bloc par bloc.**

- *Le régime général* (897dec6) : rien à déclarer, la note précédente avait
  porté ses six fonctions. Sa mesure, `_nos_calculs`, se fait en deux
  demandes — la seconde lit dans la première la durée requise, la durée
  validée et l'âge d'annulation de la décote — et sert aussi les profils de
  l'Arrco, de l'Agirc et de l'Ircantec (la décote du régime général qui
  commande leur abattement) et la référence des régimes alignés.
- *La pension civile* (6381ffc) : le minimum garanti, que l'inventaire
  omettait (`scenario_actuel.minimum_garanti.montant`).
- *L'Arrco* (2e1508e) : `liquider.valeur_du_point`, la date du départ passée
  en `DateMois`, que le pont écrit `{annee, mois}` et que `valeurDuPoint` lit
  telle quelle. La lecture des points dans la formule servie
  (`_points_servis`) se partage désormais avec l'Agirc et l'Ircantec.
- *L'Agirc* (7efb97b) : le barème que rejouent les tests de cotisation, lu au
  portage une fois (`_bareme`). Les périodes du régime, dont le pont ne garde
  que les années, l'assiette, le taux et la part du salarié
  (`scenario_actuel.catalogue.periodes`, relues par
  `pont.periodes_des_donnees`) ; le plafond de chaque année
  (`scenario_actuel.macro.plafond_securite_sociale`) ; les bornes des
  assiettes (`regimes.BORNES_ASSIETTE`), pour lesquelles `_depuis_donnees`
  apprend à relire un dictionnaire, vu rouge sur « 0 » pour « 0.0 » ; le prix
  d'achat et le taux d'appel (`scenario_actuel.valeurs_point.achat`). Les
  tests de l'Ircantec qui lisaient `_nos_points` et `_taux_de_la_tranche`
  passent avec ce bloc.
- *L'Ircantec* (8f2e838) : la valeur de service au millésime qu'OpenFisca lit
  (`scenario_actuel.valeurs_point.service`), la règle du millésime écrite une
  fois (`_millesimes_ircantec`), l'âge du taux plein de la génération
  (`scenario_actuel.ages_annulation_decote.age`) ; la cotisation rejouée lit le
  barème du portage.
- *Les régimes alignés* (a40a7d7) : `scenario_actuel.calculer` reçoit ses
  drapeaux après la carrière, dans l'ordre du jumeau — la césure,
  `liquider_successions=False`, vue rouge sur les quarante appels où le
  portage l'ignorait. Le test des indépendants prêtait au moteur Python la
  table du régime général à la place de la leur (`monkeypatch.setattr`) : le
  pont la prête au moteur du portage, sur une copie que les autres appels ne
  voient pas (`pont.MOTEUR.pretant`, `MOTEUR` devenu une instance de
  `pont.Moteur`), et `droit_et_refait` la prête au moteur Python le temps de
  l'appel. Le test du prêt (`tests/test_pont.py`), vu rouge — le pont sans
  `pretant`, puis le portage qui l'ignorait —, prend un artisan né en 1949,
  dont la pension du RSI vaut 12 460,76 € sous ses vingt et une années
  (R. 634-1-1) et 12 149,33 € sous les vingt-cinq du régime général ; une
  table que le moteur ne porte pas arrête l'appel. La référence du régime
  général, que le test des indépendants calculait sous le prêt, ne dépend pas
  de la table des indépendants : vérifiée au bit près sur ses cinq profils,
  elle est désormais celle du module.

**Ce que le pont porte désormais** (`FONCTIONS_DU_DROIT` de `pont.mjs`,
`LECTURES_DU_DROIT` de `pont.py`, `JUMEAUX_DU_DROIT` de `tests/outils_pont.py`) :
quatorze fonctions et lectures, dont six de la note précédente. Les six
premiers blocs n'appellent plus le moteur Python qu'à travers
`droit_et_refait` ; l'import de `BORNES_ASSIETTE` est sorti du fichier.

**Aucun écart trouvé.** Ni du portage à OpenFisca — chaque test garde ses cas
et ses tolérances, et passe —, ni du Python au portage : chaque appel des six
blocs se refait au bit près.

**La suite rouge, réparée** (2da3da0). La course de GitHub sur 0bf2ca2
échouait à la fabrique, sur la conservation : b4373d9 (la page « Méthode »)
avait renommé l'affirmation `methode.portage_javascript`, et le catalogue
garde ses identifiants. L'entrée est allée, telle qu'elle était, dans
`docs/archives/affirmations.yaml`, avec sa date et son motif ;
`conservation.py` dit « rien de perdu ».

**La seconde suite rouge, réparée.** La conservation réparée, la course sur
23d0783 a joué la suite complète, que les deux précédentes n'atteignaient
pas, et un seul test y a échoué :
`test_une_page_depliee_tient_son_budget[/methode]`, 5 695 mots pour 5 650 au
plus. Le dépliant de construction, récrit par b4373d9, était passé de 164 à
241 mots. Il en a désormais 193, sans perdre une idée ni une des tournures que
`test_la_methode_dit_comment_le_site_est_construit` exige : l'incise « la
vôtre, quand vous la saisissez », que « rien de ce que vous saisissez »
redisait ; « Il a d'abord été écrit en Python, et tant que la migration n'est
pas finie, le moteur du site y garde un jumeau », devenu « Écrit d'abord en
Python, il y garde un jumeau pendant la migration » ; la phrase des carrières
témoins et celle du coût, resserrées. La page fait 5 647 mots ; seul son rendu
change parmi les témoins, aucun des 913 témoins de simulation ne bouge.

**Ce qui ne change pas.** Hors la page Méthode et son rendu témoin, aucun
octet des témoins, des agrégats, du paquet ni des pages. Aucune règle du moteur, ni
en JavaScript ni en Python ; aucune garde, aucune dépendance, aucune règle du
scénario 1. Sans node, chaque mesure s'arrête (`pont.PontIndisponible`).

**Tests.** `python -m pytest -m rapide`, 3 532 ; les confrontations légères,
`tests/test_pont.py` et `tests/test_jumeaux.py`, 457 ;
`node --test tests/js/*.test.js`, 115 essais — le dossier seul,
`node --test tests/js/`, n'est pas une forme que node 22 accepte.

**Ce qu'il faudra au septième bloc**, les exemples officiels (`_carriere_exemple`,
`_mesurer`, `_cumul_exemple`, `_confronter` et leurs trois tests, de « Les
exemples chiffrés publiés par les caisses » à la fin du fichier) :

- Leurs carrières se bâtissent par `simulateur.carriere_simple`, la
  chronologie (`chronologie.valeur`), `calendrier.origine_des_ages` et
  `en_mois`. Ou le Python les bâtit encore et les passe en données, comme
  `pont.droit` le permet, ou `carriere_simple` se déclare au pont et rend une
  carrière en données (`carriere_des_donnees`).
- `_mesurer` aiguille cinquante-trois grandeurs, chacune sur sa fonction. Le
  pont porte déjà `scenario_actuel.calculer`, drapeaux compris,
  `liquider.salaire_de_reference` et `liquider.valeur_du_point` ; il lui
  faudra au moins `ouvrir.age_ouverture_droit`, `departs.age_legal`,
  `liquider.nombre_d_annees_retenues`, `mois_apres_le_depart`,
  `majoration_rafp`, `prestation_rafp`, `invalidite.exigences_du_handicap`,
  `pension_du_fonctionnaire_invalide`, `retraite_pour_invalidite`,
  `reversion.reversion`, l'`Echeancier`, `cumul.cumuler`, `releve.construire`
  et `LigneRelevee`, `foyer.foyer_et_net`, `revalorisation.faire_vivre`,
  `remuneration.fiche_depuis_brut`, `ConstructeurCompte`, et des lectures du
  catalogue, de la macro, des affiliations et de l'indexation ;
  `parametres.avec` passe par le paramètre `parametres` de `pont.droit`. Ce
  que `_mesurer` lit du résultat (`trimestres_requis`…) déborde
  `actuel_des_donnees` : sa relecture s'étendra, ou une lecture de plus.
- Ce qui rend des objets — l'échéancier, la réversion, le cumul — demandera
  sa relecture : un dataclass, que `_depuis_donnees` relit champ par champ,
  ou une fonction comme `periodes_des_donnees`.
- Le test paramétré joue chaque exemple seul : une demande par exemple, ou une
  fixture qui les groupe. Le patron des six blocs vaut : `droit_et_refait` par
  défaut, un test sans les jumeaux par groupe de grandeurs, chaque
  déclaration vue refusée puis portée, une famille de fonctions par commit.
- La fixture `simulateur` du module ne sert plus qu'à lui.

**Ce qui suit.** Le septième bloc ; puis le coût daté par le portage ; puis
les retraits, par sous-ensemble cohérent. D'autres confrontations simulent
encore au moteur Python et retiennent ses jumeaux (`test_trajectoire.py`,
`test_ines.py`, les huit `test_oracle_*.py`, `test_flux_fonction_publique.py`,
`test_cycle_de_vie_references.py`) ; `pont.droit` et `droit_et_refait` leur
sont ouverts.
