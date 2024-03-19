# ******************************************************************************************** #
# Load necessary libraries
# ******************************************************************************************** #

library(readr)
library(dplyr)
library(tidyr)
library(purrr)
library(tidyverse)
library(openxlsx)

options(dplyr.summarise.inform = FALSE)

# ******************************************************************************************** #
# Print a welcome message
# ******************************************************************************************** #

cat("
Velkommen til R-versjonen av Lærermod!

+---------------------------------------------------------------+
|    Modellen LÆRERMOD beregner tilbud av og                    |
|    etterspørsel for følgende 7 grupper av lærere:             |
+---------------------------------------------------------------+
| 1. Barnehagelærere                                            |
| 2. Grunnskolelærere                                           |
| 3. Lektorutdannede                                            |
| 4. PPU                                                        |
| 5. Lærerutdanning i praktiske og estetiske fag                |
| 6. Yrkesfaglærere                                             |
| 7. PPU Yrkesfag                                               |
+---------------------------------------------------------------+
\n")

# ******************************************************************************************** #
# Define start and end years for the projection
# ******************************************************************************************** #

Basisår <- 2020
Sluttår <- 2040

# ******************************************************************************************** #
# Reading input files. See Appendix 1 for source data.
# ******************************************************************************************** #

Aldersfordelt <- read.table("inndata/aldersfordelt.txt", header = TRUE, sep = "")
AldersfordeltStudenter <- read.table('inndata/aldersfordeltstudenter.txt', header = TRUE, sep = "")
Kandidatproduksjon <- read.table('inndata/kandidatproduksjon.txt', header = TRUE, sep = "")
Sektorfordelt <- read.table('inndata/sektorfordelt.txt', header = TRUE, sep = "")
Befolkning <- read.table('inndata/mmmm.txt', header = TRUE, sep = "")
DemografiGruppe1 <- read.table('inndata/antall_barn_barnehager.txt', header = TRUE, sep = "")
DemografiGruppe3 <- read.table('inndata/antall_elever_videregaende.txt', header = TRUE, sep = "")
DemografiGruppe4 <- read.table('inndata/antall_studenter_hoyereutdanning.txt', header = TRUE, sep = "")
Vakanse <- read.table('inndata/vakanse.txt', header = TRUE, sep = "")
Standardendring <- read.table('inndata/endring_standard_R.txt', header = TRUE, sep = "")
Timeverkendring <- read.table('inndata/endring_timeverk.txt', header = TRUE, sep = "")

# ******************************************************************************************** #
# Setting index for easier data manipulation
# ******************************************************************************************** #

#Aldersfordelt <- Aldersfordelt %>% mutate(Utdanning = factor(Utdanning)) %>% tibble::column_to_rownames(var = "Utdanning")
#AldersfordeltStudenter <- AldersfordeltStudenter %>% mutate(Utdanning = factor(Utdanning)) %>% tibble::column_to_rownames(var = "Utdanning")
#Kandidatproduksjon <- Kandidatproduksjon %>% mutate(Utdanning = factor(Utdanning)) %>% tibble::column_to_rownames(var = "Utdanning")
#Sektorfordelt <- Sektorfordelt %>% mutate(Utdanning = factor(Utdanning), Sektor = factor(Sektor)) %>% tidyr::spread(key = Sektor, value = value)
#Befolkning <- Befolkning %>% mutate(Alder = factor(Alder), Kjønn = factor(Kjønn)) %>% tidyr::unite("Index", Alder, Kjønn, sep = "_") %>% tibble::column_to_rownames(var = "Index")

Aldersfordelt <- Aldersfordelt %>% mutate(Utdanning = factor(Utdanning))
AldersfordeltStudenter <- AldersfordeltStudenter %>% mutate(Utdanning = factor(Utdanning))
Kandidatproduksjon <- Kandidatproduksjon %>% mutate(Utdanning = factor(Utdanning))
Sektorfordelt <- Sektorfordelt %>% mutate(Utdanning = factor(Utdanning), Sektor = factor(Sektor))
Befolkning <- Befolkning %>% mutate(Alder = factor(Alder), Kjønn = factor(Kjønn))

# ******************************************************************************************** #
# Define abbreviations for the types of education included in the model
# ******************************************************************************************** #

Utdanninger <- c('ba', 'gr', 'lu', 'ph', 'pe', 'yr', 'py')

# ******************************************************************************************** #
# Initialize dictionaries for later use (In R, we use lists for this purpose)
# ******************************************************************************************** #

BefolkningSektor <- list()
Brukergruppe <- list()
DemografiSektor <- list()
DemografiGruppe <- list()
SumDemografiGruppe <- list()
RelativeBrukere <- list()

# ******************************************************************************************** #
# Supply
# ******************************************************************************************** #

# ******************************************************************************************** #
# Initial teacher population
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculating employment rate
# This is Equation 1 in the model.
# ******************************************************************************************** #

Aldersfordelt$Sysselsettingsandel <- ifelse(Aldersfordelt$Antall > 0, 
                                            Aldersfordelt$Sysselsatte / Aldersfordelt$Antall, 
                                            0)

# ******************************************************************************************** #
# Copying this into a table and removing now redundant columns
# ******************************************************************************************** #

Populasjon <- Aldersfordelt
Aldersfordelt <- Aldersfordelt %>% select(-Antall, -Sysselsatte)

# ******************************************************************************************** #
# Finding the full-time equivalents in the population
# This is Equation 2 in the model.
# ******************************************************************************************** #

Populasjon$Årsverk <- Populasjon$Sysselsatte * Populasjon$GjennomsnitteligeÅrsverk

# ******************************************************************************************** #
# Indicating that this is the population in the base year and removing now redundant columns
# ******************************************************************************************** #

Populasjon$År <- Basisår
Populasjon <- Populasjon %>% select(-Sysselsatte, -Sysselsettingsandel, -GjennomsnitteligeÅrsverk)

# ******************************************************************************************** #
# Projecting the initial population from Year 2 to the final year, based on base year stats
# ******************************************************************************************** #

# ******************************************************************************************** #
# Candidate production:
# First, calculate the total number of first-year students for each of the educations.
# This is Equation 3 in the model.
# ******************************************************************************************** #

AntallFørsteårsStudenter <- AldersfordeltStudenter %>% 
  group_by(Utdanning) %>% 
  summarise(Totalt = sum(Alle)) %>% 
  ungroup()

# ******************************************************************************************** #
# Copy the total number of students for the relevant education into a new column in
# the AldersfordeltStudenter table. Add a variable for gender.
# ******************************************************************************************** #

AldersfordeltStudenter <- AldersfordeltStudenter %>%
  inner_join(AntallFørsteårsStudenter, by = "Utdanning")

# Since the original Python code seems to duplicate the AldersfordeltStudenter DataFrame
# and append it with a gender differentiation without specifying how gender is handled,
# we assume here the intention is to prepare the data for gender-specific analysis.
# We will add a gender column and duplicate the data with gender specification.

NyeStudenter <- AldersfordeltStudenter %>%
  mutate(Kjønn = 1) %>%
  bind_rows(AldersfordeltStudenter %>% mutate(Kjønn = 2))

# Please adjust the gender assignment as per your actual data specifications
# and analysis requirements.

# ******************************************************************************************** #
# Calculate the proportion of students by each age and gender.
# This is Equation 4 in the model.
# ******************************************************************************************** #

NyeStudenter <- NyeStudenter %>%
  mutate(AndelStudenterEtterAlder = if_else(Kjønn == 1, 
                                            Menn / Totalt, 
                                            Kvinner / Totalt))

# Note: This assumes 'Menn' and 'Kvinner' columns exist and contain the distribution of male
# and female students, respectively, and 'Totalt' is the total number of students.
# 'Kjønn' is assumed to be a binary indicator where 1 represents male and 2 represents female.

# ******************************************************************************************** #
# Specify that the number of students is constant in each projection year.
# ******************************************************************************************** #

# Create a dataframe with all combinations of years and educations
Years <- data.frame(År = Basisår:Sluttår)
UtdanningYears <- expand.grid(Utdanning = Utdanninger, År = Years$År)

# Merge with the Kandidatproduksjon dataframe
Kandidatproduksjon <- Kandidatproduksjon %>%
  inner_join(UtdanningYears, by = "Utdanning")

# Note: This code assumes that 'Kandidatproduksjon' already contains a column named 'Utdanning'
# that matches the education types in 'Utdanninger'. Adjust the column names and dataframe structures
# as necessary to match your actual data.

# ******************************************************************************************** #
# Calculating the number of annual graduates using new students and completion percentages.
# This is Equation 5 in the model.
# ******************************************************************************************** #

Kandidatproduksjon <- Kandidatproduksjon %>%
  mutate(Kandidater = AntallNyeStudenter * Fullføringsprosent)

# ******************************************************************************************** #
# Specify that the number of graduates is to be constant in the projection period.
# ******************************************************************************************** #

#Kandidater <- inner_join(NyeStudenter, Kandidatproduksjon, by = "Utdanning")
Kandidater <- inner_join(NyeStudenter, Kandidatproduksjon, by = "Utdanning", relationship =
  "many-to-many")

# ******************************************************************************************** #
# Calculating graduation age and number of graduates by gender. Ensure that the graduation age
# column is named the same as in the table to which rows will be added later, even though
# the name might be a bit misleading in this context.
# This is Equation 6 and Equation 7 in the model.
# ******************************************************************************************** #

Kandidater <- Kandidater %>%
  mutate(Alder = Alder + Studielengde,
         UteksaminerteEtterAlder = Kandidater * AndelStudenterEtterAlder)

# ******************************************************************************************** #
# Copy the population from the base year, calculated in Equation 2, into two new tables that
# will serve as the basis for the calculations.
# ******************************************************************************************** #

# In R, the assignment operator creates copies by default, so there's no need for an explicit copy function
PopulasjonAktueltÅr <- Populasjon

# Assuming Basisår, Sluttår, Populasjon, and Kandidater are already defined in your R environment

for (t in (Basisår + 1):Sluttår) {
  
  # Aging the population
  PopulasjonAktueltÅr$Alder <- PopulasjonAktueltÅr$Alder + 1
  
  # Merging new candidates
  # Ensure Kandidater has been filtered or prepared similarly as in Python before this step
  PopulasjonAktueltÅr <- merge(x = PopulasjonAktueltÅr, 
                               y = Kandidater[Kandidater$År == t, ], 
                               by = c("Utdanning", "Kjønn", "Alder"), 
                               all = TRUE)
  
  # Adding graduates (assuming UteksaminerteEtterAlder is a column in Kandidater)
  PopulasjonAktueltÅr$Antall <- ifelse(is.na(PopulasjonAktueltÅr$Antall), 0, PopulasjonAktueltÅr$Antall) + 
                                ifelse(is.na(PopulasjonAktueltÅr$UteksaminerteEtterAlder), 0, PopulasjonAktueltÅr$UteksaminerteEtterAlder)
  
  # Setting the year of the projection
  PopulasjonAktueltÅr$År <- t
  
  # Appending the annual projection to the cumulative dataset
  Populasjon <- rbind(Populasjon, PopulasjonAktueltÅr[, c("Utdanning", "Kjønn", "Alder", "Antall", "Årsverk", "År")])
  
  # Preparing for the next year's projection
  PopulasjonAktueltÅr <- Populasjon[Populasjon$År == t, ]
  
}

# Assuming Populasjon and Aldersfordelt are already defined data frames in your R environment
# and have the columns Utdanning, Kjønn, Alder, Antall, Sysselsettingsandel, and GjennomsnitteligeÅrsverk as applicable.

# Merging Populasjon with Aldersfordelt to get Sysselsettingsandel and Gjennomsnittelige Årsverk
# This will create the table for the supply (Tilbud)
Tilbud <- merge(x = Populasjon, 
                y = Aldersfordelt, 
                by = c("Utdanning", "Kjønn", "Alder"), 
                all.x = TRUE)

# Calculating the supply (Tilbud) according to Equation 10 in your model
Tilbud$Tilbud <- Tilbud$Antall * Tilbud$Sysselsettingsandel * Tilbud$GjennomsnitteligeÅrsverk

# Assuming Sektorfordelt dataframe is already defined with the columns for SysselsatteMenn,
# GjennomsnitteligeÅrsverkMenn, SysselsatteKvinner, and GjennomsnitteligeÅrsverkKvinner,
# and that Utdanninger is a vector listing the 7 educations.

# Calculating initial demand in the base year (Basisår) according to Equation 11
Sektorfordelt$Etterspørsel <- (Sektorfordelt$SysselsatteMenn * Sektorfordelt$GjennomsnitteligeÅrsverkMenn) + 
                             (Sektorfordelt$SysselsatteKvinner * Sektorfordelt$GjennomsnitteligeÅrsverkKvinner)
Sektorfordelt$År <- Basisår

# Creating an empty demand table for the 7 educations
Etterspørsel <- data.frame(Utdanning = Utdanninger, Etterspørsel = rep(0, length(Utdanninger)))

# Iterating through the 7 educations and the 6 sectors to populate the demand table
# Assuming Sektorfordelt is structured with a multi-level index or similar to group data by sector,
# and assuming that the 'Sektor' variable or grouping is available.
# The exact implementation might vary based on how your data is structured.

for (S in 1:6) {
  # Creating demand columns for each sector
  Etterspørsel[paste0('EtterspørselSektor', S)] <- Sektorfordelt$Etterspørsel[Sektorfordelt$Sektor == S]
}

# Initialize an empty list to store the data frames for each user group
Brukergruppe <- list()

# Creating data frames for each user group with their corresponding age ranges

# User Group 1
Brukergruppe[[1]] <- data.frame(TilAlder = c(0, 2, 2, 3, 5, 5),
                                Alder = 0:5)

# User Group 2
Brukergruppe[[2]] <- data.frame(TilAlder = rep(15, 10),
                                Alder = 6:15)

# User Group 3
Brukergruppe[[3]] <- data.frame(TilAlder = c(rep(15, 16), 16:24, rep(49, 25)),
                                Alder = 0:49)

# User Group 4
Brukergruppe[[4]] <- data.frame(TilAlder = c(19:29, rep(34, 5), rep(39, 5), rep(44, 5), rep(49, 5)),
                                Alder = 19:49)

# User Group 5
Brukergruppe[[5]] <- data.frame(TilAlder = rep(99, 100),
                                Alder = 0:99)

# User Group 6
Brukergruppe[[6]] <- data.frame(TilAlder = rep(99, 100),
                                Alder = 0:99)
# Assuming DemografiGruppe1 is already defined with columns for Age0, Age1, Age2, Age3, Age4, Age5,
# TimerMin, and TimerMax

# Calculating the average users and their average stay time for each group

BarnGruppe1 <- data.frame(Brukere = DemografiGruppe1$Alder0,
                          Timer = DemografiGruppe1$TimerMin + 
                                  ((DemografiGruppe1$TimerMax - DemografiGruppe1$TimerMin) / 2))

BarnGruppe2 <- data.frame(Brukere = DemografiGruppe1$Alder1 + DemografiGruppe1$Alder2,
                          Timer = DemografiGruppe1$TimerMin + 
                                  ((DemografiGruppe1$TimerMax - DemografiGruppe1$TimerMin) / 2))

BarnGruppe3 <- data.frame(Brukere = DemografiGruppe1$Alder3,
                          Timer = DemografiGruppe1$TimerMin + 
                                  ((DemografiGruppe1$TimerMax - DemografiGruppe1$TimerMin) / 2))

BarnGruppe4 <- data.frame(Brukere = DemografiGruppe1$Alder4 + DemografiGruppe1$Alder5,
                          Timer = DemografiGruppe1$TimerMin + 
                                  ((DemografiGruppe1$TimerMax - DemografiGruppe1$TimerMin) / 2))
# Initialize the list to store demographic groups if not already initialized
DemografiGruppe <- list()

# Create an empty data frame for the first demographic group
DemografiGruppe[[1]] <- data.frame(FraAlder = integer(), TilAlder = integer(), 
                                   Brukere = integer(), Brukerindeks = numeric())

# Calculate users and user index for each of the 4 child groups and add to the DemografiGruppe data frame

# Group 1
DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder = 0, TilAlder = 0, 
                                        Brukere = sum(BarnGruppe1$Brukere), 
                                        Brukerindeks = (2 * sum(BarnGruppe1$Brukere * BarnGruppe1$Timer)) / 
                                                       (sum(BarnGruppe1$Brukere) * 42.5)))

