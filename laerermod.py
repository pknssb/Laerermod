print()
print('Velkommen til Python-versjonen av Lærermod!')
print()

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

import pandas as pd

import beholdning
import demografi

"""
beholdning.lag_tabse_syss()
beholdning.lag_o1_syss()
"""

"""
/* Deklarasjon av globale variable */
%global basaar simslutt subst subaarst subaarsl vakaar befvekst arbtid estudpln
priobarn priofosk priogrsk priovisk priouhsk prioansk prioutsk yrke
oekstba oekstgr oekstvi oekstun oekstan oekstut
oekslba oekslgr oekslvi oekslun oekslan oekslut;

/* HOVEDVALG FORUT FOR KJØRINGEN   */
%let yrke = alle; /* Utdanningstype. Alternativt, skriv "alle" for å */
                  /* oppnå fremskrivinger av alle de 5 gruppene      */

%LET subst = 0;   /* Det skal gjøres beregning med forutsetning om  */
                  /* substitusjon mellom grupper                    */
"""
basaar = 2020
simslutt = 2040

subaarst = 2020
subaarsl = 2020

vakaar = 2020


innb = 'inndata/mmmm_2022.txt'
stkap = 'inndata/fullforingsgrader.txt'
oppta = 'inndata/opptak.txt'
vak = 'inndata/vakanse.txt'

dem3 = 'inndata/antall_elever_videregaende.txt'
dem4 = 'inndata/antall_studenter_hoyereutdanning.txt'

innpr = 'inndata/standard.txt'
inplu = 'inndata/endring_timeverk.txt'

# Filer produsert av beholdning.sas
bhl = 'utdata/beholdning.dat'
aarsv = 'utdata/aarsverk.dat'
nystu = 'utdata/nye_studenter.dat'

# Filer produsert av demografi.sas
dem1 = 'utdata/barnehage.dat';
dem2 = 'inndata/grunnskole.dat';
dem5 = 'inndata/andre_skoler.dat';
dem6 = 'inndata/andre_skoler.dat';


"""
/********************************************************************/

filename resultba "/ssb/stamme02/laermod/wk48/g2021/resultater/referansebane/ba";
filename resultgr "/ssb/stamme02/laermod/wk48/g2021/resultater/referansebane/gr";
filename resultfa "/ssb/stamme02/laermod/wk48/g2021/resultater/referansebane/fa";
filename resultph "/ssb/stamme02/laermod/wk48/g2021/resultater/referansebane/ph";
filename resultpy "/ssb/stamme02/laermod/wk48/g2021/resultater/referansebane/py";
filename resultla "/ssb/stamme02/laermod/wk48/g2021/resultater/referansebane/la";

filename o1       "/ssb/stamme02/laermod/wk48/g2021/resultater/referansebane/samle";

/********************************************************************/

%let arbtid = 1.0;   /* arbtid = 1.1 betyr 10 prosent økt arbeidstid  */
%let estudpln = 1.0; /* Varig endring i studiekapasitet i Norge       */
%let estudplu = 1.0; /* Varig endring i studiekapasitet i utlandet    */

/* POLITISKE PRIORITERINGER angitt ved prosentvis stillingsvekst  */
/* i et aktivitetsområde ved 1,0 prosent vekst i BNP pr. capita   */
/* (Prio**** = 1.0000 betyr 1 prosent økning)                     */

%LET priobarn = 1;
%LET priogrsk = 1;
%LET priovisk = 1;
%LET priouhsk = 1;
%LET prioansk = 1;
%LET prioutsk = 1;

%LET oekstba = 2020;
%LET oekstgr = 2020;
%LET oekstvi = 2020;
%LET oekstun = 2020;
%LET oekstan = 2020;
%LET oekstut = 2020;

%LET oekslba = 2020;
%LET oekslgr = 2020;
%LET oekslvi = 2020;
%LET oekslun = 2020;
%LET oekslan = 2020;
%LET oekslut = 2020;
"""

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
                     names=["yrka", "norm", "fullfor", "fullfob"])

