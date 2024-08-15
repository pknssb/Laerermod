# ******************************************************************************************** #
# Importing R libraries and printing a welcoming message.                                      #
# ******************************************************************************************** #

library(readr)
library(dplyr)
library(tidyr)
library(purrr)
library(tidyverse)
library(openxlsx)
library(writexl)

options(dplyr.summarise.inform = FALSE)

cat("
Welcome to the R version of TeacherMod!

+---------------------------------------------------------------+
|    The model TEACHERMOD calculates supply and                 |
|    demand for the following 7 groups of teachers:             |
+---------------------------------------------------------------+
| 1. Preschool Teachers                                         |
| 2. Primary School Teachers                                    |
| 3. Teachers with a Master's Degree                            |
| 4. Postgraduate Certificate in Education (PGCE)               |
| 5. Teachers of Practical and Aesthetic Subjects               |
| 6. Vocational Teachers                                        |
| 7. PGCE in Vocational Education                               |
+---------------------------------------------------------------+
\n")

# ******************************************************************************************** #
# Start and end year for the projection.                                                       #
# ******************************************************************************************** #

BaseYear <- 2020
EndYear <- 2040

# ******************************************************************************************** #
# Reading input files. See Appendix 1 for source data.                                         #
# ******************************************************************************************** #

AgeDistributed <- read.table("inputdata/agedistributed.txt", header = TRUE)

AgeDistributedStudents <- read.table('inputdata/agedistributedstudents.txt', header = TRUE)
CandidateProduction <- read.table('inputdata/candidateproduction.txt', header = TRUE)

SectorDistributed <- read.table('inputdata/sectordistributed.txt', header = TRUE)

People <- read.table('inputdata/mmmm.txt', header = TRUE)

DemographyGroup1 <- read.table('inputdata/number_children_kindergartens.txt', header = TRUE)
DemographyGroup3 <- read.table('inputdata/number_students_secondary.txt', header = TRUE)
DemographyGroup4 <- read.table('inputdata/number_students_highereducation.txt', header = TRUE)

TeacherShortage <- read.table('inputdata/teachershortage.txt', header = TRUE)

StandardChange <- read.table('inputdata/change_standard.txt', header = TRUE)
StandardChange$Year <- paste0("X", as.character(StandardChange$Year))

WorkHourChange <- read.table('inputdata/change_workhour.txt', header = TRUE)

# ******************************************************************************************** #
# Creating row labels on existing columns so they can later be used for linking.               #
# ******************************************************************************************** #

AgeDistributed <- AgeDistributed %>% mutate(Education = factor(Education))
AgeDistributedStudents <- AgeDistributedStudents %>% mutate(Education = factor(Education))
CandidateProduction <- CandidateProduction %>% mutate(Education = factor(Education))
SectorDistributed <- SectorDistributed %>% mutate(Education = factor(Education),
                                                  Sector = factor(Sector))
People <- People %>% mutate(Age = factor(Age), Gender = factor(Gender))

# ******************************************************************************************** #
# Creating a constant with the abbreviations for the educations included in the model.         #
# ******************************************************************************************** #

Educations <- c('ba', 'gr', 'lu', 'ph', 'pe', 'yr', 'py')

# ******************************************************************************************** #
# Creating lists for later filling.                                                            #
# ******************************************************************************************** #

PeopleSector <- list()
UserGroup <- list()
DemographySector <- list()
DemographyGroup <- list()
SumDemographyGroup <- list()
Users <- list()

# ******************************************************************************************** #
# Initial teacher population.                                                                  #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculating employment rate.                                                                 #
# This is Equation 1 in the model.                                                             #
# ******************************************************************************************** #

AgeDistributed$EmploymentRate <- ifelse(AgeDistributed$Count > 0, 
                                        AgeDistributed$Employed / AgeDistributed$Count, 
                                        0)

# ******************************************************************************************** #
# Copying this into a table and removing columns that are now redundant.                       #
# ******************************************************************************************** #

Population <- AgeDistributed
AgeDistributed <- AgeDistributed %>% select(-Count, -Employed)

# ******************************************************************************************** #
# Finding the full-time equivalents in the population.                                         #
# This is Equation 2 in the model.                                                             #
# ******************************************************************************************** #

Population$FTEs <- Population$Employed * Population$AverageFullTimeEquivalent

# ******************************************************************************************** #
# Indicates that this is the population in the base year and removes redundant columns.        #
# ******************************************************************************************** #

Population$Year <- BaseYear
Population <- Population %>% select(-Employed, -EmploymentRate, -AverageFullTimeEquivalent)

# ******************************************************************************************** #
# Projecting the initial population. Year 2 to end year. Based on statistics from base year.   #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Candidate production:                                                                        #
# First calculates the total number of first-year students for each of the educations.         #
# This is Equation 3 in the model.                                                             #
# ******************************************************************************************** #

TotalFirstYearStudents <- AgeDistributedStudents %>% 
  group_by(Education) %>% 
  summarise(Total = sum(All)) %>% 
  ungroup()

# ******************************************************************************************** #
# Copies the total number of students for the relevant education into a new column in          #
# the table AgeDistributedStudents. Adds a variable for gender.                                #
# ******************************************************************************************** #

AgeDistributedStudents <- AgeDistributedStudents %>%
  inner_join(TotalFirstYearStudents, by = "Education")

NewStudents <- AgeDistributedStudents %>%
  mutate(Gender = 1) %>%
  bind_rows(AgeDistributedStudents %>% mutate(Gender = 2))

# ******************************************************************************************** #
# Calculates the proportion of students by age and gender.                                     #
# This is Equation 4 in the model.                                                             #
# ******************************************************************************************** #

NewStudents <- NewStudents %>%
  mutate(StudentShareByAge = if_else(Gender == 1, 
                                     Men / Total, 
                                     Women / Total))

# ******************************************************************************************** #
# Indicates that the number of students is constant in each projection year.                   #
# ******************************************************************************************** #

Years <- data.frame(Year = BaseYear:EndYear)
EducationYears <- expand.grid(Education = Educations, Year = Years$Year)

CandidateProduction <- CandidateProduction %>% inner_join(EducationYears, by = "Education")

# ******************************************************************************************** #
# Calculates the number of annual graduates using new students and completion percentages.     #
# This is Equation 5 in the model.                                                             #
# ******************************************************************************************** #

CandidateProduction <- CandidateProduction %>%
  mutate(Graduates = NumberOfNewStudents * CompletionPercentage)

# ******************************************************************************************** #
# Indicates that the number of graduates should be constant in the projection period.          #
# ******************************************************************************************** #

Graduates <- inner_join(NewStudents, CandidateProduction,
                        by = "Education", relationship = "many-to-many")

# ******************************************************************************************** #
# Calculates graduation age and number of graduates by gender. Ensures the graduation age      #
# is named the same as in the table the rows will be added to later, Age, even if the name is  #
# a bit misleading in this context.                                                            #
# This is Equation 6 and Equation 7 in the model.                                              #
# ******************************************************************************************** #

Graduates <- Graduates %>%
  mutate(Age = Age + StudyLength,
         GraduatesByAge = Graduates * StudentShareByAge)

# ******************************************************************************************** #
# Copies the population in the base year, calculated in Equation 2, into two new tables that   #
# will be the basis for the calculations.                                                      #
# ******************************************************************************************** #

CurrentYearPopulation <- Population

# ******************************************************************************************** #
# For each projection year, the population ages one year and new graduates are added.          #
# ******************************************************************************************** #

for (t in (BaseYear + 1):EndYear) {
  
    # **************************************************************************************** #
    # Retirement (for the initial population and graduates).                                   #
    # **************************************************************************************** #

    # **************************************************************************************** #
    # For each year, the age in the population is incremented.                                 #
    # This is Equation 8 in the model.                                                         #
    # **************************************************************************************** #

    CurrentYearPopulation$Age <- CurrentYearPopulation$Age + 1
  
    # **************************************************************************************** #
    # Graduates by age and gender found in Equation 6 and 7 are added to the table.            #
    # **************************************************************************************** #

    CurrentYearPopulation <- merge(x = CurrentYearPopulation, 
                                   y = Graduates[Graduates$Year == t, ], 
                                   by = c("Education", "Gender", "Age"), 
                                   all = TRUE)
  
    # **************************************************************************************** #
    # Graduates by age and gender found in Equation 7 are added to the population.             #
    # This is Equation 9 in the model.                                                         #
    # **************************************************************************************** #

    CurrentYearPopulation$Count <- ifelse(is.na(CurrentYearPopulation$Count), 0, 
                                           CurrentYearPopulation$Count) + 
                                    ifelse(is.na(CurrentYearPopulation$GraduatesByAge), 0,
                                           CurrentYearPopulation$GraduatesByAge)
  
    # **************************************************************************************** #
    # Indicates that this should be the population in the projection year.                     #
    # **************************************************************************************** #

    CurrentYearPopulation$Year <- t
  
    # **************************************************************************************** #
    # The population in the projection year is added to the population as a new cohort.        #
    # **************************************************************************************** #

    Population <- rbind(Population, CurrentYearPopulation[, c("Education", "Gender", "Age",
                                                              "Count", "FTEs", "Year")])
  
    # **************************************************************************************** #
    # Copies the population in the projection year to the table for the next projection year.  #
    # **************************************************************************************** #

    CurrentYearPopulation <- Population[Population$Year == t, ]
}

# ******************************************************************************************** # 
# Incorporates the Employment Rate and Average FTEs calculated for the initial population in   #
# Equation 6 and 7. Specifies that this should become the table for the supply.                #
# ******************************************************************************************** #

Supply <- merge(x = Population, 
                y = AgeDistributed, 
                by = c("Education", "Gender", "Age"), 
                all.x = TRUE)

# ******************************************************************************************** #
# Calculates the supply.                                                                       #
# This is Equation 10 in the model.                                                            #
# ******************************************************************************************** #

Supply$Supply <- Supply$Count * Supply$EmploymentRate * Supply$AverageFullTimeEquivalent

# ******************************************************************************************** #
# Initial teacher population.                                                                  #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculates employed in the base year, i.e., the supply. Demand in the base year is set equal #
# to this.                                                                                     #
# This is Equation 11 in the model.                                                            #
# ******************************************************************************************** #

SectorDistributed$Demand <- (SectorDistributed$EmployedMen *
                             SectorDistributed$AverageFullTimeEquivalentMen) + 
                            (SectorDistributed$EmployedWomen *
                             SectorDistributed$AverageFullTimeEquivalentWomen)
SectorDistributed$Year <- BaseYear

# ******************************************************************************************** #
# Creates an empty table for the demand where each of the 7 educations is included.            #
# ******************************************************************************************** #

Demand <- data.frame(Education = Educations, Demand = rep(0, length(Educations)))

# ******************************************************************************************** #
# For each of the 7 educations and each of the 6 sectors, the values found in Equation 11 are  #
# copied into the table with the demand. This transposes the table.                            #
# ******************************************************************************************** #

for (S in 1:6) {
  Demand[paste0('DemandSector', S)] <- SectorDistributed$Demand[SectorDistributed$
                                                                Sector == S]
}

# ******************************************************************************************** #
# Projection years. Calculates the number of users in the base year to estimate coverage       #
# rates and densities. The growth forward in the number of users based on SSB's national       #
# population projections.                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Creates 6 empty tables that will be filled with the number of users in each sector.          #
# ******************************************************************************************** #

UserGroup[[1]] <- data.frame(ToAge = c(0, 2, 2, 3, 5, 5),
                             Age = 0:5)

UserGroup[[2]] <- data.frame(ToAge = rep(15, 10),
                             Age = 6:15)

UserGroup[[3]] <- data.frame(ToAge = c(rep(15, 16), 16:24, rep(49, 25)),
                             Age = 0:49)

UserGroup[[4]] <- data.frame(ToAge = c(19:29, rep(34, 5), rep(39, 5), rep(44, 5),
                                       rep(49, 5)),
                             Age = 19:49)

UserGroup[[5]] <- data.frame(ToAge = rep(99, 100),
                             Age = 0:99)

UserGroup[[6]] <- data.frame(ToAge = rep(99, 100),
                             Age = 0:99)

# ******************************************************************************************** #
# Sums the number of children in kindergartens in each user group by average stay duration.    #
# This is Equation 12 and Equation 13 in the model.                                            #
# ******************************************************************************************** #

ChildrenGroup1 <- data.frame(Users = DemographyGroup1$Age0,
                             Hours = DemographyGroup1$HoursMin + 
                                     ((DemographyGroup1$HoursMax -
                                       DemographyGroup1$HoursMin) / 2))

ChildrenGroup2 <- data.frame(Users = DemographyGroup1$Age1 + DemographyGroup1$Age2,
                             Hours = DemographyGroup1$HoursMin + 
                                     ((DemographyGroup1$HoursMax -
                                       DemographyGroup1$HoursMin) / 2))

ChildrenGroup3 <- data.frame(Users = DemographyGroup1$Age3,
                             Hours = DemographyGroup1$HoursMin + 
                                     ((DemographyGroup1$HoursMax -
                                       DemographyGroup1$HoursMin) / 2))

ChildrenGroup4 <- data.frame(Users = DemographyGroup1$Age4 + DemographyGroup1$Age5,
                             Hours = DemographyGroup1$HoursMin + 
                                     ((DemographyGroup1$HoursMax -
                                       DemographyGroup1$HoursMin) / 2))

# ******************************************************************************************** #
# Creates an empty table to be filled with the number of users in the kindergarten sector.     #
# ******************************************************************************************** #

DemographyGroup[[1]] <- data.frame(FromAge = integer(), ToAge = integer(), 
                                   Users = integer(), UserIndex = numeric())

# ******************************************************************************************** #
# Calculates users of kindergarten in each of the 4 user groups.                               #
# This is Equation 14 and Equation 15 in the model.                                            #
# ******************************************************************************************** #

DemographyGroup[[1]] <- rbind(DemographyGroup[[1]], 
                             data.frame(FromAge = 0, ToAge = 0, 
                                        Users = sum(ChildrenGroup1$Users), 
                                        UserIndex = (2 * sum(ChildrenGroup1$Users *
                                                            ChildrenGroup1$Hours)) / 
                                                   (sum(ChildrenGroup1$Users) * 42.5)))

DemographyGroup[[1]] <- rbind(DemographyGroup[[1]], 
                             data.frame(FromAge = 1, ToAge = 2, 
                                        Users = sum(ChildrenGroup2$Users), 
                                        UserIndex = (2 * sum(ChildrenGroup2$Users *
                                                            ChildrenGroup2$Hours)) / 
                                                   (sum(ChildrenGroup2$Users) * 42.5)))

DemographyGroup[[1]] <- rbind(DemographyGroup[[1]], 
                             data.frame(FromAge = 3, ToAge = 3, 
                                        Users = sum(ChildrenGroup3$Users), 
                                        UserIndex = (1.5 * sum(ChildrenGroup3$Users *
                                                              ChildrenGroup3$Hours)) / 
                                                   (sum(ChildrenGroup3$Users) * 42.5)))

DemographyGroup[[1]] <- rbind(DemographyGroup[[1]], 
                             data.frame(FromAge = 4, ToAge = 5, 
                                        Users = sum(ChildrenGroup4$Users), 
                                        UserIndex = (1 * sum(ChildrenGroup4$Users *
                                                            ChildrenGroup4$Hours)) / 
                                                   (sum(ChildrenGroup4$Users) * 42.5)))

# ******************************************************************************************** #
# Updating the figures for the number of kindergarten users in each of the 4 user groups when  #
# taking the user indices into account.                                                        #
# This is Equation 16 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[[1]][1, ] <- c(0, 0, DemographyGroup[[1]]$Users[1] *
                                     DemographyGroup[[1]]$UserIndex[1],
                               DemographyGroup[[1]]$UserIndex[1])
