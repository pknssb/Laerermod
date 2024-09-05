# ******************************************************************************************** #
# Import av R-biblioteker samt utskrift av en hyggelig velkomstmelding.                        #
# ******************************************************************************************** #

library(readr)
library(dplyr)
library(tidyr)
library(purrr)
library(tidyverse)
library(openxlsx)
library(writexl)

options(dplyr.summarise.inform = FALSE)

cat("
Velkommen til R-versjonen av Lærermod!

+---------------------------------------------------------------+
|    Modellen LÆRERMOD beregner tilbud og                       |
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
# Start- og sluttår for framskrivningen.                                                       #
# ******************************************************************************************** #

Basisår <- 2020
Sluttår <- 2040

# ******************************************************************************************** #
# Innlesing av inputfiler. Se Appendix 1 for kildedata.                                        #
# ******************************************************************************************** #

Aldersfordelt <- read.table("inndata/aldersfordelt.txt", header = TRUE)

AldersfordeltStudenter <- read.table('inndata/aldersfordeltstudenter.txt', header = TRUE)
Kandidatproduksjon <- read.table('inndata/kandidatproduksjon.txt', header = TRUE)

Sektorfordelt <- read.table('inndata/sektorfordelt.txt', header = TRUE)

Befolkning <- read.table('inndata/mmmm.txt', header = TRUE)

DemografiGruppe1 <- read.table('inndata/antall_barn_barnehager.txt', header = TRUE)
DemografiGruppe3 <- read.table('inndata/antall_elever_videregaende.txt', header = TRUE)
DemografiGruppe4 <- read.table('inndata/antall_studenter_hoyereutdanning.txt', header = TRUE)

Laerermangel <- read.table('inndata/laerermangel.txt', header = TRUE)

Standardendring <- read.table('inndata/endring_standard_kort.txt', header = TRUE)
Standardendring$År <- paste0("X", as.character(Standardendring$År))


# ******************************************************************************************** #
# Oppretter radetiketter på eksisterende kolonner slik at de senere kan benyttes til kopling.  #
# ******************************************************************************************** #

Aldersfordelt <- Aldersfordelt %>% mutate(Utdanning = factor(Utdanning))
AldersfordeltStudenter <- AldersfordeltStudenter %>% mutate(Utdanning = factor(Utdanning))
Kandidatproduksjon <- Kandidatproduksjon %>% mutate(Utdanning = factor(Utdanning))
Sektorfordelt <- Sektorfordelt %>% mutate(Utdanning = factor(Utdanning),Sektor = factor(Sektor))
Befolkning <- Befolkning %>% mutate(Alder = factor(Alder), Kjønn = factor(Kjønn))

# ******************************************************************************************** #
# Oppretter en konstant med forkortelsene for de utdanningene som er inkludert i modellen.     #
# ******************************************************************************************** #

Utdanninger <- c('ba', 'gr', 'lu', 'ph', 'pe', 'yr', 'py')

# ******************************************************************************************** #
# Oppretter lister for senere utfylling.                                                       #
# ******************************************************************************************** #

BefolkningSektor <- list()
Brukergruppe <- list()
DemografiSektor <- list()
DemografiGruppe <- list()
SumDemografiGruppe <- list()
Brukere <- list()

# ******************************************************************************************** #
# Tilbud.                                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Utgangspopulasjon av lærere.                                                                 #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Beregner sysselsattingsandel.                                                                #
# Dette er Likning 1 i modellen.                                                               #
# ******************************************************************************************** #

Aldersfordelt$Sysselsettingsandel <- ifelse(Aldersfordelt$Antall > 0, 
                                            Aldersfordelt$Sysselsatte / Aldersfordelt$Antall, 
                                            0)

# ******************************************************************************************** #
# Kopierer dette inn i en tabell og fjerner kolonner som nå er overflødige.                    #
# ******************************************************************************************** #

Populasjon <- Aldersfordelt
Aldersfordelt <- Aldersfordelt %>% select(-Antall, -Sysselsatte)

# ******************************************************************************************** #
# Finner gjennomsnittlige årsverk.                                                             #
# Dette er Likning 2 i modellen.                                                               #
# ******************************************************************************************** #

Populasjon$GjennomsnitteligeÅrsverk = Populasjon$Årsverk / Populasjon$Sysselsatte

# ******************************************************************************************** #
# Angir at dette er populasjonen i basisåret og fjerner kolonner som nå er overflødige.        #
# ******************************************************************************************** #

Populasjon$År <- Basisår
Populasjon <- Populasjon %>% select(-Sysselsatte, -Sysselsettingsandel,
                                    -GjennomsnitteligeÅrsverk)

# ******************************************************************************************** #
# Framskriving av utgangspopulasjonen. År 2 til sluttår. Basert på statistikk fra basisåret.   #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Kandidatproduksjonen:                                                                        #
# Beregner først totalt antall førsteårsstudenter for hver av utdanningene.                    #
# Dette er Likning 3 i modellen.                                                               #
# ******************************************************************************************** #

AntallFørsteårsStudenter <- AldersfordeltStudenter %>% 
  group_by(Utdanning) %>% 
  summarise(Totalt = sum(Alle)) %>% 
  ungroup()

# ******************************************************************************************** #
# Kopierer inn totalt antall studenter for den aktuelle utdanning i en ny kolonne i            #
# tabellen AldersfordeltStudenter. Legger til en variabel for kjønn.                           #
# ******************************************************************************************** #

AldersfordeltStudenter <- AldersfordeltStudenter %>%
  inner_join(AntallFørsteårsStudenter, by = "Utdanning")

NyeStudenter <- AldersfordeltStudenter %>%
  mutate(Kjønn = 1) %>%
  bind_rows(AldersfordeltStudenter %>% mutate(Kjønn = 2))

# ******************************************************************************************** #
# Beregner andel studenter for hver alder og hvert kjønn.                                      #
# Dette er Likning 4 i modellen.                                                               #
# ******************************************************************************************** #

NyeStudenter <- NyeStudenter %>%
  mutate(AndelStudenterEtterAlder = if_else(Kjønn == 1, 
                                            Menn / Totalt, 
                                            Kvinner / Totalt))

# ******************************************************************************************** #
# Angir at antall studenter er konstant i hvert framskrivningsår.                              #
# ******************************************************************************************** #

Years <- data.frame(År = Basisår:Sluttår)
UtdanningYears <- expand.grid(Utdanning = Utdanninger, År = Years$År)

Kandidatproduksjon <- Kandidatproduksjon %>% inner_join(UtdanningYears, by = "Utdanning")

# ******************************************************************************************** #
# Beregner antall årlige kandidater ved hjelp av nye studenter og fullføringsprosenter.        #
# Dette er Likning 5 i modellen.                                                               #
# ******************************************************************************************** #

Kandidatproduksjon <- Kandidatproduksjon %>%
  mutate(Kandidater = AntallNyeStudenter * Fullføringsprosent)

# ******************************************************************************************** #
# Angir at antall kandidater skal være konstant i framskrivingsperioden.                       #
# ******************************************************************************************** #

Kandidater <- inner_join(NyeStudenter, Kandidatproduksjon,
                         by = "Utdanning", relationship = "many-to-many")

# ******************************************************************************************** #
# Beregner alder for uteksaminering og antall uteksaminerte etter kjønn. Passer på at alder    #
# for uteksaminering heter det samme som i den tabellen radene skal leggges til i senere,      #
# Alder, selv om navnet er litt misvisende i denne sammenheng.                                 #
# Dette er Likning 6 og Likning 7 i modellen.                                                  #
# ******************************************************************************************** #

Kandidater <- Kandidater %>%
  mutate(Alder = Alder + Studielengde,
         UteksaminerteEtterAlder = Kandidater * AndelStudenterEtterAlder)

# ******************************************************************************************** #
# Kopierer populasjonen i basisåret, beregnet i likning 2, inn i to nye tabeller som blir      #
# utgangspunktet for beregningene.                                                             #
# ******************************************************************************************** #

PopulasjonAktueltÅr <- Populasjon

# ******************************************************************************************** #
# For hvert framskrivningsår skal populasjonen bli ett år eldre og nye kandidater legges til.  #
# ******************************************************************************************** #

for (t in (Basisår + 1):Sluttår) {
  
    # **************************************************************************************** #
    # Pensjonering (for utgangspopulasjonen og kandidater).                                    #
    # **************************************************************************************** #

    # **************************************************************************************** #
    # For hvert år inkrementeres alderen i populasjonen.                                       #
    # Dette er Likning 8 i modellen.                                                           #
    # **************************************************************************************** #

    PopulasjonAktueltÅr$Alder <- PopulasjonAktueltÅr$Alder + 1
  
    # **************************************************************************************** #
    # Kandidater etter alder og kjønn som ble funnet i likning 6 og 7 legges til i tabellen.   #
    # **************************************************************************************** #

    PopulasjonAktueltÅr <- merge(x = PopulasjonAktueltÅr, 
                                 y = Kandidater[Kandidater$År == t, ], 
                                 by = c("Utdanning", "Kjønn", "Alder"), 
                                 all = TRUE)
  
    # **************************************************************************************** #
    # Uteksaminerte etter alder og kjønn funnet i Likning 7 legges til populasjonen.           #
    # Dette er Likning 9 i modellen.                                                           #
    # **************************************************************************************** #

    PopulasjonAktueltÅr$Antall <- ifelse(is.na(PopulasjonAktueltÅr$Antall), 0, 
                                         PopulasjonAktueltÅr$Antall) + 
                                  ifelse(is.na(PopulasjonAktueltÅr$UteksaminerteEtterAlder), 0,
                                         PopulasjonAktueltÅr$UteksaminerteEtterAlder)
  
    # **************************************************************************************** #
    # Angir at dette skal være populasjonen i framskrivningsåret.                              #
    # **************************************************************************************** #

    PopulasjonAktueltÅr$År <- t
  
    # **************************************************************************************** #
    # Populasjonen i framskrivningsåret legges til populasjonen som en ny årgang.              #
    # **************************************************************************************** #

    Populasjon <- rbind(Populasjon, PopulasjonAktueltÅr[, c("Utdanning", "Kjønn", "Alder",
                                                            "Antall", "År")])
  
    # **************************************************************************************** #
    # Kopierer populasjonen i framskrivningsåret til tabellen for neste framskrivningsår.      #
    # **************************************************************************************** #

    PopulasjonAktueltÅr <- Populasjon[Populasjon$År == t, ]
}

# ******************************************************************************************** # 
# Henter inn Sysselsettingsandel og Gjennomsnittelige årsverk som ble beregnet for             #
# utgangspopulasjonen i Likning 6 og 7. Angir at dette skal bli tabellen for tilbudet.         #
# ******************************************************************************************** #

Tilbud <- merge(x = Populasjon, 
                y = Aldersfordelt, 
                by = c("Utdanning", "Kjønn", "Alder"), 
                all.x = TRUE)

# ******************************************************************************************** #
# Beregner tilbudet.                                                                           #
# Dette er Likning 10 i modellen.                                                              #
# ******************************************************************************************** #

Tilbud$Tilbud <- Tilbud$Antall * Tilbud$Sysselsettingsandel * Tilbud$GjennomsnitteligeÅrsverk

# ******************************************************************************************** #
# Etterspørsel.                                                                                #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Utgangspopulasjonen av lærere.                                                               #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Beregner sysselsatte i basisåret, dvs. tilbudet. Etterspørselen i basisåret blir satt lik    #
# dette.                                                                                       #
# Dette er Likning 11 i modellen.                                                              #
# ******************************************************************************************** #

Sektorfordelt$Etterspørsel <- (Sektorfordelt$SysselsatteMenn *
                               Sektorfordelt$GjennomsnitteligeÅrsverkMenn) + 
                              (Sektorfordelt$SysselsatteKvinner *
                               Sektorfordelt$GjennomsnitteligeÅrsverkKvinner)
Sektorfordelt$År <- Basisår

# ******************************************************************************************** #
# Oppretter en tom tabell for etterspørselen der hver av de 7 utdanningene inngår.             #
# ******************************************************************************************** #

Etterspørsel <- data.frame(Utdanning = Utdanninger, Etterspørsel = rep(0, length(Utdanninger)))

# ******************************************************************************************** #
# For hver av de 7 utdanningene og hver av de 6 sektorene kopieres verdiene som ble funnet     #
# i likning 11 inn i tabellen med etterspørselen. Dette transponerer tabellen.                 #
# ******************************************************************************************** #

for (S in 1:6) {
  Etterspørsel[paste0('EtterspørselSektor', S)] <- Sektorfordelt$Etterspørsel[Sektorfordelt$
                                                                              Sektor == S]
}

# ******************************************************************************************** #
# Framskrivingsår. Finner antall brukere i basisåret for å beregne dekningsgrader og           #
# tettheter. Veksten framover i antall brukere basert på SSBs nasjonale                        #
# befolkningsframskrivinger.                                                                   #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Oppretter 6 tomme tabeller som skal fylles med antall brukere i hver sektor.                 #
# ******************************************************************************************** #

Brukergruppe[[1]] <- data.frame(TilAlder = c(0, 2, 2, 3, 5, 5),
                                Alder = 0:5)

Brukergruppe[[2]] <- data.frame(TilAlder = rep(15, 10),
                                Alder = 6:15)

Brukergruppe[[3]] <- data.frame(TilAlder = c(rep(15, 16), 16:24, rep(49, 25)),
                                Alder = 0:49)

Brukergruppe[[4]] <- data.frame(TilAlder = c(19:29, rep(34, 5), rep(39, 5), rep(44, 5),
                                             rep(49, 5)),
                                Alder = 19:49)

Brukergruppe[[5]] <- data.frame(TilAlder = rep(99, 100),
                                Alder = 0:99)

Brukergruppe[[6]] <- data.frame(TilAlder = rep(99, 100),
                                Alder = 0:99)

# ******************************************************************************************** #
# Summerer antall barn i barnehager i hver brukergruppe etter gjennomsnittelig oppholdstid.    #
# Dette er Likning 12 og Likning 13 i modellen.                                                #
# ******************************************************************************************** #

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

# ******************************************************************************************** #
# Oppretter en tom tabell som skal fylles med antall brukere i barnehagesektoren.              #
# ******************************************************************************************** #

DemografiGruppe[[1]] <- data.frame(FraAlder = integer(), TilAlder = integer(), 
                                   Brukere = integer(), Brukerindeks = numeric())

# ******************************************************************************************** #
# Beregner brukere av barnehage i hver av de 4 brukergruppene.                                 #
# Dette er Likning 14 og Likning 15 i modellen.                                                #
# ******************************************************************************************** #

DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder = 0, TilAlder = 0, 
                                        Brukere = sum(BarnGruppe1$Brukere), 
                                        Brukerindeks = (2 * sum(BarnGruppe1$Brukere *
                                                                BarnGruppe1$Timer)) / 
                                                       (sum(BarnGruppe1$Brukere) * 42.5)))

DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder = 1, TilAlder = 2, 
                                        Brukere = sum(BarnGruppe2$Brukere), 
                                        Brukerindeks = (2 * sum(BarnGruppe2$Brukere *
                                                                BarnGruppe2$Timer)) / 
                                                       (sum(BarnGruppe2$Brukere) * 42.5)))

DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder = 3, TilAlder = 3, 
                                        Brukere = sum(BarnGruppe3$Brukere), 
                                        Brukerindeks = (1.5 * sum(BarnGruppe3$Brukere *
                                                                  BarnGruppe3$Timer)) / 
                                                       (sum(BarnGruppe3$Brukere) * 42.5)))

DemografiGruppe[[1]] <- rbind(DemografiGruppe[[1]], 
                             data.frame(FraAlder = 4, TilAlder = 5, 
                                        Brukere = sum(BarnGruppe4$Brukere), 
                                        Brukerindeks = (1 * sum(BarnGruppe4$Brukere *
                                                                BarnGruppe4$Timer)) / 
                                                       (sum(BarnGruppe4$Brukere) * 42.5)))

# ******************************************************************************************** #
# Oppdaterer tallene for antall brukere av barnehage i hver av de 4 brukergruppene når det tas #
# hensyn til brukerindeksene.                                                                  #
# Dette er Likning 16 i modellen.                                                              #
# ******************************************************************************************** #

