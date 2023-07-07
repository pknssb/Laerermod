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
dem2 = 'utdata/grunnskole.dat';
dem5 = 'utdata/andre_skoler.dat';
dem6 = 'utdata/andre_skoler.dat';


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


def lesinn():

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

    opptak = pd.DataFrame()

    opptak = pd.read_fwf(oppta,
                         header=None,
                         delimiter=" ",
                         names=["aar", "ba", "gr", "fa", "ph", "py", "sp"])

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
                        names=["aar", "barnplus", "grskplus", "viskplus", "uhskplus", "anskplus", "utskplus"])

    stand = stand[stand['aar'] >= basaar]
    stand = stand[stand['aar'] <= simslutt]


def styr_les():

    filnavn = ['dem1', 'dem2', 'dem3', 'dem4', 'dem5', 'dem6']
    aldersnavn = ['ald1', 'ald2', 'ald3', 'ald4', 'ald5', 'ald6']
    

    for x in range(4, 5):

        filnavn = 'dem' + str(x)
        aldnavn = aldersnavn[x-1]

        demonavn = 'demo' + str(x)

        aldnavn = pd.DataFrame()

        aldnavn = pd.read_csv(globals()[filnavn],
                              engine='python',
                              header=None,
                              delimiter=r'[\t:;: ]',
                              names=['ald1',
                                     'ald2'],
                              usecols=[0, 1],
                              dtype={'ald1': 'int',
                                     'ald2': 'int'})

        fett = pd.DataFrame(columns=['alder', 'ald2'])
        print(fett)
        
        slutt = aldnavn.ald2[0] - aldnavn.ald1[0]
        print(slutt)
        for i in range(0, slutt + 1):
            nyrad = {'alder': aldnavn.ald2[0], 'ald2': (aldnavn.ald1[0] + i)}
            fett.loc[len(fett)] = nyrad
        print(fett)
        """
            DATA ald&n(KEEP = alder ald2);
        SET ald&n;

        DO i = 0 TO (ald2 - ald1);
            alder = ald1 + i;

                        OUTPUT ald&n;
        END;
        """


        demonavn = pd.DataFrame()

"""
        demonavn = pd.read_csv(globals()[filnavn],
                               engine='python',
                               header=None,
                               delimiter=r'[\t:;: ]',
                               names=['ald1',
                                      'ald2',
                                      'bi',
                                      'bri',
                                      'antaar'],
                               usecols=[0, 1, 2, 3, 4],
                               dtype={'ald1': 'int',
                                      'ald2': 'int',
                                      'bi': 'float',
                                      'bri': 'float',
                                      'antaar': 'int'})

        print(demonavn)

"""
    
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

def aggre():
    
    for x in range(1, 7):
        
        print(aldersnavn[x])
        
        
        
"""
%MACRO aggre(n);


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
lesinn()
styr_les()
#aggre()


"""
%aggre(1)
%aggre(2)
%aggre(3)
%aggre(4)
%aggre(5)
%aggre(6)
%samle_demografi

%nykand
%nybehold
%tilbud
%espbasis

%summlaer
%velgskr

%styr_samle
%samle_samle

run;
"""

print()
print('Lærermod er nå ferdig.')
