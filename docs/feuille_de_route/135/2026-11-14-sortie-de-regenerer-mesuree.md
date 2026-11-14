# La sortie de `regenerer.py` mesurée : elle tient dans la queue de trente lignes

**Le 14 novembre 2026, la demande.** La session d'orchestration confie cette
étape (C3, troisième vague) : la note
`2026-11-14-queue-de-regenerer-et-du-resume.md` avait lu dans le code, sans
le lancer, que `python scripts/regenerer.py` réussi peut écrire jusqu'à
quarante-cinq lignes — onze étapes, une ligne et trois de détail chacune —,
dont la queue de trente que pose le hook de Bash perdrait le début. Mesurer
d'abord ; ne corriger que si la sortie dépasse.

**La mesure**, la queue contournée (`> fichier 2>&1`, puis `wc -l`), sur
`2b51c11`, dans un clone frais :

- *à froid*, sans la mémoire des fabrications : **23 lignes**, 448 s. Le
  paquet en écrit quatre, les témoins trois, l'inventaire, les régimes, le
  chiffrage, les pages, la prose et la conservation deux, l'accueil, les
  tableaux et le tableau de bord une seule — leurs scripts ne disent rien
  quand ils réussissent —, plus « tout est régénéré ».
- *juste après*, la mémoire servant : **20 lignes**, 20 s ; les étapes
  dispensées disent « inchangé depuis la dernière fabrication ».

Les deux fois, `git status` est resté vide : rien à remettre à `HEAD`.

**Conclusion : rien à corriger.** Les quarante-cinq lignes sont une borne,
qu'il faudrait que les onze étapes atteignent ensemble ; trois d'entre elles
n'écrivent rien en réussissant, et la sortie réelle laisse sept lignes de
marge sous trente. Ni `regenerer.py` ni le hook ne changent.

**Ce qui n'est pas mesuré.** Une régénération en échec écrit toute la sortie
de l'étape fautive, sans borne ; la queue en garde alors la fin, et la
dernière ligne, sur stderr, nomme les étapes en échec. Un jour où un script
gagnerait des lignes de succès, la marge fondrait sans qu'aucun test le dise.

**Publié par l'orchestration.** La session de C3 n'avait pas le dépôt dans
ses sources, et n'a pu pousser (403 du proxy git) : la session
d'orchestration a publié sa note telle qu'elle l'a rendue.
