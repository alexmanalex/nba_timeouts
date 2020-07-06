---
title: "Untitled"
author: "Alex Mansourati"
date: "01/07/2020"
output:
  pdf_document:
    latex_engine: xelatex
---




```
## ── Attaching packages ───────────── tidyverse 1.3.0 ──
```

```
## ✓ ggplot2 3.2.1     ✓ purrr   0.3.3
## ✓ tibble  2.1.3     ✓ dplyr   0.8.3
## ✓ tidyr   1.0.0     ✓ stringr 1.4.0
## ✓ readr   1.3.1     ✓ forcats 0.4.0
```

```
## ── Conflicts ──────────────── tidyverse_conflicts() ──
## x dplyr::filter() masks stats::filter()
## x dplyr::lag()    masks stats::lag()
```


```
## 
## Attaching package: 'kableExtra'
```

```
## The following object is masked from 'package:dplyr':
## 
##     group_rows
```

\begin{table}[!h]

\caption{\label{tab:unnamed-chunk-2}Estimates for the average causal effect of timeouts on the scoring run in three minutes post-timeout}
\centering
\begin{tabular}[t]{l|r|r|r}
\hline
Method & ATT & CATT (+ve Scoring Run) & CATT (-ve Scoring Run)\\
\hline
Naive & 1 & 1 & 1\\
\hline
Matching + Standardization & 2 & 2 & 2\\
\hline
\end{tabular}
\end{table}


