# ******************************************************************************************** #
# Import of Python libraries and printing a friendly welcome message.                          #
# ******************************************************************************************** #

import pandas as pd
from functools import reduce
pd.options.display.multi_sparse = False

print('\nWelcome to the Python version of Teacher Mode!\n')
print('/********************************************************************/')
print('/********************************************************************/')
print('/* The TEACHER MODE model calculates the supply and demand for      */')
print('/* the following 7 groups of teachers:                              */')
print('/*   - Kindergarten teachers                                         */')
print('/*   - Primary school teachers                                       */')
print('/*   - Secondary school teachers (with a masters degree)            */')
print('/*   - PPU (Practical Pedagogical Education)                         */')
print('/*   - Teachers of practical and aesthetic subjects                  */')
print('/*   - Vocational teachers                                            */')
print('/*   - PPU Vocational                                                 */')
print('/********************************************************************/')
print('/********************************************************************/\n')

# ******************************************************************************************** #
# Start and end year for the projection.                                                       #
# ******************************************************************************************** #

BaseYear = 2020
EndYear = 2040

# ******************************************************************************************** #
# Reading input files. See Appendix 1 for source data.                                         #
# ******************************************************************************************** #

AgeDistributed = pd.DataFrame(pd.read_fwf('inputdata/agedistributed.txt'))

AgeDistributedStudents = pd.DataFrame(pd.read_fwf('inputdata/agedistributedstudents.txt'))
CandidateProduction = pd.DataFrame(pd.read_fwf('inputdata/candidateproduction.txt'))

SectorDistributed = pd.DataFrame(pd.read_fwf('inputdata/sectordistributed.txt'))

Population = pd.DataFrame(pd.read_fwf('inputdata/mmmm.txt'))

DemographyGroup1 = pd.DataFrame(pd.read_fwf('inputdata/number_children_kindergartens.txt'))
DemographyGroup3 = pd.DataFrame(pd.read_fwf('inputdata/number_students_secondary.txt'))
DemographyGroup4 = pd.DataFrame(pd.read_fwf('inputdata/number_students_highereducation.txt'))

Vacancy = pd.DataFrame(pd.read_fwf('inputdata/vacancy.txt'))

StandardChange = pd.DataFrame(pd.read_fwf('inputdata/change_standard.txt'))
WorkHourChange = pd.DataFrame(pd.read_fwf('inputdata/change_workhour.txt'))

# ******************************************************************************************** #
# Creates row labels on existing columns for later use in linking.                             #
# ******************************************************************************************** #

AgeDistributed.set_index(['Education'], inplace=True)
AgeDistributedStudents.set_index(['Education'], inplace=True)
CandidateProduction.set_index(['Education'], inplace=True)
SectorDistributed.set_index(['Education', 'Sector'], inplace=True)
Population.set_index(['Age', 'Gender'], inplace=True)

# ******************************************************************************************** #
# Creates a constant with the abbreviations for the educations included in the model.         #
# ******************************************************************************************** #

Educations = ['ba', 'pr', 'se', 'pp', 'pa', 'vo', 'pv']

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
                                                                    row['Total']
                                                        if row['Total'] > 0 else 0, axis=1)

# ******************************************************************************************** #
# Copies this into a table and removes columns that are now redundant.                         #
# ******************************************************************************************** #

Population = AgeDistributed.copy()
AgeDistributed.drop(['Total', 'Employed'], axis=1, inplace=True)

# ******************************************************************************************** #
# Finds the work years in the population.                                                      #
# This is Equation 2 in the model.                                                             #
# ******************************************************************************************** #

Population['WorkYears'] = Population.Employed * Population.AverageWorkYears

# ******************************************************************************************** #
# Indicates that this is the population in the base year and removes redundant columns.       #
# ******************************************************************************************** #

Population['Year'] = BaseYear
Population.drop(['Employed', 'EmploymentRate', 'AverageWorkYears'],
                axis=1, inplace=True)

# ******************************************************************************************** #
# Projection of the initial population. Year 2 to end year. Based on statistics from the base year.
# ******************************************************************************************** #

# ******************************************************************************************** #
# Candidate production:                                                                        #
# First calculates the total number of first-year students for each education.                 #
# This is Equation 3 in the model.                                                             #
# ******************************************************************************************** #

TotalFirstYearStudents = AgeDistributedStudents.groupby(
                             ['Education']).sum().rename(columns={'All': 'Total'})

# ******************************************************************************************** #
# Copies the total number of students for the respective education into a new column in        #
# the table AgeDistributedStudents. Adds a variable for gender.                                #
# ******************************************************************************************** #

