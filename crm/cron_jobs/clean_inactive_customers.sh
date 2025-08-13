#!/bin/bash

set -euo pipefail

# Resolve repo root assuming this script lives in crm/cron_jobs/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

source .venv/bin/activate

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Run a tiny Django snippet to delete customers with no orders in the last year
DELETED_COUNT=$(python3 manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from django.db.models import Exists, OuterRef, Q
from crm.models import Customer, Order  # adjust if your Order model path differs

cutoff = timezone.now() - timedelta(days=365)

# A customer is 'inactive' if they have no orders in the last year.
recent_orders = Order.objects.filter(customer_id=OuterRef('pk'), created_at__gte=cutoff)
qs = Customer.objects.annotate(has_recent=Exists(recent_orders)).filter(has_recent=False)

deleted, _ = qs.delete()
print(deleted)
")

echo \"$TIMESTAMP - Deleted $DELETED_COUNT customers\" >> /tmp/customer_cleanup_log.txt
