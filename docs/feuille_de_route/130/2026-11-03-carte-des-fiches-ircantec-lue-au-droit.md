# La carte des fiches : l'Ircantec lue au droit, sixième lot

**La demande.** Le 3 novembre 2026, la session d'orchestration confie à la
file E une retouche, puis un nouveau lot de la carte (action 130), hors des
zones des autres files et de ce qui est déjà lu. La retouche : le point
ouvert de la phase 7 disait encore que le moteur ne sert ni le pilier
capitalisé ni la garantie vieillesse sur un compte ouvert à la bascule ; il
les sert depuis le 2 novembre (action 161, sous-étape 3), ce que la file C
signalait. Le lot pris : l'Ircantec, dont les deux fiches n'étaient pas
mûres, `coefficient_anticipation_ircantec`, qui vaut aussi pour les points
de l'IPACTE et de l'IGRANTE, et `surcote_ircantec`. Aucun chiffre du modèle ne
bouge. En même temps, la file G corrige la surcote de la SNCF et de la RATP,
sous le même numéro, dans sa propre note.

## Ce qui est fait

- **La retouche** : le paragraphe de la phase 7 dit, daté, que les deux
  moteurs servent le pilier et la garantie sur un compte ouvert à la bascule,
  et que la variante prospective est un univers en données, que le site ne
  montre pas (080bc2a).
- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF
  récupérés, à jour de l'incrément du 2 novembre, et du 3 pour le JORF ;
  `textes.py --inscrire`, trente-deux rédactions nouvelles « à examiner »,
  toutes de la loi n° 48-1469, que la fiche des marins cite depuis la veille.
- **Le test d'abord.** Les deux fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de leurs onze manques ; un fichier neuf,
  `tests/test_ircantec.py`, vu rouge faute de versions. Chaque paramètre
  d'une version porte le nom du champ de la période qui le porterait, ou
  d'une constante du portage, qui fait foi, lue dans
  `moteur/js/droit/liquider.js` : les deux séries de périodes de
  `regimes/ircantec.yaml`, et la période unique de l'IPACTE et de l'IGRANTE,
  que le moteur lit encore après leur fermeture, en portent la valeur, ou la
  fiche déclare l'écart, et vingt-neuf cas le tiennent, chacun par l'article
  qu'en cite l'approximation. Trois tests de plus : la table de 1970 est
  l'escalier du portage à chaque anniversaire, et en diffère de 5,25 points
  au plus entre deux ; les âges fixes de 2023, 62 et 64 ans, tombent sur
  l'escalier ancré à l'âge du taux plein pour toute génération qui l'atteint
  après le 14 septembre 2023 ; la seconde table de 1983 lit trente-sept ans
  et demi, que la durée des générations dépasse de 1994 à 2003. Une valeur
  altérée dans chaque fiche le fait rougir.
- **Les treize rédactions de l'article 16** de l'arrêté du 30 décembre 1970,
  de 1971 au 14 septembre 2023, chacune contre la suivante, et les arrêtés
  qui les ont faites, au Journal officiel : du 26 décembre 1975, du
  20 septembre 1978, du 26 juillet 1983 — son analyse : les coefficients
  « fixés désormais par trimestre », les exonérations à compter du 1er juillet
  1982 et du 1er avril 1983 —, du 29 mars 2018, du 18 décembre 2018 et du
  11 septembre 2023 ; l'article 2 du décret n° 70-1277, et L. 351-8,
  L. 161-17-4 et L. 351-6-1 du code de la sécurité sociale.
- **`coefficient_anticipation_ircantec`**, du domaine de la décote et de
  l'étape qui liquide, approchée, de conforme : treize versions. Les pensions
  de l'IPACTE et de l'IGRANTE d'avant 1971, supposées ; de 1971 au 31 août
  1983, une table par année d'âge, de 0,43 à cinquante-cinq ans à 0,96 à
  soixante-quatre, et des exonérations qui s'ajoutent une à une — les anciens
  combattants le 3 janvier 1976, les travailleurs manuels et les mères de
  famille le 26 juillet 1977, les femmes de la loi du 12 juillet 1977 le
  30 septembre 1978, rétroactivement l'ordonnance du 26 mars 1982 au
  1er juillet 1982 ; le 1er avril 1983, rétroactivement aussi, l'exonération
  au taux plein du régime général et la seconde table, sur trente-sept ans et
  demi ; le 31 août 1983, l'escalier au trimestre que le portage lit ; le
  1er janvier 2004, la carrière longue, le handicap, et la seconde table sur
  la durée de la génération ; le 1er juillet 2011, les âges de la loi de
  2010 ; le 31 mars et le 21 décembre 2018, deux exonérations ; le
  14 septembre 2023, les ancres fixes à 62 et 64 ans. Les deux exemples
  publiés par la caisse vont à la dernière version.
