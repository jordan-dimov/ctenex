from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

import httpx
import typer

from ctenex.exchange_client.db.connection import get_db_connection


# TODO: Move to settings
def get_api_url() -> str:
    """Get the API URL from environment or default to localhost."""
    return "http://0.0.0.0:8000"  # Default to localhost, can be overridden


app = typer.Typer()


@app.command()
def place_order(
    contract_id: str = typer.Argument(..., help="Contract identifier"),
    side: str = typer.Argument(..., help="Order side (BUY/SELL)"),
    type: str = typer.Argument(..., help="Order type (LIMIT/MARKET)"),
    quantity: float = typer.Argument(..., help="Order quantity"),
    price: float = typer.Argument(..., help="Order price (2 decimal places precision)"),
):
    """Place a new order through the exchange API."""
    base_url = get_api_url()

    # Convert float price to Decimal with 2 decimal places precision
    price_decimal = Decimal(str(price)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    quantity_decimal = Decimal(str(quantity)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    print(f"Contract ID: {contract_id}")
    print(f"Side: {side}")
    print(f"Quantity: {quantity_decimal}")
    print(f"Price: {price_decimal}")

    # Prepare order data
    order_data = {
        "contract_id": contract_id,
        "trader_id": "1e1590fd-f479-4bd4-ad03-56f2e265ec33",  # TODO: Load from local DB
        "side": side,
        "type": type,
        "quantity": str(quantity_decimal),
        "price": str(price_decimal),  # Convert Decimal to string for JSON serialization
    }

    try:
        with httpx.Client() as client:
            response = client.post(f"{base_url}/v1/stateless/orders", json=order_data)
            response.raise_for_status()
            order_response = response.json()

            # Store in DuckDB
            with get_db_connection() as conn:
                conn.execute(
                    """
                        INSERT INTO orders (id, contract_id, side, quantity, price, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        order_response["id"],
                        order_response["contract_id"],
                        order_response["side"],
                        str(quantity_decimal),
                        str(price_decimal),
                        order_response["status"],
                        datetime.now(),
                    ),
                )

            typer.echo(f"Order placed successfully! Order ID: {order_response['id']}")

    except httpx.HTTPError as e:
        typer.echo(f"Error placing order: {str(e)}", err=True)
        raise typer.Exit(1)


@app.command()
def list_orders(
    contract_id: Optional[str] = typer.Option(None, help="Filter by contract ID"),
):
    """List all stored orders, optionally filtered by contract ID."""
    query = "SELECT * FROM orders"
    params = []

    if contract_id:
        query += " WHERE contract_id = ?"
        params.append(contract_id)

    query += " ORDER BY created_at DESC"

    with get_db_connection() as conn:
        results = conn.execute(query, params).fetchall()

    if not results:
        typer.echo("No orders found.")
        return

    # Print results in a table format
    typer.echo("\nStored Orders:")
    typer.echo("-" * 120)
    typer.echo(
        f"{'ID':<40} {'Contract':<15} {'Side':<6} {'Quantity':<10} {'Price':<8} {'Status':<8} {'Created At'}"
    )
    typer.echo("-" * 120)

    for row in results:
        typer.echo(
            f"{row[0]:<40} {row[1]:<15} {row[2]:<6} {row[3]:<10} {row[4]:<8} {row[5]:<8} {row[6]}"
        )


if __name__ == "__main__":
    app()
