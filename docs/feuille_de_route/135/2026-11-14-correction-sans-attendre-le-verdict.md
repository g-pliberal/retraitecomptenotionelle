# Une correction rend compte sans attendre le verdict de GitHub

**Le 14 novembre 2026, la demande.** Le propriétaire : « J'ai l'impression
que c'est beaucoup long qu'avant pour travailler et que je consomme encore
beaucoup de tokens. Comment peut-on résoudre ça ? » Trente corrections de
l'action 130 passent depuis la veille, une session chacune, l'une après
l'autre, qu'une session d'aiguillage ouvre.

**La méthode.** Celle de la note du 3 novembre : les événements `result` que
rend `list_events`, lus sur la correction 10 (la majoration de la CAVAMAC) et
sur la session d'aiguillage. `process_turn_states` y partage le temps d'un
tour entre le modèle (`main_stream`, `first_event_wait`) et les outils
(`tool`) ; `process_wall_ms_between_turns` donne l'attente entre deux tours.
Les durées des autres corrections viennent de `list_sessions`, de l'ouverture
au dernier événement. Les tarifs sont ceux de la note du 9 novembre, non
relus ce jour ; ils redonnent les deux coûts affichés au centime.

**Le temps.** La correction 10 a duré 52 min 47, de 7 h 22 à 8 h 14 UTC, en
59 appels.

- *Le modèle* : 5 min 00, dont 4 min 30 à écrire.
- *Les outils* : 13 min 06, en 49 appels. La suite rapide en prend deux à
  chaque passage : 5 032 tests en 119,76 s, mesurés ce jour dans le conteneur
  de la session.
- *L'attente du verdict de la suite complète* : 34 min 15, entre l'envoi sur
  `main` et le tour de douze secondes qui rend compte.

Les onze corrections finies ont duré de 51 à 107 minutes, 69 en moyenne ;
seule la dixième a été décomposée.

**Les jetons.** La correction 10 coûte 4,86 $ : 1,30 $ de lecture du cache
(6 522 116 jetons), 2,22 $ d'écriture (138 628), 1,33 $ de sortie (33 372,
dont 7 498 de réflexion). Son contexte va de 40 338 à 164 844 jetons. Les
étapes du 11 novembre en coûtaient de 5,66 à 19,38.

La session d'aiguillage, après onze corrections, à 9 h 27 UTC : 14,59 $, dont
12,26 $ d'écriture du cache, 84 %. Elle a écrit 766 424 jetons pour un
contexte de 148 994 au dernier appel, cinq fois celui-ci. Son dernier réveil,
quatre appels pour relayer un compte rendu et ouvrir la ligne suivante, coûte
2,14 $, dont 1,96 $ à récrire 122 232 jetons. La cause est celle que dit le
skill `orchestration` : une heure sans appel vide le cache, et une correction
dure plus d'une heure.

L'attente du verdict fait donc les deux tiers de la durée d'une correction,
et c'est elle qui pousse chaque réveil de l'aiguillage au-delà de l'heure.

**La décision du propriétaire, le même jour**, les deux mesures lues :
« Applique le point 1 ».

- *La session qui corrige n'attend plus le verdict de GitHub.* Sa suite
  rapide et les tests de sa zone verts, elle envoie, rend compte et s'arrête,
  ce que `CLAUDE.md` disait déjà (« Une session, une étape ») ; la consigne
  que l'aiguillage donnait à chaque correction y ajoutait l'attente.
- *Le verdict se lit à l'ouverture de la session suivante*, par le hook
  `SessionStart`, et avant son envoi : rouge, elle répare avant tout. Les
  courses de `tests.yml` se suivent une à une, celle qui attend étant
  remplacée par la plus récente : un verdict tombe toujours.
- *La dernière ligne de la file* attend le verdict de son envoi : aucune
  session ne s'ouvre après elle pour le lire.
- *Écrit* : un paragraphe daté aux règles de la file
  (`130/2026-11-13-corrections-decidees.md`), et un message à la session
  d'aiguillage, pour les lignes qu'elle ouvre désormais. La ligne 12, en
  cours, finit sous l'ancienne consigne.

