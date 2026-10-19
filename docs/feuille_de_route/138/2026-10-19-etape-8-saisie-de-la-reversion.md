# Étape 8, quinzième partie : la saisie de la réversion du régime

**Le 19 octobre 2026, la demande.** Le premier reste de l'étape, dans l'ordre
du bloc « Reprise » : la saisie de la réversion du régime des non-salariés
agricoles, que les deux moteurs servent depuis la veille (note « réversion du
régime ») — le 2° de D. 732-110, II, la réversion retranchée de la PMR et
comptée au plafond. Session des pages de la vague du 19 octobre ; ni la PMR
revue quand les ressources changent, ni la durée de chef reconstituée, qui
viennent après.

**Ce qui est fait.**

- *Deux champs* : `reversion_agricole`, le mois où la réversion de la MSA
  commence (AAAA ou AAAA-MM), et `reversion_agricole_mensuel`, son montant
  mensuel brut de ce mois, en euros, zéro admis. Les deux saisies les lisent,
  les vérifient et les réécrivent dans l'adresse ;
  `reversion_agricole_declaree` (`reversionAgricoleDeclaree`) les rend telles
  que la chronologie les reçoit, et les deux contextes les passent aux deux
  chemins de la carrière, les métiers et le relevé, l'inversion par la pension
  comprise.
- *La vérification* : la réversion se dit entière — un montant sans mois, un
  mois sans montant se refusent — ; un mois lisible, qui suit la naissance, ce
  que la chronologie exige, et refusait sinon d'une erreur du modèle ; un
  montant positif ou nul. Les deux moteurs refusent par les mêmes mots.
- *Le formulaire* : les deux champs suivent les périodes de la carrière, et ne
  paraissent qu'avec une période de chef ou de collaborateur agricole, aux
  métiers ou au relevé, ou une réversion déjà dite. Leur bulle dit le droit
  (L. 732-41 à L. 732-46, D. 732-110, D. 732-112, D. 732-114), le montant en
  francs d'avant 2002 divisé par 6,55957, et la présomption : sans réversion
  déclarée, aucune n'est retranchée, et de 2009 à 2021 le montant du chef ne
  va qu'aux années de chef, et à celles de collaborateur de 1999 à 2008.
- *Les tests* : `tests/test_saisie_de_la_reversion_agricole.py`, la lecture et
  l'adresse, cinq refus et leurs voisines, les trois chemins de la carrière,
  la veuve saisie servie comme la règle le veut, le portage ; cinq refus et
  une voisine dans la confrontation des refus (`test_web.py`) ; le renvoi du
  formulaire et ses deux champs (`test_formulaire.py`). Un témoin de
  simulation, `reversion_agricole_veuve_de_2010`, et un de page,
  `simuler_reversion_agricole`, au formulaire entier ; aucun autre ne bouge.

**Le montant du premier mois**, comme la chronologie le porte, et non celui
d'aujourd'hui : c'est celui que la MSA notifie. Un montant d'aujourd'hui
demanderait de défaire les revalorisations, et les révisions sous le plafond
de ressources, qu'aucune pièce ne dit.

**La mesure.** La conjointe collaboratrice des tests de la règle, saisie par
l'adresse — née le 15 janvier 1952, collaboratrice de 1972 à son départ du
1er février 2016, veuve depuis mars 2010 à 150 € par mois — reçoit 331,09 € de
PMR : 8 182,60 € sur ses 164 trimestres, moins les 1 919,81 € que sa
réversion sert au départ, ce que la note de la règle mesurait. Le site sert
désormais la veuve qui déclare sa réversion.

**Ce qui reste**, de l'étape, dans l'ordre :

1. La PMR revue quand les ressources changent (D. 732-114), dont la réversion
   ouverte après le départ d'une pension prise de 2009 à 2021 ; puis la durée
   de chef reconstituée de D. 732-110, III.
2. Ce que la réversion déclarée permet désormais de servir aux plans de 1997
   à 2008 (D. 732-118, D. 732-116, D. 732-147), point 4 de la note
   « réversion du régime ».
3. À la fin de l'étape, avec la fiche `complement_differentiel_rco` : la fiche
   `pension_majoree_reference`, dont l'écart de la réversion dit encore « La
   saisie ne la demande pas encore ». Les fiches sont à une autre session.
4. Inchangés : les points 2 et 3 de « Ce qui reste » de la note « points des
   conjoints » ; au propriétaire, le montant de la MSA pour 2015 à 2017 et
   2019, depuis un poste qui atteint l'archive du web, et les seize points
   d'une année de conjoint d'avant 1999.
