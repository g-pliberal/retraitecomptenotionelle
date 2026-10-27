# Version du 27 octobre 2026 : le style de chaque page

Chaque page toute faite porte en tête les règles de `moteur/style.css` qui
peuvent la toucher (action 174, proposition du 27 octobre 2026 retenue par le
propriétaire). `scripts/feuille_de_page.py` les choisit, en Python et sans
dépendance : une règle est gardée quand l'un de ses sélecteurs ne demande que des
classes, des identifiants, des balises et des attributs présents dans la page ou
posés par le routeur ; les requêtes `@media`, `@supports` et `@container` gardent
leur condition, l'impression reste à la feuille entière, les polices sont
toujours déclarées. `scripts/construire_pages.py` les écrit dans le `<style>` de
`moteur/page.html`.

La feuille entière se charge sans bloquer l'affichage : déclarée pour
l'impression (`media="print"`), elle devient effective une fois chargée, par son
`onload` ou par le routeur — ce qui tient sous une politique de sécurité qui
refuse les gestionnaires en ligne —, et le `<noscript>` la charge sans script.
`tests/test_ecrans.py` vérifie que chaque page se peint avec son seul style comme
avec la feuille entière.
