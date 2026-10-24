# La carte des fiches : le code des minorations des complémentaires, écrit

**La demande.** Vague du 24 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui, et onze tournent ensemble. Celle-ci, de
l'action 130 : écrire, pour un premier lot, les fonctions et les paramètres des
fiches que `EN_PROSE` (`tests/test_carte.py`) tient encore à leur seule phrase
`moteur`, 46 au 23 octobre, jusqu'à ce que le test confronte leur code au dépôt
comme celui des autres ; les lots suivants viendront dans d'autres sessions.
Aucun chiffre du modèle ne bouge : seuls changent les champs `code` et
`regimes` de dix fiches, et `EN_PROSE`.

## Ce qui est fait

- **Un lot de dix fiches**, de 46 à 36, vu rouge — `EN_PROSE` resserré
  d'abord, le cliquet rougissant de quarante écarts, quatre par fiche —, puis
  écrit et vert : les huit minorations des complémentaires des libéraux
  (CARCDSF, CARMF et ASV des médecins, CARPV, CAVAMAC, CAVEC, CAVOM, CAVP,
  CPRN) et les deux de l'IRCEC (`minoration_ircec`,
  `minoration_racl_2014_2024`). Toutes passent par `liquider.abattement_points`
  (`abattementPoints`) : le barème par année d'âge, `abattement_ircec`, que
  `_ABATTEMENTS_IRCEC` et `_ABATTEMENTS_PAR_ANNEE_AGE_SEUL` ouvrent à `cavom`,
  et l'annexe du RACL, `_MINORATION_RACL_2014` ; ou la décote du régime de
  base, `abattement_regime_de_base`, `decote_opposable`, et
  `trimestres_de_decote`, qui lit `decote_annulee_par_la_duree` ; l'âge,
  `ouvrir.age_taux_plein` et `age_ouverture`, avec les tables de
  `legislation/ages_regimes.csv` (`AgesRegimes`) ; la majoration après l'âge,
  `surcote_points`, et la sortie sans minoration des mères de la CARCDSF,
  `taux_plein_anticipe`. La majoration pour trois enfants qu'une fiche nomme
  se sert dans `completer`, au taux de `_taux_majoration_enfants` ; le passage
  du RACL à la règle commune, le 16 mai 2025, par le champ `date_effet` et
  `commun.periode_de_liquidation`. Les tests : `test_sections_sante.py`, avec
  son jumeau de `tests/js/moteur.test.js`, `test_sections_liberales.py`,
  `test_sections_juridiques.py` ; pour l'IRCEC, `test_simulateur.py` et
  `test_coupures_au_mois.py`.
- **Le champ `regimes`, que ces fiches n'avaient pas**, et sans lequel l'outil
  ne lit pas un champ de fiche de régime : chacune reçoit les régimes dont les
  périodes renvoient à elle par un interrupteur, et celle de la CARMF aussi
  l'ASV des médecins (`asv_conventionnes`), dont elle décrit la majoration pour
  enfants depuis 1981, que `test_sections_sante.py` tient. La carte passe de
  792 manques à 782 ; ses 106 fiches à mûrir restent.
- **Ce que les paramètres nomment** : les champs que la règle lit dans les
  périodes, et les lignes de la table des âges ; les interrupteurs, que
  `code.interrupteurs` déclare, n'y sont pas redits. « Aucune surcote » (CAVOM,
  CARPV) n'est pas un champ : c'est le défaut `surcote_points: aucune`, et la
  fiche nomme la fonction qui l'applique.

L'écriture s'est faite par un outil de session, hors du dépôt, comme aux lots
précédents : il essaie le code proposé contre `outils_carte.ecarts`, l'écrit à
la fin du bloc `code:` de la fiche, en `>-` à 88 colonnes, sans ouvrir de ligne
sur « : » ni « ; », pose `regimes` avant `etat`, et vérifie au chargement que
rien d'autre n'a bougé. `conservation.py --depuis HEAD` n'a rien vu de perdu ;
`jumeaux.py` ne voit aucun renvoi mort. L'index LEGI n'a pas été remis à jour :
l'étape n'écrit aucune règle du scénario 1, et le journal de veille n'a pas
d'entrée. Rien n'est dû aux pages.

## Ce que l'étape laisse

- Les 36 fiches de `EN_PROSE`, avec leurs interrupteurs pour 32 d'entre elles
  et leurs tests pour deux ; aucune n'a de champ `regimes`, que leurs
  paramètres demanderont comme ici. `pension_non_salaries_agricoles_2026` est
  à la session de l'action 131. Des lots se dessinent : les décotes et les
  surcotes des régimes de base et des régimes spéciaux, les âges et les durées
  par génération, les cotisations et les points des libéraux, les
  coefficients de l'Agirc-Arrco et de l'Ircantec.
- Les limites de l'outil : `Classe.méthode` se vérifie nom par nom, non que la
  méthode est de la classe ; un champ de classe, une fonction locale du
  JavaScript, une clé dans une liste d'un YAML ne se nomment pas ; un nom
  cité n'est pas vérifié lire ce que la fiche dit.
- `code` n'est toujours pas parmi les champs documentaires de `memoire.py`.
- Les 106 fiches à lire au droit, et les points ouverts des phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition du sixième domaine, et celle sur
la retraite progressive, le cumul et la seconde pension, README muet.
