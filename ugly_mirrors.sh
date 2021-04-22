#!/usr/bin/env bash
grep browser $(find mirrors -type f -name '*.py') | sed 's/:.*$//' | sort -u
