import os
from pathlib import Path

import duckdb


BASE_DIR = Path(r"C:\Users\rattu\Downloads\Target SQL")
DATA_DIR = BASE_DIR / "Target- SQL Business Case ALL 8 CSV"
OUTPUT_DIR = BASE_DIR / "outputs"


def init_db() -> duckdb.DuckDBPyConnection:
    """
    Initialise an in-memory DuckDB database and register all CSVs as views
    that match the table names used in Target_SQL_Queries.sql.
    """
    con = duckdb.connect(database=":memory:")

    # Ensure paths exist
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    # Map logical table names → CSV file names
    csv_map = {
        "customers": "customers.csv",
        "sellers": "sellers.csv",
        "order_items": "order_items.csv",
        "geolocation": "geolocation.csv",
        "payments": "payments.csv",
        # The SQL uses table name `reviews`, CSV is `order_reviews.csv`
        "reviews": "order_reviews.csv",
        "orders": "orders.csv",
        "products": "products.csv",
    }

    for table, filename in csv_map.items():
        csv_path = DATA_DIR / filename
        if not csv_path.exists():
            raise FileNotFoundError(f"Expected CSV not found: {csv_path}")

        # Some files (e.g. order_reviews.csv) are not UTF-8 encoded and can trigger
        # unicode errors. For robustness, allow DuckDB to skip problematic rows
        # using ignore_errors=true.
        if table == "reviews":
            read_opts = ", header=True, ignore_errors=true"
        else:
            read_opts = ", header=True"

        # Create a view so we can query with simple table names
        con.execute(
            f"""
            CREATE OR REPLACE VIEW {table} AS
            SELECT * FROM read_csv_auto('{csv_path.as_posix()}'{read_opts});
            """
        )

    return con


def run_and_save(con: duckdb.DuckDBPyConnection, name: str, sql: str) -> None:
    """
    Run a query and save the full result to a CSV in OUTPUT_DIR.
    Also save the first 10 rows as a preview CSV.
    """
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    result = con.execute(sql).fetch_df()

    safe_name = name.replace(" ", "_").replace(".", "_")
    full_path = OUTPUT_DIR / f"{safe_name}.csv"
    preview_path = OUTPUT_DIR / f"{safe_name}_preview10.csv"

    result.to_csv(full_path, index=False)
    # Save first 10 rows as preview
    result.head(10).to_csv(preview_path, index=False)

    print(f"[OK] {name} -> {full_path.name} (rows={len(result)})")


