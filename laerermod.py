import pandas as pd
from functools import reduce

import time

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


basisaar = 2020
sluttaar = 2040


innb = 'inndata/mmmm_2022.txt'
stkap = 'inndata/fullforingsgrader.txt'
oppta = 'inndata/opptak.txt'
vak = 'inndata/vakanse.txt'

dem3 = 'inndata/antall_elever_videregaende.txt'
dem4 = 'inndata/antall_studenter_hoyereutdanning.txt'
i2 = 'inndata/antall_barn_barnehager.txt'

innpr = 'inndata/standard.txt'
inplu = 'inndata/endring_timeverk.txt'

# Filer produsert av beholdning.py
bhl = 'utdata/beholdning.dat'
aarsv = 'utdata/aarsverk.dat'
nystu = 'utdata/nye_studenter.dat'


i1_syss = 'inndata/syssutd2021.txt'
i1_utd = 'inndata/utd2021_dat.txt'
st = 'inndata/nye_studenter.txt'

o1 = 'utdata/aarsverk.dat'
o2 = 'utdata/beholdning.dat'
ut = 'utdata/nye_studenter.dat'

# **********
# Konstanter
# **********


sektorliste = [1, 2, 3, 4, 5, 6]
gruppeliste = [1, 1, 1, 1, 1, 1,
               2, 2, 2, 2, 2, 2,
               3, 3, 3, 3, 3, 3,
               4, 4, 4, 4, 4, 4,
               5, 5, 5, 5, 5, 5]

indeks = pd.MultiIndex.from_product([['1', '2', '3', '4', '5'],
                                    ['1', '2', '3', '4', '5', '6']],
                                    names=['gruppe', 'sektor'])

# ********************
# Innlesing av i1_syss
# ********************

tabse_syss = pd.DataFrame()

tabse_syss = pd.read_csv(i1_syss,
                         header=None,
                         delimiter=r"\s+",
                         names=['studium',
                                'sektor',
                                'syssm',
                                'syssk',
                                'gaavma',
                                'gaavka'],
                         usecols=list(range(6)),
                         dtype={'studium': 'string',
                                'sektor': 'int',
                                'syssm': 'int',
                                'syssk': 'int',
                                'gaavma': 'float',
                                'gaavka': 'float'})

tabse_syss['studium'].replace(to_replace="4", value="ba", inplace=True)
tabse_syss['studium'].replace(to_replace="2", value="gr", inplace=True)
tabse_syss['studium'].replace(to_replace="3", value="fa", inplace=True)
tabse_syss['studium'].replace(to_replace="1", value="ps", inplace=True)
tabse_syss['studium'].replace(to_replace="5", value="an", inplace=True)
tabse_syss['studium'].replace(to_replace="6", value="sp", inplace=True)
tabse_syss['studium'].replace(to_replace="7", value="st", inplace=True)
tabse_syss['studium'].replace(to_replace="a", value="ph", inplace=True)
tabse_syss['studium'].replace(to_replace="b", value="py", inplace=True)

tabse_syss['sektor'] -= 1
tabse_syss['sektor'].replace(to_replace=0, value=6, inplace=True)

tabse_syss.loc[tabse_syss['syssm'] < 0, ['syssm']] = 0
tabse_syss.loc[tabse_syss['syssk'] < 0, ['syssk']] = 0
tabse_syss.loc[tabse_syss['gaavma'] < 0, ['gaavma']] = 0
tabse_syss.loc[tabse_syss['gaavka'] < 0, ['gaavka']] = 0

tabse_syss['aavma'] = tabse_syss.apply(lambda row: row['syssm'] *
                                       row['gaavma'], axis=1)
tabse_syss['aavka'] = tabse_syss.apply(lambda row: row['syssk'] *
                                       row['gaavka'], axis=1)

tabse_syss.sort_values(by=['studium', 'sektor'], inplace=True)

# **********************
# Opprettelse av o1_syss
# **********************

o1_syss = pd.DataFrame()

o1_syss = tabse_syss.copy()

o1_syss.drop(['gaavma', 'gaavka'], axis=1, inplace=True)

o1_syss.rename(columns={"aavma": "aavm", "aavka": "aavk"}, inplace=True)

# *******************
# Innlesing av i1_utd
# *******************

tabse_utd = pd.DataFrame()

tabse_utd = pd.read_csv(i1_utd,
                        header=None,
                        delimiter=r"\s+",
                        na_values={'.', ' .'},
                        names=['studium',
                               'kjonn',
                               'alder',
                               'bestand',
                               'sysselsatte',
                               'yp',
                               'tpa',
                               'tp'],
                        usecols=list(range(8)),
                        dtype={'studium': 'string',
                               'kjonn': 'int',
                               'alder': 'int',
                               'bestand': 'int',
                               'sysselsatte': 'int',
                               'yp': 'float',
                               'tpa': 'float',
                               'tp': 'float'})

tabse_utd['studium'].replace(to_replace="4", value="ba", inplace=True)
tabse_utd['studium'].replace(to_replace="2", value="gr", inplace=True)
tabse_utd['studium'].replace(to_replace="3", value="fa", inplace=True)
tabse_utd['studium'].replace(to_replace="1", value="ps", inplace=True)
tabse_utd['studium'].replace(to_replace="5", value="an", inplace=True)
tabse_utd['studium'].replace(to_replace="6", value="sp", inplace=True)
tabse_utd['studium'].replace(to_replace="7", value="st", inplace=True)
tabse_utd['studium'].replace(to_replace="a", value="ph", inplace=True)
tabse_utd['studium'].replace(to_replace="b", value="py", inplace=True)

tabse_utd['yp'] = tabse_utd.apply(lambda row: row['sysselsatte'] /
                                  row['bestand']
                                  if row['bestand'] > 0
                                  else 0, axis=1)

tabse_utd = tabse_utd[tabse_utd['alder'] >= 17]
tabse_utd = tabse_utd[tabse_utd['alder'] <= 74]

tabse_utd.sort_values(by=['studium', 'kjonn', 'alder'], inplace=True)

# *********************
# Opprettelse av o1_utd
# *********************

o1_utd = pd.DataFrame()

o1_utd = tabse_utd.copy()

# ********************
# Opprettelse av tabet
# ********************

tabet = pd.DataFrame()

tabet = o1_syss.copy()

tabet['sysst'] = tabet.apply(lambda row: row['syssm'] + row['syssk']
                             if row['syssm'] >= 0
                             and row['syssk'] >= 0
                             else row['syssm']
                             if row['syssm'] >= 0
                             else row['syssk'], axis=1)

tabet['aavt'] = tabet.apply(lambda row: row['aavm'] + row['aavk']
                            if row['aavm'] >= 0
                            and row['aavk'] >= 0
                            else row['aavm']
                            if row['aavm'] >= 0
                            else row['aavk'], axis=1)

tabet.sort_values(by=['studium', 'sektor'], inplace=True)

# *******************
# Opprettelse av tabe
# *******************

tabe = pd.DataFrame()

tabe = tabet.copy()

