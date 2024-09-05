# ******************************************************************************************** #
# Import of Python libraries and printing of a friendly welcome message.                       #
# ******************************************************************************************** #

import pandas as pd
from functools import reduce
pd.options.display.multi_sparse = False

WelcomeMessage = """
Welcome to the Python version of the Teacher Model!

+---------------------------------------------------------------+
| The TEACHER MODEL calculates supply and                       |
| demand for the following 7 groups of teachers:                |
+---------------------------------------------------------------+
| 1. Kindergarten teachers                                      |
| 2. Primary- and middle school teachers                        |
| 3. Lecturers                                                  |
| 4. PPE (Practical Pedagogical Education)                      |
| 5. Teacher education in practical and aesthetic subjects      |
| 6. Vocational teachers                                        |
| 7. PPU Vocational                                             |
+---------------------------------------------------------------+
"""

print(WelcomeMessage)

# ******************************************************************************************** #
# Start and end year for the projection.                                                       #
# ******************************************************************************************** #

BaseYear = 2020
EndYear = 2040

# ******************************************************************************************** #
# Reading of input files. See Appendix 1 for source data.                                      #
# ******************************************************************************************** #

AgeDistributed = pd.DataFrame(pd.read_fwf('inputdata/agedistributed.txt'))

AgeDistributedStudents = pd.DataFrame(pd.read_fwf('inputdata/agedistributedstudents.txt'))
CandidateProduction = pd.DataFrame(pd.read_fwf('inputdata/candidateproduction.txt'))

SectorDistributed = pd.DataFrame(pd.read_fwf('inputdata/sectordistributed.txt'))

People = pd.DataFrame(pd.read_fwf('inputdata/mmmm.txt'))

DemographyGroup1 = pd.DataFrame(pd.read_fwf('inputdata/number_children_kindergartens.txt'))
DemographyGroup3 = pd.DataFrame(pd.read_fwf('inputdata/number_students_secondary.txt'))
DemographyGroup4 = pd.DataFrame(pd.read_fwf('inputdata/number_students_highereducation.txt'))

Vacancy = pd.DataFrame(pd.read_fwf('inputdata/vacancy.txt'))

StandardChange = pd.DataFrame(pd.read_fwf('inputdata/change_standard.txt'))
WorkHourChange = pd.DataFrame(pd.read_fwf('inputdata/change_workhour.txt'))

# ******************************************************************************************** #
# Creates row labels on existing columns so that they can be used for linking later.           #
# ******************************************************************************************** #

AgeDistributed.set_index(['Education'], inplace=True)
AgeDistributedStudents.set_index(['Education'], inplace=True)
CandidateProduction.set_index(['Education'], inplace=True)
SectorDistributed.set_index(['Education', 'Sector'], inplace=True)
People.set_index(['Age', 'Gender'], inplace=True)

# ******************************************************************************************** #
# Creates a constant with the abbreviations for the educations included in the model.          #
# ******************************************************************************************** #

Educations = ['ba', 'gr', 'lu', 'ph', 'pe', 'yr', 'py']

# ******************************************************************************************** #
# Creates dictionaries for later filling.                                                      #
# ******************************************************************************************** #

PopulationSector = {}
UserGroup = {}
DemographySector = {}
DemographyGroup = {}
SumDemographyGroup = {}
RelativeUsers = {}

# ******************************************************************************************** #
# Supply.                                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Initial population of teachers.                                                              #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculates the employment rate.                                                              #
# This is Equation 1 in the model.                                                             #
# ******************************************************************************************** #

AgeDistributed['EmploymentRate'] = AgeDistributed.apply(lambda row: row['Employed'] /
                                                                    row['Count']
                                                        if row['Count'] > 0 else 0, axis=1)

# ******************************************************************************************** #
# Copies this into a table and removes columns that are now redundant.                         #
# ******************************************************************************************** #

Population = AgeDistributed.copy()
AgeDistributed.drop(['Count', 'Employed'], axis=1, inplace=True)

# ******************************************************************************************** #
# Finds the full-time equivalents in the population.                                           #
# This is Equation 2 in the model.                                                             #
# ******************************************************************************************** #

Population['FullTimeEquivalent'] = Population.Employed * Population.AverageFullTimeEquivalent

# ******************************************************************************************** #
# Indicates that this is the population in the base year and removes redundant columns.        #
# ******************************************************************************************** #

Population['Year'] = BaseYear
Population.drop(['Employed', 'EmploymentRate', 'AverageFullTimeEquivalent'],
                axis=1, inplace=True)

