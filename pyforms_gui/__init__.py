#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__      = "Ricardo Ribeiro"
__credits__     = ["Ricardo Ribeiro"]
__license__     = "MIT"
__version__ = "4.904.149"
__maintainer__  = "Ricardo Ribeiro"
__email__       = "ricardojvr@gmail.com"
__status__      = "Development"

from confapp import conf

try:
    import local_settings
    conf += local_settings
except:
    pass

from . import settings as pyforms_settings
conf += pyforms_settings

import logging

logging.basicConfig(
    level=conf.PYFORMS_LOG_HANDLER_LEVEL,
    format=conf.PYFORMS_LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
