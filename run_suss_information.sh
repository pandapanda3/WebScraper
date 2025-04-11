#!/bin/bash
# This shell script is used to run suss_information.py multiple times,
# each time passing in a different page number as an argument.

# Purpose: to scrape all courses offered by SUSS across multiple paginated results.
# The page number is passed as $PAGE to the Python script.

# This structure helps bypass anti-scraping defenses by:
# - Limiting scraping to one page per run
# - Inserting delays between requests
# - Mimicking user interaction within the Python script

# How to run this scraper:
# 1. Modify START=1 and END=3 below to define the page range you want to scrape.
# 2. Adjust the pre_url and after_url values inside suss_information.py if needed.
# 3. Run this shell script in the terminal:
#    ./run_suss_information.sh

START=1
END=3
PAGE_COUNTS=($(seq $START $END))

PYTHON_INTERPRETER="/Users/zhangpanpan/anaconda3/envs/Resume_Refiner/bin/python"

for PAGE in "${PAGE_COUNTS[@]}"
do
  echo "Running scraper with page_count = $PAGE"
  $PYTHON_INTERPRETER suss_information.py $PAGE
  echo "Done with page_count = $PAGE"
  sleep 2
done