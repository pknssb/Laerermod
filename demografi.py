import pandas as pd

i1 = 'inndata/mmmm_2022.txt'
i2 = 'inndata/antall_barn_barnehager.txt'

b1 = 'inndata/barnehage.dat'
e1 = 'inndata/grunnskole.dat'
e2 = 'inndata/andre_skoler.dat'

bef1 = pd.DataFrame()
bef2 = pd.DataFrame()
bef3 = pd.DataFrame()
bef4 = pd.DataFrame()

befs1 = pd.DataFrame()
befs2 = pd.DataFrame()
befs3 = pd.DataFrame()
befs4 = pd.DataFrame()

def les_barn():

    global bef1
    
    bef1 = pd.read_csv(i1,
                       header=None,
                       delimiter=" ",
                       names=['alder',
                              'kjonn',
                              'a2020',
                              'a2021'],
                       skiprows=range(2, 200),
                       usecols=[1, 2, 43, 44])

    global bef2

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

    global bef3

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

    global bef4

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


"""
%MACRO les_barn;

    DATA barnut(KEEP = ald1 ald2 bu bri);
        ald1 = 0;
        ald2 = 0;
        bu = 0;
        bri = 1.000000;
  
        IF ald1 > 0;

    DATA befut(KEEP = ald1 ald2 agr2020 agr2021);
        ald1 = 0;
        ald2 = 0;
        agr2020 = 0;
        agr2021 = 0;
  
        IF ald1 > 0;

%MEND les_barn
"""


def summer_barn(inn, ut):

    ut = pd.DataFrame()

    ut = inn.groupby(['a2020', 'a2021']).sum()

    ut.sort_values(by=['alder', 'kjonn'], inplace=True)

    print(ut)
    
"""

%MACRO summer_barn(n);

    PROC SUMMARY DATA = bef&n;
        VAR a2020 a2021;
        OUTPUT OUT = befs&n SUM = agr2020 agr2021;

    DATA befs&n(KEEP = ald1 ald2 agr2020 agr2021);
        SET befs&n;
  
        IF &n = 1 THEN 
		    ald1 = 0;
        ELSE IF &n = 2 THEN 
		    ald1 = 1;
        ELSE IF &n = 3 THEN 
		    ald1 = 3;
        ELSE IF &n = 4 THEN 
		    ald1 = 4;
  
        IF &n = 1 THEN 
		    ald2 = 0;
        ELSE IF &n = 2 THEN 
		    ald2 = 2;
        ELSE IF &n = 3 THEN 
		    ald2 = 3;
        ELSE IF &n = 4 THEN 
		    ald2 = 5;

    DATA barna&n(KEEP = ald1 ald2 bu bri);
        SET barn&n;
        
		ARRAY bs(6) bs1 - bs6;
        ARRAY b(6) b1 - b6;
        
		RETAIN akk bs1 - bs6 b1 - b6 0;
  
        akk + 1;
        bs(akk) = b2021 * tim;
        b(akk) = b2021;

        IF akk = 6 THEN DO;
            bsu = 0;
            bu = 0;
     
	        DO i = 1 TO 6;
                bsu = bsu + bs(i);
                bu = bu + b(i);
            END;
     
	        IF &n < 3 THEN 
			    bi = 2;
            ELSE IF &n < 4 THEN 
			    bi = 1.5;
            ELSE 
			    bi = 1;
     
	        bri = bi * (bsu / (bu * 42.5));
     
	        OUTPUT barna&n;
        END;
		
    DATA barnut;
        SET barnut barna&n;

    DATA befut;
        SET befut befs&n;
	
%MEND summer_barn;


%MACRO skriv_barn;

    DATA barnr(KEEP = ald1 ald2 bri bu ans1 - ans2 antaar agr2020 agr2021);
        MERGE befut barnut;
        BY ald1;
        
		ARRAY ans(2) ans1 - ans2;
  
        antaar = 2;
        ans(1) = bu / agr2021;
  
        IF ald1 = 0 THEN 
		    ans(2) = 1.05 * ans(1);
        ELSE IF ald1 = 1 THEN 
		    ans(2) = 1.12 * ans(1);
        ELSE IF ald1 = 3 THEN 
		    ans(2) = 1.12 * ans(1);
        ELSE IF ald1 = 4 THEN 
		    ans(2) = 1.12 * ans(1);
		
        IF ans(2) GT 0.95 THEN 
		    ans(2) = 0.97;
		
    DATA barnu;
        SET barnr;
        FILE b1;
  
        PUT ald1 1-2 ald2 4-5 @7(bu)(8.) (bri)(8.4) antaar 24 @25(ans1 - ans2)(7.4);

%MEND skriv_barn;


%MACRO les_elev;

    DATA bef1(KEEP = alder kj a2021)
         bef2(KEEP = alder kj a2021)
         bef3(KEEP = alder kj a2021)
         bef4(KEEP = alder kj a2021)
         bef5(KEEP = alder kj a2021)
         bef6(KEEP = alder kj a2021);
        INFILE i1 lrecl = 430;
        INPUT alder 1-2 kj 4 @5(a1980 - a2040)(6.);
  
        OUTPUT bef6;
  
        IF alder = 0 THEN 
		    OUTPUT bef1;
        ELSE IF alder < 3 THEN
		    OUTPUT bef2;
        ELSE IF alder < 4 THEN 
		    OUTPUT bef3;
        ELSE IF alder < 6 THEN 
		    OUTPUT bef4;
        ELSE IF alder < 16 THEN 
		    OUTPUT bef5;
			
%MEND les_elev;


%MACRO summer_elev(n);

    PROC SUMMARY DATA = bef&n;
        VAR a2021;
        
		OUTPUT OUT = befs&n SUM = agr2021;

    DATA befs&n(KEEP = ald1 ald2 agr2021);
        SET befs&n;
  
        IF &n = 1 THEN 
		    ald1 = 0;
        ELSE IF &n = 2 THEN 
		    ald1 = 1;
        ELSE IF &n = 3 THEN 
		    ald1 = 3;
        ELSE IF &n = 4 THEN 
		    ald1 = 4;
        ELSE IF &n = 5 THEN 
		    ald1 = 6;
        ELSE IF &n = 6 THEN 
		    ald1 = 0;
  
        IF &n = 1 THEN 
		    ald2 = 0;
        ELSE IF &n = 2 THEN 
		    ald2 = 2;
        ELSE IF &n = 3 THEN 
		    ald2 = 3;
        ELSE IF &n = 4 THEN 
		    ald2 = 5;
        ELSE IF &n = 5 THEN 
		    ald2 = 15;
        ELSE IF &n = 6 THEN 
		    ald2 = 99;
				
%MEND summer_elev;


%MACRO skriv_elev;

    DATA befs5;
        SET befs5;
  
        bri = 1.000000;
        antaar = 0;
  
        FILE e1;
        PUT ald1 1-2 ald2 4-5 @7(agr2021)(8.) (bri)(8.4) antaar 24;

    DATA befs6;
        SET befs6;
  
        bri = 1.000000;
        antaar = 0;
		
        FILE e2;
        PUT ald1 1-2 ald2 4-5 @7(agr2021)(8.) (bri)(8.4) antaar 24;

%MEND skriv_elev;
"""

les_barn()

summer_barn(bef1, befs1)
summer_barn(bef2, befs2)
summer_barn(bef3, befs3)
summer_barn(bef4, befs4)

"""
%skriv_barn

%les_elev
%summer_elev(5)
%summer_elev(6)
%skriv_elev

run;

"""
