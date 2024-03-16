# Laster inn nødvendige pakker
library(readr)
library(dplyr)
library(tidyr)
library(purrr)
library(tidyverse)
library(openxlsx)


# Setter alternativer for å forbedre visningen av dataframes i R
options(dplyr.width = Inf)

# Velkomstmelding
Velkomstmelding <- "
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
"
cat(Velkomstmelding)

# Start- og sluttår for framskrivningen
Basisår <- 2020
Sluttår <- 2040

# Innlesing av inputfiler
Aldersfordelt <- read.table("inndata/aldersfordelt.txt", header = TRUE, sep = "")
AldersfordeltStudenter <- read.table('inndata/aldersfordeltstudenter.txt', header = TRUE, sep = "")
Kandidatproduksjon <- read.table('inndata/kandidatproduksjon.txt', header = TRUE, sep = "")
Sektorfordelt <- read.table('inndata/sektorfordelt.txt', header = TRUE, sep = "")
Befolkning <- read.table('inndata/mmmm.txt', header = TRUE, sep = "")
DemografiGruppe1 <- read.table('inndata/antall_barn_barnehager.txt', header = TRUE, sep = "")
DemografiGruppe3 <- read.table('inndata/antall_elever_videregaende.txt', header = TRUE, sep = "")
DemografiGruppe4 <- read.table('inndata/antall_studenter_hoyereutdanning.txt', header = TRUE, sep = "")
Vakanse <- read.table('inndata/vakanse.txt', header = TRUE, sep = "")
Standardendring <- read.table('inndata/endring_standard.txt', header = TRUE, sep = "")
Timeverkendring <- read.table('inndata/endring_timeverk.txt', header = TRUE, sep = "")

#Aldersfordelt <- read.table("inndata/aldersfordelt.txt", header = TRUE, sep = "")
#AldersfordeltStudenter <- read_fwf('inndata/aldersfordeltstudenter.txt', col_positions = fwf_empty('inndata/aldersfordeltstudenter.txt', n=100))
#Kandidatproduksjon <- read_fwf('inndata/kandidatproduksjon.txt', col_positions = fwf_empty('inndata/kandidatproduksjon.txt', n=100))
#Sektorfordelt <- read_fwf('inndata/sektorfordelt.txt', col_positions = fwf_empty('inndata/sektorfordelt.txt', n=100))
#Befolkning <- read_fwf('inndata/mmmm.txt', col_positions = fwf_empty('inndata/mmmm.txt', n=100))
#DemografiGruppe1 <- read_fwf('inndata/antall_barn_barnehager.txt', col_positions = fwf_empty('inndata/antall_barn_barnehager.txt', n=100))
#DemografiGruppe3 <- read_fwf('inndata/antall_elever_videregaende.txt', col_positions = fwf_empty('inndata/antall_elever_videregaende.txt', n=100))
#DemografiGruppe4 <- read_fwf('inndata/antall_studenter_hoyereutdanning.txt', col_positions = fwf_empty('inndata/antall_studenter_hoyereutdanning.txt', n=100))
#Vakanse <- read_fwf('inndata/vakanse.txt', col_positions = fwf_empty('inndata/vakanse.txt', n=100))
#Standardendring <- read_fwf('inndata/endring_standard.txt', col_positions = fwf_empty('inndata/endring_standard.txt', n=100))
#Timeverkendring <- read_fwf('inndata/endring_timeverk.txt', col_positions = fwf_empty('inndata/endring_timeverk.txt', n=100))

# Oppretter radetiketter på eksisterende kolonner
Aldersfordelt <- Aldersfordelt %>% mutate(Utdanning = factor(Utdanning))
AldersfordeltStudenter <- AldersfordeltStudenter %>% mutate(Utdanning = factor(Utdanning))
Kandidatproduksjon <- Kandidatproduksjon %>% mutate(Utdanning = factor(Utdanning))
Sektorfordelt <- Sektorfordelt %>% mutate(Utdanning = factor(Utdanning), Sektor = factor(Sektor))
#Befolkning <- Befolkning %>% mutate(Alder = factor(Alder), Kjønn = factor(Kjønn))