- **`surcote_ircantec`**, du même domaine et de la même étape, approchée, de
  transcrite : quatre versions — aucune majoration avant 2010, ce que toutes
  les rédactions depuis 1971 montrent ; les deux majorations du 25 septembre
  2008, « A compter du 1er janvier 2010 », à soixante et soixante-cinq ans ;
  les âges de la génération, le 1er juillet 2011 ; le trimestre à cheval, le
  non-cumul et le trimestre de quatre-vingt-dix jours, le 14 septembre 2023.
- **Le cliquet des textes** descend de 9 418 à 9 411. **La carte** passe de 93
  fiches à lire au droit à 91, de 550 manques à 539. `conservation.py --depuis
  HEAD` dit changées les lignes de veille des deux fiches, refaites depuis
  elles, ce que la référence figée admet.

## Ce que l'étape laisse

- **Deux erreurs du modèle, pour une étape du modèle** (la file E ne touche
  pas au modèle), toutes deux d'avant 1983 :
  - la table par année d'âge : de 1971 au 31 août 1983, l'article ne donne
    qu'un coefficient par âge révolu, quand le modèle lit dès 1951 l'escalier
    au trimestre de l'arrêté du 26 juillet 1983 — 0,8175 à soixante ans et
    neuf mois pour 0,78, jusqu'à 3,75 points de trop entre deux anniversaires
    à partir de soixante ans ; la correction serait un barème daté, dans les
    deux moteurs ;
  - l'exonération servie trop tôt : la période unique de l'IPACTE et celle de
    l'IGRANTE portent `duree_requise_par_generation`, que le moteur lit pour
    toute liquidation de leurs points ; il les exonère dès 1951 à qui a cent
    cinquante trimestres, et y lit la seconde table, quand l'article ne le
    fait qu'à compter du 1er avril 1983 — jusqu'à 22 points de coefficient de
    trop. Les notes de leurs fiches de régime y voient le droit commun
    d'après 1983, sans dire qu'il vaut aussi pour les pensions d'avant ;
    l'IPACTE existait depuis 1951. La correction : lire cette durée à la date
    d'effet, par exemple comme la fiche de l'Agirc-Arrco le fait
    (`exonerations_agirc_arrco`).
- **Des écarts plus petits, déclarés** : l'anticipation avant l'âge légal,
  que le modèle ne sert pas — l'exemple de la caisse le mesure déjà, en écart
  connu (fiche `liquidation_regime_par_regime`) ; soixante-cinq ans gardé aux
  points de l'IPACTE et de l'IGRANTE après 2011 ; les catégories du régime
  général exonérées avant que l'article les nomme, en 1974-1975 et en
  1976-1977 ; les exonérations que le modèle ne connaît pas — le licencié de
  soixante-trois ans, la femme de la loi de 1977, les mesures de 1982, et
  depuis 2011 l'aidant, le parent d'un enfant handicapé, le parent de trois
  enfants né de 1951 à 1955 ; le taux plein « d'un régime de retraite
  obligatoire de base » de 2023 ; le trimestre de quatre-vingt-dix jours de la
  surcote.
- **Une lecture ambiguë** : de 1994 à 2003, la seconde table lit à la lettre
  trente-sept ans et demi, quand la durée du taux plein monte d'un trimestre
  par génération ; lu à la lettre, le II ne s'ouvre plus au-delà de cent
  cinquante trimestres. Le modèle lit la durée de la génération ; la pratique
  de la caisse est à chercher (une circulaire de 1994).
- **À relire**, dans les fiches : les exonérations d'après 2011 que le modèle
  sert peut-être par l'inaptitude (incapacité permanente, amiante, handicapé
  du 1° ter, compte de prévention) ; les arrêtés de l'IPACTE et de l'IGRANTE,
  absents de LEGI ; la surcote d'avant 2023, où le texte se taisait.
- Les 91 fiches à lire au droit. Ce que ce lot ajoute : une rédaction peut
  dater une règle d'avant sa publication (« A compter du 1er avril 1983 ») ;
  une version supposée qui cite un texte n'est connue qu'à sa publication, et
  le partage de la carte le refuse si la suivante commence avant.
- `regenerer.py --verifier` dirait périmé le tableau de bord, qui compte la
  carte ; GitHub le refait.

## Ce qui attend le propriétaire

Une question : ouvrir une étape du modèle pour les deux erreurs d'avant 1983
de l'Ircantec — la table par année d'âge, et l'exonération servie trop tôt aux
points de l'IPACTE et de l'IGRANTE ? Avis : oui, sans urgence ; elles ne
touchent que des pensions prises avant 1983. Pour le reste, rien de neuf : la
septième étape du sixième domaine, la décision de la proposition, et celle sur
la retraite progressive, le cumul et la seconde pension, README muet.
