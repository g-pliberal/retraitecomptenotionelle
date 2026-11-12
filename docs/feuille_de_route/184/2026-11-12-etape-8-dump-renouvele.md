# Étape 8 : la mise à jour d'un index refuse quand la DILA a renouvelé son dump

**Reprise, au 12 novembre 2026.** Rien n'est commencé. La DILA publie pour
chaque base de droit un fichier complet, renouvelé de loin en loin, et des
mises à jour quotidiennes ; quand elle renouvelle le fichier complet, elle
retire les mises à jour d'avant. Un index en retard ce jour-là ne peut plus
rattraper ce qui lui manque : la mise à jour du lundi appliquerait ce qui
reste et publierait un index troué, sans le dire. Le propriétaire a tranché :
pour le Journal officiel et les lois, la mise à jour refuse, et la
reconstruction reste un geste voulu. Pour les conventions collectives, elle
reconstruit déjà seule, en quelques minutes. Le test d'abord. Le workflow, qui
est une garde, ne se touche pas.

**La demande, le 12 novembre 2026.** La session de l'étape 5 a constaté que la
DILA avait renouvelé le 8 novembre 2026 les dumps globaux des trois bases et
retiré les incréments antérieurs (note
`2026-11-11-etape-5-kali-dans-l-index.md`). La question posée au propriétaire
: « Quand la DILA renouvelle un dump avant que l'index JORF ou LEGI l'ait
rattrapé, la mise à jour doit-elle refuser (le workflow passe au rouge, on le
relance en cochant "reconstruire", une heure à une heure et demie sur GitHub)
ou reconstruire d'elle-même ? » Les deux sessions recommandaient de refuser.
Sa réponse : « Pour les décisions à trancher : je choisis tes recommandations
».

**Ce qui est su.** `scripts/fetch/dila_index.py`, `mettre_a_jour` : la
détection existe déjà, et pour KALI elle reconstruit l'index du dump neuf. Les
index publiés du JORF et de LEGI ont enjambé le renouvellement du 8 novembre
sans trou.

**Ce qu'il y a à faire.**

1. Le test, vu rouge : un index du JORF ou de LEGI arrêté avant un dump
   renouvelé, dont les incréments manquants ne sont plus servis ; la mise à
   jour refuse, ne publie rien, et dit comment reconstruire.

2. Le code, sans toucher à `.github/workflows/index-dila.yml` : le refus fait
   échouer la course, ce qui suffit à l'alerte.

3. `docs/veille_droit.md` : ce que la session fait quand la course du lundi
   est rouge pour cette raison.

**Fini quand** un index troué ne peut plus être publié sans bruit. Si le
changement exigeait malgré tout de toucher au workflow, s'arrêter et le
demander.
