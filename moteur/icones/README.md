# Les pictogrammes du site

Ils viennent tous de **[Lucide](https://lucide.dev) 1.46.0**, sous licence ISC
(`LICENSE`, à côté). Un seul jeu, une seule grille — 24 × 24, trait de 2,
extrémités et jointures arrondies —, et rien qui soit dessiné à la main : c'est
ce qui les fait tenir ensemble à toutes les tailles, ce qu'un emoji ou un
caractère Unicode ne font pas, leur dessin changeant d'un système à l'autre.

**Les fichiers de ce dossier sont les originaux, recopiés sans retouche.** Le
site ne les charge pas : le gabarit écrit leur tracé DANS la page, en deux
exemplaires — `src/retraite_notionnelle/web/gabarit.py` et
`moteur/js/gabarit.js` —, parce que le portage JavaScript n'utilise aucune
bibliothèque et que la page ne demande aucune ressource tierce. Un test relit
ces fichiers et vérifie que les deux tables disent exactement ce qu'ils disent.

`../icone.svg` est l'icône du site elle-même : la même grille, le même trait,
le tracé de `trending-up` posé sur un carré à l'arrondi de la charte.

## Ajouter un pictogramme

```bash
npm pack lucide-static@1.46.0          # ou npm install, puis copier le fichier
cp .../icons/nom.svg moteur/icones/
```

puis ajouter la même entrée dans `ICONES`, des deux côtés du portage. Le test
refuse une table qui s'écarte du fichier, une entrée sans fichier, et un
fichier que personne n'utilise.
