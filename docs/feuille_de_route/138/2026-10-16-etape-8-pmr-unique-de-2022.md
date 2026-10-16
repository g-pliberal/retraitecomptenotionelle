# Étape 8, dixième partie : la pension majorée de référence unique de 2022, servie aux pensions des exploitants prises depuis 2009

**Le 16 octobre 2026, la demande.** Le premier des restes de l'étape : « la
PMR unique de 2022 aux pensions prises depuis 2009 » (point 4 de « Ce qui
reste » de la note « points des conjoints »). Le modèle calculait la PMR d'une
pension prise de 2009 à 2021 au départ, puis la menait au coefficient : une
conjointe collaboratrice partie à PMR2 le restait à vie. Session du modèle,
une de onze.

**Ce que dit le droit** (journal de veille du 16 octobre, index LEGI et JORF).
La loi n° 2021-1679 (article 1er, II) rend la PMR unique « applicable[] aux
pensions dues à compter de [1er janvier 2022], y compris aux pensions de
retraite ayant pris effet avant cette date » (L. 732-54-2,
LEGIARTI000044522709) ; le décret n° 2021-1919 (article 2) en dit autant de
D. 732-111 et D. 732-113 : un seul montant, quel que soit le statut, et le
plafond relevé. Le montant et le plafond de septembre 2023 et de 2026 ne
nomment que les pensions prises depuis (D. 732-111, D. 732-113).

**Ce qui est fait**, dans les deux moteurs.

- *La liquidation garde sa PMR* : `ExploitantAgricole.pmr` (`exploitant.pmr`
  du jumeau), en euros de la date d'effet.
- *« Faire vivre » la refait depuis 2022* (`reviser_les_exploitants`,
  `reviserLesExploitants`, constante `PMR_UNIQUE`) : pour une pension prise de
  2009 à 2021, la PMR de la liquidation menée par le coefficient se retranche
  de la base et des ressources ; la majoration se refait à la règle des
  pensions dues de l'échéance (celle de 2022 au plus), avant surcote, écrêtée
  sur toutes les pensions ; la base porte la différence (`RegimeServi.pmr`,
  qui peut être négative quand les ressources ont crû). La durée minimale de
  D. 732-109 reste celle de la date d'effet : la règle unique n'ouvre pas une
  majoration refusée au départ, ce que les textes ne disent pas.
- *La fiche* `pension_majoree_reference` : la rédaction de 2022 de L. 732-54-2
  citée dans la version unique ; l'écart des pensions prises depuis 2009 récrit
  ; le cliquet des textes descend à 9 721.
- *Les tests* (`test_minima_agricoles.py`, deux de plus, un cas de plus dans la
  comparaison des deux moteurs) : la conjointe partie en 2016 à PMR2 et la
  carrière mêlée partie en 2019, rien en 2021, la PMR entière au montant unique
  en 2022 et 2026, la carrière complète sans surcote portée à la PMR entière ;
  quinze ans de chef partis au taux plein en 2012, sous les soixante-dix
  trimestres d'alors, sans PMR ni au départ ni en 2022.

**Les mesures**, à 30 % du salaire moyen. La conjointe collaboratrice de
quarante-quatre ans partie en 2016 : 7 991 € de base en 2021, 9 851 € en 2022
(1 449 € de plus), 10 609 € en 2026. Le chef de quarante-quatre ans parti en
2016 : 303 € de plus en 2022, PMR1 cédant au montant unique, le minimum
contributif majoré. Vingt ans de collaborateur et vingt-quatre de chef, partis
en 2019 : 7 579 € en 2021, 8 900 € en 2022, la PMR entière.

**Ce que la vérification a trouvé.** Le différentiel d'un chef parti en 2016
recule de 303 € en 2022 à 159 € en 2026 : la série de PMR suit le minimum
contributif, que la base, menée par le coefficient des pensions, devance un
peu. Rien ne l'interdit ; déclaré par l'écart récrit de la fiche.

**Ce qui reste**, de cette partie et de l'étape :

1. La révision de la majoration quand les ressources changent, de 2009 à 2021,
   et pour les pensions prises depuis 2022 (une pension étrangère qui commence
   après le départ).
2. Les restes de l'étape, inchangés : avant 1997, la révision des plans ; des
   conjoints, les pensions dues de 1998 à 2001 ; un montant de la MSA pour 2015
   à 2017 et 2019 ; le 2° de D. 732-110, II (décès du conjoint, à saisir) ; et
   les points 2 et 3 de « Ce qui reste » de la note « points des conjoints ».
