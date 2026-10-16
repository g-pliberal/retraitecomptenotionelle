# Étape 2, quatrième partie : Saint-Pierre-et-Miquelon, lu et mis en fiche

**Le 16 octobre 2026 : une fiche de règles, `approchee`, pour le régime calculé
de la caisse de prévoyance sociale de l'archipel, qui n'avait que la fiche
générique de liquidation — `saint_pierre_et_miquelon_pension_de_base`, en
quatre versions. Aucun moteur, aucun chiffre ne bouge. La lecture corrige la
ligne d'inventaire : les taux de cotisation qu'elle disait absents de l'index y
sont écrits.**

Demande : la vague du 16 octobre, session 12, « action 145, étape 2.
Saint-Pierre-et-Miquelon d'abord (loi n° 87-563, dans l'index), lu à la source
et mis en fiche, documenté sans être calculé ».

- *La méthode.* L'index LEGI du dépôt, mis à jour au 15 octobre, lu article par
  article, rédaction par rédaction : la loi n° 87-563, le décret n° 89-110, le
  décret n° 96-72, le décret n° 2017-1000 ; l'index JORF pour l'ordonnance
  n° 2015-896, les arrêtés de taux et les décrets n° 2025-157 et n° 2025-159.
- *Les quatre versions.* La loi de 1987 et le décret n° 89-110, jusqu'en juin
  2016 : le taux de R. 351-27 sur le revenu moyen de toute la carrière, les
  années 1960 à 1987 au forfait de 97 000 F revalorisé, en 150es, pour 108
  trimestres en 1987 puis 150 en 1998. L'ordonnance n° 2015-896, pour les
  pensions de juillet 2016 et après : le code de la sécurité sociale adapté,
  l'âge et la durée décalés de sept générations, le revenu moyen de quarante à
  vingt-huit années avant la génération 1962, la surcote de 1,25 %. La réforme
  de 2023 (septembre 2023) et la suspension de 2026 (mars 2026), que la fiche
  de régime porte déjà par ses tables `spm_2023` et `spm_2026`.
- *Ce que le modèle ne fait pas*, et que la fiche nomme :
  1. **Le revenu moyen avant juillet 2016** est celui de toute la carrière
     (décret n° 89-110, art. 8) ; la fiche de régime prend les dix meilleures
     années. Les années 1960 à 1987, au forfait, ne sont pas portées.
  2. **Depuis juillet 2016**, quarante à vingt-huit années pour les nés avant
     1962, et la surcote : déjà dits par la ligne d'inventaire, confirmés.
  3. **Les taux de cotisation sont écrits** : 10,5 % au 1er septembre 1989
     (arrêté du 11 juillet 1989), 11 % au 1er février 1996, 11,5 % au 1er
     janvier 1998 (arrêté du 29 janvier 1996), 11,5 % pour le non-salarié
     (arrêté du 24 septembre 1998) ; puis, depuis 2016, au plafond national,
     5,78 % et 6,08 % en 2016 jusqu'à 8,27 % et 6,82 % en 2025 (décret
     n° 89-110, art. 38-3, repris au décret n° 2017-1000, art. 6-2), les taux
     nationaux en 2026, aucune part déplafonnée avant 2027, et 0,20 % de plus
     depuis 2025 contre le chômage de la morte-saison compté dans le revenu.
     La fiche de régime prête les taux du régime général : la cotisation
     simulée est trop haute de 42 à 52 % de 1989 à 2016, de 17 % en 2025.
  La ligne d'inventaire est corrigée ; les périodes, non. Au propriétaire de
  dire si ces écarts rejoignent ceux des notes du 13 et du 14 octobre.
- *Les tests.* `test_donnees.py`, `test_carte.py`, `test_textes.py`,
  `test_regle_de_chacun.py` et la suite rapide passent. `inventaire.yaml` et
  `docs/regimes.md` sont refaits par leurs scripts. `textes.py --inscrire`
  n'est pas lancé : une autre session tient la liste cette nuit.
- *Ce qui devrait s'écrire dans les pages*, pour la session qui les tient :
  rien en dur ; la page Données lit la ligne d'inventaire corrigée.
- *Ce qui reste de l'étape 2.* La CAFAT, les deux tranches de la CPS de
  Polynésie, Wallis-et-Futuna, les fonctionnaires du Pacifique, dont les textes
  sont des délibérations locales hors de l'index (Juridoc, LexPol, Journal
  officiel de Wallis-et-Futuna) ; puis les hors champ (CRFM de Mayotte, élus
  du Pacifique, régies ferroviaires d'outre-mer) ; puis les limites de l'étape
  (`docs/limites/4-regimes-incomplets.md`), une fois, à sa fin. À lire pour
  l'archipel : le forfait des années 1960 à 1987 depuis 2016, le plafond local
  de 1987 à 2015, le taux d'avant septembre 1989, la réversion et les
  allocations minimales.
