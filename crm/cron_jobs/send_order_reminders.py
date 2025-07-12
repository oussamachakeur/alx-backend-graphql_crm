#!/usr/bin/env python3
"""
Fetch orders from the last 7 days and log email reminders.
"""
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

log_file = "/tmp/order_reminders_log.txt"

def send_reminders():
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
        recentOrders: orders(orderDate_Gte: "%s") {
            id
            customer {
                email
            }
        }
    }
    """ % (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))

    result = client.execute(query)

    with open(log_file, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for order in result.get("recentOrders", []):
            f.write(f"{timestamp} - Order {order['id']} reminder sent to {order['customer']['email']}\n")

    print("Order reminders processed!")

if __name__ == "__main__":
    send_reminders()
