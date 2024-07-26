# DW Latest Videos

Contact: olav.schettler@dw.com

Deployed: https://dwapps.de/feeds/

## Updates

With cron:

````
*/15 * * * * cd /var/www/pdp.zone/public/feed && python3 ./publish_videos.py >> /dev/null 2>&1
````


