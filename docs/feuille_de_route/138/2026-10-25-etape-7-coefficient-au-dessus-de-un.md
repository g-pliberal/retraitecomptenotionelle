# Étape 7, dix-septième partie : le coefficient tout juste au-dessus de un, aux pages

**La demande.** Lot du 25 octobre 2026, neuvième vague : une session par
tâche, menée sans le propriétaire ; celle-ci, les deux restes de l'action 138
aux pages, rangés sous la section « Naissances et migrations » de la page Coût
(`cout-demographie`) — de l'étape 7, les décimales du coefficient de 2070 tout
juste au-dessus de un (douzième partie, point 2, note « ex-invalides de la
Cnav ») ; de sa septième partie (note « naissances et migrations dans les
pages »), la phrase de l'ex-invalide, avec sa mortalité. Laissés au
propriétaire : la table des poids et sa phrase du partage, le rapport de
dépendance, les départs qui suivent l'espérance de vie. Aucune règle du
scénario 1 n'est en cause : ni veille du droit, ni entrée au journal.

**La phrase de l'ex-invalide était faite.** Le bloc de la septième partie,
récrit le 19 octobre avant la quatorzième, la laissait aux pages ; la
quatorzième partie (note « mortalité des ex-invalides et inapte recalé »)
l'avait écrite le même jour, avec sa mortalité. Le dépliant « Les quatre
systèmes comparés, du passé jusqu'à 2070 » dit : « Le salarié reconnu inapte
au travail et le salarié ex-invalide, comptés avec le salarié au SMIC dans le
dépliant « Ce que chaque carrière type pèse dans ces chiffres », survivent,
eux, l'un au rythme des inaptes de la Cnav, l'autre au rythme de ses
ex-invalides. » ; `test_la_page_cout_dit_au_rythme_de_qui_chaque_cas_type_survit`
(`test_web.py`) le tient, l'ex-invalide dans `nommees`. La surmortalité par
tranche d'âge (seizième partie, 24 octobre) ne la dément pas : les deux cas
types vivent toujours au rythme de ces deux populations, à chaque âge que la
Cnav publie. Rien n'y est changé.

**Le coefficient au-dessus de un** (`moteur/js/pages.js`).

- *Ce que les pages écrivaient.* Sous un, `decimalesSousUn` donnait au
  coefficient les décimales qui l'empêchaient de s'écrire 1,00 ; au-dessus,
  deux. À 1,0013, le 19 octobre, Cas types écrivait « supérieur les autres,
  jusqu'à 1,00 en 2070 », Coût « Les 1,00 de la proposition en 2070 disent une
  marge de 0 % ». Le coefficient de 2070 est à 1,0063 : les deux pages
  écrivent 1,01 et « une marge de 1 % », juste, mais à la merci du prochain
  changement du modèle.
- *Les décimales.* `decimalesHorsDeUn` remplace `decimalesSousUn` : assez de
  décimales, de deux à quatre, pour qu'un coefficient autre que un ne s'écrive
  pas 1,00, d'un côté de un comme de l'autre. Le dernier coefficient de la note
  de Coût (`noteLectureCoefficient`) et de la phrase de Cas types
  (`lectureReglageProposition`) les prend, et la marge son pourcentage à la
  même précision, comme le manque : 1,001 et « une marge de 0,1 % » pour
  1,0013.
- *La phrase commune.* La phrase de Cas types a trois branches : dessus
  partout, dessous partout, dessous sauf en 2070. L'entrée
  `cas_types.coefficient_sous_un` du catalogue des affirmations citait la
  dernière, et changeait de branche avec le signe ; les deux autres portaient
  un gras à elles, que le catalogue aurait dû suivre le jour où elles
  s'afficheraient. Les trois finissent désormais sur la même phrase
  (`LECTURE_DU_REGLAGE`), celle que l'entrée cite : « Au-dessus de un, il
  permettrait de relever les cases d'autant ; au-dessous, il faudrait les
  abaisser, ou financer l'écart autrement. » Les deux autres perdent leur gras
  et leur dernière phrase, que la commune redit : dessus partout, « à
  prélèvement égal, le système a de la marge » ; dessous partout, « le coût de
  la transition au taux unique », après le plus bas et le dernier coefficient.
  Elles comptent 48 et 51 mots, autant au plus que la branche affichée, qui ne
  change pas d'un mot : Cas types tient son budget de lecture, 448 mots pour
  450, sous chacune. L'entrée garde son identifiant et son extrait ; sa portée
  dit toutes les branches.
- *Le code mort.* La section du coefficient d'équilibre de Coût calculait une
  lecture du coefficient de 2070 (`lectureCoefficient`), à deux décimales
  au-dessus de un, qu'elle ne rendait plus depuis que la note de Coût la
  remplace ; elle est retirée, et son histoire passe au commentaire de la note.

**Ce que ça déplace.** Rien de ce que les pages rendent : aucun des 79 rendus
de page ni des 907 témoins de simulation ne change (`construire_temoins.py`,
`resumer_temoins.py`), ni le paquet. Le tableau du coefficient d'équilibre et
le README gardent deux décimales pour les quatre systèmes : un tableau aligne
ses colonnes, et un coefficient tout près de un s'y lirait 1,00 sans démentir
de phrase.

**Les tests** (`test_web_revues.py`).
`test_un_coefficient_tout_juste_au_dessus_de_un_ne_s_ecrit_pas_1_00`, neuf, sur
des réglages posés à la main — 1,0013, 1,0026, 1,0063 et 0,9984 — : vu rouge
sur les deux premiers, « jusqu'à 1,00 en 2070 » et « une marge de 0 % », les
deux autres passant déjà ; `test_la_phrase_du_reglage_tient_quel_que_soit_le_signe`,
neuf : l'extrait du catalogue dans chaque branche, aucun gras, le budget de
Cas types sous la plus longue ; vu rouge sur la branche « dessus partout ».
Les deux fonctions de la phrase sont exportées pour eux, comme
`reglageProposition`. `test_cas_types_dit_du_reglage_ce_que_le_solde_dit` suit
les décimales et les deux branches récrites ; le contrôle
`note_du_coefficient_suit_son_signe` (`test_affirmations.py`) aussi, et lit le
dernier coefficient sur Cas types dès qu'une année est sous un. Passent :
`-m site`, `-m rapide`, les trois fichiers du site, les contrôles du
catalogue touchés et la conservation, dont `--depuis HEAD` ne relève que
l'entrée récrite.

**Ce qui reste**, dans l'ordre :

1. *Aux pages* : rien de ces deux points.
2. *De l'étape 7, à sa fin* : la limite (note du 23 octobre, points 3 et 4 ;
   seizième partie, point 2).
3. *Au propriétaire* : les départs qui suivent l'espérance de vie ; de la
   septième partie, la table des poids et sa phrase du partage, que l'inapte
   et l'ex-invalide démentent, et le rapport de dépendance sous chaque
   variante.
