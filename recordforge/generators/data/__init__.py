"""Data generator registry.

Each entry maps the public type key to its build_rows() function.
Keys must match v1 exactly — do not rename.
"""

from recordforge.generators.data.customers import build_rows as build_customers
from recordforge.generators.data.edge_cases import build_rows as build_edge_cases
from recordforge.generators.data.employees import build_rows as build_employees
from recordforge.generators.data.inventory import build_rows as build_inventory
from recordforge.generators.data.messy import build_rows as build_messy
from recordforge.generators.data.transactions import build_rows as build_transactions
from recordforge.generators.data.vendors import build_rows as build_vendors

DATA_REGISTRY: dict[str, callable] = {
    "customers": build_customers,
    "vendors": build_vendors,
    "transactions": build_transactions,
    "employees": build_employees,
    "inventory": build_inventory,
    "messy": build_messy,
    "edge_cases": build_edge_cases,
}
