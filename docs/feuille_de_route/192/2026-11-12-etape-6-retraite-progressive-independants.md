# Étape 6 : la retraite progressive au régime complémentaire des indépendants, en 2027

**Reprise, au 12 novembre 2026.** Rien n'est commencé. Au 1er janvier 2027, le
règlement du régime complémentaire des indépendants plafonne l'abattement de
la fraction de pension servie en retraite progressive : il ne peut dépasser le
taux de la deuxième ligne du tableau de son annexe 2. Le modèle sert cette
fraction sous l'abattement entier, jusqu'à 22 %. Un autre article du même
règlement, à la même date, refuse le complément de points à qui demande cette
fraction : aucune fiche ne le cite, et il n'a pas été confronté au modèle. À
faire, le test d'abord : lire les articles 12 et 28 et l'annexe 2, que l'index
rend à plat, établir quelle ligne est la deuxième, puis écrire la règle et la
fiche.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot des autres régimes l'a lu
(`184/2026-11-12-etape-6-autres-regimes.md`, « Ce qui change une règle ») :
règlement du régime complémentaire des indépendants (arrêté du 9 février
2012), article 12 (LEGIARTI000054908824), date d'effet 1er janvier 2027
(arrêtés du 6 octobre 2025 et du 21 septembre 2026) ; article 28
(LEGIARTI000054908892), même date. Le lot du code de la sécurité sociale a
relevé dans l'article 12 l'âge du taux plein « au sens du 1° ou, du 1° bis ou
du 6° de l'article L. 351-8 ». Fiche : `abattement_rci`.

**Ce qu'il y a à faire.**

1. Lire les articles 12 et 28 et l'annexe 2. L'annexe se lit dans l'arrêté au
   Journal officiel, par l'index du JORF, si LEGI la rend à plat ; si elle
   reste illisible, le dire au propriétaire plutôt que de deviner la ligne.

2. Le test, vu rouge : une fraction de retraite progressive en 2027, sous le
   plafond du texte.

3. La règle, datée du 1er janvier 2027, dans le modèle et son portage ; le
   complément de points de l'article 28, s'il touche ce que le modèle sert.

4. La fiche `abattement_rci`, et celle qui porte le complément.

**Fini quand** la fraction servie en 2027 est celle du règlement, ou que la
ligne de l'annexe est une question posée au propriétaire.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.