DemografiGruppe[[1]][1, ] <- c(0, 0, DemografiGruppe[[1]]$Brukere[1] *
                                     DemografiGruppe[[1]]$Brukerindeks[1],
                               DemografiGruppe[[1]]$Brukerindeks[1])
DemografiGruppe[[1]][2, ] <- c(1, 2, DemografiGruppe[[1]]$Brukere[2] *
                                     DemografiGruppe[[1]]$Brukerindeks[2],
                               DemografiGruppe[[1]]$Brukerindeks[2])
DemografiGruppe[[1]][3, ] <- c(3, 3, DemografiGruppe[[1]]$Brukere[3] *
                                     DemografiGruppe[[1]]$Brukerindeks[3],
                               DemografiGruppe[[1]]$Brukerindeks[3])
DemografiGruppe[[1]][4, ] <- c(4, 5, DemografiGruppe[[1]]$Brukere[4] *
                                     DemografiGruppe[[1]]$Brukerindeks[4],
                               DemografiGruppe[[1]]$Brukerindeks[4])

# ******************************************************************************************** #
# Passer på at kolonnen med Alder er numerisk.                                                 #
# ******************************************************************************************** #

Befolkning$Alder <- as.numeric(as.character(Befolkning$Alder))

# ******************************************************************************************** #
# Beregner elever i grunnskolen.                                                               #
# Dette er Likning 17 i modellen.                                                              #
# ******************************************************************************************** #

