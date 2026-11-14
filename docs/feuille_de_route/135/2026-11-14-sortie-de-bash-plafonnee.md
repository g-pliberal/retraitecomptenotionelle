# La sortie de Bash plafonnée à 10 000 caractères

**Le 14 novembre 2026**, sur une piste que la session d'orchestration a tirée
de la documentation de Claude Code, et que le propriétaire a retenue
(« Faisons 1 et 2 dans un session pour chaque ») : faire de la règle « Les
sorties longues passent par `tail` ou `grep` » une garde. `.claude/settings.json`
porte désormais `"bashOutputMaxChars": 10000`.

**Ce que dit la documentation**, lue ce jour en Markdown brut.

- `settings-reference.md`, « bashOutputMaxChars » : un entier positif, que
  Claude Code ramène entre 4 000 et 128 000 ; sans lui, 30 000. Il se pose
  dans n'importe quel fichier de réglages, celui du dépôt compris, et fait
  taire la variable `BASH_MAX_OUTPUT_LENGTH`. Il demande Claude Code 2.1.261 ;
  les sessions web tournent sur la 2.1.325. La page ne dit rien des agents.
- `tools-reference.md`, « Output limits » : d'une commande réussie qui passe
  le plafond, la session reçoit les 2 000 premiers caractères et le chemin
  d'un fichier, dans le dossier de la session, où lire ou chercher le reste.
  D'une commande qui échoue, elle reçoit 10 000 caractères au plus, sans
  fichier : un extrait du début et de la fin, pris dans ce que Claude Code
  relit de la sortie. Or le réglage fixe aussi cette longueur relue.

**La mesure**, sur `main` à 076d380, de ce qu'une session lit en entier.

| Commande | Caractères |
|---|---|
| `python scripts/reprise.py` | 4 164 |
| `python scripts/reprise.py 135` | 4 331 |
| `python scripts/veille_droit.py` | 5 216 |
| `python -m pytest -m rapide 2>&1 \| tail -n 30` | 2 401 |
| `python scripts/tableau_de_bord.py` | 0 : il écrit `docs/etat.md` |
| `bash scripts/pousser.sh`, rien à publier | 0 |
| `bash scripts/pousser.sh`, un commit publié | 31 |

`reprise.py <numéro>`, lancé sur les vingt-huit actions en cours, rend moins
de 7 708 octets pour vingt-six d'entre elles, la 175 en tête. Le plafond est
posé au-dessus, avec un tiers de marge : 10 000, qui est aussi ce qu'une
commande en échec rendait déjà.

**Deux sorties dépassent nettement, et le plafond n'est pas relevé pour
elles** : `reprise.py 186`, 17 858 octets, et `reprise.py 138`, 21 125 octets
(20 466 caractères). La session de ces actions n'en reçoit plus que les 2 000
premiers caractères — le titre, le bloc de l'action et le début de la liste
des notes — et lit la suite dans le fichier, par fenêtres. Le remède est celui
que la note « `reprise.py` en sommaire » laissait déjà : ôter les blocs des
étapes finies, seize à la 138.

**Constaté dans cette session**, le réglage étant relu sans la rouvrir.

- Une commande réussie de 11 700 caractères revient en « Output too large
  (11.7KB) », le chemin du fichier, puis un aperçu de 2 Ko. Le plafond agit.
- Une commande de 25 000 caractères qui sort en code 1 revient réduite à ses
  10 000 premiers caractères, coupés au milieu d'une ligne, sans la fin, sans
  fichier et sans un mot qui le dise. Un `pytest` nu qui échoue perd donc son
  résumé, que le défaut de 30 000 aurait le plus souvent gardé : c'est le prix
  du réglage, et une raison de plus de finir par `| tail -n 30`, qui rend le
  code de `tail` et non celui du test.

**Non vérifié** : que le plafond vaut pour les agents, dont la documentation
ne dit rien ; ce que rendait une commande en échec avant le réglage, repris
de la documentation et non essayé. Une session neuve peut le revoir par
`python3 -c "print('x' * 12000)"`.

**Les tests**, vus rouges avant le réglage.
`test_la_sortie_d_une_commande_bash_est_plafonnee`
(`tests/test_reglages_claude.py`) tient la valeur, l'absence de la variable et
le chiffre de `CLAUDE.md`, ancré sur lui.
`test_sans_numero_reprise_n_imprime_qu_un_sommaire` (`tests/test_prose.py`)
tient d'accord le réglage et `SORTIE_AU_PLUS` de `scripts/reprise.py`, qui
passe de 30 000 à 10 000 ; le sommaire du dépôt doit tenir sous les trois
quarts du plafond, et non plus sous la moitié de 30 000.

**Les documents** : la puce de `CLAUDE.md`, une ligne de plus, à 197.
