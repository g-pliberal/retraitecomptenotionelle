# Retouches de la relecture R-K-ter : « sans source ni note », D. 732-77 et le décret n° 86-1084, le 17,37 % après 2025

Vague 7, le 5 novembre 2026. La relecture R-K-ter
(`2026-11-04-relecture-retouches-r-k-bis.md`, commit d9d2096) trouve les taux de la
cotisation agricole de 2003 à 2025, déclarés par K-ter, conformes : deux écarts faibles et
une observation. Cette note les reprend. La fiche
`data/reference/regles/cotisation_vieillesse_agricole_avant_2003.yaml` change de texte ;
aucun taux du modèle, aucune règle, aucune donnée, aucun test ne change.

**Pièces rouvertes pour cette note** : l'index LEGI à jour au 4 novembre 2026 (table `doc`,
en lecture seule) ; `data/sources.yaml` ; `data/reference/regimes/msa_non_salaries.yaml`, et
le même fichier au commit bdaecdbc du 8 septembre 2026, sous son nom d'alors
(`non_salaries.yaml`, `git show bdaecdbc:…`). Le clone de la session, superficiel, n'avait
pas ce commit : il a été approfondi (`git fetch origin main --deepen=3000`).

## 1. « Sans source ni note » est trop fort

La fiche (question R-K-bis, `sources.a_relire`) écrivait du 17,37 % qu'il « naît, avec les
8,5 % d'avant, sans source ni note, le 8 septembre 2026 ». Au commit bdaecdbc (8 septembre
2026), `non_salaries.yaml` portait, pour le régime `msa_non_salaries` :

- `source_id: msa_parametres` et `fiabilite: moyenne` ; `data/sources.yaml` donne à cette
  source le titre « Paramètres des régimes agricoles (RCO, points, AVA) » et l'adresse
  `https://www.msa.fr/` (la page d'accueil de la MSA, que R-K-bis nommait) ;
- à la période de 1952 à 2002, `taux_cotisation_retraite: 0.085` et une note sur la loi du
  10 juillet 1952 (retraite en deux parts) qui ne justifie pas le 8,5 % ;
- à la période de 2003 sans fin, `taux_cotisation_retraite: 0.1737` et une note qui dit : « le
  taux de 17,37 % qui figure ici n'a jamais compris les 4 % de la RCO, qui s'y ajoutent ».

Le fond tient : aucun texte lu ne fixe le 17,37 %, et la note ne le justifie pas. Ce qu'il
faut lire : **sans texte qui le fixe ni note qui le justifie**, sur un régime qui portait la
source générale `msa_parametres`. La fiche est corrigée en ce sens. Son écart de l'approximation
`depuis_2003`, qui commence par « LE TAUX DE 17,37 % N'A AUCUNE SOURCE », dit maintenant ce que
« source » y veut dire : aucun texte, aucune page précise, la source générale du régime étant la
page d'accueil de la MSA.

*Non touché, signalé* : les notes de `msa_non_salaries.yaml` (K-ter, commit 3b06c54) répètent
« LE TAUX DE 17,37 % N'A AUCUNE SOURCE » aux quatre périodes de 2003 à 2025. C'est un fichier
de données, dont le paquet porte les notes ; il n'est pas de cette tâche.

## 2. D. 732-77 et le décret n° 86-1084, article 2

La note de K-ter (`2026-11-04-retouches-de-la-relecture-r-k-bis.md`, § 5) dit que, pour P entre
19,51 et 27,34, « le modèle applique la formule « T % = 3,19 x P - 57,23 » de D. 732-77
(LEGIARTI000006597491) ». Les deux textes, rouverts dans l'index :

- **D. 732-77** (LEGIARTI000006597491, du 22 avril 2005 au 1er janvier 2026) : « 1° 5 % lorsque
  le nombre annuel moyen de points acquis par les intéressés au cours de cette période est
  compris entre 15 et 19,51. Le taux est déterminé par la formule suivante : T % = 3,19 x P -
  57,23 2° 5 à 30 % et de 30 à 45 % selon que le nombre annuel moyen […] est compris entre 19,51
  et 27,34 ou est supérieur à 27,34. Le taux est alors déterminé par la formule : T % = 1,93 x
  P - 22,74 ». La codification place la première formule après le 1°, la seconde après le 2° :
  prise telle quelle, la formule de 3,19 P − 57,23 semble celle du 1°, de 15 à 19,51.
- **Décret n° 86-1084, article 2** (LEGIARTI000006769405, du 8 octobre 1986 au 22 avril 2005) :
  « 5 à 30 p. 100 et de 30 à 45 p. 100 selon que le nombre annuel moyen […] est compris entre
  19,51 et 27,34 ou est supérieur à 27,34. Dans le premier cas, le taux est déterminé par la
  formule suivante : T p. 100 = 3,19 P - 57,23 Dans le second cas, il est déterminé par la
  formule : T p. 100 = 1,93 P - 22,74 ». **C'est ce texte qui apparie** la première formule au
  « premier cas » du 2° (de 19,51 à 27,34) et la seconde au « second cas » (au-delà) ; D. 732-77
  l'a codifié en perdant l'appariement.

Il fallait donc citer le décret n° 86-1084, article 2, avec D. 732-77 : « la formule « T p.
100 = 3,19 P - 57,23 » du « premier cas » du 2° de l'article 2 du décret n° 86-1084
(LEGIARTI000006769405), que D. 732-77 (LEGIARTI000006597491) codifie en la plaçant sous le
1° ». L'arithmétique de K-ter (6,672 %, 19,452 %, 12,78 points) ne change pas ; sa référence
devient celle-là. **La fiche `retraite_proportionnelle_msa` le dit déjà** (l. 106 à 111 : « le
moteur suit sa source, l'article 2 du décret n° 86-1084 (« Dans le premier cas » et « Dans le
second cas » du 2°) ») ; l'écart était dans la note, qui est un récit : un renvoi daté vient,
à son bout, vers celle-ci. La fiche de la cotisation reçoit la lecture des deux textes, dans ses
`sources.lectures`.

