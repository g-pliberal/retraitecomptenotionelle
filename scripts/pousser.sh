#!/usr/bin/env bash
# Publie sur main ce que la session a commité, et aligne la branche de session.
#
# Pourquoi ce script existe : le dépôt veut tout sur main (voir CLAUDE.md), mais
# une session web est posée d'office sur une branche claude/*, dont la référence
# distante est créée au démarrage. `git push origin HEAD:main` ne touche pas
# cette référence : elle reste sur le commit du clone, le compteur de commits
# « non poussés » monte à chaque commit, et chaque session y perdait un
# paragraphe d'explication. On pousse donc sur main (c'est là que le travail
# vit) puis on fait suivre la référence de branche, qui ne porte alors jamais
# que ce que main porte déjà. On ne crée jamais cette référence si elle
# n'existe pas : une session ne pourrait pas la supprimer (403).
#
# Usage : bash scripts/pousser.sh   — silencieux s'il n'y a rien à publier,
# une ligne s'il a poussé, un message sur stderr et un code non nul s'il bloque.

set -uo pipefail

ici=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
racine=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "pousser: pas dans un dépôt git" >&2; exit 1; }
cd "$racine" || exit 1

# Une tête détachée publie comme une autre : c'est `HEAD` qui part sur main,
# pas une branche. Une session créée par une autre session part ainsi, et le
# refus d'avant lui laissait son travail sur les bras. Il n'y a seulement
# aucune branche de session à faire suivre : `branche` reste vide, et les deux
# derniers blocs ne font rien.
branche=$(git rev-parse --abbrev-ref HEAD)
[ "$branche" = HEAD ] && branche=""

# Le réseau lâche : quatre essais, 2s, 4s, 8s, 16s.
avec_reprises() {
    local attente=2 essai
    for essai in 1 2 3 4 5; do
        if "$@"; then return 0; fi
        [ "$essai" = 5 ] && return 1
        sleep "$attente"
        attente=$(( attente * 2 ))
    done
}

# Les quatre fusions que git confie à scripts/fusionner.py, le temps du rebasage
# (action 148, étape 3) : `ancres`, la prose dont seuls divergent les chiffres
# ancrés et les blocs produits, qui gardent la valeur de main, puisque GitHub
# les refait ; `ensembles`, la référence de la conservation, dont chaque liste
# se fusionne comme un ensemble ; `cles`, les témoins rangés par cas, fusionnés
# entrée par entrée, une entrée changée des deux côtés restant un conflit ;
# `compteurs`, les cliquets, dont les baisses des deux côtés s'additionnent. `.gitattributes` dit quel fichier relève de
# laquelle ; git ne les connaît que par ces options : un rebasage à la main
# fusionne ces fichiers comme du texte. Le pilote est copié hors du répertoire
# de travail, que le rebasage récrit, et seulement s'il faut rebaser. Sans
# Python, pas de pilote, et rien ne change.
fusions=()
pilote=""
declarer_les_pilotes() {
    [ -f "$ici/fusionner.py" ] || return 0
    local python mode
    for python in python3 python; do
        "$python" -c 'import difflib, json' >/dev/null 2>&1 || continue
        pilote="$(git rev-parse --absolute-git-dir)/fusionner-$$.py"
        cp "$ici/fusionner.py" "$pilote" 2>/dev/null || return 0
        trap 'rm -f "$pilote"' EXIT
        for mode in ancres ensembles cles compteurs; do
            fusions+=(-c "merge.$mode.name=scripts/fusionner.py $mode"
                      -c "merge.$mode.driver=$python \"$pilote\" $mode %O %A %B %L")
        done
        return 0
    done
}
avec_fusions() {
    git ${fusions[@]+"${fusions[@]}"} "$@"
}

