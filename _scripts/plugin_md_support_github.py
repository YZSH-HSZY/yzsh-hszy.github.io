"""
the pelican plugin to support github flavored markdown
"""
import collections
import re
from typing import Any, Tuple
from pelican import signals
from pelican.readers import BaseReader, MarkdownReader, DUPLICATES_DEFINITIONS_ALLOWED
from pelican.utils import pelican_open
import logging

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = False

# META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
MD_META_MORE_RE = re.compile(r'^[ ]{4,}(?P<value>.*)')
MD_MATE_BEGIN_RE = re.compile(r'^-{3}(\s.*)?')
MD_MATE_END_RE = re.compile(r'^(-{3}|\.{3})(\s.*)?')
MD_META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

class MarkdownItReader(BaseReader):
    enabled = bool(MarkdownIt)
    file_extensions = ["md"]
    
    def read(self, source_path):
        """Parse content and metadata of markdown files"""

        self._source_path = source_path
        # self._md = Markdown(**self.settings["MARKDOWN"])
        self._md = MarkdownIt()
        with pelican_open(source_path) as text:
            metadata, content  = self._parse(text)

        if metadata:
            metadata = self._parse_metadata(metadata)
        else:
            metadata = {}
        content = self._md.render(content)
        return content, metadata
    
    def _parse(self, text) -> Tuple[dict, str]:
        """
        return metadata and content.
        """
        meta: dict[str, list] = {}
        text = str(text).strip()
        key = None

        if not MD_MATE_BEGIN_RE.match(text):
            return meta, text
        
        lines = text.split('\n')[1:]
        i = 1
        for line in lines:
            i += 1
            m1 = MD_META_RE.match(line)
            if line.strip() == '' or MD_MATE_END_RE.match(line):
                break  # blank line or end of YAML header - done
            if m1:
                key = m1.group('key').lower().strip()
                value = m1.group('value').strip()
                meta.setdefault(key, []).append(value)
            else:
                m2 = MD_META_MORE_RE.match(line)
                if m2 and key:
                    # Add another line to existing key
                    meta[key].append(m2.group('value').strip())
                else:
                    break  # no meta data - done
        return meta, '\n'.join(lines[i:])
        # try:
        #     rendered = MarkdownIt().render(fin.read())
        # except OSError:
        #     sys.stderr.write(f'Cannot open file "{filename}".\n')
        #     sys.exit(1)
    def _parse_metadata(self, meta):
        """Return the dict containing document metadata"""
        formatted_fields = self.settings["FORMATTED_FIELDS"]

        output = collections.OrderedDict()
        for name, value in meta.items():
            name = name.lower()
            if name in formatted_fields:
                rendered = self._md.render(value).strip()
                output[name] = self.process_metadata(name, rendered)
            elif not DUPLICATES_DEFINITIONS_ALLOWED.get(name, True):
                if len(value) > 1:
                    logging.warning(
                        "Duplicate definition of `%s` for %s. Using first one.",
                        name,
                        self._source_path,
                    )
                output[name] = self.process_metadata(name, value[0])
            elif len(value) > 1:
                # handle list metadata as list of string
                output[name] = self.process_metadata(name, value)
            else:
                # otherwise, handle metadata as single string
                output[name] = self.process_metadata(name, value[0])
        return output

def add_reader(readers):
    for k in MarkdownItReader.file_extensions:
        readers.reader_classes[k] = MarkdownItReader

def register():
    signals.readers_init.connect(add_reader)