tabe['studium'].replace(to_replace="ba", value="1", inplace=True)
tabe['studium'].replace(to_replace="gr", value="2", inplace=True)
tabe['studium'].replace(to_replace="fa", value="3", inplace=True)
tabe['studium'].replace(to_replace="ph", value="4", inplace=True)
tabe['studium'].replace(to_replace="py", value="5", inplace=True)
tabe['studium'].replace(to_replace=["an", "st", "sp"], value="6", inplace=True)

tabe.rename(columns={"studium": "gruppe"}, inplace=True)

tabe["gruppe"] = pd.to_numeric(tabe["gruppe"])

indexAge = tabe[(tabe['gruppe'] > 5)].index
tabe.drop(indexAge, inplace=True)

tabe.sort_values(by=['gruppe', 'sektor'], inplace=True)
tabe = tabe.reset_index()
tabe.drop(['index'], axis=1, inplace=True)

tabe = tabe.set_index(['gruppe', 'sektor'])

# ********************
# Opprettelse av taber
# ********************

taber = pd.DataFrame()

taber = tabet.copy()

taber = taber[taber['studium'] == 'an']

taber.drop(['studium'], axis=1, inplace=True)

taber.set_index('sektor', inplace=True)

# *****************************
# Proc Summary på tabet og tabe
# *****************************

tabet = tabet.groupby(['studium', 'sektor']).sum()

tabe = tabe.groupby(['gruppe', 'sektor']).sum()

# ********************
# Opprettelse av tabes
# ********************

tabes = pd.DataFrame()

tabes = tabe.copy()

tabes = tabes.groupby(['sektor']).sum()

tabes.rename(columns={"syssm": "syssms"}, inplace=True)
tabes.rename(columns={"syssk": "syssks"}, inplace=True)
tabes.rename(columns={"aavm": "aavms"}, inplace=True)
tabes.rename(columns={"aavk": "aavks"}, inplace=True)

# ********************
# Opprettelse av tabeg
# ********************

tabeg = pd.DataFrame()

tabeg = tabe.copy()

tabeg = tabeg.groupby(['gruppe']).sum()

# *********************
# Opprettelse av tabesg
# *********************

tabesg = pd.DataFrame()

tabesg = tabe.copy()

tabesg = tabesg.groupby(['sektor', 'gruppe']).sum()

# **************************************
# Slår sammen tabe og tabes og får tabea
# **************************************

tabea = pd.DataFrame()

tabes.rename(columns={"syssms": "syssm"}, inplace=True)
tabes.rename(columns={"syssks": "syssk"}, inplace=True)
tabes.rename(columns={"aavms": "aavm"}, inplace=True)
tabes.rename(columns={"aavks": "aavk"}, inplace=True)
tabes.rename(columns={"syssms": "syssm"}, inplace=True)
tabes.rename(columns={"syssms": "syssm"}, inplace=True)

kolonnenavn = ['andms', 'andks', 'andmt', 'andkt']

for x in range(5):
    tabea.insert(loc=x, column=kolonnenavn[3]+str(x+1),
                 value=[(tabe.iloc[0 + x * 6, 3] / tabes.iloc[0, 3]),
                        (tabe.iloc[1 + x * 6, 3] / tabes.iloc[1, 3]),
                        (tabe.iloc[2 + x * 6, 3] / tabes.iloc[2, 3]),
                        (tabe.iloc[3 + x * 6, 3] / tabes.iloc[3, 3]),
                        (tabe.iloc[4 + x * 6, 3] / tabes.iloc[4, 3]),
                        (tabe.iloc[5 + x * 6, 3] / tabes.iloc[5, 3])])

for x in range(5):
    tabea.insert(loc=x, column=kolonnenavn[2]+str(x+1),
                 value=[(tabe.iloc[0 + x * 6, 2] / tabes.iloc[0, 2]),
                        (tabe.iloc[1 + x * 6, 2] / tabes.iloc[1, 2]),
                        (tabe.iloc[2 + x * 6, 2] / tabes.iloc[2, 2]),
                        (tabe.iloc[3 + x * 6, 2] / tabes.iloc[3, 2]),
                        (tabe.iloc[4 + x * 6, 2] / tabes.iloc[4, 2]),
                        (tabe.iloc[5 + x * 6, 2] / tabes.iloc[5, 2])])

for x in range(5):
    tabea.insert(loc=x, column=kolonnenavn[1]+str(x+1),
                 value=[(tabe.iloc[0 + x * 6, 1] / tabes.iloc[0, 1]),
                        (tabe.iloc[1 + x * 6, 1] / tabes.iloc[1, 1]),
                        (tabe.iloc[2 + x * 6, 1] / tabes.iloc[2, 1]),
                        (tabe.iloc[3 + x * 6, 1] / tabes.iloc[3, 1]),
                        (tabe.iloc[4 + x * 6, 1] / tabes.iloc[4, 1]),
                        (tabe.iloc[5 + x * 6, 1] / tabes.iloc[5, 1])])

for x in range(5):
    tabea.insert(loc=x, column=kolonnenavn[0]+str(x+1),
                 value=[(tabe.iloc[0 + x * 6, 0] / tabes.iloc[0, 0]),
                        (tabe.iloc[1 + x * 6, 0] / tabes.iloc[1, 0]),
                        (tabe.iloc[2 + x * 6, 0] / tabes.iloc[2, 0]),
                        (tabe.iloc[3 + x * 6, 0] / tabes.iloc[3, 0]),
                        (tabe.iloc[4 + x * 6, 0] / tabes.iloc[4, 0]),
                        (tabe.iloc[5 + x * 6, 0] / tabes.iloc[5, 0])])

# **********************
# Opprettelse av taberg1
# **********************

taber = taber.reset_index()

taberg1 = pd.DataFrame()

taberg1["syssma1"] = tabea.andms1 * taber.syssm
taberg1["syssma2"] = tabea.andms2 * taber.syssm
taberg1["syssma3"] = tabea.andms3 * taber.syssm
taberg1["syssma4"] = tabea.andms4 * taber.syssm
taberg1["syssma5"] = tabea.andms5 * taber.syssm

taberg1["sysska1"] = tabea.andks1 * taber.syssk
taberg1["sysska2"] = tabea.andks2 * taber.syssk
taberg1["sysska3"] = tabea.andks3 * taber.syssk
taberg1["sysska4"] = tabea.andks4 * taber.syssk
taberg1["sysska5"] = tabea.andks5 * taber.syssk

taberg1["aavma1"] = tabea.andmt1 * taber.aavm
taberg1["aavma2"] = tabea.andmt2 * taber.aavm
taberg1["aavma3"] = tabea.andmt3 * taber.aavm
taberg1["aavma4"] = tabea.andmt4 * taber.aavm
taberg1["aavma5"] = tabea.andmt5 * taber.aavm

taberg1["aavka1"] = tabea.andkt1 * taber.aavk
taberg1["aavka2"] = tabea.andkt2 * taber.aavk
taberg1["aavka3"] = tabea.andkt3 * taber.aavk
taberg1["aavka4"] = tabea.andkt4 * taber.aavk
taberg1["aavka5"] = tabea.andkt5 * taber.aavk

# *********************
# Opprettelse av taberg
# *********************

