import pandas as pd
#import dapla as dp
from functools import reduce
pd.options.display.multi_sparse = False

Basisår = 2020
Sluttår = 2040

befolkning = 'inndata/mmmm_2022.txt'

sektorfordelt = 'inndata/sektorfordelt.txt'
sysselsatt = 'inndata/sysselsatt.txt'
studenter = 'inndata/studenter.txt'
stkap = 'inndata/fullforingsgrader.txt'
oppta = 'inndata/opptak.txt'

dem1 = 'inndata/antall_barn_barnehager.txt'
dem3 = 'inndata/antall_elever_videregaende.txt'
dem4 = 'inndata/antall_studenter_hoyereutdanning.txt'

innpr = 'inndata/endring_standard.txt'
inplu = 'inndata/endring_timeverk.txt'
vakanse = 'inndata/vakanse.txt'

print()
print('Velkommen til Python-versjonen av Lærermod!')
print()
print('/********************************************************************/')
print('/********************************************************************/')
print('/* Modellen LÆRERMOD beregner tilbud av og etterspørsel etter       */')
print('/* følgende 7 grupper av lærere:                                    */')
print('/* * Barnehagelærere                                                */')
print('/* * Grunnskolelærere                                               */')
print('/* * Lektorutdannede                                                */')
print('/* * Faglærere                                                      */')
print('/* * Yrkesfaglærere                                                 */')
print('/* * PPU                                                            */')
print('/* * PPU Yrkesfag                                                   */')
print('/********************************************************************/')
print('/********************************************************************/')
print()

# ***********************
# Innlesing av kildedata.
# ***********************

Bef = pd.DataFrame(pd.read_fwf(befolkning, index_col=['Alder', 'Kjønn']))

SysselsatteLærere = pd.DataFrame(pd.read_fwf(sektorfordelt, index_col=['Utdanning', 'Sektor']))
UtdannedeLærere = pd.DataFrame(pd.read_fwf(sysselsatt))
LærerStudenter = pd.DataFrame(pd.read_fwf(studenter, index_col=['Utdanning']))
Gjennomføring = pd.DataFrame(pd.read_fwf(stkap))
OpptatteLærerStudenter = pd.DataFrame(pd.read_fwf(oppta))

barnhin = pd.DataFrame(pd.read_fwf(dem1))
DemografiGruppe3 = pd.DataFrame(pd.read_fwf(dem3))                  
DemografiGruppe4 = pd.DataFrame(pd.read_fwf(dem4))

Standardendring = pd.DataFrame(pd.read_fwf(innpr))
Timeverkendring = pd.DataFrame(pd.read_fwf(inplu))
VakanseEtterspørsel = pd.DataFrame(pd.read_fwf(vakanse))

# ****************
# Beregner Tilbud.
# ****************

SysselsatteLærere['Tilbud'] = SysselsatteLærere.SysselsatteMenn * SysselsatteLærere.GjennomsnitteligeÅrsverkMenn + SysselsatteLærere.SysselsatteKvinner * SysselsatteLærere.GjennomsnitteligeÅrsverkKvinner
SysselsatteLærere['År'] = Basisår

UtdannedeLærere['Sysselsettingsandel'] = UtdannedeLærere.apply(lambda row: row['Sysselsatte'] / row['Antall'] if row['Antall'] > 0 else 0, axis=1)

LærerStudenterTotalt = LærerStudenter.groupby(["Utdanning"]).sum()
LærerStudenterTotalt.rename(columns={"Alle": "Totalt"}, inplace=True)

LærerStudenter = LærerStudenter.merge(LærerStudenterTotalt['Totalt'], how='inner', on='Utdanning')

NyeStudenter = pd.concat([LærerStudenter, LærerStudenter], keys=[1, 2], names=['Kjønn']).reset_index()
NyeStudenter['AndelStudenterEtterAlder'] = NyeStudenter.apply(lambda row: row['Menn'] / row['Totalt'] if row['Kjønn'] == 1 else row['Kvinner'] / row['Totalt'], axis=1)