DemographyGroup[[1]][2, ] <- c(1, 2, DemographyGroup[[1]]$Users[2] *
                                     DemographyGroup[[1]]$UserIndex[2],
                               DemographyGroup[[1]]$UserIndex[2])
DemographyGroup[[1]][3, ] <- c(3, 3, DemographyGroup[[1]]$Users[3] *
                                     DemographyGroup[[1]]$UserIndex[3],
                               DemographyGroup[[1]]$UserIndex[3])
DemographyGroup[[1]][4, ] <- c(4, 5, DemographyGroup[[1]]$Users[4] *
                                     DemographyGroup[[1]]$UserIndex[4],
                               DemographyGroup[[1]]$UserIndex[4])

# ******************************************************************************************** #
# Ensures the Age column is numeric.                                                           #
# ******************************************************************************************** #

People$Age <- as.numeric(as.character(People$Age))

# ******************************************************************************************** #
# Calculates students in primary school.                                                       #
# This is Equation 17 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[[2]] <- data.frame(FromAge = 6,
                                   ToAge = 15,
                                   Users = sum(People[People$Age >= 6 & People$Age <= 15,
                                                      paste0("X", as.character(BaseYear))]),
                                   UserIndex = 1.0)

# ******************************************************************************************** #
# Copies the users in Sector 3 and 4 that were read earlier.                                   #
# ******************************************************************************************** #