taberg = pd.DataFrame()

idx = pd.MultiIndex.from_product([['1', '2', '3', '4', '5'],
                                  ['1', '2', '3', '4', '5', '6']],
                                 names=['gruppe', 'sektor'])
col = ['syssmr', 'sysskr', 'aavmr', 'aavkr']

df = pd.DataFrame('-', idx, col)

taberg["sektor"] = sektorliste * 5
taberg["gruppe"] = gruppeliste

taberg["syssmr"] = pd.concat([taberg1.syssma1,
                              taberg1.syssma2,
                              taberg1.syssma3,
                              taberg1.syssma4,
                              taberg1.syssma5],
                             ignore_index=True,
                             sort=False)

taberg["sysskr"] = pd.concat([taberg1.sysska1,
                              taberg1.sysska2,
                              taberg1.sysska3,
                              taberg1.sysska4,
                              taberg1.sysska5],
                             ignore_index=True,
                             sort=False)

taberg["aavmr"] = pd.concat([taberg1.aavma1,
                             taberg1.aavma2,
                             taberg1.aavma3,
                             taberg1.aavma4,
                             taberg1.aavma5],
                            ignore_index=True,
                            sort=False)

taberg["aavkr"] = pd.concat([taberg1.aavka1,
                             taberg1.aavka2,
                             taberg1.aavka3,
                             taberg1.aavka4,
                             taberg1.aavka5],
                            ignore_index=True,
                            sort=False)

taberg["sysstr"] = taberg.syssmr + taberg.sysskr

taberg["aavtr"] = taberg.aavmr + taberg.aavkr

taberg.sort_values(by=['gruppe', 'sektor'], inplace=True)
taberg = taberg.reset_index()
taberg.drop(['index'], axis=1, inplace=True)

taberg = taberg.set_index(['gruppe', 'sektor'])

# **********************
# Opprettelse av tabetot
# **********************

tabetot = pd.DataFrame()

tabetot['syssm'] = tabe.syssm + taberg.syssmr
tabetot['syssk'] = tabe.syssk + taberg.sysskr
tabetot['sysst'] = tabe.sysst + taberg.sysstr
tabetot['aavm'] = tabe.aavm + taberg.aavmr
tabetot['aavk'] = tabe.aavk + taberg.aavkr
tabetot['aavt'] = tabe.aavt + taberg.aavtr

# *********************
# Opprettelse av tabeut
# *********************

tabeut = pd.DataFrame()

tabeut = tabetot.aavt.groupby(['gruppe', 'sektor']).sum()

# *******************************
# Oppretter tabell med årsverkene
# *******************************

aarsverk_ettersporsel = pd.DataFrame()

serie1 = tabeut.loc[1]
serie1 = serie1.reset_index()
serie1.drop(['sektor'], axis=1, inplace=True)
serie1.rename(columns={"aavt": "ba"}, inplace=True)

serie2 = tabeut.loc[2]
serie2 = serie2.reset_index()
serie2.drop(['sektor'], axis=1, inplace=True)
serie2.rename(columns={"aavt": "gr"}, inplace=True)

serie3 = tabeut.loc[3]
serie3 = serie3.reset_index()
serie3.drop(['sektor'], axis=1, inplace=True)
serie3.rename(columns={"aavt": "fa"}, inplace=True)

serie4 = tabeut.loc[4]
serie4 = serie4.reset_index()
serie4.drop(['sektor'], axis=1, inplace=True)
serie4.rename(columns={"aavt": "ph"}, inplace=True)

serie5 = tabeut.loc[5]
serie5 = serie5.reset_index()
serie5.drop(['sektor'], axis=1, inplace=True)
serie5.rename(columns={"aavt": "py"}, inplace=True)

aarsverk_ettersporsel = pd.concat([serie1.T, serie2.T, serie3.T, serie4.T, serie5.T])

aarsverk_ettersporsel.rename(columns={0: "ar1", 1: "ar2", 2: "ar3", 3: "ar4", 4: "ar5", 5: "ar6"}, inplace=True)

aarsverk_ettersporsel.index.name = 'yrke'

#print(list(aarsverk_ettersporsel.columns))
#print(aarsverk_ettersporsel.to_string())

# *****************************
# Skriver ut fil med årsverkene
# *****************************
"""
with open(o1, 'w') as f:
    f.write("ba")
    serie = tabeut.loc[1]
    for x in range(6):
        f.write(str(round(serie[x+1])).rjust(6))
    f.write('\ngr')
    serie = tabeut.loc[2]
    for x in range(6):
        f.write(str(round(serie[x+1])).rjust(6))
    f.write('\nfa')
    serie = tabeut.loc[3]
    for x in range(6):
        f.write(str(round(serie[x+1])).rjust(6))
    f.write('\nph')
    serie = tabeut.loc[4]
    for x in range(6):
        f.write(str(round(serie[x+1])).rjust(6))
    f.write('\npy')
    serie = tabeut.loc[5]
    for x in range(6):
        f.write(str(round(serie[x+1])).rjust(6))

    f.close()
"""
# **********************
# Opprettelse av tabergs
# **********************

tabergs = pd.DataFrame()

tabergs = taberg.groupby(['gruppe']).sum()

# *********************
# Opprettelse av tabers
# *********************

tabers = pd.DataFrame()

tabers = tabergs.sum()

# *********************
# Opprettelse av tabera
# *********************

tabera = pd.DataFrame()

tabera['andms'] = tabergs.syssmr / tabers.syssmr
tabera['andks'] = tabergs.sysskr / tabers.sysskr
tabera['andmt'] = tabergs.aavmr / tabers.aavmr
tabera['andkt'] = tabergs.aavkr / tabers.aavkr

# **********************
# Opprettelse av taberak
# **********************

taberak = pd.DataFrame()

taberak = tabera.T

# ******************
# Opprettelse av tab
# ******************

tab = pd.DataFrame()

tab = o1_utd

# ******************
# Opprettelse av tab
# ******************

tabs = pd.DataFrame()

tab['aavs'] = tab.sysselsatte * tab.tpa

tabs = tab.groupby(["studium"]).sum()

# ****************************
# Opprettelse av tabap og tabg
# ****************************

tabap = pd.DataFrame()
tabg = pd.DataFrame()

tabap = tab
tabg = tab

# ********************
# Opprettelse av tabgs
# ********************

tabgs = pd.DataFrame()

tabgs = tab.groupby(["studium"]).sum()

# ********************
# Opprettelse av tabgg
# ********************

tabgg = pd.DataFrame()

tabgg = tabg

tabgg['studium'].replace(to_replace="ba", value="1", inplace=True)
tabgg['studium'].replace(to_replace="gr", value="2", inplace=True)
tabgg['studium'].replace(to_replace="fa", value="3", inplace=True)
tabgg['studium'].replace(to_replace="ph", value="4", inplace=True)
tabgg['studium'].replace(to_replace="py", value="5", inplace=True)

tabgg.rename(columns={"studium": "gruppe"}, inplace=True)

tabgg = tabgg[tabgg['gruppe'] != "an"]
tabgg = tabgg[tabgg['gruppe'] != "sp"]
tabgg = tabgg[tabgg['gruppe'] != "st"]