# Rebaser sur origin/main. Un conflit qui ne porte QUE sur des fichiers
# fabriqués (ceux que .gitattributes marque `-merge`) se règle seul : on garde
# la version de main, sans régénérer, puisque GitHub refait tout après chaque
# envoi (tests.yml, action 148). Un commit qui ne portait que des fichiers
# fabriqués devient vide : on le saute. Un conflit sur une source refuse —
# sauf ce que les deux pilotes ci-dessus ont déjà réglé pendant la fusion.
# Le fichier fabriqué que .gitattributes marque `refaire=<script>`, le paquet,
# garde aussi la version de main, mais ne part pas ainsi : les deux moteurs y
# lisent leurs règles, et la correction de la session partirait avec le paquet
# d'une autre, son propre test rouge sur main jusqu'au commit de GitHub
# (action 135, 14 novembre 2026). Le rebasage fini, son script le refait des
# sources réunies, dans le dernier commit de la session (refaire_le_paquet).
fabrique() {
    git check-attr merge -- "$1" | grep -q ': merge: unset$'
}
le_refait="" temoins_en_conflit=""
marque_du_paquet=$(git rev-parse --git-path paquet-a-refaire)
script_qui_refait() {
    git check-attr refaire -- "$1" | sed -n 's/^.*: refaire: \(scripts\/.*\)$/\1/p'
}
rebase_en_cours() {
    [ -d "$(git rev-parse --git-path rebase-merge)" ] \
        || [ -d "$(git rev-parse --git-path rebase-apply)" ]
}
rebaser() {
    declarer_les_pilotes
    avec_fusions rebase --quiet origin/main >/dev/null 2>&1 && return 0
    local tours=0 conflits fichier script
    while rebase_en_cours; do
        tours=$(( tours + 1 ))
        [ "$tours" -gt 100 ] && return 1
        conflits=$(git diff --name-only --diff-filter=U)
        [ -z "$conflits" ] && return 1
        while IFS= read -r fichier; do
            if git check-attr merge -- "$fichier" | grep -q ': merge: cles$'; then
                temoins_en_conflit="${temoins_en_conflit:+$temoins_en_conflit, }$fichier"
            fi
        done <<< "$conflits"
        [ -z "$temoins_en_conflit" ] || return 1
        while IFS= read -r fichier; do
            fabrique "$fichier" || return 1
            script=$(script_qui_refait "$fichier")
            [ -z "$script" ] || le_refait="$script"
        done <<< "$conflits"
        while IFS= read -r fichier; do
            # « ours », au rebasage, est main (et nos commits déjà rejoués).
            if git checkout --ours -- "$fichier" 2>/dev/null; then
                git add -- "$fichier"
            else
                git rm --quiet --cached -- "$fichier" >/dev/null 2>&1
                rm -f -- "$fichier"
            fi
        done <<< "$conflits"
        if git diff --cached --quiet; then
            GIT_EDITOR=true avec_fusions rebase --skip >/dev/null 2>&1 && return 0
        else
            GIT_EDITOR=true avec_fusions rebase --continue >/dev/null 2>&1 && return 0
        fi
    done
    ! rebase_en_cours
}

avec_reprises git fetch --quiet origin main || {
    echo "pousser: fetch origin main impossible après 5 essais" >&2; exit 1; }

# origin/main est ce que GitHub porte ; le main local est un post-it périmé, on
# ne le nomme jamais. Trois cas, et un seul touche au répertoire de travail.
if git merge-base --is-ancestor origin/main HEAD; then
    :   # HEAD porte déjà tout main : rien à rattraper, on ne touche à rien
elif git merge-base --is-ancestor HEAD origin/main; then
    # En retard sur main : avance rapide. Elle refuse si des modifications non
    # commitées sont sur le chemin — le dire, plutôt que crier à la divergence.
    if ! git merge --ff-only origin/main >/dev/null 2>&1; then
        echo "pousser: impossible de rattraper origin/main (des modifications non commitées sont sur le chemin ?), rien poussé" >&2
        exit 1
    fi