AgeDistributedStudents = AgeDistributedStudents.merge(TotalFirstYearStudents['Total'],
                                                      how='inner', on='Education')
NewStudents = pd.concat([AgeDistributedStudents, AgeDistributedStudents],
                         keys=[1, 2], names=['Gender']).reset_index()

# ******************************************************************************************** #
# Calculates the share of students for each age and gender.                                    #
# This is Equation 4 in the model.                                                             #
# ******************************************************************************************** #

NewStudents['StudentShareByAge'] = NewStudents.apply(lambda row: row['Men'] /
                                                     row['Total'] if row['Gender']==1 
                                                     else row['Women'] /
                                                     row['Total'], axis=1)

# ******************************************************************************************** #
# Indicates that the number of students is constant in each projection year.                   #
# ******************************************************************************************** #

CandidateProduction = CandidateProduction.merge(
    pd.concat([pd.DataFrame({"Year": list(range(BaseYear, EndYear+1))})] * 7,
              keys=Educations, names=['Education']), how='inner', on='Education')

# ******************************************************************************************** #
# Calculates the number of annual candidates using new students and completion percentages.    #
# This is Equation 5 in the model.                                                             #
# ******************************************************************************************** #

CandidateProduction['Candidates'] = (CandidateProduction.NumberNewStudents *
                                     CandidateProduction.CompletionPercentage)

# ******************************************************************************************** #
# Indicates that the number of candidates should be constant in the projection period.         #
# ******************************************************************************************** #

Candidates = NewStudents.merge(CandidateProduction, how='inner', on=['Education'])

# ******************************************************************************************** #
# Calculates the age for graduation and the number of graduates by gender. Ensures that the age
# for graduation is named the same as in the table the rows will be added to later, Age, even though
# the name is a bit misleading in this context.
# This is Equation 6 and Equation 7 in the model.                                              #
# ******************************************************************************************** #

Candidates['Age'] = (Candidates.Age + Candidates.StudyLength)
Candidates['GraduatesByAge'] = (Candidates.Candidates *
                                Candidates.StudentShareByAge)

# ******************************************************************************************** #
# Copies the population in the base year, calculated in equation 2, into two new tables which  #
# will be the basis for the calculations.                                                      #
# ******************************************************************************************** #

Population = Population.copy()
CurrentYearPopulation = Population.copy()

# ******************************************************************************************** #
# For each projection year, the population will age by one year and new candidates are added.  #
# ******************************************************************************************** #

for x in range(BaseYear + 1, EndYear + 1):

    # **************************************************************************************** #
    # Retirement (for the initial population and candidates).                                  #
    # **************************************************************************************** #

    # **************************************************************************************** #
    # For each year, the age in the population is incremented.                                 #
    # This is Equation 8 in the model.                                                         #
    # **************************************************************************************** #
    
    CurrentYearPopulation.Age += 1

    # **************************************************************************************** #
    # Candidates by age and gender found in equation 6 and 7 are added to the table.           #
    # **************************************************************************************** #

    CurrentYearPopulation = CurrentYearPopulation.merge(Candidates[Candidates['Year'] == x].copy(),
                                                        how='outer',
                                                        on=['Education', 'Gender', 'Age'])

    # **************************************************************************************** #
    # Graduates by age and gender found in Equation 7 are added to the population.             #
    # This is Equation 9 in the model.                                                         #
    # **************************************************************************************** #

    CurrentYearPopulation.Total = (CurrentYearPopulation.Total.fillna(0) +
                                   CurrentYearPopulation.GraduatesByAge.fillna(0))
    
    # **************************************************************************************** #
    # Indicates that this should be the population in the projection year.                    #
    # **************************************************************************************** #
    
    CurrentYearPopulation['Year'] = x

    # **************************************************************************************** #
    # The population in the projection year is added to the population as a new cohort.       #
    # **************************************************************************************** #

    Population = pd.concat([Population, CurrentYearPopulation[['Education',
                                                               'Gender',
                                                               'Age',
                                                               'Total',
                                                               'WorkYears',
                                                               'Year']]])

    # **************************************************************************************** #
    # Copies the population in the projection year to the table for the next projection year. #
    # **************************************************************************************** #

    CurrentYearPopulation = Population[Population['Year']==x].copy()
    
# ******************************************************************************************** #
# Retrieves the Employment Rate and Average Work Years calculated for the initial population   #
# in Equation 6 and 7. Indicates that this will become the table for supply.                  #
# ******************************************************************************************** #

Supply = Population.merge(AgeDistributed, how='left', on=['Education', 'Gender', 'Age'])

