#!/usr/bin/env python3
"""
Query pending orders from the last 7 days and log reminders.
- Uses gql against http://localhost:8000/graphql
- Logs to /tmp/order_reminders_log.txt
- Prints the required completion message.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def main():
    # GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Calculate "since" date in ISO format (UTC)
    since_date = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()

    # GraphQL query (adjust field names to match your schema if needed)
    query = gql(
        """
        query OrdersSince($since: Date!) {
          orders(orderDate_Gte: $since, status: "PENDING") {
            id
            customer {
              email
            }
          }
        }
        """
    )

    result = client.execute(query, variable_values={"since": since_date})
    orders = result.get("orders", [])

    # Log file (spec requires this exact path)
    log_path = Path("/tmp/order_reminders_log.txt")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    with log_path.open("a", encoding="utf-8") as f:
        for o in orders:
            order_id = o.get("id")
            customer_email = (o.get("customer") or {}).get("email")
            f.write(f"{timestamp} - Order {order_id} for {customer_email}\n")

    # Required console output
    print("Order reminders processed!")


if __name__ == "__main__":
    main()