DemografiGruppe[[2]] <- data.frame(FraAlder = 6,
                                   TilAlder = 15,
                                   Brukere = sum(Befolkning[Befolkning$Alder >= 6 &
                                                            Befolkning$Alder <= 15, 
                                                           paste0("X",
                                                                  as.character(Basisår))]),
                                   Brukerindeks = 1.0)

# ******************************************************************************************** #
# Kopierer brukerne i Sektor 3 og 4 som ble lest inn tidligere.                                #
# ******************************************************************************************** #

DemografiGruppe[[3]] <- DemografiGruppe3
DemografiGruppe[[4]] <- DemografiGruppe4

# ******************************************************************************************** #
# Beregner brukere av annet i sektoren (voksenopplæring, fagskoler etc.).                      #
# Dette er Likning 18 i modellen.                                                              #
# ******************************************************************************************** #

DemografiGruppe[[5]] <- data.frame(FraAlder = 0,
                                   TilAlder = 99,
                                   Brukere = sum(Befolkning[, paste0("X",
                                                                     as.character(Basisår))]),
                                   Brukerindeks = 1.0)

# ******************************************************************************************** #
# Beregner brukere utenfor sektoren.                                                           #
# Dette er Likning 19 i modellen.                                                              #
# ******************************************************************************************** #

