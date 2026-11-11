#!/usr/bin/env bash
# Inscrit à la liste de contrôle des textes les rédactions nouvelles de
# l'index, et publie ce que l'inscription écrit.
#
# Lancé par `.github/workflows/index-dila.yml`, pour LEGI, chaque lundi après
# la mise à jour de l'index (action 184, étape 4 ; le propriétaire l'a décidé
# le 11 novembre 2026) : les sessions n'ont plus à lancer l'inscription en
# ouvrant. La commande qui inscrit est celle que le workflow passe en
# arguments :
#
#     bash scripts/publier_inscription.sh python scripts/textes.py --inscrire
#
# L'inscription se fait sur le DERNIER main, non sur l'arbre que la course a
# pris en partant : la mise à jour de l'index dure, et une session a pu pousser
# depuis. Ce qu'elle écrit sous `data/reference/textes/`, et cela seul, se
# commite sous l'identité noreply du robot et se pousse SANS FORCER. Si une
# session pousse entre-temps, la poussée est refusée : l'inscription, qui ne
# coûte que quelques secondes, se refait sur la nouvelle tête, trois fois au
# plus. Rien d'écrit, rien de commité.
#
# Entrées : GITHUB_REF_NAME, la branche ; COURSE, l'adresse de la course.
# Sortie : `inscrit=oui` dans GITHUB_OUTPUT quand un commit est poussé, et
# alors seulement : le workflow lance la suite complète, que la poussée du
# jeton d'un workflow ne déclenche pas.

set -euo pipefail

# Le script change d'arbre en cours de route : bash l'a lu en entier, dans
# cette fonction, avant de l'exécuter.
principal() {
    local branche=${GITHUB_REF_NAME:?} liste=data/reference/textes
    local essai sortie nouvelles
    [ "$#" -gt 0 ] || { echo "usage : publier_inscription.sh <commande qui inscrit>" >&2; exit 2; }
    git config user.name "github-actions[bot]"
    git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
    for essai in 1 2 3; do
        git fetch --quiet origin "$branche"
        git checkout --quiet --detach FETCH_HEAD
        sortie=$("$@")
        printf '%s\n' "$sortie"
        git add -- "$liste"
        if git diff --cached --quiet; then
            echo "Rien de neuf à la liste des textes : rien commité."
            return 0
        fi
        # « 12 rédactions nouvelles inscrites… » : le compte ouvre la sortie.
        nouvelles=des
        [[ $sortie =~ ^([0-9]+)[[:space:]] ]] && nouvelles=${BASH_REMATCH[1]}
        git commit --quiet \
            -m "Inscrit par GitHub : $nouvelles rédaction(s) nouvelle(s) à la liste des textes" \
            -m "${COURSE:-}"
        if git push --quiet origin "HEAD:refs/heads/$branche"; then
            echo "$branche ← $(git rev-parse --short HEAD) ($nouvelles rédaction(s) nouvelle(s))"
            echo "inscrit=oui" >> "${GITHUB_OUTPUT:-/dev/null}"
            return 0
        fi
        echo "::notice::$branche a bougé pendant l'inscription (essai $essai) : elle se refait sur sa nouvelle tête."
    done
    echo "::error::Poussée refusée trois fois : rien inscrit. Si $branche n'a pas bougé, le réglage est Settings → Actions → General → Workflow permissions → « Read and write permissions »."
    return 1
}

principal "$@"
exit
