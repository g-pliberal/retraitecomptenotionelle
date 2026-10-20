# Le simulateur à l'usage : réinitialiser, retirer une période, le relevé d'abord, un exemple jeune

**La demande**, le 20 octobre 2026 : quatre retouches du formulaire du
simulateur, que le propriétaire a relevées en s'en servant. Une étape par
demande, un commit par étape, chacune avec son test, vu rouge avant le code.

**Étape 1, « Réinitialiser ».** Le bouton existait, sous le nom « Effacer ma
saisie », à côté de « Calculer » ; mais il ne paraissait que lorsque le
navigateur avait retenu une saisie. Devant une adresse partagée qu'on ne fait
que regarder, ou dans un navigateur qui refuse le stockage — une navigation
privée, le cadre d'une autre origine —, il restait caché : le formulaire ne
laissait que changer les données. Renommé « Réinitialiser », il se voit dès
qu'il y a quelque chose à réinitialiser : le rendu le montre devant toute
carrière saisie (`saisie.demandee`), le script de la page dès la première
frappe, ou dès qu'une saisie est retenue. Devant l'exemple intact, il reste
caché. Il fait ce qu'il faisait : la mémoire vidée, l'exemple rendu, sous les
règles en vigueur. Vérifié dans Chromium, stockage permis et refusé.

**Étape 2, « Retirer cette période ».** Chaque période après la première porte
le bouton. Le script de la page renvoie le formulaire sans elle, par
`requeteSansPeriode` (`pages.js`), qui ôte ses champs `metierN_…` et remonte
d'un rang ceux des périodes suivantes ; rien ne se vérifie avant, puisque
c'est souvent la ligne fautive qu'on retire. La page reste en place, au pixel
près, et le focus va à ce qui prend sa place : la période suivante, ou la
demande d'en ajouter une. La première période porte la carrière (`debut`,
`statut`, `salaire`) et ne se retire pas.

**Étape 3, le relevé d'abord.** Le dépôt du relevé était replié sous les
métiers, la carrière paramétrique tenant lieu de porte d'entrée. Il ouvre
désormais le formulaire, avant la situation et la naissance, hors de tout
dépliant : le libellé « Déposez votre relevé de carrière », au poids d'un
appel, le champ du fichier, et « À télécharger sur info-retraite.fr ». Le
reste — ce que le simulateur en fait, lassuranceretraite.fr, la lecture dans
le navigateur — passe sous un point d'interrogation, et la saisie à la main,
repliée dessous, s'ouvre quand un relevé est saisi. Le formulaire vierge
passe de 186 à 191 mots visibles, et la barre de
`test_le_simulateur_tient_en_peu_de_mots` monte de cinq pour ce contrôle. Le
catalogue des affirmations suit le libellé ; le parcours de présentation dit
le relevé d'abord, et les deux boutons des étapes 1 et 2.

**Étape 4, l'exemple jeune.** L'exemple que le simulateur ouvre déjà rempli
naît le 1er janvier 2000, et non plus en 1975, dans les deux saisies
(`saisie.py`, qui fait foi, puis `saisie.js`) : premier emploi à 21 ans, en
janvier 2021, départ à 64 ans, en janvier 2064. Rien d'autre ne change —
salarié du privé non cadre, homme, 3 500 € par mois au milieu de sa
carrière —, pour que seul l'âge sépare les deux exemples. En net, comme le
parcours de présentation le décrit : 3 119 € au système actuel, financés à
85 %, 2 442 € à la proposition (−21,7 %), et 223 € de plus par mois sur la
fiche de paie pendant les 38 années qui le séparent du départ ; né en 1975,
il recevait 2 767 € et 2 188 € (−20,9 %). Un test et deux carrières du banc
des affirmations lisaient l'ancien exemple sans le dire, et le disent
désormais : la reconstruction de l'adresse des métiers (« quarante ans, pour
qui est né en janvier 1975 »), et les carrières `smic` et `smic_en_couple`,
dont la garantie complète la pension à la génération 1975 et non à celle de
2000, au même revenu. Aucun témoin de simulation ne bouge.

**Ce que le propriétaire peut trancher.** L'année de l'exemple, 2000, et ce
qui n'a pas changé avec elle : le revenu, 3 500 € bruts par mois au milieu de
la carrière, soit à peu près le salaire moyen, le statut et le sexe. Un
revenu plus proche de celui d'un jeune actif, ou une femme, se règlent de
même, aux défauts des deux saisies.
