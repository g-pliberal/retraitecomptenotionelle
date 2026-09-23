# Fraîcheur de la prose : l'état, le récit, et ce qui les distingue

Le dépôt affirme des milliers de chiffres en prose, et une vingtaine seulement
étaient tenus par un test. Les autres étaient des souvenirs. Ce document dit
comment on cesse d'en écrire.

## Le constat

Le mal n'est pas le chiffre faux. Il en traînait, et ils étaient réparables à
la main : la feuille de route donnait « plus de trois mille lignes » à
`src/retraite_notionnelle/scenarios/actuel.py`, qui en fait
<!--chiffre:lignes(src/retraite_notionnelle/scenarios/actuel.py)-->5 363<!--/-->,
et « douze mille lignes » au portage, qui en fait
<!--chiffre:lignes(moteur/js/*.js)-->35 429<!--/--> ; le README annonçait un
premier chargement de 310 Ko quand il en transfère plus du double, et
« 123 simulations » quand les témoins en figent
<!--chiffre:entrees(tests/temoins/simulations.json:)-->503<!--/-->.

Le mal est qu'on ne pouvait pas savoir. **Le dépôt écrit son ÉTAT et son
HISTOIRE dans les mêmes fichiers, dans la même typographie, sans frontière.**
« 263 Ko de modèle » est faux aujourd'hui et était vrai du temps de Pyodide,
une ligne plus haut. `limites.md` mêle trois sections au présent — ce que les
chiffres valent — et cinquante au passé, qui racontent des corrections faites.
Sur les chiffres de la feuille de route, plus de la moitié sont dans les zones
`Ce que ça a déplacé` et `Journal` : des procès-verbaux, justes à leur date,
qu'il ne faut surtout **pas** mettre à jour.

Ni un lecteur ni un test ne pouvait trancher. D'où l'impression de s'y perdre,
et d'où l'impossibilité de vérifier quoi que ce soit : un test qui corrigerait
« 263 Ko » abîmerait le récit.

La réponse du dépôt avait été, jusqu'ici, d'écrire un test par chiffre après
chaque dérive constatée — le nombre de tests, le poids du paquet, le compte des
statuts et des régimes, le tableau d'exemple. Chacun répare ; aucun n'empêche
le suivant, parce qu'il faut à chaque fois qu'un humain ait remarqué. Et la
vague ne protège pas : le README écrivait « près de cinq cents tests » pour ne
pas avoir à tenir un compte exact, et se trompait du double.

## Les quatre régimes

`data/reference/prose/zones.yaml` déclare, section par section, ce que chacune
affirme. `scripts/verifier_prose.py` l'exploite, et `tests/test_prose.py` en
fait une obligation.

| Régime | Ce que la section affirme | Ce que le test exige |
|---|---|---|
| `etat` | ce qui est vrai **aujourd'hui** | tout chiffre y est ancré ; un chiffre nu est refusé |
| `recit` | ce qui s'est passé **un jour** | rien : ses chiffres sont gelés, et les rafraîchir serait réécrire l'histoire |
| `produit` | ce qu'un script écrit | rien ici : le script a déjà son test de péremption |
| `a_declarer` | personne n'a tranché | rien, mais le cliquet les compte |

## L'ancre

Un chiffre d'une zone `etat` porte, autour de lui, la sonde qui le recalcule :

```markdown
`actuel.py` fait <!--chiffre:lignes(src/.../actuel.py)-->4 251<!--/--> lignes
```

C'est le geste de `scripts/construire_regimes_md.py`, qui écrit `docs/regimes.md`
entre deux repères — en plus fin : le repère tient dans une phrase, et le
commentaire HTML ne se voit ni sur GitHub ni sur le site.

```bash
python scripts/verifier_prose.py              # confronte, sans rien écrire
python scripts/verifier_prose.py --corriger   # réécrit les chiffres qui ont dérivé
python scripts/verifier_prose.py --inventaire # ce qui n'est pas encore déclaré
python scripts/verifier_prose.py --sondes     # le vocabulaire des sondes
```

`--corriger` garde la typographie du chiffre qu'il remplace : le dépôt écrit
« 2874 » ici et « 10 615 » là, et une correction qui changerait l'un en l'autre
ferait un diff que personne ne veut relire.

Une sonde qui arrondit se déclare : `poids(...)~5%`. Une sonde qui compte peut
traverser un cran d'entrées par `*` : `entrees(data/sources.yaml:institutions.*.jeux)`
réunit les jeux de toutes les institutions du manifeste, que rien ne totalise
ailleurs — la méthodologie en annonçait « cent vingt » en toutes lettres.

**Les paramètres de droit se lisent dans leur table.** C'est le gros du dépôt :
une durée requise, un âge légal, un taux de décote vivent dans un CSV de
`data/reference/legislation/`, une ligne par génération ou par année, et la
prose les recopiait faute de savoir y descendre. Quatre sondes le font :

```markdown
cellule(duree_assurance_requise.csv:trimestres?generation=1966)   une cellule
minimum(age_ouverture_requis.csv:age)                             une borne
maximum(coefficient_minoration.csv:coefficient*100)               l'autre
distinctes(revalorisation_salaires.csv:date_effet)                les valeurs différentes
```

Ces sondes tiennent aussi les PÉRIODES : `minimum(…:annee?fiabilite=certifiee)`
et son `maximum` disent de quand à quand une série est certifiée, et c'est le
tableau du §1 de `limites.md` qui en vit — une série s'allonge d'une année, et
la prose suivait autrefois de mémoire.

Les critères se joignent par `&`, et une cellule doit tomber sur une ligne et
une seule : deux lignes, c'est une désignation qui ne dit pas ce qu'elle croit
dire. Une colonne porte au besoin son changement d'unité, `coefficient*100`
pour lire en pour-cent une fraction stockée telle quelle, `valeur/12` pour dire
au mois un montant annuel. Et `partout(fiches.yaml:regimes.*.periodes.*.champ)`
rend la valeur que TOUTES les entrées désignées portent, en refusant dès que
deux s'écartent : c'est ce qu'affirme une prose qui annonce un nombre unique.

Trois ancres ne calculent rien, et disent pourquoi :

- `tenu(nom_du_test)` — le chiffre est tenu ailleurs, par un test qu'on nomme,
  et qui doit exister. C'est ce qui évite qu'un test supprimé laisse derrière
  lui un chiffre que plus personne ne tient.
- `illustration()` — le nombre est un exemple, pas une affirmation. Est une
  illustration ce qui ne peut pas devenir faux. La limite est celle que
  l'action 34 de la feuille de route pose pour les affirmations du site, et
  elle se tient en relecture.
- `a_verifier(la raison)` — personne ne tient ce chiffre, et voici pourquoi.
  C'est l'aveu, pas l'échappatoire : le second cliquet les compte.

## Les deux cliquets

C'est ce qui fait avancer le dépôt sans qu'on y pense. Deux compteurs, en bas
de `zones.yaml`, qui ne peuvent que décroître :

- **les sections non déclarées**, aujourd'hui
  <!--chiffre:valeur(data/reference/prose/zones.yaml:cliquet.sections_a_declarer)-->0<!--/--> ;
- **les chiffres qui portent l'aveu `a_verifier`**, aujourd'hui
  <!--chiffre:valeur(data/reference/prose/zones.yaml:cliquet.chiffres_a_verifier)-->0<!--/-->.

Une section nouvelle dans un fichier non déclaré fait monter le premier, et le
test échoue jusqu'à ce qu'on ait dit ce qu'elle engage. Une session qui déclare
une vieille section l'abaisse. Le jour où les deux tombent à zéro, plus un
chiffre du dépôt n'est un souvenir.

## Ce que le contrôle ne voit pas

Trois angles morts, nommés d'avance plutôt que découverts plus tard.

- **Les blocs de code.** Une ancre y serait visible, puisque rien n'y est
  masqué. L'arborescence du README annonce le nombre de tests dans un bloc :
  elle reste tenue par `test_le_README_dit_le_vrai_nombre_de_tests`, écrit
  pour elle. Un chiffre qui compte a intérêt à sortir du bloc. Un `#` de bloc
  n'est en revanche plus pris pour un titre : les commentaires du README
  ouvraient autant de sections fantômes, qui gonflaient le cliquet et, plus
  grave, coupaient en deux la section réelle qui les contient.
- **Les chiffres en toutes lettres.** L'ancre ne sait pas les tenir, et c'est
  l'un d'eux qui avait vieilli du simple au double dans la feuille de route.
  Le contrôle les signale dans les zones `etat`, et la seule issue est de les
  réécrire en chiffres. Les petits nombres (« six pages ») lui échappent
  encore, faute de pouvoir les distinguer de la langue ordinaire.
- **Les phrases.** Ce contrôle ne juge pas une affirmation, seulement un
  nombre : « la bascule ne reprend aucun droit acquis » lui est invisible.
  C'est l'objet de l'action 34 de la feuille de route, et les deux se
  complètent — l'une tient les chiffres du dépôt, l'autre les affirmations du
  site.

## Ce qu'une session doit en faire

Trois gestes, et aucun ne coûte plus d'une minute.

1. **Avant de pousser**, lancer `python scripts/verifier_prose.py --corriger`
   si la prose a bougé. Le test le refera, mais plus tard et moins bien.
2. **En écrivant un chiffre dans une zone `etat`**, l'ancrer. Si aucune sonde
   ne convient, en ajouter une à `scripts/verifier_prose.py` — le vocabulaire
   est fermé, mais il n'est pas figé.
3. **En arbitrant une section `a_declarer`**, dire ce qu'elle affirme et
   abaisser le cliquet. C'est le seul travail qui fasse reculer la dette, et il
   se fait section par section, sans jamais tout reprendre.