# ******************************************************************************************** #
# Calculates the supply.                                                                       #
# This is Equation 10 in the model.                                                            #
# ******************************************************************************************** #

Supply['Supply'] = Supply.Total * Supply.EmploymentRate * Supply.AverageWorkYears

# ******************************************************************************************** #
# Demand.                                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# The initial population of teachers.                                                          #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculates employed in the base year, i.e., the supply. The demand in the base year is set equal
# to this.
# This is Equation 11 in the model.                                                            #
# ******************************************************************************************** #

SectorDistributed = pd.DataFrame({'Demand': ((SectorDistributed.EmployedMen *
                                              SectorDistributed.AverageWorkYearsMen) +
                                             (SectorDistributed.EmployedWomen *
                                              SectorDistributed.AverageWorkYearsWomen)),
                                  'Year': BaseYear})

# ******************************************************************************************** #
# Creates an empty table for the demand where each of the 7 educations is included.            #
# ******************************************************************************************** #

Demand = pd.DataFrame({'Education': Educations, 'Demand': 0})

# ******************************************************************************************** #
# For each of the 7 educations and each of the 6 sectors, the values found in equation 11 are  #
# copied into the demand table. This transposes the table.                                     #
# ******************************************************************************************** #

for i in range(1, 7):
    Demand["DemandSector"+str(i)] = SectorDistributed.Demand[
        SectorDistributed.Demand.index.get_level_values('Sector') == i].reset_index(drop=True)

# ******************************************************************************************** #
# Projection years. Calculates the number of users in the base year to calculate coverage rates
# and densities. The growth forward in the number of users based on the national
# population projections from the statistics bureau.                                           #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Creates 6 empty tables that will be filled with the number of users in each sector.          #
# ******************************************************************************************** #

UserGroup1 = pd.DataFrame({'ToAge': [0, 2, 2, 3, 5, 5],
                           'Age': range(0, 6)})
UserGroup2 = pd.DataFrame({'ToAge': [15] * 10,
                           'Age': range(6, 16)})
UserGroup3 = pd.DataFrame({'ToAge': [15] * 16 + list(range(16, 25)) + [49] * 25,
                           'Age': range(0, 50)})
UserGroup4 = pd.DataFrame({'ToAge': list(range(19, 30)) + [34] * 5 + [39] * 5 +
                                                            [44] * 5 + [49] * 5,
                           'Age': range(19, 50)})
UserGroup5 = pd.DataFrame({'ToAge': 99,
                           'Age': range(0, 100)})
UserGroup6 = pd.DataFrame({'ToAge': 99,
                           'Age': range(0, 100)})

# ******************************************************************************************** #
# Sums the number of children in kindergartens in each user group according to average stay time.
# This is Equation 12 and Equation 13 in the model.                                            #
# ******************************************************************************************** #

ChildrenGroup1 = pd.DataFrame({'Users': DemographyGroup1.Age0,
                               'Hours': DemographyGroup1.HoursMin + (
                                   (DemographyGroup1.HoursMax - DemographyGroup1.HoursMin) / 2)})
ChildrenGroup2 = pd.DataFrame({'Users': DemographyGroup1.Age1 + DemographyGroup1.Age2,
                               'Hours': DemographyGroup1.HoursMin + (
                                   (DemographyGroup1.HoursMax - DemographyGroup1.HoursMin) / 2)})
ChildrenGroup3 = pd.DataFrame({'Users': DemographyGroup1.Age3,
                               'Hours': DemographyGroup1.HoursMin + (
                                   (DemographyGroup1.HoursMax - DemographyGroup1.HoursMin) / 2)})
ChildrenGroup4 = pd.DataFrame({'Users': DemographyGroup1.Age4 + DemographyGroup1.Age5,
                               'Hours': DemographyGroup1.HoursMin + (
                                   (DemographyGroup1.HoursMax - DemographyGroup1.HoursMin) / 2)})

# ******************************************************************************************** #
# Creates an empty table to be filled with the number of users in the kindergarten sector.     #
# ******************************************************************************************** #

DemographyGroup1 = pd.DataFrame(columns=['FromAge', 'ToAge', 'Users', 'UserIndex'])

# ******************************************************************************************** #
# Calculates users of kindergarten in each of the 4 user groups.                               #
# This is Equation 14 and Equation 15 in the model.                                            #
# ******************************************************************************************** #

DemographyGroup1.loc[len(DemographyGroup1.index)] = [0, 0, ChildrenGroup1.Users.sum(),
                                                     (2 * ChildrenGroup1.Users.
                                                      mul(ChildrenGroup1.Hours.values).sum())
                                                     / (ChildrenGroup1.Users.sum() * 42.5)]