# Oppretter en konstant med forkortelsene for de utdanningene som er inkludert i modellen
Utdanninger <- c('ba', 'gr', 'lu', 'ph', 'pe', 'yr', 'py')

# Oppretter lister (tilsvarende dictionaries i Python) for senere utfylling
BefolkningSektor <- list()
Brukergruppe <- list()
DemografiSektor <- list()
DemografiGruppe <- list()
SumDemografiGruppe <- list()
RelativeBrukere <- list()


# Beregner sysselsettingsandel
# Dette tilsvarer Likning 1 i modellen
Aldersfordelt$Sysselsettingsandel <- with(Aldersfordelt, ifelse(Antall > 0, Sysselsatte / Antall, 0))

# Kopierer dette inn i en tabell og fjerner kolonner som nå er overflødige
Populasjon <- Aldersfordelt
Aldersfordelt <- select(Aldersfordelt, -Antall, -Sysselsatte)

# Finner årsverkene i populasjonen
# Dette tilsvarer Likning 2 i modellen
Populasjon$Årsverk <- with(Populasjon, Sysselsatte * GjennomsnitteligeÅrsverk)

# Angir at dette er populasjonen i basisåret og fjerner kolonner som nå er overflødige
Populasjon$År <- Basisår
Populasjon <- select(Populasjon, -Sysselsatte, -Sysselsettingsandel, -GjennomsnitteligeÅrsverk)

# Framskriving av utgangspopulasjonen. År 2 til sluttår. Basert på statistikk fra basisåret.

# Kandidatproduksjonen:
# Beregner først totalt antall førsteårsstudenter for hver av utdanningene.
# Dette tilsvarer Likning 3 i modellen.
AntallFørsteårsStudenter <- AldersfordeltStudenter %>%
  group_by(Utdanning) %>%
  summarise(Totalt = sum(Alle))

# Kopierer inn totalt antall studenter for den aktuelle utdanningen i en ny kolonne
AldersfordeltStudenter <- AldersfordeltStudenter %>%
  inner_join(AntallFørsteårsStudenter, by = "Utdanning")

# Legger til en variabel for kjønn og dupliserer radene for å ha en rad per kjønn
AldersfordeltStudenter$Kjønn <- 1 # Assuming 1 is one category
duplicate <- AldersfordeltStudenter
duplicate$Kjønn <- 2 # Assuming 2 is another category

# Combine the original and the duplicate
NyeStudenter <- rbind(AldersfordeltStudenter, duplicate)

#NyeStudenter <- AldersfordeltStudenter %>%
#  expand_grid(Kjønn = c(1, 2)) %>%
#  left_join(AldersfordeltStudenter, by = c("Utdanning", "Alder")) %>%
#  select(-Totalt.y) %>%
#  rename(Totalt = Totalt.x)

# Beregner andel studenter for hver alder og hvert kjønn
NyeStudenter <- NyeStudenter %>%
  mutate(AndelStudenterEtterAlder = case_when(
    Kjønn == 1 ~ Menn / Totalt,
    Kjønn == 2 ~ Kvinner / Totalt,
    TRUE ~ NA_real_
  ))

# Oppretter en data frame for hvert år i framskrivningsperioden for hver utdanning
år_frame <- expand_grid(År = Basisår:Sluttår, Utdanning = Utdanninger) 

# Slår sammen denne med Kandidatproduksjon basert på utdanning
Kandidatproduksjon <- Kandidatproduksjon %>%
  inner_join(år_frame, by = "Utdanning")

# Beregner antall årlige kandidater
Kandidatproduksjon <- Kandidatproduksjon %>%
  mutate(Kandidater = AntallNyeStudenter * Fullføringsprosent / 100)

# Inner join mellom NyeStudenter og Kandidatproduksjon basert på Utdanning
Kandidater <- NyeStudenter %>%
  inner_join(Kandidatproduksjon, by = "Utdanning", relationship = "many-to-many")

