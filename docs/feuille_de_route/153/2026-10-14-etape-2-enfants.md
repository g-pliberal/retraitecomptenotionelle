# Étape 2, première famille : les enfants des fonctionnaires, confrontés à OpenFisca

**Le 14 octobre 2026, la demande.** Une session de nuit, la quinzième de dix-huit :
« action 153, étape 2, la famille des enfants : la bonification et la majoration de
durée au-delà de trois enfants, pour des enfants nés après 2004 ou hors des
services. » Aucun fichier des pages ni de la saisie n'est touché, aucun déplacé.

**Ce qui a été lu.** OpenFisca-France-Pension 0.1.3, installé à part dans un
environnement jetable (il lui faut un `setuptools` d'avant 70, pour
`pkg_resources`) : `bonification_cpcm_enfant`, `majoration_duree_assurance_enfant`,
`majoration_duree_assurance`, `duree_assurance`, `coefficient_de_proratisation`,
`majoration_pension` et `pension`, et le barème `bonification_enfant`. Dans l'index
LEGI, à jour au 11 octobre : L. 12, b et b bis (2004) ; R. 13 de 2004 et de 2009 ;
L. 12 bis ; l'article 21 du décret n° 2003-1306, en 2004 et en 2011. Le journal de
veille a son entrée (`2026-10-14-action-153-etape-2.yaml`).

**La convention de traduction**, écrite en tête de
`scripts/fetch/openfisca_enfants.py`, frère du script de l'étape 1 dont il reprend
la carrière, les régimes et les grandeurs, et portée par le témoin
(`tests/temoins/openfisca_enfants.json`) :

- *La carrière* : celle de la première famille, à temps plein, sans période au
  régime général.
- *Les enfants* : au dépôt, des naissances datées, comparées au recrutement et à la
  radiation ; OpenFisca n'en lit que le nombre et le compte de ceux nés avant 2004,
  pendant les services ou non, plus la troisième naissance au parent de trois
  enfants.
- *La liquidation au régime général* n'est pas déclarée : OpenFisca n'accorde les
  trimestres d'enfants qu'au fonctionnaire qui liquide avant elle, et la laisse
  sinon en 2250.
- *Ce qui ne se traduit pas* : le recrutement et la radiation ; l'interruption
  d'activité, que le dépôt présume de la mère seule ; le b bis de L. 12, que ni
  l'un ni l'autre ne lit ; les conditions d'éducation de L. 18.
- *Le départ des parents*, objet de la première famille, ne joue sur aucune
  pension confrontée : les parents de quatre et cinq enfants sont entrés en 1998,
  et ne réunissent leurs conditions qu'après 2011 ; la mère de sept enfants les
  réunit, mais atteint des deux côtés le pourcentage maximum de 80 %. Le test le
  vérifie.

**Ce qui est fait.** Dix profils, liquidés de 2009 à 2020, à l'État et à la CNRACL :
quatre parents de quatre à sept enfants, trois mères d'enfants nés depuis 2004
(deux, à l'État et à la CNRACL, et un de chaque côté de 2004), trois mères
d'enfants nés avant leur recrutement (pensions de 2009 et de 2015, et un
accouchement de 2005 avant un recrutement de 2006). `tests/test_oracle_enfants.py`,
au niveau des contrôles : onze tests, la convention d'abord ; il reprend le calcul du
dépôt de `test_oracle_familles.py`. Le manifeste a sa ligne
(`openfisca_enfants_oracle`) ; le registre trois écarts, le point 153.2 et le bilan ;
les fiches `enfants_fonction_publique` et
`majoration_enfants_plafond_fonction_publique` leur bloc `referents`, la première
une approximation de plus, le b bis ; les limites (`3-systeme-actuel.md`) un
paragraphe.

**Ce que la confrontation a trouvé.**

- *Au-delà de trois enfants : rien à corriger.* Seize, vingt et vingt-huit
  trimestres de bonification, rien au père ; la majoration de L. 18 à 15 et 20 % ;
  la mère de sept enfants, à 80 % et cinq trimestres de surcote, que 30 % porteraient
  à 110 % du traitement : les deux servent le traitement. Pension au centime.
- *Les enfants nés depuis 2004 : rien à corriger à l'État.* Deux trimestres de
  durée par enfant, aucun de services, des deux côtés, et la décote qui s'en
  déduit ; l'enfant né en 2002 garde son an de bonification.
- *Trois écarts, tous chez OpenFisca* :

  | profil | le dépôt | OpenFisca | ce qui tranche |
  |---|---|---|---|
  | CNRACL, deux enfants nés en 2004 et 2007, partie en 2020 | 4 trimestres de majoration, 19 de décote | aucun, 20 de décote | décret n° 2003-1306, article 21, I |
  | deux enfants nés avant un recrutement de 1985, partie en 2009 | aucune bonification | 8 trimestres, pension plus forte de 8/96 | R. 13 de 2009 (congé du statut), hors du b bis |
  | un enfant né en 2005, recrutée en 2006 | aucune majoration | 2 trimestres, sans effet sur la pension | L. 12 bis (« postérieurement à leur recrutement ») |

  À la CNRACL, sa variable compare la liquidation de l'ÉTAT à celle du régime
  général — ce que la note de l'étape 1 avait vu en lisant le code. Les mêmes
  enfants nés avant le recrutement, pour une pension de 2015, concordent : R. 13
  admet depuis 2011 l'enfant né avant la radiation. L'oracle a donc trouvé
  quatorze erreurs chez OpenFisca, trois à cette étape.

**Ce qui ne bouge pas.** Aucun résultat, aucun moteur, aucune page, aucune règle :
le modèle avait raison sur chaque point confronté. Aucun signalement à OpenFisca.

**Ce que le dépôt ne fait pas, vu en passant.** Le b bis de L. 12 — la
bonification de la femme qui a accouché pendant ses études, recrutée dans les deux
ans de son diplôme, sans interruption — n'est pas porté : aux pensions de 2004 à
2010, l'enfant né avant le recrutement n'ouvre rien chez nous. Il faudrait à la
saisie les études et le diplôme ; déclaré dans les approximations de la fiche, à
mesurer. L'article 21 de la CNRACL, depuis 2011, interdit le cumul de la majoration
avec la durée d'assurance du temps partiel ou de l'interruption pour l'enfant, si
celle-ci atteint deux trimestres : les profils, à temps plein, ne l'éprouvent pas.

**Ce qui devrait s'écrire dans les pages**, que cette session ne touche pas : rien
n'y devient faux. Au plus, la phrase de `methodeConstruction` (`pages.js`) sur les
« calculateurs extérieurs comme OpenFisca » pourrait nommer les enfants des
fonctionnaires parmi ce qu'ils confrontent.

**Ce qui reste.** L'étape 2 continue, une famille par session : la catégorie
active, la carrière longue de la fonction publique, les minima (le minimum garanti
de la CNRACL, nul chez lui), les points enfants et la minoration de l'Arrco, les
périodes assimilées, le salaire annuel moyen sur des salaires qui varient. Le
propriétaire tranche le signalement à OpenFisca, de quatorze erreurs désormais.