DemographyGroup[[3]] <- DemographyGroup3
DemographyGroup[[4]] <- DemographyGroup4

# ******************************************************************************************** #
# Calculates users of other in the sector (adult education, vocational schools, etc.).         #
# This is Equation 18 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[[5]] <- data.frame(FromAge = 0,
                                   ToAge = 99,
                                   Users = sum(People[, paste0("X", as.character(BaseYear))]),
                                   UserIndex = 1.0)

# ******************************************************************************************** #
# Calculates users outside the sector.                                                         #
# This is Equation 19 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[[6]] <- data.frame(FromAge = 0,
                                   ToAge = 99,
                                   Users = sum(People[, paste0("X", as.character(BaseYear))]),
                                   UserIndex = 1.0)

# ******************************************************************************************** #
# Calculates the demographic development in each employment sector.                            #
# ******************************************************************************************** #

for (S in 1:6) {
    
    # **************************************************************************************** #
    # Finds the population from the population projections for the user groups.                #
    # This is Equation 20 in the model.                                                        #
    # **************************************************************************************** #
    
    PeopleSector[[S]] <- merge(UserGroup[[S]], People, by = "Age") %>% group_by(ToAge) %>%
                             summarize(across(c(paste0("X", as.character(BaseYear))
                                               :paste0("X", as.character(EndYear))),
                                              \(x) sum(x, na.rm = TRUE)))
    
    # **************************************************************************************** #
    # Sets a row label for the maximum age of the user group.                                  #
    # **************************************************************************************** #
    
    rownames(DemographyGroup[[S]]) <- DemographyGroup[[S]]$ToAge

    # **************************************************************************************** #
    # Indicates that the number of recorded users should be the users in the base year.        #
    # **************************************************************************************** #
  
    DemographyGroup[[S]][paste0("Users", paste0("X", as.character(BaseYear)))] <-
    DemographyGroup[[S]]$Users

    # **************************************************************************************** #
    # Calculates the number of users in each projection year.                                  #
    # This is Equation 21 in the model.                                                        #
    # **************************************************************************************** #

    for (t in (BaseYear + 1):EndYear) {
        DemographyGroup[[S]][[paste0("Users", paste0("X", as.character(t)))]] <-
        DemographyGroup[[S]][[paste0("Users", paste0("X", as.character(t-1)))]] *
        (PeopleSector[[S]][[paste0("X", as.character(t))]] /
         PeopleSector[[S]][[paste0("X", as.character(t-1))]])
    }
    
    # **************************************************************************************** #
    # Creates an empty table for the summation of users in each projection year.               #
    # **************************************************************************************** #

    SumDemographyGroup[[S]] <- data.frame(t(BaseYear:EndYear))

    # **************************************************************************************** #
    # Calculates the sum of the users in each projection year.                                 #
    # This is Equation 22 in the model.                                                        #
    # **************************************************************************************** #
  
    for (t in BaseYear:EndYear) {
        SumDemographyGroup[[S]][[paste0("SumUsers",
                                        paste0("X", as.character(t)))]] <-
        sum(DemographyGroup[[S]][[paste0("Users",
                                         paste0("X", as.character(t)))]], na.rm = TRUE)
    }

    # **************************************************************************************** #
    # Creates an empty table to contain the demographic development in the sector.             #
    # **************************************************************************************** #

    KN <- paste0("DemographyComponent", S)
    DemographySector[[S]] <- data.frame(Year = paste0("X", as.character(BaseYear)),
                                        TempColumn = 1)  
    names(DemographySector[[S]])[names(DemographySector[[S]]) == "TempColumn"] <- KN
  
    # **************************************************************************************** #
    # Calculates the demographic development for each projection year for each user group.     #
    # This is Equation 23 in the model.                                                        #
    # **************************************************************************************** #

    for (t in (BaseYear + 1):EndYear) {
        NextCohort <- data.frame(Year = paste0("X", as.character(t)))
        NextCohort[KN] <- SumDemographyGroup[[S]][[paste0("SumUsers",
                                                          paste0("X", as.character(t)))]] / 
                          SumDemographyGroup[[S]][[paste0("SumUsers",
                                                          paste0("X", as.character(BaseYear)))]]
    
        # ************************************************************************************ #
        # The demographic development in the projection year is added as a new cohort in the   #
        # table with the demographic development in the sector.                                #
        # ************************************************************************************ #
    
        DemographySector[[S]] <- rbind(DemographySector[[S]], NextCohort)
    }
}

