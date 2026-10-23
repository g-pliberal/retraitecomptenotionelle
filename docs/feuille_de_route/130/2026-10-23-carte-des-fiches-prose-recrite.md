# La carte des fiches : les vingt-trois fiches au code en prose, récrites

**La demande.** Vague du 23 octobre 2026, seconde salve : la session de suivi
« Qu'est-ce qu'il reste à faire ? » lance, sur la demande du propriétaire
(« Fait ça », en réponse à l'offre d'une session par chantier qu'une session
peut mener seule), la session de l'action 130, maintenant que les six
sessions de la première salve qui touchaient aux fiches se sont arrêtées. Son
point : vider `EN_PROSE` (`tests/test_carte.py`) de ses 23 fiches à récrire,
celles dont le champ `code` s'écrivait encore en prose
(`130/2026-10-23-carte-des-fiches-code-confronte.md`), par lots, chacun
commité au vert, le test jamais rouge sur `main` ; les 46 fiches dont le code
est à écrire viennent après, à une autre session. Aucun chiffre du modèle ne
bouge : seuls changent le champ `code` de 23 fiches et `EN_PROSE`.

## Ce qui est fait

- **Quatre lots**, du huitième au onzième de l'action, de 69 fiches en prose
  à 46 : 8, 8, 4 et 3 fiches, chacun vu rouge — `EN_PROSE` resserré d'abord,
  le cliquet rougissant des écarts des fiches sorties —, puis récrit, commité
  au vert et publié (3b8c6a6, a4c9503, c6ba0d2, bb804ea). Le premier : les
  trois fiches du chômage des complémentaires, les fractions des cultes, les
  enfants et le versement unique de l'Ircantec, les services passés
  outre-mer, la réversion du RAFP. Le deuxième : les deux moyennes, la
  seconde pension, la liquidation régime par régime, les points d'avant 1973,
  l'âge du RAFP, le relèvement de 2023, l'invalidité des fonctionnaires. Le
  troisième : le minimum contributif et son pendant international, la pension
  proratisée, la totalisation des périodes étrangères. Le dernier : la
  retraite progressive, le cumul emploi-retraite, l'abattement micro-social.
- **La convention des sept lots**, suivie, et ce qu'elle devait trancher de
  neuf. Un témoin nommé sans fichier se nomme dans le sien,
  `tests/temoins/simulations.json : <témoins>`, chacun vérifié parmi ses
  clés ; « le balayage des deux statuts », par les témoins
  `statut_<statut>` de chaque génération ; un exemple du registre, par
  `tests/temoins/exemples_officiels.yaml : <id>`. Les constantes de module
  que la prose décrivait — « les dates de 2023, de 2025 et de 2027 », « le
  délai de six mois, le SMIC sur 1 820 heures et sa part » — se nomment aux
  champs `python` et `javascript` (`droit/seconde.py`, `droit/cumul.py` et
  leurs jumeaux), et la phrase passe au champ `moteur`. Y passent aussi les
  champs de classe, que l'outil ne lit pas : `Demande.regimes`,
  `Etat.servies`, `EligibleMinimum` et les siens, `PeriodeCoordonnee.comparee`,
  `TrimestresEtrangers.nationaux`, `Coordination.etranger`, `Durees.etranger`,
  `ResultatActuel.droits_apres_depart`, `.cumul` et `.trimestres_etrangers`,
  `Carriere.lignes_apres_depart`, `AnneeCarriere.quotite`, `Metier.micro`,
  `PensionRegime.capital` ; une classe que le portage n'a pas, et l'objet
  qu'il bâtit à sa place (`EligibleMinimum`, dans `liquiderChaqueRegime` ;
  `ResultatActuel`, dans `resultatActuel`) ; une fonction locale du portage,
  `plancherNational`, dans `completer` ; la clé `calcul` des accords
  internationaux, dans une liste. Une prose `moteur` que la récriture
  prolonge garde ses lignes.
- **Ce que la récriture a corrigé.** `salaire_de_reference_ircantec`, qui
  n'existe pas : `salaire_de_reference_points`. `FicheDatee` :
  `FichesDatees`. `MaximumDesCultes`, que le portage définit dans
  `regimes.js` et non `scenario-actuel.js`, qui l'instancie ;
  `CotisationsDesCultes`, de `donnees/regimes.py`, que `moteur/compte.py` lit
  sans la définir. `Demande.regimes`, que l'outil laissait passer par la
  méthode `Liquidation.regimes` du même fichier. `PensionRegime.capital`, dit
  « de droit/liquider.py et droit/commun.py » : la classe est à
  `droit/commun.py`, `prestation_rafp` fixe le capital. Le RSI, né en 2006,
  ne porte pas le champ du minimum entier de 1983 à 1989
  (`pension_bornee_au_minimum_entier_avec`), que la CANCAVA et l'ORGANIC
  seules portent. Les listes de paramètres incomplètes — `decote_maximum` de
  la retraite progressive, `jouissance`, `duree_de_services_minimale` et
  `minimum_garanti_sous_quinze_ans` de l'invalidité, entre autres — portent
  tous ceux des versions ; les chemins `data/reference/legislation/…` sont
  devenus `legislation/…`.

La récriture s'est faite par un outil de session, hors du dépôt, comme aux
sept lots : il essaie le code proposé contre `outils_carte.ecarts`, puis le
récrit dans le texte de la fiche, en `>-` à 88 colonnes, sans ouvrir de ligne
sur « : » ni « ; », et vérifie au chargement que rien d'autre n'a bougé.
`conservation.py --depuis HEAD` n'a rien vu de perdu à aucun lot ;
`jumeaux.py` ne voit aucun renvoi mort dans les champs `code`, avant comme
après ; la carte garde ses 106 fiches à mûrir et ses 792 manques. L'index
LEGI n'a pas été remis à jour : l'étape n'écrit aucune règle du scénario 1,
et le journal de veille n'a pas d'entrée. Rien n'est dû aux pages.

## Ce que l'étape laisse

- `EN_PROSE` ne garde que les 46 fiches dont le code n'est que la phrase
  `moteur`, avec leurs interrupteurs pour 42 d'entre elles et leurs tests
  pour deux : leurs fonctions et leurs paramètres sont à écrire, par lots,
  l'étape suivante.
- Les limites de l'outil : `Classe.méthode` se vérifie nom par nom, non que
  la méthode est de la classe ; un champ de classe, une fonction locale du
  JavaScript, une clé dans une liste d'un YAML ne se nomment pas.
- `code` n'est toujours pas parmi les champs documentaires de `memoire.py`.
- Les 106 fiches à lire au droit, et les points ouverts des phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition du sixième domaine, et celle sur
la retraite progressive, le cumul et la seconde pension, README muet.
