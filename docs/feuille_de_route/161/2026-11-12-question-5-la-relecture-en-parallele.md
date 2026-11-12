# Question 5 : la relecture à côté des lots A à D — en parallèle, une session à la fois, sous quatre règles

**La recommandation.** Oui : la relecture s'ouvre en parallèle des lots A à D,
une seule session de relecture à la fois, la zone grise d'abord. Elle corrige
elle-même ce qui ne déplace aucun résultat, dans les deux fichiers de sa
paire et dans un fichier de tests à elle ; ce qui déplace un résultat, elle
le consigne, et une session à part le corrige quand aucun lot ne tourne.
Chaque note dit à quel commit la paire a été relue : le lot F rouvre par ce
qui a changé depuis. La série ne protégerait rien de plus — le code relu
bouge de toute façon, par les autres actions — et coûterait 12 à 14 sessions
sur le chemin du retrait. Le propriétaire tranche ; rien n'est mis en œuvre
ici.

**La demande.** L'inventaire du 9 novembre
(`2026-11-09-l-inventaire-des-retraits.md`) pose cinq questions au
propriétaire. La cinquième : une session de relecture, qui ne modifie rien
tant qu'elle ne trouve rien, peut-elle s'ouvrir en parallèle des lots A à D,
sur la même zone, quand `CLAUDE.md` partage le dépôt par zones et que
`scripts/pousser.sh` refuse un conflit sur une source ? Cette session
instruit la question ; elle ne relit aucune paire et ne change aucun code.

**La méthode.** L'historique de `main` depuis le 13 octobre 2026 (1 885
commits, lus dans un clone à part, sans leurs fichiers) : les fichiers de
chaque commit, sa session, son heure. Les notes des relectures faites, lues
par l'éclaireur. `scripts/pousser.sh`, `.gitattributes` et les notes de
décision 0003, 0005 et 0006, lus aux passages cités.

## 1. Ce que les relectures faites ont écrit

Dix paires ont été relues du 14 au 28 octobre : le lecteur du relevé, le
lecteur PDF, les crédits des ministères, la table des agrégats, le contexte,
la saisie, le pilote, la carrière, le calendrier, la chronologie.

- **Une relecture trouve presque toujours.** Une seule paire sur dix est
  sortie sans écart, les crédits des ministères. Sept ont mené à une
  correction du code : le relevé, le lecteur PDF, les agrégats, la saisie, la
  carrière, le calendrier, la chronologie. Le contexte n'a changé que d'un
  commentaire ; le pilote a laissé une différence, non corrigée. « Qui ne
  modifie rien tant qu'elle ne trouve rien » décrit donc l'exception.
- **Où les corrections ont écrit.** Dix-neuf commits de correction.
  Dix-sept touchent le JavaScript de la paire ; cinq, son jumeau Python.
  Treize modifient un fichier de tests Python qui existait
  (`tests/test_lecture_pdf.py` sept fois, `tests/test_moteur.py` trois fois,
  `tests/test_chronologie.py` deux fois, `tests/test_releve_lu.py`) ; trois
  fichiers de tests sont créés (`tests/test_saisie_de_l_adresse.py`,
  `tests/js/saisie.test.js`, `tests/js/agregats.test.js`). Aucun ne touche
  `pont.py`, `pont.mjs`, un script de la fabrique ni un témoin.
- **Dans quelle session.** Quatre sessions de relecture ont corrigé
  elles-mêmes (le relevé, le premier défaut du lecteur PDF, la carrière, le
  calendrier avec la chronologie). Trois relectures ont laissé la correction à une session suivante,
  qui l'a faite d'après la note : les défauts communs du lecteur PDF, les
  agrégats (relus le 23, corrigés le 31), la saisie (trois défauts corrigés
  le soir même par une autre session, en trois commits).
- **Les résultats.** Les notes disent qu'aucun témoin des simulations n'a
  bougé : les écarts étaient des refus, des formes, un dernier bit. Seuls les
  défauts communs du lecteur PDF ont déplacé des données lues.

## 2. Ce que les lots A à D écrivent, et où cela croise

Du 16 octobre au 3 novembre, 154 commits de l'action ont fait ce que feront
les lots A, B et D : passer scripts, études et tests par le pont.

