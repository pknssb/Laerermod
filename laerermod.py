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

# ****************************************************************************
# Innlesing av befolkningen til og med sluttåret fordelt etter alder og kjønn.
# ****************************************************************************

bef = pd.DataFrame(pd.read_fwf(befolkning, index_col=['Alder', 'Kjønn']))

SysselsatteLærere = pd.DataFrame(pd.read_fwf(sysselsatte, index_col=['Utdanning', 'Sektor']))
UtdannedeLærere = pd.DataFrame(pd.read_fwf(utdannede))
LærerStudenter = pd.DataFrame(pd.read_fwf(studenter, index_col=['Utdanning']))
Gjennomføring = pd.DataFrame(pd.read_fwf(stkap))
OpptatteLærerStudenter = pd.DataFrame(pd.read_fwf(oppta))

barnhin = pd.DataFrame(pd.read_fwf(dem1))
demo3 = pd.DataFrame(pd.read_fwf(dem3))                  
demo4 = pd.DataFrame(pd.read_fwf(dem4))

Standardendring = pd.DataFrame(pd.read_fwf(innpr))
plussakt = pd.DataFrame(pd.read_fwf(inplu))
VakanseEtterspørsel = pd.DataFrame(pd.read_fwf(vakanse))

# ***********************
# Beregner Årsverk totalt
# ***********************

SysselsatteLærere['ÅrsverkTotalt'] = SysselsatteLærere.SysselsatteMenn * SysselsatteLærere.GjennomsnitteligeÅrsverkMenn + SysselsatteLærere.SysselsatteKvinner * SysselsatteLærere.GjennomsnitteligeÅrsverkKvinner

# ****************************
# Beregner Sysselsettingsandel
# ****************************

UtdannedeLærere['Sysselsettingsandel'] = UtdannedeLærere.apply(lambda row: row['Sysselsatte'] / row['Antall']
                                                                           if row['Antall'] > 0
                                                                           else 0, axis=1)

# ************************************************
# Oppretter LærerStudenterTotalt og LærerStudenter
# ************************************************

LærerStudenterTotalt = LærerStudenter.groupby(["Utdanning"]).sum()
LærerStudenterTotalt.rename(columns={"Alle": "Totalt"}, inplace=True)

LærerStudenter = LærerStudenter.merge(LærerStudenterTotalt['Totalt'], how='inner', on='Utdanning')

NyeStudenterMenn = LærerStudenter.copy()
NyeStudenterMenn['Kjønn'] = 1
NyeStudenterMenn['AndelStudenterEtterAlder'] = LærerStudenter.Menn / LærerStudenter.Totalt

NyeStudenterKvinner = LærerStudenter.copy()
NyeStudenterKvinner['Kjønn'] = 2
NyeStudenterKvinner['AndelStudenterEtterAlder'] = LærerStudenter.Kvinner / LærerStudenter.Totalt

NyeStudenter = pd.concat([NyeStudenterMenn, NyeStudenterKvinner])
NyeStudenter = NyeStudenter.reset_index()

# ************************************
# Beregning av antall barn i barnehage
# ************************************