PopulasjonUtdannedeLærere = UtdannedeLærere.copy()
PopulasjonUtdannedeLærere["Årsverk"] = PopulasjonUtdannedeLærere.Antall * PopulasjonUtdannedeLærere.Sysselsettingsandel * PopulasjonUtdannedeLærere.GjennomsnitteligeÅrsverk
PopulasjonUtdannedeLærere.drop(['Sysselsatte', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'], axis=1, inplace=True)
PopulasjonUtdannedeLærere['År'] = Basisår

PopulasjonSysselsatteLærere = UtdannedeLærere.copy()
PopulasjonSysselsatteLærere.drop(['Antall', 'Sysselsatte'], axis=1, inplace=True)

LærerKandidaterTotalt = OpptatteLærerStudenter.merge(Gjennomføring, how='inner', on='Utdanning')

#Gjennomføring = pd.DataFrame({"År": range(2020, 2041), })
#print(Gjennomføring.to_string())
LærerKandidaterTotalt['Uteksaminerte'] = LærerKandidaterTotalt.apply(lambda row: (row['OpptatteStudenter'] * row['FullføringIgangværende'])
                                 if row['År'] + row['NormertTid'] <= Basisår + 3 else (row['OpptatteStudenter'] * row['FullføringNye']), axis=1)

NyeKandidater = NyeStudenter.merge(LærerKandidaterTotalt, how='inner', on=['Utdanning'])
NyeKandidater['Alder'] = NyeKandidater.Alder + NyeKandidater.NormertTid
NyeKandidater['UteksaminerteEtterAlder'] = NyeKandidater.Uteksaminerte * NyeKandidater.AndelStudenterEtterAlder

LærerVekst = PopulasjonUtdannedeLærere.copy()

PopulasjonForrigeÅr = PopulasjonUtdannedeLærere.copy()
PopulasjonForrigeÅr.Alder += 1

for x in range(Basisår + 1, Sluttår + 1):
    NyeLærere = NyeKandidater[NyeKandidater['År'] == x].copy()

    PopulasjonNesteÅr = PopulasjonForrigeÅr.merge(NyeLærere, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])
    PopulasjonNesteÅr.Antall = PopulasjonNesteÅr.Antall.fillna(0) + PopulasjonNesteÅr.UteksaminerteEtterAlder.fillna(0)
    PopulasjonNesteÅr['År'] = x

    LærerVekst = pd.concat([LærerVekst, PopulasjonNesteÅr[['Utdanning', 'Kjønn', 'Alder', 'Antall', 'Årsverk', 'År']]])

    PopulasjonForrigeÅr = LærerVekst[LærerVekst['År'] == x].copy()
    PopulasjonForrigeÅr.Alder += 1

Tilbud = LærerVekst.merge(PopulasjonSysselsatteLærere, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])
Tilbud['Tilbud'] = Tilbud.Antall * Tilbud.Sysselsettingsandel * Tilbud.GjennomsnitteligeÅrsverk
Tilbud = pd.concat([SysselsatteLærere.groupby(['Utdanning', 'År'], as_index=True).sum(), Tilbud.groupby(['Utdanning', 'År'], as_index=True).sum().query('År > @Basisår')])

# **********************
# Beregner Etterspørsel.
# **********************

Brukergruppe1 = pd.DataFrame({"TilAlder": [0, 2, 2, 3, 5, 5], "Alder": range(0, 6)})
Brukergruppe2 = pd.DataFrame({"TilAlder": [15] * 10, "Alder": range(6, 16)})
Brukergruppe3 = pd.DataFrame({"TilAlder": [15] * 16 + list(range(16, 25)) + [49] * 25, "Alder": range(0, 50)})
Brukergruppe4 = pd.DataFrame({"TilAlder": list(range(19, 30)) + [34] * 5 + [39] * 5 + [44] * 5 + [49] * 5, "Alder": range(19, 50)})
Brukergruppe5 = pd.DataFrame({"TilAlder": 99, "Alder": range(0, 100)})
Brukergruppe6 = pd.DataFrame({"TilAlder": 99, "Alder": range(0, 100)})

