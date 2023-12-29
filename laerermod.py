import pandas as pd
from functools import reduce
import time

Basisår = 2020
Sluttår = 2040

befolkning = 'inndata/mmmm_2022.txt'

sysselsatte = 'inndata/sysselsatte.txt'
utdannede = 'inndata/utdannede.txt'
studenter = 'inndata/studenter.txt'
stkap = 'inndata/fullforingsgrader.txt'
oppta = 'inndata/opptak.txt'

dem1 = 'inndata/antall_barn_barnehager.txt'
dem3 = 'inndata/antall_elever_videregaende.txt'
dem4 = 'inndata/antall_studenter_hoyereutdanning.txt'

innpr = 'inndata/endring_standard.txt'
inplu = 'inndata/endring_timeverk.txt'
vakanse = 'inndata/vakanse.txt'

starttid = time.time()

print()
print('Velkommen til Python-versjonen av Lærermod!')
print()
print('/********************************************************************/')
print('/********************************************************************/')
print('/* Modellen LÆRERMOD beregner tilbud av og etterspørsel etter       */')
print('/* følgende 5 grupper av undervisningspersonell.                    */')
print('/*                                                                  */')
print('/* ba:Barnehagelærere    gr:Grunnskolelærere                        */')
print('/* fa:Faglærere          ph:PPU Universitet og høyskole             */')
print('/* py:PPU Yrkesfag                                                  */')
print('/********************************************************************/')
print('/********************************************************************/')
print()

# ***********************
# Innlesing av kildedata.
# ***********************

Bef = pd.DataFrame(pd.read_fwf(befolkning, index_col=['Alder', 'Kjønn']))

SysselsatteLærere = pd.DataFrame(pd.read_fwf(sysselsatte, index_col=['Utdanning', 'Sektor']))
UtdannedeLærere = pd.DataFrame(pd.read_fwf(utdannede))
LærerStudenter = pd.DataFrame(pd.read_fwf(studenter, index_col=['Utdanning']))
Gjennomføring = pd.DataFrame(pd.read_fwf(stkap))
OpptatteLærerStudenter = pd.DataFrame(pd.read_fwf(oppta))

barnhin = pd.DataFrame(pd.read_fwf(dem1))
demo3 = pd.DataFrame(pd.read_fwf(dem3))                  
demo4 = pd.DataFrame(pd.read_fwf(dem4))

Standardendring = pd.DataFrame(pd.read_fwf(innpr))
Timeverkendring = pd.DataFrame(pd.read_fwf(inplu))
VakanseEtterspørsel = pd.DataFrame(pd.read_fwf(vakanse))

# ********************************************************************
# Beregner Årsverk, Sysselsettingsandel og andeler for lærerstudenter.
# ********************************************************************

SysselsatteLærere['ÅrsverkTotalt'] = SysselsatteLærere.SysselsatteMenn * SysselsatteLærere.GjennomsnitteligeÅrsverkMenn + SysselsatteLærere.SysselsatteKvinner * SysselsatteLærere.GjennomsnitteligeÅrsverkKvinner

UtdannedeLærere['Sysselsettingsandel'] = UtdannedeLærere.apply(lambda row: row['Sysselsatte'] / row['Antall'] if row['Antall'] > 0 else 0, axis=1)

LærerStudenterTotalt = LærerStudenter.groupby(["Utdanning"]).sum()
LærerStudenterTotalt.rename(columns={"Alle": "Totalt"}, inplace=True)

LærerStudenter = LærerStudenter.merge(LærerStudenterTotalt['Totalt'], how='inner', on='Utdanning')

NyeStudenterMenn = LærerStudenter.copy()
NyeStudenterMenn['Kjønn'] = 1
NyeStudenterMenn['AndelStudenterEtterAlder'] = LærerStudenter.Menn / LærerStudenter.Totalt