# Beregner alder for uteksaminering og antall uteksaminerte etter kjønn
Kandidater <- Kandidater %>%
  mutate(
    Alder = Alder + Studielengde, # Oppdaterer alder for uteksaminering
    UteksaminerteEtterAlder = Kandidater * AndelStudenterEtterAlder # Beregner uteksaminerte
  )

# Kopierer populasjonen i basisåret til nye tabeller for beregningene
Populasjon <- Populasjon  # I R er dette egentlig overflødig, men viser til hensikten
PopulasjonAktueltÅr <- Populasjon  # Oppretter en kopi for bruk i beregningene

# Forbereder en tom dataframe for å lagre resultatene for alle årene
#KumulativPopulasjon <- data.frame()

for (t in (Basisår + 1):Sluttår) {
  
  # Increment age for the population for each year.
  # This corresponds to Equation 8 in the model.
  PopulasjonAktueltÅr$Alder <- PopulasjonAktueltÅr$Alder + 1
  
  # Add candidates by age and gender found in Equations 6 and 7 to the table.
  PopulasjonAktueltÅr <- full_join(PopulasjonAktueltÅr, 
                                   Kandidater[Kandidater$År == t, ], 
                                   by = c("Utdanning", "Kjønn", "Alder"))
  
  # Graduates by age and gender found in Equation 7 are added to the population.
  # This is Equation 9 in the model.
  PopulasjonAktueltÅr$Antall <- ifelse(is.na(PopulasjonAktueltÅr$Antall), 0, PopulasjonAktueltÅr$Antall) +
                                ifelse(is.na(PopulasjonAktueltÅr$UteksaminerteEtterAlder), 0, PopulasjonAktueltÅr$UteksaminerteEtterAlder)
  
  # Set this as the population for the projection year.
  PopulasjonAktueltÅr$År <- t
  
  # The population for the projection year is added to the population as a new cohort.
  Kolonner <- c("Utdanning", "Kjønn", "Alder", "Antall", "Årsverk", "År")
  Populasjon <- bind_rows(Populasjon, PopulasjonAktueltÅr[Kolonner])
  
  # Copy the population for the projection year to the table for the next projection year.
  PopulasjonAktueltÅr <- Populasjon[Populasjon$År == t, ]
  
}

# Oppdaterer Populasjon dataframe med den kumulative populasjonen
#Populasjon <- KumulativPopulasjon

# Slår sammen Populasjon med Aldersfordelt for å hente inn Sysselsettingsandel og GjennomsnitteligeÅrsverk
Tilbud <- left_join(Populasjon, Aldersfordelt, by = c("Utdanning", "Kjønn", "Alder"))

# Beregner tilbudet
Tilbud <- Tilbud %>%
  mutate(Tilbud = Antall * Sysselsettingsandel * GjennomsnitteligeÅrsverk)





# Beregner etterspørselen i basisåret basert på antall sysselsatte menn og kvinner
# og deres gjennomsnittlige årsverk
Sektorfordelt <- Sektorfordelt %>%
  mutate(Etterspørsel = (SysselsatteMenn * GjennomsnitteligeÅrsverkMenn) +
                          (SysselsatteKvinner * GjennomsnitteligeÅrsverkKvinner),
         År = Basisår)

# Oppretter en tom tabell for etterspørselen der hver av de 7 utdanningene inngår
Etterspørsel <- data.frame(Utdanning = Utdanninger, Etterspørsel = 0)

# For hver av de 7 utdanningene og hver av de 6 sektorene, kopier verdiene som ble funnet i likning 11
for (S in 1:6) {
  Etterspørsel[[paste0('EtterspørselSektor', S)]] <- Sektorfordelt[Sektorfordelt$Sektor == S, ]
}

#for (S in 1:6) {
#  SektorSpesifikkEtterspørsel <- filter(Sektorfordelt, Sektor == S) %>%
#    select(Etterspørsel) %>%
#    mutate(Row = row_number()) %>%
#    pivot_wider(names_from = Sektor, values_from = Etterspørsel,
#                names_prefix = "EtterspørselSektor")
  
