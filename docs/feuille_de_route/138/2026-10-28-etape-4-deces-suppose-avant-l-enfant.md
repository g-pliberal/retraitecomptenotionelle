# Étape 4, suite de la huitième partie : le décès supposé avant l'enfant né après lui, une question au propriétaire

**Le 28 octobre 2026, la demande.** La vague du jour, une session par tâche
qui se mène sans le propriétaire : le point « au modèle » du bloc de l'étape,
« le décès supposé avant l'enfant né après lui », détaillé au point 2 du « Ce
qui reste » de `2026-10-28-etape-4-enfant-ne-apres-le-depart.md`. Sans décès
déclaré, la réversion d'essai suppose le décès au départ, ou au 1er janvier
de l'année courante (présomption `deces_apres_le_depart`), et l'enfant né
après lui y compte comme un enfant posthume, même plus de trois cents jours
après ; la présomption pourrait ne pas précéder la dernière naissance dite de
plus de trois cents jours. Consigne de la vague : si le choix de la
présomption relève du propriétaire plutôt que du texte, consigner la question
et s'arrêter. C'est le cas : rien n'est changé, ni aux deux moteurs, ni à la
présomption.

**Le défaut, vérifié.** Le père né le 15 janvier 1975, parti à soixante-quatre
ans au 1er février 2039, marié à une femme née en 1980, déclare un fils né en
juin 2041. La réversion d'essai le suppose mort le 1er février 2039 et compte
le fils, né vingt-huit mois plus tard, comme un enfant posthume : la majoration
forfaitaire pour enfant à charge du régime général, 1 363,08 € par an, du
1er juillet 2041 au 1er juillet 2059. Or la loi présume l'enfant « conçu
pendant la période qui s'étend du trois centième au cent quatre-vingtième
jour, inclusivement, avant la date de la naissance » (code civil, article 311,
lu le même jour par la session de la saisie) : né plus de trois cents jours
après le décès, il serait conçu après lui. La saisie refuse cette naissance
quand le décès est déclaré ; le modèle, qui reçoit le décès d'une
présomption, la compte. Le cas ne vient que d'une naissance après le départ,
et plus de trois cents jours après le 1er janvier de l'année courante : une
naissance à venir, ou, en fin d'année, toute récente.

**Pourquoi le choix revient au propriétaire.** L'hypothèse de décès est sa
décision : « sur la décision du propriétaire : l'hypothèse de décès »
(action 130, quatrième étape du domaine de la réversion, le 28 septembre
2026), que `data/reference/vocabulaire/valeurs.yaml` déclare (« décision du
propriétaire, le 28 septembre 2026 »). Il l'a prise quand la saisie bornait
les naissances au départ : l'enfant né après lui n'existait pas encore pour
le modèle. L'article 311 dit que le résultat d'aujourd'hui est faux ; il ne
dit pas lequel des correctifs est juste, et chacun change ce que la page
montre.

1. *Déplacer le décès supposé*, jamais plus de trois cents jours avant la
   dernière naissance dite — la proposition de la note. L'enfant compte,
   comme l'utilisateur l'a déclaré ; les euros restent ceux de la page
   (`_pensions_au_deces` borne l'année du décès à venir à l'année courante,
   jamais avant celle du départ). Mais la carte de la réversion dit « Si vous
   décédiez juste après votre départ, en février 2039 » (`reversionDuConjoint`,
   `moteur/js/pages.js`), ou « cette année » pour qui est déjà parti : la
   phrase deviendrait fausse, et c'est aux pages de la récrire. Pour une mère,
   un décès trois cents jours avant la naissance est impossible ; la saisie du
   décès déclaré ne le distingue pas davantage.
2. *Garder le décès au départ, sans l'enfant conçu après lui* : la réversion
   d'essai ne compte pas l'enfant né plus de trois cents jours après le décès
   supposé — l'article 311 appliqué à l'hypothèse, qui ne change pas. La
   majoration de cet enfant disparaît, et les conditions de mariage que
   l'« enfant issu du mariage » lève (L. 39 des fonctionnaires, les IEG, la
   SNCF, l'Ircantec), qui comptent tout enfant déclaré, ne le comptent plus ;
   la carte devrait dire pourquoi l'enfant déclaré n'y compte pas.
3. *Supposer le décès juste après la dernière naissance* : l'enfant compte dès
   la date d'effet, sans posthume, pour un père comme pour une mère ;
   l'hypothèse s'éloigne davantage du départ.

Recommandation : le 1, qui compte l'enfant que l'utilisateur déclare, comme la
réversion d'un décès déclaré, au plus près de l'hypothèse choisie, la plus
tôt que la loi permette ; il coûte la phrase de la carte. Le 2 est le seul
qui ne touche ni la présomption ni la phrase, au prix de l'enfant déclaré.

**Les mesures.** Sur le cas du père de 1975, par le simulateur Python
(`Saisies.simuler`, celui des tests) : aujourd'hui, la réversion au
1er mars 2039, 20 650,99 € par an, et la majoration du fils de juillet 2041
à juillet 2059 ; le décès déclaré en août 2040, ce que donnerait le 1, la
réversion au 1er septembre 2040, les mêmes montants, la même majoration ; le
fils ôté, ce que donnerait le 2, la réversion au 1er mars 2039, les mêmes
montants, sans majoration. La pension du défunt, 29 194,48 € par an au régime
général, ne bouge dans aucun des trois.

**Ce qui reste.**

1. *Au propriétaire* : choisir entre le 1, le 2 et le 3.
2. *Puis, au modèle* : la règle choisie dans `_reverser_a_l_essai`
   (`echeancier.py`), puis son jumeau (`echeancier.js`) ; pour le 2, les
   enfants que la réversion d'essai lit ; la présomption récrite dans
   `valeurs.yaml`, avec le cas de `test_reversion.py`
   (`test_sans_deces_declare_le_deces_est_suppose_au_depart`) vu rouge, et ce
   qui la répète : les neuf fiches de réversion qui la citent, l'architecture
   (§ 5.6) et `docs/limites/ecarts-au-droit-positif.md`.
3. *Au site, ensuite* : la phrase de la carte (`reversionDuConjoint`), la date
   du décès supposé pour le 1 et le 3, l'enfant qui ne compte pas pour le 2.
