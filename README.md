# Clinicaltrials.gov analytics
Includes cheminformatics and medical terms text mining.

Utilizes the AACT-CTTI database from Duke.
* CTTI = Clinical Trials Transformation Initiative
* AACT = Aggregate Analysis of ClinicalTrials.gov
* See https://aact.ctti-clinicaltrials.org/.
* According to website (July 2018), data is refreshed monthly.

Text mining performed with [NextMove Leadmine](http://nextmovesoftware.com).

Identify drugs by intervention ID, since may be multiple
drugs per trial (NCT\_ID).

### Purpose:
* Associate drugs with diseases/phenotypes.
* Associate protein targets with diseases/phenotypes.
* Associate drugs with protein targets.

### Tables of interest:
* studies
* keywords
* brief\_summaries
* detailed\_descriptions
* conditions
* browse\_conditions           (NCT-MeSH links)
* interventions
* browse\_interventions        (NCT-MeSH links)
* intervention\_other\_names    (synonyms)
* study\_references            (including type results\_reference)

### Overall workflow:
* Go\_ct\_GetData.sh  - Fetch selected data from AACT db.
* Go\_xref\_drugs.sh  - PubChem and ChEMBL IDs via APIs.
* Go\_BuildDicts.sh  - Build NextMove LeadMine dicts for MeSH etc. NER.
* Go\_NER.sh         - LeadMine NER.
* Go\_NER\_pubmed.sh  - LeadMine NER, selected referenced PMIDs.
* leadmine\_utils.sh - Runs LeadMine API custom app on TSVs.

* Resulting files can be analyzed for associations.  See R code.