else
    # Les deux lignées ont divergé. Le cas ordinaire est bénin — une autre
    # session a poussé pendant celle-ci, chacune a ses commits depuis une base
    # commune — et un rebasage le règle : nos commits n'ont jamais été publiés
    # sur main. On refuse dès que ça sort de ce cas.
    base=$(git merge-base HEAD origin/main 2>/dev/null || echo "")
    if [ -z "$base" ]; then
        echo "pousser: HEAD et origin/main n'ont aucun ancêtre commun, rien poussé — c'est le cas grave, voir CLAUDE.md" >&2
        exit 1
    fi
    if [ "$(git rev-list --count "$base"..HEAD)" -gt 20 ]; then
        echo "pousser: HEAD a divergé de origin/main de plus de vingt commits, rien poussé — comprendre pourquoi avant d'insister (git log --oneline --graph HEAD origin/main)" >&2
        exit 1
    fi
    if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
        echo "pousser: origin/main a avancé et des modifications ne sont pas commitées, rien poussé — commiter, puis relancer" >&2
        exit 1
    fi
    if ! rebaser; then
        git rebase --abort >/dev/null 2>&1 || true
        if [ -n "$temoins_en_conflit" ]; then
            # Le pilote `cles` laisse le conflit quand une même entrée a bougé
            # des deux côtés : sa valeur vient des deux corrections réunies.
            echo "pousser: le rebasage sur origin/main bute sur un conflit, rien poussé — un même cas témoin a bougé des deux côtés ($temoins_en_conflit) : aucune des deux valeurs n'est celle des corrections réunies. Rebaser à la main (git rebase origin/main), garder à chaque arrêt le témoin de main (git checkout --ours -- <témoin>, git add, git rebase --continue), puis refaire les témoins des sources réunies (python scripts/construire_temoins.py), relire ce qui a bougé, et le commiter" >&2
        else
            echo "pousser: le rebasage sur origin/main bute sur un conflit, rien poussé — le résoudre à la main (git rebase origin/main)" >&2
        fi
        exit 1
    fi
    # Le paquet a gardé la version de main : il est à refaire avant tout envoi.
    # La marque survit à un hook interrompu ; le tour suivant la reprend.
    [ -z "$le_refait" ] || printf '%s\n' "$le_refait" > "$marque_du_paquet"
fi

# Le paquet à refaire (voir rebaser) : son script le refait des sources
# réunies, et le dernier commit de la session le prend. Tant qu'il n'y est
# pas, rien ne part, ni à ce tour ni aux suivants. Le script lit le
# répertoire de travail : il attend qu'il soit propre, pour qu'une source non
# commitée n'entre pas dans le paquet du commit. Les commits rejoués avant le
# dernier gardent le paquet de main ; GitHub refait de toute façon le paquet
# du dernier.
a_refaire() {
    git ls-files -z | git check-attr -z --stdin refaire \
        | tr '\0' '\n' | paste - - - | awk -F'\t' '$3 != "unspecified" {print $1}'
}
if [ -f "$marque_du_paquet" ]; then
    script=$(head -n 1 "$marque_du_paquet")
    # Un hook interrompu pendant le script laisse un paquet à moitié écrit.
    a_refaire | while IFS= read -r fichier; do
        git checkout --quiet HEAD -- "$fichier" 2>/dev/null || true; done
    if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
        echo "pousser: le paquet est à refaire des sources réunies ($script), et des modifications ne sont pas commitées, rien poussé — les commiter, puis relancer" >&2
        exit 1
    fi
    refait=1
    for python in python3 python; do
        "$python" -c 'import yaml' >/dev/null 2>&1 || continue
        "$python" "$script" >/dev/null 2>&1 && refait=0
        break
    done
    if [ "$refait" != 0 ]; then
        git checkout --quiet -- . 2>/dev/null || true
        echo "pousser: le paquet n'a pas pu être refait des sources réunies, rien poussé — lancer python $script, git add -A, git commit --amend --no-edit, puis bash scripts/pousser.sh" >&2
        exit 1
    fi
    a_refaire | while IFS= read -r fichier; do git add -- "$fichier"; done
    if ! git diff --cached --quiet; then
        if [ "$(git rev-list --count origin/main..HEAD)" -gt 0 ]; then
            git commit --quiet --amend --no-edit >/dev/null 2>&1 || {
                echo "pousser: le paquet refait n'a pas pu entrer dans le dernier commit, rien poussé" >&2; exit 1; }
        else
            git reset --quiet -- . && git checkout --quiet -- .
        fi
    fi
    rm -f "$marque_du_paquet"
