#!/bin/bash
# À l'ouverture d'une session : le verdict de la dernière course de la suite
# complète sur GitHub (action 148), lu dans le dépôt, sans API GitHub. Une
# suite rouge se répare avant toute autre chose.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
f=.github/etat_suite.yaml
[ -f "$f" ] || exit 0
etat=$(sed -n 's/^etat: //p' "$f")
sources=$(sed -n 's/^sources: //p' "$f")
# Les envois venus depuis les sources du verdict, les commits du robot à part :
# un verdict se publie aussi sur une tête qui a dépassé ses sources (action 135).
attente=$(git rev-list --count "$sources"..HEAD 2>/dev/null) || attente=
if [ -n "$attente" ]; then
    robot=$(git rev-list --count --author='github-actions\[bot\]' "$sources"..HEAD)
    attente=$((attente - robot))
fi
if [ "$etat" = rouge ]; then
    depuis=
    if [ -n "$attente" ] && [ "$attente" != 0 ]; then
        depuis=" ; $attente commit(s) depuis"
    fi
    echo "SUITE ROUGE sur main (GitHub, sources ${sources:0:7}$depuis) : la réparer avant toute autre chose."
    sed -n '/^course:/p; /^echecs:/,/^presomptions/{/^presomptions/!p}' "$f"
else
    if [ "$attente" = 0 ]; then
        echo "Suite complète verte sur GitHub, sur la tête de main (${sources:0:7})."
    else
        echo "Suite complète verte sur GitHub (sources ${sources:0:7}) ; ${attente:-?} commit(s) depuis, que la course suivante vérifie."
    fi
fi
# La garde des présomptions (action 135, levier 2) : un test qui écrit en dur
# une valeur présumée, à faire déclarer sa date avant toute autre chose.
if [ "$(sed -n 's/^presomptions: //p' "$f")" = rouge ]; then
    echo "GARDE DES PRÉSOMPTIONS ROUGE (PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide) : ces tests écrivent une valeur présumée ; leur faire déclarer leur date (action 135, levier 2)."
    sed -n '/^presomptions_echecs:/,$p' "$f" | tail -n +2
fi
exit 0
