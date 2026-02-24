#!/bin/bash
cd /home/contact_regenesis_art/regenesis-sync-core
echo "$(date): Starting email ingestion" >> /home/contact_regenesis_art/email_cron.log
/usr/bin/python3 gmail_ingest.py >> /home/contact_regenesis_art/email_cron.log 2>&1
echo "$(date): Running payment detection" >> /home/contact_regenesis_art/email_cron.log
/usr/bin/python3 payment_detector.py >> /home/contact_regenesis_art/email_cron.log 2>&1
echo "$(date): Email cycle complete" >> /home/contact_regenesis_art/email_cron_timestamp.log