DemografiGruppe[[6]] <- data.frame(FraAlder = 0,
                                   TilAlder = 99,
                                   Brukere = sum(Befolkning[, paste0("X",
                                                                     as.character(Basisår))]),
                                   Brukerindeks = 1.0)

# ******************************************************************************************** #
# Beregner den demografiske utvikling i hver sysselsettingssektor.                             #
# ******************************************************************************************** #

for (S in 1:6) {
    
    # **************************************************************************************** #
    # Finner folkemengden fra befolkningsframskrivningene for brukergruppene i brukergruppen.  #
    # Dette er Likning 20 i modellen.                                                          #
    # **************************************************************************************** #

    BefolkningSektor[[S]] <- merge(Brukergruppe[[S]],
                                   Befolkning, by = "Alder") %>% group_by(TilAlder) %>%
                             summarize(across(c(paste0("X", as.character(Basisår))
                                               :paste0("X", as.character(Sluttår))),
                                              \(x) sum(x, na.rm = TRUE)))
  
    # **************************************************************************************** #
    # Angir en radetikett for maksimumsalderen til bukergruppen.                               #
    # **************************************************************************************** #
    
    rownames(DemografiGruppe[[S]]) <- DemografiGruppe[[S]]$TilAlder
  
    # **************************************************************************************** #
    # Angir at antall innleste brukere skal være brukere i basisåret.                          #
    # **************************************************************************************** #
  
    DemografiGruppe[[S]][paste0("Brukere", paste0("X", as.character(Basisår)))] <-
    DemografiGruppe[[S]]$Brukere

    # **************************************************************************************** #
    # Beregner antall brukere i hvert framskrivningsår.                                        #
    # Dette er Likning 21 i modellen.                                                          #
    # **************************************************************************************** #

    for (t in (Basisår + 1):Sluttår) {
        DemografiGruppe[[S]][[paste0("Brukere", paste0("X", as.character(t)))]] <-
        DemografiGruppe[[S]][[paste0("Brukere", paste0("X", as.character(t-1)))]] *
        (BefolkningSektor[[S]][[paste0("X", as.character(t))]] /
         BefolkningSektor[[S]][[paste0("X", as.character(t-1))]])
    }
    
    # **************************************************************************************** #
    # Oppretter en tom tabell for summering av brukerne i hvert framskrivningsår.              #
    # **************************************************************************************** #

    SumDemografiGruppe[[S]] <- data.frame(t(Basisår:Sluttår))

    # **************************************************************************************** #
    # Beregner summen av brukerne i hvert framskrivningsår.                                    #
    # Dette er Likning 22 i modellen.                                                          #
    # **************************************************************************************** #
  
    for (t in Basisår:Sluttår) {
        SumDemografiGruppe[[S]][[paste0("SumBrukere",
                                        paste0("X", as.character(t)))]] <-
        sum(DemografiGruppe[[S]][[paste0("Brukere",
                                         paste0("X", as.character(t)))]], na.rm = TRUE)
    }

    # **************************************************************************************** #
    # Oppretter en tom tabell som skal inneholde den demografiske utviklingen i sektoren.      #
    # **************************************************************************************** #

    KN <- paste0("DemografiKomponent", S)
    DemografiSektor[[S]] <- data.frame(År = paste0("X", as.character(Basisår)), TempColumn = 1)  
    names(DemografiSektor[[S]])[names(DemografiSektor[[S]]) == "TempColumn"] <- KN
  
    # **************************************************************************************** #
    # Beregner den demografiske utviklingen for hvert framskrivningsår for hver brukergruppe.  #
    # Dette er Likning 23 i modellen.                                                          #
    # **************************************************************************************** #

    for (t in (Basisår + 1):Sluttår) {
        NesteÅrgang <- data.frame(År = paste0("X", as.character(t)))
        NesteÅrgang[KN] <- SumDemografiGruppe[[S]][[paste0("SumBrukere",
                                                           paste0("X", as.character(t)))]] / 
                           SumDemografiGruppe[[S]][[paste0("SumBrukere",
                                                           paste0("X", as.character(Basisår)))]]
    
        # ************************************************************************************ #
        # Den demografiske utviklingen i framskrivningsåret legges til som en ny årgang i      #
        # tabellen med den demografiske utviklingen i sektoren.                                #
        # ************************************************************************************ #
    
        DemografiSektor[[S]] <- rbind(DemografiSektor[[S]], NesteÅrgang)
    }
}

