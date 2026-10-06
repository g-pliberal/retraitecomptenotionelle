#!/bin/bash
# À l'ouverture d'une session : le verdict de la dernière course de la suite
# complète sur GitHub (action 148), lu dans le dépôt, sans API GitHub. Une
# suite rouge se répare avant toute autre chose.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
f=.github/etat_suite.yaml
[ -f "$f" ] || exit 0
etat=$(sed -n 's/^etat: //p' "$f")
sources=$(sed -n 's/^sources: //p' "$f")
depuis=$(git log -1 --format=%H -- "$f" 2>/dev/null)
attente=$( [ -n "$depuis" ] && git rev-list --count "$depuis"..HEAD 2>/dev/null || echo "?")
if [ "$etat" = rouge ]; then
    echo "SUITE ROUGE sur main (GitHub, sources ${sources:0:7}) : la réparer avant toute autre chose."
    sed -n '/^course:/p; /^echecs:/,$p' "$f"
else
    if [ "$attente" = 0 ]; then
        echo "Suite complète verte sur GitHub, sur la tête de main (${sources:0:7})."
    else
        echo "Suite complète verte sur GitHub (sources ${sources:0:7}) ; $attente commit(s) depuis, que la course suivante vérifie."
    fi
fi
exit 0
