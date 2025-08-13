$cronpy = @"
from datetime import datetime
from pathlib import Path

from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client


def log_crm_heartbeat():
    \"\"\"Log heartbeat and (optionally) ping GraphQL hello.\"\"\"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Try a lightweight GraphQL query to verify the endpoint is responsive.
    status_note = ""
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=1,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        # Adjust "hello" field name if your schema uses a different one.
        result = client.execute(gql("query { hello }"))
        status_note = f" (hello={result.get('hello')})"
    except Exception:
        # Keep logging even if the endpoint is down or schema differs.
        status_note = " (hello=unavailable)"

    log_path = Path("/tmp/crm_heartbeat_log.txt")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} CRM is alive{status_note}\n")
"@
[System.IO.File]::WriteAllText("crm/cron.py", $cronpy, [Text.UTF8Encoding]::new($false))
