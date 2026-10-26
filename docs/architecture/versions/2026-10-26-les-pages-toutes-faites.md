# Version du 26 octobre 2026 : les pages toutes faites

Chaque page du site est écrite toute faite : le HTML que le serveur envoie porte
déjà son titre, sa description, son adresse canonique, son texte, ses tableaux
et ses graphiques, pour ses réglages par défaut (note de décision 0004,
action 174, étape 4 (c)). La page se lit et s'affiche sans le moteur ; le
routeur ne fait que l'animer, et ne va chercher le paquet de données, ni ne
construit le simulateur, que pour ce qu'elle ne porte pas : des réglages ou une
carrière derrière le `#`, une saisie retenue, un tracé qui ne convient plus à
la colonne.

`scripts/construire_pages.py` fabrique les neuf pages — l'accueil à la racine,
les huit autres chacune dans son dossier — et `sitemap.xml`, depuis la coquille
`moteur/page.html` et le rendu de `moteur/js/pages.js` ; `index.html` n'est plus
la source des huit autres. `regenerer.py` les refait, `.gitattributes` les
déclare fabriquées. L'adresse canonique de chaque page est celle de la copie du
parti, `partiliberalfrancais.fr/retraite/…`.

Ce qui dépend de l'écran — les graphiques de Coût et de Droits non cotisés, les
deux schémas de Sankey qu'une carte pose de front au large — est écrit deux fois
dans la page, pour une colonne de téléphone et pour le large, et la feuille de
style en montre un seul. Un dessin convient à la colonne à 12 % près
(`tracesConviennent`, `moteur/js/gabarit.js`) ; au-delà, la fenêtre redessine la
page par le moteur, qui se charge alors à la demande.

L'annexe C.9 (la surface publique) dit l'adresse canonique et le plan du site.
La coquille ne demande, avant la peinture, que la feuille de style, les deux
polices et `moteur/js/routeur.js` : ni `modulepreload`, ni préchargement du
paquet.
