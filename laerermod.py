# ******************************************************************************************** #
# Import av Python-biblioteker samt utskrift av en hyggelig velkomstmelding.                   #
# ******************************************************************************************** #

import pandas as pd
from functools import reduce
pd.options.display.multi_sparse = False

print()
print('Velkommen til Python-versjonen av Lærermod!')
print()
print('/********************************************************************/')
print('/********************************************************************/')
print('/* Modellen LÆRERMOD beregner tilbud av og etterspørsel for         */')
print('/* følgende 7 grupper av lærere:                                    */')
print('/*   - Barnehagelærere                                              */')
print('/*   - Grunnskolelærere                                             */')
print('/*   - Lektorutdannede                                              */')
print('/*   - Faglærere                                                    */')
print('/*   - Yrkesfaglærere                                               */')
print('/*   - PPU                                                          */')
print('/*   - PPU Yrkesfag                                                 */')
print('/********************************************************************/')
print('/********************************************************************/')
print()

# ******************************************************************************************** #
# Start- og sluttår for framskrivningen.                                                       #
# ******************************************************************************************** #

Basisår = 2020
Sluttår = 2040

# ******************************************************************************************** #
# Innlesing av kildedata. Filene er dokumentert i Vedlegg 1 i den tekniske dokumentasjonen.    #
# ******************************************************************************************** #

Befolkning = pd.DataFrame(pd.read_fwf('inndata/mmmm.txt'))

SektorFordelt = pd.DataFrame(pd.read_fwf('inndata/sektorfordelt.txt'))
AldersFordelt = pd.DataFrame(pd.read_fwf('inndata/aldersfordelt.txt'))
AldersFordeltStudenter = pd.DataFrame(pd.read_fwf('inndata/aldersfordeltstudenter.txt'))
KandidatProduksjon = pd.DataFrame(pd.read_fwf('inndata/kandidatproduksjon.txt'))

DemografiGruppe1 = pd.DataFrame(pd.read_fwf('inndata/antall_barn_barnehager.txt'))
DemografiGruppe3 = pd.DataFrame(pd.read_fwf('inndata/antall_elever_videregaende.txt'))
DemografiGruppe4 = pd.DataFrame(pd.read_fwf('inndata/antall_studenter_hoyereutdanning.txt'))

Standardendring = pd.DataFrame(pd.read_fwf('inndata/endring_standard.txt'))
Timeverkendring = pd.DataFrame(pd.read_fwf('inndata/endring_timeverk.txt'))
Vakanse = pd.DataFrame(pd.read_fwf('inndata/vakanse.txt'))

# ******************************************************************************************** #
# Oppretter radetiketter på eksisterende kolonner slik at de senere kan benyttes til kopling.  #
# ******************************************************************************************** #

Befolkning.set_index(['Alder', 'Kjønn'], inplace=True)
SektorFordelt.set_index(['Utdanning', 'Sektor'], inplace=True)
AldersFordelt.set_index(['Utdanning'], inplace=True)
AldersFordeltStudenter.set_index(['Utdanning'], inplace=True)
KandidatProduksjon.set_index(['Utdanning'], inplace=True)

# ******************************************************************************************** #
# Oppretter en konstant med forkortelsene for de utdanningene som er inkludert i modellen.     #
# ******************************************************************************************** #

Utdanninger = ['ba', 'gr', 'lu', 'fa', 'yr', 'ph', 'py']

# ******************************************************************************************** #
# Utgangspopulasjon av lærere.                                                                 #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Beregner sysselsattingsandel for populasjonen av utdannede.                                  #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

AldersFordelt['Sysselsettingsandel'] = AldersFordelt.apply(lambda row: row['Sysselsatte'] /
                                         row['Antall'] if row['Antall'] > 0 else 0, axis=1)

# ******************************************************************************************** #
# Kopierer dette inn i en tabell med populasjonen og fjerner kolonner som nå er overflødige.   #
# ******************************************************************************************** #

Populasjon = AldersFordelt.copy()
AldersFordelt.drop(['Antall', 'Sysselsatte'], axis=1, inplace=True)

# ******************************************************************************************** #
# Finner populasjonen.                                                                         #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

Populasjon['Årsverk'] = (Populasjon.Antall *
                         Populasjon.Sysselsettingsandel *
                         Populasjon.GjennomsnitteligeÅrsverk)

