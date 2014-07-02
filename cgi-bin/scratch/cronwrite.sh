#!/bin/bash

(crontab -l ; echo "$1 * * * * your_command") | sort - | uniq - | crontab -
