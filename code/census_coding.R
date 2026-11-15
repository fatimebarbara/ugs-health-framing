# -------------------------------------------------------------
# Archived as used for the first coding pass (17 Aug - 22 Sep 2026).
# Only the two folder paths have been replaced. The input file
# DirectionA_green_posts_census.csv contains the post texts and is not
# deposited (see README); the script is shared to document the coding
# procedure (Appendix C), not to be rerun on the deposited data.
# Reject reason 7 (within-language substring) was typed by the coder
# during the census and is not in the menu below.
# -------------------------------------------------------------

# =============================================================
# DIRECTION A — FULL CENSUS CODING
# Green space framing in European mayoral communication
#
# 1,520 posts total. 105 already done in the pilot.
# 1,415 remaining. Resume any time; saves after every post.
# =============================================================

library(tidyverse)

drive_folder <- "path/to/project_folder"   # path removed for publication
local_folder <- path.expand("path/to/local_working_folder")   # path removed for publication
dir.create(local_folder, showWarnings = FALSE)

census_out <- file.path(local_folder, "census_coded.csv")

setwd(drive_folder)


# ---- 1. BUILD THE WORKING FILE (run once) -------------------

census <- read_csv("DirectionA_green_posts_census.csv", col_types = cols(.default = "c")) %>%
  mutate(row = as.integer(row)) %>%
  select(-any_of(c("tier1_health_word", "tier2_mechanism")))   # stay blind to the machine

if (!"reject_reason" %in% names(census)) census$reject_reason <- NA_character_
if (!"coded_at"      %in% names(census)) census$coded_at      <- NA_character_

# The 105 pilot decisions are embedded below, so no extra file is needed.
# Format: censusRow,codes,rejectReason   (codes: h c a e $ n)
pilot_raw <- paste0(
  "3,n,;17,ha,;21,hce,;35,cae,;57,hcae,;85,cae$,;111,,PARTY;113,,PARTY;117,,NO REFERENT;",
  "121,e,;153,hcae,;160,,NO REFERENT;163,,NO REFERENT;193,ae,;219,cae,;226,hce,;239,he,;",
  "244,hcae$,;253,,PROPER NOUN;261,,POLICY;279,e,;315,,PROPER NOUN;316,c,;317,hae,;",
  "346,,PARTY;348,e$,;353,n,;365,n,;410,,PARTY;413,,PARTY;432,,PARTY;437,hce,;515,cae,;",
  "517,a,;525,hcae,;523,$,;539,hce$,;556,,PARTY;594,c,;597,,PARTY;614,e,;626,h,;638,ca,;",
  "649,,PARTY;651,n,;660,h,;679,he,;683,,PARKING;702,,PARTY;711,,PARTY;729,n,;766,ae,;",
  "767,ce,;771,hce,;795,a,;801,,NO REFERENT;803,hcae$,;806,hca,;807,n,;822,n,;832,e$,;",
  "878,ae,;896,,NO REFERENT;914,hcae,;918,hca,;925,hca,;959,a$,;975,ca$,;1009,n,;1022,e,;",
  "1025,a$,;1032,a$,;1051,,PARTY;1075,,PARTY;1093,n,;1102,,NO REFERENT;1144,hcae$,;",
  "1151,ce,;1153,ce$,;1154,hce,;1188,a,;1191,,NO REFERENT;1214,hcae$,;1216,,FALSE FRIEND;",
  "1218,,FALSE FRIEND;1237,a$,;1242,e,;1247,,;1284,n,;1292,a,;1321,cae$,;1343,hc$,;",
  "1353,,NO REFERENT;1387,,NO REFERENT;1402,e,;1410,e,;1412,ca$,;1422,hca,;1435,ae,;",
  "1438,a,;1440,n,;1447,hcae$,;1451,,NO REFERENT;1456,hae$,;1482,,NO REFERENT"
)

pilot <- tibble(raw = str_split(pilot_raw, ";")[[1]]) %>%
  separate(raw, into = c("row","codes","reject_reason"), sep = ",", fill = "right") %>%
  mutate(row = as.integer(row),
         codes = replace_na(codes, ""),
         reject_reason = na_if(str_trim(replace_na(reject_reason, "")), ""),
         function_health   = if_else(str_detect(codes, "h"), "1", NA_character_),
         function_climate  = if_else(str_detect(codes, "c"), "1", NA_character_),
         function_amenity  = if_else(str_detect(codes, "a"), "1", NA_character_),
         function_equity   = if_else(str_detect(codes, "e"), "1", NA_character_),
         function_economic = if_else(str_detect(codes, fixed("$")), "1", NA_character_),
         function_none     = if_else(str_detect(codes, "n"), "1", NA_character_),
         coded_at = "pilot") %>%
  select(row, starts_with("function_"), reject_reason, coded_at)

census <- census %>% rows_update(pilot, by = "row", unmatched = "ignore")

cat("total", nrow(census), "| already coded", sum(!is.na(census$coded_at)),
    "| remaining", sum(is.na(census$coded_at)), "\n")


# ---- 2. THE CODING FUNCTION ---------------------------------
#   h health   c climate   a amenity   e equity   $ economic   n none
#   r reject   s skip   q quit and save
#
# reject reasons: 1 PARTY  2 NO REFERENT  3 PROPER NOUN
#                 4 FALSE FRIEND  5 POLICY  6 PARKING

