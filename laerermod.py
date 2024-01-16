# ******************************************************************************************** #
# Start- og sluttår for framskrivningen.                                                       #
# ******************************************************************************************** #

Basisår = 2020
Sluttår = 2040

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
print('/*   * Barnehagelærere                                              */')
print('/*   * Grunnskolelærere                                             */')
print('/*   * Lektorutdannede                                              */')
print('/*   * Faglærere                                                    */')
print('/*   * Yrkesfaglærere                                               */')
print('/*   * PPU                                                          */')
print('/*   * PPU Yrkesfag                                                 */')
print('/********************************************************************/')
print('/********************************************************************/')
print()

# ******************************************************************************************** #
# Innlesing av kildedata. Filene er dokumentert i Vedlegg 1 i den tekniske dokumentasjonen.    #
# ******************************************************************************************** #

Befolkning = pd.DataFrame(pd.read_fwf('inndata/mmmm_2022.txt',
                                      index_col=['Alder', 'Kjønn']))

SektorFordelt = pd.DataFrame(pd.read_fwf('inndata/sektorfordelt.txt',
                                         index_col=['Utdanning', 'Sektor']))
AldersFordelt = pd.DataFrame(pd.read_fwf('inndata/aldersfordelt.txt',
                                         index_col=['Utdanning']))
AldersFordeltStudenter = pd.DataFrame(pd.read_fwf('inndata/aldersfordeltstudenter.txt',
                                      index_col=['Utdanning']))
KandidatProduksjon = pd.DataFrame(pd.read_fwf('inndata/kandidatproduksjon.txt',
                                              index_col=['Utdanning']))

DemografiGruppe1 = pd.DataFrame(pd.read_fwf('inndata/antall_barn_barnehager.txt'))
DemografiGruppe3 = pd.DataFrame(pd.read_fwf('inndata/antall_elever_videregaende.txt'))
DemografiGruppe4 = pd.DataFrame(pd.read_fwf('inndata/antall_studenter_hoyereutdanning.txt'))

Standardendring = pd.DataFrame(pd.read_fwf('inndata/endring_standard.txt'))
Timeverkendring = pd.DataFrame(pd.read_fwf('inndata/endring_timeverk.txt'))
VakanseEtterspørsel = pd.DataFrame(pd.read_fwf('inndata/vakanse.txt'))

# ****************
# Beregner Tilbud.
# ****************

# ****************************
# Utgangspopulasjon av lærere.
# ****************************

# ******************************************************************************************** #
# Beregner sysselsattingsandel for populasjonen av utdannede lærere.                           #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

AldersFordelt['Sysselsettingsandel'] = AldersFordelt.apply(lambda row: row['Sysselsatte'] /
                                         row['Antall'] if row['Antall'] > 0 else 0, axis=1)

# ******************************************************************************************** #
# Finner populasjonen av lærere.                                                               #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

Populasjon = AldersFordelt.copy()
Populasjon["Årsverk"] = (Populasjon.Antall *
                         Populasjon.Sysselsettingsandel *
                         Populasjon.GjennomsnitteligeÅrsverk)

