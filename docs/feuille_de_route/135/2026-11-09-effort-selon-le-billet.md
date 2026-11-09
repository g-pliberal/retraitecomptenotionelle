# L'effort selon le billet « Which Claude model should you build with? »

**Le 9 novembre 2026.** Le propriétaire demandait d'appliquer aux réglages
par défaut du dépôt les recommandations de ce billet
(`claude.dev/blog/which-claude-model-should-you-build-with/`, daté du jour,
lu par un sous-agent : la session n'en a que son relevé, citations
comprises).

- *Ce que le dépôt faisait déjà.* Le billet confie à Haiku 5.5 ou à
  Sonnet 5.5 les sous-agents qui cherchent, lisent et résument (« define your
  own subagent named `Explore` with `model: haiku` »,
  `CLAUDE_CODE_SUBAGENT_MODEL` pour ceux qui ne disent pas leur modèle), et
  réserve Fable 5.2 aux projets les plus durs. L'éclaireur et Explore sur
  Haiku, les généralistes sur Sonnet, Fable 5.2 pour une règle du scénario 1 :
  rien n'y change. De même la bascule de modèle tant que le contexte est
  court (« The prompt cache belongs to the model that wrote it »), et
  `opusplan`, que le dépôt n'emploie pas et que le billet demande de mesurer
  avant d'en faire un défaut.
- *L'écart : l'effort.* Le billet fait démarrer Opus 5.5 et Sonnet 5.5 à
  `medium`, « then `high` » pour ce qui résiste, et prévient : « Past `high`,
  one more effort level can cost as much as a bigger model, so compare both
  on your own work. » Le dépôt les tenait à `xhigh` depuis le 3 novembre,
  sans mesure faite. Pour les sous-agents de lecture, il donne « The model's
  default », `medium` pour Haiku 5.5, quand l'éclaireur et Explore
  déclaraient `high`.
- *Ce qui est fait*, au choix du propriétaire, interrogé sur les deux
  points : Opus 5.5 et Sonnet 5.5 à `high` dans `modelSettings`
  (`.claude/settings.json`), le cran haut du billet, puisque les sessions
  publient sur `main` sans relecture ; l'éclaireur et Explore à
  `effort: medium`, déclaré et non omis, pour qu'ils ne suivent pas l'effort
  de la session. `tests/test_reglages_claude.py` tient les deux, et le skill
  `claude-api` les dit.
- *Laissés tels quels* : Fable 5.2 à `high`, dans la fourchette du billet
  (« `medium`, then `high` ») ; le relecteur d'impeccable à `high`, les trois
  autres agents d'impeccable à `medium` sur Sonnet ; la chaîne de secours,
  dont le billet ne dit rien.
- *Ce qui reste au propriétaire*, à l'ouverture de chaque session, que le
  dépôt ne règle pas : selon le billet, Opus 5.5 par défaut, Sonnet 5.5 pour
  un travail bien cadré (« a bug fix or a feature built against a spec »),
  Fable 5.2 pour les refontes, les migrations et la session qui mène beaucoup
  de sous-agents ; et, avant de monter d'un cran ou d'un modèle, donner à la
  session de quoi se vérifier elle-même. La mesure de `xhigh`, qui restait à
  faire, n'a plus d'objet.