# Group 2
DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder = 1, TilAlder = 2, 
                                        Brukere = sum(BarnGruppe2$Brukere), 
                                        Brukerindeks = (2 * sum(BarnGruppe2$Brukere * BarnGruppe2$Timer)) / 
                                                       (sum(BarnGruppe2$Brukere) * 42.5)))

# Group 3
DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder = 3, TilAlder = 3, 
                                        Brukere = sum(BarnGruppe3$Brukere), 
                                        Brukerindeks = (1.5 * sum(BarnGruppe3$Brukere * BarnGruppe3$Timer)) / 
                                                       (sum(BarnGruppe3$Brukere) * 42.5)))

# Group 4
DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder = 4, TilAlder = 5, 
                                        Brukere = sum(BarnGruppe4$Brukere), 
                                        Brukerindeks = (1 * sum(BarnGruppe4$Brukere * BarnGruppe4$Timer)) / 
                                                       (sum(BarnGruppe4$Brukere) * 42.5)))

# Assuming DemografiGruppe is a list where different demographic groups will be stored,
# Befolkning is a dataframe with age-specific population data, and
# Basisår is defined with the base year of interest.

# Convert the Alder column from factor to numeric if it's not already numeric
Befolkning$Alder <- as.numeric(as.character(Befolkning$Alder))