# ******************************************************************************************** #
# Projection of the initial population. Year 2 to end year. Based on statistics from           #
# the base year.                                                                               #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Candidate production:                                                                        #
# First calculates the total number of first-year students for each of the educations.         #
# This is Equation 3 in the model.                                                             #
# ******************************************************************************************** #

TotalFirstYearStudents = AgeDistributedStudents.groupby(
                               ['Education']).sum().rename(columns={'All': 'Total'})

# ******************************************************************************************** #
# Copies the total number of students for the relevant education into a new column in the      #
# AgeDistributedStudents table. Adds a variable for gender.                                    #
# ******************************************************************************************** #

AgeDistributedStudents = AgeDistributedStudents.merge(TotalFirstYearStudents['Total'],
                                                      how='inner', on='Education')
NewStudents = pd.concat([AgeDistributedStudents, AgeDistributedStudents],
                         keys=[1, 2], names=['Gender']).reset_index()

# ******************************************************************************************** #
# Calculates the share of students by age and gender.                                          #
# This is Equation 4 in the model.                                                             #
# ******************************************************************************************** #

NewStudents['StudentShareByAge'] = NewStudents.apply(lambda row: row['Men'] /
                                                            row['Total'] if row['Gender']==1 
                                                            else row['Women'] /
                                                            row['Total'], axis=1)

# ******************************************************************************************** #
# States that the number of students is constant in each projection year.                      #
# ******************************************************************************************** #

CandidateProduction = CandidateProduction.merge(
    pd.concat([pd.DataFrame({'Year': list(range(BaseYear, EndYear+1))})] * 7,
              keys=Educations, names=['Education']), how='inner', on='Education')

# ******************************************************************************************** #
# Calculates the number of annual candidates using new students and completion percentages.    #
# This is Equation 5 in the model.                                                             #
# ******************************************************************************************** #

CandidateProduction['Candidates'] = (CandidateProduction.NumberOfNewStudents *
                                     CandidateProduction.CompletionPercentage)

# ******************************************************************************************** #
# States that the number of candidates will remain constant throughout the projection period.  #
# ******************************************************************************************** #

Candidates = NewStudents.merge(CandidateProduction, how='inner', on=['Education'])

# ******************************************************************************************** #
# Calculates the graduation age and the number of graduates by gender. Ensures that the age    #
# for graduation is named the same as in the table where the rows will be added later,         #
# even though the name might be slightly misleading in this context.                           #
# This is Equation 6 and Equation 7 in the model.                                              #
# ******************************************************************************************** #

Candidates['Age'] = (Candidates.Age + 
                     Candidates.StudyLength)
Candidates['GraduatesByAge'] = (Candidates.Candidates *
                                Candidates.StudentShareByAge)

# ******************************************************************************************** #
# Copies the population from the base year, calculated in Equation 2, into a new table that    #
# will be used for the calculations.                                                           #
# ******************************************************************************************** #

PopulationCurrentYear = Population.copy()

# ******************************************************************************************** #
# For each projection year, the population will age by one year and new graduates be added.    #
# ******************************************************************************************** #

for t in range(BaseYear + 1, EndYear + 1):

    # **************************************************************************************** #
    # Retirement (for the initial population and graduates).                                   #
    # **************************************************************************************** #

    # **************************************************************************************** #
    # Increments the age in the population for each year.                                      #
    # This is Equation 8 in the model.                                                         #
    # **************************************************************************************** #
    
    PopulationCurrentYear.Age += 1

    # **************************************************************************************** #
    # Adds graduates by age and gender, as found in Equation 6 and 7, to the table.            #
    # **************************************************************************************** #

    PopulationCurrentYear = PopulationCurrentYear.merge(Candidates[Candidates['Year'] == t].
                                                        copy(),how='outer',
                                                        on=['Education', 'Gender', 'Age'])

    # **************************************************************************************** #
    # Adds the graduates by age and gender found in Equation 7 to the population.              #
    # This is Equation 9 in the model.                                                         #
    # **************************************************************************************** #
    
    PopulationCurrentYear.Count = (PopulationCurrentYear.Count.fillna(0) +
                                   PopulationCurrentYear.GraduatesByAge.fillna(0))
    
    # **************************************************************************************** #
    # Indicates that this is the population for the projection year.
    # **************************************************************************************** #
    
    PopulationCurrentYear['Year'] = t

    # **************************************************************************************** #
    # Adds the population for the projection year as a new cohort to the population.           #
    # **************************************************************************************** #

    Columns = ['Education', 'Gender', 'Age', 'Count', 'FullTimeEquivalent', 'Year']
    Population = pd.concat([Population, PopulationCurrentYear[Columns]])

    # **************************************************************************************** #
    # Copies the population for the projection year to the table for the next projection year. #
    # **************************************************************************************** #

    PopulationCurrentYear = Population[Population['Year']==t].copy()
     
