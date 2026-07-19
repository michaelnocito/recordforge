"""Random data helpers and expanded word lists.

All rand_* functions accept an rng parameter — never use module-level
random globals.
"""

import random
import secrets
import string
from datetime import date, timedelta
from decimal import Decimal
from typing import Literal

from recordforge.core.models import LineItem, Party

# --- Word lists (40+ entries each) ---

FIRST_WORDS: list[str] = [
    "Apex", "Horizon", "Meridian", "Nexus", "Pinnacle", "Summit", "Catalyst",
    "Elevate", "Vantage", "Clarity", "Arcadia", "Bridgepoint", "Crestline",
    "Delphi", "Embark", "Frontier", "Granite", "Harbor", "Ironstone", "Juniper",
    "Keystone", "Lakeview", "Monarch", "Navigate", "Oakridge", "Paragon",
    "Quantum", "Ridgeline", "Silverstone", "Trident", "Uplift", "Vertex",
    "Waypoint", "Xcalibur", "Yellowstone", "Zenith", "Alliant", "Bridgespan",
    "Clearpath", "Datapoint",
]

INDUSTRY_WORDS: list[str] = [
    "Clinical", "Health", "Analytics", "Solutions", "Systems", "Informatics",
    "Care", "Data", "Consulting", "Technologies", "Advisors", "Capital",
    "Dynamics", "Enterprises", "Financial", "Global", "Holdings", "Innovations",
    "Logistics", "Management", "Networks", "Operations", "Partners", "Research",
    "Services", "Strategies", "Supply", "Talent", "Transformation", "Ventures",
    "Workflow", "Intelligence", "Procurement", "Infrastructure", "Compliance",
    "Assurance", "Integration", "Performance", "Excellence", "Digital",
]

CORP_SUFFIXES: list[str] = [
    "LLC", "Inc.", "Group", "Partners", "Associates", "Corp.", "Co.", "Ltd.",
    "Enterprises", "Advisors",
]

STREETS: list[str] = [
    "Oak", "Maple", "Commerce", "Innovation", "Enterprise", "Corporate", "Tech",
    "Riverside", "Lakeside", "Parkview", "Summit", "Hillcrest", "Meadow",
    "Cedar", "Birch", "Elmwood", "Pinecrest", "Willow", "Springfield",
    "Clearwater", "Stonegate", "Ironwood", "Bridgewater", "Foxcroft",
    "Greenfield", "Harborview", "Kingsway", "Lakewood", "Northgate",
    "Orchard", "Primrose", "Quarry", "Ridgeview", "Sunridge", "Timberline",
    "Union", "Valley", "Westgate", "Yorktown",
]

STREET_TYPES: list[str] = [
    "Blvd", "Dr", "Ave", "Way", "Pkwy", "St", "Ct", "Ln", "Pl", "Rd",
]

CITIES: list[tuple[str, str]] = [
    ("Austin", "TX"), ("Nashville", "TN"), ("Atlanta", "GA"), ("Denver", "CO"),
    ("Charlotte", "NC"), ("Phoenix", "AZ"), ("Raleigh", "NC"), ("Tampa", "FL"),
    ("Columbus", "OH"), ("Indianapolis", "IN"), ("Kansas City", "MO"),
    ("Louisville", "KY"), ("Memphis", "TN"), ("Oklahoma City", "OK"),
    ("Portland", "OR"), ("Richmond", "VA"), ("Salt Lake City", "UT"),
    ("San Antonio", "TX"), ("Tucson", "AZ"), ("Tulsa", "OK"),
    ("Birmingham", "AL"), ("Boise", "ID"), ("Cincinnati", "OH"),
    ("Cleveland", "OH"), ("Des Moines", "IA"), ("El Paso", "TX"),
    ("Fort Worth", "TX"), ("Fresno", "CA"), ("Hartford", "CT"),
    ("Honolulu", "HI"), ("Jacksonville", "FL"), ("Las Vegas", "NV"),
    ("Little Rock", "AR"), ("Milwaukee", "WI"), ("Minneapolis", "MN"),
    ("New Orleans", "LA"), ("Omaha", "NE"), ("Pittsburgh", "PA"),
    ("Sacramento", "CA"), ("St. Louis", "MO"),
]

FIRST_NAMES: list[str] = [
    "Mia", "Liam", "Noah", "Emma", "Olivia", "Ava", "Ethan", "Lucas", "James",
    "Sophia", "Aiden", "Isabella", "Mason", "Aria", "Logan", "Ella", "Jackson",
    "Scarlett", "Sebastian", "Grace", "Mateo", "Chloe", "Jack", "Penelope",
    "Owen", "Layla", "Theodore", "Riley", "Asher", "Nora", "Henry", "Zoey",
    "Alexander", "Lily", "Daniel", "Eleanor", "Michael", "Hannah", "Benjamin",
    "Lillian", "Elijah", "Addison", "Samuel", "Aubrey", "David", "Ellie",
    "Joseph", "Stella", "Carter", "Natalie", "Jaylen", "Amara", "Destiny",
    "Marcus", "Priya", "Aiko", "Rafael", "Fatima", "Kenji", "Aaliyah",
]