fi

tete=$(git rev-parse HEAD)
avance=$(git rev-list --count origin/main..HEAD)

# Aucune adresse nominative ne part sur GitHub. L'auteur et le committer d'un
# commit publié s'y lisent par tous, adresse comprise, et ne s'effacent ensuite
# qu'en réécrivant l'historique entier. Une session web signe
# noreply@anthropic.com ; un poste local signe de l'identité git de la machine,
# et un rebasage — celui de ce script compris — en fait le committer. Ne
# passent que les adresses qui ne désignent personne. `grep -c` lit toute son
# entrée : un `grep -q` sortirait tôt, et sous pipefail le SIGPIPE de `git log`
# ferait passer le commit qu'il vient de trouver.
if [ "$avance" -gt 0 ]; then
    nominatives=$(git log --format='%ae%n%ce' origin/main..HEAD \
        | grep -c -v -E '^(noreply@anthropic\.com|noreply@github\.com|[^@]+@users\.noreply\.github\.com)$')
    if [ "$nominatives" -gt 0 ]; then
        cat >&2 <<'FIN'
pousser: un commit à publier est signé d'une adresse nominative, rien poussé.
Donner au dépôt l'identité anonyme du compte, puis re-signer ces commits :
    git config user.name "g-pliberal"
    git config user.email "240225789+g-pliberal@users.noreply.github.com"
    git rebase origin/main --exec "git commit --amend --no-edit --reset-author"
FIN
        exit 1
    fi
fi

# Le test d'abord (CLAUDE.md, action 162) : un commit qui change le code sans
# toucher aux tests ne part pas, sauf s'il le déclare par une ligne
# `Sans-test: <raison>` de son message — un remaniement, un commentaire. Ce qui
# est du code et ce qui est un test, `.claude/hooks/tdd.py` le sait, qui le
# rappelle déjà à la session avant qu'elle touche au code. Les commits sont ici
# rebasés sur origin/main. Sans Python, rien ne se vérifie.
tdd="$ici/../.claude/hooks/tdd.py"
if [ "$avance" -gt 0 ] && [ -f "$tdd" ]; then
    for python in python3 python; do
        "$python" -c 'import json, re, subprocess' >/dev/null 2>&1 || continue
        sans_test=$("$python" "$tdd" --envoi origin/main..HEAD)
        if [ -n "$sans_test" ]; then
            {
                echo "pousser: un commit à publier change le code sans toucher aux tests, rien poussé (le test d'abord, CLAUDE.md) :"
                printf '%s\n' "$sans_test" | sed 's/^/    /'
                cat <<'FIN'
Lui joindre le test qui dit ce qu'il change, vu échouer puis passer : le
dernier commit se reprend par `git add` du test et
`git commit --amend --no-edit` ; plusieurs se réunissent en un par
`git reset --soft "$(git merge-base origin/main HEAD)"`, puis `git commit`.
Un commit qui ne change aucun comportement (un remaniement, un commentaire)
le déclare dans son message :
    git commit --amend --no-edit --trailer "Sans-test: <raison>"
FIN
            } >&2
            exit 1
        fi
        break
    done
fi

