# Relecture de la zone grise : la garantie, l'impôt sur le revenu et la restitution, fonction par fonction

**La demande.** La première relecture du lot E, seule session de relecture
en cours, sous les quatre règles de la note de la question 5 : relire
`garantie.py` puis `impot_revenu.py` contre leurs portages, et
`restitution.py` si le contexte le permet ; corriger ce qui ne déplace aucun
résultat publié, dans les deux fichiers de la paire et un fichier de tests à
soi ; consigner le reste. Les trois paires sont relues ; aucun jumeau n'est
retiré, aucun résultat publié ne bouge.

## La pertinence, avant de relire

- **Aucune des trois paires n'avait été relue, ni ne l'est ailleurs.** Aucune
  note de l'action n'en porte la relecture, ni celles des actions 130, 158,
  175, 177, 178 et 186 (cherché par l'éclaireur) ; `origin/main` ne porte
  aucun commit de relecture sur ces fichiers. L'action 186 a récrit la
  garantie les 9 et 10 novembre (le barème dégressif) : `garantie.py` fait
  319 lignes, non les 244 de l'inventaire.
- **Le jumeau Python se relit encore, comme la référence.** Si les deux
  s'écrivent en JavaScript seul, c'est le portage qui reste, et c'est lui que
  la relecture doit garantir. Mais les tests tirés des sources — la brochure,
  OpenFisca, l'IPP, les valeurs posées à la main de la garantie — sont écrits
  contre le Python, et c'est le Python que le coût exécute aujourd'hui. La
  relecture utile est donc la comparaison : que le portage rende, au bit, ce
  que rend le jumeau que les sources éprouvent. L'attention est allée au
  portage et à ce que la concordance n'exécutait pas.
- **Le sort de la garantie de population ne change pas ce qui se relit.** Les
  deux exemplaires existent tant que le propriétaire n'a pas tranché, et la
  confrontation écrite ici sert les deux issues : en JavaScript seul, elle
  est la garde que la note de la question 1 demandait avant le retrait ; en
  Python seul, elle part avec les fonctions du portage. Le barème d'une
  personne, `complement_garantie`, reste des deux côtés dans les deux cas,
  jusqu'au départ du moteur.

## Le relevé

`python scripts/jumeaux.py --couverture`, au commit 3944fdc. Les tests de
concordance exécutaient :

| paire | lignes Python | lignes JavaScript | jamais confronté |
|---|---|---|---|
| la garantie | 42 sur 139 (30 %) | 126 sur 137 (92 %) | côté Python, toute la garantie de population ; côté portage, les refus |
| l'impôt | 653 sur 682 (96 %) | 829 sur 871 (95 %) | les refus, `impot_d_un_revenu_imposable`, `taxe_complementaire_des_revenus`, quatre branches rares |
| la restitution | 75 sur 78 (96 %) | 68 sur 70 (97 %) | le fichier absent, le poste nul |

Aucun test ne confrontait directement la garantie de population ni la
restitution : la mesure compte, par leur nom, des tests qui n'appellent pas
node (`test_le_moteur_python_sert_le_meme_bareme_que_le_portage`).

## La garantie — relue à 3944fdc

Fonction par fonction, les deux fichiers font le même calcul, dans le même
ordre : le barème, le manque moyen d'une tranche, le coût sur la
distribution, les deux facteurs, la pension moyenne, le coût par sexe. La
fiche (`garantie_vieillesse.yaml`) nomme les bonnes fonctions, et le barème
est celui des décisions 100 et 102 : le pivot à la moitié du plancher, la
sortie à une fois et demie. Vérifié en calculant : le rapport des pensions
moyennes que cite `pension_moyenne`, 0,641 puis 0,624 ; les treize cas
types, dont une seule femme.

**Corrigé.**
- `coutGarantie` ne tenait pour ouverte que la tranche dont la borne
  supérieure vaut `null` ; sans borne du tout, il rendait NaN, quand
  `manqueMoyen`, `pensionMoyenne` et `partSous` (`distribution.js`) la
  tiennent pour ouverte. Le paquet écrit `null` : aucun chiffre ne bouge.
  Test posé à la main, vu rouge : un million de retraités, la moitié de 0 à
  1 000 €, l'autre à 1 000 €, sous un plancher de 1 500 € — 9 000 M€.
- L'en-tête du portage disait « douze cas types », trois lignes avant
  « treize » : treize. C'est une des incohérences que l'action 167 relève
  (`feuille_de_route.md`, ligne 1036), qui peut la rayer.

**Laissé, qu'aucune donnée n'atteint.** Une `part_seule` sans l'un des deux
sexes lève `KeyError` en Python et rend NaN au portage ; une tranche de
largeur nulle, ou un taux de retrait nul passé droit à `_manque_moyen`,
divise par zéro d'un côté et rend l'infini de l'autre. Aucun des deux
barèmes ne vérifie sa forme : c'est `cout_garantie` qui la refuse, des deux
côtés du même message.

**Consigné, hors de la paire.** `distribution.js`, ligne 5, dit encore
« douze cas types ». L'en-tête de `garantie.py` compte « cinq » cas types
servis par la garantie « pour les générations récentes » : non vérifié, et
déjà à l'action 167.

## L'impôt sur le revenu — relu à 3944fdc

Les 1 320 lignes et leurs 1 092 lignes de portage, étape par étape, avec le
chargeur des barèmes et sa projection (`donnees/impot_revenu.py`), que le
portage refait : même calcul partout, mêmes constantes, mêmes messages. Un
essai jetable, hors du dépôt, a tiré 40 000 foyers au hasard, de 1960 à
2070 : aucun écart, au bit, sur aucune des trente-six valeurs rendues.

**Corrigé.** Deux commentaires : dans le portage, celui de l'abattement de
l'article 157 bis coiffait `beneficeRetenu` ; dans le Python, l'en-tête
disait que la page Coût prendrait l'impôt « plus tard », quand l'effet
retour l'appelle (`EffetRetour._impot`).

**Laissé, qu'aucune donnée n'atteint.**
- Les demi-parts du plafonnement s'arrondissent au pair en Python (`round`),
  vers le haut au portage (`Math.round`) : elles sont entières, les quarts
  de part de la résidence alternée étant hors champ.
- `round(x, 6)` et `toFixed(6)` ne diffèrent qu'à une moitié exacte du
  septième chiffre, un multiple de 1/128, qu'aucun arrondi à l'unité ou au
  centime ne voit : ce que dit l'en-tête du portage tient.
- Un revenu qui n'est pas un nombre est refusé par le Python (`math.floor`)
  et rend NaN au portage ; une clé absente d'une marche lève `KeyError` d'un
  côté, rend NaN de l'autre. Le fichier des barèmes les porte toutes.
- `prime_pour_l_emploi`, ligne 992 : le retour d'une année sans prime ne
  s'atteint que par un appel direct, `_liquider` ne l'appelant pas alors.

**Consigné, sans rien changer.**
1. *La remarque des minorations et majorations.* Des deux côtés, le code
   écrit « la règle des notes de l'IPP, sans texte lu » pour toute année
   hors de 1960 à 1972. Seule l'année 1980 en souffre : sa majoration est
   lue à la loi — la marche du fichier des barèmes le dit (`origine: "loi"`,
   loi de finances rectificative pour 1981, art. 1er, lue aux textes du
   Sénat), comme le commentaire de `PREMIERE_ANNEE_DES_LOIS_LUES` et celui
   de `_majoration`. Le cas : un salarié seul de 900 000 F en 1980 porte
   une majoration de 83 270 F et cette remarque, fausse pour lui. Non
   corrigé : la correction change une chaîne que l'impôt rend, et la borne
   se déduirait mieux de l'origine de la marche que d'une année écrite en
   dur, ce qui touche le chargeur. Une session à part, test d'abord.
2. *Le test de concordance qui existe* (`tests/test_cycle_de_vie_portage.py`,
   `_impots_python`) ne passe pas `vit_seul` au Python, quand node le reçoit :
   sa grille n'a pas de parent qui ne vit pas seul. Le lot D, qui porte ce
   fichier, le verra ; la confrontation d'ici le passe des deux côtés.

**Ce que la relecture n'a pas fait.** Elle n'a rouvert aucun texte : les
règles sont jugées contre les citations que le code porte et contre les
tests tirés des sources (`tests/test_impot_revenu.py`,
`tests/test_referents.py`), verts. Aucune règle n'est apparue fausse ;
aucune n'a été relue dans LEGI.

## La restitution — relue à 3944fdc

Les deux fichiers font le même partage. Les chiffres de l'en-tête, refaits
en calculant : 63,9 Md€ et 15,3 % des ressources en 2025, 17,8 Md€ pour les
deux impôts, 27,8 % du poste, 1,12 point de CSG.

**Corrigé.** L'en-tête du Python disait la part du poste « entre 26,6 et
28,9 % depuis 2019 » : elle vaut 29,2 % en 2020. Dans le portage, le
commentaire de `pointsCsgRendus` coiffait sa mémoire.

**Laissé.** Le Python admet que le fichier des deux impôts manque (aucun
poste, une fiabilité estimée) ; le portage non, et son repli sur « estimée »
ne s'atteint pas. La mémoire du portage garde un partage par paquet et le
refait quand la part rendue change, celle du Python en garde huit : mêmes
résultats. `eteint_de_dette` n'est lu par aucun calcul, ce que la feuille de
route note déjà. Les trois citations de droit de l'en-tête (L. 131-8, 1° et
3°, L. 241-3, 1°), lues dans LEGI le 20 septembre 2026 d'après le journal de
veille, n'ont pas été rouvertes.

