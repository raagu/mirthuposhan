"""Give changed CSS/JS new URLs so cached files cannot break a new page layout."""
from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def build():
    urls = {}
    for extension in ('css', 'js'):
        source = ROOT / 'assets' / f'site.{extension}'
        content = source.read_bytes()
        digest = sha256(content).hexdigest()[:16]
        versioned = source.with_name(f'site.{digest}.{extension}')
        versioned.write_bytes(content)
        urls[extension] = '/assets/' + versioned.name

    for page in ROOT.glob('*.html'):
        html = page.read_text()
        for extension, url in urls.items():
            pattern = (r'((?:href|src)=["\'])/assets/site(?:\.[a-f0-9]{16})?\.'
                       + extension + r'(["\'])')
            html = re.sub(pattern, lambda match: match[1] + url + match[2], html)
        page.write_text(html)


if __name__ == '__main__':
    build()