# ******************************************************************************************** #
# Copies the tables with the demographic development in each sector together with the          #
# specification of any standard change into the same table (alternative path).                 #
# ******************************************************************************************** #

DemographyIndex <- StandardChange # Assuming this is correctly initialized

for (Sector in 1:6) {
    DemographyIndex <- merge(DemographyIndex, DemographySector[[Sector]],
                             by = "Year", all = TRUE)
}

# ******************************************************************************************** #
# Adds the constant indicating the 7 educations in the model to the table.                     #
# ******************************************************************************************** #

DemographyIndex <- DemographyIndex %>% 
                   expand_grid(Education = Educations) %>%
                   arrange(Education, Year)

# ******************************************************************************************** #
# Teacher densities based on the base year. Kept constant.                                     #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Copies the table with the demographic development in each sector, the transposed table with  #
# the demand found in Equation 11, and any specified teacher shortage into the same table.     #
# ******************************************************************************************** #

Demand <- merge(DemographyIndex, Demand, by = c("Education"), all = TRUE)
Demand <- merge(Demand, TeacherShortage, by = c("Education"), all = TRUE)

# ******************************************************************************************** #
# Calculates the demand.                                                                       #
# This is Equation 24 and Equation 25 in the model.                                            #
# ******************************************************************************************** #

