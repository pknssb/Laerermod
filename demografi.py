"""

filename i1 '/ssb/stamme02/laermod/wk48/new/inndata/mmmm_2022.txt';
filename i2 '/ssb/stamme02/laermod/wk48/new/inndata/antall_barn_barnehager.txt';

filename b1 '/ssb/stamme02/laermod/wk48/g2021/inndata/barnehage.dat';
filename e1 '/ssb/stamme02/laermod/wk48/g2021/inndata/grunnskole.dat';
filename e2 '/ssb/stamme02/laermod/wk48/g2021/inndata/andre_skoler.dat';


%MACRO les_barn;

    DATA bef1(KEEP = alder kj a2020 a2021)
         bef2(KEEP = alder kj a2020 a2021)
         bef3(KEEP = alder kj a2020 a2021)
         bef4(KEEP = alder kj a2020 a2021);
        INFILE i1 lrecl = 430;
        INPUT alder 1-2 kj 4 @5(a1980 - a2040)(6.);
  
        IF alder = 0 THEN
		    OUTPUT bef1;
        ELSE IF alder < 3 THEN 
		    OUTPUT bef2;
        ELSE IF alder < 4 THEN 
		    OUTPUT bef3;
        ELSE IF alder < 6 THEN 
		    OUTPUT bef4;

    DATA barnhin;
        INFILE i2;
        INPUT aar 1-4 ti1 6-7 ti2 9-10 @11(ba1 - ba6)(8.);
		IF aar EQ 2021;

    PROC SORT DATA = barnhin;
        BY ti1;

    DATA barn1(KEEP = tim ald1 ald2 b2021)
         barn2(KEEP = tim ald1 ald2 b2021)
         barn3(KEEP = tim ald1 ald2 b2021)
         barn4(KEEP = tim ald1 ald2 b2021);
        SET barnhin;
        
		RETAIN akk b2021 0;
  
        tim = ti1 + (ti2 - ti1) / 2;
        akk + 1;
		
        ald1 = 0;
        ald2 = 0;
        b2021 = ba1;
  
        OUTPUT barn1;
  
        ald1 = 1;
        ald2 = 2;
        b2021 = ba2 + ba3;
  
        OUTPUT barn2;
  
        ald1 = 3;
        ald2 = 3;
        b2021 = ba4;
  
        OUTPUT barn3;
  
        ald1 = 4;
        ald2 = 5;
        b2021 = ba5 + ba6;
  
        OUTPUT barn4;

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

%MEND les_barn;


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


%les_barn
%summer_barn(1)
%summer_barn(2)
%summer_barn(3)
%summer_barn(4)
%skriv_barn

%les_elev
%summer_elev(5)
%summer_elev(6)
%skriv_elev

run;

"""