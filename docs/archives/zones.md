# Les zones de la prose, section par section — archive

*Archive, gelée.* Jusqu'au 26 septembre 2026, `data/reference/prose/zones.yaml`
déclarait le régime de chaque section du README, de la méthodologie et de
quelques autres documents, une à une, avec en commentaire le jour et la raison
de chaque déclaration. La phase 1 de l'architecture a donné à chaque document
un régime par défaut (`docs/architecture.md`, annexe B : « un régime par
fichier ») : ces listes ne disaient plus rien que le défaut ne dise. Elles
sont gardées ici telles quelles, pour l'histoire qu'en racontent les
commentaires.

## `README.md`

```yaml
    sections:
      # L'introduction : les paramètres de la proposition sont ceux du modèle,
      # et le partage des 23 points se lit sur la fiche de paie de deux
      # salariés d'exemple. Elle annonçait +182 € par mois au salaire moyen
      # quand la fiche en donne 203 : la CSG rendue était arrivée depuis.
      "Retraite à comptes notionnels — modèle français rétroactif": etat
      # Le tableau des exigences : des comptes de fichiers, des paramètres de
      # droit lus dans leur table, et ce que le régime unique retient. Il
      # annonçait 36 réformes pour 89, un âge de fusion de 64/67 ans quand le
      # régime unique ouvre à 65 et donne le taux plein à 67,5, un taux du
      # régime général de 16,35 % en 1991 pour 15,8, et 469 témoins pour 494.
      "Ce que le modèle fait": etat
      # Les sources, et comment on les rafraîchit : des périodes de séries,
      # des comptes de valeurs certifiées. Les âges des espérances de vie sont
      # les libellés des séries, et le 6,6651 € une conversion de francs.
      "Les données": etat
      Ouvrir le simulateur: etat
      # Le corps de la section : ce que le premier chargement transfère, ce que
      # `index.html` charge, et le poids du portage.
      "👉 [g-pliberal.github.io/retraitecomptenotionelle](https://g-pliberal.github.io/retraitecomptenotionelle/)": etat
      Tests: etat
      # Ce que le dépôt EST : comment on l'ouvre, comment on l'appelle en
      # Python, comment ses répertoires sont rangés, ce que ses options
      # exposent, sous quelle licence. Rien n'y raconte : ces sections se
      # lisent pour agir, et une seule ligne périmée s'y voit tout de suite.
      # Les six résultats et les sections de données restent à arbitrer : ce
      # sont des mesures, et chacune demande sa sonde.
      "Ouvrir le site en local": etat
      "En Python, hors du site": etat
      "En bibliothèque": etat
      "Six résultats à connaître avant de lire les chiffres": etat
      "Organisation": etat
      "Principales options": etat
      "Licence": etat
      # Les deux premiers résultats : tout chiffre y est une MESURE du modèle
      # — un écart de pension, un rendement cumulé, un taux du régime unique —
      # que la sonde `mesure` recalcule. Ils étaient recopiés d'une exécution,
      # et le 22 septembre 2026 aucune carrière ne rendait plus ceux du §1 ter
      # et du §1 quater ; le taux du régime unique avait vieilli d'un dixième.
      "1. La règle d'indexation domine tout le reste": etat
      "1 bis. Le minimum n'est pas la seule statistique : médiane et moyenne": etat
      "1 ter. La règle que la théorie désigne : la masse salariale": etat
      "1 quater. Le lissage pluriannuel, qui n'est pas une règle": etat
      "2. La fusion augmente les cotisations des indépendants": etat
      # Les taux de la contribution employeur lisent leur cellule, et ce que
      # l'exemple affiche est la mesure de l'exemple. La part salariale du
      # régime général y était donnée à 40,87 %, que plus aucune fiche ne
      # porte, et la série publique à « neuf régimes », quand elle en a huit.
      "3. La part patronale pèse plus lourd que la part salariale": etat
      # Le coût, passé et projeté : tout y est une mesure du coût agrégé, que
      # la sonde recalcule en dix-sept secondes. Le jour où ces sections ont
      # été ancrées, le README donnait la garantie vieillesse à 40 milliards
      # en 2026 pour 17,8, le système actuel à 19,3 % du PIB en 2070 pour
      # 18,4, et le COR à 14,2 % pour les 15,3 que porte son dernier rapport ;
      # il affirmait surtout que le scénario 3 n'économise rien en 2026, quand
      # il y cesse de servir la réversion.
      "4. Ce que la retraite a coûté depuis 1959": etat
      "5. Une réforme prospective ne fait rien économiser tout de suite, et beaucoup ensuite": etat
      # Le solde et le coefficient d'équilibre. Récrite le jour de son
      # ancrage : elle décrivait encore la recette du scénario 6 comme un
      # rapport de taux légaux multiplié par 0,63, quand la convention par
      # défaut applique les 18 % à l'assiette ; elle donnait à ce scénario
      # 103 % du PIB de dette en 2070 pour 84, et au fonctionnaire d'État un
      # gain net de 32,9 % pour 37,6. Les taux d'affectation de la CSG, qui
      # ne sont dans aucune donnée, n'y sont plus recopiés : `restitution.py`
      # les porte avec leurs articles.
      "6. Un coût n'est pas un solde, et le coefficient d'équilibre le dit": etat
```