# Now, calculate the number of students in primary education for demographic group 2
DemografiGruppe[[2]] <- data.frame(FraAlder = 6,
                                   TilAlder = 15,
                                   Brukere = sum(Befolkning[Befolkning$Alder >= 6 & Befolkning$Alder <= 15, 
                                                           paste0("X", as.character(Basisår))]),
                                   Brukerindeks = 1.0)

# Assuming DemografiGruppe3 and DemografiGruppe4 data frames are already defined in your R environment,
# as well as the Befolkning data frame and Basisår variable.

# Copy users in Sector 3 and 4 that were read earlier
DemografiGruppe[[3]] <- DemografiGruppe3
DemografiGruppe[[4]] <- DemografiGruppe4

# Calculate users of other in the sector (adult education, vocational schools, etc.)
DemografiGruppe[[5]] <- data.frame(FraAlder = 0,
                                   TilAlder = 99,
                                   Brukere = sum(Befolkning[, paste0("X", as.character(Basisår))]),
                                   Brukerindeks = 1.0)

# Calculate users outside the sector
DemografiGruppe[[6]] <- data.frame(FraAlder = 0,
                                   TilAlder = 99,
                                   Brukere = sum(Befolkning[, paste0("X", as.character(Basisår))]),
                                   Brukerindeks = 1.0)

