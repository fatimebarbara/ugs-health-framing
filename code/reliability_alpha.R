# Intra-coder reliability (Table 4), R version. No packages needed.
# Run from the repository root:  Rscript code/reliability_alpha.R

kalpha_nominal <- function(a, b) {
  n  <- 2 * length(a)
  Do <- mean(a != b)
  nc <- sapply(sort(unique(c(a, b))), function(v) sum(a == v) + sum(b == v))
  De <- 1 - sum(nc * (nc - 1)) / (n * (n - 1))
  if (De == 0) return(NA)
  1 - Do / De
}

s  <- read.csv("data/recode_sample_128.csv")
t4 <- s[s$in_table4 == 1, ]
cat(sprintf("Table 4, n = %d\n", nrow(t4)))
for (f in c("health", "climate", "amenity", "equity", "economic", "none")) {
  a <- t4[[paste0("pass1_", f)]]
  b <- t4[[paste0("recode_", f)]]
  cat(sprintf("%-9s alpha = %.2f  agreement = %3.0f%%  pass 1 = %2d  pass 2 = %2d\n",
              f, kalpha_nominal(a, b), 100 * mean(a == b), sum(a), sum(b)))
}
