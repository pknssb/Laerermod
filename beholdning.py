import pandas as pd

i1_syss = 'inndata/syssutd2021.txt'
i1_utd = 'inndata/utd2021_dat.txt'
st = 'inndata/nye_studenter.txt'

o1 = 'inndata/aarsverk.dat'
o2 = 'inndata/beholdning.dat'
ut = 'inndata/nye_studenter.dat'

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
                                  if row ['bestand'] > 0
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

tabe = tabe[tabe['gruppe'] >= 1]
tabe = tabe[tabe['gruppe'] <= 5]

tabe.sort_values(by=['gruppe', 'sektor'], inplace=True)

# ********************
# Opprettelse av taber
# ********************

taber = pd.DataFrame()

taber = tabet.copy()

taber = taber[taber['studium'] == 'an']

taber.drop(['studium'], axis=1, inplace=True)

# *********************
# Proc Summary på tabet
# *********************

tabet = tabet.groupby(['studium', 'sektor']).agg(['sum'])

print(tabet)

"""

PROC SUMMARY DATA = tabet;
    CLASS studium sekt;
    VAR syssm syssk sysst aavm aavk aavt;
    OUTPUT OUT = tabet SUM = syssm syssk sysst aavm aavk aavt;

DATA tabet(KEEP = studium sekt syssm syssk sysst aavm aavk aavt);
    SET tabet;
    IF studium GT '  ' OR (studium = '  ' AND sekt = .);
"""

# ********************
# Proc Summary på tabe
# ********************

tabe = tabe.groupby(['gruppe', 'sektor']).syssm.sum()# .agg(['sum'])
tabe_gruppe = tabe.groupby(['gruppe']).agg(['sum'])
tabe_sektor = tabe.groupby(['sektor']).agg(['sum'])
tabe_total = tabe.agg("sum", axis="rows")
#subtotals = tabe.groupby(['gruppe']).agg({'syssm': ['sum']})
#tabe = tabe.append(tabe_gruppe, ignore_index=True)
print(tabe)
print(tabe_gruppe)
print(tabe_sektor)
print(tabe_total)


