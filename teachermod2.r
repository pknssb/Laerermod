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

CandidateProduction <- CandidateProduction %>% mutate(Education = factor(Education))
SectorDistributed <- SectorDistributed %>% mutate(Education = factor(Education), Sector = factor(Sector))
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
RelativeUsers <- list()

# ******************************************************************************************** #
# Initial teacher population.                                                                  #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Calculating employment rate. This is Equation 1 in the model.                                #
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
# Finding the full-time equivalents in the population. This is Equation 2 in the model.        #
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

CandidateProduction <- CandidateProduction %>% mutate(NewStudents = TotalStudents * StudentShare)

# ******************************************************************************************** #
# Candidate production, continued:                                                             #
# Calculates the number of first-year students based on the statistics from the base year.     #
# This is Equation 4 in the model.                                                             #
# ******************************************************************************************** #

NewStudents <- CandidateProduction %>% select(Education, NewStudents)

# ******************************************************************************************** #
# Calculates the total number of graduates for each education.                                 #
# This is Equation 5 in the model.                                                             #
# ******************************************************************************************** #

CandidateProduction <- CandidateProduction %>% mutate(Graduates = NumberOfNewStudents * CompletionPercentage)

# ******************************************************************************************** #
# Indicates that the number of graduates should be constant in the projection period.          #
# ******************************************************************************************** #

Graduates <- inner_join(NewStudents, CandidateProduction, by = "Education",
                        relationship = "many-to-many")

# ******************************************************************************************** #
# Calculates graduation age and number of graduates by gender. Ensures the graduation age      #
# is named the same as in the table the rows will be added to later, Age, even if the name is  #
# a bit misleading in this context.                                                            #
# This is Equation 6 and Equation 7 in the model.                                              #
# ******************************************************************************************** #

Graduates <- Graduates %>% mutate(Age = Age + StudyLength, GraduatesByAge = Graduates * StudentShareByAge)

# ******************************************************************************************** #
# Copies the population in the base year, calculated in Equation 2, into two new tables that   #
# will be the basis for the calculations.                                                      #
# ******************************************************************************************** #

CurrentYearPopulation <- Population
NextYearPopulation <- Population

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

    CurrentYearPopulation$GraduatesByAge <- ifelse(is.na(CurrentYearPopulation$GraduatesByAge), 
                                                   0, 
                                                   CurrentYearPopulation$GraduatesByAge)
    CurrentYearPopulation$FTEs <- ifelse(is.na(CurrentYearPopulation$FTEs), 
                                         0, 
                                         CurrentYearPopulation$FTEs)
    CurrentYearPopulation$FTEs <- CurrentYearPopulation$FTEs + CurrentYearPopulation$GraduatesByAge
    
    # **************************************************************************************** #
    # Update the year.                                                                         #
    # **************************************************************************************** #
    
    CurrentYearPopulation$Year <- t
    
    # **************************************************************************************** #
    # Save the updated population for the next iteration.                                      #
    # **************************************************************************************** #
    
    NextYearPopulation <- rbind(NextYearPopulation, CurrentYearPopulation)
}

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
  Demand[paste0('DemandSector', S)] <- SectorDistributed$Demand[SectorDistributed$Sector == S]
}

# ******************************************************************************************** #
# Projection years. Calculates the number of users in the base year to estimate coverage       #
# rates and densities. The growth forward in the number of users based on SSB's national       #
# population projections.                                                                      #
# ******************************************************************************************** #

# ******************************************************************************************** #
# Creates 6 empty tables that will be filled with the number of users in each sector.          #
# ******************************************************************************************** #

UserGroup[[1]] <- data.frame(ToAge = c(0, 2, 2, 3, 5, 5), Age = 0:5)
UserGroup[[2]] <- data.frame(ToAge = rep(15, 10), Age = 6:15)
UserGroup[[3]] <- data.frame(ToAge = c(rep(15, 16), 16:24, rep(49, 25)), Age = 0:49)
UserGroup[[4]] <- data.frame(ToAge = c(19:29, rep(34, 5), rep(39, 5), rep(44, 5), rep(49, 5)), Age = 19:49)
UserGroup[[5]] <- data.frame(ToAge = rep(99, 100), Age = 0:99)
UserGroup[[6]] <- data.frame(ToAge = rep(99, 100), Age = 0:99)

# ******************************************************************************************** #
# Sums the number of children in kindergartens in each user group by average stay duration.    #
# ******************************************************************************************** #

DemographyGroup[[1]] <- rbind(DemographyGroup[[1]], 
                             data.frame(FromAge = 0, ToAge = 0, 
                                        Users = sum(ChildrenGroup1$Users), 
                                        UserIndex = (2 * sum(ChildrenGroup1$Users * ChildrenGroup1$Hours)) / 
                                                   (sum(ChildrenGroup1$Users) * 42.5)))

DemographyGroup[[1]] <- rbind(DemographyGroup[[1]], 
                             data.frame(FromAge = 1, ToAge = 2, 
                                        Users = sum(ChildrenGroup2$Users), 
                                        UserIndex = (2 * sum(ChildrenGroup2$Users * ChildrenGroup2$Hours)) / 
                                                   (sum(ChildrenGroup2$Users) * 42.5)))

DemographyGroup[[1]] <- rbind(DemographyGroup[[1]], 
                             data.frame(FromAge = 3, ToAge = 3, 
                                        Users = sum(ChildrenGroup3$Users), 
                                        UserIndex = (1.5 * sum(ChildrenGroup3$Users * ChildrenGroup3$Hours)) / 
                                                   (sum(ChildrenGroup3$Users) * 42.5)))

