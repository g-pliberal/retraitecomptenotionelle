# Outillage d'audit d'interface — ce qu'une machine neuve reçoit, et ce qu'elle doit encore faire

Le dépôt embarque trois outils de revue d'interface comme compétences Claude
Code, dans `.claude/skills/`. Ce fichier dit où chacun vit, ce qu'un clone frais
contient déjà, ce qu'il faut encore installer, et comment on change une version
figée. Rien ici ne touche au modèle, aux données ni au site : c'est de
l'outillage, et il ne doit rien coûter à ceux qui ne s'en servent pas.

Un seul geste met tout en place, et on peut le répéter sans risque :

```bash
scripts/setup_ui_tools.sh            # installe ce qui manque, ne retélécharge rien d'inutile
scripts/setup_ui_tools.sh --verifier # rend compte sans rien installer (sortie 1 si manque)
scripts/setup_ui_tools.sh --essai    # en plus, ouvre et ferme un Chromium pour le prouver
```

## Ce qu'un clone frais contient déjà

| Outil | Version | Dans Git | Hors Git, obtenu au premier usage |
|---|---|---|---|
| Impeccable | 4.3.1 (compétence), moteur 0.1.5 | `.claude/skills/impeccable/` (SKILL.md, références, lanceur `scripts/impeccable`, `scripts/VERSION`), les quatre agents `.claude/agents/impeccable-*.md`, le hook dans `.claude/settings.json` | le moteur natif (16 Mo), dans `~/.impeccable/bin/0.1.5/` |
| Web Interface Guidelines | 1.0.0 (compétence), règles figées au commit `e3d624b` | `.claude/skills/web-design-guidelines/` (SKILL.md, `guidelines.md`, `guidelines.provenance.yaml`) | rien |
| Playwright CLI | `@playwright/cli` 0.1.20 | `.claude/skills/playwright-cli/` (SKILL.md livré par ce paquet), `.playwright/cli.config.json` | le paquet npm global, et le Chromium qu'il attend |

Ce qui n'est **pas** dans Git, et ne doit pas y entrer : le binaire du moteur
Impeccable (`.claude/skills/impeccable/scripts/bin/`, ignoré), les navigateurs,
`.claude/settings.local.json` (ignoré), `.impeccable/hook.cache.json` et
`.impeccable/config.local.json` (ignorés), `.playwright-cli/` (sorties de
session, ignoré).

## Ce qui demande le réseau, et une seule fois

- **Le moteur Impeccable.** Le lanceur `.claude/skills/impeccable/scripts/impeccable`
  cherche un binaire à côté de lui, puis dans `~/.impeccable`, puis sur le PATH,
  et en dernier recours télécharge `impeccable-<os>-<arch>` depuis
  `github.com/pbakaus/impeccable/releases` (tag `engine-v0.1.5`), compare sa
  somme SHA-256 au fichier `.sha256` publié à côté, et refuse le binaire si la
  somme manque ou diffère. Une fois en cache, plus rien ne sort. Sans réseau,
  `IMPECCABLE_BIN` peut désigner un binaire préinstallé.
- **`@playwright/cli@0.1.20`**, depuis `registry.npmjs.org`, installé
  globalement par npm (jamais dans le dépôt : pas de `node_modules`, pas de
  `package.json`, `pyproject.toml` intact). Le script n'installe que si la
  commande manque ou répond une autre version.
- **Chromium** (« Chrome for Testing », ~190 Mo), depuis `cdn.playwright.dev`,
  par `playwright-cli install-browser chromium`, le mécanisme officiel. Le
  script ne le lance que si la révision attendue par cette version du CLI est
  absente ; `--sans-navigateur` l'en empêche. Playwright range les navigateurs
  sous `PLAYWRIGHT_BROWSERS_PATH` quand la variable est posée (les machines
  Claude Code Cloud la pointent sur `/opt/pw-browsers`), sinon dans son cache
  utilisateur. Le Chromium qu'une machine de Claude Code Cloud préinstalle est
  celui d'un autre Playwright ; il ne sert pas au CLI figé, et le script n'en
  dépend pas.