# Les gardes gardées (action 163, étape 6) : les workflows de GitHub, les hooks
# et leurs réglages, ce script et ceux qui poussent sur main depuis GitHub — le
# verdict, et l'inscription des rédactions (action 184) — ne changent
# qu'avec l'accord du propriétaire, demandé avant ; le commit le déclare par une
# ligne `Garde-modifiée: <raison>`. Un ralentisseur, non un verrou : la session
# peut l'écrire seule, mais elle s'arrête, et la trace se liste
# (`git log --grep='^Garde-modifiée:'`). Le message se lit dans une variable, et
# non par un tube, que `pipefail` ferait mentir, comme plus haut.
if [ "$avance" -gt 0 ]; then
    gardes=".github/workflows .claude/hooks .claude/settings.json scripts/pousser.sh scripts/publier_fabrique.sh scripts/publier_inscription.sh"
    declaration=$'(^|\n)Garde-modifiée: *[^[:space:]]'
    sans_accord=""
    # shellcheck disable=SC2086 # les chemins des gardes, un par mot
    for commit in $(git rev-list origin/main..HEAD -- $gardes); do
        message=$(git log -1 --format=%B "$commit")
        if ! [[ $message =~ $declaration ]]; then
            # shellcheck disable=SC2086
            touchees=$(git diff-tree --no-commit-id --name-only -r "$commit" -- $gardes | tr '\n' ' ')
            sans_accord+="    ${commit:0:7} $(git log -1 --format=%s "$commit") : $touchees"$'\n'
        fi
    done
    if [ -n "$sans_accord" ]; then
        {
            echo "pousser: un commit à publier touche une garde du dépôt sans le déclarer, rien poussé (action 163) :"
            printf '%s' "$sans_accord"
            cat <<'FIN'
Une garde ne change qu'avec l'accord du propriétaire, demandé avant. Accordé,
le commit le déclare, la raison non vide :
    git commit --amend --no-edit --trailer "Garde-modifiée: <ce qu'il a accordé>"
FIN
        } >&2
        exit 1
    fi
fi

# La feuille de route tient ses règles (action 163, étape 2) : du 6 au
# 17 octobre 2026, six rouges de main venaient du bloc « Reprise », que la
# session écrit au dernier commit, après ses tests. Quand un commit à publier
# touche la feuille de route ou ses notes, leurs deux tests se jouent ici, en
# une seconde ou deux. Sans Python qui ait pytest, rien ne se vérifie.
if [ "$avance" -gt 0 ] && [ -f tests/test_prose.py ] \
    && [ -n "$(git diff --name-only origin/main..HEAD -- docs/feuille_de_route.md docs/feuille_de_route)" ]; then
    for python in python3 python; do
        "$python" -c 'import pytest' >/dev/null 2>&1 || continue
        if ! sortie=$("$python" -m pytest -q -p no:cacheprovider \
                tests/test_prose.py::test_chaque_action_en_cours_s_ouvre_sur_son_bloc_reprise \
                tests/test_prose.py::test_les_notes_de_la_feuille_de_route_se_rangent_par_action \
                2>&1); then
            {
                echo "pousser: la feuille de route ne tient pas ses règles (le bloc « Reprise », les notes ; CLAUDE.md), rien poussé :"
                printf '%s\n' "$sortie" | grep -E '^(FAILED|ERROR|E  )' | head -n 12 | sed 's/^/    /'
                echo "Corriger, commiter, puis relancer."
            } >&2
            exit 1
        fi
        break
    done
fi