# ******************************************************************************************** # 
# Retrieves the EmploymentRate and AverageFullTimeEquivalent calculated for the                #
# initial population in Equation 6 and 7. Specifies that this will be the table for supply.    #
# ******************************************************************************************** #

Supply = Population.merge(AgeDistributed, how='left', on=['Education', 'Gender', 'Age'])

# ******************************************************************************************** #
# Calculates the supply.                                                                       #
# This is Equation 10 in the model.                                                            #
# ******************************************************************************************** #

Supply['Supply'] = Supply.Count * Supply.EmploymentRate * Supply.AverageFullTimeEquivalent

# ******************************************************************************************** #
# Demand.                                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculates the employed in the base year, i.e., the supply. The demand in the base year is   #
# set to this.                                                                                 #
# This is Equation 11 in the model.                                                            #
# ******************************************************************************************** #

SectorDistributed = pd.DataFrame({'Demand': ((SectorDistributed.EmployedMen *
                                            SectorDistributed.AverageFullTimeEquivalentMen) +
                                             (SectorDistributed.EmployedWomen *
                                            SectorDistributed.AverageFullTimeEquivalentWomen)),
                                  'Year': BaseYear})

# ******************************************************************************************** #
# Creates an empty table for the demand that includes each of the 7 educations.                #
# ******************************************************************************************** #

Demand = pd.DataFrame({'Education': Educations, 'Demand': 0})

# ******************************************************************************************** #
# For each of the 7 educations and each of the 6 sectors, copies the values found              #
# in Equation 11 into the demand table. This transposes the table.                             #
# ******************************************************************************************** #

for S in range(1, 7):
    Demand[f'DemandSector{S}'] = SectorDistributed.Demand[
        SectorDistributed.Demand.index.get_level_values('Sector') == S].reset_index(drop=True)

# ******************************************************************************************** #
# Projection years. Finds the number of users in the base year to calculate coverage rates and #
# densities. The growth going forward in the number of users is based on the national          #
# population projections from Statistics Norway.                                               #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Creates 6 empty tables to be filled with the number of users in each sector.                 #
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
# Sums the number of children in kindergartens in each user group according to average         #
# duration of stay.                                                                            #
# This is Equation 12 and Equation 13 in the model.                                            #
# ******************************************************************************************** #

ChildrenGroup1 = pd.DataFrame({'Users': DemographyGroup1.Age0,
                               'Hours': DemographyGroup1.HoursMin + 
                                        ((DemographyGroup1.HoursMax -
                                          DemographyGroup1.HoursMin) / 2)})
ChildrenGroup2 = pd.DataFrame({'Users': DemographyGroup1.Age1 + DemographyGroup1.Age2,
                               'Hours': DemographyGroup1.HoursMin + 
                                        ((DemographyGroup1.HoursMax -
                                          DemographyGroup1.HoursMin) / 2)})
ChildrenGroup3 = pd.DataFrame({'Users': DemographyGroup1.Age3,
                               'Hours': DemographyGroup1.HoursMin + 
                                        ((DemographyGroup1.HoursMax -
                                          DemographyGroup1.HoursMin) / 2)})
ChildrenGroup4 = pd.DataFrame({'Users': DemographyGroup1.Age4 + DemographyGroup1.Age5,
                               'Hours': DemographyGroup1.HoursMin + 
                                        ((DemographyGroup1.HoursMax - 
                                        DemographyGroup1.HoursMin) / 2)})

# ******************************************************************************************** #
# Creates an empty table to be filled with the number of users in the kindergarten sector.     #
# ******************************************************************************************** #

DemographyGroup[1] = pd.DataFrame(columns=['FromAge', 'ToAge', 'Users', 'UserIndex'])

# ******************************************************************************************** #
# Calculates users of kindergarten in each of the 4 user groups.                               #
# This is Equation 14 and Equation 15 in the model.                                            #
# ******************************************************************************************** #

DemographyGroup[1].loc[len(DemographyGroup[1].index)] = [0, 0, ChildrenGroup1.Users.sum(),
                                                         (2 * ChildrenGroup1.Users.
                                                          mul(ChildrenGroup1.Hours.
                                                              values).sum()) /
                                                         (ChildrenGroup1.Users.sum() * 42.5)]
