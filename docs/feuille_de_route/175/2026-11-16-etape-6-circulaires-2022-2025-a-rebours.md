# Étape 6, circulaires de 2022 à 2025 : la lecture à rebours range les 27 références sans thème de ces quatre années

**Reprise, au 16 novembre 2026.** Une seconde lecture des circulaires sans thème
avance à rebours, de 2026 vers le passé, pendant que la première avance depuis
2008. Ce bloc est le sien ; celui de la lecture chronologique reste sous sa note.
2026 à 2022 sont faites : 29 références, un écart neuf, la revalorisation de 10 %
des salaires de Mayotte. Viennent ensuite 2021 (9 circulaires), 2020 (7), 2019
(10), 2018 (8), 2017 (30). Les deux lectures s'arrêtent où elles se rejoignent.
Méthode : celle de la note de 2007, la base relue par l'API, chaque texte lu en
entier, chaque citation retrouvée par script dans le texte servi. Détail ici.

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2022 à 2025 : 27 (6 en 2022, 7 en 2023,
  11 en 2024, 3 en 2025).
- *La lecture* : les 27, relues par l'API le 16 novembre 2026 vers 12 h 50 UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies, toutes en PDF lus au site
  (`/Pdf/<nom>`) par leur texte (`pdftotext`), 383 Ko de texte, lus par la session
  elle-même, sans agent. Deux exceptions à la lecture ligne à ligne : les instructions
  sur la déontologie des organismes (n° 2022/185 et 2023/62, 33 pages) ont été lues par
  leur plan et par recherche (ni « pension » ni « trimestre » n'y figurent), et les
  tableaux mois par mois de l'annexe 2 de la circulaire n° 2023/19 par sondage. Les
  citations de cette note ont été retrouvées mot pour mot, par script, dans le texte
  servi (blancs normalisés).
- *Les sorts* : 27 références rangées, 17 `limite`, 10 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 27 lignes, les colonnes
  `sort` et `renvoi` seules). Une raison neuve : la revalorisation des prestations
  d'invalidité, d'accident du travail et de décès (instruction n° 2022/221).

**Par ce qu'elles disent.**

- *En `limite`* : l'âge légal et la durée de la réforme de 2023 (circulaire Cnav
  n° 2023/19, annulée par la n° 2024-25) ; la revalorisation des pensions de 2024, 2025
  et 2026, 1,053, 1,022 et 1,009 (instructions n° 2023/189, 2024/176 et 2025/174),
  conformes à `legislation/revalorisation_pensions.csv` ; les seuils de la CSG des
  pensions de 2023 à 2026 (lettres du 12 décembre 2022 et du 23 novembre 2023,
  instructions du 4 décembre 2024 et du 11 décembre 2025), conformes à
  `legislation/csg_pensions_seuils.csv` et, pour 2026, à la fiche
  `csg_des_pensions_selon_le_revenu.yaml` (ligne 71) ; les incidences du SMIC de 2025
  (n° 2024/40) ; les droits des micro-entrepreneurs depuis octobre 2022 (n° 2023/4),
  que `micro_social_abattement.yaml` cite déjà ; l'assiette minimale des indépendants à
  450 SMIC horaires depuis 2023 (n° 2024/24), que `assiette_minimale_independants.yaml`
  porte ; les plafonds des veuves de guerre de 2023 (n° 2023/2) ; le service national
  réputé cotisé de la carrière longue (n° 2022/25) ; les TUC et stages d'insertion, « un
  trimestre acquis pour 50 jours de stage » (instruction n° 2023/167), que
  `stages_formation_professionnelle.yaml` porte ; la régularisation des cotisations
  prescrites des artistes-auteurs (circulaire ministérielle n° 2022/206), déclarée hors
  du modèle (`docs/limites/3-systeme-actuel.md`, ligne 318) ; le salaire annuel moyen de
  la pension communautaire sous la liquidation unique (instruction n° 2024/130) ; la
  revalorisation de 10 % des salaires de Mayotte (n° 2024/5), plus bas.
- *Hors modèle* : les formulaires et scénarios de l'accord avec la Serbie (4 annexes de
  la n° 2024/20) ; la déontologie des organismes (2) ; les taux de change (n° 2022/5) ;
  les avantages en nature (n° 2024/10) ; le service de l'ASPA aux personnes sans régime
  de base, transféré à la MSA (n° 2025/21) ; la revalorisation anticipée de 4 % des
  pensions d'invalidité et des rentes d'accident du travail en juillet 2022
  (instruction n° 2022/221).

**Les montants relus.** Conformes : les coefficients de revalorisation des pensions de
2024 à 2026 ; les seuils de la CSG de 2023 à 2026 ; l'assiette minimale des indépendants
de 2023 et 2024 ; le SMIC horaire de 2025, 11,88 €. Deux montants de la n° 2024/40 que
la série ne reprend pas, parce que la circulaire Cnav n° 2025/8, qui l'annule, les a
refaits : le minimum contributif de 2025, que la n° 2024/40 revalorise « par application
du coefficient de 1,02 » (8 972,30 € et 10 723,88 € par an), quand
`legislation/minimum_contributif.csv` (lignes 45, 107 et 130) suit la n° 2025/8 et son
coefficient de 1,0197 (8 969,66 € et 10 720,72 €) ; le plafond du minimum tous régimes au
1er novembre 2024, 1 394,86 € par mois au texte, 1 394,44 € à la série (16 733,28 € par
an). La série suit le texte qui remplace : conforme.

**Un écart neuf** (candidat), pour les sessions du modèle, sans y toucher.