# ******************************************************************************************** #
# Angir at dette er populasjonen i basisåret og fjerner kolonner som nå er overflødige.        #
# ******************************************************************************************** #

Populasjon['År'] = Basisår
Populasjon.drop(['Sysselsatte', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'],
                axis=1, inplace=True)

# ******************************************************************************************** #
# Beregner totalt antall studenter for hver av utdanningene.                                   #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

AldersFordeltStudenterTotalt = AldersFordeltStudenter.groupby(
    ['Utdanning']).sum().rename(columns={'Alle': 'Totalt'})

# ******************************************************************************************** #
# Kopierer inn verdiene for totalt antall studenter for aktuell utdanning i en ny kolonne i    #
# tabellen AldersFordeltStudenter. Legger også til en variabel for kjønn.                      #
# ******************************************************************************************** #

AldersFordeltStudenter = AldersFordeltStudenter.merge(AldersFordeltStudenterTotalt['Totalt'],
                                                      how='inner',
                                                      on='Utdanning')
NyeStudenter = pd.concat([AldersFordeltStudenter, AldersFordeltStudenter],
                         keys=[1, 2],
                         names=['Kjønn']).reset_index()

# ******************************************************************************************** #
# Beregner andel studenter for hver alder og hvert kjønn.                                      #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

NyeStudenter['AndelStudenterEtterAlder'] = NyeStudenter.apply(lambda row: row['Menn'] /
                                                              row['Totalt'] if row['Kjønn']==1 
                                                              else row['Kvinner'] /
                                                              row['Totalt'], axis=1)

# ******************************************************************************************** #
# Kandidatproduksjon.                                                                          #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Angir at kandidatproduksjonen skal være konstant i framskrivingsperioden.                    #
# ******************************************************************************************** #

KandidatProduksjon = KandidatProduksjon.merge(
    pd.concat([pd.DataFrame({"År": list(range(Basisår, Sluttår+1))})] * 7,
              keys=Utdanninger, names=['Utdanning']), how='inner', on='Utdanning')

# ******************************************************************************************** #
# Beregner antall uteksaminerte.                                                               #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

KandidatProduksjon['Uteksaminerte'] = (KandidatProduksjon.AntallNyeStudenter *
                                       KandidatProduksjon.FullføringsProsent)

# ******************************************************************************************** #
# Angir at antall uteksaminerte skal være konstant i framskrivingsperioden.                    #
# ******************************************************************************************** #

NyeKandidater = NyeStudenter.merge(KandidatProduksjon, how='inner', on=['Utdanning'])

# ******************************************************************************************** #
# Beregner antall uteksaminerte etter alder og kjønn.                                          #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

NyeKandidater['Alder'] = (NyeKandidater.Alder +
                          NyeKandidater.StudieLengde)
NyeKandidater['UteksaminerteEtterAlder'] = (NyeKandidater.Uteksaminerte *
                                            NyeKandidater.AndelStudenterEtterAlder)

# ******************************************************************************************** #
# Kopierer populasjonen i basisåret inn i to nye tabeller som utgangspunkt for beregningene.   #
# ******************************************************************************************** #

NyPopulasjon = Populasjon.copy()
PopulasjonAktueltÅr = Populasjon.copy()

# ******************************************************************************************** #
# For hvert simuleringsår skal populasjonen bli ett år eldre og nye kandidater legges til.     #
# ******************************************************************************************** #

for x in range(Basisår + 1, Sluttår + 1):

    # **************************************************************************************** #
    # Pensjonering.                                                                            #
    # **************************************************************************************** #

    # **************************************************************************************** #
    # For hvert år inkrementeres nå alderen i populasjonen. De eldste blir da pensjonert.      #
    # Dette er Likning xx i modellen.                                                          #
    # **************************************************************************************** #
    
    PopulasjonAktueltÅr.Alder += 1

    # **************************************************************************************** #
    # Uteksaminerte etter alder og kjønn som ble funnet i likning xx legges til i tabellen.    #
    # **************************************************************************************** #

    PopulasjonAktueltÅr = PopulasjonAktueltÅr.merge(NyeKandidater
                                                    [NyeKandidater['År'] == x].copy(),
                                                    how='outer',
                                                    on=['Utdanning', 'Kjønn', 'Alder'])

    # **************************************************************************************** #
    # Uteksaminerte etter alder og kjønn legges til populasjonen.                              #
    # Dette er Likning xx i modellen.                                                          #
    # **************************************************************************************** #
    
    PopulasjonAktueltÅr.Antall = (PopulasjonAktueltÅr.Antall.fillna(0) +
                                  PopulasjonAktueltÅr.UteksaminerteEtterAlder.fillna(0))
    
    # **************************************************************************************** #
    # Angir at dette skal være populasjonen i simuleringsåret.                                 #
    # **************************************************************************************** #
    
    PopulasjonAktueltÅr['År'] = x

    # **************************************************************************************** #
    # Populasjonen i simuleringsåret legges til populasjonen som en ny årgang.                 #
    # **************************************************************************************** #

    NyPopulasjon = pd.concat([NyPopulasjon, PopulasjonAktueltÅr[['Utdanning',
                                                                 'Kjønn',
                                                                 'Alder',
                                                                 'Antall',
                                                                 'Årsverk',
                                                                 'År']]])

    # **************************************************************************************** #
    # Kopierer populasjonen i simuleringsåret til tabellen for neste simuleringsår.            #
    # **************************************************************************************** #

    PopulasjonAktueltÅr = NyPopulasjon[NyPopulasjon['År']==x].copy()
    
# ******************************************************************************************** #
# Henter inn Sysselsettingsandel og GjennomsnitteligeÅrsverk som ble beregnet for              #
# utgangspopulasjonen i likning xx. Angir at dette skal bli tabellen for tilbudet.             #
# ******************************************************************************************** #

Tilbud = NyPopulasjon.merge(AldersFordelt, how='left', on=['Utdanning', 'Kjønn', 'Alder'])

# ******************************************************************************************** #
# Beregner tilbudet.                                                                           #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

Tilbud['Tilbud'] = Tilbud.Antall * Tilbud.Sysselsettingsandel * Tilbud.GjennomsnitteligeÅrsverk

# ********
# Brukere.
# ********

Brukergruppe1 = pd.DataFrame({'TilAlder': [0, 2, 2, 3, 5, 5],
                              'Alder': range(0, 6)})
Brukergruppe2 = pd.DataFrame({'TilAlder': [15] * 10,
                              'Alder': range(6, 16)})
Brukergruppe3 = pd.DataFrame({'TilAlder': [15] * 16 + list(range(16, 25)) + [49] * 25,
                              'Alder': range(0, 50)})
Brukergruppe4 = pd.DataFrame({'TilAlder': list(range(19, 30)) + [34] * 5 + [39] * 5 +
                                                                [44] * 5 + [49] * 5,
                              'Alder': range(19, 50)})
Brukergruppe5 = pd.DataFrame({'TilAlder': 99,
                              'Alder': range(0, 100)})
Brukergruppe6 = pd.DataFrame({'TilAlder': 99,
                              'Alder': range(0, 100)})

# ******************************************************************************************** #
# Beregner brukere av barnehager i hver aldersgruppe.                                          #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

BarnGruppe1 = pd.DataFrame({'Brukere': DemografiGruppe1.Alder0,
                            'Timer': DemografiGruppe1.TimerMin + ((DemografiGruppe1.TimerMax -
                                                                   DemografiGruppe1.TimerMin)
                                                                  / 2)})
BarnGruppe2 = pd.DataFrame({'Brukere': DemografiGruppe1.Alder1 + DemografiGruppe1.Alder2,
                            'Timer': DemografiGruppe1.TimerMin + ((DemografiGruppe1.TimerMax -
                                                                   DemografiGruppe1.TimerMin)
                                                                   / 2)})
BarnGruppe3 = pd.DataFrame({'Brukere': DemografiGruppe1.Alder3,
                            'Timer': DemografiGruppe1.TimerMin + ((DemografiGruppe1.TimerMax -
                                                                   DemografiGruppe1.TimerMin)
                                                                  / 2)})
BarnGruppe4 = pd.DataFrame({'Brukere': DemografiGruppe1.Alder4 + DemografiGruppe1.Alder5,
                            'Timer': DemografiGruppe1.TimerMin + ((DemografiGruppe1.TimerMax -
                                                                   DemografiGruppe1.TimerMin)
                                                                  / 2)})

DemografiGruppe1 = pd.DataFrame(columns=['Brukere',
                                         'FraAlder',
                                         'TilAlder',
                                         'Populasjon',
                                         'Brukerindeks'])
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Befolkning.query('Alder==0')
                                                     [str(Basisår)].sum(), 0, 0,
                                                     BarnGruppe1.Brukere.sum(),
                                                     (2 * BarnGruppe1.Brukere.
                                                      mul(BarnGruppe1.Timer.values).sum())
                                                     / (BarnGruppe1.Brukere.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Befolkning.
                                                     query('Alder>=1 and Alder<=2')
                                                     [str(Basisår)].sum(), 1, 2,
                                                     BarnGruppe2.Brukere.sum(),
                                                     (2 * BarnGruppe2.Brukere.
                                                      mul(BarnGruppe2.Timer.values).sum()) /
                                                     (BarnGruppe2.Brukere.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Befolkning.query('Alder==3')
                                                     [str(Basisår)].sum(), 3, 3,
                                                     BarnGruppe3.Brukere.sum(),
                                                     (1.5 * BarnGruppe3.Brukere.
                                                      mul(BarnGruppe3.Timer.values).sum()) /
                                                     (BarnGruppe3.Brukere.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Befolkning.query('Alder>=4 and Alder<=5')
                                                     [str(Basisår)].sum(), 4, 5,
                                                     BarnGruppe4.Brukere.sum(),
                                                     (1 * BarnGruppe4.Brukere.
                                                      mul(BarnGruppe4.Timer.values).sum()) /
                                                     (BarnGruppe4.Brukere.sum() * 42.5)]

DemografiGruppe2 = pd.DataFrame({'FraAlder': 6,
                                 'TilAlder': 15,
                                 'Populasjon': Befolkning.query('Alder>=6 and Alder<=15')
                                 [str(Basisår)].sum(), 'Brukerindeks': 1.0}, index=[0])
DemografiGruppe5 = pd.DataFrame({'FraAlder': 0,
                                 'TilAlder': 99,
                                 'Populasjon': Befolkning[str(Basisår)].sum(),
                                 'Brukerindeks': 1.0}, index=[0])
DemografiGruppe6 = pd.DataFrame({'FraAlder': 0,
                                 'TilAlder': 99,
                                 'Populasjon': Befolkning[str(Basisår)].sum(),
                                 'Brukerindeks': 1.0}, index=[0])

# ***********************************
# Vekst (befolkningsframskrivninger).
# ***********************************

for i in range(1, 7):
    locals()[f'Befolkning{i}'] = \
    locals()[f'Brukergruppe{i}'].merge(Befolkning,
                                       how='inner',
                                       on='Alder').groupby(["TilAlder"]).sum()
     
    locals()[f'DemografiGruppe{i}'] = locals()[f'DemografiGruppe{i}'].set_index(["TilAlder"])
    locals()[f'DemografiGruppe{i}']["RelativeBrukere" + str(Basisår)] = \
    locals()[f'DemografiGruppe{i}'].Populasjon * locals()[f'DemografiGruppe{i}'].Brukerindeks
    for x in range(Basisår + 1, Sluttår + 1):
        locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x)] = \
        (locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x-1)] *
         (locals()[f'Befolkning{i}'][str(x)] /
          locals()[f'Befolkning{i}'][str(x-1)]))
        
    locals()[f'SumDemografiGruppe{i}'] = pd.DataFrame()
    for x in range(Basisår, Sluttår + 1):
        locals()[f'SumDemografiGruppe{i}']['SumRelativeBrukere' + str(x)] = \
        [locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x)].sum()]

    locals()[f'DemografiSektor{i}'] = pd.DataFrame({"År": [Basisår],
                                                    "DemografiKomponent" + str(i): [1]})
    for x in range(Basisår + 1, Sluttår + 1):
        NesteÅrgang = pd.DataFrame({"År": x,
                                    "DemografiKomponent" + str(i): \
                                    locals()[f'SumDemografiGruppe{i}'] \
                                     ['SumRelativeBrukere' + str(x)] / \
                                    locals()[f'SumDemografiGruppe{i}'] \
                                    ['SumRelativeBrukere' + str(Basisår)]})
        locals()[f'DemografiSektor{i}'] = pd.concat([locals()[f'DemografiSektor{i}'],
                                                     NesteÅrgang], ignore_index=True)
    
