# Étape 6, circulaires de 2016 : la lecture à rebours range les 15 références sans thème de l'année

**Reprise, au 16 novembre 2026.** Une seconde lecture des circulaires sans thème
avance à rebours, de 2026 vers le passé, pendant que la première avance depuis
2008. Ce bloc est le sien ; celui de la lecture chronologique reste sous sa note.
2026 à 2016 sont faites : 108 références. Deux écarts neufs en tout : la
revalorisation de 10 % des salaires de Mayotte, et l'âge de la retraite des
exploitants agricoles de 1986 à 1989, que le modèle met à soixante ans quand la
circulaire de 1986 l'abaisse d'un an par an depuis soixante-cinq. Vient ensuite
2015 : 24 circulaires, puis 2014 (26). Les deux lectures s'arrêtent où elles se
rejoignent. Méthode : celle de la note de 2017. Détail ici.

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2016 : 15.
- *La lecture* : les 15, relues par l'API le 16 novembre 2026
  (`/reference/referencesByFileLeafRef/`), toutes servies ; quatorze en PDF lus au site
  (`/Pdf/<nom>`) par leur texte (`pdftotext`), la circulaire ministérielle n° 86/7004
  du 14 mars 1986, que le site ne sert pas en PDF, par le HTML du champ `contenu` de sa
  fiche ; lues en entier par la session elle-même, sans agent. Les citations de cette
  note ont été retrouvées mot pour mot, par script, dans le texte servi (blancs
  normalisés).
- *Les sorts* : 15 références rangées, 11 `limite`, 4 `hors_modele` ; le registre seul a
  changé (`data/reference/legislation/cnav/references.csv`, 15 lignes, les colonnes
  `sort` et `renvoi` seules, chaque renvoi trouvé dans le dépôt par script). Aucune
  raison neuve.

**Par ce qu'elles disent.**

- *Les montants de l'année* : le plafond de la sécurité sociale de 2015 et ce qui s'en
  déduit pour la réversion (n° 2016/2), rangé sous la série du plafond et la fiche de
  la réversion ; la revalorisation du 1er octobre 2015 (n° 2016/13), « revalorisées du
  coefficient de 1,001 », et les minima qu'elle entraîne ; les plafonds des veuves de
  guerre (n° 2016/26), comme ceux de 2017 et 2018 ; les seuils de la CSG des pensions
  pour 2017 (n° 2016/36, que remplace la n° 2016/38), rangés comme les circulaires de
  2006 à 2008 sur ces seuils.
- *La revalorisation sur l'inflation constatée* (n° 2016/29), à l'article L. 161-25,
  dont « le coefficient ne peut jamais être inférieur à 1. », que
  `revalorisation_des_pensions.yaml` porte.
- *La régularisation des cotisations prescrites des artistes-auteurs*
  (instruction n° 2016/308), « ouverte du 1er janvier 2017 au 31 décembre 2021 »,
  rangée comme la lettre ministérielle du 27 décembre 2021 qui la prolonge.
- *Trois circulaires du RSI* : les assiettes minimales de 2016 (n° 2016/009), « le
  relèvement de l'assiette minimale de la cotisation vieillesse de base à 11,5% du
  plafond », que `assiette_minimale_independants.csv` porte depuis 2016, et leur
  dispense pour les allocataires du revenu de solidarité active ; la validation des
  micro-entrepreneurs (n° 2016/010), « Cette validation à hauteur de 150 heures SMIC
  intervient pour les périodes à compter du 01/01/2014. », et le revenu annuel moyen
  borné au plafond, que `revenu_annuel_moyen_independants.yaml` et `micro_social.yaml`
  portent ; la majoration du compte de prévention de la pénibilité au RSI
  (n° 2016/012), dont la décote bornée (« ne peut excéder 25 % »), rangée comme la
  fiche 6.6 de la circulaire carrière de 2017.
- *Hors modèle* : les taux de change des quatre trimestres de 2016 (n° 2016/1, 2016/25,
  2016/32, 2016/42), sous la raison déjà employée.
- *La circulaire ministérielle n° 86/7004 du 14 mars 1986*, que le registre date du
  26 août 2016 : l'application de la loi n° 86-19 du 6 janvier 1986 aux exploitants
  agricoles, rangée sous leur fiche et le barème de leur retraite proportionnelle. Elle
  porte l'écart neuf qui suit.

**Les montants relus.** Conformes : le plafond de 2015, 38 040 euros
(`macro/plafond_securite_sociale.csv`) ; le coefficient de 1,001 au 1er octobre 2015
(`legislation/revalorisation_pensions.csv`, ligne 117) ; les seuils de la CSG pour 2017,
que les circulaires n° 2016/36 et 2016/38 donnent inchangés (10 676 et 13 956 euros) et
que la série porte à 10 996 et 14 375 euros, d'après le texte qui les a relevés
ensuite (L. 136-8, LEGIARTI000033712894) : la série suit le dernier texte, ce n'est pas
un écart.

**L'écart neuf : l'âge des exploitants agricoles de 1986 à 1989.**

- *Ce que dit la circulaire* : « L'âge de l'ouverture du droit à la retraite est ramené
  progressivement de soixante−cinq ans à soixante ans entre le 1er janvier 1986 et le
  1er janvier 1990. » Le calendrier suit : soixante-quatre ans en 1986, soixante-trois
  en 1987, soixante-deux en 1988, soixante et un en 1989, soixante en 1990. Les
  inaptes, les anciens combattants et prisonniers de guerre, les déportés et internés
  gardent soixante ans pendant la transition.
- *Ce que dit le modèle* : la fiche `data/reference/regimes/msa_non_salaries.yaml`, sur
  la période de 1986 à 1989, ouvre la pension à soixante ans (`age_ouverture: 60`), sous
  la note « SOIXANTE ANS DEPUIS LE 1ER JANVIER 1986 », qui cite l'article 11 de la loi
  (LEGIARTI000006757038) ; la réforme `age_60_agricole_1986` de `reformes.yaml` la date
  du 1er janvier 1986.
- *Un second point, de même source* : la retraite forfaitaire se proratise, pendant la
  transition, sur une durée qui croît d'un an par an. La circulaire dit « trente−trois
  ans et demi, si la retraite prend effet en 1986 », puis trente-quatre et demi,
  trente-cinq et demi, trente-six et demi, et trente-sept et demi dès 1990 (IV de
  l'article 2 de la loi). La fiche donne à toute la période une durée requise de
  150 trimestres.
- *Ce qui reste à faire* : relire la loi n° 86-19 au Journal officiel, ses articles 1er
  et 2, que l'index de la DILA ne garde pas sous LEGI, avant de corriger la fiche, par
  une étape qui écrit une règle du scénario 1, sous ses consignes. Seuls les départs
  d'exploitants agricoles de 1986 à 1989 sont touchés.

**Ce que la base sert de travers.**

- Des textes annulés servis comme vivants : la n° 2016/36 (par la n° 2016/38), elle-même
  remplacée ensuite ; la n° 2016/2 annule une circulaire de 2015 sur le même plafond.
- La circulaire ministérielle n° 86/7004 du 14 mars 1986 est datée par le registre du
  26 août 2016, d'où sa place dans cette période, et n'est servie qu'en HTML.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les lois et décrets que ces
circulaires appliquent n'ont pas été relus au Journal officiel ; les moteurs n'ont tourné
sur aucun cas.
