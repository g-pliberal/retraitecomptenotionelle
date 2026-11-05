# Étape 17, suite : les pages du JO lues au fac-similé, sur la release, sans numéro entier

**Le 5 novembre 2026, la demande.** Le propriétaire, depuis son poste : « On peut
mettre les documents que l'on trouve dans les sessions locales dans le github en
ligne ». Les quatre JO du 11 octobre étaient restés dans `data/brut/jo/`, et une
session du cloud ne pouvait relire aucune des pages que les fiches citent.

**Ce qui a été fait.** La licence d'abord : le pied de page de Légifrance, ses
mentions légales et sa page « Open data et API », lus dans le navigateur du poste :
Etalab 2.0 sauf mention contraire. Puis `jo_fac_similes_extraits.zip` sur la release
`documents-apportes`, quatre pages (p. 2236 de 1948, p. 2019 de 1949, p. 3200 de 1965,
p. 3751 de 1970), déclarées au manifeste une à une, avec leur texte et leur empreinte.
L'archive s'est rapportée de la release à son empreinte, et ses quatre membres aux
leurs.

**Pourquoi des extraits.** Légifrance met ces numéros derrière une addition parce
qu'ils portent des données nominatives. Un numéro entier sur une release publique
ôterait cette protection, à des personnes qui n'ont rien demandé, et aucune fiche
n'en a besoin. Chaque page a donc été auditée : aucun particulier nommé aux trois de
1949, 1965 et 1970 ; sept à celle de 1948, dans ses deux premières colonnes. Celle-ci
est réduite à sa troisième colonne, rastérisée : un simple cadre laisserait le reste
de la page dans le fichier. Les textes se terminent chacun sur leur page.

**Ce qui reste.** L'archive grandit à chaque fac-similé lu, par la même recette :
`contenu` et `sha256` se refont, l'asset se redépose, sa ligne de release garde sa
mention. Publier un numéro entier resterait une décision du propriétaire.
