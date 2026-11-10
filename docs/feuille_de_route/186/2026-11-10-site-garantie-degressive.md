# Le site dit la garantie dégressive, et le parcours suit l'accueil

Dans la nuit du 9 au 10 novembre 2026, à la demande du propriétaire (« fait
le reste »), après la garantie dégressive au modèle
(`2026-11-09-garantie-degressive-au-modele.md`) et le recours d'office
(`2026-11-09-garantie-d-office.md`). Une session de l'action 189 écrivait le
gabarit des pages au même moment : les retouches se bornent au texte et aux
calculs de la garantie, et se sont rebasées sans conflit de source.

## Ce qui est écrit

**Le barème du portage, pour les pages.** `manqueMoyen`, `coutGarantie` et
`coutGarantieParSexe` (`moteur/js/garantie.js`) portent la forme, ligne pour
ligne comme `_manque_moyen` du Python ; sans forme, ils restent différentiels,
ce que la colonne de l'ASPA et « qui vit sous le plancher » lisent encore.
Les mêmes tranches posées à la main que le test du modèle
(`tests/js/garantie-degressive.test.js`).

**Trois endroits recalculaient la garantie par leur propre soustraction**, et
passent par `complementGarantie` : le tableau de l'accueil
(`tableauGarantie`), le tableau d'un foyer au simulateur, et les tableaux de
la page Coût sur la distribution. « 900 € et 900 € » y donne 300 €, 150
chacun.

**Le texte**, par une seule fonction, `formeGarantie`, qui lit les deux
paramètres et situe des ressources face au plancher et à la sortie :
- le simulateur : la règle de la ligne « g) Garantie vieillesse » (`c − f`
  sous le pivot, `c − p − 50 % × (f − p)` au-delà), les trois lectures (« reste
  sous le plancher », « dépasse le plancher, sans atteindre les … où la
  garantie s'éteint », « dépasse les … »), la garantie d'aujourd'hui, la
  bulle « Ce qui la sépare de l'ASPA », qui dit deux mots au lieu d'un ;
- la page Coût : « La garantie du système 4 est dégressive », le bas de la
  distribution au lieu de sa queue basse, « Ayants droit » au lieu de « Sous
  le plancher » en tête de deux tableaux ;
- le programme : la prestation est dite individualisée « et dégressive :
  au-delà de 50 % du plancher, chaque euro de pension ne lui retire que
  50 % » ;
- la page Méthode : le pilier volontaire (repris en entier sous la moitié du
  plancher, de moitié au-delà) et le résumé du système 4.

Les budgets de mots des pages ont tenu la plume : cinq étaient dépassés à la
première écriture (l'accueil de 66 mots, le simulateur de 31, Méthode de 30,
Cas types de 2, Coût d'un seul), et le texte a été resserré plutôt que les
budgets relevés. L'accueil n'a donc qu'une phrase sur la dégressivité.

**Le catalogue des affirmations** : `cout.queue_basse` revient à `verifiee`
sous son nouvel extrait ; une entrée de plus,
`accueil.cotiser_rapporte_au_dela_du_pivot`, sur la phrase de l'accueil, et
son contrôle.

## Une phrase écartée, et corrigée ailleurs

La session avait d'abord écrit, en gras à l'accueil, « Le travail paie
toujours ». C'est faux sous la forme suédoise : sous la moitié du plancher,
une pension cotisée n'ajoute rien, la garantie la retirant en entier — ce que
l'étude disait (« ne paie pas les très petites carrières »). L'accueil dit
seulement ce que la règle fait au-delà de la moitié du plancher. La même
erreur était partie sur `main` la veille dans deux phrases de prose (« qui a
cotisé touche toujours plus que qui n'a rien cotisé », à la méthodologie et à
la limite de la garantie) : corrigées ici.

## Le parcours de présentation

`test_chaque_chiffre_du_parcours_est_sur_sa_page`, rouge depuis que l'accueil
a été récrit (action 189, étape 2) : le parcours annonçait « quatre grands
chiffres », dont « 1 600 € pour un couple » et « 100 % de ce qui est cotisé
revient », que la page ne montre plus. La puce décrit les six repères
d'aujourd'hui ; le reste de la section a été vérifié sur la page rendue et
tient.

## Ce qui reste

- Au propriétaire : la garantie d'office peut-elle se refuser (note du
  recours) ; et comment dire à l'accueil ce que la garantie fait pour qui a
  cotisé, la forme retenue ne payant pas les pensions sous la moitié du
  plancher.
- Le plan de la réversion, étapes 2 et 4 à 7 ; ce qui paie le surcoût,
  l'export dans l'Union et la CSG du complément, restés ouverts.