| ce qu'ils touchent | commits sur 154 | une correction de relecture y écrit-elle ? |
|---|---:|---|
| les tests | 91 | oui, si elle ajoute son test à un fichier qui existe |
| `pont.py`, `pont.mjs` | 58 | jamais (0 sur 19) |
| le Python hors du pont | 34 | le jumeau de sa paire seulement |
| les scripts | 29 | jamais |
| une règle de `moteur/js/` | 26 | toujours |
| un témoin | 3 | jamais |

Des 26 commits qui touchent une règle JavaScript, dix tiennent à une
relecture et six à un retrait ; dix seulement viennent du passage par le
pont : la bibliothèque mathématique commune, un alignement au bit près, puis
des leviers et des paramètres (`config.js`, `compte.js`,
`scenario-notionnel.js`, `simulateur.js`, `regimes.js`, `pilote.js`).

- **Lots A et B** : des scripts, le pont, `castypes.py`. Ils ne croisent une
  relecture nulle part, sauf par leur preuve (ci-dessous).
- **Lot D** : les fichiers de tests, un à un. Le croisement est le fichier de
  tests où la relecture ajouterait le sien, pendant que le lot D le porte.
- **Lot C** : il récrit les paires de la zone grise elles-mêmes. Relire
  `impot_revenu.py` pendant qu'une session le défait serait le vrai conflit.
  Et la note 0006 fait de la relecture un préalable : « Le propriétaire
  tranche chaque paire à sa relecture » (ligne 106).
- **Les fichiers fabriqués** ne font pas de conflit : `.gitattributes` les
  marque `-merge`, `pousser.sh` garde la version de `main` au rebasage, et
  GitHub les refait. Les chiffres ancrés de la prose se règlent de même.
- **Le croisement qui reste est la preuve.** Les lots A, B et D se prouvent
  par des fichiers fabriqués identiques à l'octet. Une correction qui déplace
  un résultat, poussée pendant qu'un lot tourne, mêle son effet au sien dans
  le commit de GitHub ; et la note 0003 veut que « ses témoins changent dans
  un commit à elle ».

`pousser.sh` ne refuse que le conflit textuel : deux sessions qui modifient
des passages différents d'un même fichier sont rebasées sans rien demander
(ses lignes 73 à 115).

## 3. Les précédents

- **Le 28 octobre, deux relectures ont couru ensemble**, dans une vague de
  dix-sept sessions : la carrière, et le calendrier avec la chronologie. Sept
  commits entrelacés en trente-deux minutes, de 10 h 12 à 10 h 44. Les deux
  sessions ont écrit dans `tests/test_moteur.py` et récrit le même bloc
  « Reprise ». Tout est arrivé sur `main` ; aucune note ne relate de conflit.
- **Le 24 octobre**, une dizaine de sessions de l'action se sont suivies,
  des tests par le pont aux retraits ; une relecture (la saisie) s'y est glissée, et ses
  trois défauts ont été corrigés par une autre session le soir.
- **Le 31 octobre**, deux étapes de l'action ont tourné ensemble, les
  témoins par le portage et les deux paires de données, « en parallèle […]
  que mène une autre session » : leurs notes ne relatent aucun incident.
- **La règle des zones n'est déjà plus « une session sur le modèle »** : le
  3 novembre, 21 sessions distinctes ont touché `moteur/js/` ou `src/` ; le
  5 novembre, 15.
- **L'incident que relate `docs/archives/conventions.md`** est celui du
  19 septembre : les fichiers que toutes les sessions écrivaient (la feuille
  de route dans 38 commits sur 60, `pages.json` dans 18). L'action 148 l'a
  défait : une note par session, les fichiers fabriqués à GitHub.
- **Les actions 130, 158, 175, 177 et 178 séparent déjà relecture et
  correction**, du 3 au 6 novembre, d'après les titres de leurs commits : une
  session relit et consigne ses écarts, une session suivante les reprend.
  Aucun des 94 commits qui nomment une de ces relectures ne touche
  `moteur/js/` ni `src/`.

## 4. Les règles qui rendent le parallèle sûr

1. **Une seule relecture à la fois.** Elle suffit : 12 à 14 sessions de
   relecture tiennent derrière les 18 à 27 des lots A à D, qui se suivent.
   Une deuxième n'ôterait rien au chemin et doublerait les croisements.