NyeStudenterKvinner = LærerStudenter.copy()
NyeStudenterKvinner['Kjønn'] = 2
NyeStudenterKvinner['AndelStudenterEtterAlder'] = LærerStudenter.Kvinner / LærerStudenter.Totalt

NyeStudenter = pd.concat([NyeStudenterMenn, NyeStudenterKvinner]).reset_index()

PopulasjonUtdannedeLærere = UtdannedeLærere.copy()
PopulasjonUtdannedeLærere["Årsverk"] = PopulasjonUtdannedeLærere.Antall * PopulasjonUtdannedeLærere.Sysselsettingsandel * PopulasjonUtdannedeLærere.GjennomsnitteligeÅrsverk
PopulasjonUtdannedeLærere.drop(['Sysselsatte', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'], axis=1, inplace=True)

PopulasjonSysselsatteLærere = UtdannedeLærere.copy()
PopulasjonSysselsatteLærere.drop(['Antall', 'Sysselsatte'], axis=1, inplace=True)

EtterspørselLærere = pd.DataFrame({'Utdanning': ['ba', 'gr', 'fa', 'ph', 'py'], 'Etterspørsel': 0})
for i in range(1, 7):
    EtterspørselLærere["År"+str(i)] = SysselsatteLærere.ÅrsverkTotalt[SysselsatteLærere.ÅrsverkTotalt.index.get_level_values('Sektor') == i].reset_index(drop=True)

# ****************************
# Beregning av antall brukere.
# ****************************

ald1 = pd.DataFrame({"ald2": [0, 2, 2, 3, 5, 5], "Alder": range(0, 6)})
ald2 = pd.DataFrame({"ald2": [15] * 10, "Alder": range(6, 16)})
ald3 = pd.DataFrame({"ald2": [15] * 16 + list(range(16, 25)) + [99] * 75, "Alder": range(0, 100)})
ald4 = pd.DataFrame({"ald2": list(range(19, 30)) + [34] * 5 + [39] * 5 + [44] * 5 + [49] * 5, "Alder": range(19, 50)})
ald5 = pd.DataFrame({"ald2": 99, "Alder": range(0, 100)})
ald6 = pd.DataFrame({"ald2": 99, "Alder": range(0, 100)})

barn1 = pd.DataFrame({'FørsteÅr': barnhin.Alder0, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn2 = pd.DataFrame({'FørsteÅr': barnhin.Alder1 + barnhin.Alder2, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn3 = pd.DataFrame({'FørsteÅr': barnhin.Alder3, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn4 = pd.DataFrame({'FørsteÅr': barnhin.Alder4 + barnhin.Alder5, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})

demo1 = pd.DataFrame(columns=['FørsteÅr', 'ald1', 'ald2', 'Populasjon', 'Brukerindeks'])
demo1.loc[len(demo1.index)] = [Bef.query('Alder == 0').a2021.sum(), 0, 0, barn1.FørsteÅr.sum(), (2 * barn1.FørsteÅr.mul(barn1.Timer.values).sum()) / (barn1.FørsteÅr.sum() * 42.5)]
demo1.loc[len(demo1.index)] = [Bef.query('Alder >= 1 and Alder <= 2').a2021.sum(), 1, 2, barn2.FørsteÅr.sum(), (2 * barn2.FørsteÅr.mul(barn2.Timer.values).sum()) / (barn2.FørsteÅr.sum() * 42.5)]
demo1.loc[len(demo1.index)] = [Bef.query('Alder == 3').a2021.sum(), 3, 3, barn3.FørsteÅr.sum(), (1.5 * barn3.FørsteÅr.mul(barn3.Timer.values).sum()) / (barn3.FørsteÅr.sum() * 42.5)]
demo1.loc[len(demo1.index)] = [Bef.query('Alder >= 4 and Alder <= 5').a2021.sum(), 4, 5, barn4.FørsteÅr.sum(), (1 * barn4.FørsteÅr.mul(barn4.Timer.values).sum()) / (barn4.FørsteÅr.sum() * 42.5)]

demo1["ans1"] = demo1.Populasjon / demo1.FørsteÅr
demo1["ans2"] = 1.12 * demo1.ans1
demo1['ans2'] = demo1.apply(lambda row: 1.05 * row['ans1'] if row['ald1'] == 0 else row['ans2'], axis=1)
demo1['ans2'] = demo1.apply(lambda row: 0.97 if row['ans2'] > 0.95 else row['ans2'], axis=1)

demo2 = pd.DataFrame({'ald1': 6, 'ald2': 15, 'Populasjon': Bef.query('Alder >= 6 and Alder <= 15').a2021.sum(), 'Brukerindeks': 1.0}, index=[0])
demo5 = pd.DataFrame({'ald1': 0, 'ald2': 99, 'Populasjon': Bef.a2021.sum(), 'Brukerindeks': 1.0}, index=[0])
demo6 = pd.DataFrame({'ald1': 0, 'ald2': 99, 'Populasjon': Bef.a2021.sum(), 'Brukerindeks': 1.0}, index=[0])

# ********************************************************************************************
# LAGER ALDERSAGGREGATER av befolkningsfilen etter gruppering i den aktuelle etterspørselsfil.
# ********************************************************************************************
        
for i in range(1, 7):
    locals()[f'Bef{i}'] = locals()[f'ald{i}'].merge(Bef, how='inner', on='Alder').groupby(["ald2"]).sum()
     
    locals()[f'demo{i}'] = locals()[f'demo{i}'].set_index(['ald2'])
    locals()[f'demo{i}']["mg" + str(Basisår)] = locals()[f'demo{i}'].Populasjon * locals()[f'demo{i}'].Brukerindeks
    for x in range(Basisår + 1, Sluttår + 1):
        locals()[f'demo{i}']['mg' + str(x)] = locals()[f'demo{i}']['mg' + str(x-1)] * (locals()[f'Bef{i}']['a' + str(x)] / locals()[f'Bef{i}']['a' + str(x-1)])

    locals()[f'demos{i}'] = pd.DataFrame()
    for x in range(Basisår, Sluttår + 1):
        locals()[f'demos{i}']['mgs' + str(x)] = [locals()[f'demo{i}']['mg' + str(x)].sum()]
    
    locals()[f'demår{i}'] = pd.DataFrame({"År": [Basisår], "dm" + str(i): [1]})

    for x in range(Basisår + 1, Sluttår + 1):
        nyrad = pd.DataFrame({"År": x, "dm" + str(i): locals()[f'demos{i}']['mgs' + str(x)] / locals()[f'demos{i}']['mgs' + str(Basisår)]})
        locals()[f'demår{i}'] = pd.concat([locals()[f'demår{i}'], nyrad], ignore_index=True)
    
# **********************************************************************************************************************
# NYKAND: Beregner antall uteksaminerte studenter over sim.perioden, og fordeler de etter alder og kjønn (for hvert år).
# **********************************************************************************************************************

LærerKandidaterTotalt = OpptatteLærerStudenter.merge(Gjennomføring, how='inner', on='Utdanning')
LærerKandidaterTotalt['Uteksaminerte'] = LærerKandidaterTotalt.apply(lambda row: (row['OpptatteStudenter'] * row['FullføringIgangværende'])
                                 if row['År'] + row['NormertTid'] <= Basisår + 3 else (row['OpptatteStudenter'] * row['FullføringNye']), axis=1)

kand_ald = NyeStudenter.merge(LærerKandidaterTotalt, how='inner', on=['Utdanning'])
kand_ald['Alder'] = kand_ald.Alder + kand_ald.NormertTid
kand_ald['UteksaminerteEtterAlder'] = kand_ald.Uteksaminerte * kand_ald.AndelStudenterEtterAlder

# ********************************************************************************
# NYBEHOLD: Fører strømmen av nyutdannete inn i beholdningen og framskriver denne.
# ********************************************************************************

PopulasjonUtdannedeLærere['År'] = Basisår
beh_paar = PopulasjonUtdannedeLærere.copy()

PopulasjonForrigeÅr = PopulasjonUtdannedeLærere.copy()
PopulasjonForrigeÅr.Alder += 1

for x in range(Basisår + 1, Sluttår + 1):
    NyeLærere = kand_ald[kand_ald['År'] == x].copy()

    PopulasjonNesteÅr = PopulasjonForrigeÅr.merge(NyeLærere, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])
    PopulasjonNesteÅr['Antall'] = PopulasjonNesteÅr['Antall'].fillna(0)
    PopulasjonNesteÅr['UteksaminerteEtterAlder'] = PopulasjonNesteÅr['UteksaminerteEtterAlder'].fillna(0)
    PopulasjonNesteÅr.Antall = PopulasjonNesteÅr.Antall + PopulasjonNesteÅr.UteksaminerteEtterAlder
    PopulasjonNesteÅr['År'] = x

    beh_paar = pd.concat([beh_paar, PopulasjonNesteÅr[['Utdanning', 'Kjønn', 'Alder', 'Antall', 'Årsverk', 'År']]])

    PopulasjonForrigeÅr = beh_paar[beh_paar['År'] == x].copy()
    PopulasjonForrigeÅr.Alder += 1

# ************************************
# TILBUD: Beregner tilbudet av lærere.
# ************************************

Tilbud = beh_paar.merge(PopulasjonSysselsatteLærere, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])
Tilbud['Tilbud'] = Tilbud.Antall * Tilbud.Sysselsettingsandel * Tilbud.GjennomsnitteligeÅrsverk
Tilbud = Tilbud.groupby(['Utdanning', 'År'], sort=False).sum()

# ********************************
# Sluttproduktet fra simuleringen.
# ********************************

DemografiIndeks = Standardendring.merge(demår1).merge(demår2).merge(demår3).merge(demår4).merge(demår5).merge(demår6)
ind = pd.concat([DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks, DemografiIndeks], keys=['ba', 'gr', 'fa', 'ph', 'py'], names=['Utdanning'])

Etterspørsel = reduce(lambda left, right: pd.merge(left, right, on=['Utdanning'], how='outer'), [ind, EtterspørselLærere, VakanseEtterspørsel]).set_index(['Utdanning', 'År'])
for i in range(1, 7):
   Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel['År' + str(i)] + Etterspørsel['VakanseSektor' + str(i)]) * Etterspørsel['dm' + str(i)] * Etterspørsel['Sektor' + str(i)]

TilbudOgEtterspørsel = Tilbud.merge(Etterspørsel, how='outer', on=['Utdanning', 'År'])
TilbudOgEtterspørsel['Differanse'] = TilbudOgEtterspørsel.Tilbud - TilbudOgEtterspørsel.Etterspørsel
TilbudOgEtterspørsel = TilbudOgEtterspørsel[['Etterspørsel', 'Tilbud', 'Differanse']]

TilbudOgEtterspørsel.rename(index={'ba': 'Barnehagelærere', 'gr': 'Grunnskolelærere', 'fa': 'Faglærere', 'ph': 'PPU Universitet og høyskole', 'py': 'PPU Yrkesfag'}, inplace=True)

pd.options.display.multi_sparse = False

TilbudOgEtterspørsel.round(0).astype(int).to_csv("resultater/Lærermod.csv")
TilbudOgEtterspørsel.round(0).astype(int).to_excel("resultater/Lærermod.xlsx")
print(TilbudOgEtterspørsel.round(0).astype(int).to_string())

print()
print('Lærermod er nå ferdig.')
print()
print(f'Og det tok {(time.time() - starttid):.2f} sekunder. Velkommen tilbake.')
print()