Populasjon.drop(['Sysselsatte', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'],
                axis=1, inplace=True)

# ******************************************************************************************** #
# Angir at dette er populasjonen i basisåret.                                                  #
# ******************************************************************************************** #

Populasjon['År'] = Basisår

AldersFordelt.drop(['Antall', 'Sysselsatte'], axis=1, inplace=True)

# ******************************************************************************************** #
# Beregner totalt antall studenter for hver av lærerutdanningene.                              #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

AldersFordeltStudenterTotalt = AldersFordeltStudenter.groupby(["Utdanning"]).sum()
AldersFordeltStudenterTotalt.rename(columns={"Alle": "Totalt"}, inplace=True)

AldersFordeltStudenter = AldersFordeltStudenter.merge(AldersFordeltStudenterTotalt['Totalt'],
                                                      how='inner', on='Utdanning')

# ******************************************************************************************** #
# Beregner andel studenter for hver alder og hvert kjønn                                       #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

NyeStudenter = pd.concat([AldersFordeltStudenter, AldersFordeltStudenter],
                         keys=[1, 2], names=['Kjønn']).reset_index()

NyeStudenter['AndelStudenterEtterAlder'] = NyeStudenter.apply(lambda row: row['Menn'] / row['Totalt'] if row['Kjønn'] == 1 else row['Kvinner'] / row['Totalt'], axis=1)

# *******************
# Kandidatproduksjon.
# *******************

# ******************************************************************************************** #
# Beregner antall uteksaminerte.                                                               #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

Gjennomføring = pd.concat([pd.DataFrame({"År": list(range(Basisår, Sluttår+1))})] * 7, keys=['ba', 'gr', 'lu', 'fa', 'yr', 'ph', 'py'], names=['Utdanning'])

KandidatProduksjon = KandidatProduksjon.merge(Gjennomføring, how='inner', on='Utdanning')
KandidatProduksjon['Uteksaminerte'] = KandidatProduksjon.AntallNyeStudenter * KandidatProduksjon.FullføringsProsent

# ******************************************************************************************** #
# Beregner antall uteksaminerte etter alder og kjønn                                           #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

NyeKandidater = NyeStudenter.merge(KandidatProduksjon, how='inner', on=['Utdanning'])
NyeKandidater['Alder'] = NyeKandidater.Alder + NyeKandidater.StudieLengde
NyeKandidater['UteksaminerteEtterAlder'] = NyeKandidater.Uteksaminerte * NyeKandidater.AndelStudenterEtterAlder

LærerVekst = Populasjon.copy()

# ***********************
# Pensjonering av lærere.
# ***********************

PopulasjonForrigeÅr = Populasjon.copy()
PopulasjonForrigeÅr.Alder += 1

for x in range(Basisår + 1, Sluttår + 1):
    NyeLærere = NyeKandidater[NyeKandidater['År'] == x].copy()

    PopulasjonNesteÅr = PopulasjonForrigeÅr.merge(NyeLærere, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])
    PopulasjonNesteÅr.Antall = PopulasjonNesteÅr.Antall.fillna(0) + PopulasjonNesteÅr.UteksaminerteEtterAlder.fillna(0)
    PopulasjonNesteÅr['År'] = x

    LærerVekst = pd.concat([LærerVekst, PopulasjonNesteÅr[['Utdanning', 'Kjønn', 'Alder', 'Antall', 'Årsverk', 'År']]])

    PopulasjonForrigeÅr = LærerVekst[LærerVekst['År'] == x].copy()
    PopulasjonForrigeÅr.Alder += 1

Tilbud = LærerVekst.merge(AldersFordelt, how='left', on=['Utdanning', 'Kjønn', 'Alder'])
Tilbud['Tilbud'] = Tilbud.Antall * Tilbud.Sysselsettingsandel * Tilbud.GjennomsnitteligeÅrsverk

# **********************
# Beregner Etterspørsel.
# **********************

# ********
# Brukere.
# ********

Brukergruppe1 = pd.DataFrame({"TilAlder": [0, 2, 2, 3, 5, 5], "Alder": range(0, 6)})
Brukergruppe2 = pd.DataFrame({"TilAlder": [15] * 10, "Alder": range(6, 16)})
Brukergruppe3 = pd.DataFrame({"TilAlder": [15] * 16 + list(range(16, 25)) + [49] * 25, "Alder": range(0, 50)})
Brukergruppe4 = pd.DataFrame({"TilAlder": list(range(19, 30)) + [34] * 5 + [39] * 5 + [44] * 5 + [49] * 5, "Alder": range(19, 50)})
Brukergruppe5 = pd.DataFrame({"TilAlder": 99, "Alder": range(0, 100)})
Brukergruppe6 = pd.DataFrame({"TilAlder": 99, "Alder": range(0, 100)})

