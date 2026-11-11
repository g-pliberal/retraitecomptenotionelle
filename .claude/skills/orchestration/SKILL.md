---
name: orchestration
description: La relève de la session d'orchestration, celle qui lance et suit d'autres sessions Claude Code sur ce dépôt — passer la main à chaque vague.
when_to_use: Avant de lancer une autre session (`create_session`), en suivant celles qui tournent, et dès qu'une vague se clôt.
---

# La session d'orchestration passe la main à chaque vague

Celle qui lance et suit les autres sessions est la seule qui dure : leurs
comptes rendus, ses consignes et sa réflexion s'y accumulent, que chacun de
ses appels relit, et une heure sans appel lui fait récrire tout son cache. Une
vague close — chaque session lancée a rendu compte, la suite est verte —, elle
ne lance pas la suivante : elle ouvre la session qui lui succède
(`create_session`), avec son état pour consigne — les files, ce qui est fait,
ce qui attend, les questions posées au propriétaire et ses réponses —, lui
confie la vague, donne son nom au propriétaire et s'arrête.