DemografiIndeks = Standardendring.merge((DemografiSektor1).merge
                                        (DemografiSektor2).merge
                                        (DemografiSektor3).merge
                                        (DemografiSektor4).merge
                                        (DemografiSektor5).merge
                                        (DemografiSektor6))
DemografiIndeks = pd.concat([DemografiIndeks,
                             DemografiIndeks,
                             DemografiIndeks,
                             DemografiIndeks,
                             DemografiIndeks,
                             DemografiIndeks,
                             DemografiIndeks],
                            keys=Utdanninger,
                            names=['Utdanning'])

# ********************
# Utgangspopulasjonen.
# ********************

# ******************************************************************************************** #
# Beregner sysselsatte i basisåret. Etterspørselen i basisåret blir satt lik dette.            #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

SektorFordelt = pd.DataFrame({'Etterspørsel': ((SektorFordelt.SysselsatteMenn *
                                                SektorFordelt.GjennomsnitteligeÅrsverkMenn) +
                                               (SektorFordelt.SysselsatteKvinner *
                                                SektorFordelt.GjennomsnitteligeÅrsverkKvinner)),
                              'År' : Basisår})

Etterspørsel = pd.DataFrame({'Utdanning': Utdanninger,
                             'Etterspørsel': 0})
for i in range(1, 7):
    Etterspørsel["EtterspørselSektor"+str(i)] = SektorFordelt.Etterspørsel[
        SektorFordelt.Etterspørsel.index.get_level_values('Sektor') == i].reset_index(drop=True)

