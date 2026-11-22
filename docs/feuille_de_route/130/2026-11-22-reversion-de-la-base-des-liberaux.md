# La réversion de la base des libéraux servie, celle du régime général

Ouverte le 22 novembre 2026 sur la confrontation au simulateur de réversion
d'info-retraite (`comparaisons/2026-11-22-simulateurs-des-caisses/` des fichiers du
projet) : dans les dix sections, le simulateur sert 54 % de la base, le modèle rien
(motif `non_portee`). C'est le premier des écarts de réversion de ce jour.

**Le texte, lu à l'index LEGI** (à jour du 16 novembre 2026). L. 643-7, depuis le
1er janvier 2004 (loi n° 2003-775, LEGIARTI000006743799) : « En cas de décès de
l'assuré, son conjoint survivant a droit à une pension de réversion dans les
conditions prévues aux articles L. 353-1, L. 353-2 et L. 353-3 », et L. 353-6 depuis
le 1er janvier 2010 (LEGIARTI000019959385). Avant 2004, l'allocation de réversion
de L. 643-9 et D. 643-5 : la moitié de l'allocation, à 65 ans (60 en cas
d'inaptitude), deux ans de mariage sauf enfant ; différentielle de l'avantage
personnel de 1985 à 1988, puis cumulée dans la limite de 50 % du total, sans
descendre sous 70 % du maximum des pensions du régime général ; le divorcé non
remarié au prorata (D. 643-7), perdue au remariage (D. 643-11). Le simulateur le
confirme pour aujourd'hui : 540 € pour 1 000 €, l'âge de 55 ans, le refus au-dessus
de 25 001,60 € de ressources.

**Le test d'abord** (`tests/test_reversion.py`, « la base des professions
libérales »), vu rouge sur quatre cas (`non_portee`) : la veuve du médecin, née le
15 mars 1960, 15 000 € de ressources, 54 % × 12 000 = 6 480 € par an au
1er avril 2026 ; la survivante de 52 ans servie à ses 55 ans ; au-dessus du plafond,
rien, et sous lui, le plafond moins les ressources ; la base et le régime général
ensemble sous le plafond, 4 320 et 5 400 €. Un cinquième tient la ligne d'avant 2004.

**La correction.** Une fiche, `reversion_cnavpl`, la seule place de cette règle :
quatre versions sur la date d'effet. Depuis 2004, la version
`regime_general_depuis_2004` ne recopie aucune valeur : elle porte `renvoi:
reversion`, et le moteur lit la version de la fiche du régime général en vigueur aux
mêmes dates (`Reversions.version`, `versionsSuivies` pour la date d'effet). La
réversion de la base est servie par la branche du régime général
(`SUR_LE_REGIME_GENERAL`) : le taux, l'âge, le plafond, le minimum, la majoration de
11,1 %, et sa réversion compte aux ressources de l'autre régime de base. Avant 2004,
deux versions lues, leurs paramètres écrits, `portee: false`.

**Ce que la correction déplace.** Aucun témoin de simulation, aucune page. Le témoin
des servis : le dentiste et l'agent général du formulaire ont désormais une réversion
de base, 5 169,13 € et 5 680,57 € par an au cas « seule ». Le cliquet des rédactions
sans statut baisse à 9 152.

**Ce que la correction laisse, déclaré dans la fiche.**

- Les versions d'avant 2004 ne sont pas servies : restent la limite forfaitaire de
  70 % du maximum (73 % au régime général) et l'absence de condition de ressources.
- De janvier à juin 2004, le renvoi lit la version du régime général d'avant la
  réforme, qui n'entre en vigueur qu'au 1er juillet avec le décret n° 2004-857.

**La classe.** Restent non servies, dans l'ordre de la file du coordinateur : les
complémentaires des libéraux (CARMF, CARPIMKO, CAVEC, CPRN, CAVOM, CAVP, CIPAV,
CARPV), leurs ASV et PCV, la CNBF, la RATP, la Banque de France, l'Opéra, la CRPN,
les mines, l'ENIM, l'Ircec, la Cavimac et les exploitants agricoles.

**La relecture, sur Opus** (Fable indisponible jusqu'au 25 novembre, choix validé
par le propriétaire). Elle a trouvé un effet de bord : avant 2004, la ligne non
portée de la base comptait parmi les réversions de base qui divisent la limite
forfaitaire de cumul du régime général (D. 355-1), 3 760 € au lieu de 3 662,01 € au
cas sondé ; corrigé, sous un test. Le plafond se teste désormais sur la valeur
publiée (5 001,60 € et 1,60 €), l'âge de 51 ans d'un décès de 2008 sous un test ; la
disposition transitoire de la loi de 2003 (article 96, III) est citée ; un renvoi à
une fiche absente s'arrête par une erreur qui le dit.

**Vérifié** : `test_reversion.py`, `test_carte.py`, `test_textes.py`,
`test_justesse.py`, `test_pont.py`, `test_donnees.py`, `test_sections_liberales.py`,
les confrontations légères, `python -m pytest -m rapide`.
