import pandas as pd
from functools import reduce
import time


basisaar = 2020
sluttaar = 2040


befolkning = 'inndata/mmmm_2022_short.txt'
stkap = 'inndata/fullforingsgrader.txt'
oppta = 'inndata/opptak.txt'
vak = 'inndata/vakanseoriginal.txt'

sysselsatte = 'inndata/sysselsatte.txt'
utdannede = 'inndata/utdannede.txt'
studenter = 'inndata/nye_studenter.txt'

dem1 = 'inndata/antall_barn_barnehager.txt'
dem2 = 'inndata/antall_elever_grunnskole.txt'
dem3 = 'inndata/antall_elever_videregaende.txt'
dem4 = 'inndata/antall_studenter_hoyereutdanning.txt'
dem5 = 'inndata/antall_personer_andreskoler.txt'
dem6 = 'inndata/antall_personer_andreskoler.txt'

innpr = 'inndata/standard.txt'
inplu = 'inndata/endring_timeverk.txt'


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

starttid = time.time()

# **********
# Konstanter
# **********

sektorliste = [1, 2, 3, 4, 5, 6]
gruppeliste = [1, 1, 1, 1, 1, 1,
               2, 2, 2, 2, 2, 2,
               3, 3, 3, 3, 3, 3,
               4, 4, 4, 4, 4, 4,
               5, 5, 5, 5, 5, 5]

# ********************************
# Innlesing av sysselsatte lærere.
# ********************************

sysselsatte_laerere = pd.DataFrame()

sysselsatte_laerere = pd.read_csv(sysselsatte,
                                  header=None,
                                  delimiter=r"\s+",
                                  names=['utdanning',
                                         'sektor',
                                         'syssm',
                                         'syssk',
                                         'gaavma',
                                         'gaavka'],
                                  usecols=list(range(6)),
                                  dtype={'utdanning': 'string',
                                         'sektor': 'int',
                                         'syssm': 'int',
                                         'syssk': 'int',
                                         'gaavma': 'float',
                                         'gaavka': 'float'})

sysselsatte_laerere['sektor'] -= 1
sysselsatte_laerere['sektor'].replace(to_replace=0, value=6, inplace=True)

sysselsatte_laerere['aavm'] = sysselsatte_laerere.apply(lambda row:
                                                        row['syssm'] *
                                                        row['gaavma'], axis=1)
sysselsatte_laerere['aavk'] = sysselsatte_laerere.apply(lambda row: 
                                                        row['syssk'] *
                                                        row['gaavka'], axis=1)

sysselsatte_laerere.drop(['gaavma', 'gaavka'], axis=1, inplace=True)

sysselsatte_laerere['sysst'] = sysselsatte_laerere.apply(lambda row: row['syssm'] + row['syssk']
                             if row['syssm'] >= 0
                             and row['syssk'] >= 0
                             else row['syssm']
                             if row['syssm'] >= 0
                             else row['syssk'], axis=1)

sysselsatte_laerere['aavt'] = sysselsatte_laerere.apply(lambda row: row['aavm'] + row['aavk']
                            if row['aavm'] >= 0
                            and row['aavk'] >= 0
                            else row['aavm']
                            if row['aavm'] >= 0
                            else row['aavk'], axis=1)

sysselsatte_laerere.sort_values(by=['utdanning', 'sektor'], inplace=True)

# ******************************
# Innlesing av utdannede lærere.
# ******************************

utdannede_laerere = pd.DataFrame()

utdannede_laerere = pd.read_csv(utdannede,
                                header=None,
                                delimiter=r"\s+",
                                na_values={'.', ' .'},
                                names=['utdanning',
                                       'kjonn',
                                       'alder',
                                       'bestand',
                                       'sysselsatte',
                                       'sysselsettingsandel',
                                       'gjennomsnittelige_aarsverk'],
                                usecols=list(range(7)),
                                dtype={'utdanning': 'string',
                                       'kjonn': 'int',
                                       'alder': 'int',
                                       'bestand': 'int',
                                       'sysselsatte': 'int',
                                       'sysselsettingsandel': 'float',
                                       'gjennomsnittelige_aarsverk': 'float'})

