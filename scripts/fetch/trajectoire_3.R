# Exécute TRAJECTOiRE (DREES), versions 3, sur les cas types du COR et sur les
# carrières que `trajectoire.py` décrit.
#
#     Rscript trajectoire_3.R <dossier des entrées> <dossier des sorties>
#
# C'est `trajectoire.R`, récrit pour l'interface des versions 3 (la 3.3.2 du
# 20 novembre 2026) : `trajectoire.R` reste celui de la version 1.1.2, dont le
# témoin `tests/temoins/trajectoire.json` est sorti. Les tables qu'il écrit
# portent les mêmes noms et les mêmes colonnes, pour que `trajectoire.py` les
# relise sans changement ; s'y ajoutent les points des régimes de base en
# points (`points_base_*`), que les cas types 12 et 13 ont fait naître.
#
# Ce script appartient au dépôt ; TRAJECTOiRE n'y entre pas. Il s'installe à
# part (paquet R `trajectoire`, https://git.drees.fr/drees_code_public/modeles/trajectoire,
# licence EUPL), et ce script n'en appelle que les fonctions exportées.
#
# Deux exécutions, dans le même processus :
#
# 1. LES CAS TYPES DU COR, par la fonction que le paquet exporte pour cela,
#    `lancerCasTypesCor()`, sans rapport ni classeur, sur les générations
#    d'`options.json` et une seule hypothèse de croissance du salaire moyen par
#    tête. Elle calcule chaque âge de départ, par trimestre ; on garde, pour
#    chaque cas type et chaque génération, le premier âge au taux plein qu'elle
#    marque (`ageMinTxPlein`). Les entrées qu'elle donne à `calculePension()`
#    — la carrière de chaque cas type, les paramètres prolongés — sont relevées
#    à l'appel, par `trace()`, sans rien recopier du paquet.
# 2. LES CARRIÈRES DU DÉPÔT, écrites par `trajectoire.py` en tables d'entrée de
#    `calculePension()`, sous les paramètres que l'exécution 1 a prolongés.
#
# Aucune donnée confidentielle : le mode « cas types » se passe de l'EIC et de
# l'EIR, et lit les barèmes livrés avec le paquet.
#
# Le répertoire de travail est un dossier temporaire, marqué `.here` : le
# paquet écrit sa configuration et son cache à la racine du projet qu'il
# trouve, et ce ne doit être ni le dépôt ni le dossier du modèle.

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 2) {
  stop("usage : Rscript trajectoire_3.R <entrees> <sorties>")
}
entrees <- normalizePath(arguments[1], mustWork = TRUE)
sorties <- arguments[2]
dir.create(sorties, showWarnings = FALSE, recursive = TRUE)
sorties <- normalizePath(sorties, mustWork = TRUE)

travail <- file.path(tempdir(), "trajectoire")
dir.create(travail, showWarnings = FALSE)
setwd(travail)
file.create(".here")

suppressPackageStartupMessages({
  library(data.table)
  library(trajectoire)
})
stopifnot(packageVersion("trajectoire") >= "3.0.0")
logger::log_threshold(logger::WARN)
set.seed(20261120L)

reglages <- jsonlite::fromJSON(file.path(entrees, "options.json"))
generations <- as.integer(reglages$generations)
hyp_smpt <- as.numeric(reglages$hypSmpt)

# ---------------------------------------------------------------------------
# 1. Les cas types du COR, par la fonction du paquet
# ---------------------------------------------------------------------------

releve <- new.env()
suppressMessages(trace(
  "calculePension", where = asNamespace("trajectoire"), print = FALSE,
  tracer = bquote({
    releve_ <- .(releve)
    releve_$appels <- c(releve_$appels, list(list(
      dtId = dtId, dtIdAnEtat = dtIdAnEtat, dtIdAnCaisse = dtIdAnCaisse,
      dtIdAnCaisseFonctionnaire = dtIdAnCaisseFonctionnaire,
      parametres = parametres, paramModele = paramModele)))
  })
))
resultats_cor <- lancerCasTypesCor(
  generations = generations, hypSmpt = hyp_smpt,
  genererRapport = FALSE, exporterExcel = FALSE, nbProcessus = 1,
  cheminSorties = file.path(travail, "sorties"), cache = file.path(travail, "cache")
)$resultats
suppressMessages(untrace("calculePension", where = asNamespace("trajectoire")))
# Une hypothèse de salaire moyen, un appel : s'il y en a davantage, on ne sait
# plus lequel a fait les résultats.
stopifnot(length(releve$appels) == 1)
entrees_cor <- releve$appels[[1]]
parametres <- entrees_cor$parametres
param_modele <- entrees_cor$paramModele
retenus <- resultats_cor$dtIdPensionnes[ageMinTxPlein %in% TRUE, id]

