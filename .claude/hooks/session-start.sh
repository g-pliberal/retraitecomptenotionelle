#!/bin/bash
# Une session web démarre en état de marche (action 33 de la feuille de route,
# archivée) : pytest, pytest-xdist et le paquet, que `python -m pytest` exige.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" != "true" ] && exit 0
# Asynchrone : la session s'ouvre sans attendre la fin de l'installation.
# Cette ligne doit être la première de la sortie standard ; rien d'autre n'y
# va, d'où `--quiet` et `--root-user-action=ignore`.
echo '{"async": true, "asyncTimeout": 300000}'
cd "${CLAUDE_PROJECT_DIR:-.}"
pip_install() {
  python -m pip install --quiet --disable-pip-version-check \
    --root-user-action=ignore "$@"
}
pip_install -e '.[dev]'
# PyYAML de PyPI plutôt que celui de la distribution : sa roue embarque
# libyaml, que `charger_yaml` préfère au chargeur Python. Celui de Debian ne
# se laisse pas désinstaller, d'où `--ignore-installed`, qui le masque.
python -c 'import yaml,sys; sys.exit(0 if yaml.__with_libyaml__ else 1)' \
  || pip_install --ignore-installed --no-cache-dir PyYAML
