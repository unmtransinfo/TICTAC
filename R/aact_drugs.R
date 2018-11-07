#!/usr/bin/env Rscript
#############################################################################
### CTTI = Clinical Trials Transformation Initiative
### AACT = Aggregate Analysis of ClinicalTrials.gov
### According to website (July 2018), data is refreshed monthly.
### https://aact.ctti-clinicaltrials.org/
#############################################################################
### See also: https://github.com/ctti-clinicaltrials/aact
#############################################################################
### aact_drugs.tsv from intervention_drug_list.sql
### aact_drugs_leadmine.tsv from Go_NER.sh
#############################################################################
### nct_id is the study ID. 
#############################################################################
library(readr)
library(dplyr, quietly = T)
library(plotly, quietly = T)

#Studies
studies <- read_delim("data/aact_studies.tsv", "\t")
n_studies_total <- nrow(studies)
writeLines(sprintf("Total trials (NCT_IDs): %d", n_studies_total))
studies <- studies[studies$study_type=="Interventional",]
studies$study_type <- NULL
n_studies_itv <- nrow(studies)
writeLines(sprintf("Interventional trials: %d (%.1f%%)", n_studies_itv, 100*n_studies_itv/n_studies_total))
studies$phase[studies$phase == "N/A"] <- NA
writeLines("===All studies, phase:")
tbl <- table(studies$phase, useNA="ifany")
writeLines(sprintf("%18s: %6d", names(tbl), tbl))
#
#Drugs 
drugs <- read_delim("data/aact_drugs.tsv", "\t", col_types = "dcc")
studies <- merge(studies, dplyr::rename(drugs, drug_name = name, drug_itv_id = id), by="nct_id", all=T)
studies[["is_drug_trial"]] <- !is.na(studies$drug_itv_id)
#
drugs <- merge(drugs, studies, by="nct_id", all.x=T, all.y=F)
drugs <- drugs[order(drugs$name),]
#
writeLines("===All drugs, phase:")
tbl <- table(drugs$phase, useNA="ifany")
writeLines(sprintf("%18s: %6d", names(tbl), tbl))
writeLines(sprintf("Drug trials (NCT_IDs): %d", length(unique(drugs$nct_id))))
writeLines(sprintf("Unique drug names: %d", length(unique(drugs$name))))
#
drugs_leadmine <- read_delim("data/aact_drugs_leadmine.tsv",  "\t", escape_double=F, trim_ws=T)
drugs_leadmine <- dplyr::rename(drugs_leadmine, id = DocName, smiles = ResolvedForm)
#
drugs <- merge(drugs, drugs_leadmine, by="id")
drugs[["resolved_structure"]] <- !is.na(drugs$smiles)
#
writeLines("===Drugs, resolved structure:")
tbl <- table(drugs$resolved_structure)
writeLines(sprintf("%18s: %6d", names(tbl), tbl))
#
writeLines("===Drugs, overall_status:")
tbl <- table(drugs$overall_status)
writeLines(sprintf("%18s: %6d", names(tbl), tbl))
#
#plot_ly(type="pie", data=count(drugs, resolved_structure))
#
###
prefix <- "AACT"
ax0 <- list(showline=F, zeroline=F, showticklabels=F, showgrid=F)
drugs[["begin_year"]] <- as.integer(format(drugs$start_date, "%Y"))
#
p1 <- plot_ly() %>%
  add_trace(type="bar", data=count(drugs, begin_year), x = ~begin_year, y = ~n) %>%
  layout(title=paste0(prefix, ": Drug trials per begin-year"), xaxis=list(range=c(1990, 2019)))
p1
##
p2 <- plot_ly() %>%
  add_pie(data=count(drugs, phase), labels=~phase, values=~n, sort=F,
          textinfo="label+percent", textposition="inside", domain=list(x=c(0, 0.5), y=c(0, 1))) %>%
  add_pie(data = count(drugs, overall_status), labels = ~overall_status, values = ~n,
          textinfo = "label+percent", textposition = "inside", domain = list(x = c(0.5, 1), y = c(0, 1))) %>%
  add_annotations(x = c(0.25, 0.75), y = c(-.1, -.1),
                  xanchor = "center", xref = "paper", yref = "paper", showarrow = F,
                  text = c("Phase", "Overall status"),
                  font = list(family = "Arial", size = 20)) %>%
  layout(title = paste0(prefix, ": Drug trial classification<br>(N_total = ", nrow(drugs), ")"),
         xaxis=ax0, yaxis=ax0, margin=list(t = 120), showlegend = F)
