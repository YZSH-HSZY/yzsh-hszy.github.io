import re
from typing import Dict, List
import xml
import logging
import sys
from os.path import splitext, join, dirname, basename, abspath
from pathlib import Path
import xml.etree
import xml.etree.ElementTree
import xml.parsers
from pelican.contents import Article
from pelican.generators import ArticlesGenerator
from pelican import signals
from bs4 import BeautifulSoup

from html.parser import HTMLParser

class ImgLabelHTMLParser(HTMLParser):
    ATTRS_VALUES: List[Dict[str, str]] = []
    HANDLE_SIGN: List[bool] = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.HANDLE_SIGN = True
            img_attrs = dict(attrs)
            if '{' in ''.join(img_attrs.values()):
                self.HANDLE_SIGN.append(False)
            else:
                self.HANDLE_SIGN.append(True)
            self.ATTRS_VALUES.append(dict(attrs))

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

log = logging.getLogger(__name__)

def generate_img_plugin(article_gen: ArticlesGenerator):

    for article in article_gen.articles:
        article: Article

        content_path = Path(article_gen.path).resolve()
        article_path = Path(article.source_path).resolve()
        
        html_parse = ImgLabelHTMLParser()
        html_parse.feed(article.content)

        article_relative_path = ''
        # handle article in subdir of generate dir
        if article_path.parent != content_path:
            article_relative_path = article_path.parent.relative_to(content_path)

        static_links = set()

        match_re = re.compile(
            r"(?P<prefix><\s*img.*?src\s*=\s*)"
            r"(?P<scope>['\"])(?P<value>.*?)(?P=scope)", 
        )
        label_img_iter = re.finditer(match_re, article.content)
        changing_iter = zip(html_parse.HANDLE_SIGN, html_parse.ATTRS_VALUES)
        for idx, sign in enumerate(html_parse.ATTRS_VALUES):
            if not sign: continue
            img = html_parse.ATTRS_VALUES[idx]
            img_relative_path = Path(img['src'])
            if article_relative_path:
                img_relative_path = Path(article_relative_path) / Path(img['src'])
            path = (content_path / img_relative_path).resolve().absolute()
            # path = content_path.joinpath('static') / img_relative_path
            static_links.add(str(path))
        article_gen.context['static_links'] |= static_links
        # breakpoint()
        # repair img label src path
        if getattr(html_parse, 'HANDLE_SIGN', False):
            
            changing_path = ''
            article._content = re.sub(
                match_re, 
                lambda m: m.group("prefix") + m.group("scope") + \
                    f"{article}{m.group("value")}" + m.group("scope"), 
                article.content
            )
            # clear `memoized` property classs cache
            if hasattr(article.get_content, 'cache') and \
                    isinstance(article.get_content.cache, dict):
                article.get_content.cache.pop((article, article.get_siteurl()))
            

def register():
    # signals.initialized.connect(test)
    signals.article_generator_pretaxonomy.connect(generate_img_plugin)

# import logging
# import re
# from pathlib import Path

# from bs4 import BeautifulSoup
# from pelican.contents import Article

# from pelican import signals

# logger = logging.getLogger(__name__)


# def test2(article_generator):
#     for article in article_generator.articles:
#         content_path = Path(article_generator.path)
#         source_path = Path(article.source_path)
#         if content_path != source_path.parent:
#             # if a article resides in /contents/some_sub_dir,
#             # we need to update the relative path (add a prefix)
#             prefix = source_path.parent.relative_to(content_path)
#             logger.warning(f'adding prefix "{prefix}" to src of img of "{source_path}"')
#             soup = BeautifulSoup(article.content, "html.parser")
#             for img in soup.find_all('img'):
#                 img['src'] = str(prefix / img['src'])
#             article._content = str(soup)

#             # FIXME: this is dirty...
#             class _Article(Article):
#                 @property
#                 def content(self):
#                     content = self._content
#                     return self._update_content(content, self.get_siteurl())

#             article.__class__ = _Article

#         static_links = set()
#         img = re.compile(r'<img.*src="(.*)">')
#         for res in img.finditer(article.content):
#             img_relative_path = Path(res[1])
#             path = source_path.parent / img_relative_path
#             static_links.add(path)
#         article_generator.context['static_links'] |= static_links


# def register():
#     signals.article_generator_pretaxonomy.connect(test2)