- Le script n'installe pas les bibliothèques système du navigateur. Si
  `--essai` échoue au lancement, `npx playwright install-deps chromium`
  (droits root) les pose.

Rien ne dépend du répertoire personnel d'une machine précédente, ni de ses
réglages locaux.

## Impeccable

Le hook du détecteur (un passage court après chaque `Edit`/`Write` sur un
fichier d'interface, un passage complet au `Stop`) est dans
`.claude/settings.json`, commité, et n'appelle que
`"${CLAUDE_PROJECT_DIR}/.claude/skills/impeccable/scripts/impeccable" hook` :
aucun chemin absolu, rien de propre à une machine. C'est exactement ce que
`impeccable hooks on` écrit dans `.claude/settings.local.json`, déplacé dans le
fichier partagé comme la compétence le prévoit ; ne pas relancer `hooks on`,
qui recréerait le doublon local. Sans `.impeccable/config.json`, le hook tourne
avec ses valeurs par défaut (activé, cinq constats, 8 000 caractères) ;
`/impeccable hooks off|ignore-value|…` crée ce fichier, qui peut être commité.
Le hook écrit `.impeccable/hook.cache.json` à l'usage, ignoré.

`impeccable.cmd` couvre Windows sans `sh` ; le hook commité appelle le lanceur
POSIX, comme sur les machines Cloud.

## Playwright CLI

`.playwright/cli.config.json` demande Chromium par le canal `chromium` ; c'est
le fichier que `playwright-cli install` génère, à l'identique. La compétence
`.claude/skills/playwright-cli/SKILL.md` est celle que le paquet 0.1.20 livre
(`playwright-cli --help` en imprime le chemin d'origine). Pour changer de
version : modifier `PLAYWRIGHT_CLI_VERSION` dans `scripts/setup_ui_tools.sh`,
relancer le script, puis recopier la SKILL.md livrée par le nouveau paquet
dans `.claude/skills/playwright-cli/` si elle a changé. Pas de Playwright MCP :
tout passe par la ligne de commande.

## Web Interface Guidelines : règles figées

`SKILL.md` lit `guidelines.md`, copie conforme, octet pour octet, de
`command.md` du dépôt `vercel-labs/web-interface-guidelines` au commit inscrit
dans `guidelines.provenance.yaml` (avec la date de lecture et la somme
SHA-256). Un audit normal ne va donc plus chercher `main` et donne les mêmes
constats d'une session à l'autre. `scripts/setup_ui_tools.sh` vérifie que la
somme du fichier est bien celle de la provenance.

Pour rafraîchir les règles, volontairement et jamais au détour d'un audit :

1. Choisir le commit amont, par exemple la tête de `main` :
   `git ls-remote https://github.com/vercel-labs/web-interface-guidelines main`.
2. Récupérer le fichier **à ce commit**, pas à `main` :
   `curl -fsSL -o .claude/skills/web-design-guidelines/guidelines.md https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/<sha>/command.md`.
3. Mettre à jour `guidelines.provenance.yaml` : `upstream_commit`,
   `upstream_commit_date`, `upstream_blob` (`git ls-tree <sha> command.md`),
   `retrieved_from`, `retrieved_on`, `sha256` (`sha256sum guidelines.md`).
4. `scripts/setup_ui_tools.sh --verifier` doit répondre « conforme ».
5. Lire le diff de `guidelines.md` : c'est lui qui dit ce que les audits
   suivants jugeront autrement. Le commiter avec la provenance.

`skills-lock.json` garde l'empreinte de la compétence telle qu'installée
depuis `vercel-labs/agent-skills` ; la SKILL.md locale s'en écarte à dessein
(elle lit la copie figée). Un `npx skills update` écraserait ce choix : ne pas
le lancer sans refaire ensuite l'édition décrite ci-dessus.
