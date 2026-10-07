#!/usr/bin/env bash
# Publie ce que GitHub vient de fabriquer, et le verdict de la suite.
#
# Lancé par `.github/workflows/tests.yml`, après `regenerer.py` et la suite
# complète (action 148, étape 1) : les sessions ne régénèrent plus avant
# d'envoyer, GitHub refait les fichiers fabriqués sur le dernier main. Ce
# script écrit le verdict dans `.github/etat_suite.yaml` — que le hook
# `SessionStart` affiche à l'ouverture de chaque session, sans API GitHub —,
# le commite sous l'identité noreply du robot, avec les fichiers fabriqués si
# la suite est verte, et le pousse SANS FORCER. Si la branche a bougé pendant
# la course, il ne pousse rien : la course suivante, qu'a lancée cet envoi,
# refera tout.
#
# Entrées : FABRICATION et SUITE, l'issue des deux étapes (success ou autre) ;
# SORTIE_SUITE, le fichier où la suite a écrit ; COURSE, l'adresse de la course.

set -euo pipefail

branche=${GITHUB_REF_NAME:?}
source=$(git rev-parse HEAD)
# L'issue de l'étape ne suffit pas : un tube sans pipefail l'a dite réussie
# onze courses de suite, le 7 octobre 2026, sur jusqu'à six échecs. Un échec
# que la sortie nomme rend la suite rouge.
if grep -qE '^(FAILED|ERROR) ' "${SORTIE_SUITE:-/dev/null}" 2>/dev/null; then
    SUITE=echecs_dans_la_sortie
fi
etat=vert
if [ "${FABRICATION:-}" != success ] || [ "${SUITE:-}" != success ]; then
    etat=rouge
    # Une suite rouge ne publie aucun fichier fabriqué : seulement son verdict.
    git checkout -- .
    git clean -fdq
fi

fichier=.github/etat_suite.yaml
{
    echo "# Le verdict de la dernière course de tests.yml : écrit par GitHub"
    echo "# (scripts/publier_fabrique.sh), jamais à la main. Action 148."
    echo "etat: $etat"
    echo "sources: $source"
    echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "course: ${COURSE:-}"
    if [ "$etat" = rouge ]; then
        echo "echecs:"
        if [ "${FABRICATION:-}" != success ]; then
            echo "  - \"scripts/regenerer.py a échoué\""
        fi
        grep -E '^(FAILED|ERROR) ' "${SORTIE_SUITE:-/dev/null}" 2>/dev/null \
            | head -n 30 | sed 's/"/\\"/g; s/^/  - "/; s/$/"/' || true
    fi
} > "$fichier"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
fabriques=$(git diff --cached --name-only | { grep -v -x "$fichier" || true; } | wc -l)
if [ "$etat" = vert ]; then
    titre="Fabriqué par GitHub : suite verte sur ${source:0:7}, $fabriques fichier(s) refait(s)"
else
    titre="Suite ROUGE sur ${source:0:7} : voir .github/etat_suite.yaml"
fi
git commit --quiet -m "$titre" -m "${COURSE:-}"

# Pousser sans forcer, et seulement si la branche n'a pas bougé : sinon, la
# course suivante refait tout sur la nouvelle tête.
a_bouge() {
    git fetch --quiet origin "$branche"
    [ "$(git rev-parse FETCH_HEAD)" != "$source" ]
}
if a_bouge; then
    echo "::notice::$branche a bougé pendant la course : rien poussé, la suivante refera tout."
    exit 0
fi
if ! git push --quiet origin "HEAD:refs/heads/$branche"; then
    if a_bouge; then
        echo "::notice::$branche a bougé au moment de pousser : rien poussé, la suivante refera tout."
        exit 0
    fi
    echo "::error::Poussée refusée. Réglage : Settings → Actions → General → Workflow permissions → « Read and write permissions » ; et, si main est protégée, y autoriser GitHub Actions."
    exit 1
fi
echo "$branche ← $(git rev-parse --short HEAD) ($etat, $fabriques fichier(s) fabriqué(s))"
