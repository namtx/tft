#!/bin/bash

scrapy runspider -a name=${1} --nolog champions.py