# ---------------------------------------------------------------------------
# 2. Les carrières du dépôt
# ---------------------------------------------------------------------------

lire <- function(nom) {
  fread(file.path(entrees, paste0(nom, ".csv")), encoding = "UTF-8")
}
mois <- function(texte) as.Date(paste0(as.character(texte), "-01"))
dt_id <- lire("dtId")
dt_id[, `:=`(dateNaissance = mois(dateNaissance), dateLiq = mois(dateLiq))]
dt_an_etat <- lire("dtIdAnEtat")
dt_fonc <- lire("dtIdAnCaisseFonctionnaire")
dt_enfants <- lire("dtIdNumeroEnfant")
resultats_depot <- calculePension(
  dtId = dt_id,
  dtIdNumeroEnfant = if (nrow(dt_enfants)) dt_enfants else NULL,
  dtIdAnEtat = dt_an_etat,
  dtIdAnCaisseFonctionnaire = if (nrow(dt_fonc)) dt_fonc else NULL,
  parametres = parametres,
  paramModele = param_modele
)

# ---------------------------------------------------------------------------
# Les sorties
# ---------------------------------------------------------------------------

ecrire <- function(table, nom) {
  table <- copy(as.data.table(table))
  # L'âge d'ouverture a perdu ses capitales à la version 3 : les tables gardent
  # le nom que `trajectoire.py` lit.
  if ("aod" %in% names(table) && !"AOD" %in% names(table)) setnames(table, "aod", "AOD")
  # Les dates sont au mois : on les écrit « AAAA-MM ».
  for (colonne in names(table)) {
    valeurs <- table[[colonne]]
    if (inherits(valeurs, "Date")) {
      set(table, j = colonne, value = format(valeurs, "%Y-%m"))
    }
  }
  fwrite(table, file.path(sorties, paste0(nom, ".csv")))
}
colonnes <- function(table, voulues) intersect(voulues, names(table))
sortir <- function(resultats, ids, suffixe) {
  garder <- function(table, voulues) {
    if (is.null(table)) return(data.table(id = character()))
    table <- as.data.table(table)[id %in% ids]
    table[, colonnes(table, voulues), with = FALSE]
  }
  ecrire(garder(resultats$dtIdPensionnes, c(
    "id", "casType", "generation", "ageLiq", "dateNaissance", "sexe", "nbEnfant",
    "ageMort", "categCSG", "dateLiqCaissePrincipale", "caissePrincipale",
    "typeLiquidation", "typeDepart", "aod", "AAD", "dureeRequise",
    "dureeValideeTousRegimes", "aSurcoteDansCaissePrincipale",
    "aDecoteDansCaissePrincipale", "nbTrimDecoteCaissePrincipale",
    "nbTrimSurcoteCaissePrincipale", "aMinPension", "pensionLiqEurosConstants",
    "pensionLiqSmpt", "txRemplacementNet", "txRemplacementNetSmpt",
    "txRemplacementCdv", "txRemplacementNetCdv", "txAnnuite", "txRecuperation",
    "txPrestation", "dureeRetraiteRelativeDureeCotisation", "ageMinTxPlein")),
    paste0("pensionnes_", suffixe))
  ecrire(garder(resultats$dtIdCaisse, c(
    "id", "caisse", "dateLiq", "pension", "pensionAvantMinEtMajo", "majorationEnfant",
    "ajoutMinimum", "taux", "tauxDecote", "tauxSurcote", "nbTrimDecote",
    "nbTrimSurcote", "pensionNette")), paste0("caisses_", suffixe))
  ecrire(garder(resultats$dtIdCaisseBase, c(
    "id", "caisse", "dateLiq", "prorat", "dureeValideeTousRegimes",
    "dureeCotiseTousRegimes", "dureeValidee", "dureeCotisee", "dureeGratuite",
    "dureeRequise", "dureeRequiseProrat", "aod", "AAD", "MDAenfantPourTaux",
    "MDAenfantPourProrat", "nbTrimBonification", "typeDepart", "dateTauxPlein")),
    paste0("bases_", suffixe))
  ecrire(garder(resultats$dtIdCaisseSalaireReference, c("id", "caisse", "salaireReference")),
         paste0("salaires_reference_", suffixe))
  ecrire(garder(resultats$dtIdCaisseFonctionnaire, c(
    "id", "caisse", "majoBonifFonc", "aod", "AAD", "dureeRequise",
    "categFonctionPublique", "typeBonif", "typeMDAFonc", "primesDansCotiseBase")),
    paste0("fonctionnaires_", suffixe))
  ecrire(garder(resultats$dtIdAnCaisse, c(
    "id", "annee", "caisse", "remuneration", "nbTrimCotise", "nbTrimValide",
    "nbTrimGratuit", "montantAvpf")), paste0("annees_", suffixe))
  ecrire(garder(resultats$dtIdAnCaisseComplementaire, c(
    "id", "annee", "caisse", "nbMois", "nbPtCotise", "nbPtGratuit", "nbPt")),
    paste0("points_", suffixe))
  ecrire(garder(resultats$dtIdAnCaisseBasePoint, c(
    "id", "annee", "caisse", "nbMois", "nbPtCotise", "nbPt")),
    paste0("points_base_", suffixe))
  ecrire(garder(resultats$dtIdRacl, c("id", "dateLiqRacl")), paste0("racl_", suffixe))
  ecrire(garder(resultats$dtIdCaisseModulationTemporaire, c("id", "caisse", "taux", "duree")),
         paste0("modulations_", suffixe))
}
sortir(resultats_cor, retenus, "cor")
sortir(resultats_depot, unique(dt_id$id), "depot")