2. **La zone grise d'abord**, avant que le lot C n'ouvre chacune de ses
   lignes : `garantie.py`, `impot_revenu.py`, `restitution.py`, la
   revalorisation servie, les variantes des comptes. Les lots A et B, qui
   s'ouvrent les premiers, ne touchent aucun de ces fichiers. Ensuite le
   moteur, les paires les moins couvertes par la concordance en tête ;
   en dernier celles où le pont ajoute encore des paramètres (`config`,
   `compte`, `scenarios/notionnel`, `simulateur`).
3. **Ce qu'elle corrige, ce qu'elle laisse.** Elle corrige elle-même, test
   d'abord, ce qui ne déplace aucun résultat : dans les deux fichiers de sa
   paire, et dans un fichier de tests neuf, à elle — jamais dans un fichier
   de tests qui existe, ni dans le pont, ni dans un script. Ce qui déplace un
   témoin, ou change une règle du scénario 1, elle le consigne dans sa note,
   test rouge décrit ; une session à part le corrige, entre deux sessions
   des lots, avec la veille du droit que `CLAUDE.md` exige.
4. **Chaque note date sa relecture** : pour chaque paire, le commit auquel
   elle a été lue. La relecture ne récrit pas le bloc « Reprise » de
   l'action ; le lot tient le sien sous le titre de sa note, comme le veut
   `.claude/rules/documentation.md` pour des étapes menées en parallèle.

**Le gain.** En série, 30 à 41 sessions séparent aujourd'hui du lot F ; en
parallèle, 18 à 27. Le gain est de 12 à 14 sessions sur ce chemin, entre un
tiers et deux cinquièmes. Et la relecture est, avec les lots A et B, le seul travail qui
n'attend aucune décision du propriétaire.

## 5. Une relecture faite avant le lot D vaut-elle encore au lot F ?

Pas telle quelle, et la série n'y changerait rien. Le code relu bouge, mais
surtout par les autres actions. Depuis le 29 octobre, les fichiers de
`moteur/js/`, `pages.js` à part, ont été touchés 134 fois : 17 par
l'action 161, 117 par les autres ; 39 fichiers sur 79, dont
`droit/liquider.js` onze fois et `droit/acquerir.js` neuf. `carriere.js`, relu le 28 octobre, a reçu
quatorze commits depuis, et `carriere.py` onze ; `chronologie.js`, trois.
Le lot D, lui, récrit des tests, non des règles.

Ce qui tient la relecture jusqu'au retrait, c'est donc autre chose que sa
date :

- tant que le Python vit, toute règle qui change s'écrit des deux côtés, et
  la concordance au bit près la tient (note 0005) ;
- au lot F, pour chaque paire, la différence depuis le commit de sa
  relecture se relit seule (`git diff <commit> -- <les deux fichiers>`) :
  quelques dizaines de lignes, non le fichier.

Aujourd'hui, rien ne garde ce commit : `scripts/jumeaux.py` ne sait pas
qu'une paire est relue, et la colonne « relue » de l'inventaire a été refaite
à la lecture des cinquante notes. D'où la règle 4.

Relire avant le lot D a même un avantage : les tests portés tournent alors
sur un portage déjà corrigé.

## Ce qui est vérifié, ce qui est déduit

**Vérifié dans l'historique** : les fichiers de chaque commit de correction ;
les 154 commits et ce qu'ils touchent ; les sessions du 24, du 28 et du
31 octobre, par la ligne `Claude-Session` de leurs commits ; les comptes du
3 et du 5 novembre ; les commits reçus par les paires relues. **Vérifié en
lisant** : `pousser.sh`, `.gitattributes`, les notes 0003, 0005 et 0006 aux
lignes citées. **Rapporté des notes, par l'éclaireur** : ce que chaque
relecture a trouvé, de quel côté, et qu'aucun témoin n'a bougé.

**Déduit** : qu'une correction sans effet sur les résultats ne gêne pas la
preuve d'un lot ; l'ordre des groupes ; le gain, tiré des nombres de sessions
de l'inventaire, eux-mêmes déduits ; que la différence à relire au lot F
sera courte.

**Non vérifié** : si `pousser.sh` a refusé un envoi ces jours-là — un refus
ne laisse pas de trace dans l'historique, seules les notes en parleraient ;
ce que les commits de GitHub ont refait après chaque correction, que les
envois des autres sessions brouillent ; la part des 35 paires à relire dont
une correction déplacera un résultat — les dix premières n'en ont donné
aucune dans les simulations, mais aucune n'était de `droit/`.

**Ce qui ne change pas.** Aucun code, aucun test, aucune donnée, aucune
garde, aucun fichier commun : cette note seule.
