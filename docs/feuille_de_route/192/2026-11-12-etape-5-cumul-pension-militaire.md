# Étape 5 : le cumul d'une pension militaire et d'un emploi, pour les pensions prises à compter de 2027

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot de la fonction publique l'a lu
(`184/2026-11-12-etape-6-fonction-publique.md`, « Ce qui change une règle »,
point 1) : article L. 86 du code des pensions (LEGIARTI000053279638, loi n°
2025-1403, article 102) ; articles L. 161-22, III, C, 1°, et L. 161-22-1-2, 4°
et 5°, du code de la sécurité sociale. Le plafond devant un employeur public :
le tiers de la pension et la moitié du minimum garanti, sauf non-officier de
moins de vingt-cinq ans de services, limite d'âge atteinte, invalidité. Le
portage : `regle2027`, dans `moteur/js/droit/cumul.js`. La fiche
`cumul_emploi_retraite_fonction_publique` tient la rédaction à rattacher.

**Ce qu'il y a à faire.**

1. Lire les trois articles, et le sort de la pension d'invalidité, civile ou
   militaire, que le 5° laisse cumuler entièrement.

2. Rejouer le cas : un militaire parti avant l'âge légal en 2027, salarié du
   privé. Le test, vu rouge, valeur tirée du texte.

3. La règle, dans le modèle et son portage ; ce que la saisie sait du
   caractère militaire de la pension et de l'employeur, à dire s'il manque.

4. La fiche.

**Fini quand** la pension militaire suit, en 2027, le cumul que le texte lui
donne, ou que ce qui manque à la saisie pour le dire est une limite écrite.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.

**Ce qui a été fait, le 12 novembre 2026.** L'étape est close : pour une
première pension de base prise à compter du 1er janvier 2027, la pension
militaire suit le cumul que le texte lui donne, dans les deux moteurs, et rien
ne bouge pour une pension prise avant.

- *Lu*, dans les index LEGI et JORF à jour au 11 novembre 2026. L. 86 du code
  des pensions, rédaction du 31 décembre 2025 (LEGIARTI000053279638) : « Par
  dérogation au C du III de l'article L. 161-22 », le titulaire d'une pension
  militaire payé par un employeur de L. 86-1 cumule « dans la limite d'un
  plafond annuel égal à la somme, pour l'année considérée, du tiers du montant
  brut de sa pension et de la moitié du minimum fixé au a de l'article L. 17.
  Lorsqu'un excédent est constaté, la pension est réduite à due concurrence » ;
  cumulent entièrement le non-officier dont la pension rémunère « moins de
  vingt-cinq années de services », celui qui atteint « la limite d'âge du
  grade » ou « la limite de durée de services », et l'invalide. L. 161-22, III,
  C, 1° (LEGIARTI000053279730), et L. 161-22-1-2, 1° à 5°
  (LEGIARTI000053279758) : cumulent entièrement les marins, les artistes du
  ballet de l'Opéra, les anciens mineurs des entreprises fermées, les
  titulaires « d'une pension militaire prévue à l'article L. 6 » et ceux « de
  pensions civiles et militaires ou d'une solde de réforme allouées pour
  invalidité ». L. 84, L. 86-1, L. 6, R. 92 ; l'article 58 du décret
  n° 2003-1306 et l'article 48 du décret n° 2004-1056, qui règlent le cumul de
  la CNRACL et des ouvriers de l'État « conformément aux dispositions
  applicables aux fonctionnaires de l'Etat ». Les deux décrets du 2 novembre
  2026 relatifs au cumul emploi retraite, parus le 3 : le n° 2026-1016
  (R. 91 abrogé, R. 92 renvoyé à L. 86) et le n° 2026-1017 (D. 37 : le service
  des retraites de l'État détecte l'activité et calcule la réduction des
  pensions de L. 86 ; D. 37 bis ; son article 3, D. 161-2-5 à D. 161-2-13 du
  code de la sécurité sociale).
- *La caisse.* La page « Les règles de cumul » des militaires du service des
  retraites de l'État, sans date, lue ce jour, dit le droit d'avant 2027 dans
  les mêmes termes : cumul dans le privé et auprès d'un établissement
  industriel et commercial ; dans le public, cumul pour la « pension de non
  officier rémunérant moins de 25 ans de services (militaires et civils) » et
  pour qui a « atteint la limite d'âge de [son] ancien grade ». Rien sur 2027,
  aucun chiffre. La fiche F12402 de service-public, vérifiée le 1er janvier
  2026, annonce qu'elle « sera mise à jour » au 1er janvier 2027 et ne dit rien
  du militaire. Aucun exemple chiffré publié : la fiche reste `approchee`, ses
  tests sont posés à la main depuis le texte.