# ******************************************************************************************** #
# Kopierer tabellene med den demografiske utviklingen i hver sektor sammen med                 #
# spesifikasjonen av eventuell standardendring inn i en og samme tabell (alternativ bane).     #
# ******************************************************************************************** #

DemografiIndeks <- Standardendring # Assuming this is correctly initialized

for (Sektor in 1:6) {
    DemografiIndeks <- merge(DemografiIndeks, DemografiSektor[[Sektor]], by = "År", all = TRUE)
}

# ******************************************************************************************** #
# Legger til konstanten som angir de 7 utdanningene i modellen i tabellen.                     #
# ******************************************************************************************** #

DemografiIndeks <- DemografiIndeks %>% 
                   expand_grid(Utdanning = Utdanninger) %>%
                   arrange(Utdanning, År)

# ******************************************************************************************** #
# Lærertettheter basert på basisåret. Holdes konstante.                                        #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Kopierer tabellen med den demografiske utviklingen i hver sektor, den transponerte tabellen  #
# med etterspørselen funnet i likning 11 og eventuell angitt lærermangel inn i samme tabell.   #
# ******************************************************************************************** #

Etterspørsel <- merge(DemografiIndeks, Etterspørsel, by = c("Utdanning"), all = TRUE)
Etterspørsel <- merge(Etterspørsel, Laerermangel, by = c("Utdanning"), all = TRUE)

# ******************************************************************************************** #
# Beregner etterspørselen.                                                                     #
# Dette er Likning 24 og Likning 25 i modellen.                                                #
# ******************************************************************************************** #

