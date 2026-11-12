# Étape 7 : l'outil de lecture ne déclare que ce qu'une fiche déclare

**Reprise, au 12 novembre 2026.** Le premier défaut est corrigé : dans une
fiche, une déclaration « sans effet » ne vaut plus que pour la rédaction
qu'elle déclare, et son motif n'est plus lu. Le second attend le
propriétaire : aujourd'hui, une rédaction qu'une fiche déclare sans effet sort
de la liste de toutes les autres fiches. La mesure est faite, plus bas : tenir
ce statut fiche par fiche ferait revenir 79 lignes dans les listes de 25
fiches, dont une seule rédaction en vigueur, sans toucher au compte des
rédactions sans statut. La recommandation est de le tenir fiche par fiche. Si
le propriétaire la retient : le test d'abord, dans `tests/test_textes.py`,
puis `non_lues`, dans `noyau/textes.py`. S'il garde le statut commun, l'étape
est close, et ce bloc s'ôte. Aucune règle du scénario 1 n'est en jeu.

**La demande, le 12 novembre 2026.** Les quatre lots de l'étape 6 ont relevé
ces défauts (note `2026-11-12-etape-6-bilan-de-la-passe.md`, « Deux défauts de
l'outil »). La session d'orchestration avait écrit au propriétaire que l'outil
« ne devrait pas lire les identifiants d'un motif », et lui avait soumis les
deux remèdes des lots : un contrôle qui refuse un identifiant étranger dans un
motif, ou un statut tenu fiche par fiche. Sa réponse : « Pour les décisions à
trancher : je choisis tes recommandations ». La recommandation ne portait que
sur le motif ; sur le statut commun, la session d'orchestration n'en avait
donné aucune, et rien n'est donc décidé.

**Ce qui est su.** `noyau/textes.py` : `_identifiants` lit toutes les valeurs
d'une entrée ; `statuts` garde pour chaque rédaction le statut le plus établi,
toutes fiches confondues ; `non_lues` s'en sert. Trois rédactions sont « sans
effet » en statut commun alors qu'une fiche les garde à rattacher : articles
L. 613-9 (`micro_social_abattement`), R. 351-39 (`trimestres_avant_1972`) et
R. 711-1 (`un_statut_par_annee`). Le lot du code de la sécurité sociale a
corrigé à la main un motif fautif (commit 43a19f1) ; les autres lots ont
vérifié les leurs.

**Ce qu'il y a à faire.**

1. Le test, vu rouge : un motif qui nomme une autre rédaction par son
   identifiant ne lui donne aucun statut. Puis le code : seul l'identifiant
   que l'entrée déclare compte. Vérifier que le compte des rédactions sans
   statut de `perimetre.yaml` ne bouge pas à tort ; s'il doit remonter, le
   dire, puisqu'il ne fait d'ordinaire que décroître.

2. Mesurer, sans rien changer : combien de rédactions une fiche a déclarées
   sans effet alors qu'une autre fiche cite le même article, et ce que
   deviendraient les listes et le compte si le statut « sans effet » ne valait
   que pour la fiche qui le déclare.

3. Rendre cette mesure à la session d'orchestration, avec une recommandation,
   pour le propriétaire.

**Fini quand** le premier défaut est corrigé et testé, et que le second est
une question posée au propriétaire, chiffres à l'appui.

## Ce qui a été fait, le 12 novembre 2026

**Le premier défaut, corrigé.** Le test d'abord, vu rouge
(`test_un_motif_sans_effet_ne_declare_pas_la_redaction_qu_il_nomme`) : un
motif qui nomme une autre rédaction lui donnait « sans effet ». Le code
(`_declares`, dans `src/retraite_notionnelle/noyau/textes.py`) : une entrée de
`textes_sans_effet` déclare son `id` ; faute d'`id`, les rédactions que nomme
sa `reference` — la forme des onze entrées de `decote_regimes_speciaux`, qui
en déclarent trente-quatre. Ni le motif ni un autre champ ne sont lus. Les
autres listes d'une fiche gardent leur lecture large, que la décision ne
visait pas, et dont les versions se servent : dix-huit identifiants y sont
dans un champ `article`, cinq dans une `citation`.

**Ce que la correction déplace.** Cinq motifs nommaient une autre rédaction.
Trois d'entre elles tiennent leur statut d'ailleurs, et ne bougent pas. Deux
bougent :

- l'article 2 du décret n° 2019-632 (LEGIARTI000038680034, en vigueur) passe
  de « sans effet » à « à rattacher ». Un motif de
  `assiette_minimale_independants`, écrit pour L. 613-9, le nommait ; la même
  fiche le cite dans une lecture, sans l'avoir coupé en version. Le statut
  d'avant était faux ;
- D. 732-76 du code rural, rédaction du 1er janvier au 9 mai 2026
  (LEGIARTI000053365504), n'était déclaré que par le motif de la rédaction
  suivante, dans `retraite_proportionnelle_msa` : « celle du 1er janvier au 9
  mai 2026 […], qui n'en diffère que par la note d'application ». Il perdait
  tout statut, et le compte des rédactions sans statut remontait de 9 236 à
  9 237. La fiche disait bien l'avoir lu : il y reçoit sa propre entrée, des
  mots mêmes de la fiche, et le compte reste à 9 236. C'est la seule ligne
  écrite hors de `noyau/textes.py` et de ses tests ; l'index des lois n'est
  pas dans le conteneur, et le mot à mot n'a pas été relu.

Les listes des rédactions non lues ne bougent pas : 2 432 lignes, sur 169
fiches. Les statuts : 152 rédactions sans effet au lieu de 153, 628 à
rattacher au lieu de 627.

## La mesure : le statut « sans effet » tenu fiche par fiche

Rien n'est changé ici. Mesuré sur `main` après la correction, par les
fonctions de `noyau/textes.py` : une rédaction ne sort de la liste d'une fiche
que si une version la rattache, ou si la fiche elle-même la nomme.

**L'état d'aujourd'hui.** 197 rédactions sont déclarées sans effet par une
fiche au moins, en 203 déclarations. 45 sont rattachées par une autre fiche,
et ce statut l'emporte. Les 152 autres sont « sans effet » pour toutes les
fiches. Neuf d'entre elles, et non trois, sont gardées « à rattacher » par une
autre fiche, dont cinq en vigueur : L. 613-9, R. 351-39 et R. 711-1 du code de
la sécurité sociale, L. 13 et R. 13 du code des pensions civiles et militaires
de retraite, puis quatre rédactions passées (D. 161-2-1-9, L. 731-42 du code
rural, les articles 85-1 et 85-2 du décret n° 90-1215).

**Ce que le statut par fiche changerait.**

| | aujourd'hui | fiche par fiche |
|---|---|---|
| lignes des listes de rédactions non lues | 2 432 | 2 511 (+ 79) |
| fiches qui ont une liste | 169 | 179 |
| fiches que la veille dit à relire pour une rédaction en vigueur | 0 | 1 |
| rédactions sans statut (le cliquet) | 9 236 | 9 236 |

- 22 rédactions sur 152 reviennent, dans les listes de 25 fiches : 79 lignes.
  Les 130 autres ne reviennent nulle part : aucune autre fiche ne cite leur
  article sans les nommer.
- Une seule est en vigueur : L. 382-25 du code de la sécurité sociale,
  rédaction du 1er janvier 2026 (LEGIARTI000051289014), que
  `cultes_salaire_annuel_moyen` déclare sans effet, revient chez
  `taux_plein_a_soixante_cinq_ans`. La veille compterait cette fiche à relire.
- 78 lignes sont des rédactions passées, que l'outil ne montre qu'avec
  `--toutes` et que la veille ne compte pas.
- 49 lignes tiennent à cinq rédactions qui n'ont jamais été en vigueur, dont
  quatre de l'annexe 3 du statut des industries électriques et gazières
  (décret n° 46-1541), que douze fiches citent chacune pour une autre règle.
  Sans elles, il reste 30 lignes, 17 rédactions, 15 fiches.
- Le cliquet ne bouge pas : il compte les rédactions qu'aucune fiche ne
  nomme, et une rédaction déclarée par une fiche garde un statut.
- Les neuf rédactions qu'une fiche dit sans effet et qu'une autre garde à
  rattacher restent « sans effet » dans le statut commun, celui que le tableau
  de bord compte : le statut par fiche ne corrige que les listes.

**Une borne, pour comparer.** Tenir aussi « rattachée » fiche par fiche ferait
revenir 1 047 lignes, dont 80 en vigueur. Ce n'est pas proposé.

## La recommandation, pour le propriétaire

Tenir « sans effet » fiche par fiche dans les listes de rédactions non lues.

- La définition le dit déjà : une fiche déclare une rédaction « sans effet sur
  elle » (`docs/architecture.md`, § 6.6). Le motif ne parle que de sa règle.
  L'annexe 3 du statut des industries électriques et gazières le montre :
  `decote_regimes_speciaux` y lit la décote, et ne dit rien de la réversion ni
  du minimum de pension, que d'autres fiches lisent dans le même article.
- Le coût est mesuré et petit : 79 lignes de plus sur 2 432, une fiche à
  relire. Une rédaction qui revient se déclare sans effet d'une ligne, ou se
  rattache.
- Le cliquet ne bouge pas, et aucun compte ne remonte.
- « Rattachée » reste commun : le modèle porte déjà la rédaction, et la borne
  est treize fois plus haute.

Une seconde question, liée, que la mesure a fait voir : dans le statut commun,
« sans effet » passe avant « à rattacher ». Neuf rédactions comptent donc
comme lues alors qu'une fiche doit encore les couper en version. Mettre « à
rattacher » avant « sans effet » en ferait passer neuf de l'un à l'autre au
tableau de bord (143 et 637, au lieu de 152 et 628), sans toucher au cliquet.
C'est recommandé aussi, et se décide à part.

Aucune entrée au journal de veille : aucun texte n'a été lu.