code_census <- function(dat, out = census_out, target = Inf) {

  if (file.exists(out)) {
    done <- read_csv(out, col_types = cols(.default = "c")) %>%
      mutate(row = as.integer(row)) %>%
      select(row, starts_with("function_"), reject_reason, coder_notes, coded_at)
    dat <- dat %>% rows_update(done, by = "row", unmatched = "ignore")
  }

  todo <- which(is.na(dat$coded_at))
  if (length(todo) == 0) { message("Census complete."); return(invisible(dat)) }

  start_n <- sum(!is.na(dat$coded_at))
  session <- 0
  t0 <- Sys.time()

  for (i in todo) {
    if (session >= target) { message("Session target reached."); break }

    done_n <- sum(!is.na(dat$coded_at))
    pct <- round(100 * done_n / nrow(dat))

    cat("\014")
    cat(sprintf("[%s%s] %d/%d  %d%%   this session: %d\n",
                strrep("#", pct %/% 4), strrep(".", 25 - pct %/% 4),
                done_n, nrow(dat), pct, session))
    cat(strrep("=", 70), "\n")
    cat(dat$city[i], "  |  ", dat$referent[i], "  |  ", dat$date[i], "\n", sep = "")
    cat(strrep("=", 70), "\n\n")
    cat(str_wrap(dat$text[i], width = 68), "\n\n")
    cat(strrep("-", 70), "\n")
    cat("h health   c climate   a amenity   e equity   $ economic   n none\n")
    cat("r reject   s skip   q quit and save\n")

    ans <- str_to_lower(str_trim(readline("Code(s): ")))

    if (ans == "q") break
    if (ans == "s") next

    if (ans == "r") {
      cat("1 PARTY  2 NO REFERENT  3 PROPER NOUN  4 FALSE FRIEND  5 POLICY  6 PARKING\n")
      rr <- str_trim(readline("Reason: "))
      dat$reject_reason[i] <- c("PARTY","NO REFERENT","PROPER NOUN",
                                "FALSE FRIEND","POLICY","PARKING")[as.integer(rr)]
    } else {
      dat$function_health[i]   <- if (str_detect(ans, "h")) "1" else NA
      dat$function_climate[i]  <- if (str_detect(ans, "c")) "1" else NA
      dat$function_amenity[i]  <- if (str_detect(ans, "a")) "1" else NA
      dat$function_equity[i]   <- if (str_detect(ans, "e")) "1" else NA
      dat$function_economic[i] <- if (str_detect(ans, fixed("$"))) "1" else NA
      dat$function_none[i]     <- if (str_detect(ans, "n")) "1" else NA
    }

    nt <- str_trim(readline("Notes (Enter to skip): "))
    if (nzchar(nt)) dat$coder_notes[i] <- nt

    dat$coded_at[i] <- as.character(Sys.time())
    session <- session + 1
    write_csv(dat, out)
  }

  write_csv(dat, out)
  mins <- as.numeric(difftime(Sys.time(), t0, units = "mins"))
  cat("\n")
  cat("coded this session:", session, "in", round(mins), "min",
      if (session > 0) sprintf("(%.0f/hour)", session / (mins/60)) else "", "\n")
  cat("total done:", sum(!is.na(dat$coded_at)), "of", nrow(dat), "\n")
  cat("remaining:", sum(is.na(dat$coded_at)), "\n")
  invisible(dat)
}


# ---- 3. CODE ------------------------------------------------
# Run this. Press q to stop; rerun to resume.
# To cap a session, e.g. 100 posts:  code_census(census, target = 100)

census <- code_census(census)


# ---- 4. PROGRESS CHECK (run any time) -----------------------

prog <- read_csv(census_out, col_types = cols(.default = "c"))
prog %>%
  group_by(city) %>%
  summarise(total = n(),
            done = sum(!is.na(coded_at)),
            left = total - done) %>%
  arrange(desc(left)) %>%
  print(n = 25)


# ---- 5. RESULTS (run when the census is complete) -----------

coded <- read_csv(census_out, col_types = cols(.default = "c"))
stopifnot(all(!is.na(coded$coded_at)))          # refuses to run early

valid <- coded %>% filter(is.na(reject_reason))
FN <- c("function_health","function_climate","function_amenity",
        "function_equity","function_economic","function_none")

cat("\n=== CENSUS RESULT ===\n")
cat("retrieved      ", nrow(coded), "\n")
cat("rejected       ", sum(!is.na(coded$reject_reason)),
    sprintf(" (%.0f%%)\n", 100*mean(!is.na(coded$reject_reason))))
cat("valid green    ", nrow(valid), "\n\n")

valid %>%
  summarise(across(all_of(FN), ~ sum(.x == "1", na.rm = TRUE))) %>%
  pivot_longer(everything(), names_to = "function", values_to = "n") %>%
  mutate(`function` = str_remove(`function`, "function_"),
         pct = round(100 * n / nrow(valid), 1)) %>%
  arrange(desc(n)) %>%
  print()

cat("\n=== REJECT LOG ===\n")
coded %>% filter(!is.na(reject_reason)) %>% count(reject_reason, sort = TRUE) %>% print()

cat("\n=== BY CITY ===\n")
valid %>%
  group_by(city) %>%
  summarise(n = n(),
            health = sum(function_health == "1", na.rm = TRUE),
            pct = round(100*health/n, 1)) %>%
  arrange(desc(pct)) %>%
  print(n = 25)

# copy the finished file to Drive
file.copy(census_out, file.path(drive_folder, "census_coded.csv"), overwrite = TRUE)