# Initialize lists or data frames if not already done
BefolkningSektor <- list()
RelativeBrukere <- list()
SumDemografiGruppe <- list()
DemografiSektor <- list()

for (S in 1:6) {
  # Merging user group data with population projections and summing by age group
  BefolkningSektor[[S]] <- merge(Brukergruppe[[S]], Befolkning, by = "Alder") %>%
    group_by(TilAlder) %>%
    summarize(across(c(paste0("X", as.character(Basisår)):paste0("X", as.character(Sluttår))), \(x) sum(x, na.rm = TRUE)))
  
  # Setting the row names to the maximum age of the user group for DemografiGruppe
  rownames(DemografiGruppe[[S]]) <- DemografiGruppe[[S]]$TilAlder
  
  # Calculating relative users for the base year (Equation 20)
  DemografiGruppe[[S]][paste0("RelativeBrukere", paste0("X", as.character(Basisår)))] <- DemografiGruppe[[S]]$Brukere *
                                                             DemografiGruppe[[S]]$Brukerindeks

  # Calculating relative users for each projection year (Equation 21)
  for (t in (Basisår + 1):Sluttår) {
    DemografiGruppe[[S]][[paste0("RelativeBrukere", paste0("X", as.character(t)))]] <- DemografiGruppe[[S]][[paste0("RelativeBrukere", paste0("X", as.character(t-1)))]] *
                                                           (BefolkningSektor[[S]][[paste0("X", as.character(t))]] / 
                                                            BefolkningSektor[[S]][[paste0("X", as.character(t-1))]])
  }
  # Summing relative users for each year (Equation 22)
  SumDemografiGruppe[[S]] <- data.frame(t(Basisår:Sluttår))
  for (t in Basisår:Sluttår) {
    SumDemografiGruppe[[S]][[paste0("SumRelativeBrukere", paste0("X", as.character(t)))]] <- sum(DemografiGruppe[[S]][[paste0("RelativeBrukere", paste0("X", as.character(t)))]], na.rm = TRUE)
  }
    
  # Initializing demographic development table for the sector
  #DemografiSektor[[S]] <- data.frame(År = Basisår, 
  #                                   paste0("DemografiKomponent", S) = 1)
    
  # Correcting the approach for setting dynamic column names in the data frame

  # Initializing demographic development table for the sector with a temporary placeholder column name
  tempColumnName <- paste0("DemografiKomponent", S)
  DemografiSektor[[S]] <- data.frame(År = paste0("X", as.character(Basisår)), TempColumn = 1)
  
  # Renaming the temporary column to the desired dynamic name
  names(DemografiSektor[[S]])[names(DemografiSektor[[S]]) == "TempColumn"] <- tempColumnName
  
  # Calculating demographic development for each projection year for each user group (Equation 23)
  for (t in (Basisår + 1):Sluttår) {
    NesteÅrgang <- data.frame(År = paste0("X", as.character(t)))
    NesteÅrgang[tempColumnName] <- SumDemografiGruppe[[S]][[paste0("SumRelativeBrukere", paste0("X", as.character(t)))]] / 
                                   SumDemografiGruppe[[S]][[paste0("SumRelativeBrukere", paste0("X", as.character(Basisår)))]]
    
    # Adding the new year's data to the demographic development table for the sector
    DemografiSektor[[S]] <- rbind(DemografiSektor[[S]], NesteÅrgang)
  }
  # Correct approach to dynamically name a column and assign values
  # Initializing the DemografiSektor[[S]] data frame
  DemografiSektor[[S]] <- data.frame(År = paste0("X", as.character(Basisår)))
  DemografiSektor[[S]][[paste0("DemografiKomponent", S)]] <- 1
  
  # Calculating demographic development for each projection year for each user group (Equation 23)
  for (t in (Basisår + 1):Sluttår) {
    # Creating a new data frame for the next year
    NesteÅrgang <- data.frame(År = paste0("X", as.character(t)))
    # Dynamically adding the DemografiKomponent column with values
    NesteÅrgang[[paste0("DemografiKomponent", S)]] <- SumDemografiGruppe[[S]][[paste0("SumRelativeBrukere", paste0("X", as.character(t)))]] /
                                                      SumDemografiGruppe[[S]][[paste0("SumRelativeBrukere", paste0("X", as.character(Basisår)))]]
    
    # Concatenating this year's data to the demographic development data frame for the sector
    DemografiSektor[[S]] <- rbind(DemografiSektor[[S]], NesteÅrgang)
  }
}