#  Etterspørsel <- left_join(Etterspørsel, SektorSpesifikkEtterspørsel, by = "Row") %>%
#    select(-Row)
#}

# Rens opp kolonner om nødvendig, avhengig av nøyaktig struktur ønsket

# Neste trinn ville være å håndtere befolkningsframskrivinger og beregne dekningsgrader
# og tettheter for framskrivningsår, basert på SSBs nasjonale befolkningsframskrivinger.

# Oppretter de tomme tabellene for brukergruppene
Brukergruppe <- list()

Brukergruppe[[1]] <- data.frame(TilAlder = c(0, 2, 2, 3, 5, 5), Alder = 0:5)
Brukergruppe[[2]] <- data.frame(TilAlder = rep(15, 10), Alder = 6:15)
Brukergruppe[[3]] <- data.frame(TilAlder = c(rep(15, 16), 16:24, rep(49, 25)), Alder = 0:49)
Brukergruppe[[4]] <- data.frame(TilAlder = c(19:29, rep(34, 5), rep(39, 5), rep(44, 5), rep(49, 5)), Alder = 19:49)
Brukergruppe[[5]] <- data.frame(TilAlder = rep(99, 100), Alder = 0:99)
Brukergruppe[[6]] <- data.frame(TilAlder = rep(99, 100), Alder = 0:99)

# Kalkulerer antall brukere og deres gjennomsnittlige timer
BarnGruppe1 <- data.frame(Brukere = DemografiGruppe1$Alder0,
                          Timer = DemografiGruppe1$TimerMin + 
                                  (DemografiGruppe1$TimerMax - DemografiGruppe1$TimerMin) / 2)
BarnGruppe2 <- data.frame(Brukere = DemografiGruppe1$Alder1 + DemografiGruppe1$Alder2,
                          Timer = DemografiGruppe1$TimerMin + 
                                  (DemografiGruppe1$TimerMax - DemografiGruppe1$TimerMin) / 2)
BarnGruppe3 <- data.frame(Brukere = DemografiGruppe1$Alder3,
                          Timer = DemografiGruppe1$TimerMin + 
                                  (DemografiGruppe1$TimerMax - DemografiGruppe1$TimerMin) / 2)
BarnGruppe4 <- data.frame(Brukere = DemografiGruppe1$Alder4 + DemografiGruppe1$Alder5,
                          Timer = DemografiGruppe1$TimerMin + 
                                  (DemografiGruppe1$TimerMax - DemografiGruppe1$TimerMin) / 2)

# Oppretter en tom tabell for å fylles med antall brukere i barnehagesektoren
DemografiGruppe <- list()
DemografiGruppe[[1]] <- data.frame(FraAlder=integer(), TilAlder=integer(), 
                                   Brukere=numeric(), Brukerindeks=numeric())

# Beregner brukere av barnehage i hver av de 4 brukergruppene

# Gruppe 1
DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder=0, TilAlder=0, 
                                        Brukere=sum(BarnGruppe1$Brukere), 
                                        Brukerindeks=(2 * sum(BarnGruppe1$Brukere * BarnGruppe1$Timer)) / 
                                                      (sum(BarnGruppe1$Brukere) * 42.5)))

# Gruppe 2
DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder=1, TilAlder=2, 
                                        Brukere=sum(BarnGruppe2$Brukere), 
                                        Brukerindeks=(2 * sum(BarnGruppe2$Brukere * BarnGruppe2$Timer)) / 
                                                      (sum(BarnGruppe2$Brukere) * 42.5)))

# Gruppe 3
DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder=3, TilAlder=3, 
                                        Brukere=sum(BarnGruppe3$Brukere), 
                                        Brukerindeks=(1.5 * sum(BarnGruppe3$Brukere * BarnGruppe3$Timer)) / 
                                                      (sum(BarnGruppe3$Brukere) * 42.5)))

