# 0 - Genereal Information ----

# Open data table
Data <- read.table("Res-AllTaps.txt", header=TRUE, dec=".", na.string="NaN")
head(Data)

# Define independent variables
Data$Group <- as.factor(as.character(Data$Group))
Data$Pattern <- as.factor(as.character(Data$Pattern))
Data$Sujet <- as.factor(as.character(Data$Sujet))

# Filter datatable to consider a subset of data
Data_PeriodicAlong <- subset(Data, (Pattern==1))
Data_PNS_AperiodicAlong <- subset(Data, (Pattern==1)&(Group==0))

# 1 - Generalized linear model ----

Data_subject <- subset(Data, (Data$Sujet==9))
VD <- Data_subject$RT

# Descriptive stats
boxplot(VD~Pattern, data=Data_subject)
# For the subject in question the RT in the periodic condition is, as expected, 
# around 0, however half of the values seems to be negative as the subject 
# predicts the stimuli. As for the aperiodic condition, the RT it seems to be 
# around 0.4 including 0.5 in between the median and the first quartile.


# Linear model
M1 <- lm(VD~Pattern, data=Data_subject, na.action=na.exclude)
summary(M1)
# The linear model demonstrates that the Pattern variable significantly explains
# 59% of RT's variability. Specifically in the aperiodic condition RT is 
# significantly longer by 0.443 seconds.


# Contrast / Pairwise comparison
library(multcomp)
Contrast <- cbind(1,0)
Contrast <- rbind(Contrast, cbind(1,1)) # Test periodic diff 0 and aperiodic diff 0
Niveaux <- glht(M1, linfct=Contrast)
summary(Niveaux)
# Periodic condition (Intercept): the mean RT for the periodic condition is not 
# significantly different from 0 (p-value=0.302)
# Aperiodic condition (Intercept + Pattern=2): the mean RT for the aperiodic 
# condition is significantly different from 0 (p-value<1e−10)

Contrast <- cbind(0,1) # test difference between aperiodic and peridic RT
Niveaux <- glht(M1, linfct=Contrast)
summary(Niveaux)
# The test shows that the difference between the aperiodic condition and the 
# periodic  condition is significalty different from 0, with the aperiodic 
# condition having higher RT by approximately 0.4435s  




# 2 - Linear mixed model ----
Data_PNS <- subset(Data,(Data$Group==0))
VD <- Data_PNS$RT

# Descriptive stats
boxplot(VD~Pattern, data=Data_PNS)
# The boxplot visually confirms that the aperiodic condition leads to longer 
# and more variable RT compared to the periodic condition, consistent with the 
# previous statistical analysis showing a significant difference in RT between 
# the two conditions

# Mixed models
library(nlme)
M1 <- lme(VD~Pattern, random=~1|Sujet, data=Data_PNS, method="ML", na.action=na.exclude)
summary(M1)
# Pattern significantly affects RT with aperiodic condition increasing RT by 
# 0.3005 seconds compared to the periodic condition (p-value < 2e−16)

# Contrasts / Pairwise comparison
Contrast <- cbind(1,0)
Contrast <- rbind(Contrast, cbind(1,1))
Niveaux <- glht(M1, linfct=Contrast)
summary(Niveaux)
# The test confirms that both conditions have mean RTs significantly different 
# from 0, with the aperiodic condition having a larger mean RT, indicating 
# significant impact of the condition on RT

Contrast <- cbind(0,1)
Niveaux <- glht(M1, linfct=Contrast)
summary(Niveaux)
# The contrast test confirms that the difference in mean RT between the two 
# conditions is significant 

# 3 - Linear mixed models ----
VD <- Data$RT

# Descriptive stats
boxplot(VD~Pattern*Group, data=Data)
# The boxplot indicates clear differences in reaction time based on both 
# Pattern and Group, with noticeable effects of variability and outliers 
# in the aperiodic condition, particularly for PWS subjects

# Mixt model
library(nlme)
# Test intreaction between Pattern and Group
M1 <- lme(VD~Pattern *Group, random=~1|Sujet, data=Data, method="ML",na.action=na.exclude)
summary(M1)
# The model highlight that the conditions have a strong effect on RT, while 
# group  does not independently influence RT significantly
# However the interaction between Pattern and Group suggests that group slightly
# moderates the effect of the condition.

# Exploration of the interaction between factors and model simplification
# Test independent contributions of Pattern and Group
M2<-lme(VD~Pattern+Group, random=~1|Sujet, data=Data, method="ML", na.action=na.exclude)
anova(M1, M2)
BIC(M1)
BIC(M2)
# The interaction term (Pattern * Group) significantly improves the model fit, 
# indicating that the effect of Pattern on RT varies by Group and that effect
# shouldn't be ignored. Therefore, the more complex model M1 is preferred over 
# the simpler model M2
# While BIC slightly favors M1 the difference is minimal. So the choice of M1 
# is further supported by the statistical test

M3<-lme(VD~Pattern, random=~1|Sujet, data=Data, method="ML", na.action=na.exclude)
anova(M3, M2)
# The p-value of 0.7092 indicates that the inclusion of the Group does not 
# significantly improve the model fit. The main effect of Group is not important
# for explaining the variability in RT. Both AIC and BIC also favor the simpler 
# model (M3)

