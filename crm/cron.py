from datetime import datetime
from pathlib import Path

def log_crm_heartbeat():
    """Log heartbeat message every 5 minutes."""
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_path = Path("/tmp/crm_heartbeat_log.txt")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} CRM is alive\n")