# *********************
# Opprettelse av tabtot
# *********************

tabtot = pd.DataFrame()

tabtot = tabgg

tabtot['gruppe'].replace(to_replace="1", value="ba", inplace=True)
tabtot['gruppe'].replace(to_replace="2", value="gr", inplace=True)
tabtot['gruppe'].replace(to_replace="3", value="fa", inplace=True)
tabtot['gruppe'].replace(to_replace="4", value="ph", inplace=True)
tabtot['gruppe'].replace(to_replace="5", value="py", inplace=True)

tabtot = tabtot.fillna('')

tabtot['yp'] = pd.to_numeric(tabtot['yp'])
tabtot['tpa'] = pd.to_numeric(tabtot['tpa'])
tabtot['tp'] = pd.to_numeric(tabtot['tp'])
tabtot['aavs'] = pd.to_numeric(tabtot['aavs'])

# *******************************
# Skriver ut fil med beholdningen
# *******************************

tabtot.to_csv(o2, float_format='%.5f', sep=';', header=False, index=False)

# **************************
# Innlesing av nye studenter
# **************************

studa = pd.DataFrame()

studa = pd.read_csv(st,
                    header=None,
                    delimiter=r"\s+",
                    na_values={'.', ' .'},
                    names=['studium',
                           'alder',
                           'bs',
                           'bm',
                           'bk'],
                    usecols=list(range(5)),
                    dtype={'studium': 'string',
                           'alder': 'int',
                           'bs': 'int',
                           'bm': 'int',
                           'bk': 'int'})

studa['studium'].replace(to_replace="ba", value="1", inplace=True)
studa['studium'].replace(to_replace="gr", value="2", inplace=True)
studa['studium'].replace(to_replace="fa", value="3", inplace=True)
studa['studium'].replace(to_replace="ph", value="4", inplace=True)
studa['studium'].replace(to_replace="py", value="5", inplace=True)
studa['studium'].replace(to_replace="sp", value="6", inplace=True)

studa = studa.set_index(['studium'])

# ********************
# Opprettelse av studs
# ********************

studs = pd.DataFrame()

studs = studa.groupby(["studium"]).sum()

studs.rename(columns={"bs": "bss"}, inplace=True)

studs.drop(['alder'], axis=1, inplace=True)
studs.drop(['bk'], axis=1, inplace=True)
studs.drop(['bm'], axis=1, inplace=True)

# *******************
# Opprettelse av taba
# *******************

taba = pd.DataFrame()

taba = studa

taba = taba.merge(studs, how='outer', on='studium')

taba.bs = taba.bs / taba.bss
taba.bm = taba.bm / taba.bss
taba.bk = taba.bk / taba.bss

taba.drop(['bss'], axis=1, inplace=True)

taba.sort_values(by=['studium', 'alder'], inplace=True)

taba.rename(columns={"bs": "bss"}, inplace=True)

taba = taba.reset_index()

taba['studium'].replace(to_replace="1", value="ba", inplace=True)
taba['studium'].replace(to_replace="2", value="gr", inplace=True)
taba['studium'].replace(to_replace="3", value="fa", inplace=True)
taba['studium'].replace(to_replace="4", value="ph", inplace=True)
taba['studium'].replace(to_replace="5", value="py", inplace=True)
taba['studium'].replace(to_replace="6", value="sp", inplace=True)

# ********************************
# Skriver ut fil med nye studenter
# ********************************

taba.to_csv(ut, float_format='%.4f', sep=' ', header=False, index=False)






# ****************************************
# Innlesing av folkemengden i alder 0-5 år
# ****************************************

bef1 = pd.DataFrame()

bef1 = pd.read_csv(innb,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(2, 200),
                   usecols=[1, 2, 43, 44])

bef2 = pd.DataFrame()

bef2 = pd.read_csv(innb,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(6, 200),
                   usecols=[1, 2, 43, 44])

bef2 = bef2.drop([0, 1])

bef2 = bef2.reset_index()
bef2.drop(['index'], axis=1, inplace=True)

bef3 = pd.DataFrame()

bef3 = pd.read_csv(innb,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(8, 200),
                   usecols=[1, 2, 43, 44])

bef3.drop(bef3.index[:6], inplace=True)

bef3 = bef3.reset_index()
bef3.drop(['index'], axis=1, inplace=True)

bef4 = pd.DataFrame()

bef4 = pd.read_csv(innb,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(12, 200),
                   usecols=[1, 2, 43, 44])

bef4.drop(bef4.index[:8], inplace=True)

bef4 = bef4.reset_index()
bef4.drop(['index'], axis=1, inplace=True)

# ************************************
# Innlesing av antall barn i barnehage
# ************************************

barnhin = pd.DataFrame()

barnhin = pd.read_csv(i2,
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
                       'bu': barn1.b2021.sum(),
                       'bri': (2 * barn1.b2021.mul(barn1.tim.values).sum()) /
                              (barn1.b2021.sum() * 42.5)}, index=[0])

barna2 = pd.DataFrame({'ald1': 1,
                       'ald2': 2,
                       'bu': barn2.b2021.sum(),
                       'bri': (2 * barn2.b2021.mul(barn2.tim.values).sum()) /
                              (barn2.b2021.sum() * 42.5)}, index=[0])

barna3 = pd.DataFrame({'ald1': 3,
                       'ald2': 3,
                       'bu': barn3.b2021.sum(),
                       'bri': (1.5 * barn3.b2021.mul(barn3.tim.values).sum()) /
                              (barn3.b2021.sum() * 42.5)}, index=[0])

barna4 = pd.DataFrame({'ald1': 4,
                       'ald2': 5,
                       'bu': barn4.b2021.sum(),
                       'bri': (1 * barn4.b2021.mul(barn4.tim.values).sum()) /
                              (barn4.b2021.sum() * 42.5)}, index=[0])

# ********************
# Slår sammen tabeller
# ********************

barnr = pd.DataFrame

barnr = pd.concat([befs1, befs2, befs3, befs4], ignore_index=True)
barnar = pd.concat([barna1, barna2, barna3, barna4], ignore_index=True)

barnr["bu"] = barnar.bu
barnr["bri"] = barnar.bri

barnr["ans1"] = barnr.bu / barnr.agr2021
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

fwf = pd.read_fwf(innb, colspecs=kolonneposisjoner, header=None)
fwf.columns = kolonnenavn

bef5 = pd.DataFrame()

bef5 = fwf[fwf['alder'] >= 6]
bef5 = bef5[bef5['alder'] <= 15]

bef5 = bef5.reset_index()
bef5.drop(['index'], axis=1, inplace=True)

bef6 = pd.DataFrame()
bef6 = fwf

# *************************************
# Oppretter flere oppsummeringstabeller
# *************************************

befs5 = pd.DataFrame({'agr2020': bef5.a2020.sum(),
                      'agr2021': bef5.a2021.sum(),
                      'ald1': 6,
                      'ald2': 15,
                      'bri': 1,
                      'antaar': 0}, index=[0])