# Assuming Standardendring and other necessary datasets are already loaded into your R environment

# Copy tables with demographic development in each sector into a single table (alternative path)
DemografiIndeks <- Standardendring # Assuming this is correctly initialized
for (Sektor in 1:6) {
  DemografiIndeks <- merge(DemografiIndeks, DemografiSektor[[Sektor]], by = "År", all = TRUE)
}
expanded_data <- DemografiIndeks %>% 
  expand_grid(Utdanning = Utdanninger)

DemografiIndeks <- expanded_data %>%
  arrange(Utdanning, År)

# Add the constant indicating the 7 educations in the model to the table
#DemografiIndeks <- DemografiIndeks %>%
#  expand_grid(Utdanning = Utdanninger, .data = .) %>%
#  arrange(Utdanning, År)
#print(DemografiIndeks)
# Assuming calculation of teacher densities and vacancy data is done earlier

# Combine the table with demographic development in each sector, the transposed table with demand
# found in Equation 11, and any specified vacancy into the same table
Etterspørsel <- merge(DemografiIndeks, Etterspørsel, by = c("Utdanning"), all = TRUE)
#print(Etterspørsel)#, n=Inf, width=Inf)
#Etterspørsel <- merge(Etterspørsel, Vakanse, by = c("Utdanning", "År"), all = TRUE)