# Gruppe 4
DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder=4, TilAlder=5, 
                                        Brukere=sum(BarnGruppe4$Brukere), 
                                        Brukerindeks=(1 * sum(BarnGruppe4$Brukere * BarnGruppe4$Timer)) / 
                                                      (sum(BarnGruppe4$Brukere) * 42.5)))

# Beregner elever i grunnskolen
DemografiGruppe[[2]] <- data.frame(FraAlder = 6,
                                   TilAlder = 15,
                                   Brukere = sum(Befolkning[Befolkning$Alder >= 6 & Befolkning$Alder <= 15, paste0("X", as.character(Basisår))]),
                                   Brukerindeks = 1.0)

# Kopierer brukerne i Sektor 3 og 4 som ble lest inn tidligere
DemografiGruppe[[3]] <- DemografiGruppe3
DemografiGruppe[[4]] <- DemografiGruppe4

# Beregner brukere av annet i sektoren (voksenopplæring, fagskoler etc.)
DemografiGruppe[[5]] <- data.frame(FraAlder = 0,
                                   TilAlder = 99,
                                   Brukere = sum(Befolkning[Befolkning$Alder >= 0 & Befolkning$Alder <= 99, paste0("X", as.character(Basisår))]),
                                   Brukerindeks = 1.0)

# Beregner brukere utenfor sektoren
DemografiGruppe[[6]] <- data.frame(FraAlder = 0,
                                   TilAlder = 99,
                                   Brukere = sum(Befolkning[Befolkning$Alder >= 0 & Befolkning$Alder <= 99, paste0("X", as.character(Basisår))]),
                                   Brukerindeks = 1.0)


# Initiere lister for å holde dataframer
BefolkningSektor <- list()
RelativeBrukere <- list()
SumDemografiGruppe <- list()
DemografiSektor <- list()


for (S in 1:6) {
  # Oppretter en tom tabell for befolkningen i aktuell sektor
  BefolkningSektor[[S]] <- data.frame()
  
  # Finner folkemengden fra befolkningsframskrivningene for brukergruppene
  BefolkningSektor[[S]] <- merge(Brukergruppe[[S]], Befolkning, by = "Alder") %>%
    group_by(TilAlder) %>%
    summarise_all(sum)
  
  # Beregner antall relative brukere i basisåret
  DemografiGruppe[[S]]$RelativeBrukereX2020 <- DemografiGruppe[[S]]$Brukere * DemografiGruppe[[S]]$Brukerindeks
  
  # Beregner antall relative brukere i hvert framskrivningsår
  for (t in (Basisår + 1):Sluttår) {
    DemografiGruppe[[S]][paste0("RelativeBrukereX", t)] <- DemografiGruppe[[S]][paste0("RelativeBrukereX", t - 1)] * 
      (BefolkningSektor[[S]][paste0("X", t)] / BefolkningSektor[[S]][paste0("X", t - 1)])
  }
  
  # Beregner summen av brukerne i hvert framskrivningsår
  SumDemografiGruppe[[S]] <- data.frame(t(sapply((Basisår:Sluttår), function(t) {
    sum(DemografiGruppe[[S]][paste0("RelativeBrukereX", t)])
  })))
  
  # Beregner den demografiske utviklingen for hvert framskrivningsår for hver brukergruppe
  DemografiSektor[[S]] <- data.frame(År = Basisår:Sluttår, DemografiKomponent = NA)
  DemografiSektor[[S]]$DemografiKomponent <- SumDemografiGruppe[[S]] / SumDemografiGruppe[[S]][1, 1]
}

# Omstrukturering av data kan være nødvendig avhengig av spesifikke krav


# Anta at DemografiSektor er en liste av dataframes for hver sektor
# og Standardendring er en dataframe som allerede eksisterer

# Kopierer tabellene med den demografiske utviklingen i hver sektor sammen
DemografiIndeks <- Standardendring
for (Sektor in 1:6) {
  DemografiIndeks <- merge(DemografiIndeks, DemografiSektor[[Sektor]], by = "År", all = TRUE)
}

