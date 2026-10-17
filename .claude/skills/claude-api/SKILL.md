---
name: claude-api
description: Les modèles Claude (Opus, Sonnet, Haiku, Fable) et leurs tarifs, pour ce dépôt, qui n'appelle pas l'API Claude — où lire le tarif du jour et la documentation de Claude Code, au lieu d'une table figée. Remplace le skill du même nom que Claude Code fournit.
when_to_use: Avant toute réponse sur le choix d'un modèle Claude pour une session ou un agent, sur son prix, l'effort, le cache ou l'API Claude, et dès qu'une demande nomme Claude, Anthropic, Opus, Sonnet, Haiku ou Fable.
---

# Les modèles Claude et leurs tarifs, pour ce dépôt

Ce skill remplace celui que Claude Code fournit sous le même nom. Le 17 octobre
2026, la table des tarifs de ce dernier avait un jour de retard : elle donnait
encore 0,20 $ pour la lecture du cache de Sonnet 5.5, divisée par deux le
7 octobre. Son texte, environ 49 000 jetons, entrait de plus dans le contexte
de la session pour une seule ligne. Le dépôt n'appelle pas l'API Claude : la
question porte presque toujours sur Claude Code lui-même, quel modèle pour une
session ou un agent, et ce qu'il coûte.

- **Un tarif ne se donne jamais de mémoire, ni d'une table figée** : il se lit
  le jour même sur la page des tarifs de l'API, dont cette commande ne garde
  que la table principale, en dollars par million de jetons (entrée, écriture
  du cache à cinq minutes puis à une heure, lecture du cache, sortie) :

  ```bash
  curl -sS -L https://platform.claude.com/docs/en/about-claude/pricing.md \
    | awk -F'|' '(/^\| Model/ || /^\| Claude/) && NF==8'
  ```

  Un `grep` des seuls modèles voulus la raccourcit.
- **Ce que Claude Code permet** se lit dans sa documentation, en Markdown
  brut : `https://code.claude.com/docs/en/<page>.md`. Les pages utiles :
  `model-config` (le modèle de la session, l'effort, `opusplan`), `sub-agents`
  (le modèle d'un agent, ceux que Claude Code fournit), `costs`,
  `prompt-caching` (chaque modèle a son cache) et `skills`. Un `curl` suivi
  d'un `grep` y prend la phrase utile ; la page entière ne se lit pas.
- **Les choix du dépôt** : la lecture confiée à Haiku, par l'éclaireur et
  Explore (`.claude/agents/`, et la règle de `CLAUDE.md`) ; trois agents
  d'impeccable sur Sonnet, et les agents généralistes aussi
  (`CLAUDE_CODE_SUBAGENT_MODEL`, dans `.claude/settings.json`, qui tient
  encore l'effort `max` et la chaîne de secours, `fallbackModel`). Pas de
  Fable : Opus 5.5 le devance sur toutes les mesures que publie son annonce
  (22 septembre 2026), pour moins cher. Le détail est
  dans la note `docs/feuille_de_route/135/2026-10-17-trois-modeles.md` ; ce
  que les sessions consomment, modèle par modèle :
  `python scripts/consommation.py`.
- **Pour écrire du code qui appelle l'API**, ce skill ne suffit pas : ôter son
  dossier rend celui de Claude Code.
