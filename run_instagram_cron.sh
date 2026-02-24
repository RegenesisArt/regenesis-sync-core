#!/bin/bash
cd /home/contact_regenesis_art/regenesis-sync-core
echo "$(date): Starting Instagram fetch" >> /home/contact_regenesis_art/instagram_cron.log
/usr/bin/python3 instagram_automation.py >> /home/contact_regenesis_art/instagram_cron.log 2>&1
echo "$(date): Instagram fetch complete" >> /home/contact_regenesis_art/instagram_cron_timestamp.log