- *La revalorisation de 10 % des salaires portés au compte à Mayotte.* Circulaire Cnav
  n° 2024/5, d'après la loi n° 2023-270 (article 19, III) et le décret n° 2023-966
  (article 2, III) : les salaires portés au compte avant le 1er septembre 2023 qui
  servent au salaire annuel moyen « font l'objet d'une revalorisation exceptionnelle » ;
  « Le montant de la revalorisation exceptionnelle est de 10%. » ; « La mesure de
  revalorisation des salaires s'applique pour toutes les retraites personnelles de base
  attribuées à compter du 1er septembre 2023. » Le salaire relevé reste écrêté au
  plafond de Mayotte (« ne doit donc pas avoir pour effet de retenir un salaire annuel
  qui soit supérieur audit plafond »), puis se revalorise comme les autres ; « Cette
  mesure ne doit pas conduire à valider des trimestres d'assurance supplémentaires. » Ni
  la fiche `mayotte_pension_de_base.yaml` (ses versions et ses approximations, lignes
  246 à 318) ni la fiche de régime `cssm_mayotte.yaml` ne la portent, et le calcul du
  salaire annuel moyen (`moteur/js/droit/liquider.js`, lignes 2233 à 2242, et son jumeau
  `src/retraite_notionnelle/droit/liquider.py`, lignes 3030 à 3045) n'applique au salaire
  de Mayotte que le plafond de sa caisse. Effet : pour un salarié de Mayotte dont la
  pension prend effet depuis le 1er septembre 2023, le salaire annuel moyen simulé est
  jusqu'à 10 % trop bas sur les années d'avant septembre 2023 restées sous le plafond,
  et sa pension d'autant, hors minimum ; non chiffré sur la population.

**Candidats plus étroits**, non trouvés déclarés, à trancher au texte.

- *La durée de référence de la réversion d'un assuré mort avant son départ, autour du
  1er septembre 2023.* Circulaire n° 2023/19, point 6.6 : la durée est celle de la
  génération du défunt à la date d'effet de la réversion ; « Si la date d'effet de la
  retraite de réversion est antérieure au 1er septembre 2023, il convient de retenir la
  durée de référence qui aurait été opposable à l'assuré décédé » avant la réforme (169
  et non 172 pour un défunt né en 1965). `reversion.yaml` (lignes 1158 à 1173) déclare la
  même règle à la bascule du 1er septembre 2026, non à celle de 2023, et dit que le
  modèle prend les règles du jour du décès : un décès d'avant septembre 2023 dont la
  réversion prend effet après recevrait l'ancienne durée, quand la caisse prend la
  nouvelle.
- *Le salaire annuel moyen de la pension communautaire de 2017 à 2022.* L'instruction
  n° 2024/130 tient la fin de la réduction au prorata pour applicable depuis la
  liquidation unique, au 1er juillet 2017, et ne fait pas réviser les pensions liquidées
  depuis : « Dès lors que le calcul initial devrait être plus favorable, ces droits ne
  doivent pas être révisés. » `pension_proratisee.yaml` (version `salaire_moyen_lura_2022`)
  la date du 1er juillet 2022, comme la caisse (circulaire n° 2021/33) : le modèle suit
  la caisse, ce que le scénario 1 demande.
- *Le service national réputé cotisé « y compris si service national accompli en temps
  de guerre »*, et les périodes indemnisées par la Caisse des Français de l'étranger
  (n° 2022/25, mise à jour des fiches 3.16, 3.17 et 3.29 de la circulaire n° 2017-01) :
  `carriere_longue_reputes_cotises_autres.yaml` ne nomme ni l'une ni les autres, et les
  périodes de guerre sont déclarées hors du modèle (`docs/limites/3-systeme-actuel.md`,
  ligne 377).

**Points non tranchés, les sorts retenus.** En `hors_modele`, quand `limite` se
défendrait : les avantages en nature (n° 2024/10), que la circulaire applique aux
ressources des allocations du minimum (R. 815-26) plus qu'au salaire, rangés avec la
raison de leurs devancières ; l'annexe 4 de l'accord avec la Serbie, sur les soins de
santé, rangée avec ses trois sœurs plutôt qu'à l'assurance maladie. En `limite`, quand
`hors_modele` se défendrait : la régularisation des artistes-auteurs (une procédure de
rachat) et l'instruction sur les TUC (une liste de pièces justificatives).

**Ce que la base sert de travers.**

- Quatre circulaires annulées, servies comme textes vivants : la n° 2023/19, « Annulée
  et remplacée par la circulaire 2024-25 du 01/08/2024 » ; la n° 2024/40, par la
  n° 2025/8 ; la n° 2023/4, par la n° 2024/23 « à compter du 01/07/2024 » ; la
  n° 2023/2, par la n° 2023/10.
- L'instruction du 11 décembre 2025 garde de l'année précédente la note de sa première
  annexe : la cotisation maladie « est due sur la seule base du RFR 2023 », pour 2024 ;
  son annexe 3 répète la colonne des revenus de 2023 en quatre blocs identiques, au lieu
  des seize couples de l'annexe de 2025.
- La n° 2024/10 s'intitule « Ressources-Evaluation des avantages en nature au 1er
  janvier 2024 » en tête de sommaire, et « au 1er janvier 2023 » partout ailleurs.
- Le registre nomme la n° 2023/4 « Circulaire 2023/4 », sans « Cnav » ; l'instruction n° 2023/167 y est sous un nom qui finit par
  une espace (`instruction_ministerielle_2023_167_19102023 .pdf`).

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. La loi n° 2023-270 (article 19,
III) et le décret n° 2023-966 n'ont pas été relus au Journal officiel ; les circulaires
qui remplacent celles-ci (n° 2023/10, 2024/23, 2024-25, 2025/8) ne sont pas de cette
lecture ; les moteurs n'ont tourné sur aucun cas.