barn1 = pd.DataFrame({'b2021': barnhin.Alder0, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn2 = pd.DataFrame({'b2021': barnhin.Alder1 + barnhin.Alder2, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn3 = pd.DataFrame({'b2021': barnhin.Alder3, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})
barn4 = pd.DataFrame({'b2021': barnhin.Alder4 + barnhin.Alder5, 'Timer': barnhin.TimerMin + ((barnhin.TimerMax - barnhin.TimerMin) / 2)})

# ************************************
# Oppretter noen oppsummeringstabeller
# ************************************

befs1 = pd.DataFrame({'agr2020': bef.query('Alder == 0').a2020.sum(),
                      'agr2021': bef.query('Alder == 0').a2021.sum(),
                      'ald1': 0,
                      'ald2': 0,
                      'Populasjon': barn1.b2021.sum(),
                      'Brukerindeks': (2 * barn1.b2021.mul(barn1.Timer.values).sum()) /
                                      (barn1.b2021.sum() * 42.5)}, index=[0])

befs2 = pd.DataFrame({'agr2020': bef.query('Alder >= 1 and Alder <= 2').a2020.sum(),
                      'agr2021': bef.query('Alder >= 1 and Alder <= 2').a2021.sum(),
                      'ald1': 1,
                      'ald2': 2,
                      'Populasjon': barn2.b2021.sum(),
                      'Brukerindeks': (2 * barn2.b2021.mul(barn2.Timer.values).sum()) /
                                      (barn2.b2021.sum() * 42.5)}, index=[0])

befs3 = pd.DataFrame({'agr2020': bef.query('Alder == 3').a2020.sum(),
                      'agr2021': bef.query('Alder == 3').a2021.sum(),
                      'ald1': 3,
                      'ald2': 3,
                      'Populasjon': barn3.b2021.sum(),
                      'Brukerindeks': (1.5 * barn3.b2021.mul(barn3.Timer.values).sum()) /
                                      (barn3.b2021.sum() * 42.5)}, index=[0])

befs4 = pd.DataFrame({'agr2020': bef.query('Alder >= 4 and Alder <= 5').a2020.sum(),
                      'agr2021': bef.query('Alder >= 4 and Alder <= 5').a2021.sum(),
                      'ald1': 4,
                      'ald2': 5,
                      'Populasjon': barn4.b2021.sum(),
                      'Brukerindeks': (1 * barn4.b2021.mul(barn4.Timer.values).sum()) /
                                      (barn4.b2021.sum() * 42.5)}, index=[0])

# ********************
# Slår sammen tabeller
# ********************

demo1 = pd.concat([befs1, befs2, befs3, befs4], ignore_index=True)

demo1["ans1"] = demo1.Populasjon / demo1.agr2021

demo1["ans2"] = 1.12 * demo1.ans1
demo1['ans2'] = demo1.apply(lambda row: 1.05 * row['ans1'] if row['ald1'] == 0 else row['ans2'], axis=1)
demo1['ans2'] = demo1.apply(lambda row: 0.97 if row['ans2'] > 0.95 else row['ans2'], axis=1)

# ******************************************************
# Innlesing av folkemengden i grunnskole og andre skoler
# ******************************************************

PopulasjonUtdannedeLærere = UtdannedeLærere.copy()

PopulasjonUtdannedeLærere["Årsverk"] = PopulasjonUtdannedeLærere.Antall * PopulasjonUtdannedeLærere.Sysselsettingsandel * PopulasjonUtdannedeLærere.GjennomsnitteligeÅrsverk

PopulasjonUtdannedeLærere.drop(['Sysselsatte', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'], axis=1, inplace=True)

beh_syss = UtdannedeLærere.copy()
beh_syss.drop(['Antall', 'Sysselsatte'], axis=1, inplace=True)

EtterspørselLærere = pd.DataFrame({'Utdanning': ['ba', 'gr', 'fa', 'ph', 'py']})

for i in range(1, 7):
    EtterspørselLærere["År"+str(i)] = SysselsatteLærere.ÅrsverkTotalt[SysselsatteLærere.ÅrsverkTotalt.index.get_level_values('Sektor') == i].reset_index(drop=True)

# ****************************************
# Oppretter datasett for senere utfylling.
# ****************************************

ald1 = pd.DataFrame({"ald2": [0, 2, 2, 3, 5, 5],
                     "Alder": [0, 1, 2, 3, 4, 5]})

ald2 = pd.DataFrame({"ald2": [15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
                     "Alder": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]})

ald3 = pd.DataFrame(columns=['ald2', 'Alder'])

for x in range(0, 16):
    ald3.loc[len(ald3)] = {'ald2': 15, 'Alder': x}

for x in range(16, 25):
    ald3.loc[len(ald3)] = {'ald2': x, 'Alder': x}

for x in range(25, 100):
    ald3.loc[len(ald3)] = {'ald2': 99, 'Alder': x}

ald4 = pd.DataFrame({"ald2": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 34, 34, 34, 34, 34, 39, 39, 39, 39, 39, 44, 44, 44, 44, 44, 49, 49, 49, 49, 49],
                     "Alder": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]})

ald5 = pd.DataFrame(columns=['ald2', 'Alder'])
ald6 = pd.DataFrame(columns=['ald2', 'Alder'])

for x in range(0, 100):
    ald5.loc[len(ald5)] = {'ald2': 99, 'Alder': x}
    ald6.loc[len(ald6)] = {'ald2': 99, 'Alder': x}    

demo2 = pd.DataFrame({'ald1': 6,
                      'ald2': 15,
                      'Populasjon': bef.query('Alder >= 6 and Alder <= 15').a2021.sum(),
                      'Brukerindeks': 1.0}, index=[0])

demo5 = pd.DataFrame({'ald1': 0,
                      'ald2': 99,
                      'Populasjon': bef.a2021.sum(),
                      'Brukerindeks': 1.0}, index=[0])

demo6 = pd.DataFrame({'ald1': 0,
                      'ald2': 99,
                      'Populasjon': bef.a2021.sum(),
                      'Brukerindeks': 1.0}, index=[0])

# ************************************************
# LAGER ALDERSAGGREGATER av befolkningsfilen etter
# gruppering i den aktuelle etterspørselsfil
# ************************************************
        
for i in range(1, 7):
    locals()[f'bef{i}'] = locals()[f'ald{i}'].merge(bef, how='inner', on='Alder').groupby(["ald2"]).sum()
    
    locals()[f'demo{i}'] = locals()[f'demo{i}'].set_index(['ald2'])

    for x in range(Basisår, Sluttår + 1):
        locals()[f'demo{i}']['agr' + str(x)] = locals()[f'bef{i}']['a' + str(x)]

    locals()[f'demo{i}']["pg" + str(Basisår)] = locals()[f'demo{i}'].Populasjon * locals()[f'demo{i}'].Brukerindeks

    for x in range(Basisår + 1, Sluttår + 1):
        locals()[f'demo{i}']['pg' + str(x)] = locals()[f'demo{i}']['pg' + str(x-1)] * (locals()[f'bef{i}']['a' + str(x)] /
                                                         locals()[f'bef{i}']['a' + str(x-1)])

    locals()[f'demo{i}']["mg" + str(Basisår)] = locals()[f'demo{i}'].Populasjon * locals()[f'demo{i}'].Brukerindeks

    for x in range(Basisår + 1, Sluttår + 1):
        locals()[f'demo{i}']['mg' + str(x)] = locals()[f'demo{i}']['mg' + str(x-1)] * (locals()[f'bef{i}']['a' + str(x)] /
                                                                                       locals()[f'bef{i}']['a' + str(x-1)])

    locals()[f'demos{i}'] = pd.DataFrame()
    
    for x in range(Basisår, Sluttår + 1):
        locals()[f'demos{i}']['agrs' + str(x)] = [locals()[f'demo{i}']['agr' + str(x)].sum()]
        locals()[f'demos{i}']['pgs' + str(x)] = [locals()[f'demo{i}']['pg' + str(x)].sum()]
        locals()[f'demos{i}']['mgs' + str(x)] = [locals()[f'demo{i}']['mg' + str(x)].sum()]
    
    y = locals()[f'demos{i}']['pgs' + str(Basisår)].loc[0]
    """
    locals()[f'demy{i}'] = pd.DataFrame({'Utdanning': ['ba', 'gr', 'fa', 'ph', 'py'],
                                         'Brukerindeks': [y, y, y, y, y]})

    locals()[f'Årsverk{i}'] = locals()[f'demy{i}']
    
    locals()[f'Årsverk{i}']['År'] = EtterspørselLærere['År' + str(i)]
    locals()[f'Årsverk{i}']['stdrd'] = locals()[f'Årsverk{i}']['År'] / locals()[f'Årsverk{i}']['Brukerindeks']
    """
    locals()[f'demår{i}'] = pd.DataFrame({"År": [Basisår], "dm" + str(i): [1], "dp" + str(i): [1], "dem" + str(i): locals()[f'demos{i}']['agrs' + str(Basisår)]})

    for x in range(Basisår + 1, Sluttår + 1):
        nyrad = pd.DataFrame({"År": x,
                              "dm" + str(i): locals()[f'demos{i}']['mgs' + str(x)] / locals()[f'demos{i}']['mgs' + str(Basisår)],
                              "dp" + str(i): (locals()[f'demos{i}']['pgs' + str(x)] / locals()[f'demos{i}']['pgs' + str(Basisår)]) /
                                     (locals()[f'demos{i}']['mgs' + str(x)] / locals()[f'demos{i}']['mgs' + str(Basisår)]),
                              "dem" + str(i): locals()[f'demos{i}']['agrs' + str(x)]})
        locals()[f'demår{i}'] = pd.concat([locals()[f'demår{i}'], nyrad], ignore_index=True)
    
# ******************************************************
# Lager indeks for demografikomponenten i etterspørselen
# etter tjenester
# ******************************************************

dmindeks = Standardendring.merge(demår1).merge(demår2).merge(demår3).merge(demår4).merge(demår5).merge(demår6)

#Årsverk = pd.concat([Årsverk1, Årsverk2, Årsverk3, Årsverk4, Årsverk5, Årsverk6])

# ******************************************************************
# NYKAND: Beregner antall uteksaminerte studenter over sim.perioden.
# Disse fordeles så etter alder og kjønn (for hvert år).
# ******************************************************************

LærerKandidaterTotalt = OpptatteLærerStudenter.merge(Gjennomføring, how='inner', on='Utdanning')

LærerKandidaterTotalt['Uteksaminerte'] = LærerKandidaterTotalt.apply(lambda row: (row['OpptatteStudenter'] * row['FullføringIgangværende'])
                                 if row['År'] + row['NormertTid'] <= Basisår + 3
                                 else (row['OpptatteStudenter'] * row['FullføringNye']), axis=1)

kand_ald = NyeStudenter.merge(LærerKandidaterTotalt, how='inner', on=['Utdanning'])

kand_ald["Alder"] = kand_ald.Alder + kand_ald.NormertTid
kand_ald["UteksaminerteEtterAlder"] = kand_ald.Uteksaminerte * kand_ald.AndelStudenterEtterAlder

# *************************************************************
# NYBEHOLD: Fører strømmen av nyutdannete inn i beholdningen av
#           en yrkesgruppe, og framskriver beholdningen av fag-
#           utdannete over simuleringsperioden.
# *************************************************************

PopulasjonUtdannedeLærere['År'] = Basisår
beh_paar = PopulasjonUtdannedeLærere.copy()

forrige_år = PopulasjonUtdannedeLærere.copy()
forrige_år.Alder += 1

kand_år = kand_ald
kand_år = kand_år[kand_år['År'] == Basisår + 1]

neste_år = forrige_år.merge(kand_år, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])
neste_år['Antall'] = neste_år['Antall'].fillna(0)
neste_år['UteksaminerteEtterAlder'] = neste_år['UteksaminerteEtterAlder'].fillna(0)

neste_år.Antall = neste_år.Antall + neste_år.UteksaminerteEtterAlder
neste_år['År'] = Basisår + 1

slutt = neste_år[['Utdanning', 'Kjønn', 'Alder', 'Antall', 'Årsverk', 'År']]

beh_paar = pd.concat([beh_paar, slutt])

for x in range(Basisår + 2, Sluttår + 1):
    forrige_år = beh_paar.copy()
    forrige_år = forrige_år[forrige_år['År'] == x-1]
    forrige_år.Alder += 1

    kand_år = kand_ald
    kand_år = kand_år[kand_år['År'] == x]

    neste_år = forrige_år.merge(kand_år, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])

    neste_år['Antall'] = neste_år['Antall'].fillna(0)
    neste_år['UteksaminerteEtterAlder'] = neste_år['UteksaminerteEtterAlder'].fillna(0)

    neste_år.Antall = neste_år.Antall + neste_år.UteksaminerteEtterAlder
    neste_år['År'] = x

    slutt = neste_år[['Utdanning', 'Kjønn', 'Alder', 'Antall', 'Årsverk', 'År']]

    beh_paar = pd.concat([beh_paar, slutt])

# ************************************************************
# TILBUD: Beregner
#         årsverkstilbudet ut fra mønsteret i yrkesdeltakelsen
#         og eventuell eksogen økning i yrkesdeltakelsen.
# ************************************************************

Tilbud = beh_paar.merge(beh_syss, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])
Tilbud['Tilbud'] = Tilbud.Antall * Tilbud.Sysselsettingsandel * Tilbud.GjennomsnitteligeÅrsverk
Tilbud = Tilbud.groupby(['Utdanning', 'År'], sort=False).sum()
Tilbud = Tilbud.drop(['Kjønn', 'Alder', 'Antall', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'], axis=1)

# ********************************
# Sluttproduktet fra simuleringen.
# ********************************

dmindeks['Utdanning'] = 'ba'
ind1 = dmindeks.copy()
dmindeks['Utdanning'] = 'gr'
ind2 = dmindeks.copy()
dmindeks['Utdanning'] = 'fa'
ind3 = dmindeks.copy()
dmindeks['Utdanning'] = 'ph'
ind4 = dmindeks.copy()
dmindeks['Utdanning'] = 'py'
ind5 = dmindeks.copy()

ind = pd.concat([ind1, ind2, ind3, ind4, ind5])
ind = ind.reset_index()

Etterspørsel = reduce(lambda left, right: pd.merge(left, right, on=['Utdanning'], how='outer'), [ind, EtterspørselLærere, VakanseEtterspørsel])

Etterspørsel = Etterspørsel.set_index(['Utdanning', 'År'])

Etterspørsel['Etterspørsel'] = (Etterspørsel.År1 + Etterspørsel.VakanseSektor1) * Etterspørsel.dm1 * Etterspørsel.Sektor1
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År2 + Etterspørsel.VakanseSektor2) * Etterspørsel.dm2 * Etterspørsel.Sektor2
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År3 + Etterspørsel.VakanseSektor3) * Etterspørsel.dm3 * Etterspørsel.Sektor3
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År4 + Etterspørsel.VakanseSektor4) * Etterspørsel.dm4 * Etterspørsel.Sektor4
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År5 + Etterspørsel.VakanseSektor5) * Etterspørsel.dm5 * Etterspørsel.Sektor5
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År6 + Etterspørsel.VakanseSektor6) * Etterspørsel.dm6 * Etterspørsel.Sektor6

