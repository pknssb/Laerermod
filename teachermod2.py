import pandas as pd
from functools import reduce
pd.options.display.multi_sparse = False

WelcomeMessage = """
Welcome to the Python version of TeacherMod!

+---------------------------------------------------------------+
|    The TeacherMod model calculates supply and                 |
|    demand for the following 7 groups of teachers:             |
+---------------------------------------------------------------+
| 1. Kindergarten teachers                                       |
| 2. Primary school teachers                                     |
| 3. Teachers with a Master's degree                            |
| 4. PPU (Practical Pedagogical Education)                      |
| 5. Teacher education in practical and aesthetic subjects      |
| 6. Vocational teachers                                         |
| 7. PPU Vocational                                              |
+---------------------------------------------------------------+
"""

print(WelcomeMessage)

# ******************************************************************************************** #
# Start and end year for the projection.                                                       #
# ******************************************************************************************** #

BaseYear = 2020
EndYear = 2040

# ******************************************************************************************** #
# Reading input files. See Appendix 1 for source data.                                         #
# ******************************************************************************************** #

AgeDistributed = pd.read_fwf('inputdata/agedistributed.txt')

AgeDistributedStudents = pd.read_fwf('inputdata/agedistributedstudents.txt')
CandidateProduction = pd.read_fwf('inputdata/candidateproduction.txt')

SectorDistributed = pd.read_fwf('inputdata/sectordistributed.txt')

Population = pd.read_fwf('inputdata/mmmm.txt')

DemographicsGroup1 = pd.read_fwf('inputdata/number_children_kindergartens.txt')
DemographicsGroup3 = pd.read_fwf('inputdata/number_students_secondary.txt')
DemographicsGroup4 = pd.read_fwf('inputdata/number_students_highereducation.txt')

TeacherShortage = pd.read_fwf('inputdata/vacancy.txt')

StandardChange = pd.read_fwf('inputdata/change_standard.txt')

# ******************************************************************************************** #
# Creating row labels on existing columns for later use in merging.                            #
# ******************************************************************************************** #

AgeDistributed.set_index(['Education'], inplace=True)
AgeDistributedStudents.set_index(['Education'], inplace=True)
CandidateProduction.set_index(['Education'], inplace=True)
SectorDistributed.set_index(['Education', 'Sector'], inplace=True)
Population.set_index(['Age', 'Gender'], inplace=True)

# ******************************************************************************************** #
# Creating a constant with abbreviations for the educations included in the model.             #
# ******************************************************************************************** #

Educations = ['ba', 'gr', 'lu', 'ph', 'pe', 'yr', 'py']

# ******************************************************************************************** #
# Creating dictionaries for later use.                                                         #
# ******************************************************************************************** #

PopulationSector = {}
UserGroup = {}
DemographicsSector = {}
DemographicsGroup = {}
SumDemographicsGroup = {}
Users = {}

# ******************************************************************************************** #
# Supply.                                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Initial population of teachers.                                                              #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculating employment rate.                                                                 #
# This is Equation 1 in the model.                                                             #
# ******************************************************************************************** #

AgeDistributed['EmploymentRate'] = AgeDistributed.apply(lambda row: row['Employed'] /
                                                                    row['Count']
                                                        if row['Count'] > 0 else 0, axis=1)

# ******************************************************************************************** #
# Copying this into a table and removing columns that are now redundant.                       #
# ******************************************************************************************** #

Population = AgeDistributed.copy()
AgeDistributed.drop(['Count', 'Employed'], axis=1, inplace=True)

# ******************************************************************************************** #
# Finding full-time equivalents in the population.                                             #
# This is Equation 2 in the model.                                                             #
# ******************************************************************************************** #

Population['FullTimeEquivalents'] = Population.Employed * Population.AverageFullTimeEquivalents

# ******************************************************************************************** #
# Indicating that this is the population in the base year and removing redundant columns.      #
# ******************************************************************************************** #

Population['Year'] = BaseYear
Population.drop(['Employed', 'EmploymentRate', 'AverageFullTimeEquivalents'],
                axis=1, inplace=True)

