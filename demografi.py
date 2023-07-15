import pandas as pd

i1 = 'inndata/mmmm_2022.txt'
i2 = 'inndata/antall_barn_barnehager.txt'

b1 = 'utdata/barnehage.dat'
e1 = 'utdata/grunnskole.dat'
e2 = 'utdata/andre_skoler.dat'

# ****************************************
# Innlesing av folkemengden i alder 0-5 år
# ****************************************

bef1 = pd.DataFrame()

bef1 = pd.read_csv(i1,
                   header=None,
                   delimiter=" ",
                   names=['alder',
                          'kjonn',
                          'a2020',
                          'a2021'],
                   skiprows=range(2, 200),
                   usecols=[1, 2, 43, 44])

bef2 = pd.DataFrame()

bef2 = pd.read_csv(i1,
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

bef3 = pd.read_csv(i1,
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

bef4 = pd.read_csv(i1,
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

# ***********************************
# Skriver ut fil med barn i barnehage
# ***********************************

barnr.to_csv(b1,
             columns=['ald1',
                      'ald2',
                      'agr2020',
                      'agr2021',
                      'bu',
                      'bri',
                      'ans1',
                      'ans2',
                      'antaar'],
             float_format='%.10f',
             sep=';',
             header=False,
             index=False)

# ******************************************************
# Innlesing av folkemengden i grunnskole og andre skoler
# ******************************************************

kolonneposisjoner = [(0, 2), (3, 4), (245, 250), (251, 256)]
kolonnenavn = ['alder', 'kjonn', 'a2020', 'a2021']

fwf = pd.DataFrame()

fwf = pd.read_fwf(i1, colspecs=kolonneposisjoner, header=None)
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

# **************************************
# Skriver ut fil med elever i grunnskole
# **************************************

befs5.to_csv(e1,
             columns=['ald1',
                      'ald2',
                      'agr2020',
                      'agr2021',
                      'bri',
                      'antaar'],
             float_format='%.10f',
             sep=' ',
             header=False,
             index=False)

# ****************************************
# Skriver ut fil med elever i andre skoler
# ****************************************

befs6.to_csv(e2,
             columns=['ald1',
                      'ald2',
                      'agr2020',
                      'agr2021',
                      'bri',
                      'antaar'],
             float_format='%.10f',
             sep=' ',
             header=False,
             index=False)
