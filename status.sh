echo "WARC files:       $(ls ./warcs | wc -l)"
echo "Download scripts: $(ls ./dl | wc -l)"

echo
echo "Storage"
df -h /

echo
echo "Memory"
free -h 

echo
echo "Log"
tail -n 1 run-dl.log
tail -n 1 warc-to-es-bulk.log 