- *Le cas rejoué, vu rouge.* La sous-officière née le 15 janvier 1982, engagée
  à vingt ans, partie en février 2027 avec vingt-cinq ans de services, qui
  retravaille d'août 2027 à janvier 2030 à son dernier salaire. Le moteur lui
  retirait toute sa pension, 60 730 € en trente mois, quel que soit
  l'employeur. Sept tests dans `tests/test_emploi_retraite.py`, leur pendant
  dans `tests/js/moteur.test.js`, deux dans `tests/test_web.py` pour la page.
- *La règle*, dans `moteur/js/droit/cumul.js` et son jumeau
  (`entiere2027`, `horsDesAges2027`, `pensionMilitaireServie`). La pension
  militaire et la pension qu'une radiation pour invalidité a fait liquider ne
  passent plus par les trois régimes selon l'âge, et ne comptent plus parmi
  les pensions de base entre lesquelles la réduction des autres se répartit.
  La pension d'invalidité se cumule entièrement. La pension militaire aussi
  dans le privé ; devant un employeur public, entièrement pour le non-officier
  de moins de vingt-cinq ans de services et passé la limite d'âge, sinon dans
  la limite du tiers de la pension et de la moitié du minimum garanti de
  l'année, l'excédent déduit. La page le dit par quatre phrases, dont deux
  neuves (`sortDeLaBase`, dans `pages.js`). Rien n'est lu de la fiche par le
  moteur : la conversion de cette fiche revient à l'action 191, et la constante
  des vingt-cinq ans redit son paramètre.
- *Les chiffres, avant et après*, pour cette sous-officière : salariée du
  privé, 60 730 € non servis, puis rien ; contractuelle d'un employeur public
  à son dernier salaire, 60 730 €, puis 51 355 € ; au même emploi public à
  30 % de ce salaire, 33 226 €, puis rien ; avec vingt-quatre ans de services
  (née en 1983, partie à quarante-quatre ans), 57 420 €, puis rien. Partie en
  février 2026, rien ne bouge : rien dans le privé, 50 315 € devant un
  employeur public.
- *Ce que la règle déplace.* Aucun des 932 témoins de simulation ni des 85
  rendus de page ; un témoin de plus, `cumul_militaire_2027`, que le jumeau
  refait au bit près. `-m rapide`, `-m site`, les confrontations du moteur et
  les quatre fichiers du coût sont verts, sans valeur reposée ni seuil touché.
  Le cliquet des textes passe de 9 231 à 9 229.

**Ce qui manque à la saisie, et que la fiche déclare.** Le grade : la limite
d'âge est celle que le modèle prête à la catégorie, cinquante-neuf ans pour le
non-officier et soixante-six pour l'officier, les plus hautes du code de la
défense ; un sergent, libre à quarante-sept ans, reste plafonné jusqu'à
cinquante-neuf. Le lien au service : la limite de durée de services du
militaire sous contrat n'est pas lue. L'employeur : le public est celui du
contractuel de la fonction publique, sans l'établissement industriel et
commercial. L'année où la limite d'âge est atteinte, l'excédent ne compte que
les revenus des mois qui la précèdent : le texte ne dit rien de cette année.

**Au propriétaire.**

1. *Le grade à la saisie.* Recommandation : ne rien ajouter. Le champ ne
   servirait qu'au militaire payé par un employeur public après vingt-cinq ans
   de services, et la fiche dit l'écart.
2. *Avant 2027, le même défaut dort.* Le modèle plafonne devant un employeur
   public la pension d'invalidité et celle du non-officier de moins de
   vingt-cinq ans de services, que L. 86 laisse se cumuler entièrement dans ses
   rédactions de 2004 à 2023. Les deux se calculent maintenant. Non écrit ici :
   l'étape ne devait rien déplacer avant 2027. Recommandation : une étape
   courte, le test d'abord ; elle déplacera des pensions prises avant 2027.
3. *Le reste de la règle de 2027 est paru, et n'est pas porté.* Le décret
   n° 2026-1017 fixe le seuil à sept mille euros pour 2027 (D. 161-2-8), que
   le modèle dit encore non publié ; il impute la réduction aux pensions de
   base « par ordre de montants de pension décroissant » (D. 161-2-10, II),
   quand le modèle la répartit au prorata ; il l'étale sur douze mois. Et le
   même C laisse cumuler entièrement les marins, les artistes du ballet de
   l'Opéra et les anciens mineurs, que le modèle réduit selon l'âge.
   Recommandation : une étape pour le seuil et l'imputation, qui touche tous
   les régimes, et une pour ces trois populations. Les deux fiches du cumul le
   portent dans `sources.a_relire`.
