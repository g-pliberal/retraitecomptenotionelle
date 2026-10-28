# Étape 4, suite de la huitième partie : le champ qui dit l'enfant étudiant, apprenti ou infirme, et jusqu'à quand

**Le 28 octobre 2026, la demande.** La vague du jour, une session par tâche
qui se mène sans le propriétaire : le premier point « Au site » du bloc de
l'étape, « les études », détaillé au point 1 du « Ce qui reste » de la
huitième partie (`2026-10-24-etape-4-parts-prolongation-et-regime.md`) — le
champ qui dit l'enfant étudiant, apprenti ou infirme, et jusqu'à quand, que
le modèle lit déjà (`chronologie.prolongations_de_la_charge`). Ce champ seul :
l'enfant né après le départ, les révisions et les autres points du site
viendront à d'autres sessions.

**Ce qui est fait.**

- *La chronologie* : `avec_prolongations_de_la_charge`, et son jumeau
  `avecProlongationsDeLaCharge`, sur le modèle de `avec_periodes_assimilees`.
  Chaque déclaration — le rang de l'enfant, dont la naissance est dite, son
  motif, `etudes`, `apprentissage` ou `infirmite`, et la fin des études ou de
  l'apprentissage s'il la dit — devient un fait de l'enfant que
  `prolongations_de_la_charge` relit : une période d'études, un emploi qui
  porte `apprentissage`, une décision médicale `infirmite`, sans fin. Chacun
  court depuis la naissance de l'enfant, comme les revenus d'activité du
  conjoint courent depuis le décès : à charge jusqu'à l'âge limite quoi qu'il
  fasse, l'enfant ne doit à son motif que ce qui suit, et les parts sont
  celles d'un fait qui commencerait à seize ans. Les constructeurs
  `depuis_parcours` et `depuis_releve` la reçoivent
  (`prolongations_de_la_charge`) ; vide, la chronologie ne change pas.
- *La saisie* : le champ `charge_enfants`, « 1:etudes:2009-07, 2:infirmite »,
  sous « Naissance des enfants », dans les options de modélisation : le rang,
  le motif, écrit avec ses accents ou sans, et le mois où les études ou
  l'apprentissage cessent, premier jour hors de charge, comme les autres fins
  du formulaire. Elle refuse une entrée mal formée, un rang hors des enfants,
  un enfant sans naissance dite, un motif inconnu ou dit deux fois pour le
  même enfant, une infirmité datée, une fin illisible ou qui précède la
  naissance ; l'adresse garde le champ tel qu'il est écrit ; le contexte le
  passe aux deux chemins de la carrière, le parcours et le relevé.
- *Les tests* : `test_chronologie.py` — les faits, les refus, les deux
  constructeurs, sept saisies confrontées aux deux moteurs ; `moteur.test.js`
  — la déclaration rend les étapes des faits posés à la main, aux quatre cas
  de la huitième partie ; `test_web_saisie.py` — la carrière que le portage
  bâtit, l'adresse, le formulaire, dix refus ; `test_web.py` — deux refus et
  leurs voisins, qui calculent.
- *Un témoin de simulation* : `reversion_enfants_etudiant_et_apprenti`, le
  veuf de 2024 dont l'aînée étudie et le cadet est apprenti jusqu'en septembre
  2033. Par le pont, avant la fabrique : la majoration baisse le 1er février
  2032 et cesse le 1er octobre 2033, au lieu du 1er février 2030 et du
  1er février 2032.
- *Le texte* : la présomption `charge_jusqu_a_l_age_limite` au vocabulaire,
  l'approximation de la fiche `majoration_forfaitaire_reversion` et la page
  des écarts au droit positif disent que le formulaire les demande ; celle de
  la fiche `majoration_enfants_a_charge_agirc_arrco`, que sa règle ne les lit
  pas.

**Les mesures.** Dans Chromium, à 320 et à 1 280 points, la page que le
routeur recalcule porte le champ sans erreur ni défilement en largeur ; la
page toute faite du simulateur est refaite (`construire_pages.py`). Les
témoins, le paquet et les chiffres ancrés restent à la fabrique de GitHub :
à l'ouverture, sur le dernier `main`, `regenerer.py --verifier` les disait
périmés, et sept confrontations de `-m rapide` (le pont, les coupures au mois,
la surcote parentale, le cycle de vie de la profession libérale de 1960)
échouaient déjà, comme le test des témoins du portage, 102 écarts sur 909
cas, avant comme après ces commits.

**Ce qui reste.**

1. *Au site*, les autres points du bloc : l'enfant né après le départ, que
   `verifierNaissances` refuse toujours ; les révisions et leurs quatre
   champs ; la catégorie ; la période et son moment ; le plancher non majoré ;
   la page, qui tait une majoration nulle à la date d'effet et servie ensuite.
2. *Au modèle* : la majoration de l'Agirc-Arrco pour enfants à charge, qui
   tient l'étudiant et l'apprenti jusqu'à vingt-cinq ans, pourrait lire les
   mêmes faits (fiche `majoration_enfants_a_charge_agirc_arrco`, première
   approximation) ; l'aide du champ, qui ne nomme que la réversion, suivrait.
