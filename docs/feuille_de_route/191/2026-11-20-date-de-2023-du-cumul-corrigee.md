# La date de 2023 du cumul, corrigée au texte

Pour une première pension de base d'avant le 1er janvier 2015, le dépôt
éteignait dès le 1er janvier 2023 les droits de l'activité reprise. La loi ne
le fait qu'au 1er septembre 2023. L'étape 2 du cumul avait relevé la question
(`2026-11-19-etape-2-du-cumul.md`), une session qui n'avait vu ni la fiche ni
cette lecture l'a tranchée le même jour
(`2026-11-19-relecture-de-la-date-de-2023-du-cumul.md`). La correction,
préparée le 19 novembre 2026 à sa suite, déplace des résultats : elle a
attendu l'accord du propriétaire. Il l'a donné le 20 novembre (« Je veux
mettre en place toutes les recommandations y compris "on corrige tout ce qui
est faux" »), et elle est publiée ce jour-là.

## Le texte

- Loi n° 2023-270 du 14 avril 2023, article 26, XII (`JORFARTI000047445113`) :
  « Le présent article entre en vigueur le 1er septembre 2023, sous réserve
  des dispositions suivantes ». Son 3° ne remonte au 1er janvier 2023 que
  pour « les droits en vue d'une nouvelle pension de vieillesse constitués à
  partir du 1er janvier 2023 en application du 2° de l'article L. 161-22-1 et
  de l'article L. 161-22-1-1 ».
- Loi n° 2014-40 du 20 janvier 2014, article 19, VIII
  (`JORFARTI000028493657`) : L. 161-22-1 A, seul à éteindre les droits jusqu'au
  31 août 2023, est « applicable aux assurés dont la première pension prend
  effet à compter du 1er janvier 2015 ».

Les deux lectures, faites à part, concordent. Aucun exemple officiel n'a été
trouvé : la version le dit, avec ce qui a été cherché.

## Ce qui change

- **La fiche** `droits_apres_la_premiere_pension` prend une cinquième
  version, `transition_2023` : première pension d'avant 2015, droit acquis du
  1er janvier au 31 août 2023, exception de `loi_2023`. L'activité y ouvre
  encore des droits ordinaires dans le régime qui n'a rien liquidé
  (`droits_nouveaux: selon_le_regime`). Les bornes des quatre autres versions
  ne bougent pas.
- **Le cumul intégral de ces huit mois**, dans le régime qui sert déjà la
  pension, garde ce que le dépôt faisait : les droits à une nouvelle pension,
  que le 3° du XII ouvre dès janvier 2023 sans borne de première pension
  (`exceptions: [cumul_integral]`). La relecture ne posait que le cas du
  régime qui n'a rien liquidé ; reprendre `sans_regle_generale` jusqu'en août
  aurait ôté ces droits-là, à tort.
- **Le moteur** (`motif`, dans `moteur/js/droit/seconde.js`) lit ces deux
  paramètres ensemble : le régime qui n'a rien liquidé ouvre ses droits ;
  sinon, seul un cumul que la version excepte ouvre une nouvelle pension.
- **L'année que la règle coupe** ne compte que ses mois qui ouvrent des
  droits (`lignesQuiOuvrent`) : de 2023, huit douzièmes du revenu et deux
  trimestres. Jusque-là la règle changeait au 1er janvier, et l'année entière
  suivait.
- **La page** dit la reprise chez le dernier employeur et le régime qui sert
  déjà la pension par leur motif seul, sans quoi ces huit mois retombaient
  sur la phrase des droits ouverts.

## Ce qui bouge

- Aucun des 936 témoins de simulation, aucun des 86 rendus de page : aucun ne
  portait une première pension d'avant 2015 en activité en 2023.
- Un témoin de plus, `cumul_premiere_pension_de_2014_en_2023` : la
  fonctionnaire née en 1953, partie en août 2014, salariée d'août 2022 à
  juillet 2024. Avant la correction, ses droits ordinaires s'arrêtaient à
  décembre 2022 : 106,04 € par an au régime général et 79,89 € à
  l'Agirc-Arrco, tous deux sous leurs seuils et versés en capital. Après, ils
  courent jusqu'en août 2023 : 344,46 € et 204,14 € par an, servis en rente.
  Ses nouvelles pensions du cumul intégral ne partent plus que de septembre
  2023 : 1 000,79 € au lieu de 1 007,68 € au régime général, 168,80 € au lieu
  de 293,06 € à l'Agirc-Arrco. En tout, 1 718 € par an au lieu de 1 487 €.

## Ce qui est vérifié

- `tests/js/droits-apres-la-premiere-pension.test.js` : trois essais de
  plus, vus rouges puis verts, sur les valeurs des deux lois et un calcul
  posé à la main ; deux essais d'avant, qui disaient la date fausse, corrigés.
- `tests/test_emploi_retraite.py`, un essai de bout en bout ;
  `tests/test_web.py`, un essai de la page, vu rouge.
- Le 20 novembre, sur le `main` du jour : `python -m pytest -m rapide`
  (5 711 passés), les tests de la zone, `tests/test_web.py`,
  `python -m pytest -m site`, les 288 essais de `tests/js/`. Le témoin des
  sorties prend les entrées du cas ajouté (`FIGER_SORTIES=1`, sur
  `tests/test_liquidation.py` et `tests/test_droit.py`). La suite complète
  est à GitHub.

## Ce qui reste, et ce qui est une convention

- **Les trimestres de l'année coupée** suivent la convention du moteur pour
  toute année incomplète, les trimestres civils entiers de ses mois : deux
  pour huit mois. R. 351-9 les compte au salaire, quatre au plus par an : la
  salariée de l'exemple en validerait quatre. L'écart vaut pour toute année
  d'activité incomplète, et n'est pas de cette correction.
- **Après août 2023**, la fiche suit la lettre de L. 161-22-1, qui ne
  reprend pas la borne de 2015 ; l'exposé de la Cnav la garde sans date de
  fin. La réserve de la relecture est inscrite aux sources de la fiche
  (`a_relire`).

## Ce que la correction a coûté

Deux heures environ le 19 novembre pour la préparer, dans la session de
l'étape 2, et une demi-heure le 20 pour la publier ; un commit ; neuf
fichiers écrits à la main, le paquet et les témoins refaits.
