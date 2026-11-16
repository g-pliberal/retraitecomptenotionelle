# Les chiffres ancrés au portage : la documentation ne lit plus les règles Python

Action 161, étape 5 de l'inventaire
(`2026-11-16-l-inventaire-du-retrait-des-regles.md`, section 5), menée la
nuit du 16 novembre 2026, sur la consigne du propriétaire d'avancer ce qui ne
demande pas son avis. Aucun chiffre de la prose, aucune donnée, aucun
résultat n'a bougé, et aucun module Python n'est supprimé.

- **Les ancres.** L'inventaire en comptait 22 ; la carte des jumeaux
  (`scripts/jumeaux.py`) en relève 23 qui chargent un fichier de règles par
  son nom, dans sept documents : `README.md`, `docs/methodologie.md`,
  `docs/parcours_presentation.md` et quatre parties de `docs/limites/`.
  Chacune lit désormais la même constante dans le moteur JavaScript, qui fait
  foi : l'âge d'ouverture de l'ASPA (`regimes.js`, quatorze ancres), le taux
  de la garantie de points (`regimes.js`, deux), les tranches d'âge des
  profils (`carriere.js`, deux), les deux surcotes de l'Ircantec
  (`droit/liquider.js`), les trimestres de décote des militaires
  (`droit/ouvrir.js`), la maturité maximale de la capitalisation
  (`capitalisation.js`, quatre). Les 23 valeurs ont été relues une à une :
  identiques ; `verifier_prose.py --corriger` ne récrit rien.
- **Le portage.** Trois constantes ne s'exportaient pas : `TAUX_DE_LA_GARANTIE`
  (`regimes.js`), `SURCOTE_IRCANTEC_AGE` et `SURCOTE_IRCANTEC_DUREE`
  (`droit/liquider.js`). Elles s'exportent, sans autre changement ;
  `tests/test_ircantec.py`, qui lit leur valeur littérale, accepte le mot
  `export`.
- **La garde.** `test_aucun_chiffre_ancre_ne_charge_un_fichier_de_regles`
  (`tests/test_jumeaux.py`), vu rouge d'abord sur les cinq fichiers de règles
  nommés, refuse une ancre qui charge un fichier des dossiers `droit/`,
  `moteur/`, `scenarios/` ou l'un des fichiers que la sonde du moteur Python
  compte parmi les règles.

Les ancres qui chargent `config.py`, `donnees/mortalite.py` et
`donnees/taux.py` restent : ces fichiers ont un jumeau, mais ne sont pas des
règles, et restent en Python (note de décision 0006).

**Ce qui reste.** Les gardes des jumeaux (`scripts/jumeaux.py`,
`tests/test_jumeaux.py`, `scripts/jumeaux_gardees.yaml`) ; les chargements
par chemin ; puis la carrière que le pont relit sous la classe des règles.

**Tests.** `python -m pytest -m rapide` : 5 693 passés.
`tests/test_jumeaux.py`, `test_ircantec.py`, `test_agirc_arrco_au_droit.py`,
`test_prose.py`, `test_site.py` : verts.
