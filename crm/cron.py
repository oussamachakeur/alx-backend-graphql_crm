"""
Django cron job to log heartbeat status.
"""
from datetime import datetime

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(f"{timestamp} CRM is alive\n")


def update_low_stock():
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport
    from datetime import datetime

    client = Client(
        transport=RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True, retries=3),
        fetch_schema_from_transport=True
    )

    mutation = gql("""
    mutation {
        updateLowStock {
            updated {
                name
                stock
            }
            success
        }
    }
    """)

    result = client.execute(mutation)
    with open("/tmp/low_stock_updates_log.txt", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for product in result["updateLowStock"]["updated"]:
            f.write(f"{timestamp} - {product['name']} restocked to {product['stock']}\n")