# ******************************************************************************************** #
# Projection of the initial population. Year 2 to end year. Based on statistics from           #
# the base year.                                                                               #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Candidate production:                                                                        #
# First calculating the total number of first-year students for each education.                #
# This is Equation 3 in the model.                                                             #
# ******************************************************************************************** #

NumberOfFirstYearStudents = AgeDistributedStudents.groupby(
                               ['Education']).sum().rename(columns={'All': 'Total'})

# ******************************************************************************************** #
# Copying the total number of students for the relevant education into a new column in         #
# the AgeDistributedStudents table. Adding a variable for gender.                              #
# ******************************************************************************************** #

AgeDistributedStudents = AgeDistributedStudents.merge(NumberOfFirstYearStudents['Total'],
                                                      how='inner', on='Education')
NewStudents = pd.concat([AgeDistributedStudents, AgeDistributedStudents],
                         keys=[1, 2], names=['Gender']).reset_index()

# ******************************************************************************************** #
# Calculating the proportion of students for each age and gender.                              #
# This is Equation 4 in the model.                                                             #
# ******************************************************************************************** #

NewStudents['ProportionStudentsByAge'] = NewStudents.apply(lambda row: row['Men'] /
                                                              row['Total'] if row['Gender']==1 
                                                              else row['Women'] /
                                                              row['Total'], axis=1)

# ******************************************************************************************** #
# Indicating that the number of students is constant in each projection year.                  #
# ******************************************************************************************** #

CandidateProduction = CandidateProduction.merge(
    pd.concat([pd.DataFrame({'Year': list(range(BaseYear, EndYear+1))})] * 7,
              keys=Educations, names=['Education']), how='inner', on='Education')

# ******************************************************************************************** #
# Calculating the number of annual candidates using new students and completion percentages.   #
# This is Equation 5 in the model.                                                             #
# ******************************************************************************************** #

CandidateProduction['Candidates'] = (CandidateProduction.NumberOfNewStudents *
                                     CandidateProduction.CompletionPercentage)

# ******************************************************************************************** #
# Indicating that the number of candidates should be constant during the projection period.    #
# ******************************************************************************************** #

Candidates = NewStudents.merge(CandidateProduction, how='inner', on=['Education'])

# ******************************************************************************************** #
# Calculating the age of graduation and the number of graduates by gender. Ensuring that the   #
# age of graduation is named the same as in the table to which the rows will be added later,   #
# Age, even though the name is somewhat misleading in this context.                            #
# This is Equation 6 and Equation 7 in the model.                                              #
# ******************************************************************************************** #

Candidates['Age'] = (Candidates.Age + 
                     Candidates.StudyLength)
Candidates['GraduatesByAge'] = (Candidates.Candidates *
                                Candidates.ProportionStudentsByAge)

# ******************************************************************************************** #
# Copying the population in the base year, calculated in equation 2, into a new table which    #
# will be the starting point for calculations.                                                 #
# ******************************************************************************************** #

PopulationCurrentYear = Population.copy()

# ******************************************************************************************** #
# For each projection year, the population will get one year older and new candidates added.   #
# ******************************************************************************************** #