**Ce que la décision coûte.** La course de GitHub dure de 17 à 30 minutes :
un rouge se voit une ou deux corrections plus tard, et la session qui le
trouve a deux ou trois commits à trier au lieu d'un.

**Deux corrections à la fois, une file par caisse : écarté.** Le propriétaire,
la décision prise : « Je veux accélérer ». Les dix-huit lignes restantes
tiennent à cinq caisses, et deux files menées de front auraient divisé la
durée. Relevé, par `git log --name-only`, sur les douze corrections finies :
les caisses ne sont pas séparées dans le code.

- *Sept sur douze ajoutent un champ au catalogue commun des régimes* (les
  lignes 1, 2, 5, 6, 7, 11 et 12) : `data/reference/regimes/_schema.yaml`,
  sous `champs_periode` ; `src/retraite_notionnelle/donnees/regimes.py`, dans
  `PeriodeRegime` et `CatalogueRegimes` ; `scripts/construire_donnees.py`. Au
  même endroit : la ligne 2, la CAVOM, et la ligne 11, la CAVP, insèrent
  toutes deux après la ligne 804 de `regimes.py`.
- *Neuf sur douze touchent un fichier du droit commun aux caisses*, dans les
  deux moteurs : `acquerir`, `ouvrir`, `departs`, `liquider`, `reversion`,
  `compte`.
- *Sept sur douze écrivent dans `tests/test_sections_sante.py`*, qui tient les
  médecins, les dentistes, les pharmaciens et la CARPIMKO.
- *Onze sur douze refont `moteur/donnees.json`*, que `pousser.sh` règle seul.

Deux sessions de front se heurteraient donc au rebasage plus d'une fois sur
deux, sur une source, ce que `pousser.sh` refuse ; et nul ne sait, avant de
relire le texte, si une ligne demande un champ de plus. La file reste en
série.

**La décision du propriétaire, à 12 h 20 UTC**, ce relevé lu : « C'est
beaucoup trop lent. Il faut enchaîner », puis, entre la série, une session par
caisse et deux files de front, cette dernière, son prix dit : à peu près un
envoi sur deux tombe sur un conflit que la session résout à la main, et un
rouge est plus dur à attribuer. La règle « une seule session à la fois sur le
modèle » est donc levée pour cette file seulement, et la conclusion du
paragraphe précédent ne tient plus.

- *La file A* : les lignes 13 à 20. *La file B* : les lignes 21 à 30. La
  correction 13, partie à 11 h 51 UTC sous la consigne sans attente, continue ;
  la ligne 21 s'ouvre sans l'attendre.
- *Un conflit sur une source* : la session rebase à la main, garde les deux
  ajouts, refait ce que les scripts fabriquent, relance ses tests et renvoie.
- *Le bloc « Reprise » de l'action 130* ne se récrit plus à chaque ligne, ce
  que `documentation.md` demande quand des étapes se mènent de front.
- *Écrit* : un second paragraphe daté aux règles de la file, et un second
  message à la session d'aiguillage.

**Ce qui reste.**

- Le temps des outils dans une session de correction, 13 min 06 sur 18 min 11
  pour la dixième, n'est pas décomposé : ce que ses 49 appels ont lancé, et
  combien de fois la suite rapide. C'est le levier qui reste pour aller plus
  vite.

- Relever, sur les deux files, combien d'envois ont buté sur un conflit et ce
  que chacun a coûté, et si un rouge s'est laissé attribuer.
- Relever, sur les lignes 13 et suivantes, la durée d'une correction et
  l'écriture du cache à chaque réveil de l'aiguillage. Attendu, non mesuré :
  une demi-heure de moins par correction, et un réveil à quelques dizaines de
  centimes tant que les comptes rendus se suivent à moins d'une heure.
- Au propriétaire : raccourcir la course de GitHub, par exemple en la
  partageant entre plusieurs travaux parallèles. `tests.yml` est une garde ;
  la décision, proposée ce jour, n'est pas prise.
