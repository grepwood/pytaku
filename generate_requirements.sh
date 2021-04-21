#!/usr/bin/env bash

INTEGRATED_LIBS='sys|subprocess|winreg|pdb'

OWN_LIBS='mirrors|util'

grep import . -r | grep -vE '\.log|#|LICENSE|\.git' | grep \\.py: | sed 's/^.*://;s/\t*//;s/\ import.*$//;s/^from\ /import\ /;s/\..*$//' | grep -vE "${INTEGRATED_LIBS}|${OWN_LIBS}" | sort -u | sed 's/mega/mega\.py/;s/import\ //' > requirements.txt
