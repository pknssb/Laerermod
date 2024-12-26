# ******************************************************************************************** #
# Import av Python-biblioteker samt utskrift av en hyggelig velkomstmelding.                   #
# ******************************************************************************************** #

import pandas as pd
from functools import reduce
pd.options.display.multi_sparse = False

import time

starttid = time.time()

Velkomstmelding = """
Velkommen til Python-versjonen av Lærermod!

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
"""

print(Velkomstmelding)

# ******************************************************************************************** #
# Start- og sluttår for framskrivningen.                                                       #
# ******************************************************************************************** #

Basisår = 2024
Sluttår = 2060

# ******************************************************************************************** #
# Innlesing av inputfiler. Se Appendix 1 for kildedata.                                        #
# ******************************************************************************************** #

Aldersfordelt = pd.read_fwf('inndata/aldersfordelt.txt')

AldersfordeltStudenter = pd.read_fwf('inndata/aldersfordeltstudenter.txt')
Kandidatproduksjon = pd.read_fwf('inndata/kandidatproduksjon.txt')

Sektorfordelt = pd.read_fwf('inndata/sektorfordelt.txt')

Befolkning = pd.read_fwf('inndata/lmm_24.txt')

DemografiGruppe1 = pd.read_fwf('inndata/antall_barn_barnehager.txt')
DemografiGruppe3 = pd.read_fwf('inndata/antall_elever_videregaende.txt')
DemografiGruppe4 = pd.read_fwf('inndata/antall_studenter_hoyereutdanning.txt')

Laerermangel = pd.read_fwf('inndata/laerermangel.txt')

Standardendring = pd.read_fwf('inndata/endring_standard.txt')

# ******************************************************************************************** #
# Oppretter radetiketter på eksisterende kolonner slik at de senere kan benyttes til kopling.  #
# ******************************************************************************************** #

Aldersfordelt.set_index(['Utdanning'], inplace=True)
AldersfordeltStudenter.set_index(['Utdanning'], inplace=True)
Kandidatproduksjon.set_index(['Utdanning'], inplace=True)
Sektorfordelt.set_index(['Utdanning', 'Sektor'], inplace=True)
Befolkning.set_index(['Alder', 'Kjønn'], inplace=True)

# ******************************************************************************************** #
# Oppretter en konstant med forkortelsene for de utdanningene som er inkludert i modellen.     #
# ******************************************************************************************** #

Utdanninger = ['ba', 'gr', 'lu', 'ph', 'pe', 'yr', 'py']

# ******************************************************************************************** #
# Oppretter dictionaries for senere utfylling.                                                 #
# ******************************************************************************************** #

BefolkningSektor = {}
Brukergruppe = {}
DemografiSektor = {}
DemografiGruppe = {}
SumDemografiGruppe = {}
Brukere = {}

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

Aldersfordelt['Sysselsettingsandel'] = Aldersfordelt.apply(lambda row: row['Sysselsatte'] /
                                                                       row['Antall']
                                                           if row['Antall'] > 0 else 0, axis=1)

# ******************************************************************************************** #
# Kopierer dette inn i en tabell og fjerner kolonner som nå er overflødige.                    #
# ******************************************************************************************** #

Populasjon = Aldersfordelt.copy()
Aldersfordelt.drop(['Antall', 'Sysselsatte'], axis=1, inplace=True)

# ******************************************************************************************** #
# Finner gjennomsnittlige årsverk                                                              #
# Dette er Likning 2 i modellen.                                                               #
# ******************************************************************************************** #

Populasjon['Årsverk'] = Populasjon.GjennomsnitteligeÅrsverk * Populasjon.Sysselsatte

# ******************************************************************************************** #
# Angir at dette er populasjonen i basisåret og fjerner kolonner som nå er overflødige.        #
# ******************************************************************************************** #

