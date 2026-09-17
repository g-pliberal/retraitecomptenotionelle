#!/usr/bin/env bash
# Outillage d'audit d'interface : installe ou vérifie, sans rien casser quand on
# le relance, les trois outils que le dépôt embarque en compétences Claude Code
# (.claude/skills/) :
#   - Impeccable : le lanceur est commité, le moteur natif (16 Mo) est
#     téléchargé une fois dans ~/.impeccable et vérifié par somme SHA-256 ;
#   - Playwright CLI : @playwright/cli à la version testée, installé
#     globalement par npm, plus le Chromium qu'il attend s'il manque ;
#   - Web Interface Guidelines : la copie figée guidelines.md, dont la somme
#     est comparée à guidelines.provenance.yaml.
# Ne touche ni pyproject.toml, ni les dépendances de l'application, et ne crée
# pas de node_modules dans le dépôt. Voir docs/outillage_interface.md.
#
# Usage : scripts/setup_ui_tools.sh [--verifier] [--sans-navigateur] [--essai]
#   --verifier         ne rien installer ni télécharger, seulement rendre compte
#                      (sortie 1 si quelque chose manque)
#   --sans-navigateur  ne pas télécharger Chromium même s'il manque
#   --essai            ouvrir puis fermer un navigateur pour prouver que la
#                      chaîne Playwright complète fonctionne
set -euo pipefail

PLAYWRIGHT_CLI_VERSION=0.1.20

racine=$(cd -- "$(dirname -- "$0")/.." && pwd)
lanceur="$racine/.claude/skills/impeccable/scripts/impeccable"
version_impeccable=$(tr -d '[:space:]' < "$racine/.claude/skills/impeccable/scripts/VERSION")
guidelines="$racine/.claude/skills/web-design-guidelines/guidelines.md"
provenance="$racine/.claude/skills/web-design-guidelines/guidelines.provenance.yaml"

verifier=0; sans_navigateur=0; essai=0
for arg in "$@"; do
  case "$arg" in
    --verifier) verifier=1 ;;
    --sans-navigateur) sans_navigateur=1 ;;
    --essai) essai=1 ;;
    -h|--help) sed -n '2,/^set -/{/^set -/!p}' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "argument inconnu : $arg (voir --help)" >&2; exit 2 ;;
  esac
done

manques=0
reseau=()
ok()     { printf '  ok      %s\n' "$*"; }
fait()   { printf '  fait    %s\n' "$*"; }
manque() { printf '  MANQUE  %s\n' "$*"; manques=$((manques + 1)); }
titre()  { printf '\n%s\n' "$*"; }
somme()  {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else shasum -a 256 "$1" | cut -d' ' -f1; fi
}

# --- Impeccable ---------------------------------------------------------------
titre "Impeccable $version_impeccable"
if [ ! -x "$lanceur" ]; then
  manque "lanceur non exécutable : $lanceur (chmod +x)"
else
  # IMPECCABLE_LAUNCHER_PROBE=1 fait répondre le lanceur sans jamais télécharger.
  reponse=$(IMPECCABLE_LAUNCHER_PROBE=1 "$lanceur" engine-probe 2>/dev/null || true)
  if [ "$reponse" = "impeccable-engine $version_impeccable" ]; then
    ok "moteur $version_impeccable présent (cache ${IMPECCABLE_HOME:-$HOME/.impeccable}/bin ou binaire préinstallé)"
  elif [ "$verifier" = 1 ]; then
    manque "moteur $version_impeccable absent ; sans --verifier, le lanceur le télécharge et vérifie sa somme"
  else
    reponse=$("$lanceur" engine-probe 2>&1 || true)
    if [ "$reponse" = "impeccable-engine $version_impeccable" ]; then
      fait "moteur $version_impeccable téléchargé, somme SHA-256 vérifiée, mis en cache"
      reseau+=("moteur Impeccable $version_impeccable depuis github.com/pbakaus/impeccable/releases")
    else
      manque "le lanceur n'a pas obtenu le moteur : ${reponse:-(aucune sortie)}"
    fi
  fi
fi
if grep -qF 'scripts/impeccable\" hook' "$racine/.claude/settings.json" 2>/dev/null; then
  ok "hook du détecteur porté par .claude/settings.json (PostToolUse et Stop)"
else
  manque "hook absent de .claude/settings.json"
fi

