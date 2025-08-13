#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

deleted_count=$(python manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from django.db.models import Exists, OuterRef
from crm.models import Customer, Order  # adjust import if needed

cutoff = timezone.now() - timedelta(days=365)
recent_orders = Order.objects.filter(customer_id=OuterRef('pk'), created_at__gte=cutoff)
qs = Customer.objects.annotate(has_recent=Exists(recent_orders)).filter(has_recent=False)

deleted, _ = qs.delete()
print(deleted)
")

echo \"$TIMESTAMP - Deleted count: $deleted_count\" >> /tmp/customer_cleanup_log.txt
