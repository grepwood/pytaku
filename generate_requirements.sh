#!/usr/bin/env bash
INTEGRATED_LIBS='^sys$|^subprocess$|^winreg$|^pdb$|^json$|^re$|^traceback$|^os$|^tarfile$|^zipfile$|^difflib$|^getopt$|^itertools$|^time$'
OWN_LIBS='^mirrors$|^util$|^shinden$|^browser$'
grep -E '^import\ |^from\ .*\ import\ ' $(find . -type f -name '*.py') | sed 's/^.*://;s/\t*//;s/\ import.*$//;s/^from\ /import\ /;s/\..*$//;s/^import\ //' | grep -vE "${INTEGRATED_LIBS}|${OWN_LIBS}" | sort -u > requirements.txt
