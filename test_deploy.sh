#!/bin/bash
echo "Testing dashboard deployment..."
cd ~/regenesis-sync-core

# Check if main.py has dashboard routes
if ! grep -q "@app.route('/dashboard')" main.py; then
    echo "ERROR: Dashboard routes not found in main.py"
    exit 1
fi

if ! grep -q "@app.route('/api/dashboard')" main.py; then
    echo "ERROR: API routes not found in main.py"
    exit 1
fi

# Check if template exists
if [ ! -f "templates/dashboard.html" ]; then
    echo "ERROR: templates/dashboard.html not found"
    exit 1
fi

echo "✅ All checks passed"
echo "Ready to deploy with: gcloud functions deploy regenesis-hub-v1 ..."