for(S in 1:6) {
    Demand <- Demand %>%
    mutate(!!sym(paste0("Demand")) := !!sym(paste0("Demand")) +
                                        (!!sym(paste0("DemandSector", S)) +
                                         !!sym(paste0("TeacherShortageSector", S))) *
                                        !!sym(paste0("DemographyComponent", S)) *
                                        !!sym(paste0("StandardChange", S)))
}

# ******************************************************************************************** #
# Combines supply and demand.                                                                  #
# This is Equation 26 and Equation 27 in the model.                                            #
# ******************************************************************************************** #

Supply$Year <- paste0("X", as.character(Supply$Year))

FirstAggregate <- aggregate(Demand ~ Education + Year, data = SectorDistributed, FUN = sum)
FirstAggregate$Year <- paste0("X", as.character(BaseYear))
names(FirstAggregate)[names(FirstAggregate) == "Demand"] <- "Supply"

SecondAggregate <- aggregate(Supply ~ Education + Year,
                             data = Supply,
                             FUN = sum,
                             subset = Year > paste0("X", as.character(BaseYear)))

SupplyDemand <- merge(rbind(FirstAggregate, SecondAggregate),
                      Demand,
                      by = c("Education", "Year"),
                      all = TRUE)

SupplyDemand$Year <- sub("X", "", SupplyDemand$Year, fixed = TRUE)

