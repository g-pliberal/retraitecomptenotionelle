# Trois modèles : Haiku pour lire, Sonnet à moitié prix, Opus pour juger

**Le 17 octobre 2026, la demande.** Le propriétaire, qui a lu les annonces de
Haiku 5.5 : « J'aimerais optimiser l'utilisation des différents modèles opus,
sonnet et haiku […] Il faut regarder la doc pour voir si on ne pourrait pas
optimiser en utilisant les 3 modèles au lieu d'un seul. » Jusque-là, toute
session tournait sur Opus 5.5, ses sous-agents aussi (`model: inherit` pour
ceux d'impeccable), et l'effort est fixé à `max` depuis le matin même
(`1214e18`).

- *Les tarifs du jour*, en dollars par million de jetons, sur la page des
  tarifs de l'API (`platform.claude.com/docs/en/about-claude/pricing`), lue
  le 17 octobre. L'écriture du cache coûte 1,25 fois l'entrée pour cinq
  minutes, deux fois pour une heure, la durée que tient une session.

  | modèle | entrée | lecture du cache | sortie |
  |---|---|---|---|
  | Opus 5.5 | 4 | 0,20 | 20 |
  | Sonnet 5.5 | 2 | 0,10 | 10 |
  | Haiku 5.5, contexte de 100 000 jetons au plus | 0,10 | 0,01 | 0,50 |
  | Haiku 5.5, au-delà | 0,50 | 0,05 | 2,50 |

  La lecture du cache de Sonnet coûtait 0,20 $ jusqu'au 7 octobre ; l'annonce
  de Haiku 5.5 l'a divisée par deux (« Cache reads now cost 50% less: $0.10
  per million tokens rather than $0.20 »). Le skill `claude-api` de Claude
  Code 2.1.302, figé au 6 octobre, donne encore l'ancien tarif : une première
  version de cette note, publiée le même jour sur lui, en concluait à tort
  que Sonnet ne gagnait qu'un sixième à un tiers, la lecture du cache, qui
  fait l'essentiel de la facture, lui coûtant alors autant qu'à Opus.
- *Sonnet coûte moitié moins qu'Opus*, sur chaque ligne de la facture : la
  même session, quel que soit son profil, coûte la moitié. Cette session-ci,
  à 43 appels, coûtait 4,62 $ au tarif d'Opus ; elle en aurait coûté 2,31 au
  tarif de Sonnet, 0,78 à celui de Haiku. La documentation de Claude Code
  (`costs.md`) : « Sonnet handles most coding tasks well and costs less than
  Opus. Reserve Opus for complex architectural decisions or multi-step
  reasoning. »
- *Haiku coûte de quatre à quarante fois moins qu'Opus*, selon la ligne de la
  facture et la longueur du contexte, mais ne tient pas une session : sur
  Terminal-Bench 4.0, 39,2 % contre 70,6 % pour Sonnet 5.5, et l'annonce le
  dit : « Sonnet 5.5 and Opus 5.5 remain better choices for complex agentic
  coding tasks ». Sa place, selon elle : « It pairs well with Opus 5.5 and
  Sonnet 5.5 as a subagent on coding work. » La lecture, faite par un
  sous-agent sur Haiku, gagne deux fois : ses jetons sont à son tarif, et ce
  qu'il lit n'entre pas dans le contexte de la session, relu à chaque appel.
  Cette session-ci en donne la mesure à rebours : le skill `claude-api`,
  chargé pour y prendre la table des tarifs, pèse environ 50 000 jetons,
  relus à chaque appel qui a suivi — près du quart des jetons relus de la
  session.

**Ce que Claude Code permet** (Claude Code 2.1.302, session du cloud ; sa
documentation, `code.claude.com/docs/en/`, lue le 17 octobre).

- *Le modèle d'un sous-agent* : le `model` passé à l'appel de l'outil
  `Agent`, sinon celui de l'en-tête de l'agent (`haiku`, `sonnet`, `opus`,
  `fable`, un identifiant complet, ou `inherit`), sinon
  `CLAUDE_CODE_SUBAGENT_MODEL`, sinon celui de la session (`sub-agents.md`).
  Éprouvé ici : l'éclaireur, par son en-tête, et l'agent générique, forcé à
  l'appel, ont tourné sur `claude-haiku-5-5`.
- *Les agents que Claude Code fournit* : son guide de la documentation tourne
  sur Haiku ; Explore, qu'une session lance pour une recherche en éventail, et
  Plan, sur le modèle de la session, donc sur Opus. « A user or project
  subagent named `Explore` overrides the built-in and keeps its own `model`
  field » ; `CLAUDE_CODE_SUBAGENT_MODEL` seul ne change ni l'un ni l'autre.
- *Chaque modèle a son cache* (`prompt-caching.md`) : « Switching models
  recomputes the entire request even when the content is identical. » Le
  modèle se choisit donc à l'ouverture de la session, pas en chemin ;
  `opusplan`, qui fait le plan sur Opus et l'exécution sur Sonnet
  (`model-config.md`), paie une réécriture du contexte à chaque bascule, et
  le mode plan d'une session du cloud attend l'approbation du propriétaire.
- *Le cache d'une session tient une heure*, celui d'un sous-agent cinq
  minutes (`ephemeral_1h_input_tokens`, `ephemeral_5m_input_tokens` dans les
  transcriptions) : un sous-agent écrit son cache moins cher, mais chacun
  repart d'un contexte neuf, sans rien du cache de la session.
