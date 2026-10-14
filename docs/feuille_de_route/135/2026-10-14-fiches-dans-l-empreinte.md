# Les fiches de règles dans l'empreinte, sans leur documentation

**Le 14 octobre 2026.** La note du 10 octobre laissait les fiches de règles :
le modèle en lit une centaine, et elles changent souvent pour leur seule
documentation — la date de lecture, l'état —, ce qui refaisait toute la
mémoire des calculs.

- *L'empreinte.* `memoire.CHAMPS_DOCUMENTAIRES` nomme les champs d'une fiche
  qui la documentent : `intitule`, `etat`, `effet`, `sources`,
  `approximations`, `exemples`, `referents`, `historique`,
  `textes_a_rattacher`, `textes_sans_effet`, `textes_a_relire`. L'empreinte
  lit chaque fiche de `data/reference/regles/` sans eux
  (`_sans_documentation`), par le texte, sans analyser le YAML : une clé de
  premier niveau commence en première colonne, et son bloc court jusqu'à la
  suivante. L'empreinte reste sous le dixième de seconde.
  `test_l_empreinte_d_une_fiche_ignore_sa_seule_documentation` vérifie, sur
  les 225 fiches, que le texte qui reste se lit comme la fiche privée de ces
  champs.
- *Le garde-fou.* `charger_yaml` laisse un relevé substituer au dictionnaire
  rendu un dictionnaire qui note les champs lus (`chargement.SUIVI`, `None`
  hors du relevé). `scripts/lectures_du_modele.py` s'en sert pour les fiches :
  un champ lu, ou la fiche parcourue, copiée, comparée en entier (`*`), et
  une fiche ouverte sans `charger_yaml` compte pour lue en entier. Le relevé
  du jour : 96 fiches lues, et rien d'autre que `id`, `versions`,
  `dates_qui_decident`, `code` et `regimes`. Le script échoue, et
  `test_aucun_calcul_garde_ne_lit_ce_que_l_empreinte_ignore` avec lui, si un
  calcul gardé lit un champ documentaire. La carte (`noyau/carte.py`) et le
  registre des textes (`noyau/textes.py`) lisent `etat`, `sources`,
  `exemples` et les listes de textes, mais aucun calcul gardé ne passe par
  là.
- *Ce qui n'y est pas.* Les champs structurels que les calculs ne lisent
  pas aujourd'hui (`etape`, `face`, `lit`, `ecrit`, `domaine`, `reformes`,
  `presomptions`) restent dans l'empreinte : le relevé ne couvre que deux
  carrières par statut, et une branche qu'il ne parcourt pas pourrait les
  lire. Seule la documentation, qu'aucun code du modèle ne cherche, en sort.

**Mesuré.** L'historique de `main` ne remonte plus qu'au 14 octobre (53
commits) : 23 changeaient l'empreinte, 13 en touchant des fiches ; 3 ne la
changent plus. La part reste à mesurer sur un mois de commits.

**Ce qui reste.** La fin du portage que node rejoue (note du 10 octobre) ;
`actions/cache` sur GitHub, au propriétaire.
