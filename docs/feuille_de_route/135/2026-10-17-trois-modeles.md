# Trois modèles : Opus pour juger, Haiku pour lire

**Le 17 octobre 2026, la demande.** Le propriétaire, qui a lu les annonces de
Haiku 5.5 : « J'aimerais optimiser l'utilisation des différents modèles opus,
sonnet et haiku […] Il faut regarder la doc pour voir si on ne pourrait pas
optimiser en utilisant les 3 modèles au lieu d'un seul. » Jusque-là, toute
session tournait sur Opus 5.5, ses sous-agents aussi (`model: inherit` pour
ceux d'impeccable), et l'effort est fixé à `max` depuis le matin même
(`1214e18`).

- *Les tarifs du jour*, en dollars par million de jetons (API ; le skill
  `claude-api` de Claude Code 2.1.302, à jour au 6 octobre). L'écriture du
  cache coûte 1,25 fois l'entrée pour cinq minutes, deux fois pour une heure,
  la durée que tient une session.

  | modèle | entrée | lecture du cache | sortie |
  |---|---|---|---|
  | Opus 5.5 | 4 | 0,20 | 20 |
  | Sonnet 5.5 | 2 | 0,20 | 10 |
  | Haiku 5.5, contexte de 100 000 jetons au plus | 0,10 | 0,01 | 0,50 |
  | Haiku 5.5, au-delà | 0,50 | 0,05 | 2,50 |

- *Sonnet lit le cache au prix d'Opus*, et c'est la lecture du cache qui
  coûte : 79 % au relevé du 10 octobre, aux tarifs relatifs d'alors
  (`2026-10-07-contexte-1-mesurer.md`), 65 % du même trafic au tarif d'Opus
  5.5. Une longue session passée d'Opus à Sonnet n'économise donc qu'environ
  17 %, sur l'écriture du cache et la sortie ; une courte, davantage : cette
  session-ci, à 43 appels, coûtait 4,62 $ au tarif d'Opus, et en aurait coûté
  3,13 au tarif de Sonnet (−32 %), 0,78 à celui de Haiku (−83 %). Pour un
  modèle moins sûr sur le droit et sur le modèle, le gain de Sonnet est
  maigre.
- *Haiku coûte de quatre à quarante fois moins qu'Opus*, selon la ligne de la
  facture et la longueur du contexte. Le droit et le modèle ne se jugent pas sur lui ;
  la lecture, si : trouver où une règle est écrite, ce que la feuille de route
  et les fiches renvoient à une action. Faite par un sous-agent, elle gagne
  deux fois : ses jetons sont au tarif de Haiku, et ce qu'il lit n'entre pas
  dans le contexte de la session, relu à chaque appel au tarif d'Opus. Cette
  session-ci en donne la mesure à rebours : le skill `claude-api`, chargé pour
  y prendre la table des tarifs, pèse environ 50 000 jetons, relus à chaque
  appel qui a suivi — près du quart des jetons relus de la session.

**Ce que Claude Code permet** (Claude Code 2.1.302, session du cloud ; ce
qui n'a pas été éprouvé ici dit sa source).

- *Un agent du dépôt choisit son modèle* par le champ `model` de son en-tête :
  `haiku` pour l'éclaireur, `inherit`, celui de la session, pour les agents
  d'impeccable. L'outil `Agent` accepte aussi un `model` à l'appel, qui a
  forcé l'agent générique sur Haiku. Le guide de la documentation, que
  Claude Code fournit, tourne déjà sur `claude-haiku-5-5`.
- *Le cache d'une session tient une heure*, celui d'un sous-agent cinq
  minutes (`ephemeral_1h_input_tokens`, `ephemeral_5m_input_tokens` dans les
  transcriptions) : un sous-agent écrit son cache moins cher, mais chacun
  repart d'un contexte neuf, sans rien du cache de la session.
- *Le cache est propre à chaque modèle* (le skill `claude-api`) : une session
  qui change de modèle en chemin réécrit tout son contexte dans le cache du
  nouveau. Passer d'Opus à Sonnet au milieu d'une longue session coûte donc
  une écriture entière, pour une lecture du cache au même prix.

**Ce qui est fait.**

- *L'éclaireur*, `.claude/agents/eclaireur.md` : `model: haiku`, en lecture
  seule (`Read`, `Grep`, `Glob`, `Bash`), qui rend des `fichier:ligne` et des
  citations mot pour mot, jamais un jugement ni une modification. Le hook de
  lecture (`lecture.py`) le tient comme la session. Un agent nouveau se
  charge au tour suivant : appelé dans le tour qui l'a écrit, il est inconnu
  (« Agent type 'eclaireur' not found ») ; d'où un premier essai par un agent
  générique forcé sur Haiku, son texte en consigne, puis, au tour d'après, un
  appel par son nom, qui a tourné sur `claude-haiku-5-5`. L'essai portait
  sur ce que le dépôt disait déjà des modèles, de l'effort et des
  sous-agents : un relevé exact, cité mot pour mot, qui dit ses absences
  (« aucune règle ne fixe de modèle par tâche ») et ce qu'il n'a pu
  vérifier ; un peu plus long que demandé, et lent à l'effort `max` (neuf
  minutes, 52 outils). Coût, au tarif de la tranche de chaque appel :
  0,27 $, quand le même trafic en aurait coûté 1,92 au tarif d'Opus ; et rien
  de ce qu'il a lu n'est entré dans le contexte de la session.
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

**Ce qui reste au propriétaire.** Le modèle de chaque session se choisit à
son ouverture, dans l'interface : Opus 5.5 pour le modèle, le droit et les
données ; Sonnet 5.5 n'y gagnerait qu'un sixième à un tiers. L'effort `max`
passe devant celui que déclarent les agents : l'éclaireur tourne donc à `max`
sur Haiku, ce qui le ralentit sans peser sur la facture, et les agents
d'impeccable, qui déclaraient `medium` ou `high`, à `max` sur Opus. Dans
quelques jours, `python scripts/consommation.py` dira la part que l'éclaireur
prend.
