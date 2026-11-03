# Le taux plein à 65 ans du parent de trois enfants né de juillet 1951 à 1955

File M4 de la quatrième vague, sur décision du propriétaire du 3 novembre 2026 : faire
calculer au modèle le troisième des « Trois écarts déclarés » de la note
`2026-11-03-etape-4-retraite-personnelle-de-base.md`. Les deux autres cas de la fiche —
l'aidant familial, le parent d'un enfant handicapé — n'étaient pas pour cette session.

**Le 3 novembre 2026, ce qui est fait.**

- *La règle, dans les deux moteurs* : l'âge du 1° de L. 351-8 que lit tout le moteur
  (`ageTauxPlein`, `moteur/js/droit/ouvrir.js` ; son jumeau `age_taux_plein`) est
  soixante-cinq ans au régime général, chez les salariés agricoles et chez les artisans et
  commerçants, pour qui remplit les conditions (`ageDuParentDeTroisEnfants` et
  `remplitPourLEnfant`, `moteur/js/droit/categories.js` ; leurs jumeaux dans
  `droit/categories.py`). La décote s'annule à cet âge et se compte jusqu'à lui ; la
  majoration de durée de R. 351-7 court après lui ; le minimum contributif, qui demande le
  taux plein, le lit : aucun autre changement n'était à faire.
- *La fiche* `taux_plein_a_soixante_cinq_ans` : trois versions datées (avant le 1er juillet
  2011 ; du 1er juillet 2011 au 1er janvier 2026 ; après), chaque texte cité par son
  identifiant et mot pour mot, la circulaire et l'exposé de la Cnav avec l'empreinte de la
  copie lue ; elle passe de `pas_encore_modelisee` à `approchee`, entre dans
  `FichesDatees.NOMS` (le paquet la porte) et dans `LUES_AU_DROIT` de `tests/test_carte.py`.
  Le cliquet des textes descend de 9 382 à 9 375 rédactions sans statut : sept rédactions
  sont désormais citées.
- *Le test* `tests/test_taux_plein_a_soixante_cinq_ans.py`, vu rouge puis vert : la fiche
  datée ; l'âge de dix-sept carrières au régime général et de trois régimes, rendu par le
  portage et refait par le jumeau (`droit_et_refait`) ; la pension de bout en bout, quatre
  requêtes du simulateur servies et refaites (`servi_et_refait`), qui ont rougi tant que le
  jumeau manquait. Aucun témoin ne bouge (`construire_temoins.py`) : aucun ne déclare ces
  naissances.
- *Les limites* : une phrase dans `docs/limites/ecarts-au-droit-positif.md`, à côté des
  autres taux pleins de L. 351-8.

**Les textes lus, et ce qu'ils décident** (citations entières dans la fiche).

- Loi n° 2010-1330, article 20, IV (LEGIARTI000023023835, seule rédaction, du 11 novembre
  2010 au 28 février 2025) : « l'âge mentionné au 1° dudit article est fixé à soixante-cinq
  ans pour les assurés nés entre le 1er juillet 1951 et le 31 décembre 1955 inclus » qui ont
  « eu ou élevé [...] au moins trois enfants », interrompu ou réduit leur activité après la
  naissance de l'un d'eux, et validé avant un nombre minimum de trimestres d'activité ;
  « applicable dans tous les régimes obligatoires de retraite auxquels s'appliquent les
  dispositions de l'article L. 351-8 ». Article 118, II (JORFARTI000023022348) : pour les
  pensions prenant effet à compter du 1er juillet 2011. Loi n° 2025-199, article 87, IV et
  VIII, A (JORFARTI000051269910) : le IV est abrogé pour les pensions prenant effet à compter
  du 1er janvier 2026.
- Décret n° 2011-620, article 2 (LEGIARTI000024111672, seule rédaction) : au plus huit
  trimestres l'année de la naissance et les deux suivantes, ou les trois suivantes pour
  l'enfant né au second semestre, sans l'AVPF (L. 381-1) ni l'invalidité et l'accident du
  travail (R. 351-12, 3° et 5°, les mêmes dans ses sept rédactions de juin 2011 à septembre
  2023) ; au moins huit les deux années qui la précèdent, cotisés ou de maladie, de
  maternité, de chômage, de formation, de rééducation ; huit trimestres d'activité avant.
- R. 351-27, I, 2°, et II (LEGIARTI000024113020) : la décote se compte jusqu'au
  « soixante-cinquième anniversaire » de qui remplit le IV, « arrondi au chiffre
  immédiatement supérieur », le plus petit des deux nombres, à « 1,25 % pour l'assuré né
  après 1952 ». R. 351-7 (LEGIARTI000024113035) : la majoration court après « l'âge de
  soixante-cinq ans ». L. 351-12 (LEGIARTI000006742643) : les enfants eus, et ceux élevés.
