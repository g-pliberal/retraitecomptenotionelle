# La façade des tests : les huit entrées du moteur Python servies par le portage, lues strictement, et la liste des fichiers encore sur le moteur Python

La façade est bâtie, à côté du jumeau Python : `tests/facade.py` sert sous
leurs noms les huit entrées que la note de la question 2 nomme, le portage
les calcule, et ce qu'il rend revient sous les types du Python, champ par
champ. Elle refuse ce qu'elle ne sait pas transmettre. Un test tient la liste
des fichiers de tests qui entrent encore dans le moteur Python. Aucun fichier
de tests n'est basculé : c'est l'étape suivante. Il reste à la façade le
contenu d'une liquidation au journal, et les tables du moteur que les tests
lisent directement, qui font presque tous ses refus.

**La consigne.** « L'ordre proposé » de
`2026-11-12-question-2-la-methode-des-tests.md` : la façade dans un module à
elle tant que le jumeau vit, lue strictement, le journal et les erreurs
compris ; un client qui refuse ce qu'il ne sait pas transmettre ; un test qui
tient la liste, décroissante, des fichiers qui exécutent encore une règle
Python. L'essai de cette note-là n'était pas commité : rien n'en est repris.

## Ce qui est fait

**Le client, `tests/facade.py`.** Un fichier de tests y passe en changeant
ses imports, ses tests inchangés : `Simulateur` (`simuler`,
`carriere_simple`, `carriere_parcours`, `carriere_releve`, et
`scenario_actuel.calculer`), `Carriere` (`depuis_profil`, `depuis_parcours`)
et `reversion`. Les arguments se lient par la signature du jumeau Python :
un argument inconnu reste une `TypeError`. Les données du simulateur — ses
séries (`macro`), son catalogue, ses affiliations — se lisent par leurs
chargeurs Python, qui restent.

**Ce que le client refuse** (`pont.NonTransmissible`, qui ne dérive pas
d'`Exception`, pour qu'un `pytest.raises(Exception)` ne verdisse pas d'un
refus) :

- une série passée à un bâtisseur de `Carriere` qui n'est pas celle d'un
  simulateur de la façade — celles d'un simulateur portent ses paramètres ;
- un moteur passé à `reversion` qui n'est pas celui d'un simulateur de la
  façade ;
- toute retouche de son simulateur ou de son moteur (`setattr`,
  `monkeypatch.setattr`) ;
- tout appel sous un modèle modifié : `memoire.modele_modifie`, que la
  fixture `monkeypatch` du dépôt ouvre (`memoire.modele_intact`, neuf) ;
- des variantes d'univers ;
- la lecture, sur son simulateur ou son moteur, de ce qu'elle ne sert pas :
  une table du moteur, le compte, la conversion.

**La demande, `pont.facade`, et `facade` de `pont.mjs`.** Un bloc à part dans
chaque fichier, sans toucher au reste du pont. `telQuel` écrit un objet du
portage tel qu'il le tient : ses champs publics, une table en objet, un
nombre non fini par son nom. Un refus du portage revient avec la classe et
le motif de son erreur, et le Python lève la sienne
(`pont.erreur_du_portage`) : `DonneeInsuffisante`, `KeyError` pour une
affiliation ou une présomption inconnue, `ValueError` sinon.

**La lecture, `pont.lu_strictement`.** Chaque champ du type est attendu,
sous son type : un entier doit en être un, « 2 » se relit 2.0, un type que
la lecture ne connaît pas l'arrête. Les écarts que la note de la question 2
relevait sont déclarés un à un, dans des tables :

| table de `pont.py` | ce qu'elle déclare |
|---|---|
| `CHAMPS_SANS_OBJET` | les champs que le portage n'écrit pas quand ils ne s'appliquent pas : dix de `PensionRegime`, trois d'`AvantageApplique`, `minimum_ecrete` |
| `CLASSES_EN_CHAMEAU`, `NOMS_DU_PORTAGE` | six classes aux champs en casse de chameau, et deux champs renommés |
| `OBJETS_DU_RESULTAT` | le type de trois champs que le Python annonce `object` |
| `HORS_DU_TYPE` | ce que le portage tient et que le type ne porte pas : `Comparaison.scenarios` |
| `CONTENUS_DU_JOURNAL` | le type du contenu d'une entrée du journal, par sa sorte |

Une valeur que le portage tient en champ et le Python en propriété
(`pension_mensuelle`, `pension_totale`…) ne se relit pas : le type la refait.
Ces petites règles en double restent, comme la note le disait.

**Le journal.** Chaque entrée revient avec ce qui la date, et son contenu
sous le type de sa sorte : un événement, une composante, la décision du
foyer, la revalorisation, la réversion. Le contenu d'une liquidation, qui
tient les tables du moteur, ne passe pas : le lire est refusé
(`pont.ContenuNonLu`).

