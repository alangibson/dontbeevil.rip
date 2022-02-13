import sys, re, json, os
from xml.etree.ElementTree import dump
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
import lxml
from lxml.html.clean import Cleaner


# https://www.kdnuggets.com/2018/03/text-data-preprocessing-walkthrough-python.html
def denoise_html(html):

    def strip_html_elements(html):
        # Remove various tags completely
        cleaner = Cleaner()
        cleaner.javascript = True
        cleaner.scripts = True
        cleaner.style = True
        cleaner.inline_style = True
        cleaner.kill_tags = ['script']
        return lxml.html.tostring(cleaner.clean_html(lxml.html.fromstring(html)))

    def strip_html_tags(html):
         # Extract just the text
        return BeautifulSoup(html, "html.parser").get_text()

    def remove_between_square_brackets(html):
        return re.sub('\[[^]]*\]', '', html)

    def dedupe_whitespace(text):
        # Remove redundant newlines
        return re.sub(r'(\r?\n)+', r'\n', text)

    html = strip_html_elements(html)
    text = strip_html_tags(html)
    text = remove_between_square_brackets(text)
    text = dedupe_whitespace(text)
    return text


# Returns list of objects suitable for converting to JSON
def convert_warc_to_document(filename):
    with open(filename, 'rb') as stream:
        for record in ArchiveIterator(stream):
            # Only consider responses
            if record.rec_type != 'response':
                continue

            # Extract all interesting properties
            url = record.rec_headers.get_header('WARC-Target-URI')
            media_type = record.rec_headers.get_header('WARC-Identified-Payload-Type')
            retrieved_at = record.rec_headers.get_header('WARC-Date')
            updated_at = record.http_headers.get_header('Last-Modified')
            language = record.http_headers.get_header('Content-Language')
            raw_body = record.content_stream().read()
            # TODO extract these fields
            # HTML elements
            #   title = html.head.title

            print(retrieved_at, media_type, url)

            # Preprocess HTML
            # TODO raw_body for indexing based on media_type
            text = denoise_html(raw_body)
            
            # Yield a change object
            yield [
                { 'index': { '_id': url } },
                { 
                    'url': url,
                    'language': language,
                    'text': text
                }
            ]


def dump_chunk(chunk, file_num):
    filename = '%s/%s.ndjson' % (ndjsondir, file_num)
    print('Dumping', filename)
    with open(filename, 'w') as f:
        for c in chunk:
            for l in c:
                f.write(json.dumps(l) + '\n')
    return filename


def finish_chunk(chunk, file_num):
    # Write changes in chunk out to ndjson file
    dump_chunk(chunk, file_num)


if __name__ == '__main__':
    warcdir = sys.argv[1]
    ndjsondir = sys.argv[2]
    chunk_size = int(sys.argv[3])
    delete_warcs = bool(sys.argv[4])

    # Make sure output directory exists
    os.mkdir(ndjsondir)

    current_file_num = 1
    chunk = []
    for warcfile in ['%s/%s' % (warcdir, w,) for w in os.listdir(warcdir)]:
        try:
            for change in convert_warc_to_document(warcfile):
                if len(chunk) == chunk_size:
                    finish_chunk(chunk, current_file_num)
                    chunk = []
                    current_file_num = current_file_num + 1
                else:
                    chunk.append(change)
            if delete_warcs:
                os.remove(warcfile)
        except Exception as e:
            print('Error', e, warcfile)
    # Write out whatever is left over
    finish_chunk(chunk, current_file_num)