befs6 = pd.DataFrame({'agr2020': bef6.a2020.sum(),
                      'agr2021': bef6.a2021.sum(),
                      'ald1': 0,
                      'ald2': 99,
                      'bri': 1,
                      'antaar': 0}, index=[0])





# ********************
# Innlesing av inndata
# ********************

kolonnenavn = ["alder"] + ["kjonn"]

for x in range(1980, 2051):
    kolonnenavn = kolonnenavn + ["a" + str(x)]

bef = pd.DataFrame()
bef = pd.read_fwf(innb,
                  header=None,
                  delimiter=" ",
                  col_names=kolonnenavn)

bef.columns = kolonnenavn

gjfoer = pd.DataFrame()
gjfoer = pd.read_fwf(stkap,
                     header=None,
                     delimiter=" ",
                     names=["yrke", "norm", "fullfor", "fullfob"])

innles = pd.DataFrame()
innles = pd.read_fwf(oppta,
                     header=None,
                     delimiter=" ",
                     names=["aar", "ba", "gr", "fa", "ph", "py", "sp"])

innles = innles.set_index(['aar'])

ba = pd.DataFrame()
ba['oppfag'] = innles['ba']
ba.loc[:, 'yrke'] = 'ba'

gr = pd.DataFrame()
gr['oppfag'] = innles['gr']
gr.loc[:, 'yrke'] = 'gr'

fa = pd.DataFrame()
fa['oppfag'] = innles['fa']
fa.loc[:, 'yrke'] = 'fa'

ph = pd.DataFrame()
ph['oppfag'] = innles['ph']
ph.loc[:, 'yrke'] = 'ph'

py = pd.DataFrame()
py['oppfag'] = innles['py']
py.loc[:, 'yrke'] = 'py'

opptak = pd.concat([ba, gr, fa, ph, py])

plussakt = pd.DataFrame()
plussakt = pd.read_fwf(inplu,
                       header=None,
                       delimiter=" ",
                       names=["alder", "plussm", "plussk"])

nystud1 = pd.read_fwf(nystu,
                      header=None,
                      delimiter=" ",
                      names=["yrke", "alder", "st", "stm", "stk"])

nystud1['kjonn'] = 1
nystud1['st_ald'] = nystud1.stm

nystud2 = pd.read_fwf(nystu,
                      header=None,
                      delimiter=" ",
                      names=["yrke", "alder", "st", "stm", "stk"])

nystud2['kjonn'] = 2
nystud2['st_ald'] = nystud2.stk

nystud = pd.concat([nystud1, nystud2])

beh_pers = pd.DataFrame()
beh_pers = pd.read_csv(bhl,
                       header=None,
                       delimiter=r";",
                       names=['yrke',
                              'kjonn',
                              'alder',
                              'pers',
                              'syss',
                              'yp',
                              'tpa',
                              'tp',
                              'aavs'],
                       usecols=list(range(9)),
                       dtype={'yrke': 'string',
                              'kjonn': 'int',
                              'alder': 'int',
                              'pers': 'int',
                              'syss': 'int',
                              'yp': 'float',
                              'tpa': 'float',
                              'tp': 'float',
                              'aavs': 'float'})

beh_pers["arsv"] = beh_pers.pers * beh_pers.yp * beh_pers.tpa

beh_pers.drop(['syss', 'yp', 'tpa', 'tp', 'aavs'], axis=1, inplace=True)

beh_syss = pd.DataFrame()
beh_syss = pd.read_csv(bhl,
                       header=None,
                       delimiter=r";",
                       names=['yrke',
                              'kjonn',
                              'alder',
                              'pers',
                              'syss',
                              'yp',
                              'tpa',
                              'tp',
                              'aavs'],
                       usecols=list(range(9)),
                       dtype={'yrke': 'string',
                              'kjonn': 'int',
                              'alder': 'int',
                              'pers': 'int',
                              'syss': 'int',
                              'yp': 'float',
                              'tpa': 'float',
                              'tp': 'float',
                              'aavs': 'float'})

beh_syss.rename(columns={"yp": "syssand",
                         "tpa": "garsv"},
                inplace=True)

beh_syss.drop(['pers', 'syss', 'tp', 'aavs'], axis=1, inplace=True)
"""
arsvesp = pd.DataFrame()
arsvesp = pd.read_fwf(aarsv,
                      header=None,
                      delimiter=" ",
                      names=["yrke", "ar1", "ar2", "ar3", "ar4", "ar5", "ar6"])
"""
vakesp = pd.DataFrame()
vakesp = pd.read_fwf(vak,
                     header=None,
                     delimiter=" ",
                     names=["yrke", "vak1", "vak2", "vak3", "vak4", "vak5", "vak6"])

vakesp = vakesp[vakesp['yrke'] != 'sp']

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

filnavn = ['dem1', 'dem2', 'dem3', 'dem4', 'dem5', 'dem6']
aldersnavn = ['ald1', 'ald2', 'ald3', 'ald4', 'ald5', 'ald6']
demografinavn = ['demo1', 'demo2', 'demo3', 'demo4', 'demo5', 'dem6']

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
demo1.rename(columns={"bu": "br"},
             inplace=True)

demo2 = befs5
demo2.rename(columns={"agr2021": "br"},
             inplace=True)

demo3 = pd.DataFrame()

kolonneposisjoner = [(0, 2), (3, 5), (6, 14), (15, 18), (19, 20)]
kolonnenavn = ['ald1', 'ald2', 'br', 'bri', 'antaar']

demo3 = pd.read_fwf(dem3, colspecs=kolonneposisjoner, header=None)
demo3.columns = kolonnenavn

demo4 = pd.DataFrame()
demo4 = pd.read_fwf(dem4,
                    header=None,
                    delimiter=" ",
                    names=["ald1",
                           "ald2",
                           "br",
                           "bri",
                           "antaar"])

demo5 = befs6
demo5.rename(columns={"agr2021": "br"},
             inplace=True)

demo6 = befs6
demo6.rename(columns={"agr2021": "br"},
             inplace=True)

# ************************************************
# LAGER ALDERSAGGREGATER av befolkningsfilen etter
# gruppering i den aktuelle etterspørselsfil
# ************************************************

bef1 = pd.DataFrame()

bef1 = ald1.merge(bef, how='inner', on='alder')
bef1 = bef1.groupby(["ald2"]).sum()

bef1.drop(['alder'], axis=1, inplace=True)
bef1.drop(['kjonn'], axis=1, inplace=True)

bef2 = pd.DataFrame()

bef2 = ald2.merge(bef, how='inner', on='alder')
bef2 = bef2.groupby(["ald2"]).sum()

bef2.drop(['alder'], axis=1, inplace=True)
bef2.drop(['kjonn'], axis=1, inplace=True)

bef3 = pd.DataFrame()

bef3 = ald3.merge(bef, how='inner', on='alder')
bef3 = bef3.groupby(["ald2"]).sum()

bef3.drop(['alder'], axis=1, inplace=True)
bef3.drop(['kjonn'], axis=1, inplace=True)

bef4 = pd.DataFrame()

bef4 = ald4.merge(bef, how='inner', on='alder')
bef4 = bef4.groupby(["ald2"]).sum()