# Le filet des fichiers communs (20 novembre 2026) : deux chantiers verts
# chacun de son côté peuvent être rouges une fois réunis — un compteur de
# cliquet que les deux ont monté, des sorties figées qu'un cas témoin de plus
# décale —, et la suite rapide de la session, jouée avant de rattraper main,
# ne le voit pas. Les tests que nomme `tests/filet_avant_envoi.txt` se jouent
# donc ici, le travail des autres rattrapé, juste avant l'envoi : un lot par
# ligne, les lots de front, sous la minute, le hook `Stop` n'en laissant que
# deux. Rouges, rien ne part. Un envoi qui ne touche que la documentation ne
# les joue pas. Ils lisent le répertoire de travail. Sans Python qui ait
# pytest, rien ne se vérifie.
filet=tests/filet_avant_envoi.txt
if [ "$avance" -gt 0 ] && [ -f "$filet" ] \
    && [ -n "$(git diff --name-only origin/main..HEAD -- . ':(exclude)docs' ':(exclude)*.md')" ]; then
    for python in python3 python; do
        "$python" -c 'import pytest' >/dev/null 2>&1 || continue
        sorties=$(mktemp -d)
        lot=0
        lots=()
        while IFS= read -r ligne || [ -n "$ligne" ]; do
            ligne=${ligne%%#*}
            [ -z "${ligne//[[:space:]]/}" ] && continue
            lot=$(( lot + 1 ))
            # shellcheck disable=SC2086 # les tests d'un lot, un par mot
            "$python" -m pytest -q -p no:cacheprovider $ligne >"$sorties/$lot" 2>&1 &
            lots+=($!)
        done < "$filet"
        rouge=0
        for lot in ${lots[@]+"${lots[@]}"}; do
            wait "$lot" || rouge=1
        done
        if [ "$rouge" = 1 ]; then
            {
                echo "pousser: le filet des fichiers communs est rouge, rien poussé ($filet) :"
                cat "$sorties"/* | grep -E '^(FAILED|ERROR)' | head -n 12 | cut -c1-400 | sed 's/^/    /'
                cat <<'FIN'
Ces tests gardent ce que tous les chantiers écrivent : le travail de la session
et celui que main a reçu entre-temps ne tiennent pas ensemble. Les relancer
(`python -m pytest <le test>`), corriger — un compteur à suivre, des sorties à
refiger —, commiter, puis relancer. Si main est rouge sans la session
(`.github/etat_suite.yaml`), c'est lui qui se répare d'abord.
FIN
            } >&2
            rm -rf "$sorties"
            exit 1
        fi
        rm -rf "$sorties"
        break
    done
fi

if [ "$avance" -gt 0 ]; then
    avec_reprises git push --quiet origin HEAD:main || {
        echo "pousser: push vers main impossible après 5 essais" >&2; exit 1; }
fi

# Faire suivre la référence de la branche de session, pour que le compteur de
# commits non poussés lise zéro. Jamais de création. `ls-remote` distingue les
# trois cas par son code de sortie, et c'est ce qui rend ce bloc sûr : 0 la
# référence est sur GitHub, 2 elle n'y est pas, autre chose le réseau a lâché.
# Sans branche (tête détachée), le code 3 saute les deux blocs.
if [ -n "$branche" ]; then
    git ls-remote --exit-code --heads origin "$branche" >/dev/null 2>&1
    suivi=$?
else
    suivi=3
fi
case $suivi in
    0)
        distant=$(git rev-parse --quiet --verify "refs/remotes/origin/$branche" 2>/dev/null || echo "")
        if [ "$distant" != "$tete" ]; then
            # --force-with-lease : après un rebasage, la référence de session ne
            # descend plus de ce qu'elle portait. Elle ne porte que ce que main
            # porte, et n'appartient qu'à cette session : rien à perdre. Le bail
            # refuse quand même si elle a bougé sous nos pieds.
            avec_reprises git push --quiet --force-with-lease origin "HEAD:refs/heads/$branche" >/dev/null 2>&1 || true
        fi
        ;;
    2)
        # La branche n'est pas, ou n'est plus, sur GitHub — supprimée à la main
        # depuis l'onglet Branches, comme CLAUDE.md le demande. Le script ne la
        # recrée pas : une session ne saurait pas la supprimer (403). Mais le
        # POINTEUR DE SUIVI local, lui, survit à la suppression et reste figé
        # sur le commit du clone ; tout ce qui compte « origin/$branche..HEAD »
        # lit alors une branche entière de retard sur un fantôme. C'est ce qui
        # faisait remonter le compteur malgré le script. On le supprime : le
        # geste est PUREMENT LOCAL, il ne crée ni n'efface rien sur GitHub, et
        # c'est ce que ferait `git fetch --prune`.
        git update-ref -d "refs/remotes/origin/$branche" >/dev/null 2>&1 || true
        ;;
    3)
        : # tête détachée : aucune branche de session
        ;;
    *)
        : # ls-remote a échoué : ne rien conclure de son silence, ne rien toucher.
        ;;
esac

# Et donner à la branche locale l'amont qu'elle n'a pas : sans lui, le compteur
# compare à un point fixe et remonte à chaque commit.
[ -n "$branche" ] \
    && git branch --quiet --set-upstream-to=origin/main "$branche" >/dev/null 2>&1
true

if [ "$avance" -gt 0 ]; then
    echo "main ← ${tete:0:7} ($avance commit(s))"
fi