BarnGruppe1 = pd.DataFrame({'FørsteÅr': DemografiGruppe1.Alder0, 'Timer': DemografiGruppe1.TimerMin + ((DemografiGruppe1.TimerMax - DemografiGruppe1.TimerMin) / 2)})
BarnGruppe2 = pd.DataFrame({'FørsteÅr': DemografiGruppe1.Alder1 + DemografiGruppe1.Alder2, 'Timer': DemografiGruppe1.TimerMin + ((DemografiGruppe1.TimerMax - DemografiGruppe1.TimerMin) / 2)})
BarnGruppe3 = pd.DataFrame({'FørsteÅr': DemografiGruppe1.Alder3, 'Timer': DemografiGruppe1.TimerMin + ((DemografiGruppe1.TimerMax - DemografiGruppe1.TimerMin) / 2)})
BarnGruppe4 = pd.DataFrame({'FørsteÅr': DemografiGruppe1.Alder4 + DemografiGruppe1.Alder5, 'Timer': DemografiGruppe1.TimerMin + ((DemografiGruppe1.TimerMax - DemografiGruppe1.TimerMin) / 2)})

DemografiGruppe1 = pd.DataFrame(columns=['FørsteÅr', 'FraAlder', 'TilAlder', 'Populasjon', 'Brukerindeks'])
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Befolkning.query('Alder == 0')[str(Basisår)].sum(), 0, 0, BarnGruppe1.FørsteÅr.sum(), (2 * BarnGruppe1.FørsteÅr.mul(BarnGruppe1.Timer.values).sum()) / (BarnGruppe1.FørsteÅr.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Befolkning.query('Alder >= 1 and Alder <= 2')[str(Basisår)].sum(), 1, 2, BarnGruppe2.FørsteÅr.sum(), (2 * BarnGruppe2.FørsteÅr.mul(BarnGruppe2.Timer.values).sum()) / (BarnGruppe2.FørsteÅr.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Befolkning.query('Alder == 3')[str(Basisår)].sum(), 3, 3, BarnGruppe3.FørsteÅr.sum(), (1.5 * BarnGruppe3.FørsteÅr.mul(BarnGruppe3.Timer.values).sum()) / (BarnGruppe3.FørsteÅr.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Befolkning.query('Alder >= 4 and Alder <= 5')[str(Basisår)].sum(), 4, 5, BarnGruppe4.FørsteÅr.sum(), (1 * BarnGruppe4.FørsteÅr.mul(BarnGruppe4.Timer.values).sum()) / (BarnGruppe4.FørsteÅr.sum() * 42.5)]

DemografiGruppe2 = pd.DataFrame({'FraAlder': 6, 'TilAlder': 15, 'Populasjon': Befolkning.query('Alder >= 6 and Alder <= 15')[str(Basisår)].sum(), 'Brukerindeks': 1.0}, index=[0])
DemografiGruppe5 = pd.DataFrame({'FraAlder': 0, 'TilAlder': 99, 'Populasjon': Befolkning[str(Basisår)].sum(), 'Brukerindeks': 1.0}, index=[0])
DemografiGruppe6 = pd.DataFrame({'FraAlder': 0, 'TilAlder': 99, 'Populasjon': Befolkning[str(Basisår)].sum(), 'Brukerindeks': 1.0}, index=[0])

# ***********************************
# Vekst (befolkningsframskrivninger).
# ***********************************

for i in range(1, 7):
    locals()[f'Befolkning{i}'] = locals()[f'Brukergruppe{i}'].merge(Befolkning, how='inner', on='Alder').groupby(["TilAlder"]).sum()
     
    locals()[f'DemografiGruppe{i}'] = locals()[f'DemografiGruppe{i}'].set_index(["TilAlder"])
    locals()[f'DemografiGruppe{i}']["RelativeBrukere" + str(Basisår)] = locals()[f'DemografiGruppe{i}'].Populasjon * locals()[f'DemografiGruppe{i}'].Brukerindeks
    for x in range(Basisår + 1, Sluttår + 1):
        locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x)] = locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x-1)] * (locals()[f'Befolkning{i}'][str(x)] / locals()[f'Befolkning{i}'][str(x-1)])
        
    locals()[f'SumDemografiGruppe{i}'] = pd.DataFrame()
    for x in range(Basisår, Sluttår + 1):
        locals()[f'SumDemografiGruppe{i}']['SumRelativeBrukere' + str(x)] = [locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x)].sum()]

    locals()[f'Demografiår{i}'] = pd.DataFrame({"År": [Basisår], "DemografiKomponent" + str(i): [1]})
    for x in range(Basisår + 1, Sluttår + 1):
        NesteÅrgang = pd.DataFrame({"År": x, "DemografiKomponent" + str(i): locals()[f'SumDemografiGruppe{i}']['SumRelativeBrukere' + str(x)] / locals()[f'SumDemografiGruppe{i}']['SumRelativeBrukere' + str(Basisår)]})
        locals()[f'Demografiår{i}'] = pd.concat([locals()[f'Demografiår{i}'], NesteÅrgang], ignore_index=True)
    