for t in range(BaseYear + 1, EndYear + 1):

    # **************************************************************************************** #
    # Retirement (for the initial population and candidates).                                  #
    # **************************************************************************************** #

    # **************************************************************************************** #
    # For each year, the age in the population is incremented.                                 #
    # This is Equation 8 in the model.                                                         #
    # **************************************************************************************** #
    
    PopulationCurrentYear.Age += 1

    # **************************************************************************************** #
    # Candidates by age and gender found in equations 6 and 7 are added to the table.          #
    # **************************************************************************************** #

    PopulationCurrentYear = PopulationCurrentYear.merge(
                                Candidates[Candidates['Year'] == t].copy(),
                                                    how='outer',
                                                    on=['Education', 'Gender', 'Age'])
    
    # **************************************************************************************** #
    # Graduates by age and gender found in Equation 7 are added to the population.             #
    # This is Equation 9 in the model.                                                         #
    # **************************************************************************************** #
    
    PopulationCurrentYear.Count = (PopulationCurrentYear.Count.fillna(0) +
                                   PopulationCurrentYear.GraduatesByAge.fillna(0))
    
    # **************************************************************************************** #
    # Indicating that this should be the population in the projection year.                    #
    # **************************************************************************************** #
    
    PopulationCurrentYear['Year'] = t

    # **************************************************************************************** #
    # The population in the projection year is added to the population as a new cohort.        #
    # **************************************************************************************** #

    Columns = ['Education', 'Gender', 'Age', 'Count', 'FullTimeEquivalents', 'Year']
    Population = pd.concat([Population, PopulationCurrentYear[Columns]])

    # **************************************************************************************** #
    # Copying the population in the projection year to the table for the next projection year. #
    # **************************************************************************************** #

    PopulationCurrentYear = Population[Population['Year']==t].copy()

# ******************************************************************************************** # 
# Retrieving EmploymentRate and AverageFullTimeEquivalents calculated for                    #
# the initial population in Equation 6 and 7. Indicating that this should be the supply table. #
# ******************************************************************************************** #

Supply = Population.merge(AgeDistributed, how='left', on=['Education', 'Gender', 'Age'])

# ******************************************************************************************** #
# Calculating supply.                                                                         #
# This is Equation 10 in the model.                                                           #
# ******************************************************************************************** #

Supply['Supply'] = Supply.Count * Supply.EmploymentRate * Supply.AverageFullTimeEquivalents

# ******************************************************************************************** #
# Demand.                                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Initial population of teachers.                                                              #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculating employed in the base year, i.e., supply. The demand in the base year is set      #
# equal to this.                                                                               #
# This is Equation 11 in the model.                                                            #
# ******************************************************************************************** #

SectorDistributed = pd.DataFrame({'Demand': ((SectorDistributed.EmployedMen *
                                              SectorDistributed.AverageFullTimeEquivalentMen) +
                                             (SectorDistributed.EmployedWomen *
                                             SectorDistributed.AverageFullTimeEquivalentWomen)),
                                  'Year': BaseYear})

# ******************************************************************************************** #
# Creating an empty table for demand where each of the 7 educations is included.               #
# ******************************************************************************************** #

Demand = pd.DataFrame({'Education': Educations, 'Demand': 0})

# ******************************************************************************************** #
# For each of the 7 educations and each of the 6 sectors, the values found in                  #
# equation 11 are copied into the table with demand. This transposes the table.                #
# ******************************************************************************************** #

for S in range(1, 7):
    Demand[f'DemandSector{S}'] = SectorDistributed.Demand[
        SectorDistributed.Demand.index.get_level_values('Sector') == S].reset_index(drop=True)

# ******************************************************************************************** #
# Projection years. Finding the number of users in the base year to calculate coverage rates   #
# and densities. Growth in the number of users forward based on SSB’s national                 #
# population projections.                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Creating 6 empty tables to be filled with the number of users in each sector.                #
# ******************************************************************************************** #

UserGroup[1] = pd.DataFrame({'ToAge': [0, 2, 2, 3, 5, 5],
'Age': range(0, 6)})
UserGroup[2] = pd.DataFrame({'ToAge': [15] * 10,
'Age': range(6, 16)})
UserGroup[3] = pd.DataFrame({'ToAge': [15] * 16 + list(range(16, 25)) + [49] * 25,
'Age': range(0, 50)})
UserGroup[4] = pd.DataFrame({'ToAge': list(range(19, 30)) + [34] * 5 + [39] * 5 +
[44] * 5 + [49] * 5,
'Age': range(19, 50)})
UserGroup[5] = pd.DataFrame({'ToAge': 99,
'Age': range(0, 100)})
UserGroup[6] = pd.DataFrame({'ToAge': 99,
'Age': range(0, 100)})

# ******************************************************************************************** #
# Summarizing the number of children in kindergartens in each user group by average stay.      #
# This is Equation 12 and Equation 13 in the model.                                            #
# ******************************************************************************************** #

