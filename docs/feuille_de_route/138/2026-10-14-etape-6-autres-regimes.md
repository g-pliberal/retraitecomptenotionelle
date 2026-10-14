# Étape 6, quatrième partie : la pension minimum d'avant 1983 aux autres régimes, et le cumul

**La demande.** La session n° 5 du 14 octobre 2026 : « la pension minimum
d'avant avril 1983, portée cette nuit au régime général : les autres régimes et le
cumul, puis, si la session le permet, l'AVTS de R. 732-70, dans les deux
moteurs, texte en main ». Le point 2 de « Ce qui reste » de la troisième partie
(`2026-10-14-etape-6-pension-minimum.md`). La règle d'avant 1976 attend les
fac-similés du propriétaire : non touchée.

**Ce que disent les textes, lus dans les index LEGI et JORF** (journal de veille
`2026-10-14-action-138-etape-6-autres-regimes.yaml`).

- *Les salariés agricoles* : le décret n° 50-1225, article 55-5, II, depuis le
  30 juin 1976 (55-7 en décembre 1982), recopie le texte du régime général —
  soixante trimestres « accomplies dans le régime des assurances sociales
  agricoles », des soixantièmes en dessous. Ce que le modèle présumait : rien ne
  change au calcul, la fiche le dit lu.
- *Les artisans et les commerçants* : le décret n° 73-937, article 7, rédaction
  du 5 mars 1976 : « Le minimum de base prévu à l'article L. 345 […] est attribué,
  au titre des périodes d'assurance postérieures au 31 décembre 1972, dans les
  conditions fixées par le II de l'article 70-2 du décret du 29 décembre 1945 » ;
  et, s'il y a des périodes d'avant 1973, il ne peut « porter à un montant
  supérieur à celui du minimum de base entier le montant cumulé » de la pension
  d'après 1972 et de l'avantage d'avant 1973.
- *Le cumul* : chaque texte proratise sur les trimestres de son régime ; aucun
  texte lu ne borne la somme de deux pensions portées au minimum. Avant le
  1er juillet 1974 au régime général, la coordination des salariés et des
  non-salariés (décret n° 58-436, article 4, abrogé pour le régime général par le
  décret n° 75-109) portait la fraction de chaque régime au minimum « réduit au
  prorata de la durée des périodes accomplies sous ledit régime par rapport à la
  durée totale ». Le décret n° 51-820 (agricole et non agricole) ne partage ainsi
  que le minimum de la réversion.

**Ce qui est fait.**

- *La fiche `minimum_contributif`* : les deux versions d'avant 1983 servent la
  pension minimum aussi chez `cancava` et `organic`, un paramètre de plus,
  `alignes_en_1973`, portant la règle de l'article 7 ; la version de 1976 cite
  les deux décrets ; deux écarts déclarés (la part d'après 1972 lue au prorata des
  trimestres ; la coordination de 1958) ; la question de `a_relire` récrite.
- *Les régimes* : `cancava.yaml` et `organic.yaml` déclarent l'avantage de 1973
  à 1982.
- *Les deux moteurs* : `complement_des_alignes` (`complementDesAlignes`) porte la
  part d'après 1972 de la pension — la pension au prorata des trimestres d'après
  1972, faute de la pension d'avant 1973 à part (étape 18) — aux soixantièmes de
  ces seuls trimestres, sans porter le total au-delà du minimum entier s'il y a des
  trimestres d'avant 1973. Avant le 1er avril 1983, le taux plein qui ouvre le
  minimum est la pension qu'aucun abattement ne réduit, pour ces régimes aussi
  (`liquider`), dont la fiche ne porte pas l'ajournement.
- *Les tests* (`tests/test_pension_minimum_avant_1983.py`) : vingt-huit
  trimestres d'artisan et de commerçant en 1981, aux 28/60 de l'AVTS ; vingt-cinq
  ans d'artisanat de 1956 à 1981, bornés au minimum entier ; l'artisan abattu à
  soixante ans, sans minimum ; deux requêtes de plus, identiques dans les deux
  moteurs.
- *L'effet* : aucun des 816 témoins ne bouge, aucune page.

**Ce qui reste**, dans l'ordre :

1. *R. 732-70* : l'AVTS au lieu du forfait (`droit/acquerir.py`), avec la série
   datée de l'AVTS prolongée jusqu'en 2026 ; à mener avec l'étape 8.
2. *Quand l'étape 18 séparera la pension d'avant 1973 des artisans et des
   commerçants*, `complement_des_alignes` lira la pension d'après 1972 et
   l'avantage d'avant au lieu du prorata.
3. *Au fac-similé* : le décret n° 73-937 avant 1976 et l'article 70-2 du décret
   n° 45-0179 auquel il renvoie ; le décret n° 50-1225 avant le 30 juin 1976 ; la
   coordination de 1958, à modéliser si l'on veut les départs d'avant juillet 1974.
4. Les autres points de l'étape : l'outre-mer ; avant 1946, la retenue ; la rente
   de 1940 et celle des retraites ouvrières et paysannes.
