# DW Latest Videos

Contact: olav.schettler@dw.com

Deployed: https://dwapps.de/feed/

This script reads published videos in English, Spanish, and German from WebAPI and dumps then to JSON files. Videos with length >5min are skipped.

The following JSON files are created:

* videos_all_america.json
* videos_de.json
* videos_de_america.json
* videos_en.json
* videos_en_america.json
* videos_es.json
* videos_es_america.json

## Installation

````
python3 -mvenv env
source env/bin/activate
pip install -r requirements.txt
````

## Updates

With cron:

````
*/15 * * * * cd /var/www/pdp.zone/public/feed && python3 ./publish_videos.py >> /dev/null 2>&1
````