# Utvider tabellen for å inkludere de 7 utdanningene
DemografiIndeks <- expand.grid(Utdanning = Utdanninger, DemografiIndeks)
names(DemografiIndeks)[1] <- "År"

# Anta at Etterspørsel og Vakanse er dataframes som allerede eksisterer
# Slår sammen DemografiIndeks, Etterspørsel og Vakanse basert på 'Utdanning' og 'År'
Etterspørsel <- reduce(list(DemografiIndeks, Etterspørsel, Vakanse), full_join, by = c("Utdanning", "År"))

# Beregner etterspørselen
for (S in 1:6) {
  Etterspørsel$Etterspørsel <- Etterspørsel$Etterspørsel +
    (Etterspørsel[[paste0("EtterspørselSektor", S)]] + Etterspørsel[[paste0("VakanseSektor", S)]]) *
    Etterspørsel[[paste0("DemografiKomponent", S)]] * Etterspørsel[[paste0("StandardEndring", S)]]
}

# Setter 'Utdanning' og 'År' som indeks hvis ønskelig
Etterspørsel <- Etterspørsel %>%
  arrange(Utdanning, År) %>%
  group_by(Utdanning, År) %>%
  summarise_all(sum, na.rm = TRUE) %>%
  as.data.frame()

# Etterspørsel beregning kan justeres basert på spesifikke detaljer i likningene 24 og 25

# Anta at Sektorfordelt, Tilbud, og Etterspørsel er data frames som allerede eksisterer og er forberedt

# Setter sammen tilbud og etterspørsel
TilbudEtterspørsel <- bind_rows(
  data.frame(Tilbud = Sektorfordelt$Etterspørsel, År = Basisår) %>% group_by(Utdanning, År) %>% summarise_all(sum),
  Tilbud %>% group_by(Utdanning, År) %>% summarise_all(sum) %>% filter(År > Basisår)
) %>% full_join(Etterspørsel, by = c("Utdanning", "År"))

# Beregner differansen
TilbudEtterspørsel <- TilbudEtterspørsel %>%
  mutate(Differanse = Tilbud - Etterspørsel)

# Sorterer etter utdanning og år
Rekkefølge <- c('ba' = 1, 'gr' = 2, 'lu' = 3, 'ph' = 4, 'pe' = 5, 'yr' = 6, 'py' = 7)
TilbudEtterspørsel$Utdanning <- factor(TilbudEtterspørsel$Utdanning, levels = names(Rekkefølge))
TilbudEtterspørsel <- TilbudEtterspørsel %>% arrange(Utdanning, År)

# Omdøper indeksene
UtdanningNavn <- c('ba' = 'Barnehagelærere', 'gr' = 'Grunnskolelærere', 'lu' = 'Lektorutdannede',
                   'ph' = 'PPU', 'pe' = 'Praktiske og estetiske fag', 'yr' = 'Yrkesfaglærere', 
                   'py' = 'PPU Yrkesfag')
TilbudEtterspørsel$Utdanning <- UtdanningNavn[TilbudEtterspørsel$Utdanning]

# Runder av og konverterer til heltall
TilbudEtterspørsel <- round(TilbudEtterspørsel)
TilbudEtterspørsel[is.na(TilbudEtterspørsel)] <- 0 # Erstatter NA med 0 om nødvendig
TilbudEtterspørsel <- transform(TilbudEtterspørsel, Tilbud = as.integer(Tilbud), Etterspørsel = as.integer(Etterspørsel), Differanse = as.integer(Differanse))

# Lagrer resultatene
write.csv(TilbudEtterspørsel, "resultater/Lærermod.csv", row.names = FALSE)
write.xlsx(TilbudEtterspørsel, "resultater/Lærermod.xlsx")

# Skriver ut resultatene og en avskjedshilsen
print(TilbudEtterspørsel)

cat("\nLærermod er nå ferdig, velkommen tilbake.\n")







