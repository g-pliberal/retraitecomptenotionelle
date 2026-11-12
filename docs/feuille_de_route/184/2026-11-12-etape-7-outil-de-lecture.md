# Étape 7 : l'outil de lecture ne déclare que ce qu'une fiche déclare

**Reprise, au 12 novembre 2026.** Rien n'est commencé. La passe de lecture a
trouvé deux défauts à l'outil qui dit quelles rédactions une fiche n'a pas
lues. Le premier : dans une fiche, tout identifiant de rédaction écrit dans
une déclaration « sans effet », son motif compris, reçoit ce statut ; citer
une rédaction pour la comparer la classe donc à tort. Le propriétaire a retenu
la correction : seul l'identifiant déclaré compte. Le second : une rédaction
qu'une fiche déclare sans effet sort de la liste de toutes les autres.
Celui-là n'est pas tranché : la session mesure ce que changerait un statut
tenu fiche par fiche, et le propose. Le test d'abord. Aucune règle du scénario
1 n'est en jeu.

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
