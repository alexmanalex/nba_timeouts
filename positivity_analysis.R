df = read.csv('output/nba_timeouts_analysis.csv')
df = df[df$outcome > -12,]
df = df[df$outcome < 12,] 


treated = df[df$treatment==1, ]
untreated = df[df$treatment==0, ]


covariates = c('scoring_run', 'coach_exp', 'time_since_last_break', 
               'point_diff')
bucketed_covariates = c()
num_breaks = 10

for (cov in covariates){
  colname = paste(cov, '_bucketed', sep="")
  bucketed_covariates = append(bucketed_covariates, colname)
  df[colname] = cut(df[,cov], breaks=num_breaks)
}

a = group_by(df, scoring_run_bucketed, coach_exp_bucketed, 
             time_since_last_break_bucketed, point_diff_bucketed, treatment)
b = summarise(a, num = n())

treatment_strata = b[b$treatment==1,]
nontreatment_strata = b[b$treatment==0,]

a = anti_join(x=treatment_strata, y=nontreatment_strata, 
          by=bucketed_covariates)

a = a[order(-a$num),]

write.csv(a, file = 'missing_untreated_strata.csv')
