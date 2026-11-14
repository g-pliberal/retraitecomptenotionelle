#!/usr/bin/env bash
# Publie ce que GitHub vient de fabriquer, et le verdict de la suite.
#
# Lancé par `.github/workflows/tests.yml`, après `regenerer.py` et la suite
# complète (action 148, étape 1) : les sessions ne régénèrent plus avant
# d'envoyer, GitHub refait les fichiers fabriqués sur le dernier main. Ce
# script écrit le verdict dans `.github/etat_suite.yaml` — que le hook
# `SessionStart` affiche à l'ouverture de chaque session, sans API GitHub —,
# le commite sous l'identité noreply du robot, avec les fichiers fabriqués si
# la suite est verte, et le pousse SANS FORCER. Si une session a envoyé pendant
# la course, il publie le verdict seul, sur la tête qui a dépassé ses sources
# (action 135) : les fichiers refaits ne valent que pour l'arbre de la course,
# et la suivante, qu'a lancée cet envoi, les refera ; le verdict, lui, tient à
# ses sources, que le hook compare à la tête. Le verdict d'une autre course,
# publié de même, n'est pas un envoi : il ne retient ni les fichiers ni le site.
#
# Entrées : FABRICATION et SUITE, l'issue des deux étapes (success ou autre) ;
# SORTIE_SUITE, le fichier où la suite a écrit ; COURSE, l'adresse de la course ;
# GARDE et SORTIE_GARDE, l'issue et la sortie de la garde des présomptions
# (action 135, levier 2), dont le verdict s'écrit à part : une garde rouge ne
# retient pas les fichiers fabriqués, justes si la suite est verte ; DUREES, ce
# que chaque étape a duré, en secondes (`fabrique=470 suite=2162 garde=175`),
# que le verdict porte : une course qui s'allonge se voit ; DUREES_SUITE, le
# tableau de ce que chaque fichier de tests a duré (`scripts/durees_suite.py`),
# que la course ne passe que partie sans mémoire des calculs, et qui se publie
# alors comme le verdict, dans `.github/durees_suite.tsv`.
#
# Sortie : `en_ligne=oui` dans GITHUB_OUTPUT quand une suite verte sur main est
# poussée avec ses fichiers, et alors seulement : `tests.yml` met le site en ligne (action 163).
# Chaque verdict s'inscrit aussi au journal, `.github/verdicts.tsv`, une ligne
# par course publiée, où `tableau_de_bord.py --cout` compte les rouges.

set -euo pipefail

branche=${GITHUB_REF_NAME:?}
source=$(git rev-parse HEAD)
# L'issue de l'étape ne suffit pas : un tube sans pipefail l'a dite réussie
# onze courses de suite, le 7 octobre 2026, sur jusqu'à six échecs. Un échec
# que la sortie nomme rend la suite rouge.
if grep -qE '^(FAILED|ERROR) ' "${SORTIE_SUITE:-/dev/null}" 2>/dev/null; then
    SUITE=echecs_dans_la_sortie
fi
garde=
if [ -n "${GARDE:-}" ]; then
    garde=vert
    if [ "$GARDE" != success ] \
        || grep -qE '^(FAILED|ERROR) ' "${SORTIE_GARDE:-/dev/null}" 2>/dev/null; then
        garde=rouge
    fi
    [ "$GARDE" = skipped ] && garde=non_jouee
fi
etat=vert
if [ "${FABRICATION:-}" != success ] || [ "${SUITE:-}" != success ]; then
    etat=rouge
    # Une suite rouge ne publie aucun fichier fabriqué : seulement son verdict.
    git checkout -- .
    git clean -fdq
fi

fichier=.github/etat_suite.yaml
journal=.github/verdicts.tsv
tableau=.github/durees_suite.tsv
quand=$(date -u +%Y-%m-%dT%H:%M:%SZ)
durees=
for paire in ${DUREES:-}; do
    case "${paire#*=}" in
        '' | *[!0-9]*) ;;
        *) durees="$durees  ${paire%%=*}: ${paire#*=}"$'\n' ;;
    esac
done