## 3. Le 17,37 % court aussi après 2025

`msa_non_salaries.yaml` porte `taux_cotisation_retraite: 0.1737` aux périodes de 2026 à 2027 et
de 2028 sans fin, qui n'ont pas la note des périodes de 2003 à 2025. Ce que les textes disent
du taux depuis 2026, rouvert :

- **D. 731-121** depuis le 1er janvier 2026 (LEGIARTI000053296666) : « Les taux applicables à
  la cotisation prévue au 1° de l'article L. 731-42 sont égaux à ceux fixés respectivement au I
  de l'article D. 633-3 du code de la sécurité sociale pour la part calculée sur l'assiette
  retenue dans la limite du plafond mentionné au premier alinéa de l'article L. 241-3 du même
  code et au II du même article pour la part calculée sur la totalité de l'assiette » ; le
  même article précise que ces dispositions, « dans leur rédaction résultant de l’article 4 »
  du décret n° 2025-1417 du 30 décembre 2025, « entrent en vigueur le 1 er janvier 2026 et
  s'appliquent aux cotisations dues au titre des périodes courant à compter de cette date » ;
- **D. 633-3**, depuis le 7 juillet 2024 (LEGIARTI000049904636) : « I.-Le taux des cotisations
  assises sur l'assiette de cotisations dans la limite du plafond est fixé à 17,15 %.
  II.-Le taux des cotisations assises sur la totalité de l'assiette de cotisations est fixé à
  0,72 %. »

17,15 % et 17,15 + 0,72 = 17,87 % ne sont pas 17,37 %. **Ce que cette lecture ne tranche pas** :
la structure de L. 731-42 en 2026 (quelle cotisation est « le 1° ») et le décret n° 2025-1417,
dont D. 731-121 dit qu'il la fonde, ne sont pas relus ici ; c'est une piste, non une lecture.
La fiche le dit à l'`effet` de l'approximation `depuis_2003` (« Depuis 2026, non lu ici » est
remplacé), avec une lecture du 5 novembre aux `sources`. Le taux du modèle n'est pas changé, et
la question au propriétaire de K-ter ne change pas : elle vaut aussi pour 2026 et après.

## Signalé, non fait

- Les notes des périodes de 2026 à 2027 et de 2028 sans fin de `msa_non_salaries.yaml` (données ;
  leurs notes entrent dans le paquet) ne disent rien du 17,37 % : à la session qui touche ce
  fichier, avec le décret n° 2025-1417 et L. 731-42 lus.
- Le décret n° 2025-1417, article 4 (qui récrit D. 731-121) et son article 5, I et II, ne sont
  pas relus : le texte du décret est au JORF, non ouvert ici.