## Tests

`tests/test_relecture_zone_grise.py`, dix tests de la suite rapide, deux
secondes, un seul appel à node. Les deux jumeaux y calculent les mêmes
demandes, égales au bit, les refus du même message :
- la garantie, 1 051 demandes : le barème, le manque moyen de part et
  d'autre du pivot et de la sortie, le coût sur les trois distributions sous
  cinq facteurs, quatre planchers et quatre formes, le coût par sexe sous un
  plancher ou deux, la pension moyenne, les deux facteurs ; neuf refus ;
- l'impôt : 3 000 foyers d'une graine fixe, les quatre branches rares
  chacune sous son nom, l'impôt d'un revenu imposable donné, la taxe
  complémentaire seule de 1958 à 1971, les paramètres lus et projetés, d'un
  coup ou année après année, dix-huit refus, les constantes des deux
  modules ;
- la restitution : quinze années sous quatre parts rendues.

Chaque confrontation dit qu'elle a un objet, et sept mutations d'une ligne
l'ont rougie. Mesuré ensuite : le fichier exécute les 108 lignes de fonction
de `garantie.py` et 574 des 575 d'`impot_revenu.py`. La suite rapide, 4 783 ;
celle du site, 38 ; les tests de la zone, 376.

## Ce qui reste

1. **Le lot F relit ce qui a changé depuis** : `git diff` de chaque paire
   depuis le commit qui porte cette note.
2. **La suite du lot E**, une session : le cœur de `RevalorisationServie`
   avec `Indexation`, et les variantes des comptes, qui ferment la zone
   grise ; puis les paires du moteur, les moins couvertes d'abord.
3. **Le lot C1** trouve sa confrontation de la garantie écrite ; il lui
   reste la demande au pont.
4. **Au propriétaire** : rien de neuf. La garantie de population attend
   toujours sa décision (question 1) ; la relecture n'y ajoute qu'un fait,
   la concordance au bit est désormais tenue par un test et non par un
   essai. La remarque de 1980 (ci-dessus) se corrige d'après la marche,
   sans décision de sa part.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun témoin, aucun
agrégat, aucun chiffre du site ; ni `pont.py`, ni `pont.mjs`, ni un script ;
le bloc « Reprise » de l'action, que cette session ne récrit pas.