DemographyGroup[1].loc[len(DemographyGroup[1].index)] = [1, 2, ChildrenGroup2.Users.sum(),
                                                         (2 * ChildrenGroup2.Users.
                                                          mul(ChildrenGroup2.Hours.
                                                              values).sum()) /
                                                         (ChildrenGroup2.Users.sum() * 42.5)]
DemographyGroup[1].loc[len(DemographyGroup[1].index)] = [3, 3, ChildrenGroup3.Users.sum(),
                                                         (1.5 * ChildrenGroup3.Users.
                                                          mul(ChildrenGroup3.Hours.
                                                              values).sum()) /
                                                         (ChildrenGroup3.Users.sum() * 42.5)]
DemographyGroup[1].loc[len(DemographyGroup[1].index)] = [4, 5, ChildrenGroup4.Users.sum(),
                                                         (1 * ChildrenGroup4.Users.
                                                          mul(ChildrenGroup4.Hours.
                                                              values).sum()) /
                                                         (ChildrenGroup4.Users.sum() * 42.5)]

# ******************************************************************************************** #
# Calculates students in primary education.                                                    #
# This is Equation 16 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[2] = pd.DataFrame({'FromAge': 6,
                                   'ToAge': 15,
                                   'Users': People.query('Age>=6 and Age<=15')
                                   [str(BaseYear)].sum(), 'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Copies the users in Sector 3 and 4 as previously read.                                       #
# ******************************************************************************************** #

DemographyGroup[3] = DemographyGroup3.copy()
DemographyGroup[4] = DemographyGroup4.copy()

# ******************************************************************************************** #
# Calculates users of other sectors (adult education, vocational schools, etc.).               #
# This is Equation 17 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[5] = pd.DataFrame({'FromAge': 0,
                                   'ToAge': 99,
                                   'Users': People[str(BaseYear)].sum(),
                                   'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Calculates users outside of the sector.                                                      #
# This is Equation 18 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[6] = pd.DataFrame({'FromAge': 0,
                                   'ToAge': 99,
                                   'Users': People[str(BaseYear)].sum(),
                                   'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Calculates the demographic development in each employment sector.                            #
# ******************************************************************************************** #

for S in range(1, 7):

    # **************************************************************************************** #
    # Creates an empty table for the population in the relevant sector.                        #
    # **************************************************************************************** #

    PopulationSector[S] = pd.DataFrame()
    
    # **************************************************************************************** #
    # Finds the population from population projections for the user groups in the sector.      #
    # This is Equation 19 in the model.                                                        #
    # **************************************************************************************** #

    PopulationSector[S] = UserGroup[S].merge(People, how='inner',
                                             on='Age').groupby(['ToAge']).sum()
    
    # **************************************************************************************** #
    # Sets a row label for the maximum age of the user group.                                  #
    # **************************************************************************************** #

    DemographyGroup[S] = DemographyGroup[S].set_index(['ToAge'])

    # **************************************************************************************** #
    # Creates an empty table for relative users.                                               #
    # **************************************************************************************** #

    RelativeUsers[BaseYear] = pd.DataFrame()
    
    # **************************************************************************************** #
    # Calculates the number of relative users in the base year.                                #
    # This is Equation 20 in the model.                                                        #
    # **************************************************************************************** #

    DemographyGroup[S][f'RelativeUsers{BaseYear}'] = (DemographyGroup[S].Users *
                                                      DemographyGroup[S].UserIndex)
    
    # **************************************************************************************** #
    # Calculates the number of relative users in each projection year.                         #
    # This is Equation 21 in the model.                                                        #
    # **************************************************************************************** #

    for t in range(BaseYear + 1, EndYear + 1):
        DemographyGroup[S][f'RelativeUsers{t}'] = \
        DemographyGroup[S][f'RelativeUsers{t-1}'] * (PopulationSector[S][str(t)] / 
                                                     PopulationSector[S][str(t-1)])
    
    # **************************************************************************************** #
    # Creates an empty table for the summation of relative users in each projection year.      #
    # **************************************************************************************** #

    SumDemographyGroup[S] = pd.DataFrame()
    
    # **************************************************************************************** #
    # Calculates the sum of users in each projection year.                                     #
    # This is Equation 22 in the model.                                                        #
    # **************************************************************************************** #

    for t in range(BaseYear, EndYear + 1):
        SumDemographyGroup[S][f'SumRelativeUsers{t}'] = [DemographyGroup[S]
                                                         [f'RelativeUsers{t}'].sum()]

    # **************************************************************************************** #
    # Creates an empty table that will contain the demographic development in the sector.      #
    # **************************************************************************************** #

    DemographySector[S] = pd.DataFrame({'Year': [BaseYear], f'DemographicComponent{S}': [1]})
    
    # **************************************************************************************** #
    # Calculates the demographic development for each projection year for each user group.     #
    # This is Equation 23 in the model.                                                        #
    # **************************************************************************************** #

    for t in range(BaseYear + 1, EndYear + 1):
        NextYear = pd.DataFrame({
            'Year': t,
            f'DemographicComponent{S}': (SumDemographyGroup[S][f'SumRelativeUsers{t}'] /
                                         SumDemographyGroup[S][f'SumRelativeUsers{BaseYear}'])})
        
        # ************************************************************************************ #
        # The demographic development for the projection year is added as a new cohort to      #
        # the table with the demographic development in the sector.                            #
        # ************************************************************************************ #

        DemographySector[S] = pd.concat([DemographySector[S], NextYear], ignore_index=True)
        