ChildrenGroup1 = pd.DataFrame({'Users': DemographicsGroup1.Age0,
                               'Hours': DemographicsGroup1.HoursMin + (
                                        (DemographicsGroup1.HoursMax -
                                         DemographicsGroup1.HoursMin) / 2)})
ChildrenGroup2 = pd.DataFrame({'Users': DemographicsGroup1.Age1 + DemographicsGroup1.Age2,
                               'Hours': DemographicsGroup1.HoursMin + (
                                        (DemographicsGroup1.HoursMax -
                                         DemographicsGroup1.HoursMin) / 2)})
ChildrenGroup3 = pd.DataFrame({'Users': DemographicsGroup1.Age3,
                               'Hours': DemographicsGroup1.HoursMin + (
                                        (DemographicsGroup1.HoursMax -
                                         DemographicsGroup1.HoursMin) / 2)})
ChildrenGroup4 = pd.DataFrame({'Users': DemographicsGroup1.Age4 + DemographicsGroup1.Age5,
                               'Hours': DemographicsGroup1.HoursMin + (
                                        (DemographicsGroup1.HoursMax -
                                         DemographicsGroup1.HoursMin) / 2)})

# ******************************************************************************************** #
# Creating an empty table to be filled with the number of users in the kindergarten sector.    #
# ******************************************************************************************** #

DemographicsGroup[1] = pd.DataFrame(columns=['FromAge', 'ToAge', 'Users', 'UserIndex'])

# ******************************************************************************************** #
# Calculating users of kindergarten in each of the 4 user groups and user indices for these.   #
# This is Equation 14 and Equation 15 in the model.                                            #
# ******************************************************************************************** #

DemographicsGroup[1].loc[len(DemographicsGroup[1].index)] = [0, 0, ChildrenGroup1.Users.sum(),
(2 * ChildrenGroup1.Users.
mul(ChildrenGroup1.Hours.values).sum()) /
(ChildrenGroup1.Users.sum() * 42.5)]
DemographicsGroup[1].loc[len(DemographicsGroup[1].index)] = [1, 2, ChildrenGroup2.Users.sum(),
(2 * ChildrenGroup2.Users.
mul(ChildrenGroup2.Hours.values).sum()) /
(ChildrenGroup2.Users.sum() * 42.5)]
DemographicsGroup[1].loc[len(DemographicsGroup[1].index)] = [3, 3, ChildrenGroup3.Users.sum(),
(1.5 * ChildrenGroup3.Users.
mul(ChildrenGroup3.Hours.values).sum()) /
(ChildrenGroup3.Users.sum() * 42.5)]
DemographicsGroup[1].loc[len(DemographicsGroup[1].index)] = [4, 5, ChildrenGroup4.Users.sum(),
(1 * ChildrenGroup4.Users.
mul(ChildrenGroup4.Hours.values).sum()) /
(ChildrenGroup4.Users.sum() * 42.5)]

# ******************************************************************************************** #
# Updating the numbers for the number of kindergarten users in each of the 4 user groups when  #
# accounting for user indices.                                                                 #
# This is Equation 16 in the model.                                                            #
# ******************************************************************************************** #

DemographicsGroup[1].loc[0] = [0, 0, DemographicsGroup[1].loc[0].Users *
DemographicsGroup[1].loc[0].UserIndex,
DemographicsGroup[1].loc[0].UserIndex]
DemographicsGroup[1].loc[1] = [1, 2, DemographicsGroup[1].loc[1].Users *
DemographicsGroup[1].loc[1].UserIndex,
DemographicsGroup[1].loc[1].UserIndex]
DemographicsGroup[1].loc[2] = [3, 3, DemographicsGroup[1].loc[2].Users *
DemographicsGroup[1].loc[2].UserIndex,
DemographicsGroup[1].loc[2].UserIndex]
DemographicsGroup[1].loc[3] = [4, 5, DemographicsGroup[1].loc[3].Users *
DemographicsGroup[1].loc[3].UserIndex,
DemographicsGroup[1].loc[3].UserIndex]

