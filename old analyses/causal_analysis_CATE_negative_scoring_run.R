library(boot)

#Set the working direcrtory to file location
df = read.csv('output/nba_timeouts_analysis.csv')

#Some plots to evaluate outliers
plot(density(df$outcome))

# Removes ~4% of rows as outliers
df = df[df$outcome > -12,]
df = df[df$outcome < 12,] 

#Conditional on positive scoring run
df = df[df$scoring_run < 0,]

treated_index_start = 0
treated_index_end = nrow(df[df$treatment==1,])
untreated_index_start = as.integer(nrow(df[df$treatment==1,])+1)
untreated_index_end = nrow(df)


#Naive, Difference in Conditional Means
treated = df[df$treatment==1,]
untreated = df[df$treatment==0,]
naive_ACE = mean(treated[['outcome']]) - mean(untreated[['outcome']])
naive_ACE_std = ((var(treated[['outcome']]) + var(untreated[['outcome']]))/nrow(df))**0.5
naive_ACE_CI = naive_ACE + c(-1, 1) * 1.96 * naive_ACE_std

#IP Weighting
treatment_model = glm(treatment ~ scoring_run + coach_exp + time_since_last_break + point_diff, data=df, family="binomial")

ip_weights_treated = 1 /predict(treatment_model, type="response")
ip_weights_treated = ip_weights_treated[treated_index_start:treated_index_end]

ip_weights_untreated = 1/(1-predict(treatment_model, type="response"))
ip_weights_untreated = ip_weights_untreated[untreated_index_start:untreated_index_end]
ip_weights = c(ip_weights_treated, ip_weights_untreated)

ps_outcome_mean = lm(outcome~treatment, data=df, weights=ip_weights)
ip_ACE = coefficients(ps_outcome_mean)['treatment']
ip_std = sqrt(diag(vcov(ps_outcome_mean)))[2]
ip_ACE_CI = ip_ACE + c(-1, 1) * 1.96 * ip_std

#Standardization

outcome_model = lm(outcome~treatment+scoring_run+coach_exp+time_since_last_break+point_diff, data=df)
df_all_treated = df
df_all_treated$treatment = 1
df_none_treated = df
df_none_treated$treatment = 0
df_standardization = rbind(df_all_treated, df_none_treated)
outcomes = predict(outcome_model, newdata=df_standardization)
treated_index_start = 0
treated_index_end = nrow(df_all_treated)
untreated_index_start = as.integer(nrow(df_all_treated) + 1)
untreated_index_end = nrow(df_standardization)
standardization_ACE = (sum(outcomes[treated_index_start:treated_index_end]) / nrow(df_all_treated)) - (sum(outcomes[untreated_index_start:untreated_index_end]) / nrow(df_none_treated))

fc <- function(df,i){
  df_boot <- df[i,]
  outcome_model = lm(outcome~treatment+scoring_run+coach_exp+time_since_last_break+point_diff, data=df_boot)
  df_all_treated = df_boot
  df_all_treated$treatment = 1
  df_none_treated = df_boot
  df_none_treated$treatment = 0
  df_standardization = rbind(df_all_treated, df_none_treated)
  outcomes = predict(outcome_model, newdata=df_standardization)
  treated_index_start = 0
  treated_index_end = nrow(df_all_treated)
  untreated_index_start = as.integer(nrow(df_all_treated) + 1)
  untreated_index_end = nrow(df_standardization)
  standardization_ACE = (sum(outcomes[treated_index_start:treated_index_end]) / nrow(df_all_treated)) - (sum(outcomes[untreated_index_start:untreated_index_end]) / nrow(df_none_treated))
  return(standardization_ACE)
}

boot_standardization_ACE <- boot(df, fc, R=500)
standardization_CI = toString(standardization_ACE + c(-1,1) * 1.96 * sd(boot_standardization_ACE$t))


cat('ACE (Naive):', naive_ACE, ', CI:', naive_ACE_CI,
    '\nACE (via IP Weighting):', ip_ACE, ', CI:', ip_ACE_CI,
    '\nACE (via Standardization):', standardization_ACE, ', CI:', standardization_CI)
