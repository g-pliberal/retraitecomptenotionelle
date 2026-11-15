# La liste des fonctions gardées des deux côtés : chaque fonction écrite en Python et en JavaScript dans les 24 paires qui restent est déclarée, gardée ou au moteur, et un test la confronte au dépôt

Action 161, étape 7a, après `2026-11-15-la-fiche-de-paie-par-le-portage.md`.
Elle suit la recommandation de `2026-11-12-question-4-la-cloture.md` (la
clôture par fonction, la liste écrite avant le retrait du moteur Python),
que la note de décision 0008 a retenue. Aucune règle, aucune donnée, aucun
témoin n'a bougé.

## Ce qui est fait

- **La carte lit les fonctions** (`scripts/jumeaux.py`) :
  `fonctions_python`, par l'arbre syntaxique (fonctions du module et
  méthodes des classes, hors des méthodes spéciales et des fonctions
  imbriquées) ; `fonctions_javascript`, ligne à ligne (fonctions déclarées
  ou fléchées au bord gauche, méthodes des classes à deux espaces, hors du
  constructeur et des méthodes privées) ; `en_double`, au passage près de
  `nom_long` à `nomLong`.
- **La liste**, `scripts/jumeaux_gardees.yaml` : pour chacune des 24 paires
  qui restent (les 18 de `donnees/`, `config.py`, `calendrier.py`,
  `noyau/versions.py`, `contexte.py`, `frontiere.py`,
  `contributions_equilibre.py`), ses fonctions en double — 238 —, chacune
  *gardée* (170), avec le fichier Python qui la lit, ou *au moteur* (68).
- **Le test** : `ecarts_de_la_liste`, que
  `test_les_fonctions_gardees_des_deux_cotes_sont_declarees_et_tenues`
  exige vide sur le dépôt, rougit à une fonction en double non déclarée,
  une entrée périmée, une paire déclarée qui n'en est pas une, un lecteur
  qui est un test, un jumeau du moteur ou qui ne nomme pas la fonction, un
  test de confrontation absent. Vu rouge en ôtant `revenu_avpf` de la liste.
  Un dépôt miniature éprouve chaque faute.

## Comment la liste a été dressée

Par un script hors du dépôt, non commité. Une fonction est gardée quand un
fichier Python de `src/` ou `scripts/`, ni test, ni jumeau du moteur, ni
outil de la carte, emploie son nom dans son arbre syntaxique (un nom ou un
attribut, non une chaîne) et atteint la paire par la fermeture de ses
imports ; puis, par ricochet, quand une fonction gardée de son propre
fichier, ou le code de tête du module, l'appelle (le lecteur est alors ce
fichier). Le reste est au moteur. Une première passe par le nom seul
gardait à tort `applicable` (`versions.py`) ou `prime` (`primes.py`), lus
dans un commentaire ou un autre objet.

Ce qui part au moteur recoupe la note de la question 4 : les prélèvements
d'une paie et d'une pension (12 de `prelevements_historiques.py`), les
repères de validation de `macro.py` (`revenu_avpf`, `smic_horaire_de`,
`coefficient_smic`…), les méthodes de `PeriodeRegime` et
`ClassesCotisation.revenu_retenu` dans `regimes.py`, six méthodes de
`Parametres`, `versions.applicable`, `trimestres_civils`,
`mois_travailles` et `origine_des_ages` de `calendrier.py`,
`contributions_d_une_carriere` et `part_salariale_annualisee`.

## Ce que la liste ne dit pas encore

- **Un seul test de confrontation** est nommé : `en_mois`
  (`test_un_demi_mois_compte_le_mois_qui_suit_dans_les_deux_moteurs`).
  Les 169 autres fonctions gardées n'en ont pas ; la colonne `test` reste
  facultative tant que le test paramétré n'existe pas.
- **Les paires du moteur et de la zone grise** ne sont pas déclarées : la
  condition « aucune paire hors de la liste » ne pourra s'exiger qu'après
  le retrait du moteur Python.
- **Le lecteur est tiré des noms** : un nom commun (`taux`, `annee`)
  peut compter un lecteur à tort, et un accès par un objet reçu d'un
  module qui n'importe pas la paire peut manquer. La liste est à relire en
  écrivant les grilles du test de confrontation.

## Ce qui reste

1. **L'étape suivante (7b)** : le test de confrontation, un seul,
   paramétré par la liste — pour chaque fonction gardée, sur une grille
   d'arguments déclarée avec elle, le Python sur le YAML et le JavaScript
   sur le paquet rendent la même valeur au bit près — puis la colonne `test`
   rendue obligatoire. Commencer par les calculs (`mortalite.py`,
   `taux.py`, `patrimoine.py`, `distribution.py`), que le coût et le site
   font chacun de leur côté.
2. Puis le retrait des règles du moteur Python, d'un bloc, avec les 68
   fonctions `au_moteur` de la liste, qui en sortent alors.
3. Puis les périodes assimilées du relevé, en JavaScript seul.

**Tests.** `tests/test_jumeaux.py` (21) ; `python -m pytest -m rapide`.