# Les entrées des cas types du COR retenus : la carrière que la fonction du
# paquet a construite, d'où `trajectoire.py` écrit la requête du dépôt.
extraire <- function(table, voulues) {
  table <- as.data.table(table)[id %in% retenus]
  table[, colonnes(table, voulues), with = FALSE]
}
ecrire(extraire(entrees_cor$dtId, c(
  "id", "casType", "sexe", "dateNaissance", "generation", "dateLiq", "ageLiq",
  "ageMort", "nbEnfant", "categCSG")), "entrees_cor_id")
ecrire(extraire(entrees_cor$dtIdAnEtat, c(
  "id", "annee", "etatTravail", "dureeEnMois", "remuneration", "salaireRelatif",
  "smpt")), "entrees_cor_etats")
ecrire(extraire(entrees_cor$dtIdAnCaisse, c(
  "id", "annee", "caisse", "nbTrimGratuit", "nbTrimCotise", "montantAvpf")),
  "entrees_cor_caisses")
ecrire(extraire(entrees_cor$dtIdAnCaisseFonctionnaire, c(
  "id", "annee", "caisse", "primes", "nbTrimValideFonc")), "entrees_cor_fonctionnaires")
# L'âge d'ouverture, l'âge d'annulation de la décote et la durée requise que le
# paquet lit, par génération et catégorie : la législation qu'il porte.
ecrire(parametres$ageDuree, "parametres_age_duree")
# Les paramètres qui expliquent un écart de montant sans relancer R.
annees <- 1960:2035
par_annee <- Reduce(function(x, y) merge(x, y, by = "annee", all = TRUE), list(
  as.data.table(parametres$revaloSam)[, .(annee, revaloSam)],
  as.data.table(parametres$pss)[, .(annee, pss)],
  as.data.table(parametres$salaireValidant)[, .(annee, salaireValidant)],
  as.data.table(parametres$smicAVPF)[, .(annee, smicAVPF)],
  as.data.table(parametres$paramCotis)[, .(
    annee, txCotARRCOsalempl_t1, txCotMIN_ARRCOsalempl_t1, txCotARRCOsalempl_t2,
    txCotMIN_ARRCOsalempl_t2, txCotAGIRCsalempl_TB, txCotMIN_AGIRCsalempl_TB)]
))
ecrire(par_annee[annee %in% annees], "parametres_annuels")
suivies <- c("Arrco", "Agirc", "Agirc-Arrco", "Rafp", "CNAVPL", "CARMF complementaire",
             "CARMF sur-complementaire", "MSA exploitant", "MSA exploitant complementaire")
ecrire(as.data.table(parametres$valeurPtAcquisition)[
  caisse %chin% suivies & annee %in% annees],
  "parametres_valeur_achat")
ecrire(as.data.table(parametres$valeurPtService)[
  caisse %chin% suivies & dateLiq >= as.Date("2010-01-01") &
    dateLiq <= as.Date("2035-12-01"), .(date = dateLiq, caisse, valeurPtService)],
  "parametres_valeur_service")
ecrire(as.data.table(parametres$revalo)[
  caisse %chin% c("SRE", "CNRACL") & dateValeurPension >= as.Date("2010-01-01") &
    dateValeurPension <= as.Date("2035-12-01"), .(date = dateValeurPension, caisse, revalo)],
  "parametres_revalorisation_fonction_publique")

versions <- list(
  R = paste(R.version$major, R.version$minor, sep = "."),
  trajectoire = as.character(packageVersion("trajectoire")),
  legiretraite = as.character(packageVersion("legiretraite")),
  data.table = as.character(packageVersion("data.table")),
  logger = as.character(packageVersion("logger")),
  plateforme = R.version$platform
)
writeLines(jsonlite::toJSON(versions, auto_unbox = TRUE, pretty = TRUE),
           file.path(sorties, "versions.json"))