def main() -> None:
    con = init_db()

    # SECTION 1
    queries = [
        (
            "1_2_orders_time_range",
            """
            SELECT
                MIN(order_purchase_timestamp) AS first_order_date,
                MAX(order_purchase_timestamp) AS last_order_date,
                date_diff('day',
                          MIN(order_purchase_timestamp),
                          MAX(order_purchase_timestamp)) AS total_days
            FROM orders;
            """,
        ),
        (
            "1_3_customer_cities_states",
            """
            SELECT
                COUNT(DISTINCT c.customer_city) AS total_cities,
                COUNT(DISTINCT c.customer_state) AS total_states
            FROM customers c
            INNER JOIN orders o ON c.customer_id = o.customer_id;
            """,
        ),
        # SECTION 2
        (
            "2_1_orders_trend_by_year",
            """
            WITH yearly AS (
                SELECT
                    EXTRACT(year FROM order_purchase_timestamp) AS order_year,
                    COUNT(*) AS total_orders
                FROM orders
                GROUP BY order_year
            )
            SELECT
                order_year,
                total_orders,
                LAG(total_orders) OVER (ORDER BY order_year) AS previous_year_orders,
                CASE
                    WHEN LAG(total_orders) OVER (ORDER BY order_year) IS NULL THEN NULL
                    ELSE (total_orders - LAG(total_orders) OVER (ORDER BY order_year))
                         * 100.0 / LAG(total_orders) OVER (ORDER BY order_year)
                END AS year_over_year_growth_pct
            FROM yearly
            ORDER BY order_year;
            """,
        ),
        (
            "2_2_monthly_seasonality",
            """
            SELECT
                EXTRACT(year  FROM order_purchase_timestamp) AS order_year,
                EXTRACT(month FROM order_purchase_timestamp) AS order_month,
                COUNT(*) AS total_orders
            FROM orders
            GROUP BY order_year, order_month
            ORDER BY order_year, order_month;
            """,
        ),
        (
            "2_3_time_of_day_distribution",
            """
            WITH classified AS (
                SELECT
                    CASE
                        WHEN EXTRACT(hour FROM order_purchase_timestamp) BETWEEN 0 AND 6  THEN 'Dawn'
                        WHEN EXTRACT(hour FROM order_purchase_timestamp) BETWEEN 7 AND 12 THEN 'Morning'
                        WHEN EXTRACT(hour FROM order_purchase_timestamp) BETWEEN 13 AND 18 THEN 'Afternoon'
                        WHEN EXTRACT(hour FROM order_purchase_timestamp) BETWEEN 19 AND 23 THEN 'Night'
                    END AS time_of_day
                FROM orders
            )
            SELECT
                time_of_day,
                COUNT(*) AS order_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
            FROM classified
            GROUP BY time_of_day
            ORDER BY order_count DESC;
            """,
        ),
        # SECTION 3
        (
            "3_1_month_on_month_orders_by_state",
            """
            SELECT
                c.customer_state,
                EXTRACT(year  FROM o.order_purchase_timestamp) AS order_year,
                EXTRACT(month FROM o.order_purchase_timestamp) AS order_month,
                COUNT(*) AS total_orders
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            GROUP BY c.customer_state, order_year, order_month
            ORDER BY c.customer_state, order_year, order_month;
            """,
        ),
        (
            "3_2_customer_distribution_by_state",
            """
            WITH counts AS (
                SELECT
                    customer_state,
                    COUNT(DISTINCT customer_id) AS total_customers
                FROM customers
                GROUP BY customer_state
            )
            SELECT
                customer_state,
                total_customers,
                ROUND(total_customers * 100.0 / SUM(total_customers) OVER (), 2) AS percentage
            FROM counts
            ORDER BY total_customers DESC;
            """,
        ),
        # SECTION 4
        (
            "4_1_cost_increase_2017_to_2018",
            """
            WITH OrderCosts AS (
                SELECT
                    EXTRACT(year FROM o.order_purchase_timestamp) AS order_year,
                    SUM(p.payment_value) AS total_cost
                FROM orders o
                INNER JOIN payments p ON o.order_id = p.order_id
                WHERE EXTRACT(year FROM o.order_purchase_timestamp) IN (2017, 2018)
                  AND EXTRACT(month FROM o.order_purchase_timestamp) BETWEEN 1 AND 8
                GROUP BY order_year
            )
            SELECT
                (SELECT total_cost FROM OrderCosts WHERE order_year = 2018) AS cost_2018,
                (SELECT total_cost FROM OrderCosts WHERE order_year = 2017) AS cost_2017,
                ROUND(
                    (
                        (SELECT total_cost FROM OrderCosts WHERE order_year = 2018) -
                        (SELECT total_cost FROM OrderCosts WHERE order_year = 2017)
                    ) * 100.0 /
                    (SELECT total_cost FROM OrderCosts WHERE order_year = 2017),
                    2
                ) AS percentage_increase;
            """,
        ),
        (
            "4_2_total_avg_order_price_by_state",
            """
            SELECT
                c.customer_state,
                SUM(oi.price) AS total_order_price,
                AVG(oi.price) AS avg_order_price
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            INNER JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_state
            ORDER BY total_order_price DESC;
            """,
        ),
        (
            "4_3_total_avg_freight_by_state",
            """
            SELECT
                c.customer_state,
                SUM(oi.freight_value) AS total_freight_value,
                AVG(oi.freight_value) AS avg_freight_value
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            INNER JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_state
            ORDER BY total_freight_value DESC;
            """,
        ),
        # SECTION 5
        (
            "5_1_delivery_time_and_estimated_diff",
            """
            SELECT
                o.order_id,
                o.order_purchase_timestamp,
                o.order_delivered_customer_date,
                o.order_estimated_delivery_date,
                date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS time_to_deliver,
                date_diff('day', o.order_delivered_customer_date, o.order_estimated_delivery_date) AS diff_estimated_delivery
            FROM orders o
            WHERE o.order_delivered_customer_date IS NOT NULL
              AND o.order_estimated_delivery_date IS NOT NULL;
            """,
        ),
        (
            "5_2_top5_states_highest_avg_freight",
            """
            SELECT
                customer_state,
                AVG(freight_value) AS avg_freight_value
            FROM (
                SELECT
                    c.customer_state,
                    oi.freight_value
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                INNER JOIN order_items oi ON o.order_id = oi.order_id
            )
            GROUP BY customer_state
            ORDER BY avg_freight_value DESC
            LIMIT 5;
            """,
        ),
        (
            "5_2_top5_states_lowest_avg_freight",
            """
            SELECT
                customer_state,
                AVG(freight_value) AS avg_freight_value
            FROM (
                SELECT
                    c.customer_state,
                    oi.freight_value
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                INNER JOIN order_items oi ON o.order_id = oi.order_id
            )
            GROUP BY customer_state
            ORDER BY avg_freight_value ASC
            LIMIT 5;
            """,
        ),
        (
            "5_3_top5_states_highest_avg_delivery_time",
            """
            SELECT
                customer_state,
                AVG(delivery_days) AS avg_delivery_time
            FROM (
                SELECT
                    c.customer_state,
                    date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_delivered_customer_date IS NOT NULL
            )
            GROUP BY customer_state
            ORDER BY avg_delivery_time DESC
            LIMIT 5;
            """,
        ),
        (
            "5_3_top5_states_lowest_avg_delivery_time",
            """
            SELECT
                customer_state,
                AVG(delivery_days) AS avg_delivery_time
            FROM (
                SELECT
                    c.customer_state,
                    date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_delivered_customer_date IS NOT NULL
            )
            GROUP BY customer_state
            ORDER BY avg_delivery_time ASC
            LIMIT 5;
            """,
        ),
        (
            "5_4_top5_states_fast_vs_estimated",
            """
            SELECT
                customer_state,
                AVG(days_faster) AS avg_days_faster_than_estimated
            FROM (
                SELECT
                    c.customer_state,
                    date_diff('day', o.order_delivered_customer_date, o.order_estimated_delivery_date) AS days_faster
                FROM orders o
                INNER JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_delivered_customer_date IS NOT NULL
                  AND o.order_estimated_delivery_date IS NOT NULL
            )
            GROUP BY customer_state
            HAVING AVG(days_faster) > 0
            ORDER BY avg_days_faster_than_estimated DESC
            LIMIT 5;
            """,
        ),
        # SECTION 6
        (
            "6_1_monthly_orders_by_payment_type",
            """
            SELECT
                EXTRACT(year  FROM o.order_purchase_timestamp) AS order_year,
                EXTRACT(month FROM o.order_purchase_timestamp) AS order_month,
                p.payment_type,
                COUNT(DISTINCT o.order_id) AS order_count
            FROM orders o
            INNER JOIN payments p ON o.order_id = p.order_id
            GROUP BY order_year, order_month, p.payment_type
            ORDER BY order_year, order_month, p.payment_type;
            """,
        ),
        (
            "6_2_orders_by_installments",
            """
            SELECT
                payment_installments,
                COUNT(DISTINCT order_id) AS order_count
            FROM payments
            GROUP BY payment_installments
            ORDER BY payment_installments;
            """,
        ),
        # ADDITIONAL INSIGHTS
        (
            "A1_top10_products_by_volume",
            """
            SELECT
                p."product category" AS product_category_name,
                COUNT(oi.order_item_id) AS total_items_sold,
                SUM(oi.price) AS total_revenue
            FROM order_items oi
            INNER JOIN products p ON oi.product_id = p.product_id
            WHERE p."product category" IS NOT NULL
            GROUP BY p."product category"
            ORDER BY total_items_sold DESC
            LIMIT 10;
            """,
        ),
        (
            "A2_customer_retention",
            """
            WITH customer_orders AS (
                SELECT
                    customer_id,
                    COUNT(*) AS order_count
                FROM orders
                GROUP BY customer_id
            )
            SELECT
                COUNT(DISTINCT customer_id) AS total_customers,
                COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) AS repeat_customers,
                ROUND(
                    COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) * 100.0 /
                    COUNT(DISTINCT customer_id),
                    2
                ) AS retention_rate
            FROM customer_orders;
            """,
        ),
        (
            "A3_avg_order_value_by_state",
            """
            SELECT
                c.customer_state,
                COUNT(DISTINCT o.order_id) AS total_orders,
                SUM(p.payment_value) AS total_revenue,
                AVG(p.payment_value) AS avg_order_value
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            INNER JOIN payments p ON o.order_id = p.order_id
            GROUP BY c.customer_state
            ORDER BY avg_order_value DESC;
            """,
        ),
        (
            "A4_order_status_distribution",
            """
            WITH counts AS (
                SELECT
                    order_status,
                    COUNT(*) AS order_count
                FROM orders
                GROUP BY order_status
            )
            SELECT
                order_status,
                order_count,
                ROUND(order_count * 100.0 / SUM(order_count) OVER (), 2) AS percentage
            FROM counts
            ORDER BY order_count DESC;
            """,
        ),
        (
            "A5_review_score_distribution",
            """
            WITH counts AS (
                SELECT
                    review_score,
                    COUNT(*) AS review_count
                FROM reviews
                WHERE review_score IS NOT NULL
                GROUP BY review_score
            )
            SELECT
                review_score,
                review_count,
                ROUND(review_count * 100.0 / SUM(review_count) OVER (), 2) AS percentage
            FROM counts
            ORDER BY review_score DESC;
            """,
        ),
    ]

    for name, sql in queries:
        run_and_save(con, name, sql)


if __name__ == "__main__":
    main()


