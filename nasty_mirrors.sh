#!/usr/bin/env bash
grep gd_apicode_cc $(find mirrors -type f -name '*.py') | sed 's/:.*$//' | sort -u