Etterspørsel = reduce(lambda left, right: pd.merge(left, right, on=['Utdanning'], how='outer'),
                      [DemografiIndeks,
                       Etterspørsel,
                       Vakanse]).set_index(['Utdanning', 'År'])

# ********
# Tetthet.
# ********

for i in range(1, 7):
    Etterspørsel['Etterspørsel'] = (Etterspørsel['Etterspørsel'] +
                                    (Etterspørsel['EtterspørselSektor' + str(i)] +
                                     Etterspørsel['VakanseSektor' + str(i)]) *
                                    Etterspørsel['DemografiKomponent' + str(i)] *
                                    Etterspørsel['StandardEndring' + str(i)])

TilbudOgEtterspørsel = pd.concat([pd.DataFrame({'Tilbud': SektorFordelt.Etterspørsel,
                                                'År': Basisår}).groupby(['Utdanning', 'År'],
                                                                        as_index=True).sum(),
                                  Tilbud.groupby(['Utdanning', 'År'],
                                                 as_index=True).sum().
                                  query('År > @Basisår')]).merge(Etterspørsel, 
                                                                 how='outer', 
                                                                 on=['Utdanning', 'År'])

# ******************************************************************************************** #
# Beregner differansen.                                                                        #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

TilbudOgEtterspørsel['Differanse'] = (TilbudOgEtterspørsel.Tilbud -
                                      TilbudOgEtterspørsel.Etterspørsel)

