# Fraîcheur de la prose : un document dit l'état, ou raconte

Un document du dépôt dit ce qui est vrai aujourd'hui, ou raconte ce qui s'est
passé un jour ; il ne mêle plus les deux. La décision, et ce qui l'a fait
prendre, sont dans la note `docs/decisions/0002-fraicheur-de-la-prose.md` ;
la mécanique, dans l'en-tête de `scripts/verifier_prose.py`. Cette page dit
la règle, et ce qu'une session en fait.

## Un régime par document

`data/reference/prose/zones.yaml` donne à chaque document son régime.

| Régime | Ce que le document affirme | Ce que le contrôle exige |
|---|---|---|
| `etat` | ce qui est vrai **aujourd'hui** | tout chiffre y est ancré sur une sonde qui le recalcule ; un chiffre nu est refusé |
| `recit` | ce qui s'est passé **un jour** | qu'on n'y touche plus : ses chiffres sont justes à leur date, et `scripts/conservation.py` refuse qu'il se perde ou se réécrive |
| `produit` | ce qu'un script écrit | rien ici : le script a son test de péremption |

Un récit qui naît dans un document d'état — un défaut trouvé, sa correction,
ce qu'elle a déplacé — va dans la feuille de route, ou dans l'archive du
document (`docs/archives/`). Quelques documents gardent, par construction,
des exceptions que `zones.yaml` déclare une à une : les paragraphes qui
racontent, au milieu du README, texte de la proposition, ou de la
méthodologie ; les procès-verbaux enclavés dans `limites.md` ; la liste des
versions de l'architecture ; le préambule d'état de la feuille de route ;
les blocs qu'un script écrit au milieu d'une prose.

## L'ancre

Un chiffre d'un document d'état porte, autour de lui, la sonde qui le
recalcule. Le commentaire HTML ne se voit ni sur GitHub ni sur le site :

```markdown
le dépôt porte <!--chiffre:entrees(data/reference/regimes/inventaire.yaml:inventaire)-->91<!--/--> lignes d'inventaire
```

`python scripts/verifier_prose.py --sondes` imprime le vocabulaire des
sondes : des comptes d'entrées, des cellules et des bornes de tables de droit,
des mesures du modèle. Trois ancres ne calculent rien, et disent pourquoi :
`tenu(nom_du_test)`, quand un test nommé tient le chiffre ; `illustration()`,
pour un exemple qui ne peut pas devenir faux ; `a_verifier(la raison)`,
l'aveu qu'un cliquet compte.

Un chiffre qui décrit le dépôt lui-même — ses lignes, ses tests — ne s'écrit
pas du tout : il change à chaque session, et
`python scripts/tableau_de_bord.py --cout` l'affiche à la demande.

## Ce qu'une session en fait

1. **Après toute modification de la prose**, lancer
   `python scripts/verifier_prose.py --corriger` : il réécrit les chiffres
   ancrés qui ont dérivé, en gardant leur typographie.
2. **En écrivant un chiffre dans un document d'état**, l'ancrer. Si aucune
   sonde ne convient, en ajouter une à `scripts/verifier_prose.py`.
3. **En créant un document**, le déclarer dans `zones.yaml`, avec son régime :
   un test refuse un document que rien ne déclare.
4. **En racontant**, écrire dans un récit — la feuille de route, une archive —
   et non au milieu d'un document d'état.
