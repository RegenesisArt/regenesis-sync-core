#!/bin/bash
cd /home/contact_regenesis_art/regenesis-sync-core
export EBAY_APP_ID="DanielFe-Regenesi-PRD-24eaa38ed-2c2bab79"
echo "$(date): Starting eBay market research" >> /home/contact_regenesis_art/ebay_cron.log
/usr/bin/python3 ebay_tracker_delayed.py >> /home/contact_regenesis_art/ebay_cron.log 2>&1
echo "$(date): eBay market research complete" >> /home/contact_regenesis_art/ebay_cron_timestamp.log