# --- Playwright CLI -----------------------------------------------------------
titre "Playwright CLI $PLAYWRIGHT_CLI_VERSION"
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  manque "node et npm sont requis (Node.js 18 ou plus) ; rien d'autre n'est tenté pour Playwright"
else
  version_actuelle=""
  if command -v playwright-cli >/dev/null 2>&1; then
    version_actuelle=$(playwright-cli --version 2>/dev/null || true)
  fi
  if [ "$version_actuelle" = "$PLAYWRIGHT_CLI_VERSION" ]; then
    ok "playwright-cli $version_actuelle déjà installé ($(command -v playwright-cli))"
  elif [ "$verifier" = 1 ]; then
    manque "playwright-cli ${version_actuelle:-absent}, version attendue $PLAYWRIGHT_CLI_VERSION"
  else
    # Depuis un répertoire hors du dépôt : npm -g ne lit alors aucun package.json
    # et ne peut rien créer dans l'arborescence du projet.
    if (cd "${TMPDIR:-/tmp}" && npm install -g --no-fund --no-audit "@playwright/cli@$PLAYWRIGHT_CLI_VERSION" >/dev/null); then
      hash -r
      version_actuelle=$(playwright-cli --version 2>/dev/null || true)
      if [ "$version_actuelle" = "$PLAYWRIGHT_CLI_VERSION" ]; then
        fait "playwright-cli $version_actuelle installé globalement dans $(npm prefix -g)/bin"
        reseau+=("@playwright/cli@$PLAYWRIGHT_CLI_VERSION depuis registry.npmjs.org")
      else
        manque "après installation, playwright-cli répond « ${version_actuelle:-rien} » au lieu de $PLAYWRIGHT_CLI_VERSION (PATH sans $(npm prefix -g)/bin ?)"
      fi
    else
      manque "npm install -g @playwright/cli@$PLAYWRIGHT_CLI_VERSION a échoué (réseau, ou droits sur $(npm prefix -g))"
    fi
  fi

  if [ "$version_actuelle" = "$PLAYWRIGHT_CLI_VERSION" ]; then
    if playwright-cli --help >/dev/null 2>&1; then
      ok "playwright-cli --help répond"
    else
      manque "playwright-cli --help échoue"
    fi

    # Le Chromium attendu par cette version : Playwright le nomme par révision
    # (chromium-NNNN) sous PLAYWRIGHT_BROWSERS_PATH ou son cache par défaut, et
    # dépose INSTALLATION_COMPLETE quand le téléchargement a abouti.
    cli_js=$(node -e 'process.stdout.write(require("fs").realpathSync(process.argv[1]))' "$(command -v playwright-cli)")
    pw_core=$(node -e 'const p=require("path");process.stdout.write(p.dirname(require.resolve("playwright-core/package.json",{paths:[p.dirname(process.argv[1])]})))' "$cli_js")
    emplacement=$(node "$pw_core/cli.js" install --dry-run chromium 2>/dev/null \
      | awk '/\(playwright chromium v[0-9]+\)/ {bloc=1; next}
             bloc && /Install location:/ {sub(/.*Install location:[ \t]*/, ""); print; exit}
             /^$/ {bloc=0}')
    if [ -z "$emplacement" ]; then
      manque "impossible de déterminer où Playwright range Chromium (playwright install --dry-run muet)"
    elif [ -f "$emplacement/INSTALLATION_COMPLETE" ]; then
      ok "Chromium présent : $emplacement"
    elif [ "$verifier" = 1 ] || [ "$sans_navigateur" = 1 ]; then
      manque "Chromium absent de $emplacement ; « playwright-cli install-browser chromium » l'installe (téléchargement ~190 Mo)"
    else
      if playwright-cli install-browser chromium >/dev/null 2>&1 && [ -f "$emplacement/INSTALLATION_COMPLETE" ]; then
        fait "Chromium installé par playwright-cli install-browser dans $emplacement"
        reseau+=("Chromium (Chrome for Testing) depuis cdn.playwright.dev, ~190 Mo")
      else
        manque "playwright-cli install-browser chromium a échoué (réseau ?)"
      fi
    fi

    if [ "$essai" = 1 ]; then
      # Session nommée pour ne pas toucher un navigateur déjà ouvert ; la sortie
      # va dans .playwright-cli/, ignoré par Git.
      if (cd "$racine" && playwright-cli -s=setup-essai open about:blank >/dev/null 2>&1 \
          && playwright-cli -s=setup-essai close >/dev/null 2>&1); then
        ok "essai : un Chromium s'est ouvert et fermé avec .playwright/cli.config.json"
      else
        playwright-cli -s=setup-essai close >/dev/null 2>&1 || true
        manque "essai : le navigateur n'a pas démarré ; bibliothèques système ? (« npx playwright install-deps chromium », droits root)"
      fi
    fi
  fi
fi

# --- Web Interface Guidelines -------------------------------------------------
titre "Web Interface Guidelines"
if [ ! -f "$guidelines" ] || [ ! -f "$provenance" ]; then
  manque "guidelines.md ou guidelines.provenance.yaml absent de .claude/skills/web-design-guidelines/"
else
  attendue=$(sed -n 's/^sha256:[[:space:]]*//p' "$provenance")
  commit=$(sed -n 's/^upstream_commit:[[:space:]]*//p' "$provenance")
  reelle=$(somme "$guidelines")
  if [ -n "$attendue" ] && [ "$reelle" = "$attendue" ]; then
    ok "guidelines.md conforme à sa provenance (commit amont ${commit:0:12})"
  else
    manque "guidelines.md ne correspond plus à guidelines.provenance.yaml (somme $reelle) : mettre à jour les deux ensemble, voir docs/outillage_interface.md"
  fi
fi

# --- Bilan --------------------------------------------------------------------
titre "Bilan"
if [ "${#reseau[@]}" -gt 0 ]; then
  echo "  Téléchargé cette fois :"
  for r in "${reseau[@]}"; do echo "    - $r"; done
else
  echo "  Rien téléchargé : tout était déjà en place."
fi
if [ "$manques" -gt 0 ]; then
  echo "  $manques point(s) manquant(s), voir ci-dessus." >&2
  exit 1
fi
echo "  Les trois outils sont opérationnels."