# ******************************************************************************************** #
# Calculating students in primary school.                                                      #
# This is Equation 17 in the model.                                                            #
# ******************************************************************************************** #

DemographicsGroup[2] = pd.DataFrame({'FromAge': 6,
                                     'ToAge': 15,
                                     'Users': Population.query('Age>=6 and Age<=15')
                                     [str(BaseYear)].sum(), 'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Copying the users in Sector 3 and 4 that were read in earlier.                               #
# ******************************************************************************************** #

DemographicsGroup[3] = DemographicsGroup3.copy()
DemographicsGroup[4] = DemographicsGroup4.copy()

# ******************************************************************************************** #
# Calculating users of other in the sector (adult education, vocational schools, etc.).        #
# This is Equation 18 in the model.                                                            #
# ******************************************************************************************** #

DemographicsGroup[5] = pd.DataFrame({'FromAge': 0,
'ToAge': 99,
'Users': Population[str(BaseYear)].sum(),
'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Calculating users outside the sector.                                                        #
# This is Equation 19 in the model.                                                            #
# ******************************************************************************************** #

DemographicsGroup[6] = pd.DataFrame
DemographicsGroup[6] = pd.DataFrame({'FromAge': 0,
                                   'ToAge': 99,
                                   'Users': Population[str(BaseYear)].sum(),
                                   'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Calculating the demographic development in each employment sector.                          #
# ******************************************************************************************** #

for S in range(1, 7):

    # **************************************************************************************** #
    # Creating an empty table for the population in the current sector.                       #
    # **************************************************************************************** #

    PopulationSector[S] = pd.DataFrame()
    
    # **************************************************************************************** #
    # Finding the population from the population projections for the user groups in the user group. #
    # This is Equation 20 in the model.                                                       #
    # **************************************************************************************** #

    PopulationSector[S] = UserGroup[S].merge(Population, how='inner',
                                             on='Age').groupby(['ToAge']).sum()
    
    # **************************************************************************************** #
    # Indicating a row label for the maximum age of the user group.                           #
    # **************************************************************************************** #

    DemographicsGroup[S] = DemographicsGroup[S].set_index(['ToAge'])

    # **************************************************************************************** #
    # Indicating that the number of read users should be users in the base year.              #
    # **************************************************************************************** #
    
    DemographicsGroup[S]['Users' + str(BaseYear)] = DemographicsGroup[S].Users 
    
    # **************************************************************************************** #
    # Calculating the number of users in each projection year.                                #
    # This is Equation 21 in the model.                                                       #
    # **************************************************************************************** #

    for t in range(BaseYear + 1, EndYear + 1):
        DemographicsGroup[S][f'Users{t}'] = \
        DemographicsGroup[S][f'Users{t-1}'] * (PopulationSector[S][str(t)] / 
                                               PopulationSector[S][str(t-1)])
    
    # **************************************************************************************** #
    # Creating an empty table for summing the users in each projection year.                  #
    # **************************************************************************************** #
    
    SumDemographicsGroup[S] = pd.DataFrame()
    
    # **************************************************************************************** #
    # Calculating the sum of users in each projection year.                                   #
    # This is Equation 22 in the model.                                                       #
    # **************************************************************************************** #

    for t in range(BaseYear, EndYear + 1):
        SumDemographicsGroup[S][f'SumUsers{t}'] = [DemographicsGroup[S][f'Users{t}'].sum()]
    
    # **************************************************************************************** #
    # Creating an empty table to contain the demographic development in the sector.           #
    # **************************************************************************************** #

    DemographicsSector[S] = pd.DataFrame({'Year': [BaseYear], f'DemographicComponent{S}': [1]})
    
    # **************************************************************************************** #
    # Calculating the demographic development for each projection year for each user group.   #
    # This is Equation 23 in the model.                                                       #
    # **************************************************************************************** #

    for t in range(BaseYear + 1, EndYear + 1):
        NextCohort = pd.DataFrame({
            'Year': t,
            f'DemographicComponent{S}': (SumDemographicsGroup[S][f'SumUsers{t}'] /
                                         SumDemographicsGroup[S][f'SumUsers{BaseYear}'])})
        
        # ************************************************************************************ #
        # The demographic development in the projection year is added as a new cohort in      #
        # the table with the demographic development in the sector.                           #
        # ************************************************************************************ #

        DemographicsSector[S] = pd.concat([DemographicsSector[S], NextCohort], ignore_index=True)

# ******************************************************************************************** #
# Copying the tables with the demographic development in each sector together with             #
# the specification of any standard change into one and the same table (alternative path).     #
# ******************************************************************************************** #

DemographicIndex = StandardChange.copy()
for Sector in range(1, 7):
    DemographicIndex = pd.merge(DemographicIndex, DemographicsSector[Sector])

# ******************************************************************************************** #
# Adding the constant indicating the 7 educations in the model to the table.                  #
# ******************************************************************************************** #

DemographicIndex = pd.concat([DemographicIndex] * 7, keys=Educations, names=['Education'])

# ******************************************************************************************** #
# Teacher densities based on the base year. Held constant.                                    #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Copying the table with the demographic development in each sector, the transposed table      #
# with demand found in equation 11, and any specified teacher shortage into the same table.   #
# ******************************************************************************************** #

Demand = reduce(lambda left, right: pd.merge(left, right, on=['Education'], how='outer'),
                [DemographicIndex, Demand, TeacherShortage]).set_index(['Education', 'Year'])

# ******************************************************************************************** #
# Calculating demand.                                                                          #
# This is Equation 24 and Equation 25 in the model.                                            #
# ******************************************************************************************** #

for S in range(1, 7):
    Demand['Demand'] = (Demand['Demand'] +
                        (Demand[f'DemandSector{S}'] +
                         Demand[f'TeacherShortageSector{S}']) *
                        Demand[f'DemographicComponent{S}'] *
                        Demand[f'StandardChange{S}'])

# ******************************************************************************************** #
# Combining supply and demand.                                                                 #
# This is Equation 26 and Equation 27 in the model.                                            #
# ******************************************************************************************** #

SupplyDemand = pd.concat([pd.DataFrame({'Supply': SectorDistributed.Demand,
                                        'Year': BaseYear}).groupby(['Education', 'Year'],
                                                                  as_index=True).sum(),
                          Supply.groupby(['Education', 'Year'], as_index=True).sum().
                          query('Year > @BaseYear')]).merge(Demand, how='outer', 
                                                            on=['Education', 'Year'])

# ******************************************************************************************** #
# Calculating the difference.                                                                  #
# This is Equation 28 in the model.                                                            #
# ******************************************************************************************** #

SupplyDemand['Difference'] = SupplyDemand.Supply - SupplyDemand.Demand
    
# ******************************************************************************************** #
# Printing the results and a pleasant farewell greeting.                                       #
# ******************************************************************************************** #

Order = {'kt': 1, 'ps': 2, 'ms': 3, 'pp': 4, 'ae': 5, 'vt': 6, 'vp': 7}

SupplyDemand = SupplyDemand[['Supply', 'Demand', 'Difference']]
SupplyDemand = SupplyDemand.sort_values(by=['Education', 'Year'],
                                        key=lambda x: x.map(Order))                         
SupplyDemand.rename(index={'kt': 'Kindergarten Teachers',
                           'ps': 'Primary School Teachers',
                           'ms': 'Teachers with a Master\'s Degree',
                           'pp': 'Practical Pedagogical Education',
                           'ae': 'Practical and Aesthetic Subjects',
                           'vt': 'Vocational Teachers',
                           'vp': 'PPU Vocational'}, inplace=True)

SupplyDemand.round(0).astype(int).to_csv('results/TeacherMod.csv')
SupplyDemand.round(0).astype(int).to_excel('results/TeacherMod.xlsx')
print(SupplyDemand.round(0).astype(int).to_string())

print('\nTeacherMod is now complete, welcome back.\n')