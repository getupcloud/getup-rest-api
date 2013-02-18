#!/usr/bin/env python

import sys
import os

os.environ['APP_ROOT'] = os.path.dirname(__file__)
os.environ['CONFIG_FILE'] = os.environ['APP_ROOT'] + '/getup-rest-api-devel.conf'
sys.path.insert(0, '.')

import getup