utdannede_laerere['sysselsettingsandel'] = utdannede_laerere.apply(lambda row:
                                                                   row['sysselsatte'] /
                                                                   row['bestand']
                                                                   if row['bestand'] > 0
                                                                   else 0, axis=1)

# *******************
# Opprettelse av tabe
# *******************

tabe = pd.DataFrame()

tabe = sysselsatte_laerere.copy()

tabe['utdanning'].replace(to_replace="ba", value="1", inplace=True)
tabe['utdanning'].replace(to_replace="gr", value="2", inplace=True)
tabe['utdanning'].replace(to_replace="fa", value="3", inplace=True)
tabe['utdanning'].replace(to_replace="ph", value="4", inplace=True)
tabe['utdanning'].replace(to_replace="py", value="5", inplace=True)
tabe['utdanning'].replace(to_replace="an", value="6", inplace=True)

tabe["utdanning"] = pd.to_numeric(tabe["utdanning"])

index_andre = tabe[(tabe['utdanning'] > 5)].index
tabe.drop(index_andre, inplace=True)

tabe = tabe.reset_index()
tabe.drop(['index'], axis=1, inplace=True)

tabe = tabe.set_index(['utdanning', 'sektor'])

# ********************
# Opprettelse av taber
# ********************

taber = pd.DataFrame()

taber = sysselsatte_laerere.copy()

taber = taber[taber['utdanning'] == 'an']
taber.drop(['utdanning'], axis=1, inplace=True)

taber.set_index('sektor', inplace=True)

# *****************************
# Proc Summary på tabet og tabe
# *****************************

sysselsatte_laerere = sysselsatte_laerere.groupby(['utdanning', 'sektor']).sum()

tabe = tabe.groupby(['utdanning', 'sektor']).sum()

# ********************
# Opprettelse av tabes
# ********************

tabes = pd.DataFrame()

tabes = tabe.copy()

tabes = tabes.groupby(['sektor']).sum()

# **************************************
# Slår sammen tabe og tabes og får tabea
# **************************************

tabea = pd.DataFrame()

kolonnenavn = ['andms', 'andks', 'andmt', 'andkt']

for i in range(4):
    for x in range(5):
        tabea.insert(loc=x, column=kolonnenavn[i]+str(x+1),
                     value=[(tabe.iloc[0 + x * 6, i] / tabes.iloc[0, i]),
                            (tabe.iloc[1 + x * 6, i] / tabes.iloc[1, i]),
                            (tabe.iloc[2 + x * 6, i] / tabes.iloc[2, i]),
                            (tabe.iloc[3 + x * 6, i] / tabes.iloc[3, i]),
                            (tabe.iloc[4 + x * 6, i] / tabes.iloc[4, i]),
                            (tabe.iloc[5 + x * 6, i] / tabes.iloc[5, i])])

# **********************
# Opprettelse av taberg1
# **********************

taber = taber.reset_index()

taberg1 = pd.DataFrame()

for i in range(1, 6):
    taberg1["aavma"+str(i)] = tabea["andmt"+str(i)] * taber.aavm
    taberg1["aavka"+str(i)] = tabea["andkt"+str(i)] * taber.aavk

# *********************
# Opprettelse av taberg
# *********************

taberg = pd.DataFrame()

taberg["sektor"] = sektorliste * 5
taberg["utdanning"] = gruppeliste

taberg["aavtr"] = pd.concat([taberg1.aavma1 + taberg1.aavka1,
                             taberg1.aavma2 + taberg1.aavka2,
                             taberg1.aavma3 + taberg1.aavka3,
                             taberg1.aavma4 + taberg1.aavka4,
                             taberg1.aavma5 + taberg1.aavka5],
                            ignore_index=True,
                            sort=False)

taberg = taberg.reset_index()
taberg.drop(['index'], axis=1, inplace=True)

taberg = taberg.set_index(['utdanning', 'sektor'])

# **********************
# Opprettelse av tabetot
# **********************

tabetot = pd.DataFrame()

tabetot['aavt'] = tabe.aavt + taberg.aavtr

# *********************
# Opprettelse av tabtot
# *********************

