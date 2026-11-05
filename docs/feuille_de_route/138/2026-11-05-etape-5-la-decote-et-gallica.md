# Étape 5, suite : la décote de 1961 absente des débats, et Gallica, qui s'arrête trop tôt

**Le 5 novembre 2026, la demande.** « On peut tout faire », depuis le poste : la
loi qui porte la décote à 70 F et 210 F par part, le texte définitif de la loi de
finances pour 1962, et la doctrine de 1961 à 1970, que la note du 23 octobre
renvoyait à Gallica.

**Ce qui a été lu.** Les 86 comptes rendus de la session ordinaire d'octobre à
décembre 1961, à `archives.assemblee-nationale.fr` (certificat vérifié, par `curl`) :
« décote », « moitié de la différence », « 198 ter », 70 et 210 NF. Gallica, dans le
navigateur du poste, où `/SRU` et `/services/Issues` répondent sans contrôle.

**Ce que la lecture a trouvé.**

- *Les débats de 1961 ne disent pas la décote de l'impôt sur le revenu* : ses seules
  mentions sont les décotes sur stocks, la décote de 10 % des plus-values, et une
  réponse du ministre, qui ne chiffre rien. Le compte rendu du 15 décembre est le
  dernier de la session ; la troisième lecture n'y porte pas le texte cherché. Il
  reste au fac-similé : la loi de finances pour 1962, et la première partie de celle
  pour 1963 (n° 62-1529, JORFTEXT000000875162).
- *Gallica ne sert pas ces années.* Le JO, Lois et décrets, y va de 1881 à 1940, plus
  un numéro de 1948 ; ses débats, de 1880 à 1940 ; le Bulletin officiel des
  contributions directes, de 1935 à 1946. La doctrine de 1961 à 1970 n'y est pas, et
  le fac-similé de Légifrance reste seul pour les textes d'après 1948.

**Ce qui change.** La ligne `gallica_sru` de `sources_a_explorer.yaml` passe à
`explore`. Aucune valeur.

**Ce qui reste.** Au fac-similé, la décote et le taux de 6 % des revenus de 1961. La
doctrine reste sans source en ligne connue.