for(S in 1:6) {
    Etterspørsel <- Etterspørsel %>%
    mutate(!!sym(paste0("Etterspørsel")) := !!sym(paste0("Etterspørsel")) +
                                            (!!sym(paste0("EtterspørselSektor", S)) +
                                             !!sym(paste0("LaerermangelSektor", S))) *
                                            !!sym(paste0("DemografiKomponent", S)) *
                                            !!sym(paste0("StandardEndring", S)))
}

# ******************************************************************************************** #
# Setter sammen tilbud og etterspørsel.                                                        #
# Dette er Likning 26 og Likning 27 i modellen.                                                #
# ******************************************************************************************** #

Tilbud$År <- paste0("X", as.character(Tilbud$År))

FørsteAggregat <- aggregate(Etterspørsel ~ Utdanning + År, data = Sektorfordelt, FUN = sum)
FørsteAggregat$År <- paste0("X", as.character(Basisår))
names(FørsteAggregat)[names(FørsteAggregat) == "Etterspørsel"] <- "Tilbud"

AndreAggregat <- aggregate(Tilbud ~ Utdanning + År,
                           data = Tilbud,
                           FUN = sum,
                           subset = År > paste0("X", as.character(Basisår)))

TilbudEtterspørsel <- merge(rbind(FørsteAggregat, AndreAggregat),
                            Etterspørsel,
                            by = c("Utdanning", "År"),
                            all = TRUE)

TilbudEtterspørsel$År <- sub("X", "", TilbudEtterspørsel$År, fixed = TRUE)

# ******************************************************************************************** #
# Beregner differansen.                                                                        #
# Dette er Likning 28 i modellen.                                                              #
# ******************************************************************************************** #

TilbudEtterspørsel$Differanse <- with(TilbudEtterspørsel, Tilbud - Etterspørsel)

# ******************************************************************************************** #
# Skriver ut resultatene og en hyggelig avskjedshilsen.                                        #
# ******************************************************************************************** #

TilbudEtterspørsel <- data.frame(lapply(TilbudEtterspørsel[c("Utdanning",
                                                             "År",
                                                             "Tilbud",
                                                             "Etterspørsel",
                                                             "Differanse")],
                                        function(x) {if(is.numeric(x)) {as.integer(round(x))} 
                                                     else {x}}))

Rekkefølge <- c(ba = 1, gr = 2, lu = 3, ph = 4, pe = 5, yr = 6, py = 7)

TilbudEtterspørsel$UtdanningOrdered <- TilbudEtterspørsel$Utdanning
TilbudEtterspørsel$UtdanningOrdered <- with(TilbudEtterspørsel, names(Rekkefølge)
                                            [match(Utdanning, names(Rekkefølge))])
TilbudEtterspørsel$UtdanningOrdered <- factor(TilbudEtterspørsel$UtdanningOrdered,
                                              levels = names(Rekkefølge))

TilbudEtterspørsel <- TilbudEtterspørsel %>% arrange(UtdanningOrdered, År)

TilbudEtterspørsel$UtdanningOrdered <- NULL
TilbudEtterspørsel$Utdanning <- factor(TilbudEtterspørsel$Utdanning, 
                                       levels = c("ba", "gr", "lu", "ph", "pe", "yr", "py"),
                                       labels = c("Barnehagelærere", "Grunnskolelærere",
                                                  "Lektorutdannede", "PPU",
                                                  "Praktiske og estetiske fag",
                                                  "Yrkesfaglærere", "PPU Yrkesfag"))

write_csv(TilbudEtterspørsel, 'resultater/Lærermod.csv')
write_xlsx(TilbudEtterspørsel, 'resultater/Lærermod.xlsx')

cat(sprintf("Utdanning                      År Tilbud Ettterspørsel Differanse\n"))
invisible(apply(TilbudEtterspørsel, 1, function(x) {
    cat(sprintf("%-27s   %4s %5d         %5s      %5s",
                x[["Utdanning"]],
                x[["År"]],
                round(as.numeric(x[["Tilbud"]])),
                round(as.numeric(x[["Etterspørsel"]])),
                round(as.numeric(x[["Differanse"]]))),
        "\n")
}))

cat("\nLærermod er nå ferdig, velkommen tilbake.\n")
