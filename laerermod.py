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
vak = 'inndata/vakanse.txt'


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

kolonnenavn = ["Alder"] + ["Kjønn"]
for x in range(Basisår, Sluttår+1):
    kolonnenavn = kolonnenavn + ["a" + str(x)]

bef = pd.DataFrame(pd.read_fwf(befolkning,
                   header=None,
                   delimiter=" "))

bef.columns = kolonnenavn
bef.set_index(['Alder', 'Kjønn'])

# ********************************
# Innlesing av sysselsatte lærere.
# ********************************

SysselsatteLærere = pd.DataFrame(pd.read_csv(
                                 sysselsatte,
                                 header=None,
                                 delimiter=r"\s+",
                                 names=['Utdanning',
                                        'Sektor',
                                        'SysselsatteMenn',
                                        'SysselsatteKvinner',
                                        'GjennomsnitteligeÅrsverkMenn',
                                        'GjennomsnitteligeÅrsverkKvinner'],
                                 usecols=list(range(6)),
                                 dtype={'Utdanning': 'string',
                                        'Sektor': 'int',
                                        'SysselsatteMenn': 'int',
                                        'SysselsatteKvinner': 'int',
                                        'GjennomsnitteligeÅrsverkMenn': 'float',
                                        'GjennomsnitteligeÅrsverkKvinner': 'float'}))

SysselsatteLærere = SysselsatteLærere.set_index(['Utdanning', 'Sektor'])

# ******************************
# Innlesing av utdannede lærere.
# ******************************

UtdannedeLærere = pd.DataFrame(pd.read_csv(
                              utdannede,
                              header=None,
                              delimiter=r"\s+",
                              na_values={'.', ' .'},
                              names=['Utdanning',
                                     'Kjønn',
                                     'Alder',
                                     'Populasjon',
                                     'Sysselsatte',
                                     'GjennomsnitteligeÅrsverk'],
                              usecols=list(range(6)),
                              dtype={'Utdanning': 'string',
                                     'Kjønn': 'int',
                                     'Alder': 'int',
                                     'Populasjon': 'int',
                                     'Sysselsatte': 'int',
                                     'GjennomsnitteligeÅrsverk': 'float'}))

UtdannedeLærere['Sysselsettingsandel'] = UtdannedeLærere.apply(lambda row: row['Sysselsatte'] / row['Populasjon']
                                                                           if row['Populasjon'] > 0
                                                                           else 0, axis=1)

# ***************************
# Innlesing av lærerstudenter
# ***************************

LærerStudenter = pd.DataFrame(pd.read_csv(studenter,
                        header=None,
                        delimiter=r"\s+",
                        na_values={'.', ' .'},
                        names=['Utdanning',
                               'Alder',
                               'Alle',
                               'Menn',
                               'Kvinner'],
                        usecols=list(range(5)),
                        dtype={'Utdanning': 'string',
                               'Alder': 'int',
                               'Alle': 'int',
                               'Menn': 'int',
                               'Kvinner': 'int'}))

LærerStudenter = LærerStudenter.set_index(['Utdanning'])

# ***********************
# Beregner Årsverk totalt
# ***********************

SysselsatteLærere['ÅrsverkTotalt'] = SysselsatteLærere.SysselsatteMenn * SysselsatteLærere.GjennomsnitteligeÅrsverkMenn + SysselsatteLærere.SysselsatteKvinner * SysselsatteLærere.GjennomsnitteligeÅrsverkKvinner

# ************************************************
# Oppretter LærerStudenterTotalt og LærerStudenter
# ************************************************

LærerStudenterTotalt = pd.DataFrame(LærerStudenter.groupby(["Utdanning"]).sum())
LærerStudenterTotalt.rename(columns={"Alle": "totalt"}, inplace=True)
LærerStudenterTotalt.drop(['Alder', 'Kvinner', 'Menn'], axis=1, inplace=True)

LærerStudenter = LærerStudenter.merge(LærerStudenterTotalt, how='outer', on='Utdanning')
LærerStudenter.Menn = LærerStudenter.Menn / LærerStudenter.totalt
LærerStudenter.Kvinner = LærerStudenter.Kvinner / LærerStudenter.totalt
LærerStudenter = LærerStudenter.reset_index()

# ************************************
# Innlesing av antall barn i barnehage
# ************************************

barnhin = pd.DataFrame(pd.read_csv(dem1,
                      header=None,
                      delimiter=" ",
                      names=['År', 'TimerMin', 'TinerMax', 'Alder0', 'Alder1', 'Alder2', 'Alder3', 'Alder4', 'Alder5'],
                      usecols=list(range(9))))

