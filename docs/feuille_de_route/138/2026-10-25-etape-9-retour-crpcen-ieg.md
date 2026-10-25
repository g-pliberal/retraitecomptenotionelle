# Étape 9, suite de la huitième partie : le retour à la CRPCEN et aux IEG après le 1er septembre 2023

**La demande.** Vingtième vague, le 25 octobre 2026 : une session par tâche,
que le propriétaire ne suit pas pas à pas. Le point « au modèle, le retour à
la CRPCEN et aux IEG après 2023 » du bloc « Reprise » de la huitième partie,
que la note « entrée d'un relevé interrompu »
(`2026-10-25-etape-9-entree-d-un-releve-interrompu.md`, « Trouvé en
chemin ») laissait au modèle : la carrière datait l'entrée du premier
recrutement, et le clerc de notaire de 2010 à 2023, salarié du privé en
2024, revenu en 2025, gardait la CRPCEN.

**Ce que disent les textes**, lus le jour même dans les index LEGI (à jour
au 24 octobre) et JORF de la DILA. Le « sans aucune interruption » de la loi
n° 2023-270 (art. 1er, III et V), que citaient la note et
`affiliations.yaml`, n'est plus le droit : la loi n° 2023-1250 (art. 15, V
et VI) l'ôte de la loi du 12 juillet 1937 (art. 1er, § 2,
LEGIARTI000048701185) et de la loi n° 2004-803 (art. 16, I,
LEGIARTI000048701181) au 1er janvier 2024, pour les congés, suspensions et
ruptures d'avant comme d'après (VIII). Les deux caisses servent la pension
aux recrutés d'avant le 1er septembre 2023 « qui remplissent, à compter de
cette date, les conditions d'affiliation », et l'affiliation se maintient :
dix ans au plus après une suspension ou une rupture antérieure, « quelle
qu'en soit la cause » ; après une rupture postérieure, un mois (démission,
commun accord) ou un an (licenciement), « jusqu'à la reprise d'une activité
entraînant une affiliation auprès d'un autre régime » si elle vient avant ;
pendant les congés qui ne donnent ni cotisation ni droit, treize à la CRPCEN
(décret n° 2025-799, LEGIARTI000052088701), dix-sept aux IEG (décret
n° 2025-761, LEGIARTI000052046341), dont « tout autre congé ou absence dont
la durée est inférieure à un mois ». La CNIEG l'applique ainsi : la maladie
à salaire maintenu maintient l'affiliation, une suspension hors liste la
rompt ; parti le 1er mars 2021, réembauché le 1er février 2026, l'agent
garde le régime. Le texte tranche donc ce que la demande craignait de lui
voir taire : l'interruption de quelques jours (moins d'un mois), le
détachement sans cotisation (rompu au-delà d'un mois, dit la CNIEG), la
mise à disposition, que l'employeur continue de payer et qui n'interrompt
rien. La classe : la RATP garde « les anciens agents […] recrutés avant le
1er septembre 2023 » (décret n° 2008-637, art. 1er, 1°) ; la Banque de
France (L. 142-9) et la SNCF (décret n° 2007-730, art. 2) ne disent que
« recrutés avant » ; aucune ne pose de condition d'affiliation continue.

**Ce qui est fait.**

- *Les tests* (`tests/test_retour_crpcen_ieg.py`, quatre tests, vingt-deux
  cas), vus rouges. Dix carrières posées à la main, lues par le compte, par
  l'étape « coordonner les affiliations » du scénario 1 et par celle du
  portage : le clerc et l'agent des IEG partis fin 2023 et salariés du privé
  en 2024 reviennent en 2025 au régime général et à l'Agirc-Arrco ; l'agent
  parti en 2021 et revenu en 2026 garde les IEG ; le clerc parti fin 2015
  et revenu en 2025 garde la CRPCEN, parti fin 2014 il la perd ; revenu en
  2023, il est recruté avant la fermeture ; le congé parental de 2024 et
  2025 maintient les IEG, le chômage de 2024 rompt la CRPCEN ; la
  suspension commencée en 2011 ne maintient plus rien en 2025 ; l'agent de
  la RATP garde son régime. La naissance se déclare, l'année seule ; ni le
  jour ni le sexe n'y comptent. Une garde de la donnée : seuls ces deux
  statuts portent `maintien`, sur leur borne du grand-père.
- *La règle*, écrite comme une borne de version (architecture, § 4.3) :
  `maintien: 10` sur la période `entres_avant: 2023-09` des deux statuts
  (`affiliations.yaml`). La carrière dit ses retours au statut
  (`Carriere.retours`), la loi les lit (`Affiliations.date_entree`) : un
  retour que rien ne maintient date l'entrée de son année et des suivantes.
  Chaque routage passe par elle — les étapes du scénario 1, le compte, la
  fiche de paie, les contributions d'équilibre, et au portage le cycle de
  vie (`Affiliations.dateEntree`, `Carriere.retours`). Fiche
  `maintien_affiliation_crpcen_ieg`, « approchée ».
- *Les présomptions*, déclarées dans la fiche. Le modèle ne connaît que
  l'année : le départ se date de la fin de sa dernière année d'emploi sous
  le statut, le retour de janvier ; une année civile entière sans emploi
  sous le statut, après une rupture postérieure à la fermeture, dépasse le
  mois comme l'an ; un départ et un retour qui n'en laissent aucune entière
  ne rompent rien. Une interruption déclarée sous le statut le suspend, sauf
  le chômage et la préretraite (`INTERRUPTIONS_DE_RUPTURE`) : l'inactivité,
  les études et le service sont présumés un congé des listes. Une année sous
  un autre statut rompt toujours : la mobilité de cinq ans hors des IEG et le
  congé de création d'entreprise ne se voient pas. Le maintien de dix ans se
  lit à la lettre, quoi qu'il s'y passe.

**Ce que montrent les mesures.** Ni les témoins de simulation ni ceux des
pages ne bougent (`construire_temoins.py --verifier`, le 25 octobre) :
aucune de leurs carrières ne revient au statut.

**Ce qui reste**, une session par point : le plafond de 2027 ; la limite
5 ante ter (2), en fin d'étape, qui peut reprendre les approximations de la
fiche. Au site : la saisie en net remonte au brut par la fiche du premier
recrutement (`Saisie.dateEntree`), et un retour que rien ne maintient y
garde la retenue du régime spécial. À relire : la doctrine de la CRPCEN ;
une rupture postérieure à la fermeture pendant une suspension commencée
avant, que le texte ne règle pas ; le CESE, dont la caisse se ferme aux
membres « entrant en fonction » depuis le 1er septembre 2023 (loi
n° 2023-270, art. 1er, IX) — un membre revenu après la date, ou renouvelé,
y entre-t-il de nouveau ? Le modèle lui garde la caisse de sa première
entrée. Au propriétaire, sans changement : la
CAMIEG, l'écrêtement du minimum de la SNCF, l'ASPA de l'article 23, les
textes au fac-similé de la note « seuil de février 1991 ».