# ******************************************************************************************** #
# Skriver ut resultatene og en hyggelig avskjedshilsen.                                        #
# ******************************************************************************************** #

TilbudOgEtterspørsel = TilbudOgEtterspørsel[['Tilbud', 'Etterspørsel', 'Differanse']]
TilbudOgEtterspørsel = TilbudOgEtterspørsel.sort_values(by=['Utdanning', 'År'],
                                                        key=lambda x: x.map({'ba': 1,
                                                                             'gr': 2,
                                                                             'lu': 3,
                                                                             'fa': 4,
                                                                             'yr': 5,
                                                                             'ph': 6,
                                                                             'py': 7}))
TilbudOgEtterspørsel.rename(index={'ba': 'Barnehagelærere',
                                   'gr': 'Grunnskolelærere',
                                   'lu': 'Lektorutdannede',
                                   'fa': 'Faglærere',
                                   'yr': 'Yrkesfaglærere',
                                   'ph': 'PPU',
                                   'py': 'PPU Yrkesfag'}, inplace=True)

TilbudOgEtterspørsel.round(0).astype(int).to_csv("resultater/Lærermod.csv")
TilbudOgEtterspørsel.round(0).astype(int).to_excel("resultater/Lærermod.xlsx")
print(TilbudOgEtterspørsel.round(0).astype(int).to_string())

print()
print('Lærermod er nå ferdig. Velkommen tilbake.')
print()