## `docs/methodologie.md`

```yaml
    sections:
      "Méthodologie": etat
      "1. Ce qu'est un compte notionnel": etat
      "2. Périmètre temporel": etat
      "3. L'indexation": etat
      "La règle par défaut, et la règle demandée": etat
      "La règle d'équilibre : la masse salariale": etat
      "L'assiette la plus large : le PIB nominal": etat
      "4. L'âge de référence": etat
      "Variantes": etat
      "La validation des trimestres": etat
      "8. Les six scénarios": etat
      "Scénario 2 — comptes notionnels rétroactifs": etat
      "Scénario 3 — comptes notionnels à compter d'aujourd'hui": etat
      "Scénarios 4 et 5 — les mêmes, part patronale comprise": etat
      "8 bis. Du droit individuel au coût collectif": etat
      "Et de là, l'avenir": etat
      "9. Les données": etat
      "Sources": etat
      "Quelle source l'emporte": etat
      "Fiabilité": etat
      "Unité de compte": etat
      "Ce qu'elle produit, et pourquoi il faut le savoir": etat
      "Changer de statistique : médiane et moyenne": etat
      "Le lissage pluriannuel, qui n'est pas une règle": etat
      "Comment l'écart pèse sur la pension": etat
      "Ce que l'âge de référence déplace, et ce qu'il ne déplace pas": etat
      # Posée le 22 septembre 2026 avec la mesure : son seul chiffre lit le
      # paramètre qu'elle décrit.
      "L'âge légal de départ": etat
      "6. Les neutralisations": etat
      "Le droit ouvre-t-il cette liquidation ?": etat
      "Après la bascule, le régime unique tranche": etat
      "Ce que ces scénarios ne disent pas": etat
      "Brut, et pas net": etat
      "Arrondis : ce que le droit fait, et ce que le modèle fait": etat
      "Ancrage des rémunérations": etat
      "La seule ligne qui ne soit pas une hypothèse": etat
      "7. La fusion des régimes": etat
      "La catégorie active et la pension militaire": etat
      "La cascade des avantages non contributifs, dans l'ordre du droit": etat
      "Le taux plein, et ce qui l'ouvre": etat
      "La construction": etat
      "L'âge de conversion des droits acquis": etat
      "Scénario 1 — le système actuel": etat
      "Ce que chaque régime liquide, et sur quoi": etat
      "Tables de mortalité": etat
      "Précision des coefficients affichés": etat
      "Une carrière, plusieurs métiers": etat
      "Le périmètre du taux de cotisation": etat
      "5. Le coefficient de conversion": etat
      "`part_salariale` : qui paie quoi, dans les fiches": etat
      "La contribution employeur du public": etat
      "Au-delà de 2025": etat
      "Scénario 6 — la proposition libérale : un taux unique dès la bascule, un pilier capitalisé, et une garantie vieillesse": etat
      "Le pilier de capitalisation obligatoire": etat
      "Et de là, le solde": etat
```