LAST_NAMES: list[str] = [
    "Carter", "Hayes", "Brooks", "Foster", "Morgan", "Bennett", "Turner",
    "Parker", "Bailey", "Reed", "Coleman", "Jenkins", "Perry", "Powell",
    "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler",
    "Simmons", "Foster", "Gonzalez", "Bryant", "Alexander", "Russell",
    "Griffin", "Diaz", "Myers", "Ford", "Hamilton", "Graham",
    "Sullivan", "Wallace", "Woods", "Cole", "West", "Jordan", "Owens",
    "Reynolds", "Fisher", "Ellis", "Harrison", "Gibson", "Mcdonald",
    "Cruz", "Marshall", "Ortiz", "Gomez", "Murray", "Freeman", "Wells",
    "Webb", "Simpson", "Stevens", "Tucker", "Porter", "Hunter", "Hicks",
]

EMAIL_DOMAINS: list[str] = [
    "acmecorp.io", "bridgepoint.co", "crestlinegroup.net", "dataworks.biz",
    "elevateops.co", "frontiertech.io", "graniteadvisors.com", "harborgroup.net",
    "ironbridge.biz", "junipersystems.co", "keystonellc.io", "lakewoodco.net",
    "monarchtech.biz", "navigatecorp.co", "oakridgeinc.io", "paragonworks.net",
    "quantumgrp.biz", "ridgelineops.co", "silverstoneco.io", "tridentgroup.net",
]

PRODUCTS: list[str] = [
    "Laptop Docking Station", "24-inch Monitor", "Wireless Keyboard",
    "USB-C Hub", "Ergonomic Chair", "Standing Desk", "Webcam HD 1080p",
    "Network Switch 24-Port", "Uninterruptible Power Supply", "Label Printer",
    "Barcode Scanner", "Thermal Printer", "External SSD 1TB", "RAM Module 16GB",
    "Cat6 Ethernet Cable 50ft", "Patch Panel 24-Port", "Rack Mount Cabinet",
    "Surge Protector 8-Outlet", "Cable Management Kit", "KVM Switch 4-Port",
    "Laser Printer Toner Cartridge", "Shredder Cross-Cut", "Projector 3500 Lumens",
    "Whiteboard 4x6ft", "Conference Phone", "Headset Noise-Cancelling",
    "Tablet 10-inch", "Wireless Access Point", "Firewall Appliance",
    "Server RAM 32GB",
]

SERVICES: list[str] = [
    "Implementation Services", "Configuration Support", "Training Session",
    "Project Management", "System Integration", "Data Migration",
    "Security Audit", "Compliance Review", "Custom Development",
    "API Integration", "Workflow Automation", "Technical Documentation",
    "Infrastructure Assessment", "Disaster Recovery Planning",
    "Performance Optimization", "Staff Augmentation", "Onboarding Services",
    "Quality Assurance Review", "Change Management Consulting",
    "Business Process Analysis", "Cloud Architecture Review",
    "Database Optimization", "Network Assessment", "Vendor Management",
    "Contract Negotiation Support", "Executive Briefing", "Roadmap Planning",
    "Stakeholder Workshop", "Post-Go-Live Support", "Annual Maintenance",
]

_EMAIL_PREFIXES = ["info", "contact", "hello", "admin", "support", "billing"]


# --- Helpers ---

def sanitize_filename(s: str) -> str:
    """Preserve v1 sanitize_filename behavior exactly."""
    s = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in str(s).strip())
    return s[:100] or "output"


def rand_company(rng: random.Random) -> str:
    """Generate a random fictional company name."""
    return f"{rng.choice(FIRST_WORDS)} {rng.choice(INDUSTRY_WORDS)} {rng.choice(CORP_SUFFIXES)}"


def rand_person(rng: random.Random) -> str:
    """Generate a random fictional full name."""
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def rand_phone(rng: random.Random) -> str:
    """Generate a random US phone number string."""
    return f"({rng.randint(200, 989)}) {rng.randint(200, 989)}-{rng.randint(1000, 9999)}"


def rand_address(rng: random.Random) -> tuple[str, str]:
    """Return (street_line, city_state_zip) tuple."""
    city, state = rng.choice(CITIES)
    street = f"{rng.randint(100, 9999)} {rng.choice(STREETS)} {rng.choice(STREET_TYPES)}"
    return street, f"{city}, {state} {rng.randint(10000, 99999)}"


def rand_email(rng: random.Random, company_name: str) -> str:
    """Derive a plausible email address from a company name."""
    slug = "".join(ch.lower() for ch in company_name.split()[0] if ch.isalnum())
    domain = rng.choice(EMAIL_DOMAINS)
    prefix = rng.choice(_EMAIL_PREFIXES + [slug])
    return f"{prefix}@{domain}"


