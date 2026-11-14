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

**Ce qui reste.**

- Relever, sur les lignes 13 et suivantes, la durée d'une correction et
  l'écriture du cache à chaque réveil de l'aiguillage. Attendu, non mesuré :
  une demi-heure de moins par correction, et un réveil à quelques dizaines de
  centimes tant que les comptes rendus se suivent à moins d'une heure.
- Au propriétaire : raccourcir la course de GitHub, par exemple en la
  partageant entre plusieurs travaux parallèles. `tests.yml` est une garde ;
  la décision, proposée ce jour, n'est pas prise.