TilbudOgEtterspørsel = Tilbud.merge(Etterspørsel, how='outer', on=['Utdanning', 'År'])

TilbudOgEtterspørsel['Differanse'] = TilbudOgEtterspørsel.Tilbud - TilbudOgEtterspørsel.Etterspørsel

TilbudOgEtterspørsel = TilbudOgEtterspørsel[['Etterspørsel', 'Tilbud', 'Differanse']]
TilbudOgEtterspørsel.index.names = ['Utdanning', 'År']

TilbudOgEtterspørsel.rename(index={'ba': 'Barnehagelærere'}, inplace=True)
TilbudOgEtterspørsel.rename(index={'gr': 'Grunnskolelærere'}, inplace=True)
TilbudOgEtterspørsel.rename(index={'fa': 'Faglærere'}, inplace=True)
TilbudOgEtterspørsel.rename(index={'ph': 'PPU Universitet og høyskole'}, inplace=True)
TilbudOgEtterspørsel.rename(index={'py': 'PPU Yrkesfag'}, inplace=True)

pd.options.display.multi_sparse = False

TilbudOgEtterspørsel.round(0).astype(int).to_csv("resultater/Lærermod.csv")
TilbudOgEtterspørsel.round(0).astype(int).to_excel("resultater/Lærermod.xlsx")

print(TilbudOgEtterspørsel.round(0).astype(int).to_string())

totaltid = time.time() - starttid

print()
print('Lærermod er nå ferdig.')
print()
print(f'Og det tok {totaltid:.2f} sekunder. Velkommen tilbake.')
print()