tabtot = utdannede_laerere

tabtot = tabtot.fillna('')

tabtot['sysselsettingsandel'] = pd.to_numeric(tabtot['sysselsettingsandel'])
tabtot['gjennomsnittelige_aarsverk'] = pd.to_numeric(tabtot['gjennomsnittelige_aarsverk'])

# **************************
# Innlesing av nye studenter
# **************************

Studenter = pd.DataFrame()

Studenter = pd.read_csv(studenter,
                        header=None,
                        delimiter=r"\s+",
                        na_values={'.', ' .'},
                        names=['utdanning',
                               'alder',
                               'alle',
                               'menn',
                               'kvinner'],
                        usecols=list(range(5)),
                        dtype={'utdanning': 'string',
                               'alder': 'int',
                               'alle': 'int',
                               'menn': 'int',
                               'kvinner': 'int'})

Studenter = Studenter.set_index(['utdanning'])

# ********************
# Opprettelse av studs
# ********************

studs = pd.DataFrame()

studs = Studenter.groupby(["utdanning"]).sum()
studs.rename(columns={"alle": "totalt"}, inplace=True)

studs.drop(['alder', 'kvinner', 'menn'], axis=1, inplace=True)

# *******************
# Opprettelse av taba
# *******************

taba = pd.DataFrame()

taba = Studenter

taba = taba.merge(studs, how='outer', on='utdanning')

taba.menn = taba.menn / taba.totalt
taba.kvinner = taba.kvinner / taba.totalt

taba = taba.reset_index()

# ****************************************
# Innlesing av folkemengden i alder 0-5 år
# ****************************************

bef1 = pd.DataFrame()

bef1 = pd.read_csv(befolkning,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(2, 200),
                   usecols=[1, 2, 3, 4])

bef2 = pd.DataFrame()

bef2 = pd.read_csv(befolkning,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(6, 200),
                   usecols=[1, 2, 3, 4])

bef2 = bef2.drop([0, 1])

bef2 = bef2.reset_index()
bef2.drop(['index'], axis=1, inplace=True)

bef3 = pd.DataFrame()

bef3 = pd.read_csv(befolkning,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(8, 200),
                   usecols=[1, 2, 3, 4])

bef3.drop(bef3.index[:6], inplace=True)

bef3 = bef3.reset_index()
bef3.drop(['index'], axis=1, inplace=True)

bef4 = pd.DataFrame()

bef4 = pd.read_csv(befolkning,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(12, 200),
                   usecols=[1, 2, 3, 4])

bef4.drop(bef4.index[:8], inplace=True)

bef4 = bef4.reset_index()
bef4.drop(['index'], axis=1, inplace=True)

# ************************************
# Innlesing av antall barn i barnehage
# ************************************

barnhin = pd.DataFrame()

barnhin = pd.read_csv(dem1,
                      header=None,
                      delimiter=" ",
                      names=['aar',
                             'ti1',
                             'ti2',
                             'ba1',
                             'ba2',
                             'ba3',
                             'ba4',
                             'ba5',
                             'ba6'],
                      usecols=list(range(9)))

barn1 = pd.DataFrame()

barn1["b2021"] = barnhin.ba1
barn1["tim"] = barnhin.ti1 + ((barnhin.ti2 - barnhin.ti1) / 2)
barn1["ald1"] = 0
barn1["ald2"] = 0

barn2 = pd.DataFrame()

barn2["b2021"] = barnhin.ba2 + barnhin.ba3
barn2["tim"] = barnhin.ti1 + ((barnhin.ti2 - barnhin.ti1) / 2)
barn2["ald1"] = 1
barn2["ald2"] = 2

barn3 = pd.DataFrame()

barn3["b2021"] = barnhin.ba4
barn3["tim"] = barnhin.ti1 + ((barnhin.ti2 - barnhin.ti1) / 2)
barn3["ald1"] = 3
barn3["ald2"] = 3

barn4 = pd.DataFrame()

barn4["b2021"] = barnhin.ba5 + barnhin.ba6
barn4["tim"] = barnhin.ti1 + ((barnhin.ti2 - barnhin.ti1) / 2)
barn4["ald1"] = 4
barn4["ald2"] = 5