# ******************************************************************************************** #
# Calculates the difference.                                                                   #
# This is Equation 28 in the model.                                                            #
# ******************************************************************************************** #

SupplyDemand$Difference <- with(SupplyDemand, Supply - Demand)

# ******************************************************************************************** #
# Prints the results and a friendly farewell message.                                          #
# ******************************************************************************************** #

SupplyDemand <- data.frame(lapply(SupplyDemand[c("Education",
                                                 "Year",
                                                 "Supply",
                                                 "Demand",
                                                 "Difference")],
                                  function(x) {if(is.numeric(x)) {as.integer(round(x))} 
                                               else {x}}))

Order <- c(ba = 1, gr = 2, lu = 3, ph = 4, pe = 5, yr = 6, py = 7)

SupplyDemand$EducationOrdered <- SupplyDemand$Education
SupplyDemand$EducationOrdered <- with(SupplyDemand, names(Order)
                                      [match(Education, names(Order))])
SupplyDemand$EducationOrdered <- factor(SupplyDemand$EducationOrdered,
                                        levels = names(Order))

SupplyDemand <- SupplyDemand %>% arrange(EducationOrdered, Year)

SupplyDemand$EducationOrdered <- NULL
SupplyDemand$Education <- factor(SupplyDemand$Education, 
                                 levels = c("ba", "gr", "lu", "ph", "pe", "yr", "py"),
                                 labels = c("Preschool Teachers", "Primary School Teachers",
                                            "Teachers with a Master's Degree", "PGCE",
                                            "Teachers of Practical and Aesthetic Subjects",
                                            "Vocational Teachers",
                                            "PGCE in Vocational Education"))

write_csv(SupplyDemand, 'results/TeacherMod.csv')
write_xlsx(SupplyDemand, 'results/TeacherMod.xlsx')

cat(sprintf("Education                                          Year Supply Demand Difference\n"))
invisible(apply(SupplyDemand, 1, function(x) {
    cat(sprintf("%-47s     %4s %5d  %5s     %6s",
                x[["Education"]],
                x[["Year"]],
                round(as.numeric(x[["Supply"]])),
                round(as.numeric(x[["Demand"]])),
                round(as.numeric(x[["Difference"]]))),
        "\n")
}))

cat("\nTeacherMod has now completed, welcome back.\n")