M4<-lme(VD~Group, random=~1|Sujet, data=Data, method="ML", na.action=na.exclude)
anova(M4, M2)
# The variable Pattern is critical for explaining variability in RT
# The simpler model M4 which includes only Group is insufficient. The highly 
# significant improvement when adding Pattern (p<0.0001) suggests that any 
# meaningful model for RT must include Pattern as a predictor

BIC(M2)
BIC(M3)
BIC(M4)
# The smaller value of BIC is for M3, the simpler model M3 is preferred over the 
# more complex model M2 and M1 that does not capture key predictors

# Null model
# Does adding predictors (Pattern, Group,...) significantly improve the 
# explanation of variability in RT beyond this simplest baseline model?
M5<-lme(VD~1, random=~1|Sujet, data=Data, method="ML", na.action=na.exclude)
anova(M4, M5)
BIC(M4)
BIC(M5)
# The comparison shows that adding Group as a predictor in M4 does not 
# significantly improve the model's ability to explain variability in RT 
# compared to the null model (M5). The value of BIC for M5 alsoe supports the 
# conclusion that M5 is preffered over M4.


# Contrasts - Pairwise comparisions
# If significant interaction
Contrast <- cbind(1, 0, 0, 0) # PNS in Condition 1
Contrast <- rbind(Contrast, cbind(1, 1, 0, 0 )) # PNS in Condition 2
Contrast <- rbind(Contrast, cbind(1, 0, 1, 0)) # PWS in Condition 1
Contrast <- rbind(Contrast, cbind(1, 1, 1, 1)) # PWS in Condition 2
Niveaux <- glht(M1, linfct=Contrast)
summary(Niveaux)

Contrast <- cbind(0, 0, 1, 0) # Group effect (PWS-PNS) in condition 1
Contrast <- rbind(Contrast, cbind(0, 0, 1, 1 )) # Group effect (PWS-PNS) in condition 2
Niveaux <- glht(M1, linfct=Contrast)
summary(Niveaux)

Contrast <- cbind(0, 1, 0, 0) # Condition effect (Aperiodic-Periodic) in PNS
Contrast <- rbind(Contrast, cbind(0, 1, 0, 1 )) # Condition effect in PWS
Niveaux <- glht(M1, linfct=Contrast)
summary(Niveaux)

# If no significant interaction
Contrast <- cbind(1, 0, 0) # PNS in Condition 1
Contrast <- rbind(Contrast, cbind(1, 1, 0)) # PNS in Condition 2
Contrast <- rbind(Contrast, cbind(1, 0, 1)) # PWS in Condition 1
Contrast <- rbind(Contrast, cbind(1, 1, 1)) # PWS in Condition 2
Niveaux <- glht(M2, linfct=Contrast)
summary(Niveaux)

Contrast <- cbind(0, 0, 1) # Group effect (PWS-PNS)
Niveaux <- glht(M2, linfct=Contrast)
summary(Niveaux)

Contrast <- cbind(0, 1, 0) # Condition effect (Aperiodic-Periodic)
Niveaux <- glht(M2, linfct=Contrast)
summary(Niveaux)

Contrast <- rbind(c(0, 0, 1)) # Group1 + Pattern2:Group1
Niveaux <- glht(M2, linfct = Contrast)
summary(Niveaux)


# 4 - Group Difference of stdIRI ----

# Read data
DataTrain <- read.table("Res-StdIRI.txt", header=TRUE, dec=".", na.string="NaN")
head(DataTrain)

VD <- DataTrain$stdIRI

# Visualize data
boxplot(VD~Group, data=DataTrain, main="Standard Deviation of IRI For Both Groups", names=c("PNS", "PWS"), ylab="stdIRI")

# Test groups
library(nlme)
M1 <- lme(VD~Group, random=~1|Sujet, data=DataTrain, method="ML", na.action=na.exclude)

# Group effect (PWS-PNS)
library(multcomp)
Contrast <- rbind(c(0, 1)) # Test Group1 coefficient
Niveaux <- glht(M1, linfct = Contrast)
summary(Niveaux)
# This indicates that there is a significant difference in stdIRI between 
# groups, with PWS > PNS


# 5 - Conclusion ----

#Do PWS have difficulties in the initiation of movements compared to PNS? 
#Yes, the results indicate that PWS have longer reaction times, which suggests 
# challenges in movement initiation. This finding was consistent across 
# conditions and supports the movement initiation hypothesis.

#Are PWS able to anticipate the appearance of a regular beat in the periodic 
# condition, like PNS? 
# While PWS demonstrated the ability to anticipate a regular beat, their 
# synchronization was less consistent and more variable than that of PNS. 
# This indicates partial capability but reduced efficiency compared to typical 
# speakers.

# Are PWS able to sustain a regular rhythm with similar accuracy and consistency
# as PNS? 
# No, PWS showed significantly greater variability in IRI, suggesting they face
# difficulties in maintaining a regular rhythm. This observation aligns with the
# regularity hypothesis.
