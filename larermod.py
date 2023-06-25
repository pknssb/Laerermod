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

import beholdning

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

"""
filename innb     '/ssb/stamme02/laermod/wk48/g2021/inndata/mmmm_2022.txt';
filename dem3     '/ssb/stamme02/laermod/wk48/g2021/inndata/antall_elever_videregaende.txt';
filename dem4     '/ssb/stamme02/laermod/wk48/g2021/inndata/antall_studenter_hoyereutdanning.txt';
filename vak      '/ssb/stamme02/laermod/prog/vakanse.txt';
filename oppta    '/ssb/stamme02/laermod/wk48/g2021/inndata/opptak.txt';
filename inbnp    '/ssb/stamme02/laermod/prog/g2021/referansebane/bnp.txt';
filename innpr    '/ssb/stamme02/laermod/prog/g2021/referansebane/standard.txt';
filename inplu    '/ssb/stamme02/laermod/prog/g2021/referansebane/endring_timeverk.txt';
filename stkap    '/ssb/stamme02/laermod/wk48/g2017/inndata/fullforingsgrader.txt';

/* Spesifikasjon av substitusjon. */
filename subi     '/ssb/stamme02/laermod/prog/g2021/referansebane/substind.dat';
filename subst    '/ssb/stamme02/laermod/prog/g2021/referansebane/substst.dat';
filename subsl    '/ssb/stamme02/laermod/prog/g2021/referansebane/substsl.dat';

/* Filer produsert av beholdning.sas */
filename bhl      '/ssb/stamme02/laermod/wk48/g2021/inndata/beholdning.dat';
filename aarsv    '/ssb/stamme02/laermod/wk48/g2021/inndata/aarsverk.dat';
filename nystu    '/ssb/stamme02/laermod/wk48/g2021/inndata/nye_studenter.dat';

/* Filer produsert av demografi.sas */
filename dem1     '/ssb/stamme02/laermod/wk48/g2021/inndata/barnehage.dat';
filename dem2     '/ssb/stamme02/laermod/wk48/g2021/inndata/grunnskole.dat';
filename dem5     '/ssb/stamme02/laermod/wk48/g2021/inndata/andre_skoler.dat';
filename dem6     '/ssb/stamme02/laermod/wk48/g2021/inndata/andre_skoler.dat';

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

%MACRO lesinn;

    DATA bef;
        INFILE innb lrecl = 430;
        INPUT alder 1-2 kj 4 @5(a1980 - a2050)(6.);

    /* LESER inn fullføringsgrader */
    DATA gjfoer;
        INFILE stkap;
        INPUT (stj)($CHAR1.)@;
        IF substr(stj, 1, 1) NE '*';
        INPUT yrka $ 1-2  norm 15 @24(fullfor fullfob)(5.2);

    PROC SORT DATA = gjfoer;
        BY yrka;

    /* LESER inn indeks for tidsserie opptak     */
    DATA opptak(KEEP = yrka aar oppfag);
        INFILE oppta;
        INPUT (stj)($CHAR1.)@;
        IF substr(stj, 1, 1) NE '*';
        INPUT aar 1-4 @5(oppt1 - oppt5)(8.);

                    ARRAY oppt (i) oppt1 - oppt5;

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

                        oppfag = oppt;

                        OUTPUT opptak;
        END;

    PROC SORT DATA = opptak;
        BY yrka aar;

    /* Prosentvis endring i gjennomsnittlig timeverkstilbud. Denne merges med   */
    /* begynnerstudentenes aldersfordeling forå få alle alderstrinn med på fil. */
    DATA plussakt(KEEP = kj alder pluss);
        INFILE inplu;
        INPUT alder 1-2 plussm 4-6 plussk 8-10;
        IF alder GE 17 AND alder LE 74;

        kj = 1;
        pluss = plussm;

        OUTPUT plussakt;

        kj = 2;
        pluss = plussk;

        OUTPUT plussakt;

    DATA plussakt(KEEP = yrka kj alder pluss);
        SET plussakt;

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

                        OUTPUT plussakt;
        END;

    /* Nye studenter fordelt på kjønn og alder ifølge opplysninger fra utdanningsregisteret. */
    DATA nystud(KEEP = yrka kj alder st_ald);
        INFILE nystu;
        INPUT (stj)($CHAR1.)@;

        IF substr(stj, 1, 1) NE '*';
        INPUT yrka $ 1-2 alder 9-10  @23(stm stk)(8.0);

        kj = 1;
        st_ald = stm;

        OUTPUT nystud;
        kj = 2;
        st_ald = stk;

        OUTPUT nystud;

    PROC SORT DATA = nystud;
        BY yrka kj alder;

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

    DATA arsvesp;
        INFILE aarsv;
        INPUT yrka $ 1-2 @3(ar1 - ar6)(6.);

    PROC SORT DATA=arsvesp;
        BY yrka;

    DATA vakesp;
        INFILE vak;
        INPUT yrka $ 1-2 @3(vaks1 - vaks6)(6.);

    PROC SORT DATA = vakesp;
        BY yrka;

    /* Opplysninger om substitusjon               */
    DATA substi;
        INFILE subi;
        INPUT sk 1-2 @3(sigr1 - sigr4)(3.);

    DATA substst;
        INFILE subst;
        INPUT sk 1-2 @3(stgr1 - stgr4)(6.2);

    DATA substsl;
        INFILE subsl;
        INPUT sk 1-2 @3(slgr1 - slgr4)(6.2);

    /* Referansebane for BNP-utvikling i MODAG.   */
    DATA rf(KEEP = aar bnpvekst);
        INFILE inbnp;
        INPUT aar 1-4 @9(bnpvekst)(4.1);

    /*   PROSENTVIS ENDRING I ANTALL ELEVER pr. 1000 INNBYGGERE      */
    /*   ved de ulike aktivitetsområdene over simuleringsperioden    */
    /*   tallet 1.01 tolkes som 1 prosent økt elevtall pr. 1000      */
    DATA stand;
        INFILE innpr;
        INPUT aar 1-4 @5(barnplus grskplus viskplus uhskplus anskplus utskplus)(8.5);

        IF aar < &basaar THEN
                                   delete;
        IF aar > &simslutt THEN
                                   delete;

%MEND lesinn;

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

* LAGER ALDERSAGGREGATER av befolkningsfilen etter gruppering i *;
* den aktuelle etterspørselsfil                                 *;
%MACRO aggre(n);

    DATA ald&n(KEEP = alder ald2);
        SET ald&n;

        DO i = 0 TO (ald2 - ald1);
            alder = ald1 + i;

                        OUTPUT ald&n;
        END;

    DATA bef&n(keep = ald2 a1980 - a2050);
        MERGE bef(IN = A) ald&n(IN = B);
        BY alder;
        IF B;

    PROC SUMMARY DATA = bef&n;
        CLASS ald2;
        VAR a1980 - a2050;
        OUTPUT OUT = bef&n SUM = agr1980 - agr2050;

    DATA bef&n(KEEP = ald2 agr1980 - agr2050);
        SET bef&n;
        IF ald2 GE 0;

    DATA demo&n(KEEP = ald1 ald2 pg&basaar - pg&simslutt mg&basaar - mg&simslutt agr&basaar - agr&simslutt);
        MERGE bef&n demo&n;
        BY ald2;

        ARRAY dg(i) dg1 - dg6;
        ARRAY mg(1980:2050) mg1980 - mg2050;
        ARRAY pg(1980:2050) pg1980 - pg2050;
        ARRAY agr(1980:2050) agr1980 - agr2050;
        RETAIN akk 0;

        akk + 1;
        pg&basaar = br * bri;
        mg&basaar = br * bri;

        IF antaar = 0 THEN
                                   antaar = 1;

        IF antaar > 1 THEN DO;
            DO i = 2 to antaar;
                pg(&basaar + i - 1) = dg * bri * agr(&basaar + i - 1);
            END;
        END;

        DO i = (&basaar + 1) TO &simslutt;
            mg(i) = mg(&basaar) * agr(i) / agr(&basaar);
        END;

        DO i = (&basaar + antaar) TO &simslutt;
            pg(i) = pg(&basaar + antaar - 1) * agr(i) / agr(&basaar + antaar - 1);
        END;

    PROC SUMMARY DATA = demo&n;
        VAR pg&basaar - pg&simslutt mg&basaar - mg&simslutt agr&basaar - agr&simslutt;
        OUTPUT OUT = demos&n SUM = pgs&basaar - pgs&simslutt mgs&basaar - mgs&simslutt agrs&basaar - agrs&simslutt;

    DATA demy&n(KEEP = brind yrka);
        SET demos&n;

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

                        brind = pgs&basaar;

                        OUTPUT demy&n;
        END;

    PROC SORT DATA = demy&n;
        BY yrka;

    DATA arsv&n(KEEP = yrka stdrd brind);
        MERGE arsvesp demy&n;
        BY yrka;

        ars = ar&n;
        stdrd = ar&n / brind;

    DATA demaar&n(KEEP = aar dm&n dp&n dem&n);
        SET demos&n;

                               ARRAY pgs(1980:2050) pgs1980 - pgs2050;
        ARRAY mgs(1980:2050) mgs1980 - mgs2050;
        ARRAY agrs(1980:2050) agrs1980 - agrs2050;

        DO aar = &basaar TO &simslutt;
            dm&n = mgs(aar) / mgs(&basaar);
            dp&n = (pgs(aar) / pgs(&basaar)) / dm&n;
            dem&n = agrs(aar);

                        OUTPUT demaar&n;
        END;

%MEND aggre;

/*******************************************************************/
/*  Lager indeks for demografikomponenten i etterspørselen         */
/*  etter tjenester                                                */
/*******************************************************************/
%MACRO samle_demografi;

    DATA dmindeks(KEEP = aar dm1 - dm6 dp1 - dp6 ds1 - ds6 totm);
        MERGE demaar1 demaar2 demaar3 demaar4 demaar5 demaar6 stand;
        BY aar;

        ds1 = barnplus;
        ds2 = grskplus;
        ds3 = viskplus;
        ds4 = uhskplus;
        ds5 = anskplus;
        ds6 = utskplus;

        totm = dem6;

    DATA arsv;
        SET arsv1 arsv2 arsv3 arsv4 arsv5 arsv6;

%MEND samle_demografi;

/***********************************************************************/
/*      BNPKORR:                                                        */
/*      Danner demografisk korrigeringsfaktor til BNP-veksten           */
/*      Denne korrigeringsfaktoren benyttes når vi anslår vekst         */
/*      i BNP pr. capita                                                */
/***********************************************************************/
%MACRO bnpkorr;

    DATA bnpkorr (KEEP = bnpkorr aar);
        SET dmindeks(KEEP = aar totm);

        z = lag1(totm);

                    IF z = . THEN
                                   z = 1;

        bnpkorr = ((totm - z) / z);
        IF aar = &basaar THEN
                                   bnpkorr = 0.000;

%MEND bnpkorr;

/*******************************************************************/
/*           Beregner veksten i antall etterspurte årsverk på      */
/*           grunnlag av BNP-veksten, og den andel som kanaliseres */
/*           mot den aktuelle yrkesgruppe.                         */
/*******************************************************************/
%MACRO bnp;

    DATA rf;
        SET rf;

        bnpvekst = bnpvekst / 100;

        IF aar GE &basaar OR aar LE &simslutt;

    /* Korrigerer for befolkningsveksten, middels bef.vekst, og får */
    /* et mål på realvekst i økonomien pr. capita                   */
    DATA rf (keep = aar bnpvekst);
        MERGE rf(IN = A) bnpkorr(IN = B);
        BY aar;
        IF A AND B;
        bnpvekst = bnpvekst - bnpkorr;

        IF aar = &basaar THEN
                                   bnpvekst = 0.0000;

    /* Beregner spesifikk vekst for hver sektor */
    DATA laerebnp(KEEP = aar pp1 - pp6);
        SET rf;

        ARRAY pp(i) pp1 - pp6;

        DO i = 1 TO 6;
            pp = 0;
        END;

        IF aar GE &oekstba AND aar LE &oekslba THEN
                                   pp1 = bnpvekst * &priobarn;

        IF aar GE &oekstgr AND aar LE &oekslgr THEN
                                   pp2 = bnpvekst * &priogrsk;

        IF aar GE &oekstvi AND aar LE &oekslvi THEN
                                   pp3 = bnpvekst * &priovisk;

        IF aar GE &oekstun AND aar LE &oekslun THEN
                                   pp4 = bnpvekst * &priouhsk;

        IF aar GE &oekstan AND aar LE &oekslan THEN
                                   pp5 = bnpvekst * &prioansk;

        IF aar GE &oekstut AND aar LE &oekslut THEN
                                   pp6 = bnpvekst * &prioutsk;

    DATA laerebnp(keep = aar pr1 - pr6);
        ARRAY pr(i) pr1 - pr6;
        ARRAY lp(i) lp1 - lp6;
        ARRAY pp(i) pp1 - pp6;
        RETAIN lp1 - lp6 0;
        SET laerebnp;

        IF _N_ = 1 THEN DO;
            DO i = 1 TO 6;
                lp = 1;
            END;
        END;

        DO i = 1 TO 6;
            pr = lp * (1 + pp);
            lp = pr;
        END;

    DATA inde1(KEEP = aar dt1 - dt6)
         inde2;
        MERGE laerebnp dmindeks;
        BY aar;

        ARRAY dm(i) dm1 - dm6;
        ARRAY dp(i) dp1 - dp6;
        ARRAY ds(i) ds1 - ds6;
        ARRAY pr(i) pr1 - pr6;
        ARRAY dt(i) dt1 - dt6;

        DO i = 1 TO 6;
            dt = dm * dp * ds * pr;
        END;

%MEND bnp;

/**********************************************************************/
/*                                                                    */
/* NYKAND: Beregner antall uteksaminerte studenter over sim.perioden. */
/*         Disse fordeles så etter alder og kjønn (for hvert år)      */
/**********************************************************************/
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

%MACRO substi;

    %IF &subst = 1 %THEN %DO;
        DATA substs(KEEP = sk sigr1 - sigr4 stgr1 - stgr4 slgr1 - slgr4 ind skplus skmin );
            MERGE substi substst substsl;
            BY sk;

            ARRAY sigr (i) sigr1 - sigr4;

            ind = 0;

            DO i = 1 to 4;
                IF sigr NE 0 THEN
                                                                   ind = 1;
                IF sigr = 1 THEN
                                                                   skplus = i;
                IF sigr = -1 THEN
                                                                   skmin = i;
            END;

        ***** Snur matrise med sektortall ****************;
        DATA esp_sk1(KEEP = nr yrka aar sk esek);
            SET esp_sk0;

            ARRAY ep (sk) ep1 - ep6;

            DO sk = 1 TO 6;
                nr = (sk - 1) * 2100 + aar;
                esek = ep;

                            OUTPUT esp_sk1;
            END;

        PROC SORT DATA = esp_sk1;
            BY nr yrka;

        DATA esp_sk2(KEEP = sk aar gr1 - gr4);
            SET esp_sk1;
            BY nr;

            ARRAY gr(i) gr1 - gr4;
            RETAIN gr1 - gr4 0;

            IF yrka = 'ba' THEN
                                                   i = 1;
            ELSE IF yrka = 'gr' THEN
                                                   i = 2;
            ELSE IF yrka = 'fa' THEN
                                                   i = 3;
            ELSE IF yrka = 'ps' THEN
                                                    i = 4;

            gr = esek;

            IF LAST.nr THEN
                                                   OUTPUT esp_sk2;

        PROC SORT DATA = esp_sk2;
            BY sk aar;

        ** Her avgjøres om det skal være 99-opplegg eller korrigert opplegg  **;
        DATA esp_sk3(KEEP = sk aar gr1 - gr4 aar1 aar2 sgr2 stgr2 slgr2
                            grdiff sugr surest skplus skmin);
            MERGE esp_sk2 substs;
            BY sk;

            ARRAY gr(4) gr1 - gr4;
            ARRAY sigr(4) sigr1 - sigr4;
            ARRAY stgr(4) stgr1 - stgr4;
            ARRAY slgr(4) slgr1 - slgr4;
            ARRAY sgr(4) sgr1 - sgr4;

            IF ind > 0 AND aar GE &subaarst THEN DO;
                k = skplus;
                aar1 = %EVAL(&subaarst);
               aar2 = %EVAL(&subaarsl);

                            IF aar EQ &subaarst THEN
                                                                   sgr(skplus) = stgr(skplus);
                ELSE IF aar GT &subaarst AND aar LT &subaarsl THEN
                    sgr(k) = stgr(k) + ((aar - aar1) * (slgr(k) - stgr(k)) / (aar2 - aar1));
                ELSE IF aar GE &subaarsl THEN
                                                                   sgr(skplus) = slgr(skplus);

                ****** her kommer bruk av substitusjonsinformasjonen **********;
                sugr = 0;

                            IF skmin GT 0 THEN
                                                                   sugr = gr(skmin) + gr(skplus);
                ELSE DO;
                    DO i = 1 TO 4;
                        sugr + gr(i);
                    END;
                END;

                            surest = sugr - gr(skplus);
                grdiff = gr(skplus) - sugr * sgr(skplus);
                gr(skplus) = sugr * sgr(skplus);

                            IF skmin > 0 THEN
                                                                   gr(skmin) = gr(skmin) + grdiff;
                ELSE DO;
                    DO i = 1 TO 4;
                        IF i NE skplus THEN
                                                                                                  gr(i) = gr(i) + (grdiff * gr(i)) / surest;
                    END;
                END;
            END;

        DATA esp_sk(KEEP = nr aar sk yrka g);
            SET esp_sk3;

            ARRAY gr(i) gr1 - gr4;

            DO i = 1 TO 4;
                nr = (i - 1) * 2100 + aar;

                            IF i = 1 THEN
                                                                   yrka = 'ba';
                ELSE IF i = 2 THEN
                                                                   yrka = 'gr';
                ELSE IF i = 3 THEN
                                                                   yrka = 'fa';
                ELSE IF i = 4 THEN
                                                                   yrka = 'ps';

                            g = gr;

                            OUTPUT esp_sk;
            END;

        PROC SORT DATA = esp_sk;
            BY nr sk;

        DATA esp_ny(KEEP = yrka aar espn);
            SET esp_sk;
            BY nr;

            ARRAY epn(sk) epn1 - epn6;
            RETAIN epn1 - epn6 0;

            epn = g;

            IF LAST.nr THEN DO;
                espn = 0;

                            DO sk = 1 TO 6;
                    espn + epn;
                END;

                            OUTPUT esp_ny;
            END;

        PROC SORT DATA = esp_ny;
            BY yrka aar;

        ** Disse trinn er laget for å rekonstruere resultat fra gamle program **;
        DATA t_ep(KEEP = yrka aar diff);
           MERGE t_e esp_ny;
            BY yrka aar;

            diff = espn - esp;

        DATA t_e(KEEP = yrka aar espd esp aarsv vakans);
            MERGE t_e t_ep;
            BY yrka aar;
            esp = esp + diff;
            vakans = aarsv - esp;
        ****** Ekstratrinn for å videreutvikle det som er gjort i gamle program;

    %END;

%MEND substi;

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

%lesinn
%styr_les

%aggre(1)
%aggre(2)
%aggre(3)
%aggre(4)
%aggre(5)
%aggre(6)
%samle_demografi
%bnpkorr
%bnp

%nykand
%nybehold
%tilbud
%espbasis
/* %substi */
%summlaer
%velgskr

%styr_samle
%samle_samle

run;
"""

print()
print('Lærermod er nå ferdig.')