- Circulaire Cnav n° 2014-64 du 23 décembre 2014 (PDF de la base de législation, sha256
  f6717a0f…) : les enfants comptés comme pour la majoration de 10 % (point 2.1) ; l'activité
  avant la naissance comptée « au dernier jour du trimestre civil précédant la date de la
  naissance », périodes assimilées exclues (2.2.2, 2.2.3) ; les deux fenêtres et leurs
  exemples (2.3.1, 2.3.2) ; avant 65 ans, la décote comptée jusqu'au 65e anniversaire (4).
- Exposés de la Cnav « Taux plein à 65 ans » (version du 18 septembre 2026) et « Taux de la
  retraite personnelle » (version du 29 juillet 2026) : la même règle, et l'âge du taux plein
  de chaque génération, « 1953 66 ans et 2 mois », « à partir de 1955 67 ans », « du
  01/07/1951 au 31/12/1951 65 ans et 4 mois ».

**Chaque condition, et ce que le simulateur en connaît.**

| Condition | Ce que la saisie demande | Ce que le modèle en fait |
|---|---|---|
| Né du 1er juillet 1951 au 31 décembre 1955 | l'année et le mois de naissance | lue |
| Trois enfants eus ou élevés | le nombre des enfants | lue, comme la majoration de 10 % ; les neuf ans d'éducation de l'enfant non né de l'assuré, présumés (approximation) |
| L'interruption ou la réduction : au plus 8 trimestres dans la fenêtre, au moins 8 les deux années d'avant | la carrière année par année, ses interruptions et leur motif, et la naissance de chaque enfant, au mois ou à l'année | lue sur les lignes de la carrière ; une naissance présumée ne l'ouvre pas, une naissance dite à l'année l'ouvre si les conditions tiennent quel que soit son mois, l'adoption n'est pas saisie (approximations) |
| 8 trimestres d'activité avant | la même carrière | lue sur les années d'emploi ; les périodes européennes, les rachats, la formation ne sont pas saisis (approximation) |

Aucune condition décisive ne manque au formulaire : la naissance des enfants y est
demandée, au mois, à qui veut la dire. Rien n'a été changé au site.

**Les calculs posés à la main**, pour chaque valeur que le test attend. L'assurée naît le 15
mars 1953 sauf mention, part à 65 ans — sa pension prend effet le 1er avril 2018, dans la
version de 2011 —, travaille chaque année de 1973 à 2017 (quatre trimestres), sauf ce que le
cas dit ; trois enfants, nés en avril 1980, mai 1984, juin 1986 sauf mention. « Avant » : les
deux années qui précèdent celle de la naissance ; « fenêtre » : l'année de la naissance et
les deux suivantes (premier semestre) ou les trois suivantes (second) ; « activité » :
l'emploi des années d'avant, plus, l'année de la naissance, les trimestres civils écoulés
avant le sien (au plus ses trimestres d'emploi).

- *Interrompue trois ans* (aucune ligne de 1980 à 1982) : avant, 1978 + 1979 = 4 + 4 = 8 ≥ 8 ;
  fenêtre 1980-1982, 0 ≤ 8 ; activité, 1973-1979, 7 × 4 = 28 ≥ 8 : **65 ans**.
- *À l'AVPF trois ans* : les douze trimestres de l'AVPF ne comptent pas (L. 381-1) ;
  fenêtre 0 : **65 ans**. *En invalidité trois ans* : de même (R. 351-12, 3°) : **65 ans**.
- *En arrêt maladie trois ans* : la maladie compte, fenêtre 12 > 8 ; l'enfant de 1984 (fenêtre
  1984-1986, 12) et celui de 1986 (12) non plus : l'âge de la génération, **66 ans et 2
  mois**. *Sans interruption* : chaque fenêtre, 12 : **66 ans et 2 mois**.
- *Deux enfants* : 2 < 3 : **66 ans et 2 mois**. *Naissances non dites* : aucune naissance
  déclarée : **66 ans et 2 mois**.
- *À l'année, les deux fenêtres* (nés « 1980 », « 1984 », « 1986 », aucune ligne de 1980 à
  1982) : avant 8 ; fenêtre du premier semestre 1980-1982, 0 ; du second, 1981-1983,
  0 + 0 + 4 = 4 ; activité des années d'avant 1980, 28 : **65 ans**.
