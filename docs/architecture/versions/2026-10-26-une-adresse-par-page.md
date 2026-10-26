# Version du 26 octobre 2026 : une adresse par page

Chaque page du site a son adresse : l'accueil est la racine, les huit autres
sont chacune un dossier — `simuler/`, `cout/`, `risque/`, `partager/`,
`saviez-vous/`, `cas-types/`, `avantages/`, `methode/` — qui porte son
`index.html`. Le lecteur, sa carrière et ses réglages, reste derrière le `#`,
que le navigateur ne transmet pas ; un mot sans `=` y désigne une section. Les
anciennes adresses (`#/cout?indexation=prix`, `#/trajectoire`, `#/donnees`,
`#/?…`) sont redirigées par le routeur vers les nouvelles (note de décision
0004, action 174).

L'annexe C.9 (la surface publique) décrit les adresses sous leur nouvelle
forme. `moteur/js/adresses.js` lit les deux formes et écrit la nouvelle ;
`moteur/js/gabarit.js` dit où va chaque page (`dossierDe`) et écrit les liens,
relatifs à la page rendue ; `moteur/js/routeur.js`, sorti d'`index.html`, est
le script que toutes les pages chargent ; `scripts/construire_pages.py`
fabrique les huit pages en dossier depuis `index.html`, et `regenerer.py` les
refait.
