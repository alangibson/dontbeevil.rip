import sys, re, json, os, gzip, csv
from xml.etree.ElementTree import dump
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
import lxml
from lxml.html.clean import Cleaner

#
# Turn WARCs and dumped BigQuery tables into ES bulk import JSON
#


# Increase csv field size limit to the maximum possible on this system
# https://til.simonwillison.net/python/csv-error-column-too-large
field_size_limit = sys.maxsize
while True:
    try:
        csv.field_size_limit(field_size_limit)
        break
    except OverflowError:
        field_size_limit = int(field_size_limit / 10)


# https://www.kdnuggets.com/2018/03/text-data-preprocessing-walkthrough-python.html
def extract_text_from_html(html):

    def strip_html_elements(text):
        # Remove various tags completely
        cleaner = Cleaner()
        cleaner.javascript = True
        cleaner.scripts = True
        cleaner.style = True
        cleaner.inline_style = True
        cleaner.kill_tags = ['script']
        return lxml.html.tostring(cleaner.clean_html(lxml.html.fromstring(text)))

    # Extract text and title from html
    def extract_text(html):
        bs = BeautifulSoup(html, "html.parser")
        return ( bs.get_text(), bs.title.string if bs.title else None )

    def remove_between_square_brackets(html):
        return re.sub('\[[^]]*\]', '', html)

    def dedupe_whitespace(text):
        # Remove redundant newlines
        return re.sub(r'(\r?\n)+', r'\n', text)

    try:
        html = strip_html_elements(html)
        text, title = extract_text(html)
        text = remove_between_square_brackets(text)
        text = dedupe_whitespace(text)
        return text, title
    except: 
        return None, None

def bulk_change_document(url, text, score=None, title=None, language='en'):
    return [
        { 'index': { '_id': url } },
        { 
            'url': url,
            'title': title,
            'language': language,
            'text': text,
            'score': score
        }
    ]

# Returns list of objects suitable for converting to JSON
def yield_documents_from_warc(filename):
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
            # TODO pull in score from initial data set
            score = None

            # Preprocess HTML
            text, text_title = extract_text_from_html(raw_body)
            # Don't overwrite title unless we have to
            title = title if title else text_title
            
            # Yield a change object
            yield bulk_change_document(
                url=url,
                title=title,
                text=text,
                score=score,
                language=language,
            )


# Returns list of objects suitable for converting to JSON
def yield_documents_from_csv(filename):
    with gzip.open(filename, mode='rt') as f:
        for row in csv.DictReader(f):

            # FIXME filter out NUL bytes
            # https://stackoverflow.com/questions/7894856/line-contains-null-byte-in-csv-reader-python
            # Error line contains NUL ./bq/combined_posts-000000000014.csv.gz

            url = row['post_url']
            title = row['post_title']
            score = int(row['post_score']) if row['post_score'] else None
            raw_body = row['post_body']
            # TODO guess language
            language = 'en'

            # Preprocess HTML
            text, text_title = extract_text_from_html(raw_body)
            # Don't overwrite title unless we have to
            title = title if title else text_title

            # Yield a change object
            yield bulk_change_document(
                url=url,
                title=title,
                text=text,
                score=score,
                language=language
            )


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


def main(srcdir, ndjsondir, yielder, chunk_size=1000, delete_src_files=False):
    # Make sure output directory exists
    # TODO idempotent
    os.mkdir(ndjsondir)

    current_file_num = 1
    chunk = []
    for srcfile in ['%s/%s' % (srcdir, w,) for w in os.listdir(srcdir)]:
        try:
            for change in yielder(srcfile):
                if len(chunk) == chunk_size:
                    finish_chunk(chunk, current_file_num)
                    chunk = []
                    current_file_num += 1
                else:
                    chunk.append(change)
            if delete_src_files:
                os.remove(srcfile)
        except Exception as e:
            print('Error', e, srcfile)
    # Write out whatever is left over
    finish_chunk(chunk, current_file_num)


if __name__ == '__main__':
    type = sys.argv[1]
    srcdir = sys.argv[2]
    ndjsondir = sys.argv[3]
    chunk_size = int(sys.argv[4])
    # delete_source_files = bool(sys.argv[5]) if len(sys.argv) == 6 else False
    delete_source_files = False

    if type == 'warc':
        main(srcdir, ndjsondir, yield_documents_from_warc, chunk_size, delete_source_files)
    elif type == 'csv.gz':
        main(srcdir, ndjsondir, yield_documents_from_csv, chunk_size, delete_source_files)

    print('Finished converting archive to ElasticSearch bulk import')