## `docs/outillage_interface.md`

```yaml
    sections:
      # Elle raconte la demi-journée où l'on a cru qu'un site public bloquait le
      # dépôt, quand c'était son propre navigateur qui ne faisait confiance à
      # personne. La date est le sujet de la section.
      "Le navigateur ne voit rien hors de `localhost`, et il le dit mal": recit
      "Ce qu'un navigateur ne débloque pas": recit
      # Les trois sections qui ne portent aucune de ces tailles : ce qu'un
      # clone reçoit, la commande à lancer, et les règles figées à un commit.
      "Outillage d'audit d'interface — ce qu'une machine neuve reçoit, et ce qu'elle doit encore faire": etat
      Playwright CLI: etat
      "Web Interface Guidelines : règles figées": etat
      # Les trois sections qui portent les tailles de logiciels installés hors
      # du dépôt. Aucune sonde ne les atteint depuis un clone, mais une version
      # publiée ne change plus : chaque chiffre est lié à la version figée sur
      # laquelle il a été lu, et
      # `test_les_chiffres_de_l_outillage_sont_ceux_des_versions_figees` échoue
      # dès que le dépôt en fige une autre.
      "Ce qu'un clone frais contient déjà": etat
      "Ce qui demande le réseau, et une seule fois": etat
      Impeccable: etat
```

## `docs/fraicheur.md`

```yaml
    sections:
      # Cette section cite les chiffres périmés qu'on a trouvés : les ancrer
      # serait les corriger, et le constat n'aurait plus de sens.
      Le constat: recit
```

## L'en-tête, et l'annonce de l'arbitrage section par section

```yaml
# Ce que chaque section de la prose du dépôt AFFIRME — et donc ce qu'un test
# peut en exiger. Lu par `scripts/verifier_prose.py` ; voir son en-tête pour la
# mécanique, et `docs/fraicheur.md` pour la raison d'être.
#
# Quatre régimes, et un seul est contraignant :
#
#   etat        la section décrit ce qui est vrai AUJOURD'HUI. Tout chiffre y
#               est ancré sur une sonde qui le recalcule, et un chiffre nu y
#               est refusé.
#   recit       la section raconte ce qui s'est passé un jour. Ses chiffres
#               sont justes à leur date, gelés, et les rafraîchir serait
#               réécrire l'histoire.
#   produit     la section est écrite par un script, qui a déjà son test.
#   a_declarer  personne n'a encore tranché. Le cliquet les compte.
#
# Le cliquet, en bas, est ce qui fait avancer le dépôt sans qu'on y pense : il
# ne peut que décroître. Une section nouvelle dans un fichier `a_declarer` le
# fait monter, et le test échoue jusqu'à ce qu'on ait dit ce qu'elle engage.

  # ------------------------------------------------------------------------
  # Le reste s'arbitre section par section, et ce qui reste se ressemble : des
  # sections au présent dont chaque chiffre est une mesure du modèle — un
  # écart en pourcentage, un montant, une part de PIB — et qui demandent donc
  # une sonde par chiffre, ou un test nommé qui le tienne déjà. Le §1 de
  # `limites.md` en porte deux cents à lui seul.
  # ------------------------------------------------------------------------
```

## `docs/veille_droit.md`

```yaml
  # La procédure de veille, et ce que le registre porte. Elle est écrite pour
  # être SUIVIE par la session d'après : périmée, elle enverrait relire ce qui
  # l'a déjà été. Sa dernière section s'intitule « aujourd'hui » et donnait un
  # compte figé au 17 septembre 2026 — vingt-deux exemples publiés pour 21 ;
  # elle lit maintenant le registre et les témoins.
  docs/veille_droit.md:
    defaut: etat
    sections:
      # Le jour où le dépôt a servi des âges légaux certifiés et faux : le
      # récit qui fonde les trois outils, et ses chiffres sont ceux de ce
      # jour-là — dont le « 63 ans et 171 trimestres » qui était l'erreur.
      Ce qui s'est passé le 17 septembre 2026: recit
```