- *Ce qu'elle ne dit pas* : combien chaque modèle pèse sur les limites d'un
  abonnement. `/usage` y attribue la consommation aux sous-agents et aux
  skills (`costs.md`) : c'est lui qui en montrera l'effet à un abonné, les
  comptes de cette note étant aux tarifs de l'API.

**Ce qui est fait.**

- *L'éclaireur*, `.claude/agents/eclaireur.md` : `model: haiku`, en lecture
  seule (`Read`, `Grep`, `Glob`, `Bash`), qui rend des `fichier:ligne` et des
  citations mot pour mot, jamais un jugement ni une modification. Le hook de
  lecture (`lecture.py`) le tient comme la session. Un agent nouveau se
  charge au tour suivant : appelé dans le tour qui l'a écrit, il est inconnu
  (« Agent type 'eclaireur' not found ») ; d'où un premier essai par un agent
  générique forcé sur Haiku, son texte en consigne, puis, au tour d'après, un
  appel par son nom. L'essai portait sur ce que le dépôt disait déjà des
  modèles, de l'effort et des sous-agents : un relevé exact, cité mot pour
  mot, qui dit ses absences (« aucune règle ne fixe de modèle par tâche ») et
  ce qu'il n'a pu vérifier ; un peu plus long que demandé, et lent à l'effort
  `max` (neuf minutes, 52 outils). Coût, au tarif de la tranche de chaque
  appel : 0,27 $, quand le même trafic en aurait coûté 1,92 au tarif d'Opus ;
  et rien de ce qu'il a lu n'est entré dans le contexte de la session.
  L'appel par son nom, sur ce que le dépôt dit de `consommation.py` : le même
  soin, 25 outils, six minutes.
- *`CLAUDE.md`* : une sixième règle d'« Économiser le contexte », qui confie
  à l'éclaireur, une à la fois, toute recherche de plusieurs lectures dont la
  session ne veut que la réponse, et la liste de début d'étape, qui peut lui
  confier son relevé. Ce que la session modifie ou cite, elle le relit
  elle-même, à la fenêtre qu'il désigne.
- *`scripts/consommation.py` ignorait les sous-agents.* Claude Code 2.1.302
  marque `isSidechain` chaque entrée de leur transcription, la leur comprise ;
  le script, qui écarte ces entrées de la transcription de la session, les
  écartait aussi de la leur, et le test passait sur un sous-agent écrit sans
  ce marqueur. Le relevé du 10 octobre les a sans doute manqués : relancé sur
  le poste, le script le dira. Le test prend la forme réelle, un cas tient
  les deux transcriptions, et le rapport ventile les appels par modèle. Un
  appel garde enfin le plus grand compte de sortie de ses entrées : le
  rapport de l'essai en portait 177 jetons sur la première, près de 7 000 sur
  la dernière, seule à dire le compte entier.
- *Le skill `claude-api` du dépôt*, `.claude/skills/claude-api/SKILL.md`, à
  la demande du propriétaire : un skill du projet qui porte le nom d'un skill
  fourni le remplace (`skills.md` : « Your skill replaces the bundled
  command »). Le sien, environ 350 mots quand celui de Claude Code pesait
  49 000 jetons, renvoie à la page des tarifs du jour, par une commande qui
  n'en garde que la table principale, à la documentation de Claude Code et
  aux choix du dépôt ; ôter son dossier rend celui de Claude Code. Un
  sous-agent sur Haiku l'a invoqué : c'est bien celui du dépôt qui se charge.
  Le défaut de celui de Claude Code est rédigé pour Anthropic, et le
  propriétaire l'envoie (`/bug`, ou un ticket sur `anthropics/claude-code`,
  que cette session ne peut ouvrir faute du droit d'y pousser).
- *L'agent Explore du dépôt*, `.claude/agents/Explore.md`, à la demande du
  propriétaire : celui de Claude Code, qu'une session lance pour une
  recherche en éventail, tournait sur le modèle de la session, donc sur
  Opus ; celui du dépôt, du même nom, le remplace (`sub-agents.md`) et tourne
  sur Haiku, au contrat de l'éclaireur, avec l'ampleur que la demande lui
  fixe — rapide, moyenne ou très poussée. Appelé au tour qui a suivi son
  écriture, il a tourné sur `claude-haiku-5-5`, et rendu un inventaire exact
  des agents et des skills du dépôt. La règle de `CLAUDE.md` ne change pas :
  une recherche en éventail ne se lance qu'à la demande du propriétaire.

**Ce qui reste au propriétaire.** Le modèle de chaque session, à son
ouverture : Opus 5.5 pour le modèle, le droit et la certification des
données, où un jugement faux part sur `main` sans relecture ; Sonnet 5.5, à
moitié prix, pour ce que les tests tiennent serré — le site, l'outillage, la
prose, l'archivage d'une action. L'effort `max` passe devant celui que
déclarent les agents : l'éclaireur et Explore tournent donc à `max` sur
Haiku, ce qui les ralentit sans peser sur la facture, et les agents
d'impeccable, qui déclaraient `medium` ou `high`, à `max` sur Opus. Dans
quelques jours, `python scripts/consommation.py`, ou `/usage` pour un
abonné, dira la part que prennent les agents sur Haiku.
