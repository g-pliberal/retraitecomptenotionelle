# L'âge du taux plein de la Banque de France, lu dans son règlement

Le 21 novembre 2026, le soir, sur Opus 5.5, relu sur Fable avant l'envoi
(bonne à publier), au titre de la règle du propriétaire du 20 novembre : ce
qui s'écarte du droit se corrige, puis se dit. L'écart avait été laissé par la
note des dix bascules (`2026-11-21-etape-4-les-dix-bascules.md`, « laissé :
à corriger »).

**Le texte.** Règlement annexé au décret n° 2007-262, dans ses rédactions de
2007 (`LEGIARTI000006778516`), du 9 mai 2012 (`LEGIARTI000025882187`) et du
1er janvier 2025 (`LEGIARTI000047909725`), lues dans l'index LEGI. Aucune ne
nomme L. 351-8 du code de la sécurité sociale. Le seul âge où la pension
cesse d'être minorée est « l'âge auquel s'annule le coefficient de
minoration » : la limite d'âge du grade (article 32, 1°), que l'article 70
abaisse à titre transitoire. Le tableau de 2007 l'écrit par période où
l'agent « est susceptible de liquider sa pension », celui de 2012 par période
de naissance, en trimestres retranchés de la limite d'âge. Il écrit « Sans
objet » jusqu'au 31 décembre 2008, et aux nés jusqu'au second semestre 1948.

**L'écart.** De 2008 à 2022 et depuis 2025, la fiche du régime renvoyait l'âge
du taux plein à `age_annulation_decote`, l'âge du régime général. La décote
lisait déjà l'article 70 depuis le 19 novembre ; mais `ouvrir.ageTauxPlein`
rendait l'âge du régime général, et trois lecteurs le prenaient.

| Lecteur | Ce qu'il fait | Avant | Après |
|---|---|---|---|
| `ageTauxPleinDroit` | l'âge du départ « au taux plein » que le site propose (`pilote.js`) | L. 351-8 | article 70 |
| `ageAnnulationDroit` | le « taux plein automatique » de l'estimation | L. 351-8 | article 70 |
| `decoteBanqueDeFrance` | l'âge rendu « Sans objet » | L. 351-8 | l'âge d'ouverture, sans effet sur le taux |
| `finIndemnisation` | la fin du chômage indemnisé | L. 351-8 | L. 351-8, inchangé |

Les autres lectures de `ageTauxPlein` dans `liquider.js` et `acquerir.js`
relevées une à une : le minimum contributif et les cultes, les points
gratuits agricoles, l'IRCEC, l'anticipation de l'Agirc-Arrco, la surcote des
régimes en points, l'Ircantec, le taux plein anticipé des mères de la
CARCDSF. Aucune ne s'applique à une période de la Banque de France. Le
minimum garanti lit les trimestres de décote, donc déjà l'article 70.

**La correction.** `ouvrir.minorationBanqueDeFrance` lit la fiche
`decote_banque_de_france` (le corps de l'ancienne `decoteBanqueDeFrance`,
déplacé) ; `ageAnnulationBanqueDeFrance` en tire l'âge, ou l'âge d'ouverture
quand le tableau écrit « Sans objet », comme aux régimes sans décote dont la
fiche porte l'âge du taux plein égal à l'âge d'ouverture (État et CNRACL
avant 2004, SNCF, RATP et IEG avant 2008). `ageTauxPlein` le rend pour toute
période dont la décote est celle du règlement. La décote en reprend l'âge ;
quand le statut ne donne pas de limite, elle retranche ses trimestres de
`age_taux_plein`, et non plus de l'âge du régime général. Le renvoi est
parti des quatorze périodes : valeurs de repli 1 429 → 1 415, renvois sans
texte 296 → 294.

**Le chômage garde L. 351-8.** L'article L. 5421-4 du code du travail coupe
l'indemnisation à l'âge du 1° de L. 351-8, quel que soit le régime (de 2011
à 2023, il écrit l'âge de L. 161-17-2 augmenté de cinq ans, le même âge) :
`finIndemnisation` lit pour la Banque de France l'âge du régime général
(`ageDuChomage`), comme avant.

**Ce qui bouge.** Aucun des 937 témoins ni des 86 rendus de page : les dix
témoins de la Banque de France partent à une date fixée. Bougent l'âge du
départ au taux plein et celui du taux plein automatique qu'un agent saisi
au site se voit proposer, entré dans le régime à 28 ans (25 pour le né en
1955) :

| Né en | Avant | Après | Pension à cet âge, avant → après |
|---|---|---|---|
| juillet 1951 | 65 ans et 4 mois | 62 ans et 3 mois | 29 092 → 25 667 € par an |
| janvier 1955 | 66 ans et 6 mois (durée), automatique à 67 | 63 ans | 32 880 → 29 454 € par an |
| janvier 1958 | 67 ans | 65 ans | 34 939 → 31 744 € par an |

À l'âge proposé, la pension n'est minorée ni avant ni après ; elle est plus
basse parce que l'agent part plus tôt, avec moins de trimestres.

**Tests.** `tests/test_age_du_taux_plein_banque_de_france.py`, vu rouge pour
la raison attendue (65 ans et 4 mois rendus pour 62 ans et 3 mois) : l'âge
de six lignes des tableaux, les deux lecteurs du site, et la fin du chômage
inchangée. Suite rapide : 6 450 réussis ; filet des fichiers communs vert.

**Laissé, trouvé en route.** Deux écarts de la même famille, à mener chacun
dans une étape à lui, et une question de lecture.

- Le minimum garanti de la Banque de France : l'article 72, III, de la
  rédaction de 2012 minore l'âge de l'article 34 de neuf trimestres en 2016 à
  un en 2020, selon l'année où l'âge d'ouverture est atteint ; le moteur ne
  porte cette minoration qu'à la fonction publique, de 2011 à 2015, et la date
  depuis laquelle l'article 34 réserve le minimum au taux plein reste à lire.
- La fonction publique : `ageTauxPlein` y rend la limite d'âge (65 ans au
  fonctionnaire de l'État né en 1950), quand la décote s'annule à 62 ans et
  6 mois (table de L. 14) ; le départ au taux plein et le taux plein
  automatique que le site propose lisent la première.
- Les agents nés au second semestre 1962 : le tableau de l'article 70 vaut
  « pour les agents nés avant le 1er janvier 1963 », mais s'arrête au premier
  semestre 1962. La fiche leur prête cette dernière ligne (67 ans moins un
  trimestre) ; l'article 32 seul donnerait la limite d'âge, 67 ans. Le choix
  vaut déjà pour la décote depuis le 19 novembre ; il est à vérifier à part
  (remarque de la relecture sur Fable du 21 novembre).
