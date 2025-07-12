from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    client = Client(
        transport=RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True, retries=3),
        fetch_schema_from_transport=True
    )

    query = gql("""
    query {
        customersCount
        ordersCount
        totalRevenue
    }
    """)

    result = client.execute(query)
    log = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
        f"Report: {result['customersCount']} customers, "
        f"{result['ordersCount']} orders, "
        f"{result['totalRevenue']} revenue\n"
    )

    with open("/tmp/crm_report_log.txt", "a") as f:
        f.write(log)