# ******************************************************************************************** #
# Copies the tables with the demographic development in each sector along with                 #
# the specification of any standard change into a single table (alternative path).             #
# ******************************************************************************************** #

DemographicIndex = StandardChange.copy()
for Sector in range(1, 7):
    DemographicIndex = pd.merge(DemographicIndex, DemographySector[Sector])

# ******************************************************************************************** #
# Adds the constant specifying the 7 educations in the model to the table.                     #
# ******************************************************************************************** #

DemographicIndex = pd.concat([DemographicIndex] * 7, keys=Educations, names=['Education'])

# ******************************************************************************************** #
# Teacher densities based on the base year. Kept constant.
# ******************************************************************************************** #

# ******************************************************************************************** #
# Copies the table with demographic development in each sector, the transposed table           #
# with demand found in Equation 11, and any specified vacancy into the same table.             #
# ******************************************************************************************** #

Demand = reduce(lambda left, right: pd.merge(left, right, on=['Education'], how='outer'),
                [DemographicIndex, Demand, Vacancy]).set_index(['Education', 'Year'])

# ******************************************************************************************** #
# Calculates the demand.                                                                       #
# This is Equation 24 and Equation 25 in the model.                                            #
# ******************************************************************************************** #

for S in range(1, 7):
    Demand['Demand'] = (Demand['Demand'] +
                        (Demand[f'DemandSector{S}'] +
                         Demand[f'VacancySector{S}']) *
                        Demand[f'DemographicComponent{S}'] *
                        Demand[f'StandardChange{S}'])

# ******************************************************************************************** #
# Combining supply and demand.                                                                 #
# This is Equation 26 and Equation 27 in the model.                                            #
# ******************************************************************************************** #

SupplyDemand = pd.concat([pd.DataFrame({'Supply': SectorDistributed.Demand,
                                        'Year': BaseYear}).groupby(['Education', 'Year'],
                                                                    as_index=True).sum(),
                          Supply.groupby(['Education', 'Year'],as_index=True).sum().
                          query('Year > @BaseYear')]).merge(Demand, how='outer', 
                                                             on=['Education', 'Year'])

# ******************************************************************************************** #
# Calculates the difference.                                                                   #
# This is Equation 28 in the model.                                                            #
# ******************************************************************************************** #

SupplyDemand['Difference'] = SupplyDemand.Supply - SupplyDemand.Demand
    
# ******************************************************************************************** #
# Prints out the results and a friendly farewell message.                                      #
# ******************************************************************************************** #

Order = {'ba': 1, 'gr': 2, 'lu': 3, 'ph': 4, 'pe': 5, 'yr': 6, 'py': 7}

SupplyDemand = SupplyDemand[['Supply', 'Demand', 'Difference']]
SupplyDemand = SupplyDemand.sort_values(by=['Education', 'Year'],
                                        key=lambda x: x.map(Order))                         
SupplyDemand.rename(index={'ba': 'Kindergarten teachers',
                           'gr': 'Primary- and middle school teachers',
                           'lu': 'Lecturers',
                           'ph': 'PPE (Practical Pedagogical Education)',
                           'pe': 'Practical and aesthetic subjects',
                           'yr': 'Vocational teachers',
                           'py': 'PPU Vocational'}, inplace=True)

SupplyDemand.round(0).astype(int).to_csv('results/TeacherModel.csv')
SupplyDemand.round(0).astype(int).to_excel('results/TeacherModel.xlsx')
print(SupplyDemand.round(0).astype(int).to_string())

print('\nThe Teacher Model is now complete, welcome back.\n')