DemographyGroup1.loc[len(DemographyGroup1.index)] = [1, 2, ChildrenGroup2.Users.sum(),
                                                     (2 * ChildrenGroup2.Users.
                                                      mul(ChildrenGroup2.Hours.values).sum()) /
                                                     (ChildrenGroup2.Users.sum() * 42.5)]
DemographyGroup1.loc[len(DemographyGroup1.index)] = [3, 3, ChildrenGroup3.Users.sum(),
                                                     (1.5 * ChildrenGroup3.Users.
                                                      mul(ChildrenGroup3.Hours.values).sum()) /
                                                     (ChildrenGroup3.Users.sum() * 42.5)]
DemographyGroup1.loc[len(DemographyGroup1.index)] = [4, 5, ChildrenGroup4.Users.sum(),
                                                     (1 * ChildrenGroup4.Users.
                                                      mul(ChildrenGroup4.Hours.values).sum()) /
                                                     (ChildrenGroup4.Users.sum() * 42.5)]

# ******************************************************************************************** #
# Calculates students in primary school.                                                       #
# This is Equation 16 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup2 = pd.DataFrame({'FromAge': 6,
                                 'ToAge': 15,
                                 'Users': Population.query('Age>=6 and Age<=15')
                                 [str(BaseYear)].sum(), 'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Calculates users of other in the sector (adult education, vocational schools, etc.).         #
# This is Equation 17 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup5 = pd.DataFrame({'FromAge': 0,
                                 'ToAge': 99,
                                 'Users': Population[str(BaseYear)].sum(),
                                 'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Calculates users outside the sector.                                                         #
# This is Equation 18 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup6 = pd.DataFrame({'FromAge': 0,
                                 'ToAge': 99,
                                 'Users': Population[str(BaseYear)].sum(),
                                 'UserIndex': 1.0}, index=[0])

# ******************************************************************************************** #
# Growth in the number of users (population projections).                                      #
# ******************************************************************************************** #

for i in range(1, 7):
    
    # **************************************************************************************** #
    # Finds the population from the population projections for user groups in the sector.      #
    # This is Equation 19 in the model.                                                        #
    # **************************************************************************************** #
    
    locals()[f'Population{i}'] = locals()[f'UserGroup{i}'].merge(Population,
                                          how='inner', on='Age').groupby(["ToAge"]).sum()
    
    # **************************************************************************************** #
    # Sets a row label for the maximum age of the user group.                                  #
    # **************************************************************************************** #

    locals()[f'DemographyGroup{i}'] = locals()[f'DemographyGroup{i}'].set_index(["ToAge"])
    
    # **************************************************************************************** #
    # Calculates the number of relative users in the base year.                                #
    # This is Equation 20 in the model.                                                        #
    # **************************************************************************************** #
    
    locals()[f'DemographyGroup{i}']["RelativeUsers" + str(BaseYear)] = \
    locals()[f'DemographyGroup{i}'].Users * locals()[f'DemographyGroup{i}'].UserIndex
    
    # **************************************************************************************** #
    # Calculates the number of relative users in each projection year.                         #
    # This is Equation 21 in the model.                                                        #
    # **************************************************************************************** #

    for x in range(BaseYear + 1, EndYear + 1):
        locals()[f'DemographyGroup{i}']['RelativeUsers' + str(x)] = \
        (locals()[f'DemographyGroup{i}']['RelativeUsers' + str(x-1)] *
         (locals()[f'Population{i}'][str(x)] / locals()[f'Population{i}'][str(x-1)]))
    
    # **************************************************************************************** #
    # Creates an empty table for summing the relative users in each simulation year.           #
    # **************************************************************************************** #

    locals()[f'SumDemographyGroup{i}'] = pd.DataFrame()
    
    # **************************************************************************************** #
    # Calculates the sum of the users in each simulation year.                                 #
    # This is Equation 22 in the model.                                                        #
    # **************************************************************************************** #
    
    for x in range(BaseYear, EndYear + 1):
        locals()[f'SumDemographyGroup{i}']['SumRelativeUsers' + str(x)] = \
        [locals()[f'DemographyGroup{i}']['RelativeUsers' + str(x)].sum()]
    
    # **************************************************************************************** #
    # Creates an empty table to contain the demographic development in the sector.             #
    # **************************************************************************************** #

    locals()[f'DemographySector{i}'] = pd.DataFrame({"Year": [BaseYear],
                                                     "DemographyComponent" + str(i): [1]})

    # **************************************************************************************** #
    # Calculates the demographic development for each projection year for each user group.     #
    # This is Equation 23 in the model.                                                        #
    # **************************************************************************************** #

    for x in range(BaseYear + 1, EndYear + 1):
        NextCohort = pd.DataFrame({"Year": x,
                                    "DemographyComponent" + str(i): \
                                    locals()[f'SumDemographyGroup{i}'] \
                                     ['SumRelativeUsers' + str(x)] / \
                                    locals()[f'SumDemographyGroup{i}'] \
                                    ['SumRelativeUsers' + str(BaseYear)]})
        
        # ************************************************************************************ #
        # The demographic development in the simulation year is added as a new cohort in the   #
        # table with the demographic development in the sector.                                #
        # ************************************************************************************ #

        locals()[f'DemographySector{i}'] = pd.concat([locals()[f'DemographySector{i}'],
                                                      NextCohort], ignore_index=True)

