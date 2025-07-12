#!/bin/bash
# Deletes customers with no orders in the past year and logs the result.

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
cd /path/to/your/project || exit
source venv/bin/activate

DELETED=$(echo "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=365)
deleted = Customer.objects.filter(order__isnull=True, created_at__lt=cutoff).delete()
print(deleted[0])
" | python3 manage.py shell)

echo "$TIMESTAMP - Deleted $DELETED inactive customers" >> /tmp/customer_cleanup_log.txt
