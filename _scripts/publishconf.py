# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

AUTHOR = 'YZSH-HSZY'
SITENAME = 'Welcome to YZSH-HSZY blog.'

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = "https://yzsh-hszy.github.io"
RELATIVE_URLS = False

PATH = "content"
TIMEZONE = 'Asia/Shanghai'
DEFAULT_LANG = 'zh-cn'

FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"

DELETE_OUTPUT_DIRECTORY = True

DEFAULT_PAGINATION = 10

# Following items are often useful when publishing

# DISQUS_SITENAME = ""
# GOOGLE_ANALYTICS = ""

ARTICLE_SAVE_AS = "{date:%Y}-{date:%m}-{date:%d}-{slug}.html"
ARTICLE_URL = ARTICLE_SAVE_AS
PAGE_SAVE_AS = ARTICLE_SAVE_AS
PAGE_URL = ARTICLE_SAVE_AS