bef4.drop(['alder'], axis=1, inplace=True)
bef4.drop(['kjonn'], axis=1, inplace=True)

bef5 = pd.DataFrame()

bef5 = ald5.merge(bef, how='inner', on='alder')
bef5 = bef5.groupby(["ald2"]).sum()

bef5.drop(['alder'], axis=1, inplace=True)
bef5.drop(['kjonn'], axis=1, inplace=True)

bef6 = pd.DataFrame()

bef6 = ald6.merge(bef, how='inner', on='alder')
bef6 = bef6.groupby(["ald2"]).sum()

bef6.drop(['alder'], axis=1, inplace=True)
bef6.drop(['kjonn'], axis=1, inplace=True)

demo1 = demo1.set_index(['ald2'])

for x in range(basisaar, sluttaar + 1):
    demo1['agr' + str(x)] = bef1['a' + str(x)]

demo1['pg2020'] = demo1.br * demo1.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo1['pg' + str(x)] = demo1['pg' + str(x-1)] * (bef1['a' + str(x)] /
                                                     bef1['a' + str(x-1)])

demo1['mg2020'] = demo1.br * demo1.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo1['mg' + str(x)] = demo1['mg' + str(x-1)] * (bef1['a' + str(x)] /
                                                     bef1['a' + str(x-1)])

demo2 = demo2.set_index(['ald2'])

for x in range(basisaar, sluttaar + 1):
    demo2['agr' + str(x)] = bef2['a' + str(x)]

demo2['pg2020'] = demo2.br * demo2.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo2['pg' + str(x)] = demo2['pg' + str(x-1)] * (bef2['a' + str(x)] /
                                                     bef2['a' + str(x-1)])

demo2['mg2020'] = demo2.br * demo2.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo2['mg' + str(x)] = demo2['mg' + str(x-1)] * (bef2['a' + str(x)] /
                                                     bef2['a' + str(x-1)])

demo3 = demo3.set_index(['ald2'])

for x in range(basisaar, sluttaar + 1):
    demo3['agr' + str(x)] = bef3['a' + str(x)]

demo3['pg2020'] = demo3.br * demo3.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo3['pg' + str(x)] = demo3['pg' + str(x-1)] * (bef3['a' + str(x)] /
                                                     bef3['a' + str(x-1)])

demo3['mg2020'] = demo3.br * demo3.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo3['mg' + str(x)] = demo3['mg' + str(x-1)] * (bef3['a' + str(x)] /
                                                     bef3['a' + str(x-1)])

demo4 = demo4.set_index(['ald2'])

for x in range(basisaar, sluttaar + 1):
    demo4['agr' + str(x)] = bef4['a' + str(x)]

demo4['pg2020'] = demo4.br * demo4.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo4['pg' + str(x)] = demo4['pg' + str(x-1)] * (bef4['a' + str(x)] /
                                                     bef4['a' + str(x-1)])

demo4['mg2020'] = demo4.br * demo4.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo4['mg' + str(x)] = demo4['mg' + str(x-1)] * (bef4['a' + str(x)] /
                                                     bef4['a' + str(x-1)])

demo5 = demo5.set_index(['ald2'])

for x in range(basisaar, sluttaar + 1):
    demo5['agr' + str(x)] = bef5['a' + str(x)]

demo5['pg2020'] = demo5.br * demo5.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo5['pg' + str(x)] = demo5['pg' + str(x-1)] * (bef5['a' + str(x)] /
                                                     bef5['a' + str(x-1)])

demo5['mg2020'] = demo5.br * demo5.bri

for x in range(basisaar + 1, sluttaar + 1):
    demo5['mg' + str(x)] = demo5['mg' + str(x-1)] * (bef5['a' + str(x)] /
                                                     bef5['a' + str(x-1)])

demo6 = demo5

demos1 = pd.DataFrame()
demos2 = pd.DataFrame()
demos3 = pd.DataFrame()
demos4 = pd.DataFrame()
demos5 = pd.DataFrame()
demos6 = pd.DataFrame()

for x in range(basisaar, sluttaar + 1):
    demos1['agrs' + str(x)] = [demo1['agr' + str(x)].sum()]
    demos1['pgs' + str(x)] = [demo1['pg' + str(x)].sum()]
    demos1['mgs' + str(x)] = [demo1['mg' + str(x)].sum()]

    demos2['agrs' + str(x)] = [demo2['agr' + str(x)].sum()]
    demos2['pgs' + str(x)] = [demo2['pg' + str(x)].sum()]
    demos2['mgs' + str(x)] = [demo2['mg' + str(x)].sum()]

    demos3['agrs' + str(x)] = [demo3['agr' + str(x)].sum()]
    demos3['pgs' + str(x)] = [demo3['pg' + str(x)].sum()]
    demos3['mgs' + str(x)] = [demo3['mg' + str(x)].sum()]

    demos4['agrs' + str(x)] = [demo4['agr' + str(x)].sum()]
    demos4['pgs' + str(x)] = [demo4['pg' + str(x)].sum()]
    demos4['mgs' + str(x)] = [demo4['mg' + str(x)].sum()]

    demos5['agrs' + str(x)] = [demo5['agr' + str(x)].sum()]
    demos5['pgs' + str(x)] = [demo5['pg' + str(x)].sum()]
    demos5['mgs' + str(x)] = [demo5['mg' + str(x)].sum()]

    demos6['agrs' + str(x)] = [demo6['agr' + str(x)].sum()]
    demos6['pgs' + str(x)] = [demo6['pg' + str(x)].sum()]
    demos6['mgs' + str(x)] = [demo6['mg' + str(x)].sum()]

x = demos1.pgs2020.loc[0]
demy1 = pd.DataFrame({'gruppe': ['ba', 'gr', 'fa', 'ph', 'py'],
                      'brind': [x, x, x, x, x]})

x = demos2.pgs2020.loc[0]
demy2 = pd.DataFrame({'gruppe': ['ba', 'gr', 'fa', 'ph', 'py'],
                      'brind': [x, x, x, x, x]})

x = demos3.pgs2020.loc[0]
demy3 = pd.DataFrame({'gruppe': ['ba', 'gr', 'fa', 'ph', 'py'],
                      'brind': [x, x, x, x, x]})

x = demos4.pgs2020.loc[0]
demy4 = pd.DataFrame({'gruppe': ['ba', 'gr', 'fa', 'ph', 'py'],
                      'brind': [x, x, x, x, x]})

x = demos5.pgs2020.loc[0]
demy5 = pd.DataFrame({'gruppe': ['ba', 'gr', 'fa', 'ph', 'py'],
                      'brind': [x, x, x, x, x]})

x = demos6.pgs2020.loc[0]
demy6 = pd.DataFrame({'gruppe': ['ba', 'gr', 'fa', 'ph', 'py'],
                      'brind': [x, x, x, x, x]})

arsv1 = pd.DataFrame()
arsv1 = demy1

arsvesp1 = tabeut[tabeut.index.get_level_values('sektor').isin([1])]
arsvesp1.reset_index(drop=True, inplace=True)
#print(arsvesp1.to_string())
arsvesp2 = tabeut[tabeut.index.get_level_values('sektor').isin([2])]
arsvesp2.reset_index(drop=True, inplace=True)

