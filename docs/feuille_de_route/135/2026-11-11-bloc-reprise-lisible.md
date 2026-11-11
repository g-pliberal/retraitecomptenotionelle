# Le bloc « Reprise » lisible : 150 mots, pour un lecteur sans contexte

**Le 11 novembre 2026, à la demande du propriétaire**, troisième des quatre
chantiers de la note `2026-11-11-plateforme-claude.md`. Un bloc « Reprise » se
limite désormais en mots, 150 au plus, et non plus en lignes. Il s'écrit en
lignes de largeur ordinaire, pour une session qui n'a rien lu d'autre.
`CLAUDE.md` porte la règle, `scripts/reprise.py` la mesure, et
`tests/test_prose.py` la tient : `pousser.sh`, qui joue ce test avant
d'envoyer, refuse un bloc qui l'enfreint.

**Le défaut.** La règle d'avant voulait un bloc « de dix lignes au plus ». Les
70 blocs du jour la tenaient tous, et elle ne bornait rien, puisqu'aucune
ligne n'avait de largeur. Le bloc de l'action 130 tenait en huit lignes, dont
une de 1 578 caractères. Une session neuve, qui ne lit que ce bloc, y trouvait
vingt et un codes d'étape qu'aucune phrase n'expliquait.

**La mesure**, sur les 70 blocs : 27 ouvrent une action, 43 une note d'étape.
Un mot est ce qu'un blanc sépare, sans la ponctuation isolée.

| | minimum | médiane | neuvième décile | maximum |
|---|---|---|---|---|
| mots | 74 | 111 | 138 | 913 |
| caractères | 505 | 702 | 868 | 5 278 |
| plus longue ligne | 74 | 78 | 95 | 1 578 |

Six blocs dépassent 150 mots, et cinq d'entre eux ont aussi une ligne de plus
de 100 caractères ; les 64 autres tiennent les deux bornes. Sept blocs portent
des codes d'étape ou de relecture forgés par les sessions (« R-E14 »,
« B7-bis », « K-ter », « H13 »), et un huitième un code qu'il n'explique pas.
Trois blocs portent des empreintes de commit : quatorze dans celui de
l'action 130, trois dans celui de l'action 162, une dans une note de
l'action 186. Les blocs portent 77 sigles en capitales distincts, des caisses
et des organismes pour la plupart : c'est le vocabulaire du domaine, que la
règle ne vise pas. Le style est télégraphique : 2,8 points-virgules pour cent
mots.

**La source** est le guide de rédaction de Fable 5.2, sur la plateforme
Claude (`build-with-claude/prompt-engineering/prompting-claude-fable-5-2`).
Sur les règles de style : « Claude Fable 5.2 follows them closely, so a hard
limit such as "one instruction per sentence, in 20 words or fewer" can make
its prose choppy. » Pour un passage de relais, il donne un texte, dont :
« Write for an intelligent but low-context reader. […] Put the key points in
the first few sentences. […] Do not use a term or abbreviation that you made
up during the work. Say what the thing is in a way any reader would
understand. » Il ajoute qu'une consigne de longueur peut s'y joindre.

**La règle**, proposée au propriétaire et accordée le jour même, en trois
parties.

- *150 mots au plus.* C'est ce que dix lignes ordinaires contiennent au plus
  aujourd'hui : 64 blocs sur 70 tiennent déjà la limite. Elle porte sur le
  bloc entier, et non sur la phrase, que la source déconseille de borner.
- *Des lignes de largeur ordinaire.* Le bloc se coupe comme le reste de la
  prose. Le test refuse une ligne de plus de 100 caractères : la marge laisse
  passer un chemin de fichier un peu long.
- *La consigne de lisibilité*, adaptée du texte de la source : écrire pour un
  lecteur intelligent mais sans contexte, l'essentiel d'abord, en phrases
  entières et en mots ordinaires, sans terme ni sigle forgé pendant le
  travail. Ce qui ne tient pas va dans la note, et non dans une phrase plus
  dense : c'est ce qui empêche la limite de serrer la prose.

**Ce que le test tient.** `reprise.fautes_d_un_bloc` dit ce qu'un bloc
enfreint : sa date, ses mots, sa plus longue ligne.
`test_un_bloc_reprise_se_mesure_en_mots_et_en_lignes_ordinaires` la tient sur
des exemples, et `test_chaque_action_en_cours_s_ouvre_sur_son_bloc_reprise`
l'applique aux blocs du dépôt. Un troisième test vérifie que `CLAUDE.md` et la
carte du dépôt disent la limite que le script porte. Les sigles restent à la
consigne : un motif qui refuserait « R-E14 » refuserait aussi « T2 », la
tranche 2 d'une cotisation.

**Les blocs d'avant la règle** restent tenus par leurs dix lignes : le test
lit la date qui ouvre le bloc, et n'applique la règle neuve qu'à partir du
11 novembre 2026. La session qui avance une action récrit son bloc daté du
jour, comme `CLAUDE.md` le voulait déjà ; le bloc tombe alors sous la règle,
sans liste à entretenir. Six blocs attendent ainsi : ceux des actions 130
(913 mots), 158 (183), 151 (167) et 131 (162), et ceux de deux notes de
l'action 138, l'étape 14 (301) et l'étape 4 (172). Ce que leur réécriture
ôtera du bloc ira dans la note de la session qui la fait.

**Le rouge, vu deux fois.** L'ancienne règle, portée telle quelle dans
`reprise.py`, refusait 150 mots en quinze lignes et acceptait 913 mots en
huit. Le test de la règle écrite échouait ensuite sur `CLAUDE.md`, qui disait
encore dix lignes.

**À savoir.**

- Le bloc de l'action 135, récrit selon la règle, fait 148 mots en quatorze
  lignes : l'ancien test l'aurait refusé.
- Il ne compte plus parmi ce qui reste le quatrième des cinq leviers du
  diagnostic, le parcours de présentation que la conservation gelait. La note
  du 8 octobre l'a réglé, et `zones.yaml` déclare depuis le parcours tenu par
  son test ; les blocs suivants le portaient encore par erreur.
- La règle ajoute six lignes à `CLAUDE.md`, qui en fait 265 : le chantier qui
  doit le ramener sous deux cents en tiendra compte.