# Calculate the demand (Equation 24 and 25)
# Note: Implement the specific calculations as per your model's equations
# Adding "X" prefix to each value in the "År" column of the Tilbud dataframe

for(S in 1:6) {
  Etterspørsel <- Etterspørsel %>%
    mutate(!!sym(paste0("Etterspørsel")) := !!sym(paste0("Etterspørsel")) +
             ( !!sym(paste0("EtterspørselSektor", S)) +
 #              !!sym(paste0("VakanseSektor", S)) ) *
              0) *
             !!sym(paste0("DemografiKomponent", S)) *
             !!sym(paste0("StandardEndring", S))
           )
}

#print(Etterspørsel)
Tilbud$År <- paste0("X", as.character(Tilbud$År))

# First aggregation (adjusting to ensure structure matches)
first_aggregate <- aggregate(Etterspørsel ~ Utdanning + År, data = Sektorfordelt, FUN = sum)
first_aggregate$År <- paste0("X", as.character(Basisår)) # Adjust all rows to have the modified year

# Ensure the column names exactly match what is expected in the second aggregate
first_aggregate <- first_aggregate[, c("Utdanning", "År", "Etterspørsel")] # Adjust column order if necessary

# Second aggregation (your existing approach, assuming "År" values in Tilbud already have "X" prefixed where necessary)
second_aggregate <- aggregate(Tilbud ~ Utdanning + År, data = Tilbud, FUN = sum, subset = År > paste0("X", as.character(Basisår)))

