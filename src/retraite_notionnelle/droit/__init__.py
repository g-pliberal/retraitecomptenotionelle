"""Le droit applicable, en étapes (docs/architecture.md, § 7.2).

Le scénario 1 quitte ``scenarios/actuel.py`` pour ce paquet, une étape par
module, et ``moteur/js/droit/`` le suit fonction pour fonction. Pour une
demande, quatre étapes construisent le RELEVÉ DES DROITS qu'elle fait
valoir :

* :mod:`.preparer` — préparer la chronologie : la compléter par les
  présomptions ;
* :mod:`.coordonner` — coordonner les affiliations : rétablir l'agent parti
  de la fonction publique sans droit à pension, router chaque ligne vers les
  régimes qui la reçoivent, puis réunir en groupes les régimes que le droit
  fait liquider ensemble ;
* :mod:`.compter` — compter les durées : assurance, services, cotisés, et les
  trimestres des enfants, dans le régime que la priorité entre régimes
  désigne ;
* :mod:`.acquerir` — acquérir les droits : points, cotisations, durée qu'un
  régime plafonne, points attribués sans cotisation.

Chaque étape écrit une donnée que décrit son schéma, dans
``data/reference/etapes/`` ; :mod:`.releve` les enchaîne, et en tire les
lignes du relevé (contrat C.5). La liquidation, qui reste dans
``scenarios/actuel.py`` jusqu'à la phase 5, lit le relevé qu'il lui rend.

Jusque-là, les étapes lisent la chronologie par sa vue, la carrière, et les
tables du scénario 1 par le moteur qui les tient — ``moteur``, un
:class:`~retraite_notionnelle.scenarios.actuel.ScenarioActuel`. Les fiches et
leurs versions les remplaceront (phase 6).
"""