DemographyGroup[[1]] <- rbind(DemographyGroup[[1]], 
                             data.frame(FromAge = 4, ToAge = 5, 
                                        Users = sum(ChildrenGroup4$Users), 
                                        UserIndex = (1 * sum(ChildrenGroup4$Users * ChildrenGroup4$Hours)) / 
                                                   (sum(ChildrenGroup4$Users) * 42.5)))

# ******************************************************************************************** #
# Ensures the Age column is numeric.                                                           #
# ******************************************************************************************** #

People$Age <- as.numeric(as.character(People$Age))

# ******************************************************************************************** #
# Calculates students in primary school.                                                       #
# This is Equation 16 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[[2]] <- data.frame(FromAge = 6,
                                   ToAge = 15,
                                   Users = sum(People[People$Age >= 6 &
                                                      People$Age <= 15, 
                                                      paste0("X",
                                                             as.character(BaseYear))]),
                                   UserIndex = 1.0)

# ******************************************************************************************** #
# Copies the users in Sector 3 and 4 that were read earlier.                                   #
# ******************************************************************************************** #

DemographyGroup[[3]] <- DemographyGroup3
DemographyGroup[[4]] <- DemographyGroup4

# ******************************************************************************************** #
# Calculates users of other in the sector (adult education, vocational schools, etc.).         #
# This is Equation 17 in the model.                                                            #
# ******************************************************************************************** #

DemographyGroup[[5]] <- data.frame(FromAge = 19, ToAge = 99, Users = sum(People[People$Age >= 19 & People$Age <= 99, paste0("X", as.character(BaseYear))]), UserIndex = 1.0)

# ******************************************************************************************** #
# Calculates the relative number of users in the base year.                                    #
# This is Equation 20 in the model.                                                            #
# ******************************************************************************************** #

for (S in 1:6) {
    DemographyGroup[[S]][paste0("RelativeUsers", paste0("X", as.character(BaseYear)))] <- DemographyGroup[[S]]$Users * DemographyGroup[[S]]$UserIndex

    # **************************************************************************************** #
    # Calculates the number of relative users in each projection year.                         #
    # This is Equation 21 in the model.                                                        #
    # **************************************************************************************** #

    for (t in (BaseYear + 1):EndYear) {
        DemographyGroup[[S]][[paste0("RelativeUsers", paste0("X", as.character(t)))]] <- DemographyGroup[[S]][[paste0("RelativeUsers", paste0("X", as.character(t-1)))]] *
        (PeopleSector[[S]][[paste0("X", as.character(t))]] /
         PeopleSector[[S]][[paste0("X", as.character(t-1))]])
    }
    
    # **************************************************************************************** #
    # Creates an empty table for the summation of the relative users in each projection year.  #
    # **************************************************************************************** #

    SumDemographyGroup[[S]] <- data.frame(t(BaseYear:EndYear))

    # **************************************************************************************** #
    # Calculates the sum of the users in each projection year.                                 #
    # This is Equation 22 in the model.                                                        #
    # **************************************************************************************** #
}

for (t in BaseYear:EndYear) {
    SumDemographyGroup[[S]][[paste0("SumRelativeUsers", paste0("X", as.character(t)))]] <- 
    sum(DemographyGroup[[S]][[paste0("RelativeUsers", paste0("X", as.character(t)))]], na.rm = TRUE)
}

# ******************************************************************************************** #
# Creates an empty table to contain the demographic development in the sector.                 #
# ******************************************************************************************** #

KN <- paste0("DemographyComponent", S)
DemographySector[[S]] <- data.frame(Year = paste0("X", as.character(BaseYear)),
                                    TempColumn = 1)  
names(DemographySector[[S]])[names(DemographySector[[S]]) == "TempColumn"] <- KN

# ******************************************************************************************** #
# Calculates the demographic development for each projection year for each user group.         #
# This is Equation 23 in the model.                                                            #
# ******************************************************************************************** #

for (t in (BaseYear + 1):EndYear) {
    NextCohort <- data.frame(Year = paste0("X", as.character(t)))
    NextCohort[KN] <- SumDemographyGroup[[S]][[paste0("SumRelativeUsers", paste0("X", as.character(t)))]] / 
                      SumDemographyGroup[[S]][[paste0("SumRelativeUsers", paste0("X", as.character(BaseYear)))]] 

    # Adding the new cohort data
    DemographySector[[S]] <- rbind(DemographySector[[S]], NextCohort)
}

# Convert numeric columns to integers
SupplyDemand <- as.data.frame(lapply(SupplyDemand, function(x) {
    if(is.numeric(x)) {as.integer(round(x))} else {x}
}))

Order <- c(ba = 1, gr = 2, lu = 3, ph = 4, pe = 5, yr = 6, py = 7)

SupplyDemand$EducationOrdered <- SupplyDemand$Education
SupplyDemand$EducationOrdered <- with(SupplyDemand, names(Order)[match(Education, names(Order))])
SupplyDemand$EducationOrdered <- factor(SupplyDemand$EducationOrdered, levels = names(Order))

SupplyDemand <- SupplyDemand %>% arrange(EducationOrdered, Year)

SupplyDemand$EducationOrdered <- NULL
SupplyDemand$Education <- factor(SupplyDemand$Education, 
                                 levels = c("ba", "gr", "lu", "ph", "pe", "yr", "py"),
                                 labels = c("Preschool Teachers", "Primary School Teachers",
                                            "Teachers with a Master's Degree", "PGCE",
                                            "Teachers of Practical and Aesthetic Subjects",
                                            "Vocational Teachers", "PGCE in Vocational Education"))

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
