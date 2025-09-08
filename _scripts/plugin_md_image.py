"""
the plugin for generate img label
"""
import os
import re
from typing import Dict, List, Tuple
import logging
from os.path import splitext, join, dirname, basename, abspath
from pathlib import Path
from pelican.contents import Article
from pelican.generators import ArticlesGenerator
from pelican import signals

from html.parser import HTMLParser

class ImgLabelHTMLParser(HTMLParser):
    ATTRS_VALUES: List[Dict[str, str]]
    HANDLE_SIGN: List[bool]

    STATIC_PATHS: List[str] = []

    @classmethod
    def set_static_paths(cls, paths: List[str]):
        if not isinstance(paths, list): return
        cls.STATIC_PATHS = paths

    def __init__(self, *args):
        super().__init__(*args)
        self.ATTRS_VALUES = []
        self.HANDLE_SIGN = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        if tag == 'img':
            img_attrs = dict(attrs)
            if '{' in ''.join(img_attrs.values()):
                self.HANDLE_SIGN.append(False)
            elif any([
                    img_attrs.get('src', '').startswith(p) 
                        for p in self.STATIC_PATHS
                ]):
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

    def article_content_replace(
            source: str, 
            scopes_values: List[Tuple[Tuple[int, int], str]]
        ) -> str:
        ret = ''
        assert all([len(scope[0]) == 2 for scope in scopes_values]), \
            "Fail: scope len is not 2"
        
        for idx, (scope, target) in enumerate(scopes_values):
            if idx == 0:
                ret += source[:scope[0]] + target
                if idx == len(scopes_values) - 1: ret += source[scope[1]:]
                continue
            ret += source[scopes_values[idx - 1][0][1]:scope[0]] + target
            if idx == len(scopes_values) - 1:
                ret += source[scope[1]:]
        return ret
    
    for article in article_gen.articles:
        article: Article

        content_path = Path(article_gen.path).resolve()
        article_path = Path(article.source_path).resolve()
        
        ImgLabelHTMLParser.set_static_paths(
            article_gen.settings.get('STATIC_PATHS', []))
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
        label_img_iter = list(re.finditer(match_re, article.content))
        signs_len = len(html_parse.HANDLE_SIGN)
        attrs_len = len(html_parse.ATTRS_VALUES)
        labels_len = len(label_img_iter)

        assert signs_len == attrs_len == labels_len, \
            (
                "Fail: re match img label number is not equal "
                f"html-parse img label number, signs_len: {signs_len}, "
                f"attrs_len: {attrs_len}, labels_len: {labels_len}"             
            )
        changing_iter = zip(
            html_parse.HANDLE_SIGN, 
            html_parse.ATTRS_VALUES, 
            label_img_iter
        )

        source_content = article.content
        replace_scopes_values: List[Tuple[Tuple[int, int], str]] = []
        
        for idx, (sign, atts, match_g) in enumerate(changing_iter):
            if not sign: continue
            img_relative_path = Path(atts['src'])
            if article_relative_path:
                img_relative_path = Path(
                    article_relative_path) / Path(atts['src'])
            path = (content_path / img_relative_path).resolve().absolute()
            # path = content_path.joinpath('static') / img_relative_path
            # "".startswith("STATIC")
            # list(filter(lambda x:x.startswith("STATIC"), article_gen.settings.keys()))
            static_output_path = content_path / (
                article_gen.settings['STATIC_SAVE_AS'].replace(
                    article_gen.settings['STATIC_URL'], ''
                ).strip('/')
            )
            after_relative_path = path.relative_to(content_path)
            after_relative_path = (static_output_path / after_relative_path
                ).relative_to(content_path)
            
            replace_scopes_values.append(
                (
                    (match_g.start(), match_g.end()), 
                    (
                        match_g.group("prefix") + 
                        match_g.group("scope") + 
                        f"/{after_relative_path.as_posix()}" + 
                        match_g.group("scope")
                    ).replace(os.sep, '/')
                )
            )

            static_links.add(str(path))
        article_gen.context['static_links'] |= static_links
        
        article._content = article_content_replace(
            source_content, 
            replace_scopes_values
        )

        # repair img label src path
        if any(html_parse.HANDLE_SIGN):
            # clear `memoized` property classs cache
            if hasattr(article.get_content, 'cache') and \
                    isinstance(article.get_content.cache, dict):
                article.get_content.cache.pop((article, article.get_siteurl()))
            

def register():
    signals.article_generator_pretaxonomy.connect(generate_img_plugin)