barn1 = pd.DataFrame()
barn1["b2021"] = barnhin.Alder0
barn1["tim"] = barnhin.TimerMin + ((barnhin.TinerMax - barnhin.TimerMin) / 2)

barn2 = pd.DataFrame()
barn2["b2021"] = barnhin.Alder1 + barnhin.Alder2
barn2["tim"] = barnhin.TimerMin + ((barnhin.TinerMax - barnhin.TimerMin) / 2)

barn3 = pd.DataFrame()
barn3["b2021"] = barnhin.Alder3
barn3["tim"] = barnhin.TimerMin + ((barnhin.TinerMax - barnhin.TimerMin) / 2)

barn4 = pd.DataFrame()
barn4["b2021"] = barnhin.Alder4 + barnhin.Alder5
barn4["tim"] = barnhin.TimerMin + ((barnhin.TinerMax - barnhin.TimerMin) / 2)

# ************************************
# Oppretter noen oppsummeringstabeller
# ************************************

befs1 = pd.DataFrame({'agr2020': bef.query('Alder == 0').a2020.sum(),
                      'agr2021': bef.query('Alder == 0').a2021.sum(),
                      'ald1': 0,
                      'ald2': 0}, index=[0])

befs2 = pd.DataFrame({'agr2020': bef.query('Alder >= 1 and Alder <= 2').a2020.sum(),
                      'agr2021': bef.query('Alder >= 1 and Alder <= 2').a2021.sum(),
                      'ald1': 1,
                      'ald2': 2}, index=[0])

befs3 = pd.DataFrame({'agr2020': bef.query('Alder == 3').a2020.sum(),
                      'agr2021': bef.query('Alder == 3').a2021.sum(),
                      'ald1': 3,
                      'ald2': 3}, index=[0])

befs4 = pd.DataFrame({'agr2020': bef.query('Alder >= 4 and Alder <= 5').a2020.sum(),
                      'agr2021': bef.query('Alder >= 4 and Alder <= 5').a2021.sum(),
                      'ald1': 4,
                      'ald2': 5}, index=[0])

barna1 = pd.DataFrame({'ald1': 0,
                       'ald2': 0,
                       'br': barn1.b2021.sum(),
                       'bri': (2 * barn1.b2021.mul(barn1.tim.values).sum()) /
                              (barn1.b2021.sum() * 42.5)}, index=[0])

barna2 = pd.DataFrame({'ald1': 1,
                       'ald2': 2,
                       'br': barn2.b2021.sum(),
                       'bri': (2 * barn2.b2021.mul(barn2.tim.values).sum()) /
                              (barn2.b2021.sum() * 42.5)}, index=[0])

barna3 = pd.DataFrame({'ald1': 3,
                       'ald2': 3,
                       'br': barn3.b2021.sum(),
                       'bri': (1.5 * barn3.b2021.mul(barn3.tim.values).sum()) /
                              (barn3.b2021.sum() * 42.5)}, index=[0])

barna4 = pd.DataFrame({'ald1': 4,
                       'ald2': 5,
                       'br': barn4.b2021.sum(),
                       'bri': (1 * barn4.b2021.mul(barn4.tim.values).sum()) /
                              (barn4.b2021.sum() * 42.5)}, index=[0])

# ********************
# Slår sammen tabeller
# ********************

barnr = pd.concat([befs1, befs2, befs3, befs4], ignore_index=True)
barnar = pd.concat([barna1, barna2, barna3, barna4], ignore_index=True)

barnr["br"] = barnar.br
barnr["bri"] = barnar.bri

barnr["ans1"] = barnr.br / barnr.agr2021
barnr["ans2"] = 1.12 * barnr.ans1

barnr['ans2'] = barnr.apply(lambda row: 1.05 * row['ans1']
                            if row['ald1'] == 0
                            else row['ans2'], axis=1)

barnr['ans2'] = barnr.apply(lambda row: 0.97
                            if row['ans2'] > 0.95
                            else row['ans2'], axis=1)

# ******************************************************
# Innlesing av folkemengden i grunnskole og andre skoler
# ******************************************************

Gjennomføring = pd.DataFrame(pd.read_fwf(stkap,
                     header=None,
                     delimiter=" ",
                     names=["Utdanning", "NormertTid", "fullfor", "fullfob"]))

OpptatteLærerStudenter = pd.DataFrame(pd.read_fwf(oppta,
                     header=None,
                     delimiter=" ",
                     names=["År", "Utdanning", "OpptatteStudenter"]))

