import csv, os, stat, sys
from slugify import slugify

input = sys.argv[1]
warcdir = sys.argv[2]
scriptdir = sys.argv[3]

print('Processing %s into %s' % (input, warcdir))

# Make sure out dir exists
os.mkdir(warcdir)
os.mkdir(scriptdir)

with open(input, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    processed_urls = set()
    for row in reader:
        url = row['url']

        # Dedupe
        if url in processed_urls:
            continue
        else:
            processed_urls.add(url)

        print('%s\t%s\t%s' % (row['fetch_time'], row['score'], url,))

        # Build download script
        # "platform","site","url","score","fetch_time","fetch_status","warc_filename","warc_segment","warc_record_offset","warc_record_length"
        bucket = 'commoncrawl'
        warc_filename = row['warc_filename']
        start_byte = int(row['warc_record_offset'])
        offset = int(row['warc_record_length'])
        end_byte = start_byte + (offset - 1)
        outfile_gz = '%s-%s-%s.gz' % (slugify(warc_filename), start_byte, offset)
        script = """aws s3api get-object --range 'bytes=%s-%s' --bucket '%s' --key '%s' '%s/%s'""" % \
            (start_byte, end_byte, bucket, warc_filename, warcdir, outfile_gz)

        # Write out download script file
        # aws s3api get-object --range 'bytes=30680420-30681660' --bucket 'commoncrawl' --key 'crawl-data/CC-MAIN-2022-05/segments/1642320301217.83/warc/CC-MAIN-20220119003144-20220119033144-00465.warc.gz' out.gz
        scriptfile = '%s/%s.sh' % (scriptdir, outfile_gz)
        with open(scriptfile, 'w') as sf:
            sf.write(script)
            os.chmod(scriptfile, stat.S_IRUSR | stat.S_IXUSR)