innles = pd.DataFrame()

innles = pd.read_fwf(oppta,
                     header=None,
                     delimiter=" ",
                     names=["aar", "ba", "gr", "fa", "ph", "py", "sp"])

innles = innles.set_index(['aar'])

ba = pd.DataFrame()
ba['oppfag'] = innles['ba']
ba.loc[:, 'yrka'] = 'ba'

gr = pd.DataFrame()
gr['oppfag'] = innles['gr']
gr.loc[:, 'yrka'] = 'gr'

fa = pd.DataFrame()
fa['oppfag'] = innles['fa']
fa.loc[:, 'yrka'] = 'fa'

ph = pd.DataFrame()
ph['oppfag'] = innles['ph']
ph.loc[:, 'yrka'] = 'ph'

py = pd.DataFrame()
py['oppfag'] = innles['py']
py.loc[:, 'yrka'] = 'py'

opptak = pd.concat([ba, gr, fa, ph, py])

plussakt = pd.DataFrame()

plussakt = pd.read_fwf(inplu,
                       header=None,
                       delimiter=" ",
                       names=["alder", "plussm", "plussk"])

nystud = pd.read_fwf(nystu,
                     header=None,
                     delimiter=" ",
                     names=["yrka", "alder", "st", "stm", "stk"])

beholdning = pd.DataFrame()
beholdning = pd.read_csv(bhl,
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

beh_pers = pd.DataFrame()
beh_syss = pd.DataFrame()


"""
%MACRO lesinn;


    DATA beh_pers(KEEP=yrka aar kj alder pers arsv)
         beh_syss(KEEP=yrka kj alder syss_and garsv);
        INFILE bhl;
       INPUT (stj)($CHAR1.)@;

        IF substr(stj,1,1) NE '*';

                    INPUT yrka        $ 1-2
              kj              4
              alder         6-7
              @8(pers syss) (10.3)
              @28(syss_and garsv tarsv)(10.5);
  *           @8(pers syss) (10.3)
              @28(syss_and garsv)(10.5);

        arsv = pers * syss_and * garsv;
        aar = &basaar;
"""
arsvesp = pd.DataFrame()

arsvesp = pd.read_fwf(aarsv,
                      header=None,
                      delimiter=" ",
                      names=["yrka", "ar1", "ar2", "ar3", "ar4", "ar5", "ar6"])

vakesp = pd.DataFrame()

vakesp = pd.read_fwf(vak,
                     header=None,
                     delimiter=" ",
                     names=["yrka", "vak1", "vak2", "vak3", "vak4", "vak5", "vak6"])

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

stand = stand[stand['aar'] >= basaar]
stand = stand[stand['aar'] <= simslutt]

# ****************************************
# Oppretter datasett for senere utfylling.
# ****************************************

filnavn = ['dem1', 'dem2', 'dem3', 'dem4', 'dem5', 'dem6']
aldersnavn = ['ald1', 'ald2', 'ald3', 'ald4', 'ald5', 'ald6']
demografinavn = ['demo1', 'demo2', 'demo3', 'demo4', 'demo5', 'dem6']

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

demo2 = pd.DataFrame()

demo2 = pd.read_fwf(dem2,
                    header=None,
                    delimiter=" ",
                    names=["ald1",
                           "ald2",
                           "br",
                           "bri",
                           "antaar"])
"""
demo2 = pd.read_csv(dem2,
                    engine='python',
                    header=None,
                    delimiter=r'[\t:;: ]',
                    names=['ald1',
                           'ald2',
                           'br',
                           'bri',
                           'antaar'],
                    usecols=[0, 1, 2, 4, 5],
                    dtype={'ald1': 'int',
                           'ald2': 'int',
                           'br': 'float',
                           'bri': 'float',
                           'antaar': 'int'})
"""

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

demo5 = pd.DataFrame()

demo5 = pd.read_fwf(dem5, colspecs=kolonneposisjoner, header=None)
demo5.columns = kolonnenavn

demo6 = pd.DataFrame()

demo6 = pd.read_fwf(dem6,
                    header=None,
                    delimiter=" ",
                    names=["ald1",
                           "ald2",
                           "br",
                           "bri",
                           "antaar"])


"""


%MACRO lesd(n);

    DATA demo&n(KEEP=ald1 ald2 br bri antaar dg1 - dg6)
         ald&n(keep=ald1 ald2);
        INFILE dem&n;
        INPUT ald1 1-2 ald2 4-5 @7(br)(8.) (bri)(8.4) antaar 19 @;

        IF antaar GT 0 THEN DO;
            ARRAY dg (6) dg1 - dg6;

                        DO i = 1 TO antaar;
                INPUT (dg(i))(7.4) @;
            END;
        END;

%MEND lesd;

%MACRO styr_les;

    %DO n = 1 %TO 6;
        %lesd(&n)
    %END;

%MEND styr_les;
"""
# ************************************************
# LAGER ALDERSAGGREGATER av befolkningsfilen etter
# gruppering i den aktuelle etterspørselsfil
# ************************************************

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


demo2 = demo2.set_index(['ald2'])

for x in range(2020, 2041):
    demo2['agr' + str(x)] = bef2['a' + str(x)]

demo2['pg2020'] = demo2.br * demo2.bri

for x in range(2021, 2041):
    demo2['pg' + str(x)] = demo2['pg' + str(x-1)] * (bef2['a' + str(x)] / bef2['a' + str(x-1)])

demo2['mg2020'] = demo2.br * demo2.bri

for x in range(2021, 2041):
    demo2['mg' + str(x)] = demo2['mg' + str(x-1)] * (bef2['a' + str(x)] / bef2['a' + str(x-1)])

demo3 = demo3.set_index(['ald2'])

for x in range(2020, 2041):
    demo3['agr' + str(x)] = bef3['a' + str(x)]

demo3['pg2020'] = demo3.br * demo3.bri

for x in range(2021, 2041):
    demo3['pg' + str(x)] = demo3['pg' + str(x-1)] * (bef3['a' + str(x)] / bef3['a' + str(x-1)])

demo3['mg2020'] = demo3.br * demo3.bri

for x in range(2021, 2041):
    demo3['mg' + str(x)] = demo3['mg' + str(x-1)] * (bef3['a' + str(x)] / bef3['a' + str(x-1)])

demo4 = demo4.set_index(['ald2'])

for x in range(2020, 2041):
    demo4['agr' + str(x)] = bef4['a' + str(x)]

demo4['pg2020'] = demo4.br * demo4.bri

for x in range(2021, 2041):
    demo4['pg' + str(x)] = demo4['pg' + str(x-1)] * (bef4['a' + str(x)] / bef4['a' + str(x-1)])

demo4['mg2020'] = demo4.br * demo4.bri

for x in range(2021, 2041):
    demo4['mg' + str(x)] = demo4['mg' + str(x-1)] * (bef4['a' + str(x)] / bef4['a' + str(x-1)])

demo5 = demo5.set_index(['ald2'])

for x in range(2020, 2041):
    demo5['agr' + str(x)] = bef5['a' + str(x)]

demo5['pg2020'] = demo5.br * demo5.bri

for x in range(2021, 2041):
    demo5['pg' + str(x)] = demo5['pg' + str(x-1)] * (bef5['a' + str(x)] / bef5['a' + str(x-1)])

demo5['mg2020'] = demo5.br * demo5.bri

for x in range(2021, 2041):
    demo5['mg' + str(x)] = demo5['mg' + str(x-1)] * (bef5['a' + str(x)] / bef5['a' + str(x-1)])

demo6 = demo5

demos2 = pd.DataFrame()
demos3 = pd.DataFrame()
demos4 = pd.DataFrame()
demos5 = pd.DataFrame()
demos6 = pd.DataFrame()

for x in range(2020, 2041):
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

arsv2 = pd.DataFrame()

arsv2 = demy2

arsv2['ar'] = arsvesp.ar2
arsv2['stdrd'] = arsv2['ar'] / arsv2['brind']

arsv3 = pd.DataFrame()

arsv3 = demy3

arsv3['ar'] = arsvesp.ar3
arsv3['stdrd'] = arsv3['ar'] / arsv3['brind']

arsv4 = pd.DataFrame()

arsv4 = demy4

arsv4['ar'] = arsvesp.ar4
arsv4['stdrd'] = arsv4['ar'] / arsv4['brind']

arsv5 = pd.DataFrame()

arsv5 = demy5

arsv5['ar'] = arsvesp.ar5
arsv5['stdrd'] = arsv5['ar'] / arsv5['brind']

arsv6 = pd.DataFrame()

arsv6 = demy6

arsv6['ar'] = arsvesp.ar6
arsv6['stdrd'] = arsv6['ar'] / arsv6['brind']

demaar2 = pd.DataFrame({"aar": [2020], "dm2": [1], "dp2": [1], "dem2": demos2['agrs2020']})

for x in range(2021, 2041):
    nyrad = pd.DataFrame({"aar": x,
                          "dm2": demos2['mgs' + str(x)] / demos2['mgs2020'],
                          "dp2": (demos2['pgs' + str(x)] / demos2['pgs2020']) / 
                                 (demos2['mgs' + str(x)] / demos2['mgs2020']),
                          "dem2": demos2['agrs' + str(x)]})
    demaar2 = pd.concat([demaar2, nyrad], ignore_index=True)

demaar3 = pd.DataFrame({"aar": [2020], "dm3": [1], "dp3": [1], "dem3": demos3['agrs2020']})

for x in range(2021, 2041):
    nyrad = pd.DataFrame({"aar": x,
                          "dm3": demos3['mgs' + str(x)] / demos3['mgs2020'],
                          "dp3": (demos3['pgs' + str(x)] / demos3['pgs2020']) / 
                                 (demos3['mgs' + str(x)] / demos3['mgs2020']),
                          "dem3": demos3['agrs' + str(x)]})
    demaar3 = pd.concat([demaar3, nyrad], ignore_index=True)

demaar4 = pd.DataFrame({"aar": [2020], "dm4": [1], "dp4": [1], "dem4": demos4['agrs2020']})

for x in range(2021, 2041):
    nyrad = pd.DataFrame({"aar": x,
                          "dm4": demos4['mgs' + str(x)] / demos4['mgs2020'],
                          "dp4": (demos4['pgs' + str(x)] / demos4['pgs2020']) / 
                                 (demos4['mgs' + str(x)] / demos4['mgs2020']),
                          "dem4": demos4['agrs' + str(x)]})
    demaar4 = pd.concat([demaar4, nyrad], ignore_index=True)

demaar5 = pd.DataFrame({"aar": [2020], "dm5": [1], "dp5": [1], "dem5": demos5['agrs2020']})

for x in range(2021, 2041):
    nyrad = pd.DataFrame({"aar": x,
                          "dm5": demos5['mgs' + str(x)] / demos5['mgs2020'],
                          "dp5": (demos5['pgs' + str(x)] / demos5['pgs2020']) / 
                                 (demos5['mgs' + str(x)] / demos5['mgs2020']),
                          "dem5": demos5['agrs' + str(x)]})
    demaar5 = pd.concat([demaar5, nyrad], ignore_index=True)

demaar6 = pd.DataFrame({"aar": [2020], "dm6": [1], "dp6": [1], "dem6": demos6['agrs2020']})

for x in range(2021, 2041):
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

dmindeks = stand.merge(demaar2, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar3, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar4, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar5, how='inner', on='aar')
dmindeks = dmindeks.merge(demaar6, how='inner', on='aar')

dmindeks.rename(columns={"ds2": "grskplus",
                         "ds3": "viskplus",
                         "ds4": "uhskplus",
                         "ds5": "anskplus",
                         "ds6": "utskplus"},
                inplace=True)

dmindeks['totm'] = dmindeks.dem6

arsv = pd.concat([arsv2, arsv3, arsv4, arsv5, arsv6])

# ******************************************************************
# NYKAND: Beregner antall uteksaminerte studenter over sim.perioden.
# Disse fordeles så etter alder og kjønn (for hvert år).
# ******************************************************************

opptak = opptak.reset_index()
opptak = opptak[opptak['aar'] > basaar]

kandtot = opptak.merge(gjfoer, how='inner', on='yrka')

kandtot["uteks"] = kandtot.oppfag * kandtot.fullfor

#kandtot['uteks'] = kandtot.apply(lambda row: kandtot.oppfag * kandtot.fullfor if row['aar'] == '2030'
#                             else kandtot.oppfag * kandtot.fullfor, axis=1)

kandtot = kandtot.set_index(['aar', 'yrka'])

print(kandtot.to_string())

"""
%MACRO nykand;

    DATA kandtot(KEEP = yrka aar uteks norm);
        MERGE gjfoer opptak;
        BY yrka;

        aar = aar + norm;

        IF aar LE (&basaar + 3) THEN
                                   uteks = oppfag * fullfob;
        ELSE
                                   uteks = oppfag * fullfor;

        IF aar GE (&basaar + 1) AND aar LE &simslutt;

    DATA nystud;
        SET nystud;

        DO aar = (&basaar + 1) TO &simslutt;
            OUTPUT nystud;
        END;

    PROC SORT DATA = nystud;
        BY yrka aar kj alder;

    DATA kand_ald(KEEP = yrka aar kj alder eks_ald);
        MERGE nystud kandtot;
        BY yrka aar;

        alder = alder + norm;
        eks_ald = uteks * st_ald;

        IF alder LE 74;

    DATA plussts;
        SET plussakt;

        DO aar = (&basaar + 1) TO &simslutt;
            OUTPUT plussts;
        END;

    PROC SORT DATA = plussts;
        BY yrka aar kj alder;

    /* Rutine som sikrer at hele aldersskalaen fylles ut før MERGE med dødelighet  */
    DATA kand_ald(DROP = pluss);
        MERGE kand_ald (IN = A) plussts (IN = B);
        BY yrka aar kj alder;
        IF B;
        IF NOT A THEN
                                   eks_ald = 0;

    PROC SORT DATA = kand_ald;
        BY aar kj alder yrka;

    DATA kandidater;
                    SET kand_ald;

    PROC SORT DATA = kandidater;
        BY yrka aar kj alder;

    PROC SORT DATA = beh_pers;
        BY yrka kj alder;

    PROC SORT DATA = plussakt;
        BY yrka kj alder;

    DATA beh_pers(DROP = pluss);
        MERGE beh_pers (IN = A) plussakt (IN = B);
        BY yrka kj alder;
        IF B;
        IF NOT A THEN
                                   pers = 0;
        IF NOT A THEN
                                   aar = %EVAL(&basaar);

%MEND nykand;

/**********************************************************************/
/*                                                                    */
/* NYBEHOLD: Fører strømmen av nyutdannete inn i beholdningen av      */
/*          en yrkesgruppe, og framskriver beholdningen av fag-       */
/*          utdannete over simuleringsperioden.                       */
/*                                                                    */
/**********************************************************************/
%MACRO nybehold;

    %DO aarn = %EVAL(&basaar + 1) %TO &simslutt;

        DATA kand_aar;
            SET kandidater;
            IF aar = &aarn;

        DATA beh_paar(DROP = aar);
            SET beh_pers;
            IF aar = &aarn - 1;

            alder = alder + 1;
            IF alder LE 74;

        /* Rutine som sikrer at hele aldersskalaen fylles ut før MERGE med tilvekst */
        DATA beh_paar(DROP = pluss);
            MERGE beh_paar (IN = A) plussakt (IN = B);
            BY yrka kj alder;
            IF B;
            IF NOT A THEN
                                                   pers = 0;

        DATA beh_paar(KEEP = yrka aar kj alder pers eks_ald);
            MERGE beh_paar kand_aar;
            BY yrka kj alder;

            pers = pers + eks_ald;

        DATA beh_pers;
            SET beh_pers beh_paar;

    %END;

%MEND nybehold;

/********************************************************************/
/*                                                                  */
/* TILBUD: Beregner                                                 */
/*         årsverkstilbudet ut fra mønsteret i yrkesdeltakelsen     */
/*         og eventuell eksogen økning i yrkesdeltakelsen.          */
/*                                                                  */
/********************************************************************/
%MACRO tilbud;

    PROC SORT DATA = beh_syss;
        BY yrka kj alder;

    DATA beh_syss;
        MERGE beh_syss(IN = A) plussakt(IN = B);
        BY yrka kj alder;
        IF B;
        IF NOT A THEN
                                   syss_and = 0;
        IF NOT A THEN
                                   garsv = 0;

    PROC SORT DATA = beh_pers;
        BY yrka kj alder aar;

    DATA tilb;
        MERGE beh_pers beh_syss(IN = B);
        BY yrka kj alder;

        aarsv = pers * syss_and * garsv * pluss;

        IF aar > &basaar THEN
                                   aarsv = aarsv * &arbtid;

    PROC SORT DATA = tilb;
        BY yrka aar;

    PROC SUMMARY DATA = tilb;
        CLASS yrka aar;
        VAR aarsv;
        OUTPUT OUT = tilb SUM = aarsv;

    DATA tilb(keep = yrka aar aarsv);
        SET tilb;
        IF aar GT 0 AND yrka GT '  ';

%MEND tilbud;

/******************************************************************/
/*                                                                */
/*  TILB-ESP: Sluttproduktet fra simuleringen.                    */
/*                                                                */
/******************************************************************/
%MACRO espbasis;

    DATA ind;
        MERGE dmindeks laerebnp;
        BY aar;

    DATA ind(KEEP = yrka aar dm1 - dm6 dp1 - dp6 ds1 - ds6 pr1 - pr6);
        SET ind;

        DO i = 1 TO 5;
            IF i = 1 THEN
                                                   yrka = 'ba';
            ELSE IF i = 2 THEN
                                                   yrka = 'gr';
            ELSE IF i = 3 THEN
                                                   yrka = 'fa';
            ELSE IF i = 4 THEN
                                                   yrka = 'ph';
                                               ELSE IF i = 5 THEN
                                                   yrka = 'py';

                        OUTPUT ind;
        END;

    PROC SORT DATA = ind;
        BY yrka aar;

    DATA esp;
        MERGE ind arsvesp vakesp;
        BY yrka;

    DATA esp;
        SET esp;
        BY yrka;

        ARRAY dm(6) dm1 - dm6;
        ARRAY dp(6) dp1 - dp6;
        ARRAY ds(6) ds1 - ds6;
        ARRAY pr(6) pr1 - pr6;
        ARRAY ar(6) ar1 - ar6;
        ARRAY vaks(6) vaks1 - vaks6;
        ARRAY epd(6) epd1 - epd6;
        ARRAY ep(6) ep1 - ep6;

        esp = 0;
        espd = 0;
        vaksum = 0;
        asum = 0;

        DO i = 1 TO 6;
            epd(i) = (ar(i) + vaks(i)) * dm(i) * ds(i) * pr(i); /* dp(i) */
                                   ep(i) = (ar(i) + vaks(i)) * dm(i) * ds(i) * pr(i);  /* dp(i) */

                        espd = espd + epd(i);
            esp = esp + ep(i);
            vaksum = vaksum + vaks(i);
            asum = asum + ar(i);
        END;

    DATA tl_esp
         t_e(KEEP = yrka aar esp espd aarsv vakans)
         esp_sk0(KEEP = aar yrka ep1 - ep6 epd1 - epd6);
        MERGE tilb esp;
        BY yrka aar;

        vakans = aarsv - espd;

    %IF &vakaar GT &basaar AND (&subst = 0 OR &vakaar < &subaarst) %THEN %DO;
        DATA estl&vakaar(KEEP = yrka aar vakans va esp espk espd espdk
                                esp&vakaar espd&vakaar
                                epd&vakaar.1 - epd&vakaar.6 ep&vakaar.1 - ep&vakaar.6
                                dm&vakaar.1 - dm&vakaar.6 pr&vakaar.1 - pr&vakaar.6);
            SET tl_esp;

            ARRAY epd(i) epd1 - epd6;
            ARRAY ep(i) ep1 - ep6;
            ARRAY epd&vakaar(i) epd&vakaar.1 - epd&vakaar.6;
            ARRAY ep&vakaar(i) ep&vakaar.1 - ep&vakaar.6;
            ARRAY dm(i) dm1 - dm6;
            ARRAY pr(i) pr1 - pr6;
            ARRAY dm&vakaar(i) dm&vakaar.1 - dm&vakaar.6;
            ARRAY pr&vakaar(i) pr&vakaar.1 - pr&vakaar.6;

            n = %EVAL(&vakaar - &basaar);

            IF n = 1 THEN
                                                   va = lag1(vakans);
            ELSE IF n = 2 THEN
                                                   va = lag2(vakans);
            ELSE IF n = 3 THEN
                                                   va = lag3(vakans);
            ELSE IF n = 4 THEN
                                                   va = lag4(vakans);
            ELSE IF n = 5 THEN
                                                   va = lag5(vakans);

            IF aar = &vakaar;

            espk = 0;
            espdk = 0;
            esp&vakaar = esp - vakans + va;
            espd&vakaar = esp&vakaar / pr1;

            DO i = 1 TO 6;
                ep&vakaar = ep * esp&vakaar / esp;
                epd&vakaar = epd * espd&vakaar / espd;
                espk + ep&vakaar;
                espdk + epd&vakaar;
                dm&vakaar = dm;
                pr&vakaar = pr;
            END;

        DATA tl_esp
             t_e(KEEP = yrka aar esp espd aarsv vakans)
             esp_sk0(KEEP = aar yrka ep1 - ep6 epd1 - epd6);
            MERGE tl_esp estl&vakaar;
            BY yrka;

            ARRAY epd(i) epd1 - epd6;
            ARRAY ep(i) ep1 - ep6;
            ARRAY epd&vakaar(i) epd&vakaar.1 - epd&vakaar.6;
            ARRAY ep&vakaar(i) ep&vakaar.1 - ep&vakaar.6;
            ARRAY dm(i) dm1 - dm6;
            ARRAY pr(i) pr1 - pr6;
            ARRAY dm&vakaar(i) dm&vakaar.1 - dm&vakaar.6;
            ARRAY pr&vakaar(i) pr&vakaar.1 - pr&vakaar.6;

            espg = esp;
            espdg = espd;
            vakg =
            esp = 0;
            espd = 0;

            DO i = 1 TO 6;
                epd = epd&vakaar * dm / dm&vakaar;
                ep = ep&vakaar * dm * pr / (dm&vakaar * pr&vakaar);
                espd + epd;
                esp + ep;
            END;

            vakans = esp - aarsv;

    %END;

%MEND espbasis;

%MACRO summlaer;

    PROC SORT DATA = t_e;
        BY aar;

    PROC SUMMARY DATA = t_e;
        CLASS aar;
        VAR espd esp aarsv vakans;

        OUTPUT OUT = t_es SUM = espd esp aarsv vakans;

    DATA t_es(KEEP = yrka aar espd esp aarsv vakans);
        SET t_es;
        IF aar GT 0;

        yrka = 'la';

    DATA t_e;
        SET t_e t_es;

%MEND summlaer;

%MACRO skriv_laer;

    DATA skriv;
        SET t_e;
        IF yrka = "&yrke";

        FILE result&yrke;
        PUT @3(yrka)($CHAR2.) aar 8-11 @15(espd aarsv vakans)(10.);

%MEND skriv_laer;

%MACRO velgskr;

    %IF &yrke = alle %THEN %DO;
        %DO i = 1 %TO 6;
            %IF &i = 1 %THEN %DO;
                                                   %LET yrke = ba;
                                               %END;

                        %IF &i = 2 %THEN %DO;
                                                   %LET yrke = gr;
                                               %END;

                        %IF &i = 3 %THEN %DO;
                                                   %LET yrke = fa;
                                               %END;

                        %IF &i = 4 %THEN %DO;
                                                   %LET yrke = ph;
                                               %END;

                                               %IF &i = 5 %THEN %DO;
                                                   %LET yrke = py;
                                               %END;

                        %IF &i = 6 %THEN %DO;
                                                   %LET yrke = la;
                                               %END;

                        %skriv_laer
        %END;
    %END;
    %ELSE %DO;
                    %skriv
                %END;

%MEND velgskr;

%MACRO skrive_samle(n);

    DATA skriv&n;
        IF &n = 1 THEN DO;
            INFILE resultba;
        END;

        IF &n = 2 THEN DO;
            INFILE resultgr;
        END;

        IF &n = 3 THEN DO;
            INFILE resultfa;
        END;

        IF &n = 4 THEN DO;
            INFILE resultph;
        END;

        IF &n = 5 THEN DO;
            INFILE resultpy;
        END;

        IF &n = 6 THEN DO;
            INFILE resultla;
        END;

        INPUT @3(yrka)($CHAR2.) aar 8-11 @15(espd aarsverk vakanser)(10.);

        gr = %EVAL(&n);

%MEND skrive_samle;

%MACRO styr_samle;

    %DO n = 1 %TO 6;
        %IF n = 1 %THEN %DO;
            %LET yrke = ba;
        %END;

        %IF n = 2 %THEN %DO;
            %LET yrke = gr;
        %END;

        %IF n = 3 %THEN %DO;
            %LET yrke = fa;
        %END;

        %IF n = 4 %THEN %DO;
            %LET yrke = ph;
        %END;

        %IF n = 5 %THEN %DO;
            %LET yrke = py;
        %END;

        %IF n = 6 %THEN %DO;
            %LET yrke = la;
        %END;

        %skrive_samle(&n)
    %END;

%MEND styr_samle;

%MACRO samle_samle;
    DATA skriv;
        SET skriv1 skriv2 skriv3 skriv4 skriv5 skriv6;
    DATA samle;
        SET skriv;
        BY gr;
        FILE o1;

        IF _N_ = 1 THEN DO;
            d0 = 'Referansebane 2022                           ';
            PUT @1(d0)($CHAR54.);
            d0 = '                                                  ';
            PUT @1(d0)($CHAR54.);
            d1 = 'Aar';
            d2 = 'Ettersp';
            d3 = 'Tilbud';
            d4 = 'Vakans';
            PUT @8(d1)($CHAR3.) @18(d2)($CHAR10.) @29(d3)($CHAR10.)(d4)($CHAR6.);
        END;

        IF FIRST.gr THEN DO;
            d0 = '                                                  ';
            PUT @1(d0)($CHAR54.);

                        IF yrka = 'ba' THEN
                                                   d0 = 'Barnehagelærere              ';

                                               IF yrka = 'gr' THEN
                                                   d0 = 'Grunnskolelærere             ';

                        IF yrka = 'fa' THEN
                                                   d0 = 'Faglærere                    ';

                        IF yrka = 'ph' THEN
                                                   d0 = 'PPU UH                       ';

                        IF yrka = 'py' THEN
                                                   d0 = 'PPU YF                       ';

                        IF yrka = 'la' THEN
                                                   d0 = 'Alle lærere                  ';

                        PUT @8(d0)($CHAR47.);

                        d0 = '                                                  ';

                        PUT @1(d0)($CHAR54.);

            PUT (yrka)($CHAR2.) aar 8-11 @15(espd aarsverk vakanser)(10.);
        END;
        ELSE DO;
            PUT (yrka)($CHAR2.) aar 8-11 @15(espd aarsverk vakanser)(10.);
       END;

%MEND samle_samle;
"""
#lesinn()
#styr_les()
#aggre()

"""

%nykand
%nybehold
%tilbud
%espbasis

%summlaer
%velgskr

%styr_samle
%samle_samle

"""

print()
print('Lærermod er nå ferdig.')