plussakt = pd.DataFrame(pd.read_fwf(inplu,
                       header=None,
                       delimiter=" ",
                       names=["Alder", "plussm", "plussk"]))

nystud1 = LærerStudenter.copy()
nystud1['Kjønn'] = 1
nystud1['st_ald'] = nystud1.Menn

nystud2 = LærerStudenter.copy()
nystud2['Kjønn'] = 2
nystud2['st_ald'] = nystud2.Kvinner

nystud = pd.concat([nystud1, nystud2])

PopulasjonUtdannedeLærere = UtdannedeLærere.copy()

PopulasjonUtdannedeLærere["Årsverk"] = PopulasjonUtdannedeLærere.Populasjon * PopulasjonUtdannedeLærere.Sysselsettingsandel * PopulasjonUtdannedeLærere.GjennomsnitteligeÅrsverk

PopulasjonUtdannedeLærere.drop(['Sysselsatte', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'], axis=1, inplace=True)

beh_syss = UtdannedeLærere.copy()

beh_syss.drop(['Populasjon', 'Sysselsatte'], axis=1, inplace=True)

EtterspørselLærere = pd.DataFrame({'Utdanning': ['ba', 'gr', 'fa', 'ph', 'py']})

for i in range(1, 7):
    EtterspørselLærere["År"+str(i)] = SysselsatteLærere.ÅrsverkTotalt[SysselsatteLærere.ÅrsverkTotalt.index.get_level_values('Sektor') == i].reset_index(drop=True)

vakesp = pd.DataFrame(pd.read_fwf(vak,
                     header=None,
                     delimiter=" ",
                     names=["Utdanning", "vak1", "vak2", "vak3", "vak4", "vak5", "vak6"]))

# ********************************************************
# PROSENTVIS ENDRING I ANTALL ELEVER pr. 1000 INNBYGGERE
# ved de ulike aktivitetsområdene over simuleringsperioden
# tallet 1.01 tolkes som 1 prosent økt elevtall pr. 1000
# ********************************************************

stand = pd.DataFrame(pd.read_fwf(innpr,
                    header=None,
                    delimiter=" ",
                    names=["År", "Sektor1", "Sektor2", "Sektor3", "Sektor4", "Sektor5", "Sektor6"]))

stand = stand[stand['År'] >= Basisår]
stand = stand[stand['År'] <= Sluttår]

# ****************************************
# Oppretter datasett for senere utfylling.
# ****************************************

ald1 = pd.DataFrame(columns=['ald2', 'Alder'])

for x in range(0, 1):
    nyrad = {'ald2': 0, 'Alder': x}
    ald1.loc[len(ald1)] = nyrad

for x in range(1, 3):
    nyrad = {'ald2': 2, 'Alder': x}
    ald1.loc[len(ald1)] = nyrad

for x in range(3, 4):
    nyrad = {'ald2': 3, 'Alder': x}
    ald1.loc[len(ald1)] = nyrad

for x in range(4, 6):
    nyrad = {'ald2': 5, 'Alder': x}
    ald1.loc[len(ald1)] = nyrad

ald2 = pd.DataFrame(columns=['ald2', 'Alder'])

for x in range(6, 16):
    nyrad = {'ald2': 15, 'Alder': x}
    ald2.loc[len(ald2)] = nyrad

ald3 = pd.DataFrame(columns=['ald2', 'Alder'])

for x in range(0, 16):
    nyrad = {'ald2': 15, 'Alder': x}
    ald3.loc[len(ald3)] = nyrad

for x in range(16, 25):
    nyrad = {'ald2': x, 'Alder': x}
    ald3.loc[len(ald3)] = nyrad

for x in range(25, 100):
    nyrad = {'ald2': 99, 'Alder': x}
    ald3.loc[len(ald3)] = nyrad

ald4 = pd.DataFrame(columns=['ald2', 'Alder'])

for x in range(19, 30):
    nyrad = {'ald2': x, 'Alder': x}
    ald4.loc[len(ald4)] = nyrad

for x in range(30, 35):
    nyrad = {'ald2': 34, 'Alder': x}
    ald4.loc[len(ald4)] = nyrad

for x in range(35, 40):
    nyrad = {'ald2': 39, 'Alder': x}
    ald4.loc[len(ald4)] = nyrad

for x in range(40, 45):
    nyrad = {'ald2': 44, 'Alder': x}
    ald4.loc[len(ald4)] = nyrad

for x in range(45, 50):
    nyrad = {'ald2': 49, 'Alder': x}
    ald4.loc[len(ald4)] = nyrad
print(ald4)
ald5 = pd.DataFrame(columns=['ald2', 'Alder'])

for x in range(0, 100):
    nyrad = {'ald2': 99, 'Alder': x}
    ald5.loc[len(ald5)] = nyrad

ald6 = pd.DataFrame(columns=['ald2', 'Alder'])

for x in range(0, 100):
    nyrad = {'ald2': 99, 'Alder': x}
    ald6.loc[len(ald6)] = nyrad

demo1 = barnr

demo2 = pd.DataFrame({'ald1': 6,
                      'ald2': 15,
                      'br': bef.query('Alder >= 6 and Alder <= 15').a2021.sum(),
                      'bri': 1.0}, index=[0])

kolonnenavn = ['ald1', 'ald2', 'br', 'bri']

demo3 = pd.DataFrame(pd.read_fwf(dem3,
                    header=None,
                    delimiter=" ",
                    names=kolonnenavn))
                     
demo4 = pd.DataFrame(pd.read_fwf(dem4,
                    header=None,
                    delimiter=" ",
                    names=kolonnenavn))

demo5 = pd.DataFrame({'ald1': 0,
                      'ald2': 99,
                      'br': bef.a2021.sum(),
                      'bri': 1.0}, index=[0])

demo6 = pd.DataFrame({'ald1': 0,
                      'ald2': 99,
                      'br': bef.a2021.sum(),
                      'bri': 1.0}, index=[0])

# ************************************************
# LAGER ALDERSAGGREGATER av befolkningsfilen etter
# gruppering i den aktuelle etterspørselsfil
# ************************************************

for i in range(1, 7):
    locals()[f'bef{i}'] = pd.DataFrame()

    locals()[f'bef{i}'] = locals()[f'ald{i}'].merge(bef, how='inner', on='Alder')

    locals()[f'bef{i}'] = locals()[f'bef{i}'].groupby(["ald2"]).sum()

    locals()[f'bef{i}'].drop(['Alder'], axis=1, inplace=True)
    locals()[f'bef{i}'].drop(['Kjønn'], axis=1, inplace=True)
    
    locals()[f'demo{i}'] = locals()[f'demo{i}'].set_index(['ald2'])

    for x in range(Basisår, Sluttår + 1):
        locals()[f'demo{i}']['agr' + str(x)] = locals()[f'bef{i}']['a' + str(x)]

    locals()[f'demo{i}']["pg" + str(Basisår)] = locals()[f'demo{i}'].br * locals()[f'demo{i}'].bri

    for x in range(Basisår + 1, Sluttår + 1):
        locals()[f'demo{i}']['pg' + str(x)] = locals()[f'demo{i}']['pg' + str(x-1)] * (locals()[f'bef{i}']['a' + str(x)] /
                                                         locals()[f'bef{i}']['a' + str(x-1)])

    locals()[f'demo{i}']["mg" + str(Basisår)] = locals()[f'demo{i}'].br * locals()[f'demo{i}'].bri

    for x in range(Basisår + 1, Sluttår + 1):
        locals()[f'demo{i}']['mg' + str(x)] = locals()[f'demo{i}']['mg' + str(x-1)] * (locals()[f'bef{i}']['a' + str(x)] /
                                                                                       locals()[f'bef{i}']['a' + str(x-1)])

    locals()[f'demos{i}'] = pd.DataFrame()
    
    for x in range(Basisår, Sluttår + 1):
        locals()[f'demos{i}']['agrs' + str(x)] = [locals()[f'demo{i}']['agr' + str(x)].sum()]
        locals()[f'demos{i}']['pgs' + str(x)] = [locals()[f'demo{i}']['pg' + str(x)].sum()]
        locals()[f'demos{i}']['mgs' + str(x)] = [locals()[f'demo{i}']['mg' + str(x)].sum()]
    
    y = locals()[f'demos{i}']['pgs' + str(Basisår)].loc[0]
    
    locals()[f'demy{i}'] = pd.DataFrame({'Utdanning': ['ba', 'gr', 'fa', 'ph', 'py'],
                                         'Brukerindeks': [y, y, y, y, y]})
    
    locals()[f'Årsverk{i}'] = pd.DataFrame()
    locals()[f'Årsverk{i}'] = locals()[f'demy{i}']
    
    locals()[f'Årsverk{i}']['År'] = EtterspørselLærere['År' + str(i)]
    locals()[f'Årsverk{i}']['stdrd'] = locals()[f'Årsverk{i}']['År'] / locals()[f'Årsverk{i}']['Brukerindeks']
    
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

dmindeks = stand.merge(demår1, how='inner', on='År')
dmindeks = dmindeks.merge(demår2, how='inner', on='År')
dmindeks = dmindeks.merge(demår3, how='inner', on='År')
dmindeks = dmindeks.merge(demår4, how='inner', on='År')
dmindeks = dmindeks.merge(demår5, how='inner', on='År')
dmindeks = dmindeks.merge(demår6, how='inner', on='År')

Årsverk = pd.concat([Årsverk1, Årsverk2, Årsverk3, Årsverk4, Årsverk5, Årsverk6])

# ******************************************************************
# NYKAND: Beregner antall uteksaminerte studenter over sim.perioden.
# Disse fordeles så etter alder og kjønn (for hvert år).
# ******************************************************************

LærerKandidaterTotalt = OpptatteLærerStudenter.merge(Gjennomføring, how='inner', on='Utdanning')

LærerKandidaterTotalt['uteks'] = LærerKandidaterTotalt.apply(lambda row: (row['OpptatteStudenter'] * row['fullfob'])
                                 if row['År'] + row['NormertTid'] <= Basisår + 3
                                 else (row['OpptatteStudenter'] * row['fullfor']), axis=1)

kand_ald = nystud.merge(LærerKandidaterTotalt, how='inner', on=['Utdanning'])

kand_ald["Alder"] = kand_ald.Alder + kand_ald.NormertTid
kand_ald["eks_ald"] = kand_ald.uteks * kand_ald.st_ald

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
neste_år['Populasjon'] = neste_år['Populasjon'].fillna(0)
neste_år['eks_ald'] = neste_år['eks_ald'].fillna(0)

neste_år.Populasjon = neste_år.Populasjon + neste_år.eks_ald
neste_år['År'] = Basisår + 1

slutt = neste_år[['Utdanning', 'Kjønn', 'Alder', 'Populasjon', 'Årsverk', 'År']]

beh_paar = pd.concat([beh_paar, slutt])

for x in range(Basisår + 2, Sluttår + 1):
    forrige_år = beh_paar.copy()
    forrige_år = forrige_år[forrige_år['År'] == x-1]
    forrige_år.Alder += 1

    kand_år = kand_ald
    kand_år = kand_år[kand_år['År'] == x]

    neste_år = forrige_år.merge(kand_år, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])

    neste_år['Populasjon'] = neste_år['Populasjon'].fillna(0)
    neste_år['eks_ald'] = neste_år['eks_ald'].fillna(0)

    neste_år.Populasjon = neste_år.Populasjon + neste_år.eks_ald
    neste_år['År'] = x

    slutt = neste_år[['Utdanning', 'Kjønn', 'Alder', 'Populasjon', 'Årsverk', 'År']]

    beh_paar = pd.concat([beh_paar, slutt])

# ************************************************************
# TILBUD: Beregner
#         årsverkstilbudet ut fra mønsteret i yrkesdeltakelsen
#         og eventuell eksogen økning i yrkesdeltakelsen.
# ************************************************************

Tilbud = beh_paar.merge(beh_syss, how='outer', on=['Utdanning', 'Kjønn', 'Alder'])
Tilbud['Tilbud'] = Tilbud.Populasjon * Tilbud.Sysselsettingsandel * Tilbud.GjennomsnitteligeÅrsverk
Tilbud = Tilbud.groupby(['Utdanning', 'År'], sort=False).sum()
Tilbud = Tilbud.drop(['Kjønn', 'Alder', 'Populasjon', 'Sysselsettingsandel', 'GjennomsnitteligeÅrsverk'], axis=1)

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

Etterspørsel = reduce(lambda left, right: pd.merge(left, right, on=['Utdanning'], how='outer'), [ind, EtterspørselLærere, vakesp])

Etterspørsel = Etterspørsel.reset_index()
Etterspørsel = Etterspørsel.set_index(['Utdanning', 'År'])

Etterspørsel['Etterspørsel'] = (Etterspørsel.År1 + Etterspørsel.vak1) * Etterspørsel.dm1 * Etterspørsel.Sektor1
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År2 + Etterspørsel.vak2) * Etterspørsel.dm2 * Etterspørsel.Sektor2
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År3 + Etterspørsel.vak3) * Etterspørsel.dm3 * Etterspørsel.Sektor3
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År4 + Etterspørsel.vak4) * Etterspørsel.dm4 * Etterspørsel.Sektor4
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År5 + Etterspørsel.vak5) * Etterspørsel.dm5 * Etterspørsel.Sektor5
Etterspørsel['Etterspørsel'] = Etterspørsel['Etterspørsel'] + (Etterspørsel.År6 + Etterspørsel.vak6) * Etterspørsel.dm6 * Etterspørsel.Sektor6

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