p2
###
#
drugs_smi <- drugs_leadmine[!is.na(drugs_leadmine$smiles),c("smiles","OriginalText")]
drugs_smi <- unique(drugs_smi)
drugs_smi <- rename(drugs_smi, name = "OriginalText")
#drugs_smi <- drugs_smi[order(drugs_smi$name),]
writeLines(sprintf("Unique drug smiles: %d", length(unique(drugs_smi$smiles))))
#
# Aggregate by same smiles.
drugs_smi <- group_by(drugs_smi, smiles) %>% summarise(names = paste(name, collapse="; "))
drugs_smi <- drugs_smi[order(nchar(drugs_smi$smiles)),]
write_delim(drugs_smi, "data/aact_drugs_smi.smi", "\t", col_names=F)
#
###
# Aggregate mentions by intervention ID.
ner <- drugs_leadmine[!is.na(drugs_leadmine$smiles),] %>% group_by(id) %>% summarise(n = n())
writeLines(sprintf("Mentions by intervention ID: %.1f%% (%d/%d)", 
                   100*nrow(ner)/length(unique(drugs$id)),
                   nrow(ner), length(unique(drugs$id))))
#
# Aggregate mentions by trial.
drugs_leadmine <- merge(drugs_leadmine, drugs[,c("drug_itv_id", "nct_id")], by.x="id", by.y="drug_itv_id")
ner <- drugs_leadmine[!is.na(drugs_leadmine$smiles),] %>% group_by(nct_id) %>% summarise(n = n())
writeLines(sprintf("Mentions by study: %.1f%% (%d/%d)", 
                   100*nrow(ner)/length(unique(drugs$nct_id)),
                   nrow(ner), length(unique(drugs$nct_id))))
#
# Aggregate mentions by drug.
ner <- drugs_leadmine[!is.na(drugs_leadmine$smiles),] %>% group_by(OriginalText) %>% summarise(n = n())
writeLines(sprintf("Mentions by drug name: %.1f%% (%d/%d)", 
                   100*nrow(ner)/length(unique(drugs$name)),
                   nrow(ner), length(unique(drugs$name))))
#
###
# PUBCHEM:
# Intervention IDs to CIDs from PubChem (via SMILES)
drug2cid <- read_delim("data/aact_drugs_smi_pubchem_cid.tsv", "\t", col_names=c("smiles","cid","names"))
drug2cid <- drug2cid[!is.na(drug2cid$cid),]
drug2cid <- drug2cid[drug2cid$cid!=0,]
drug2cid <- merge(drug2cid, unique(drugs[,c("smiles","id")]), all.x=F, all.y=F, by="smiles")
drug2cid <- dplyr::rename(drug2cid, itv_id = "id")
drug2cid$smiles <- NULL
drug2cid$names <- NULL
drug2cid <- unique(drug2cid)
writeLines(sprintf("Intervention IDs mapped to PubChem CIDs (via SMILES): %d", nrow(drug2cid)))
write_delim(drug2cid, "data/aact_drugs_itvid2cid.tsv", delim="\t")
#
#InChIKeys from PubChem (via CIDs)
pubchem <- read_delim("data/aact_drugs_smi_pubchem_cid2inchi.tsv", "\t")
writeLines(sprintf("PubChem CIDs with InChIKeys: %d", nrow(pubchem)))

###
# CHEMBL:
#ChEMBL molecule IDs, and properties (via InChIKeys)
chembl_mol <- read_delim("data/aact_drugs_inchi2chembl.tsv", "\t")
writeLines(sprintf("ChEMBL compounds mapped via InChIKeys: %d", nrow(chembl_mol)))

#ChEMBL activities (via compounds)
chembl_act <- read_delim("data/aact_drugs_chembl_activity_pchembl.tsv", "\t")
writeLines(sprintf("ChEMBL activities (with pChembl): %d", nrow(chembl_act)))

#ChEMBL target IDs (via activities)
chembl_tgt <- read_delim("data/aact_drugs_chembl_target_component.tsv", "\t")
writeLines(sprintf("ChEMBL target proteins: %d", nrow(chembl_tgt)))

###
#IDG/TCRD:
tcrd_tgt <- read_delim("~/projects/IDG/TCRD/data/pharos_targets.tsv", "\t")

tgt <- merge(chembl_tgt, tcrd_tgt, all.x=T, all.y=F, by.x="accession", by.y="accession")
writeLines(sprintf("ChEMBL target proteins mapped to TCRD (human): %d",
	nrow(tgt[!is.na(tgt$idgTDL),])))

writeLines("===Targets, human_or_other:")
print(table(tgt$organism=="Homo sapiens"))

writeLines("===Targets, TDL for human:")
print(table(tgt$idgTDL[tgt$organism=="Homo sapiens"], useNA="ifany"))

