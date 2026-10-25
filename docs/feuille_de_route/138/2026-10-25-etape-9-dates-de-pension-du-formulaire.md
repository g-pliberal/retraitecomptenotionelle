# Étape 9, suite de la huitième partie : les dates de pension du formulaire

**La demande.** Seizième vague, le 25 octobre 2026 : une session par tâche,
que le propriétaire ne suit pas pas à pas, celle-ci seule du lot sur les
pages. Le point « aux pages, les dates de pension du formulaire » du bloc
« Reprise » de la huitième partie, que la note « date d'entrée dans la
saisie » (`2026-10-25-etape-9-date-d-entree-dans-la-saisie.md`, « Trouvé en
chemin ») laissait à une session des pages : le formulaire propose la date de
chaque pension par `regimesDeBaseSaisis` (`pages.js`), qui datait chaque
métier de son propre début, et lisait les régimes du micro-entrepreneur de
la Cipav sous son statut, non sous celui du libéral.

**Ce que disent les textes.** Rien de neuf à lire. Le micro-entrepreneur des
professions que la Cipav garde relève de la CNAVPL et de la Cipav (D. 613-4,
b ; fiche `micro_social_abattement`). Le libéral non réglementé affilié avant
le 1er janvier 2019 à la CNAVPL et à la Cipav « reste affilié » à ces régimes
(loi n° 2017-1836, art. 15), la règle que la note du 25 octobre cite, et
qu'`affiliations.yaml` porte par `entres_avant`.

**Ce qui est fait.**

- *Le test* (`tests/test_web_saisie.py`,
  `test_le_formulaire_date_les_pensions_que_la_carriere_porte`, deux cas),
  vu rouge pour ces deux raisons. Le micro-entrepreneur de la Cipav de 2009
  à 2014, puis salarié, date la CNAVPL, puis le régime général : le
  formulaire proposait le RSI et le régime général. Le libéral non
  réglementé installé en 2010, dont un second métier dit en 2020 que le
  revenu change, n'a que la CNAVPL, dont le départ dit la date : le
  formulaire datait le second métier de 2020, et proposait aussi le régime
  général. La naissance se déclare entière, le 15 mars 1985 ; ni son jour ni
  le sexe ne changent les régimes.
- *La correction*, deux lignes : chaque métier se lit sous son affiliation
  (`Saisie.affiliationDe`) et à l'entrée dans celle-ci
  (`Saisie.dateEntree`), comme la carrière le lit (`lignesDuParcours`,
  `Carriere.dateEntree`). La branche du relevé n'a pas changé : il nomme
  l'affiliation de chaque année, sans routage.

**Ce que montrent les mesures.** Ni les témoins de simulation (909) ni ceux
des pages (82) ne bougent (`construire_temoins.py`, le 25 octobre) : la
correction ne change que les champs de date que le formulaire propose.

**Trouvé en chemin.** Sur un relevé, le formulaire date l'entrée dans une
affiliation à sa première année d'emploi ; la carrière, et
`Saisie.dateEntree` avec elle, à la première année qui la nomme, année
d'interruption comprise (`Carriere.entree`). Un relevé salarié de 2008 à
2017, puis libéral non réglementé, sans activité en 2018 et actif depuis
2019 : la carrière date l'entrée de 2018 et porte la CNAVPL ; le formulaire
la date de 2019, lit le régime général et le RCI, et ne propose aucune date.
Sans activité en 2018, l'assuré ne s'installe qu'en 2019, et la clause du
grand-père ne devrait pas jouer : c'est le formulaire qui lit la loi, non la
carrière, dont le refus d'un statut fermé (`verifierStatutsReleve`) lit la
même date. Au modèle, avec son test ; le formulaire ne bouge pas.

**Ce qui reste**, une session par point : le plafond de 2027 ; la limite
5 ante ter (2), en fin d'étape ; au modèle, la date d'entrée d'un relevé
qu'ouvre une année d'interruption (« Trouvé en chemin ») ; au propriétaire,
la CAMIEG, l'écrêtement du minimum de la SNCF, l'ASPA de l'article 23, et
les textes au fac-similé de la note « seuil de février 1991 ».