arsvesp3 = tabeut[tabeut.index.get_level_values('sektor').isin([3])]
arsvesp3.reset_index(drop=True, inplace=True)

arsvesp4 = tabeut[tabeut.index.get_level_values('sektor').isin([4])]
arsvesp4.reset_index(drop=True, inplace=True)

arsvesp5 = tabeut[tabeut.index.get_level_values('sektor').isin([5])]
arsvesp5.reset_index(drop=True, inplace=True)

arsvesp6 = tabeut[tabeut.index.get_level_values('sektor').isin([6])]
arsvesp6.reset_index(drop=True, inplace=True)

#print(asas.to_string())
#print(arsvesp.ar2)
arsv1['ar'] = arsvesp2#arsvesp.ar2
arsv1['stdrd'] = arsv1['ar'] / arsv1['brind']

arsv2 = pd.DataFrame()
arsv2 = demy2

arsv2['ar'] = arsvesp2#arsvesp.ar2
arsv2['stdrd'] = arsv2['ar'] / arsv2['brind']

arsv3 = pd.DataFrame()
arsv3 = demy3

arsv3['ar'] = arsvesp3#arsvesp.ar3
arsv3['stdrd'] = arsv3['ar'] / arsv3['brind']

arsv4 = pd.DataFrame()
arsv4 = demy4

arsv4['ar'] = arsvesp4#arsvesp.ar4
arsv4['stdrd'] = arsv4['ar'] / arsv4['brind']

arsv5 = pd.DataFrame()
arsv5 = demy5

arsv5['ar'] = arsvesp5#arsvesp.ar5
arsv5['stdrd'] = arsv5['ar'] / arsv5['brind']

arsv6 = pd.DataFrame()
arsv6 = demy6

arsv6['ar'] = arsvesp6#arsvesp.ar6
arsv6['stdrd'] = arsv6['ar'] / arsv6['brind']

demaar1 = pd.DataFrame({"aar": [basisaar], "dm1": [1], "dp1": [1], "dem1": demos1['agrs2020']})

for x in range(basisaar + 1, sluttaar + 1):
    nyrad = pd.DataFrame({"aar": x,
                          "dm1": demos1['mgs' + str(x)] / demos1['mgs2020'],
                          "dp1": (demos1['pgs' + str(x)] / demos1['pgs2020']) /
                                 (demos1['mgs' + str(x)] / demos1['mgs2020']),
                          "dem1": demos1['agrs' + str(x)]})
    demaar1 = pd.concat([demaar1, nyrad], ignore_index=True)

demaar2 = pd.DataFrame({"aar": [basisaar], "dm2": [1], "dp2": [1], "dem2": demos2['agrs2020']})

for x in range(basisaar + 1, sluttaar + 1):
    nyrad = pd.DataFrame({"aar": x,
                          "dm2": demos2['mgs' + str(x)] / demos2['mgs2020'],
                          "dp2": (demos2['pgs' + str(x)] / demos2['pgs2020']) /
                                 (demos2['mgs' + str(x)] / demos2['mgs2020']),
                          "dem2": demos2['agrs' + str(x)]})
    demaar2 = pd.concat([demaar2, nyrad], ignore_index=True)

demaar3 = pd.DataFrame({"aar": [basisaar], "dm3": [1], "dp3": [1], "dem3": demos3['agrs2020']})

for x in range(basisaar + 1, sluttaar + 1):
    nyrad = pd.DataFrame({"aar": x,
                          "dm3": demos3['mgs' + str(x)] / demos3['mgs2020'],
                          "dp3": (demos3['pgs' + str(x)] / demos3['pgs2020']) /
                                 (demos3['mgs' + str(x)] / demos3['mgs2020']),
                          "dem3": demos3['agrs' + str(x)]})
    demaar3 = pd.concat([demaar3, nyrad], ignore_index=True)

demaar4 = pd.DataFrame({"aar": [basisaar], "dm4": [1], "dp4": [1], "dem4": demos4['agrs2020']})

for x in range(basisaar + 1, sluttaar + 1):
    nyrad = pd.DataFrame({"aar": x,
                          "dm4": demos4['mgs' + str(x)] / demos4['mgs2020'],
                          "dp4": (demos4['pgs' + str(x)] / demos4['pgs2020']) /
                                 (demos4['mgs' + str(x)] / demos4['mgs2020']),
                          "dem4": demos4['agrs' + str(x)]})
    demaar4 = pd.concat([demaar4, nyrad], ignore_index=True)

demaar5 = pd.DataFrame({"aar": [basisaar], "dm5": [1], "dp5": [1], "dem5": demos5['agrs2020']})

for x in range(basisaar + 1, sluttaar + 1):
    nyrad = pd.DataFrame({"aar": x,
                          "dm5": demos5['mgs' + str(x)] / demos5['mgs2020'],
                          "dp5": (demos5['pgs' + str(x)] / demos5['pgs2020']) /
                                 (demos5['mgs' + str(x)] / demos5['mgs2020']),
                          "dem5": demos5['agrs' + str(x)]})
    demaar5 = pd.concat([demaar5, nyrad], ignore_index=True)

demaar6 = pd.DataFrame({"aar": [basisaar], "dm6": [1], "dp6": [1], "dem6": demos6['agrs2020']})

for x in range(basisaar + 1, sluttaar + 1):
    nyrad = pd.DataFrame({"aar": x,
                          "dm6": demos6['mgs' + str(x)] / demos6['mgs2020'],
                          "dp6": (demos6['pgs' + str(x)] / demos6['pgs2020']) /
                                 (demos6['mgs' + str(x)] / demos6['mgs2020']),
                          "dem6": demos6['agrs' + str(x)]})
    demaar6 = pd.concat([demaar6, nyrad], ignore_index=True)

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

dmindeks.rename(columns={"ds1": "barnplus",
                         "ds2": "grskplus",
                         "ds3": "viskplus",
                         "ds4": "uhskplus",
                         "ds5": "anskplus",
                         "ds6": "utskplus"},
                inplace=True)

dmindeks['totm'] = dmindeks.dem6

arsv = pd.concat([arsv1, arsv2, arsv3, arsv4, arsv5, arsv6])

# ******************************************************************
# NYKAND: Beregner antall uteksaminerte studenter over sim.perioden.
# Disse fordeles så etter alder og kjønn (for hvert år).
# ******************************************************************

opptak = opptak.reset_index()
opptak = opptak[opptak['aar'] > basisaar]

kandtot = opptak.merge(gjfoer, how='inner', on='yrke')

kandtot['uteks'] = kandtot.apply(lambda row: (row['oppfag'] * row['fullfob'])
                                 if row['aar'] + row['norm'] <= basisaar + 3
                                 else (row['oppfag'] * row['fullfor']), axis=1)

kandtot = kandtot.set_index(['yrke'])

nystud = nystud.set_index(['yrke'])

kand_ald = nystud.merge(kandtot, how='inner', on=['yrke'])

kand_ald["alder"] = kand_ald.alder + kand_ald.norm
kand_ald["eks_ald"] = kand_ald.uteks * kand_ald.st_ald