# Adjusting column names to match, example:
names(second_aggregate) <- c("Utdanning", "År", "Etterspørsel") # Adjust based on actual desired alignment

# Ensure order of columns matches
second_aggregate <- second_aggregate[, names(first_aggregate)]

# Now, both aggregates should have matching structures. If not, adjust the column names or structures accordingly.
combined <- rbind(first_aggregate, second_aggregate)

# Then merge with Etterspørsel
TilbudEtterspørsel <- merge(combined, Etterspørsel, by = c("Utdanning", "År"), all = TRUE)
# Combine supply and demand (Equation 26 and 27)
#TilbudEtterspørsel <- rbind(
#  data.frame(Tilbud = aggregate(Etterspørsel ~ Utdanning + År, data = Sektorfordelt, FUN = sum)$Etterspørsel, År = paste0("X", as.character(Basisår))),
#  aggregate(Tilbud ~ Utdanning + År, data = Tilbud, FUN = sum, subset = År > paste0("X", as.character(Basisår)))
#) %>%
#  merge(Etterspørsel, by = c("Utdanning", "År"), all = TRUE)

# Calculate the difference (Equation 28)
names(TilbudEtterspørsel)[names(TilbudEtterspørsel) == "Etterspørsel.x"] <- "Tilbud"
names(TilbudEtterspørsel)[names(TilbudEtterspørsel) == "Etterspørsel.y"] <- "Etterspørsel"
# Assuming df is your dataframe and År is the column with values like X2020, X2021, etc.
TilbudEtterspørsel$År <- sub("X", "", TilbudEtterspørsel$År, fixed = TRUE)

