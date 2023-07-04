import pandas as pd

i1_syss = 'inndata/syssutd2021.txt'
i1_utd = 'inndata/utd2021_dat.txt'
st = 'inndata/nye_studenter.txt'

o1 = 'utdata/aarsverk.dat'
o2 = 'utdata/beholdning.dat'
ut = 'utdata/nye_studenter.dat'

# **********
# Konstanter
# **********

sektorer = [1, 2, 3, 4, 5, 6]
grupper = [1, 2, 3, 4, 5]

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

tabet['sysst'] = tabet.apply(lambda row: row['syssm'] + row['syssk'] if row ['syssm'] >= 0
                             and row['syssk'] >= 0 else row['syssm'] if row['syssm'] >= 0
                             else row['syssk'], axis=1)

tabet['aavt'] = tabet.apply(lambda row: row['aavm'] + row['aavk'] if row ['aavm'] >= 0
                             and row['aavk'] >= 0 else row['aavm'] if row['aavm'] >= 0
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

# *****************************
# Skriver ut fil med årsverkene
# *****************************

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

taberak = (tabera.T)

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

# *******************************
# Skriver ut fil med beholdningen
# *******************************

tabtot.to_csv(o2, float_format='%.5f', sep=' ', header=False, index=False)

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