- *Septembre, 1983 seule* (née en septembre 1980, aucune ligne en 1983) : avant 8 ; fenêtre
  1981-1983, 4 + 4 + 0 = 8 ≤ 8 ; activité 28 + min(4, 2) = 30 : **65 ans**. *Mars, 1983
  seule* (née en mars 1980) : fenêtre 1980-1982, 12 ; l'enfant de mai 1984 : avant, 1982 +
  1983 = 4 + 0 = 4 < 8 ; celui de 1986 : fenêtre 12 : **66 ans et 2 mois**. *À l'année,
  1983 seule* : la fenêtre du premier semestre de 1980, 12 ; « 1984 », avant 4 ; « 1986 »,
  fenêtre 12 : **66 ans et 2 mois**.
- *Chômage, novembre* (un trimestre d'emploi en 1972, le chômage indemnisé en 1973, l'emploi
  en 1974 et 1975, aucune ligne de 1976 à 1978 ; premier enfant né en novembre 1975, les
  autres en avril 1980 et 1982) : avant, 1973 + 1974 = 4 + 4 = 8, le chômage compris ;
  fenêtre 1976-1978, 0 ; activité 1 + 0 + 4 + min(4, 3) = 8 — le décompte de l'exemple 2 de la
  circulaire, point 2.2.2 : **65 ans**. *Chômage, septembre* (né en septembre 1975) : activité
  1 + 0 + 4 + min(4, 2) = 7 < 8 ; l'enfant d'avril 1980, avant 0 + 4 = 4 ; celui d'avril 1982,
  fenêtre 12 : **66 ans et 2 mois**.
- *Née en juillet 1951* (au travail de 1971 à 2015, nés en avril 1978, mai 1982, juin 1984,
  aucune ligne de 1978 à 1980 ; effet le 1er août 2016) : avant 8, fenêtre 0, activité 28 :
  **65 ans** ; sans interruption, **65 ans et 4 mois**. *Née en décembre 1955* (de 1975 à
  2019, nés en avril 1982, mai 1986, juin 1988, aucune ligne de 1982 à 1984 ; effet le 1er
  janvier 2021) : **65 ans**. *Née en janvier 1956* : hors des générations, **67 ans**.
- *Les régimes* : le même cas que le premier, aux salariés agricoles et au RSI, **65 ans** ;
  à l'Arrco de 2018, l'âge de la génération, **66 ans et 2 mois**.
- *De bout en bout* : née le 15 mars 1953, au travail dès dix-huit ans, sans activité de
  1976 à 1999, trois enfants nés en avril 1976, juin 1978 et juin 1980 ; l'enfant de 1976
  remplit les conditions (avant, 1974 + 1975 = 8 ; fenêtre 1976-1978, 0 ; activité 1971-1975).
  À 65 ans, aucun trimestre jusqu'à 65 ans : **taux 50 %**. Sans la dérogation (deux
  enfants), 14 mois jusqu'à 66 ans et 2 mois, 4,67 arrondis à **5 trimestres**, moins que ceux
  qui lui manquent pour la durée requise (le détail du modèle en affiche 116 sur 165, que le
  test n'affirme pas) : 50 % × (1 − 5 × 1,25 %) = **46,875 %**. À 64 ans, 4 trimestres
  jusqu'à 65 ans : 50 % × (1 − 4 × 1,25 %) = **47,5 %** ; sans elle, 26 mois, 8,67 arrondis à
  9 : 50 % × (1 − 9 × 1,25 %) = **44,375 %**. La table du modèle écrit 66,17 pour 66 ans et 2
  mois : le test compare les âges au centième.

**Ce qui reste, et qui n'est pas de cette file.**

- *Les complémentaires* : l'Ircantec sert sans coefficient l'agent qui a ce taux plein à
  65 ans (arrêté du 30 décembre 1970, article 16, I, 3°, d, LEGIARTI000037845437) ; le modèle
  l'abat encore jusqu'à l'âge de sa génération. L'Agirc-Arrco garde l'âge de la génération :
  ni l'accord du 18 mars 2011 ni celui du 17 novembre 2017, tels que la fiche
  `coefficients_anticipation_agirc_arrco` les cite, ne nomment ces parents ; à relire dans
  leur texte. Je n'ai rien changé au code des complémentaires.
- *Les autres régimes de base* qui ont le même âge : les non-salariés agricoles (article 21,
  IV), les professions libérales (R. 643-7) et les avocats (R. 723-38), que le décret
  n° 2011-620, article 4, 14° et 16°, y porte ; leurs rédactions de 2016 à 2022 restent à
  lire avant de les ajouter aux `regimes` de la version.
- *Le site*, file fermée : l'aide du champ « Naissance des enfants » pourrait dire qu'au mois,
  la naissance décide de ce taux plein. Je n'y ai pas touché.
- De la note du premier thème de l'étape 4, la garantie de D. 173-2 et la revalorisation des
  pensions d'invalidité restent à la session du modèle.