Populasjon['År'] = Basisår
Populasjon.drop(['Sysselsatte', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'],
                axis=1, inplace=True)

# ******************************************************************************************** #
# Framskriving av utgangspopulasjonen. År 2 til sluttår. Basert på statistikk fra basisåret.   #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Kandidatproduksjonen:                                                                        #
# Beregner først totalt antall førsteårsstudenter for hver av utdanningene.                    #
# Dette er Likning 3 i modellen.                                                               #
# ******************************************************************************************** #

AntallFørsteårsStudenter = AldersfordeltStudenter.groupby(
                               ['Utdanning']).sum().rename(columns={'Alle': 'Totalt'})

# ******************************************************************************************** #
# Kopierer inn totalt antall studenter for den aktuelle utdanning i en ny kolonne i            #
# tabellen AldersfordeltStudenter. Legger til en variabel for kjønn.                           #
# ******************************************************************************************** #

AldersfordeltStudenter = AldersfordeltStudenter.merge(AntallFørsteårsStudenter['Totalt'],
                                                      how='inner', on='Utdanning')
NyeStudenter = pd.concat([AldersfordeltStudenter, AldersfordeltStudenter],
                         keys=[1, 2], names=['Kjønn']).reset_index()

# ******************************************************************************************** #
# Beregner andel studenter for hver alder og hvert kjønn.                                      #
# Dette er Likning 4 i modellen.                                                               #
# ******************************************************************************************** #

NyeStudenter['AndelStudenterEtterAlder'] = NyeStudenter.apply(lambda row: row['Menn'] /
                                                              row['Totalt'] if row['Kjønn']==1 
                                                              else row['Kvinner'] /
                                                              row['Totalt'], axis=1)

# ******************************************************************************************** #
# Angir at antall studenter er konstant i hvert framskrivningsår.                              #
# ******************************************************************************************** #

Kandidatproduksjon = Kandidatproduksjon.merge(
    pd.concat([pd.DataFrame({'År': list(range(Basisår, Sluttår+1))})] * 7,
              keys=Utdanninger, names=['Utdanning']), how='inner', on='Utdanning')

# ******************************************************************************************** #
# Beregner antall årlige kandidater ved hjelp av nye studenter og fullføringsprosenter.        #
# Dette er Likning 5 i modellen.                                                               #
# ******************************************************************************************** #

Kandidatproduksjon['Kandidater'] = (Kandidatproduksjon.AntallNyeStudenter *
                                    Kandidatproduksjon.Fullføringsprosent)

# ******************************************************************************************** #
# Angir at antall kandidater skal være konstant i framskrivingsperioden.                       #
# ******************************************************************************************** #

Kandidater = NyeStudenter.merge(Kandidatproduksjon, how='inner', on=['Utdanning'])

# ******************************************************************************************** #
# Beregner alder for uteksaminering. Passer på at alder for uteksaminering heter det samme som #
# i den tabellen radene skal leggges til i senere.                                             #
# Dette er Likning 6 og Likning 7 i modellen.                                                  #
# ******************************************************************************************** #

Kandidater['Alder'] = (Kandidater.Alder + 
                       Kandidater.Studielengde)
Kandidater['UteksaminerteEtterAlder'] = (Kandidater.Kandidater *
                                         Kandidater.AndelStudenterEtterAlder)

# ******************************************************************************************** #
# Kopierer populasjonen i basisåret, beregnet i likning 2, inn i en ny tabell som blir         #
# utgangspunktet for beregningene.                                                             #
# ******************************************************************************************** #

PopulasjonAktueltÅr = Populasjon.copy()

# ******************************************************************************************** #
# For hvert framskrivningsår skal populasjonen bli ett år eldre og nye kandidater legges til.  #
# ******************************************************************************************** #

for t in range(Basisår + 1, Sluttår + 1):

    # **************************************************************************************** #
    # Pensjonering (for utgangspopulasjonen og kandidater).                                    #
    # **************************************************************************************** #

    # **************************************************************************************** #
    # For hvert år inkrementeres alderen i populasjonen.                                       #
    # Dette er Likning 8 i modellen.                                                           #
    # **************************************************************************************** #
    
    PopulasjonAktueltÅr.Alder += 1

    # **************************************************************************************** #
    # Kandidater etter alder og kjønn som ble funnet i likning 6 og 7 legges til i tabellen.   #
    # **************************************************************************************** #

    PopulasjonAktueltÅr = PopulasjonAktueltÅr.merge(Kandidater[Kandidater['År'] == t].copy(),
                                                    how='outer',
                                                    on=['Utdanning', 'Kjønn', 'Alder'])

    # **************************************************************************************** #
    # Uteksaminerte etter alder og kjønn funnet i Likning 7 legges til populasjonen.           #
    # Dette er Likning 9 i modellen.                                                           #
    # **************************************************************************************** #
    
    PopulasjonAktueltÅr.Antall = (PopulasjonAktueltÅr.Antall.fillna(0) +
                                  PopulasjonAktueltÅr.UteksaminerteEtterAlder.fillna(0))
    
    # **************************************************************************************** #
    # Angir at dette skal være populasjonen i framskrivningsåret.                              #
    # **************************************************************************************** #
    
    PopulasjonAktueltÅr['År'] = t

    # **************************************************************************************** #
    # Populasjonen i framskrivningsåret legges til populasjonen som en ny årgang.              #
    # **************************************************************************************** #

    Kolonner = ['Utdanning', 'Kjønn', 'Alder', 'Antall', 'År']
    Populasjon = pd.concat([Populasjon, PopulasjonAktueltÅr[Kolonner]])

    # **************************************************************************************** #
    # Kopierer populasjonen i framskrivningsåret til tabellen for neste framskrivningsår.      #
    # **************************************************************************************** #

    PopulasjonAktueltÅr = Populasjon[Populasjon['År']==t].copy()

# ******************************************************************************************** # 
# Henter inn Sysselsettingsandel og Gjennomsnittelige årsverk som ble beregnet for             #
# utgangspopulasjonen i Likning 6 og 7. Angir at dette skal bli tabellen for tilbudet.         #
# ******************************************************************************************** #

Tilbud = Populasjon.merge(Aldersfordelt, how='left', on=['Utdanning', 'Kjønn', 'Alder'])

# ******************************************************************************************** #
# Beregner tilbudet.                                                                           #
# Dette er Likning 10 i modellen.                                                              #
# ******************************************************************************************** #

Tilbud['Tilbud'] = Tilbud.Antall * Tilbud.Sysselsettingsandel * Tilbud.GjennomsnitteligeÅrsverk

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

Sektorfordelt = pd.DataFrame({'Etterspørsel': ((Sektorfordelt.SysselsatteMenn *
                                                Sektorfordelt.GjennomsnitteligeÅrsverkMenn) +
                                               (Sektorfordelt.SysselsatteKvinner *
                                                Sektorfordelt.GjennomsnitteligeÅrsverkKvinner)),
                              'År': Basisår})

# ******************************************************************************************** #
# Oppretter en tom tabell for etterspørselen der hver av de 7 utdanningene inngår.             #
# ******************************************************************************************** #

Etterspørsel = pd.DataFrame({'Utdanning': Utdanninger, 'Etterspørsel': 0})

# ******************************************************************************************** #
# For hver av de 7 utdanningene og hver av de 6 sektorene kopieres verdiene som ble funnet     #
# i likning 11 inn i tabellen med etterspørselen. Dette transponerer tabellen.                 #
# ******************************************************************************************** #

for S in range(1, 7):
    Etterspørsel[f'EtterspørselSektor{S}'] = Sektorfordelt.Etterspørsel[
        Sektorfordelt.Etterspørsel.index.get_level_values('Sektor') == S].reset_index(drop=True)

# ******************************************************************************************** #
# Framskrivingsår. Finner antall brukere i basisåret for å beregne dekningsgrader og           #
# tettheter. Veksten framover i antall brukere basert på SSBs nasjonale                        #
# befolkningsframskrivinger.                                                                   #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Oppretter 6 tomme tabeller som skal fylles med antall brukere i hver sektor.                 #
# ******************************************************************************************** #

Brukergruppe[1] = pd.DataFrame({'TilAlder': [0, 2, 2, 3, 5, 5],
                                'Alder': range(0, 6)})
Brukergruppe[2] = pd.DataFrame({'TilAlder': [15] * 10,
                                'Alder': range(6, 16)})
Brukergruppe[3] = pd.DataFrame({'TilAlder': [15] * 16 + list(range(16, 25)) + [49] * 25,
                                'Alder': range(0, 50)})
Brukergruppe[4] = pd.DataFrame({'TilAlder': list(range(19, 30)) + [34] * 5 + [39] * 5 +
                                                                  [44] * 5 + [49] * 5,
                                'Alder': range(19, 50)})
Brukergruppe[5] = pd.DataFrame({'TilAlder': 99,
                                'Alder': range(0, 100)})
Brukergruppe[6] = pd.DataFrame({'TilAlder': 99,
                                'Alder': range(0, 100)})

# ******************************************************************************************** #
# Summerer antall barn i barnehager i hver brukergruppe etter gjennomsnittelig oppholdstid.    #
# Dette er Likning 12 og Likning 13 i modellen.                                                #
# ******************************************************************************************** #

BarnGruppe1 = pd.DataFrame({'Brukere': DemografiGruppe1.Alder0,
                            'Timer': DemografiGruppe1.TimerMin + (
                                (DemografiGruppe1.TimerMax - DemografiGruppe1.TimerMin) / 2)})
BarnGruppe2 = pd.DataFrame({'Brukere': DemografiGruppe1.Alder1 + DemografiGruppe1.Alder2,
                            'Timer': DemografiGruppe1.TimerMin + (
                                (DemografiGruppe1.TimerMax - DemografiGruppe1.TimerMin) / 2)})
BarnGruppe3 = pd.DataFrame({'Brukere': DemografiGruppe1.Alder3,
                            'Timer': DemografiGruppe1.TimerMin + (
                                (DemografiGruppe1.TimerMax - DemografiGruppe1.TimerMin) / 2)})
BarnGruppe4 = pd.DataFrame({'Brukere': DemografiGruppe1.Alder4 + DemografiGruppe1.Alder5,
                            'Timer': DemografiGruppe1.TimerMin + (
                                (DemografiGruppe1.TimerMax - DemografiGruppe1.TimerMin) / 2)})

# ******************************************************************************************** #
# Oppretter en tom tabell som skal fylles med antall brukere i barnehagesektoren.              #
# ******************************************************************************************** #

DemografiGruppe[1] = pd.DataFrame(columns=['FraAlder', 'TilAlder', 'Brukere', 'Brukerindeks'])

# ******************************************************************************************** #
# Beregner brukere av barnehage i hver av de 4 brukergruppene samt brukerindekser for disse.   #
# Dette er Likning 14 og Likning 15 i modellen.                                                #
# ******************************************************************************************** #

DemografiGruppe[1].loc[len(DemografiGruppe[1].index)] = [0, 0, BarnGruppe1.Brukere.sum(),
                                                         (2 * BarnGruppe1.Brukere.
                                                          mul(BarnGruppe1.Timer.values).sum()) /
                                                         (BarnGruppe1.Brukere.sum() * 42.5)]
DemografiGruppe[1].loc[len(DemografiGruppe[1].index)] = [1, 2, BarnGruppe2.Brukere.sum(),
                                                         (2 * BarnGruppe2.Brukere.
                                                          mul(BarnGruppe2.Timer.values).sum()) /
                                                         (BarnGruppe2.Brukere.sum() * 42.5)]
DemografiGruppe[1].loc[len(DemografiGruppe[1].index)] = [3, 3, BarnGruppe3.Brukere.sum(),
                                                         (1.5 * BarnGruppe3.Brukere.
                                                          mul(BarnGruppe3.Timer.values).sum()) /
                                                         (BarnGruppe3.Brukere.sum() * 42.5)]
DemografiGruppe[1].loc[len(DemografiGruppe[1].index)] = [4, 5, BarnGruppe4.Brukere.sum(),
                                                         (1 * BarnGruppe4.Brukere.
                                                          mul(BarnGruppe4.Timer.values).sum()) /
                                                         (BarnGruppe4.Brukere.sum() * 42.5)]

# ******************************************************************************************** #
# Oppdaterer tallene for antall brukere av barnehage i hver av de 4 brukergruppene når det tas #
# hensyn til brukerindeksene.                                                                  #
# Dette er Likning 16 i modellen.                                                              #
# ******************************************************************************************** #

DemografiGruppe[1].loc[0] = [0, 0, DemografiGruppe[1].loc[0].Brukere *
                                   DemografiGruppe[1].loc[0].Brukerindeks,
                             DemografiGruppe[1].loc[0].Brukerindeks]
DemografiGruppe[1].loc[1] = [1, 2, DemografiGruppe[1].loc[1].Brukere *
                                   DemografiGruppe[1].loc[1].Brukerindeks,
                             DemografiGruppe[1].loc[1].Brukerindeks]
DemografiGruppe[1].loc[2] = [3, 3, DemografiGruppe[1].loc[2].Brukere *
                                   DemografiGruppe[1].loc[2].Brukerindeks,
                             DemografiGruppe[1].loc[2].Brukerindeks]
DemografiGruppe[1].loc[3] = [4, 5, DemografiGruppe[1].loc[3].Brukere *
                                   DemografiGruppe[1].loc[3].Brukerindeks,
                             DemografiGruppe[1].loc[3].Brukerindeks]

# ******************************************************************************************** #
# Beregner elever i grunnskolen.                                                               #
# Dette er Likning 17 i modellen.                                                              #
# ******************************************************************************************** #

DemografiGruppe[2] = pd.DataFrame({'FraAlder': 6,
                                   'TilAlder': 15,
                                   'Brukere': Befolkning.query('Alder>=6 and Alder<=15')
                                   [str(Basisår)].sum(), 'Brukerindeks': 1.0}, index=[0])

# ******************************************************************************************** #
# Kopierer brukerne i Sektor 3 og 4 som ble lest inn tidligere.                                #
# ******************************************************************************************** #

DemografiGruppe[3] = DemografiGruppe3.copy()
DemografiGruppe[4] = DemografiGruppe4.copy()

# ******************************************************************************************** #
# Beregner brukere av annet i sektoren (voksenopplæring, fagskoler etc.).                      #
# Dette er Likning 18 i modellen.                                                              #
# ******************************************************************************************** #

DemografiGruppe[5] = pd.DataFrame({'FraAlder': 0,
                                   'TilAlder': 99,
                                   'Brukere': Befolkning[str(Basisår)].sum(),
                                   'Brukerindeks': 1.0}, index=[0])

# ******************************************************************************************** #
# Beregner brukere utenfor sektoren.                                                           #
# Dette er Likning 19 i modellen.                                                              #
# ******************************************************************************************** #

DemografiGruppe[6] = pd.DataFrame({'FraAlder': 0,
                                   'TilAlder': 99,
                                   'Brukere': Befolkning[str(Basisår)].sum(),
                                   'Brukerindeks': 1.0}, index=[0])

# ******************************************************************************************** #
# Beregner den demografiske utvikling i hver sysselsettingssektor.                             #
# ******************************************************************************************** #

for S in range(1, 7):

    # **************************************************************************************** #
    # Oppretter en tom tabell for befolkningen i aktuell sektor.                               #
    # **************************************************************************************** #

    BefolkningSektor[S] = pd.DataFrame()
    
    # **************************************************************************************** #
    # Finner folkemengden fra befolkningsframskrivningene for brukergruppene i brukergruppen.  #
    # Dette er Likning 20 i modellen.                                                          #
    # **************************************************************************************** #

    BefolkningSektor[S] = Brukergruppe[S].merge(Befolkning, how='inner',
                                                on='Alder').groupby(['TilAlder']).sum()
    
    # **************************************************************************************** #
    # Angir en radetikett for maksimumsalderen til bukergruppen.                               #
    # **************************************************************************************** #

    DemografiGruppe[S] = DemografiGruppe[S].set_index(['TilAlder'])

    # **************************************************************************************** #
    # Angir at antall innleste brukere skal være brukere i basisåret.                          #
    # **************************************************************************************** #
    
    DemografiGruppe[S]['Brukere' + str(Basisår)] = DemografiGruppe[S].Brukere 
    
    # **************************************************************************************** #
    # Beregner antall brukere i hvert framskrivningsår.                                        #
    # Dette er Likning 21 i modellen.                                                          #
    # **************************************************************************************** #

    for t in range(Basisår + 1, Sluttår + 1):
        DemografiGruppe[S][f'Brukere{t}'] = \
        DemografiGruppe[S][f'Brukere{t-1}'] * (BefolkningSektor[S][str(t)] / 
                                               BefolkningSektor[S][str(t-1)])
    
    # **************************************************************************************** #
    # Oppretter en tom tabell for summering av brukerne i hvert framskrivningsår.              #
    # **************************************************************************************** #
    
    SumDemografiGruppe[S] = pd.DataFrame()
    
    # **************************************************************************************** #
    # Beregner summen av brukerne i hvert framskrivningsår.                                    #
    # Dette er Likning 22 i modellen.                                                          #
    # **************************************************************************************** #

    for t in range(Basisår, Sluttår + 1):
        SumDemografiGruppe[S][f'SumBrukere{t}'] = [DemografiGruppe[S][f'Brukere{t}'].sum()]
    
    # **************************************************************************************** #
    # Oppretter en tom tabell som skal inneholde den demografiske utviklingen i sektoren.      #
    # **************************************************************************************** #

    DemografiSektor[S] = pd.DataFrame({'År': [Basisår], f'DemografiKomponent{S}': [1]})
    
    # **************************************************************************************** #
    # Beregner den demografiske utviklingen for hvert framskrivningsår for hver brukergruppe.  #
    # Dette er Likning 23 i modellen.                                                          #
    # **************************************************************************************** #

    for t in range(Basisår + 1, Sluttår + 1):
        NesteÅrgang = pd.DataFrame({
            'År': t,
            f'DemografiKomponent{S}': (SumDemografiGruppe[S][f'SumBrukere{t}'] /
                                       SumDemografiGruppe[S][f'SumBrukere{Basisår}'])})
        
        # ************************************************************************************ #
        # Den demografiske utviklingen i framskrivningsåret legges til som en ny årgang i      #
        # tabellen med den demografiske utviklingen i sektoren.                                #
        # ************************************************************************************ #

        DemografiSektor[S] = pd.concat([DemografiSektor[S], NesteÅrgang], ignore_index=True)

# ******************************************************************************************** #
# Kopierer tabellene med den demografiske utviklingen i hver sektor sammen med                 #
# spesifikasjonen av eventuell standardendring inn i en og samme tabell (alternativ bane).     #
# ******************************************************************************************** #

DemografiIndeks = Standardendring.copy()
for Sektor in range(1, 7):
    DemografiIndeks = pd.merge(DemografiIndeks, DemografiSektor[Sektor])

# ******************************************************************************************** #
# Legger til konstanten som angir de 7 utdanningene i modellen i tabellen.                     #
# ******************************************************************************************** #

DemografiIndeks = pd.concat([DemografiIndeks] * 7, keys=Utdanninger, names=['Utdanning'])

# ******************************************************************************************** #
# Lærertettheter basert på basisåret. Holdes konstante.                                        #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Kopierer tabellen med den demografiske utviklingen i hver sektor, den transponerte tabellen  #
# med etterspørselen funnet i likning 11 og eventuell angitt lærermangel inn i samme tabell.   #
# ******************************************************************************************** #

Etterspørsel = reduce(lambda left, right: pd.merge(left, right, on=['Utdanning'], how='outer'),
                      [DemografiIndeks, Etterspørsel, Laerermangel]).set_index(['Utdanning',
                                                                                'År'])

# ******************************************************************************************** #
# Beregner etterspørselen.                                                                     #
# Dette er Likning 24 og Likning 25 i modellen.                                                #
# ******************************************************************************************** #

for S in range(1, 7):
    Etterspørsel['Etterspørsel'] = (Etterspørsel['Etterspørsel'] +
                                    (Etterspørsel[f'EtterspørselSektor{S}'] +
                                     Etterspørsel[f'LaerermangelSektor{S}']) *
                                    Etterspørsel[f'DemografiKomponent{S}'] *
                                    Etterspørsel[f'StandardEndring{S}'])

# ******************************************************************************************** #
# Setter sammen tilbud og etterspørsel.                                                        #
# Dette er Likning 26 og Likning 27 i modellen.                                                #
# ******************************************************************************************** #

TilbudEtterspørsel = pd.concat([pd.DataFrame({'Tilbud': Sektorfordelt.Etterspørsel,
                                              'År': Basisår}).groupby(['Utdanning', 'År'],
                                                                      as_index=True).sum(),
                                Tilbud.groupby(['Utdanning', 'År'],as_index=True).sum().
                                query('År > @Basisår')]).merge(Etterspørsel, how='outer', 
                                                               on=['Utdanning', 'År'])

# ******************************************************************************************** #
# Beregner differansen.                                                                        #
# Dette er Likning 28 i modellen.                                                              #
# ******************************************************************************************** #

TilbudEtterspørsel['Differanse'] = TilbudEtterspørsel.Tilbud - TilbudEtterspørsel.Etterspørsel
    
# ******************************************************************************************** #
# Skriver ut resultatene og en hyggelig avskjedshilsen.                                        #
# ******************************************************************************************** #

Rekkefølge = {'ba': 1, 'gr': 2, 'lu': 3, 'ph': 4, 'pe': 5, 'yr': 6, 'py': 7}

TilbudEtterspørsel = TilbudEtterspørsel[['Tilbud', 'Etterspørsel', 'Differanse']]
TilbudEtterspørsel = TilbudEtterspørsel.sort_values(by=['Utdanning', 'År'],
                                                        key=lambda x: x.map(Rekkefølge))                         
TilbudEtterspørsel.rename(index={'ba': 'Barnehagelærere',
                                 'gr': 'Grunnskolelærere',
                                 'lu': 'Lektorutdannede',
                                 'ph': 'PPU',
                                 'pe': 'Praktiske og estetiske fag',
                                 'yr': 'Yrkesfaglærere',
                                 'py': 'PPU Yrkesfag'}, inplace=True)

# TilbudEtterspørsel.round(0).astype(int).to_csv('resultater/Lærermod.csv')
# TilbudEtterspørsel.round(0).astype(int).to_excel('resultater/Lærermod.xlsx')
print(TilbudEtterspørsel.round(0).astype(int).to_string())

print('\nLærermod er nå ferdig, velkommen tilbake.\n')

totaltid = time.time() - starttid

print(f'Og det tok {totaltid:.2f} sekunder.')
print()