ecrire_le_verdict() {
    {
        echo "# Le verdict de la dernière course de tests.yml : écrit par GitHub"
        echo "# (scripts/publier_fabrique.sh), jamais à la main. Action 148."
        echo "etat: $etat"
        echo "sources: $source"
        echo "date: $quand"
        echo "course: ${COURSE:-}"
        if [ "$etat" = rouge ]; then
            echo "echecs:"
            if [ "${FABRICATION:-}" != success ]; then
                echo "  - \"scripts/regenerer.py a échoué\""
            fi
            grep -E '^(FAILED|ERROR) ' "${SORTIE_SUITE:-/dev/null}" 2>/dev/null \
                | head -n 30 | sed 's/"/\\"/g; s/^/  - "/; s/$/"/' || true
        fi
        if [ -n "$garde" ]; then
            echo "presomptions: $garde"
        fi
        if [ "$garde" = rouge ]; then
            echo "presomptions_echecs:"
            grep -E '^(FAILED|ERROR) ' "${SORTIE_GARDE:-/dev/null}" 2>/dev/null \
                | head -n 30 | sed 's/"/\\"/g; s/^/  - "/; s/$/"/' || true
        fi
        if [ -n "$durees" ]; then
            echo "durees:"
            printf '%s' "$durees"
        fi
    } > "$fichier"
    printf '%s\t%s\t%s\t%s\n' "$quand" "${source:0:7}" "$etat" "$garde" >> "$journal"
    if [ -n "$durees_suite" ]; then
        cp "$durees_suite" "$tableau"
    fi
}

# Le tableau des durées se lit avant que l'arbre ne se remette à la tête.
durees_suite=
if [ -s "${DUREES_SUITE:-}" ]; then
    durees_suite=$(mktemp)
    cp "$DUREES_SUITE" "$durees_suite"
fi

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

# Le commit se bâtit sur la tête de la branche, et se pousse sans forcer ; si
# elle avance au moment de pousser, il se rebâtit sur la nouvelle. Dépassée
# par un envoi — autre chose que le verdict d'une course —, la course ne
# publie plus que son verdict, et le reste jusqu'au bout.
depassee=non
pousse=non
for essai in 1 2 3 4 5; do
    git fetch --quiet origin "$branche"
    tete=$(git rev-parse FETCH_HEAD)
    if ! git diff --quiet "$source" "$tete" -- . \
            ":(exclude)$fichier" ":(exclude)$journal" ":(exclude)$tableau"; then
        depassee=oui
    fi
    if [ "$depassee" = oui ]; then
        git reset --quiet --hard "$tete"
        git clean -fdq
    else
        git reset --quiet --soft "$tete"
        for verdict in "$fichier" "$journal" "$tableau"; do
            if git cat-file -e "$tete:$verdict" 2>/dev/null; then
                git checkout --quiet "$tete" -- "$verdict"
            else
                git rm --quiet --cached --ignore-unmatch -- "$verdict"
                rm -f "$verdict"
            fi
        done
    fi
    ecrire_le_verdict
    git add -A
    fabriques=$(git diff --cached --name-only \
        | { grep -v -x -e "$fichier" -e "$journal" -e "$tableau" || true; } | wc -l)
    if [ "$etat" = rouge ]; then
        titre="Suite ROUGE sur ${source:0:7} : voir .github/etat_suite.yaml"
        [ "$depassee" = oui ] && titre="$titre ; $branche l'a dépassée"
    elif [ "$depassee" = oui ]; then
        titre="Suite verte sur ${source:0:7}, que $branche a dépassée : le verdict seul"
    else
        titre="Fabriqué par GitHub : suite verte sur ${source:0:7}, $fabriques fichier(s) refait(s)"
    fi
    if [ "$garde" = rouge ]; then
        titre="$titre ; garde des présomptions ROUGE"
    fi
    git commit --quiet -m "$titre" -m "${COURSE:-}"
    if git push --quiet origin "HEAD:refs/heads/$branche"; then
        pousse=oui
        break
    fi
    git fetch --quiet origin "$branche"
    if [ "$(git rev-parse FETCH_HEAD)" = "$tete" ]; then
        echo "::error::Poussée refusée. Réglage : Settings → Actions → General → Workflow permissions → « Read and write permissions » ; et, si main est protégée, y autoriser GitHub Actions."
        exit 1
    fi
    echo "::notice::$branche a avancé au moment de pousser (essai $essai) : le commit se refait sur sa nouvelle tête."
done
if [ "$pousse" != oui ]; then
    echo "::error::$branche a avancé à chacun des cinq essais : verdict non publié."
    exit 1
fi
if [ "$depassee" = oui ]; then
    echo "::notice::$branche a été dépassée pendant la course : le verdict seul est publié, la course suivante refait les fichiers."
fi
echo "$branche ← $(git rev-parse --short HEAD) ($etat, $fabriques fichier(s) fabriqué(s))"
if [ "$etat" = vert ] && [ "$branche" = main ] && [ "$depassee" = non ]; then
    echo "en_ligne=oui" >> "${GITHUB_OUTPUT:-/dev/null}"
fi