def rand_party(rng: random.Random) -> Party:
    """Build a fully populated Party instance."""
    company = rand_company(rng)
    a1, a2 = rand_address(rng)
    return Party(
        name=company,
        address1=a1,
        address2=a2,
        phone=rand_phone(rng),
        email=rand_email(rng, company),
    )


def rand_date_pair(rng: random.Random) -> tuple[str, str]:
    """Return (doc_date, due_date) strings, due_date always after doc_date."""
    doc_date = date.today() + timedelta(days=rng.randint(-60, 0))
    due_date = doc_date + timedelta(days=rng.randint(15, 45))
    return doc_date.strftime("%B %d, %Y"), due_date.strftime("%B %d, %Y")


def rand_line_items(
    rng: random.Random,
    kind: Literal["products", "services"],
    count: int = 3,
) -> list[LineItem]:
    """Generate realistic LineItem instances.

    Products: unit price $15–$500, quantity 1–50.
    Services: unit price $500–$8000, quantity 1–5.
    """
    pool = PRODUCTS if kind == "products" else SERVICES
    chosen = rng.sample(pool, min(count, len(pool)))
    items = []
    for desc in chosen:
        if kind == "products":
            qty = rng.randint(1, 50)
            unit_price = Decimal(rng.randint(15, 500))
        else:
            qty = rng.randint(1, 5)
            unit_price = Decimal(rng.randint(500, 8000))
        items.append(LineItem(description=desc, quantity=qty, unit_price=unit_price))
    return items


# --- Checksum-valid identifiers ---
#
# These pass the standard format checks (Luhn / IBAN mod-97 / ABA) so they
# survive validators in test pipelines, while being deliberately fake: card
# numbers are random within test BIN ranges, and routing numbers use a "99"
# prefix that is not an assigned Federal Reserve routing symbol, so they are
# checksum-valid but non-routable. Never real accounts.

# brand -> (list of allowed prefixes, total length)
_CARD_BRANDS: dict[str, tuple[list[str], int]] = {
    "Visa": (["4"], 16),
    "Mastercard": (["51", "52", "53", "54", "55", "2221", "2720"], 16),
    "Amex": (["34", "37"], 15),
    "Discover": (["6011", "65"], 16),
}

# Countries whose BBAN we can build validly. digits = numeric BBAN length;
# letters = leading uppercase-letter block (bank code) counted within total.
_IBAN_SPECS: dict[str, tuple[int, int]] = {
    # country: (bban_letters, bban_digits)
    "DE": (0, 18),
    "ES": (0, 20),
    "NL": (4, 10),
}


def _luhn_check_digit(payload: str) -> int:
    """Return the Luhn check digit for a numeric payload (without check digit)."""
    total = 0
    for i, ch in enumerate(reversed(payload)):
        d = int(ch)
        if i % 2 == 0:  # every other digit starting from payload's rightmost
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - (total % 10)) % 10


def rand_card(rng: random.Random) -> tuple[str, str]:
    """Return (brand, Luhn-valid card number) — fake, within test BIN ranges."""
    brand = rng.choice(list(_CARD_BRANDS))
    prefixes, length = _CARD_BRANDS[brand]
    prefix = rng.choice(prefixes)
    body = prefix + "".join(str(rng.randint(0, 9)) for _ in range(length - 1 - len(prefix)))
    return brand, body + str(_luhn_check_digit(body))


def _iban_check_digits(country: str, bban: str) -> str:
    """Compute the two IBAN check digits (mod-97) for a country + BBAN."""
    rearranged = bban + country + "00"
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    return f"{98 - (int(numeric) % 97):02d}"


def rand_iban(rng: random.Random) -> str:
    """Return a mod-97-valid IBAN for a supported country. Fake account."""
    country = rng.choice(list(_IBAN_SPECS))
    n_letters, n_digits = _IBAN_SPECS[country]
    bank = "".join(rng.choice(string.ascii_uppercase) for _ in range(n_letters))
    account = "".join(str(rng.randint(0, 9)) for _ in range(n_digits))
    bban = bank + account
    return f"{country}{_iban_check_digits(country, bban)}{bban}"


def rand_routing_number(rng: random.Random) -> str:
    """Return an ABA-checksum-valid but non-routable routing number (99 prefix)."""
    d = [9, 9] + [rng.randint(0, 9) for _ in range(6)]  # d1..d8; 99 = unassigned prefix
    partial = 3 * (d[0] + d[3] + d[6]) + 7 * (d[1] + d[4] + d[7]) + (d[2] + d[5])
    d.append((10 - (partial % 10)) % 10)  # d9 makes the ABA checksum land on 0
    return "".join(str(x) for x in d)


def rand_account_number(rng: random.Random) -> str:
    """Return a random bank account number (10–12 digits)."""
    return "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(10, 12)))
