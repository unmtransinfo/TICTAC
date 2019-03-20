#!/usr/bin/env Rscript
#############################################################################
library(readr)
library(dplyr, quietly=T)

drugs_leadmine <- read_delim("data/aact_drugs_leadmine.tsv",  "\t", escape_double=F, trim_ws=T)
drugs_leadmine <- dplyr::rename(drugs_leadmine, id = DocName, smiles = ResolvedForm)
#
drugs_smi <- drugs_leadmine[!is.na(drugs_leadmine$smiles), c("smiles","OriginalText")]
drugs_smi <- unique(drugs_smi)
drugs_smi <- rename(drugs_smi, name = "OriginalText")
writeLines(sprintf("Unique drug smiles: %d", length(unique(drugs_smi$smiles))))
#
# Aggregate by same smiles.
drugs_smi <- group_by(drugs_smi, smiles) %>% summarise(names = paste(name, collapse="; "))
drugs_smi <- drugs_smi[order(nchar(drugs_smi$smiles)),]
write_delim(drugs_smi, "data/aact_drugs_smi.smi", "\t", col_names=F)
#