# ******************************************************************************************** #
# Copies the tables with the demographic development in each sector along with the             #
# specification of any standard change into one table (alternative path).                      #
# ******************************************************************************************** #

DemographyIndex = StandardChange.merge((DemographySector1).merge
                                        (DemographySector2).merge
                                        (DemographySector3).merge
                                        (DemographySector4).merge
                                        (DemographySector5).merge
                                        (DemographySector6))

# ******************************************************************************************** #
# Adds the constant that indicates the 7 educations in the model to the table.                 #
# ******************************************************************************************** #

DemographyIndex = pd.concat([DemographyIndex,
                             DemographyIndex,
                             DemographyIndex,
                             DemographyIndex,
                             DemographyIndex,
                             DemographyIndex,
                             DemographyIndex],
                            keys=Educations,
                            names=['Education'])

# ******************************************************************************************** #
# Teacher densities based on the base year. Kept constant.                                     #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Copies the table with the demographic development in each sector, the transposed table with  #
# demand found in equation 11, and any specified vacancy into the same table.                  #
# ******************************************************************************************** #

Demand = reduce(lambda left, right: pd.merge(left, right, on=['Education'], how='outer'),
                [DemographyIndex, Demand, Vacancy]).set_index(['Education', 'Year'])

# ******************************************************************************************** #
# Calculates the demand.                                                                       #
# This is Equation 24 and Equation 25 in the model.                                            #
# ******************************************************************************************** #

for i in range(1, 7):
    Demand['Demand'] = (Demand['Demand'] +
                        (Demand['DemandSector' + str(i)] +
                         Demand['VacancySector' + str(i)]) *
                        Demand['DemographyComponent' + str(i)] *
                        Demand['StandardChange' + str(i)])

# ******************************************************************************************** #
# Combines supply and demand.                                                                  #
# This is Equation 26 and Equation 27 in the model.                                            #
# ******************************************************************************************** #

SupplyDemand = pd.concat([pd.DataFrame({'Supply': SectorDistributed.Demand,
                                        'Year': BaseYear}).groupby(['Education', 'Year'],
                                                                    as_index=True).sum(),
                          Supply.groupby(['Education', 'Year'],
                                         as_index=True).sum().
                          query('Year > @BaseYear')]).merge(Demand, 
                                                             how='outer', 
                                                             on=['Education', 'Year'])

# ******************************************************************************************** #
# Calculates the difference.                                                                   #
# This is Equation 28 in the model.                                                            #
# ******************************************************************************************** #

SupplyDemand['Difference'] = SupplyDemand.Supply - SupplyDemand.Demand
    
# ******************************************************************************************** #
# Outputs the results and a friendly farewell message.                                         #
# ******************************************************************************************** #

SupplyDemand = SupplyDemand[['Supply', 'Demand', 'Difference']]
SupplyDemand = SupplyDemand.sort_values(by=['Education', 'Year'],
                                        key=lambda x: x.map({'ba': 1,
                                                             'pr': 2,
                                                             'se': 3,
                                                             'pp': 4,
                                                             'pa': 5,
                                                             'vo': 6,
                                                             'pv': 7}))
SupplyDemand.rename(index={'ba': 'Kindergarten teachers',
                           'pr': 'Primary school teachers',
                           'se': 'Secondary school teachers',
                           'pp': 'PPU',
                           'pa': 'Practical and aesthetic subjects',
                           'vo': 'Vocational teachers',
                           'pv': 'PPU Vocational'}, inplace=True)

SupplyDemand.round(0).astype(int).to_csv("results/TeacherMode.csv")
SupplyDemand.round(0).astype(int).to_excel("results/TeacherMode.xlsx")
print(SupplyDemand.round(0).astype(int).to_string())

print('\nTeacher Mode is now complete, welcome back.\n')