kandidater = pd.DataFrame()
kandidater = kand_ald

# *************************************************************
# NYBEHOLD: Fører strømmen av nyutdannete inn i beholdningen av
#           en yrkesgruppe, og framskriver beholdningen av fag-
#           utdannete over simuleringsperioden.
# *************************************************************

beh_pers['aar'] = basisaar
beh_paar = beh_pers.copy()

forrige_aar = beh_pers.copy()
forrige_aar.alder += 1

kand_aar = kandidater
kand_aar = kand_aar[kand_aar['aar'] == basisaar + 1]

neste_aar = forrige_aar.merge(kand_aar, how='outer', on=['yrke', 'kjonn', 'alder'])
neste_aar['pers'] = neste_aar['pers'].fillna(0)
neste_aar['eks_ald'] = neste_aar['eks_ald'].fillna(0)

neste_aar.pers = neste_aar.pers + neste_aar.eks_ald
neste_aar['aar'] = basisaar + 1

slutt = neste_aar[['yrke', 'kjonn', 'alder', 'pers', 'arsv', 'aar']]

beh_paar = pd.concat([beh_paar, slutt])
beh_paar.sort_values(by=['yrke', 'kjonn', 'alder'], inplace=True)

for x in range(basisaar + 2, sluttaar + 1):
    forrige_aar = beh_paar.copy()
    forrige_aar = forrige_aar[forrige_aar['aar'] == x-1]
    forrige_aar.alder += 1

    kand_aar = kandidater
    kand_aar = kand_aar[kand_aar['aar'] == x]

    neste_aar = forrige_aar.merge(kand_aar, how='outer', on=['yrke', 'kjonn', 'alder'])

    neste_aar['pers'] = neste_aar['pers'].fillna(0)
    neste_aar['eks_ald'] = neste_aar['eks_ald'].fillna(0)

    neste_aar.pers = neste_aar.pers + neste_aar.eks_ald
    neste_aar['aar'] = x

    slutt = neste_aar[['yrke', 'kjonn', 'alder', 'pers', 'arsv', 'aar']]

    beh_paar = pd.concat([beh_paar, slutt])
    beh_paar.sort_values(by=['yrke', 'kjonn', 'alder'], inplace=True)

# ************************************************************
# TILBUD: Beregner
#         årsverkstilbudet ut fra mønsteret i yrkesdeltakelsen
#         og eventuell eksogen økning i yrkesdeltakelsen.
# ************************************************************

tilb = beh_paar.merge(beh_syss, how='outer', on=['yrke', 'kjonn', 'alder'])

tilb['aarsverk'] = tilb.pers * tilb.syssand * tilb.garsv

tilb = tilb.groupby(['yrke', 'aar']).sum()

tilb = tilb.drop(['kjonn', 'alder', 'pers', 'arsv', 'syssand', 'garsv'], axis=1)

# ******************************************
# TILB-ESP: Sluttproduktet fra simuleringen.
# ******************************************

dmindeks['yrke'] = 'ba'
ind1 = dmindeks.copy()
dmindeks['yrke'] = 'gr'
ind2 = dmindeks.copy()
dmindeks['yrke'] = 'fa'
ind3 = dmindeks.copy()
dmindeks['yrke'] = 'ph'
ind4 = dmindeks.copy()
dmindeks['yrke'] = 'py'
ind5 = dmindeks.copy()

ind = pd.concat([ind1, ind2, ind3, ind4, ind5])
ind = ind.reset_index()

data_frames = [ind, aarsverk_ettersporsel, vakesp]

esp = reduce(lambda left, right: pd.merge(left, right, on=['yrke'],
                                          how='outer'), data_frames)

esp = esp.reset_index()
esp = esp.set_index(['yrke', 'aar'])

esp['epd1'] = (esp.ar1 + esp.vak1) * esp.dm1 * esp.barnplus
esp['ep1'] = (esp.ar1 + esp.vak1) * esp.dm1 * esp.barnplus
esp['epd2'] = (esp.ar2 + esp.vak2) * esp.dm2 * esp.grskplus
esp['ep2'] = (esp.ar2 + esp.vak2) * esp.dm2 * esp.grskplus
esp['epd3'] = (esp.ar3 + esp.vak3) * esp.dm3 * esp.viskplus
esp['ep3'] = (esp.ar3 + esp.vak3) * esp.dm3 * esp.viskplus
esp['epd4'] = (esp.ar4 + esp.vak4) * esp.dm4 * esp.uhskplus
esp['ep4'] = (esp.ar4 + esp.vak4) * esp.dm4 * esp.uhskplus
esp['epd5'] = (esp.ar5 + esp.vak5) * esp.dm5 * esp.anskplus
esp['ep5'] = (esp.ar5 + esp.vak5) * esp.dm5 * esp.anskplus
esp['epd6'] = (esp.ar6 + esp.vak6) * esp.dm6 * esp.utskplus
esp['ep6'] = (esp.ar6 + esp.vak6) * esp.dm6 * esp.utskplus

esp['espd'] = esp['epd1'] + esp['epd2'] + esp['epd3'] + esp['epd4'] + esp['epd5'] + esp['epd6']
esp['esp'] = esp['ep1'] + esp['ep2'] + esp['ep3'] + esp['ep4'] + esp['ep5'] + esp['ep6']
esp['vaksum'] = esp['vak1'] + esp['vak2'] + esp['vak3'] + esp['vak4'] + esp['vak5'] + esp['vak6']
esp['asum'] = esp['ar1'] + esp['ar2'] + esp['ar3'] + esp['ar4'] + esp['ar5'] + esp['ar6']

t_e = tilb.merge(esp, how='outer', on=['yrke', 'aar'])

t_e['vakans'] = t_e.aarsverk - t_e.espd

t_e = t_e[['esp', 'aarsverk', 'vakans']]

t_e.rename(columns={"aarsverk": "Tilbud",
                    "esp": "Etterspørsel",
                    "vakans": "Vakanse"}, inplace=True)

custom_dict = {'ba': 1, 'gr': 2, 'fa': 3, 'ph': 4, 'py': 5}
t_e = t_e.sort_values(by=['yrke', 'aar'], key=lambda x: x.map(custom_dict))

t_e.index.names = ['Utdanning', 'År']

t_e.rename(index={'ba': 'Barnehagelærer'}, inplace=True)
t_e.rename(index={'gr': 'Grunnskolelærer'}, inplace=True)
t_e.rename(index={'fa': 'Faglærer'}, inplace=True)
t_e.rename(index={'ph': 'PPU Universitet og høyskole'}, inplace=True)
t_e.rename(index={'py': 'PPU Yrkesfag'}, inplace=True)

pd.options.display.multi_sparse = False

t_e.round(0).astype(int).to_csv("resultater/Lærermod.csv")
t_e.round(0).astype(int).to_excel("resultater/Lærermod.xlsx")

print(t_e.round(0).astype(int).to_string())

print()
print('Lærermod er nå ferdig.')
print()

totaltid = time.time() - starttid

print(f'Og det tok {totaltid:.2f} sekunder. Velkommen tilbake.')
print()
