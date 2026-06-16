from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os

BASE_URL = "https://delhipolice.gov.in/"

# ======================
# LOAD SERVICES
# ======================

with open(
    "data/services.json",
    "r",
    encoding="utf-8"
) as f:

    services = json.load(f)

os.makedirs(
    "data/pages",
    exist_ok=True
)

# ======================
# START EXTRACTION
# ======================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    for service in services:

        try:

            url = service["url"]

            # Fix relative URLs
            if not (

                url.startswith(
                    "http"
                )

            ):

                url = (

                    BASE_URL

                    +

                    url.lstrip(
                        "/"
                    )

                )

            print(
                f"Opening {url}"
            )

            page.goto(

                url,

                wait_until="domcontentloaded",

                timeout=60000

            )

            page.wait_for_timeout(
                3000
            )

            html = page.content()

            soup = BeautifulSoup(

                html,

                "html.parser"

            )

            # Remove junk
            for tag in soup(

                [

                    "script",

                    "style"

                ]

            ):

                tag.decompose()

            # Extract text
            text = soup.get_text(

                separator=" ",

                strip=True

            )

            text = " ".join(

                text.split()

            )

            lower = text.lower()

            # Detect login
            requires_login = any(

                x in lower

                for x in [

                    "login",

                    "password",

                    "otp",

                    "user id",

                    "sign in"

                ]

            )

            # Detect procedure
            procedure_available = any(

                x in lower

                for x in [

                    "faq",

                    "register",

                    "apply",

                    "procedure",

                    "instructions",

                    "report",

                    "documents"

                ]

            )

            # Extract links
            internal_links = []

            for a in soup.find_all(

                "a",

                href=True

            ):

                href = (

                    a[
                        "href"
                    ]

                    .strip()

                )

                title = (

                    a
                    .get_text(
                        strip=True
                    )

                )

                if (

                    not href

                    or href == "#"

                    or href.startswith(
                        "javascript"
                    )

                    or href.startswith(
                        "mailto"
                    )

                    or href.startswith(
                        "tel"
                    )

                ):

                    continue

                if not (

                    href.startswith(
                        "http"
                    )

                ):

                    href = (

                        BASE_URL

                        +

                        href.lstrip(
                            "/"
                        )

                    )

                internal_links.append({

                    "title":
                    title,

                    "url":
                    href

                })

            output = {

                "tab":
                service.get(
                    "tab"
                ),

                "service":
                service[
                    "title"
                ],

                "url":
                url,

                "requires_login":
                requires_login,

                "procedure_available":
                procedure_available,

                "content":
                text,

                "internal_links":
                internal_links

            }

            filename = (

                service[
                    "title"
                ]

                .replace(
                    "/",
                    "_"
                )

                .replace(
                    "\\",
                    "_"
                )

                .replace(
                    " ",
                    "_"
                )

            )

            with open(

                f"data/pages/{filename}.json",

                "w",

                encoding="utf-8"

            ) as out:

                json.dump(

                    output,

                    out,

                    indent=2,

                    ensure_ascii=False

                )

            print(
                "Saved ✓"
            )

        except Exception as e:

            print(

                f"FAILED → {service['title']}"

            )

            print(
                e
            )

    browser.close()

print(
    "\nDONE"
)