TilbudEtterspørsel$Differanse <- with(TilbudEtterspørsel, Tilbud - Etterspørsel)
#print(TilbudEtterspørsel[c("Utdanning", "År", "Etterspørsel.x", "Etterspørsel.y", "Differanse")])
# Assuming TilbudEtterspørsel is your data frame
selected_columns <- TilbudEtterspørsel[c("Utdanning", "År", "Tilbud", "Etterspørsel", "Differanse")]

# Convert numeric columns to integers and avoid scientific notation
formatted_columns <- data.frame(lapply(selected_columns, function(x) {
  if(is.numeric(x)) {
    as.integer(format(x, scientific = FALSE))
  } else {
    x
  }
}))

#print(formatted_columns)

# Ensure necessary packages are installed and loaded
if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr")
library(dplyr)

# Assuming TilbudEtterspørsel is your dataframe
# Select the columns 'Tilbud', 'Etterspørsel', 'Differanse'
#formatted_columns <- formatted_columns %>% select(Utdanning, År, Tilbud, Etterspørsel, Differanse)

# Define the order for sorting
Rekkefølge <- c(ba = 1, gr = 2, lu = 3, ph = 4, pe = 5, yr = 6, py = 7)
#print(formatted_columns)
# Sort by 'Utdanning' and 'År' based on the defined order
# Assuming 'Utdanning' is a factor with levels not in the order of Rekkefølge
# Assuming Rekkefølge and formatted_columns are already defined

# Create a new column for the ordered factor based on 'Rekkefølge'
formatted_columns$UtdanningOrdered <- formatted_columns$Utdanning

# Replace the values in UtdanningOrdered with their corresponding order in 'Rekkefølge'
formatted_columns$UtdanningOrdered <- with(formatted_columns, names(Rekkefølge)[match(Utdanning, names(Rekkefølge))])

# Check for any NA values which indicate unmatched 'Utdanning' values
if (any(is.na(formatted_columns$UtdanningOrdered))) {
  stop("Some 'Utdanning' values do not match any key in 'Rekkefølge'. Please check your data and 'Rekkefølge' mapping.")
}

# Convert the ordered column into a factor with levels specified by 'Rekkefølge'
formatted_columns$UtdanningOrdered <- factor(formatted_columns$UtdanningOrdered, levels = names(Rekkefølge))

# Now you can arrange your data frame based on this new ordered factor and any other columns as needed
formatted_columns <- formatted_columns %>%
  arrange(UtdanningOrdered, År)

# Optionally, if you want to replace the original 'Utdanning' column with the ordered factor:
# formatted_columns$Utdanning <- formatted_columns$UtdanningOrdered
formatted_columns$UtdanningOrdered <- NULL  # Remove the temporary ordered column if not needed

# Rename the levels of 'Utdanning'
formatted_columns$Utdanning <- factor(formatted_columns$Utdanning, 
                                       levels = c("ba", "gr", "lu", "ph", "pe", "yr", "py"),
                                       labels = c("Barnehagelærere", "Grunnskolelærere", "Lektorutdannede", 
                                                  "PPU", "Praktiske og estetiske fag", "Yrkesfaglærere", "PPU Yrkesfag"))

# Write to CSV and Excel, print the table
#write_csv(round(formatted_columns, 0), 'resultater/Lærermod.csv')
#write_xlsx(round(formatted_columns, 0), 'resultater/Lærermod.xlsx')
#print(round(formatted_columns, 0))
#print(formatted_columns)

row_format <- "%-27s   %s  %s         %s      %s"

# Use apply() to iterate over rows, and sprintf() for formatting
cat(sprintf("Utdanning                      År Tilbud Ettterspørsel Differanse\n"))
invisible(apply(formatted_columns, 1, function(x) {
  cat(sprintf(row_format, x[["Utdanning"]], x[["År"]], x[["Tilbud"]], x[["Etterspørsel"]], x[["Differanse"]]), "\n")
}))


cat("\nLærermod er nå ferdig, velkommen tilbake.\n")