# ************************************
# Oppretter noen oppsummeringstabeller
# ************************************

befs1 = pd.DataFrame({'agr2020': bef1.a2020.sum(),
                      'agr2021': bef1.a2021.sum(),
                      'ald1': 0,
                      'ald2': 0}, index=[0])

befs2 = pd.DataFrame({'agr2020': bef2.a2020.sum(),
                      'agr2021': bef2.a2021.sum(),
                      'ald1': 1,
                      'ald2': 2}, index=[0])

befs3 = pd.DataFrame({'agr2020': bef3.a2020.sum(),
                      'agr2021': bef3.a2021.sum(),
                      'ald1': 3,
                      'ald2': 3}, index=[0])

befs4 = pd.DataFrame({'agr2020': bef4.a2020.sum(),
                      'agr2021': bef4.a2021.sum(),
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

barnr = pd.DataFrame

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

barnr["antaar"] = 2

# ******************************************************
# Innlesing av folkemengden i grunnskole og andre skoler
# ******************************************************

kolonneposisjoner = [(0, 2), (3, 4), (245, 250), (251, 256)]
kolonnenavn = ['alder', 'kjonn', 'a2020', 'a2021']

fwf = pd.DataFrame()

fwf = pd.read_fwf(befolkning, colspecs=kolonneposisjoner, header=None)
fwf.columns = kolonnenavn

bef5 = pd.DataFrame()

bef5 = fwf[fwf['alder'] >= 6]
bef5 = bef5[bef5['alder'] <= 15]

bef5 = bef5.reset_index()
bef5.drop(['index'], axis=1, inplace=True)

bef6 = pd.DataFrame()
bef6 = fwf

# ********************
# Innlesing av inndata
# ********************

kolonnenavn = ["alder"] + ["kjonn"]

for x in range(basisaar, sluttaar+1):
    kolonnenavn = kolonnenavn + ["a" + str(x)]

bef = pd.DataFrame()
bef = pd.read_fwf(befolkning,
                  header=None,
                  delimiter=" ",
                  col_names=kolonnenavn)

bef.columns = kolonnenavn

gjfoer = pd.DataFrame()
gjfoer = pd.read_fwf(stkap,
                     header=None,
                     delimiter=" ",
                     names=["utdanning", "norm", "fullfor", "fullfob"])

innles = pd.DataFrame()
innles = pd.read_fwf(oppta,
                     header=None,
                     delimiter=" ",
                     names=["aar", "ba", "gr", "fa", "ph", "py"])

innles = innles.set_index(['aar'])

ba = pd.DataFrame()
ba['oppfag'] = innles['ba']
ba.loc[:, 'utdanning'] = 'ba'

gr = pd.DataFrame()
gr['oppfag'] = innles['gr']
gr.loc[:, 'utdanning'] = 'gr'

fa = pd.DataFrame()
fa['oppfag'] = innles['fa']
fa.loc[:, 'utdanning'] = 'fa'

ph = pd.DataFrame()
ph['oppfag'] = innles['ph']
ph.loc[:, 'utdanning'] = 'ph'

py = pd.DataFrame()
py['oppfag'] = innles['py']
py.loc[:, 'utdanning'] = 'py'

opptak = pd.concat([ba, gr, fa, ph, py])

plussakt = pd.DataFrame()
plussakt = pd.read_fwf(inplu,
                       header=None,
                       delimiter=" ",
                       names=["alder", "plussm", "plussk"])

nystud1 = taba.copy()
nystud1['kjonn'] = 1
nystud1['st_ald'] = nystud1.menn

nystud2 = taba.copy()
nystud2['kjonn'] = 2
nystud2['st_ald'] = nystud2.kvinner

nystud = pd.concat([nystud1, nystud2])

beh_pers = tabtot.copy()

beh_pers["aarsverk"] = beh_pers.bestand * beh_pers.sysselsettingsandel * beh_pers.gjennomsnittelige_aarsverk

beh_pers.drop(['sysselsatte', 'sysselsettingsandel', 'gjennomsnittelige_aarsverk'], axis=1, inplace=True)

beh_syss = tabtot.copy()

beh_syss.drop(['bestand', 'sysselsatte'], axis=1, inplace=True)

arsvesp = pd.DataFrame({'utdanning': ['ba', 'gr', 'fa', 'ph', 'py']})

for i in range(1, 7):
    arsvesp["ar"+str(i)] = tabetot.aavt[tabetot.aavt.index.get_level_values('sektor') == i].reset_index(drop=True)

vakesp = pd.DataFrame()
vakesp = pd.read_fwf(vak,
                     header=None,
                     delimiter=" ",
                     names=["utdanning", "vak1", "vak2", "vak3", "vak4", "vak5", "vak6"])

# ********************************************************
# PROSENTVIS ENDRING I ANTALL ELEVER pr. 1000 INNBYGGERE
# ved de ulike aktivitetsområdene over simuleringsperioden
# tallet 1.01 tolkes som 1 prosent økt elevtall pr. 1000
# ********************************************************

stand = pd.DataFrame()
stand = pd.read_fwf(innpr,
                    header=None,
                    delimiter=" ",
                    names=["aar",
                           "barnplus",
                           "grskplus",
                           "viskplus",
                           "uhskplus",
                           "anskplus",
                           "utskplus"])

stand = stand[stand['aar'] >= basisaar]
stand = stand[stand['aar'] <= sluttaar]

# ****************************************
# Oppretter datasett for senere utfylling.
# ****************************************

ald1 = pd.DataFrame(columns=['ald2', 'alder'])

for x in range(0, 1):
    nyrad = {'ald2': 0, 'alder': x}
    ald1.loc[len(ald1)] = nyrad

for x in range(1, 3):
    nyrad = {'ald2': 2, 'alder': x}
    ald1.loc[len(ald1)] = nyrad

for x in range(3, 4):
    nyrad = {'ald2': 3, 'alder': x}
    ald1.loc[len(ald1)] = nyrad

for x in range(4, 6):
    nyrad = {'ald2': 5, 'alder': x}
    ald1.loc[len(ald1)] = nyrad

ald2 = pd.DataFrame(columns=['ald2', 'alder'])

for x in range(6, 16):
    nyrad = {'ald2': 15, 'alder': x}
    ald2.loc[len(ald2)] = nyrad

ald3 = pd.DataFrame(columns=['ald2', 'alder'])

for x in range(0, 16):
    nyrad = {'ald2': 15, 'alder': x}
    ald3.loc[len(ald3)] = nyrad

for x in range(16, 25):
    nyrad = {'ald2': x, 'alder': x}
    ald3.loc[len(ald3)] = nyrad

for x in range(25, 100):
    nyrad = {'ald2': 99, 'alder': x}
    ald3.loc[len(ald3)] = nyrad

ald4 = pd.DataFrame(columns=['ald2', 'alder'])

for x in range(19, 30):
    nyrad = {'ald2': x, 'alder': x}
    ald4.loc[len(ald4)] = nyrad

for x in range(30, 35):
    nyrad = {'ald2': 34, 'alder': x}
    ald4.loc[len(ald4)] = nyrad

for x in range(35, 40):
    nyrad = {'ald2': 39, 'alder': x}
    ald4.loc[len(ald4)] = nyrad

for x in range(40, 45):
    nyrad = {'ald2': 44, 'alder': x}
    ald4.loc[len(ald4)] = nyrad

for x in range(45, 50):
    nyrad = {'ald2': 49, 'alder': x}
    ald4.loc[len(ald4)] = nyrad

ald5 = pd.DataFrame(columns=['ald2', 'alder'])

for x in range(0, 100):
    nyrad = {'ald2': 99, 'alder': x}
    ald5.loc[len(ald5)] = nyrad

ald6 = pd.DataFrame(columns=['ald2', 'alder'])

for x in range(0, 100):
    nyrad = {'ald2': 99, 'alder': x}
    ald6.loc[len(ald6)] = nyrad

kolonneposisjoner = [(0, 2), (4, 6), (7, 16), (17, 22), (23, 25)]
kolonnenavn = ['ald1', 'ald2', 'br', 'bri', 'antaar']

demo1 = barnr

demo2 = pd.DataFrame()
demo2 = pd.read_fwf(dem2,
                    header=None,
                    delimiter=" ",
                    names=kolonnenavn)

demo3 = pd.DataFrame()

kolonneposisjoner = [(0, 2), (3, 5), (6, 14), (15, 18), (19, 20)]

demo3 = pd.read_fwf(dem3, colspecs=kolonneposisjoner, header=None)
demo3.columns = kolonnenavn

demo4 = pd.DataFrame()
demo4 = pd.read_fwf(dem4,
                    header=None,
                    delimiter=" ",
                    names=kolonnenavn)

demo5 = pd.DataFrame()
demo5 = pd.read_fwf(dem5, colspecs=kolonneposisjoner, header=None)

demo5.columns = kolonnenavn

demo6 = pd.DataFrame()
demo6 = pd.read_fwf(dem6, colspecs=kolonneposisjoner, header=None)

demo6.columns = kolonnenavn

# ************************************************
# LAGER ALDERSAGGREGATER av befolkningsfilen etter
# gruppering i den aktuelle etterspørselsfil
# ************************************************

for i in range(1, 7):
    locals()[f'bef{i}'] = pd.DataFrame()

    locals()[f'bef{i}'] = locals()[f'ald{i}'].merge(bef, how='inner', on='alder')

    locals()[f'bef{i}'] = locals()[f'bef{i}'].groupby(["ald2"]).sum()

    locals()[f'bef{i}'].drop(['alder'], axis=1, inplace=True)
    locals()[f'bef{i}'].drop(['kjonn'], axis=1, inplace=True)
    
    locals()[f'demo{i}'] = locals()[f'demo{i}'].set_index(['ald2'])

    for x in range(basisaar, sluttaar + 1):
        locals()[f'demo{i}']['agr' + str(x)] = locals()[f'bef{i}']['a' + str(x)]

    locals()[f'demo{i}']["pg" + str(basisaar)] = locals()[f'demo{i}'].br * locals()[f'demo{i}'].bri

    for x in range(basisaar + 1, sluttaar + 1):
        locals()[f'demo{i}']['pg' + str(x)] = locals()[f'demo{i}']['pg' + str(x-1)] * (locals()[f'bef{i}']['a' + str(x)] /
                                                         locals()[f'bef{i}']['a' + str(x-1)])

    locals()[f'demo{i}']["mg" + str(basisaar)] = locals()[f'demo{i}'].br * locals()[f'demo{i}'].bri

    for x in range(basisaar + 1, sluttaar + 1):
        locals()[f'demo{i}']['mg' + str(x)] = locals()[f'demo{i}']['mg' + str(x-1)] * (locals()[f'bef{i}']['a' + str(x)] /
                                                                                       locals()[f'bef{i}']['a' + str(x-1)])

    locals()[f'demos{i}'] = pd.DataFrame()
    
    for x in range(basisaar, sluttaar + 1):
        locals()[f'demos{i}']['agrs' + str(x)] = [locals()[f'demo{i}']['agr' + str(x)].sum()]
        locals()[f'demos{i}']['pgs' + str(x)] = [locals()[f'demo{i}']['pg' + str(x)].sum()]
        locals()[f'demos{i}']['mgs' + str(x)] = [locals()[f'demo{i}']['mg' + str(x)].sum()]
    
    y = locals()[f'demos{i}']['pgs' + str(basisaar)].loc[0]
    
    locals()[f'demy{i}'] = pd.DataFrame({'utdanning': ['ba', 'gr', 'fa', 'ph', 'py'],
                                         'brind': [y, y, y, y, y]})
    
    locals()[f'arsv{i}'] = pd.DataFrame()
    locals()[f'arsv{i}'] = locals()[f'demy{i}']
    
    locals()[f'arsv{i}']['ar'] = arsvesp['ar' + str(i)]
    locals()[f'arsv{i}']['stdrd'] = locals()[f'arsv{i}']['ar'] / locals()[f'arsv{i}']['brind']
    
    locals()[f'demaar{i}'] = pd.DataFrame({"aar": [basisaar], "dm" + str(i): [1], "dp" + str(i): [1], "dem" + str(i): locals()[f'demos{i}']['agrs' + str(basisaar)]})

    for x in range(basisaar + 1, sluttaar + 1):
        nyrad = pd.DataFrame({"aar": x,
                              "dm" + str(i): locals()[f'demos{i}']['mgs' + str(x)] / locals()[f'demos{i}']['mgs' + str(basisaar)],
                              "dp" + str(i): (locals()[f'demos{i}']['pgs' + str(x)] / locals()[f'demos{i}']['pgs' + str(basisaar)]) /
                                     (locals()[f'demos{i}']['mgs' + str(x)] / locals()[f'demos{i}']['mgs' + str(basisaar)]),
                              "dem" + str(i): locals()[f'demos{i}']['agrs' + str(x)]})
        locals()[f'demaar{i}'] = pd.concat([locals()[f'demaar{i}'], nyrad], ignore_index=True)
    
# ******************************************************
# Lager indeks for demografikomponenten i etterspørselen
# etter tjenester
# ******************************************************

dmindeks = stand.merge(demaar1, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar2, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar3, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar4, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar5, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar6, how='inner', on='aar')

arsv = pd.concat([arsv1, arsv2, arsv3, arsv4, arsv5, arsv6])

# ******************************************************************
# NYKAND: Beregner antall uteksaminerte studenter over sim.perioden.
# Disse fordeles så etter alder og kjønn (for hvert år).
# ******************************************************************

opptak = opptak.reset_index()
opptak = opptak[opptak['aar'] > basisaar]

kandtot = opptak.merge(gjfoer, how='inner', on='utdanning')

kandtot['uteks'] = kandtot.apply(lambda row: (row['oppfag'] * row['fullfob'])
                                 if row['aar'] + row['norm'] <= basisaar + 3
                                 else (row['oppfag'] * row['fullfor']), axis=1)

kandtot = kandtot.set_index(['utdanning'])
nystud = nystud.set_index(['utdanning'])

kand_ald = nystud.merge(kandtot, how='inner', on=['utdanning'])

kand_ald["alder"] = kand_ald.alder + kand_ald.norm
kand_ald["eks_ald"] = kand_ald.uteks * kand_ald.st_ald

# *************************************************************
# NYBEHOLD: Fører strømmen av nyutdannete inn i beholdningen av
#           en yrkesgruppe, og framskriver beholdningen av fag-
#           utdannete over simuleringsperioden.
# *************************************************************

beh_pers['aar'] = basisaar
beh_paar = beh_pers.copy()

forrige_aar = beh_pers.copy()
forrige_aar.alder += 1

kand_aar = kand_ald
kand_aar = kand_aar[kand_aar['aar'] == basisaar + 1]

neste_aar = forrige_aar.merge(kand_aar, how='outer', on=['utdanning', 'kjonn', 'alder'])
neste_aar['bestand'] = neste_aar['bestand'].fillna(0)
neste_aar['eks_ald'] = neste_aar['eks_ald'].fillna(0)

neste_aar.bestand = neste_aar.bestand + neste_aar.eks_ald
neste_aar['aar'] = basisaar + 1

slutt = neste_aar[['utdanning', 'kjonn', 'alder', 'bestand', 'aarsverk', 'aar']]

beh_paar = pd.concat([beh_paar, slutt])

for x in range(basisaar + 2, sluttaar + 1):
    forrige_aar = beh_paar.copy()
    forrige_aar = forrige_aar[forrige_aar['aar'] == x-1]
    forrige_aar.alder += 1

    kand_aar = kand_ald
    kand_aar = kand_aar[kand_aar['aar'] == x]

    neste_aar = forrige_aar.merge(kand_aar, how='outer', on=['utdanning', 'kjonn', 'alder'])

    neste_aar['bestand'] = neste_aar['bestand'].fillna(0)
    neste_aar['eks_ald'] = neste_aar['eks_ald'].fillna(0)

    neste_aar.bestand = neste_aar.bestand + neste_aar.eks_ald
    neste_aar['aar'] = x

    slutt = neste_aar[['utdanning', 'kjonn', 'alder', 'bestand', 'aarsverk', 'aar']]

    beh_paar = pd.concat([beh_paar, slutt])

# ************************************************************
# TILBUD: Beregner
#         årsverkstilbudet ut fra mønsteret i yrkesdeltakelsen
#         og eventuell eksogen økning i yrkesdeltakelsen.
# ************************************************************

tilbud = beh_paar.merge(beh_syss, how='outer', on=['utdanning', 'kjonn', 'alder'])

tilbud['aarsverk'] = tilbud.bestand * tilbud.sysselsettingsandel * tilbud.gjennomsnittelige_aarsverk

tilbud = tilbud.groupby(['utdanning', 'aar']).sum()

tilbud = tilbud.drop(['kjonn', 'alder', 'bestand', 'sysselsettingsandel', 'gjennomsnittelige_aarsverk'], axis=1)

# ******************************************
# TILB-ESP: Sluttproduktet fra simuleringen.
# ******************************************

dmindeks['utdanning'] = 'ba'
ind1 = dmindeks.copy()
dmindeks['utdanning'] = 'gr'
ind2 = dmindeks.copy()
dmindeks['utdanning'] = 'fa'
ind3 = dmindeks.copy()
dmindeks['utdanning'] = 'ph'
ind4 = dmindeks.copy()
dmindeks['utdanning'] = 'py'
ind5 = dmindeks.copy()

ind = pd.concat([ind1, ind2, ind3, ind4, ind5])
ind = ind.reset_index()

data_frames = [ind, arsvesp, vakesp]

esp = reduce(lambda left, right: pd.merge(left, right, on=['utdanning'],
                                          how='outer'), data_frames)

esp = esp.reset_index()
esp = esp.set_index(['utdanning', 'aar'])

esp['ep1'] = (esp.ar1 + esp.vak1) * esp.dm1 * esp.barnplus
esp['ep2'] = (esp.ar2 + esp.vak2) * esp.dm2 * esp.grskplus
esp['ep3'] = (esp.ar3 + esp.vak3) * esp.dm3 * esp.viskplus
esp['ep4'] = (esp.ar4 + esp.vak4) * esp.dm4 * esp.uhskplus
esp['ep5'] = (esp.ar5 + esp.vak5) * esp.dm5 * esp.anskplus
esp['ep6'] = (esp.ar6 + esp.vak6) * esp.dm6 * esp.utskplus

esp['Etterspørsel'] = esp['ep1'] + esp['ep2'] + esp['ep3'] + esp['ep4'] + esp['ep5'] + esp['ep6']

t_e = tilbud.merge(esp, how='outer', on=['utdanning', 'aar'])

t_e['Vakanse'] = t_e.aarsverk - t_e.Etterspørsel

t_e = t_e[['Etterspørsel', 'aarsverk', 'Vakanse']]

t_e.rename(columns={"aarsverk": "Tilbud"}, inplace=True)

custom_dict = {'ba': 1, 'gr': 2, 'fa': 3, 'ph': 4, 'py': 5}
t_e = t_e.sort_values(by=['utdanning', 'aar'], key=lambda x: x.map(custom_dict))

t_e.index.names = ['Utdanning', 'År']

t_e.rename(index={'ba': 'Barnehagelærere'}, inplace=True)
t_e.rename(index={'gr': 'Grunnskolelærere'}, inplace=True)
t_e.rename(index={'fa': 'Faglærere'}, inplace=True)
t_e.rename(index={'ph': 'PPU Universitet og høyskole'}, inplace=True)
t_e.rename(index={'py': 'PPU Yrkesfag'}, inplace=True)

pd.options.display.multi_sparse = False

t_e.round(0).astype(int).to_csv("resultater/Lærermod.csv")
t_e.round(0).astype(int).to_excel("resultater/Lærermod.xlsx")

print(t_e.round(0).astype(int).to_string())

totaltid = time.time() - starttid

print()
print('Lærermod er nå ferdig.')
print()
print(f'Og det tok {totaltid:.2f} sekunder. Velkommen tilbake.')
print()