**La liste, `tests/test_fichiers_sur_le_moteur_python.py`.** Un fichier de
tests « entre dans le moteur Python » s'il importe, des fichiers de règles
ou de ceux qui tiennent les entrées de la façade, autre chose qu'un type de
données ou une constante. La liste se lit dans les imports, sans rien
lancer : 135 fichiers sur 251, les deux fichiers de tests de la façade
compris, qui confrontent et qui vérifient les refus. La mesure dynamique de
la question 2 en comptait 143. Un fichier de plus rougit le test ; un
fichier porté quitte la liste dans son commit.

## Ce qui est mesuré

**Contre le jumeau** (`tests/test_facade_jumeau.py`). Sur les 933 témoins de
simulations, la carrière que le portage bâtit, liquidée puis simulée par la
façade et par le moteur Python : le résultat du scénario 1 concorde sur
tous, au bit près ; la comparaison entière, journal compris, sur 929. Les
quatre autres ne diffèrent que par la fiche de paie de la proposition,
certaines années à venir (voir « Trouvé en chemin »). Un échantillon tourne
dans la suite rapide, tous les témoins dans la suite complète, où le jumeau
calcule six minutes.

**Sur les deux fichiers instruits**, par des copies non commitées dont seuls
les imports changeaient : 451 tests sur 691 passent par la façade, 187 de
`test_simulateur.py` et 264 de `test_reversion.py`. Des 240 autres, 239
sont des refus de la façade :

| ce que le test lit | refus |
|---|---:|
| une table ou un attribut du moteur (`scenario_actuel.reversions` 56, `.affiliations` 33, `.valeurs_point` 24, `.carriere_longue` 23, `.revalorisations_pensions` 20, `.fiches_datees` 19, `.invalidites` 13…) | 218 |
| une règle du simulateur (`constructeur_employeur` 14, `proposition`, `scenario_notionnel`…) | 21 |

Le dernier compare deux carrières par leur identité (`is`), que la façade
ne garde pas. L'essai de la question 2 en voyait 679 verts : il laissait le
simulateur Python entier, et ces tables s'y lisaient.

## Trouvé en chemin

- **La fiche de paie du jumeau.** Sur quatre témoins
  (`assimilee_apprenti_paye_peu`, `projection_cor_productivite_basse`,
  `rattachement_pension_smic`, `salaire_0.55`), `remuneration.py` ne refait
  pas la fiche que le portage calcule sous la proposition : le brut s'écarte
  du dernier chiffre, la réduction générale de 3 à 6 €, et le coût du
  travail avec elle. Aucun témoin n'écrit ces années, et le portage fait
  foi. Le test le déclare (`FICHES_QUE_LE_JUMEAU_NE_REFAIT_PAS`). Rien n'est
  corrigé : l'origine n'est pas cherchée.
- **La clé des simulateurs du portage.** `cleParametres`
  (`moteur/js/config.js`) écrit `{}` tout objet imbriqué : deux jeux de
  paramètres qui ne diffèrent que par leurs neutralisations partagent un
  simulateur. Sans effet sur un chiffre, les neutralisations ne commandant
  rien, et aucun autre paramètre n'étant un objet ; un paramètre de cette
  forme, s'il naissait, se perdrait sans bruit. Rien n'est corrigé.
- **Le zéro entier.** Le jumeau rend `pension_hors_repartition` « 0 »,
  entier, quand rien n'est hors de la répartition ; la lecture le rend 0.0,
  comme le type le dit.

## Ce qui reste

1. **Basculer les fichiers.** Aucun ne l'est. Par fichier : ses imports
   passent à `facade`, ses rouges se règlent, son nom quitte `FICHIERS`.
   Commencer par les fichiers dont tous les tests entrent par `simuler`,
   `calculer` ou `reversion`.
2. **Les tables du moteur.** Elles font 218 des 239 refus des deux
   fichiers. Une entrée de plus, la lecture d'une table du moteur par son
   nom et sa méthode, en lèverait la plupart ; `pont.droit` en sert déjà
   huit.
3. **Le contenu d'une liquidation au journal**, et
   `Simulateur.echeancier`, que 52 tests appellent et qui n'est pas une des
   huit entrées.
4. **Les entrées par fréquence** de la question 2, inchangées :
   `releve.construire`, `ConstructeurCompte`, `liquider.abattement_points`.

## Ce qui n'est pas vérifié

- La façade sur d'autres fichiers que les deux instruits.
- Les bâtisseurs sous chacune de leurs options : cinq cas sont confrontés au
  jumeau, et les tests des deux fichiers.
- `Simulateur.simuler` sur des données d'ailleurs (`racine_donnees`).
- La durée de la suite une fois des fichiers basculés.
- Ce que la liste ne voit pas : un fichier qui atteint le moteur Python par
  un outil commun (`tests/outils_pont.py`) ou par un script.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun témoin, aucun
script ; `pont.droit` et ses lectures ; les tests du moteur Python.

**Tests.** `tests/test_facade.py`, 45 tests, vus rouges puis verts, lancés
aussi sous `PRESOMPTIONS_DECALEES=1` ; `tests/test_facade_jumeau.py` ;
`tests/test_fichiers_sur_le_moteur_python.py` ; la suite rapide.