DemografiIndeks = Standardendring.merge(Demografiår1).merge(Demografiår2).merge(Demografiår3).merge(Demografiår4).merge(Demografiår5).merge(Demografiår6)
DemografiIndeks = pd.concat([DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks], keys=['ba', 'gr', 'lu', 'fa', 'yr', 'ph', 'py'], names=['Utdanning'])

# ********************
# Utgangspopulasjonen.
# ********************

# ******************************************************************************************** #
# Beregner sysselsatte lærere i basisåret. Etterspørselen etter lærere blir satt lik dette.    #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

SektorFordelt['Tilbud'] = SektorFordelt.SysselsatteMenn \
                              * SektorFordelt.GjennomsnitteligeÅrsverkMenn \
                              + SektorFordelt.SysselsatteKvinner \
                              * SektorFordelt.GjennomsnitteligeÅrsverkKvinner

# ******************************************************************************************** #
# Angir at dette skal være etterspørselen i basisåret.                                         #
# ******************************************************************************************** #

SektorFordelt['År'] = Basisår

Tilbud = pd.concat([SektorFordelt.groupby(['Utdanning', 'År'], as_index=True).sum(), Tilbud.groupby(['Utdanning', 'År'], as_index=True).sum().query('År > @Basisår')])

EtterspørselLærere = pd.DataFrame({'Utdanning': ['ba', 'gr', 'lu', 'fa', 'yr', 'ph', 'py'], 'Etterspørsel': 0})
for i in range(1, 7):
    EtterspørselLærere["År"+str(i)] = SektorFordelt.Tilbud[SektorFordelt.Tilbud.index.get_level_values('Sektor') == i].reset_index(drop=True)

# ********
# Tetthet.
# ********

Etterspørsel = reduce(lambda left, right: pd.merge(left, right, on=['Utdanning'], how='outer'), [DemografiIndeks, EtterspørselLærere, VakanseEtterspørsel]).set_index(['Utdanning', 'År'])
for i in range(1, 7):
   Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel['År' + str(i)] + Etterspørsel['VakanseSektor' + str(i)]) * Etterspørsel['DemografiKomponent' + str(i)] * Etterspørsel['Sektor' + str(i)]

# ******************************************************************************************** #
# Beregner differansen.                                                                        #
# Dette er Likning xx i modellen.                                                              #
# ******************************************************************************************** #

TilbudOgEtterspørsel = Tilbud.merge(Etterspørsel, how='outer', on=['Utdanning', 'År'])
TilbudOgEtterspørsel['Differanse'] = TilbudOgEtterspørsel.Tilbud - TilbudOgEtterspørsel.Etterspørsel

# ******************************************************************************************** #
# Skriver ut resultatene.                                                                      #
# ******************************************************************************************** #

TilbudOgEtterspørsel = TilbudOgEtterspørsel[['Tilbud', 'Etterspørsel', 'Differanse']]
TilbudOgEtterspørsel = TilbudOgEtterspørsel.sort_values(by=['Utdanning', 'År'], key=lambda x: x.map({'ba': 1, 'gr': 2, 'lu': 3, 'fa': 4, 'yr': 5, 'ph': 6, 'py': 7}))
TilbudOgEtterspørsel.rename(index={'ba': 'Barnehagelærere', 'gr': 'Grunnskolelærere', 'lu': 'Lektorutdannede', 'fa': 'Faglærere', 'yr': 'Yrkesfaglærere', 'ph': 'PPU', 'py': 'PPU Yrkesfag'}, inplace=True)

TilbudOgEtterspørsel.round(0).astype(int).to_csv("resultater/Lærermod.csv")
TilbudOgEtterspørsel.round(0).astype(int).to_excel("resultater/Lærermod.xlsx")
print(TilbudOgEtterspørsel.round(0).astype(int).to_string())

print()
print('Lærermod er nå ferdig. Velkommen tilbake.')
print()