"""

PROC SUMMARY DATA = tabe;
    CLASS gr sekt;
    VAR syssm syssk sysst aavm aavk aavt;
    OUTPUT OUT = tabe SUM = syssm syssk sysst aavm aavk aavt;

DATA tabe(KEEP = gr sekt syssm syssk sysst aavm aavk aavt)
     tabes(KEEP = sekt syssm syssk sysst aavm aavk aavt)
     tabeg(KEEP = gr syssm syssk sysst aavm aavk aavt)
     tabesg(KEEP = sekt gr syssm syssk sysst aavm aavk aavt);
    SET tabe;
  
    IF gr GT 0 AND sekt GT 0 THEN 
	    OUTPUT tabe;
    ELSE IF gr GT 0 THEN 
	    OUTPUT tabeg;
    ELSE IF sekt GT 0 THEN 
	    OUTPUT tabes;
    ELSE OUTPUT 
	    tabesg;

DATA tabes;
    SET tabes;
    RENAME syssm = syssms syssk = syssks aavm = aavms aavk = aavks;

PROC SORT DATA = tabe;
    BY sekt gr;

DATA tabea(KEEP = sekt andms1 - andms5 andks1 - andks5 andmt1 - andmt5 andkt1 - andkt5);
    MERGE tabe tabes;
    BY sekt;
  
    ARRAY andms(5) andms1 - andms5;
    ARRAY andks(5) andks1 - andks5;
    ARRAY andmt(5) andmt1 - andmt5;
    ARRAY andkt(5) andkt1 - andkt5;
    RETAIN andms1 - andms5 andks1 - andks5 andmt1 - andmt5 andkt1 - andkt5 0;
  
    andms(gr) = syssm / syssms;
    andks(gr) = syssk / syssks;
    andmt(gr) = aavm / aavms;
    andkt(gr) = aavk / aavks;
  
    IF gr = 5 THEN 
	    OUTPUT tabea;

PROC SORT DATA = taber;
    BY sekt;

DATA taberg1(KEEP = sekt sysma1 - sysma5 syska1 - syska5 aavma1 - aavma5 aavka1 - aavka5);
    MERGE tabea (IN = A) taber (IN = B);
    BY sekt;
    IF A AND B;
  
    ARRAY andms(5) andms1 - andms5;
    ARRAY andks(5) andks1 - andks5;
    ARRAY andmt(5) andmt1 - andmt5;
    ARRAY andkt(5) andkt1 - andkt5;
    ARRAY sysma(5) sysma1 - sysma5;
    ARRAY syska(5) syska1 - syska5;
    ARRAY aavma(5) aavma1 - aavma5;
    ARRAY aavka(5) aavka1 - aavka5;
  
    sysmt = 0;
    syskt = 0;
    sysms = 0;
    sysks = 0;
  
    DO i = 1 TO 5;
        aavma(i) = aavm * andmt(i);
        aavka(i) = aavk * andkt(i);
        sysma(i) = syssm * andms(i);
        syska(i) = syssk * andks(i);
        sysmt + sysma(i);
        syskt + syska(i);
    END;

DATA taberg(KEEP = sekt gr syssmr sysskr sysstr aavmr aavkr aavtr);
    SET taberg1;
    ARRAY sysma(5) sysma1 - sysma5;
    ARRAY syska(5) syska1 - syska5;
    ARRAY aavma(5) aavma1 - aavma5;
    ARRAY aavka(5) aavka1 - aavka5;
  
    DO gr = 1 TO 5;
        syssmr = sysma(gr);
        sysskr = syska(gr);
        aavmr = aavma(gr);
        aavkr = aavka(gr); 
        sysstr = syssmr + sysskr;
        aavtr = aavmr + aavkr;
     
	    OUTPUT taberg;
    END;

DATA tabetot(KEEP = sekt gr syssm syssk sysst aavm aavk aavt);
    MERGE tabe taberg;
    BY sekt gr;
  
    aavm = aavm + aavmr;
    aavk = aavk + aavkr;
    aavt = aavt + aavtr;
    syssm = syssm + syssmr;
    syssk = syssk + sysskr;
    sysst = sysst + sysstr;

PROC SORT DATA = tabetot;
    BY gr sekt;

PROC SUMMARY DATA = tabetot;
    CLASS gr;
    VAR syssm syssk sysst aavm aavk aavt;
    OUTPUT OUT = tabetots SUM = syssm syssk sysst aavm aavk aavt;

DATA tabetots(KEEP = gr syssm syssk sysst aavm aavk aavt);
    SET tabetots;

DATA tabeut(KEEP = studium aav1 - aav6);
    SET tabetot;
  
    ARRAY aav(sekt) aav1 - aav6;
    RETAIN aav1 - aav6 0;
  
    IF gr = 1 THEN 
	    studium = 'ba';
    ELSE IF gr = 2 THEN 
	    studium = 'gr';
    ELSE IF gr = 3 THEN 
	    studium = 'fa';
    ELSE IF gr = 4 THEN 
	    studium = 'ph';
	ELSE IF gr = 5 THEN
	    studium = 'py';
  
    aav = aavt;
  
    FILE o1;
    IF sekt = 6 THEN DO;
        OUTPUT tabeut;
        PUT @1(studium)($CHAR2.) @3(aav1 - aav6)(6.);
	END;
	
PROC SORT DATA = taberg;
    BY gr;

PROC SUMMARY DATA = taberg;
    CLASS gr;
    VAR syssmr sysskr aavmr aavkr;
    OUTPUT OUT = tabergs SUM=syssmr sysskr aavmr aavkr;

DATA tabergs(KEEP = a gr syssmr sysskr sysstr aavmr aavkr aavtr)
     tabers(KEEP = a syssmrs sysskrs sysstrs aavmrs aavkrs aavtrs);
    SET tabergs;

    a = 0;
    sysstr = syssmr + sysskr;
    aavtr = aavmr + aavkr;
  
    IF gr GT 0 THEN 
	    OUTPUT tabergs;
    ELSE DO;
        syssmrs = syssmr;
        sysskrs = sysskr;
        aavmrs = aavmr;
        aavkrs = aavkr;
        sysstrs = syssmrs + sysskrs;
        aavtrs = aavmrs + aavkrs;
      
	    OUTPUT tabers;
    END;

DATA tabera(KEEP = a andms1 - andms5 andks1 - andks5 andmt1 - andmt5 andkt1 - andkt5);
    MERGE tabergs tabers;
    BY a;

    ARRAY andms(5) andms1 - andms5;
    ARRAY andks(5) andks1 - andks5;
    ARRAY andmt(5) andmt1 - andmt5;
    ARRAY andkt(5) andkt1 - andkt5;
    RETAIN andms1 - andms5 andks1 - andks5 andmt1 - andmt5 andkt1 - andkt5 0;
  
    andms(gr) = syssmr / syssmrs;
    andks(gr) = sysskr / sysskrs;
    andmt(gr) = aavmr / aavmrs;
    andkt(gr) = aavkr / aavkrs;
  
    IF gr = 5 THEN 
	    OUTPUT tabera;
		
DATA taberak(KEEP = kj alder ands1 - ands5 andt1 - andt5);
    SET tabera;

    ARRAY andms(5) andms1 - andms5;
    ARRAY andks(5) andks1 - andks5;
    ARRAY andmt(5) andmt1 - andmt5;
    ARRAY andkt(5) andkt1 - andkt5;
    ARRAY ands(5) ands1 - ands5;
    ARRAY andt(5) andt1 - andt5;

    DO alder = 20 TO 74;
        DO kj = 1 TO 2;
            DO gr = 1 TO 5;
                IF kj = 1 THEN 
				    ands(gr) = andms(gr);
                ELSE 
				    ands(gr) = andks(gr);
          
		        IF kj = 1 THEN 
				    andt(gr) = andmt(gr);
                ELSE 
				    andt(gr) = andkt(gr);
            END;
       
	        OUTPUT taberak;
        END;
    END;
	
PROC SORT DATA = taberak;
    BY kj alder;

DATA tab;
	SET o1_utd;  
    
	IF syss GT 0 AND tpa GT 0 THEN 
	    aav = syss * tpa;
    ELSE 
	    aav = 0;

PROC SUMMARY DATA = tab;
    CLASS studium;
    VAR best syss aav;
    OUTPUT OUT = tabs SUM = bests sysss aavs;

DATA tabs(KEEP = studium bests sysss aavs);
    SET tabs;

DATA tabap(KEEP = studium kj alder best syss aav)
     tabg(KEEP = studium kj alder best syss aav yp);
    SET tab;
    IF studium NE 'st' AND studium NE 'sp';
 
    IF studium = 'an' THEN 
	    OUTPUT tabap;
    ELSE 
	    OUTPUT tabg;

PROC SORT DATA = tabg;
    BY studium;

PROC SUMMARY DATA = tabg;
    CLASS studium;
    VAR best syss aav;
    OUTPUT OUT = tabgs SUM = bests sysss aavs;

DATA tabgs(KEEP = studium bests sysss aavs);
    SET tabgs;

PROC SUMMARY DATA = tabap;
    CLASS studium;
    VAR best syss aav;
    OUTPUT OUT = tabaps SUM = bests sysss aavs;

DATA tabaps(KEEP = studium bests sysss aavs);
    SET tabaps;

DATA tabgg(KEEP = gr kj alder best syss aav);
    SET tabg;
  
    IF studium = 'ba' THEN 
	    gr = 1;
    ELSE IF studium = 'gr' THEN 
	    gr = 2;
    ELSE IF studium = 'fa' THEN 
	    gr = 3;
    ELSE IF studium = 'ph' THEN 
	    gr = 4;
	ELSE IF studium = 'py' THEN
	    gr = 5;

DATA taberk1(KEEP = kj alder besa1 - besa5 sysa1 - sysa5 aava1 - aava5 syss syst);
    MERGE tabap(IN = A) taberak(IN = B);
    BY kj alder;
    IF A;

    ARRAY ands(5) ands1 - ands5;
    ARRAY andt(5) andt1 - andt5;
    ARRAY besa(5) besa1 - besa5;
    ARRAY sysa(5) sysa1 - sysa5;
    ARRAY aava(5) aava1 - aava5;
  
    bestt = 0;
    syst = 0;
    anstst = 0;
    
	DO i = 1 TO 5;
        aava(i) = aav * andt(i);
        sysa(i) = syss * ands(i);
        besa(i) = best * ands(i);
        syst + sysa(i);
        bestt + besa(i);
    END;
	
DATA taberk(KEEP = gr kj alder bestr syssr aavr);
    SET taberk1;
  
    ARRAY besa(5) besa1 - besa5;
    ARRAY sysa(5) sysa1 - sysa5;
    ARRAY aava(5) aava1 - aava5;
	
    DO gr = 1 TO 5;
        bestr = besa(gr);
        syssr = sysa(gr);
        aavr = aava(gr);
     
	    OUTPUT taberk;
    END;

PROC SUMMARY DATA = taberk;
    CLASS gr;
    VAR bestr syssr aavr;
    OUTPUT OUT = taberks SUM = bestr syssr aavr;

PROC SORT DATA = tabgg;
    BY gr kj alder;

PROC SORT DATA = taberk;
    BY gr kj alder;

DATA tabtot(KEEP = gr kj alder bests sysss aavs yp tp);
    MERGE tabgg taberk;
    BY gr kj alder;
  
    IF best = . THEN 
	    bests = bestr;
    ELSE IF bestr = . THEN 
	    bests = best;
    ELSE 
	    bests = best + bestr;
  
    IF aav = . THEN 
	    aavs = aavr;
    ELSE IF aavr = . THEN 
	    aavs = aav;
    ELSE 
	    aavs = aav + aavr;
  
    IF syss = . THEN 
	    sysss = syssr;
    ELSE IF syssr = . THEN 
	    sysss = syss;
    ELSE 
	    sysss = syss + syssr;
  
    IF bests = 0 THEN 
	    yp = 0;
    ELSE 
	    yp = sysss / bests;
  
    IF sysss = 0 THEN 
	    tp = 0;
    ELSE 
	    tp = aavs / sysss;

PROC SORT DATA = tabtot;
    BY gr;

PROC SUMMARY DATA = tabtot;
    CLASS gr;
    VAR bests sysss aavs;
    OUTPUT OUT = tabtots SUM = bests sysss aavs;

DATA tabut(KEEP = studium kj alder bests sysss yp tp aavs);
    SET tabtot;
  
    IF gr = 1 THEN 
	    studium = 'ba';
    ELSE IF gr = 2 THEN 
	    studium = 'gr';
    ELSE IF gr = 3 THEN 
	    studium = 'fa';
    ELSE IF gr = 4 THEN 
	    studium = 'ph';
	ELSE IF gr = 5 THEN
	    studium = 'py';
  
FILE o2;
    PUT @1(studium)($CHAR2.) kj 4 alder 6-7 @8(bests sysss)(10.3) @28(yp tp aavs)(10.5);

DATA studa;
    INFILE st;
    INPUT stud $ 1-2 alder 9-10 bs 18-22 bm 26-30 bk 34-38;
	    
	IF stud = 'ba' THEN
	    teller = 1;
    ELSE IF stud = 'gr' THEN
	    teller = 2;
    ELSE IF stud = 'fa' THEN
	    teller = 3;
    ELSE IF stud = 'ph' THEN
	    teller = 4;
	ELSE IF stud = 'py' THEN
        teller = 5;
	ELSE IF stud = 'sp' THEN
	    teller = 6;

PROC SORT DATA = studa;
    BY teller;

PROC SUMMARY DATA = studa;
    CLASS teller;
    VAR bs;
    OUTPUT OUT = studs SUM = bss;

DATA studs(KEEP = teller bss);
    SET studs;
    IF teller > 0;

DATA taba;
    MERGE studa studs;
    BY teller;
	
    bs = bs / bss;
    bm = bm / bss;
    bk = bk / bss;
  
    IF teller = 1 THEN
	    studium = 'ba';
    ELSE IF teller = 2 THEN
	    studium = 'gr';
    ELSE IF teller = 3 THEN
	    studium = 'fa';
    ELSE IF teller = 4 THEN
	    studium = 'ph';
	ELSE IF teller = 5 THEN
		studium = 'py';
    ELSE IF teller = 6 THEN
		studium = 'sp';
	
FILE ut;
    PUT @1(studium)($CHAR2.) alder 9-10 @15(bs bm bk)(8.4);
	
	
run;

"""