barn1 = pd.DataFrame({'FørsteÅr': barnhin.Alder0, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn2 = pd.DataFrame({'FørsteÅr': barnhin.Alder1 + barnhin.Alder2, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn3 = pd.DataFrame({'FørsteÅr': barnhin.Alder3, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn4 = pd.DataFrame({'FørsteÅr': barnhin.Alder4 + barnhin.Alder5, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})

DemografiGruppe1 = pd.DataFrame(columns=['FørsteÅr', 'FraAlder', 'TilAlder', 'Populasjon', 'Brukerindeks'])
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Bef.query('Alder == 0')[str(Basisår)].sum(), 0, 0, barn1.FørsteÅr.sum(), (2 * barn1.FørsteÅr.mul(barn1.Timer.values).sum()) / (barn1.FørsteÅr.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Bef.query('Alder >= 1 and Alder <= 2')[str(Basisår)].sum(), 1, 2, barn2.FørsteÅr.sum(), (2 * barn2.FørsteÅr.mul(barn2.Timer.values).sum()) / (barn2.FørsteÅr.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Bef.query('Alder == 3')[str(Basisår)].sum(), 3, 3, barn3.FørsteÅr.sum(), (1.5 * barn3.FørsteÅr.mul(barn3.Timer.values).sum()) / (barn3.FørsteÅr.sum() * 42.5)]
DemografiGruppe1.loc[len(DemografiGruppe1.index)] = [Bef.query('Alder >= 4 and Alder <= 5')[str(Basisår)].sum(), 4, 5, barn4.FørsteÅr.sum(), (1 * barn4.FørsteÅr.mul(barn4.Timer.values).sum()) / (barn4.FørsteÅr.sum() * 42.5)]
DemografiGruppe2 = pd.DataFrame({'FraAlder': 6, 'TilAlder': 15, 'Populasjon': Bef.query('Alder >= 6 and Alder <= 15')[str(Basisår)].sum(), 'Brukerindeks': 1.0}, index=[0])
DemografiGruppe5 = pd.DataFrame({'FraAlder': 0, 'TilAlder': 99, 'Populasjon': Bef[str(Basisår)].sum(), 'Brukerindeks': 1.0}, index=[0])
DemografiGruppe6 = pd.DataFrame({'FraAlder': 0, 'TilAlder': 99, 'Populasjon': Bef[str(Basisår)].sum(), 'Brukerindeks': 1.0}, index=[0])

for i in range(1, 7):
    locals()[f'Bef{i}'] = locals()[f'Brukergruppe{i}'].merge(Bef, how='inner', on='Alder').groupby(["TilAlder"]).sum()
     
    locals()[f'DemografiGruppe{i}'] = locals()[f'DemografiGruppe{i}'].set_index(["TilAlder"])
    locals()[f'DemografiGruppe{i}']["RelativeBrukere" + str(Basisår)] = locals()[f'DemografiGruppe{i}'].Populasjon * locals()[f'DemografiGruppe{i}'].Brukerindeks
    for x in range(Basisår + 1, Sluttår + 1):
        locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x)] = locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x-1)] * (locals()[f'Bef{i}'][str(x)] / locals()[f'Bef{i}'][str(x-1)])
        
    locals()[f'SumDemografiGruppe{i}'] = pd.DataFrame()
    for x in range(Basisår, Sluttår + 1):
        locals()[f'SumDemografiGruppe{i}']['SumRelativeBrukere' + str(x)] = [locals()[f'DemografiGruppe{i}']['RelativeBrukere' + str(x)].sum()]

    locals()[f'Demografiår{i}'] = pd.DataFrame({"År": [Basisår], "dm" + str(i): [1]})
    for x in range(Basisår + 1, Sluttår + 1):
        NesteÅrgang = pd.DataFrame({"År": x, "dm" + str(i): locals()[f'SumDemografiGruppe{i}']['SumRelativeBrukere' + str(x)] / locals()[f'SumDemografiGruppe{i}']['SumRelativeBrukere' + str(Basisår)]})
        locals()[f'Demografiår{i}'] = pd.concat([locals()[f'Demografiår{i}'], NesteÅrgang], ignore_index=True)
    
DemografiIndeks = Standardendring.merge(Demografiår1).merge(Demografiår2).merge(Demografiår3).merge(Demografiår4).merge(Demografiår5).merge(Demografiår6)
DemografiIndeks = pd.concat([DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks], keys=['ba', 'gr', 'lu', 'fa', 'yr', 'ph', 'py'], names=['Utdanning'])

EtterspørselLærere = pd.DataFrame({'Utdanning': ['ba', 'gr', 'lu', 'fa', 'yr', 'ph', 'py'], 'Etterspørsel': 0})
for i in range(1, 7):
    EtterspørselLærere["År"+str(i)] = SysselsatteLærere.Tilbud[SysselsatteLærere.Tilbud.index.get_level_values('Sektor') == i].reset_index(drop=True)

Etterspørsel = reduce(lambda left, right: pd.merge(left, right, on=['Utdanning'], how='outer'), [DemografiIndeks, EtterspørselLærere, VakanseEtterspørsel]).set_index(['Utdanning', 'År'])
for i in range(1, 7):
   Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel['År' + str(i)] + Etterspørsel['VakanseSektor' + str(i)]) * Etterspørsel['dm' + str(i)] * Etterspørsel['Sektor' + str(i)]

# *********************
# Beregner resultatene.
# *********************

TilbudOgEtterspørsel = Tilbud.merge(Etterspørsel, how='outer', on=['Utdanning', 'År'])
TilbudOgEtterspørsel['Differanse'] = TilbudOgEtterspørsel.Tilbud - TilbudOgEtterspørsel.Etterspørsel
TilbudOgEtterspørsel = TilbudOgEtterspørsel[['Tilbud', 'Etterspørsel', 'Differanse']]
TilbudOgEtterspørsel = TilbudOgEtterspørsel.sort_values(by=['Utdanning', 'År'], key=lambda x: x.map({'ba': 1, 'gr': 2, 'lu': 3, 'fa': 4, 'yr': 5, 'ph': 6, 'py': 7}))
TilbudOgEtterspørsel.rename(index={'ba': 'Barnehagelærere', 'gr': 'Grunnskolelærere', 'lu': 'Lektorutdannede', 'fa': 'Faglærere', 'yr': 'Yrkesfaglærere', 'ph': 'PPU', 'py': 'PPU Yrkesfag'}, inplace=True)

TilbudOgEtterspørsel.round(0).astype(int).to_csv("resultater/Lærermod.csv")
TilbudOgEtterspørsel.round(0).astype(int).to_excel("resultater/Lærermod.xlsx")
print(TilbudOgEtterspørsel.round(0).astype(int).to_string())

print()
print('Lærermod er nå ferdig. Velkommen tilbake.')
print()
