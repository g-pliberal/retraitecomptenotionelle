# Étape 2 de la note 0009, première session : les versions de l'âge légal deviennent la source

**Reprise, au 19 novembre 2026.** L'étape 2 de la note de décision 0009 range
l'âge légal dans les versions de sa fiche, en trois sessions. La première est
faite : la fiche `age_legal_par_generation` porte six versions, et la table de
l'âge légal comme ses deux copies d'avant réforme se fabriquent depuis elles,
identiques à ce qu'elles étaient. Le moteur ne les lit pas encore. Reste la
deuxième session, qui fait lire l'âge légal au moteur par ces versions, puis
la troisième, qui change les deux droits d'avant réforme en couches. Commencer
par le brief de la deuxième session, « Brief A2b », dans
`/mnt/project-files/architecture/191-briefs-amendes.md`. Aucun résultat ne
doit bouger. Au propriétaire : dire si les deux copies passent du niveau
`haute` au niveau `certifiee`, et faire relire par une autre session les deux
versions de 1985 à 2011, qui n'ont pas d'exemple officiel.

Le 19 novembre 2026, le propriétaire ouvre l'étape 2 de la note de décision
0009. Cette session en est la première des trois (« Brief A2a ») : les
versions de la fiche deviennent la source de l'âge légal, sans que le moteur
change. Aucune règle ne bouge, et aucun résultat.

**Ce que le contrat de la fiche dit de plus.** Le contenu d'une version reste
libre, mais trois de ses parties ont une forme
(`data/reference/contrats/fiche.yaml`, `noyau/contrats.py`) :

- `table` désigne les lignes de la version dans un fichier : le fichier, les
  colonnes qui choisissent les lignes, la colonne de la clé, celle de la
  valeur ;
- `renvois` est une liste de renvois datés. Chacun nomme la fiche lue, la
  valeur, la date qui choisit la version, et la personne dont on lit l'âge,
  `assure` ou `conjoint_survivant` (liste `personnes_lues` du vocabulaire) ;
  il porte au plus une opération, une durée ajoutée ou retranchée, ou un
  code ;
- `redaction_anterieure` nomme la version de la même fiche à laquelle le texte
  renvoie, et les naissances qu'il lui laisse.

**Le contrôle des renvois** (`noyau/renvois.py`, `tests/test_renvois.py`) dit
ce qui ne tient pas d'une fiche à l'autre : la fiche lue manque, ne se choisit
pas à la date nommée, n'a pas une version et une seule sur toute l'étendue de
la version qui lit, ne porte pas la valeur ; la rédaction antérieure n'est pas
une autre version de la fiche ; une chaîne de renvois boucle. La carte le joue
(`carte.controler`), et la fabrication des tables de l'âge légal avant
d'écrire : un renvoi sans cible arrête la fabrication.

**Le récupérateur écrit la table de chaque version.**
`scripts/fetch/dila_legi_parametres_retraite.py` écrit, à côté de la table
fusionnée, ce que chaque rédaction de L. 161-17-2 et de D. 161-2-1-9 dit
elle-même : 38 lignes, que la certification verse dans
`data/reference/legislation/age_legal_par_version.csv`. Aucune table n'est
recopiée à la main dans la fiche.

**Les six versions de la fiche**, choisies par la date d'effet de la pension :

| Version | Pensions prenant effet | Texte | Exemple officiel |
|---|---|---|---|
| `avant_la_codification_de_1985` | avant le 21 décembre 1985 | aucun dans l'index, version `supposee` | aucun |
| `soixante_ans` | du 21 décembre 1985 au 30 juin 2011 | R. 351-2, « fixé à soixante ans » | aucun |
| `loi_de_2010` | du 1er juillet au 22 décembre 2011 | loi n° 2010-1330, décret n° 2010-1734 | aucun |
| `loi_de_2011` | du 23 décembre 2011 au 31 août 2023 | loi n° 2011-1906, décret n° 2011-2034 | `cnav_2012_27_inapte` |
| `loi_de_2023` | du 1er septembre 2023 au 31 août 2026 | loi n° 2023-270, décret n° 2023-436 | `cnav_2026_07_decote_1961`, `cnracl_surcote_ne_un_1er` |
| `suspension_de_2025` | à compter du 1er septembre 2026 | loi n° 2025-1403, article 105 | les cinq exemples de la fiche |

La version de la suspension n'écrit que les assurés nés à compter du
1er septembre 1961 ; pour les autres, elle renvoie à sa rédaction antérieure,
la version de 2023, comme le fait l'article. Quand la loi et le décret d'une
même version écrivent la même génération, ils doivent dire le même âge, sans
quoi la fabrication s'arrête.

**Les trois tables se fabriquent** (`donnees/tables_de_version.py`,
`tests/test_tables_de_version.py`). `age_ouverture_requis.csv` est la table de
la dernière version ; chaque copie d'avant réforme est la table de la version
que la réforme a fermée, depuis la première génération qu'elle change.
`scripts/verifier_donnees.py --appliquer` les confronte : 79, 1 et 5 valeurs
identiques, aucune corrigée, aucune ajoutée. Les trois fichiers n'ont pas
changé d'un octet.

**Ce qui a bougé.** Aucun calcul : les témoins des simulations, des pensions
servies et du droit sont identiques. La page « Méthode » du site, qui affiche
le journal de la certification, compte trois séries de plus, la table par
version et les deux copies, que le brief plaçait sous ce contrôle : 233 séries
au lieu de 230, 443 506 valeurs recontrôlées au lieu de 443 462. Deux
compteurs baissent : les réformes dont la fiche n'avait pas de version, de 96
à 94 (`tests/cliquets_du_droit_date/reformes.yaml`), et les rédactions citées
sans réponse, de 435 à 433 (`data/reference/textes/perimetre.yaml`).

**Ce qui reste ouvert.**

- Les deux copies gardent le niveau `haute`. Les passer à `certifiee`, puisque
  leurs valeurs viennent maintenant de LEGI, changerait la fiabilité affichée
  sous les droits d'avant réforme : au propriétaire de le dire.
- `soixante_ans` et `loi_de_2010` décident de pensions du régime général et
  n'ont pas d'exemple officiel : la fiche dit où l'exemple a été cherché. Une
  seconde lecture de leurs textes, par une session qui n'a pas vu celle-ci,
  est demandée.
- La version d'avant le 21 décembre 1985 est `supposee` : ses textes ne sont
  pas dans l'index de la DILA.
- La version de 2011 commence le 23 décembre 2011, date d'entrée en vigueur de
  la loi, quand son décret date du 31 décembre : LEGI ne porte pas de
  disposition d'application, et aucune pension ne prend effet entre les deux.
- La fiche n'est pas encore de celles que le moteur lit : c'est la deuxième
  session.

**Ce que la session a coûté.** Un commit, 27 fichiers, dont sept nouveaux :
deux modules, deux fichiers de tests, la table par version, cette note et
l'entrée du journal de veille. Ouverte à
22 h 04 UTC le 19 novembre 2026 et close dans la soirée, sur Fable 5.2.
