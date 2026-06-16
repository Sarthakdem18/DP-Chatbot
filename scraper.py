from playwright.sync_api import sync_playwright
import json
import os

URL = "https://delhipolice.gov.in/index"

os.makedirs(
    "data",
    exist_ok=True
)

services = []

BLACKLIST = [

"HOME",
"ABOUT US",
"SERVICES",
"INITIATIVES",
"RECRUITMENT",
"WELFARE",
"FEEDBACK",
"CONTACT US",
"USEFUL LINKS",
"Citizen Services",
"Police Services",

"View All",

"Feedback"

]

BAD_PREFIX = (

"#",

"mailto:",

"tel:",

"javascript"

)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout = 90000
    )

    page.wait_for_timeout(
        5000
    )

    tabs = [

        "Citizen Services",

        "Police Services"

    ]

    for tab in tabs:

        print(
            f"\nScanning {tab}"
        )

        try:

            page.get_by_role(
                "link",
                name=tab,
                exact=True
            ).click()

            page.wait_for_timeout(
                2500
            )

        except:
            pass

        # IMPORTANT
        cards = page.locator(
            "#service-box a"
        )

        count = cards.count()

        for i in range(
            count
        ):

            try:

                card = cards.nth(
                    i
                )

                title = (

                    card
                    .inner_text()

                    .replace(
                        "\n",
                        " "
                    )

                    .strip()

                )

                href = card.get_attribute(
                    "href"
                )

                if (
                    not title
                    or not href
                ):

                    continue

                if (
                    title
                    in BLACKLIST
                ):

                    continue

                if (
                    href.startswith(
                        BAD_PREFIX
                    )
                ):

                    continue

                services.append({

                    "tab":
                    tab,

                    "title":
                    title,

                    "url":
                    href

                })

            except:
                pass

    browser.close()

# Remove duplicates

seen = set()

clean = []

for s in services:

    key = (
        s["title"],
        s["url"]
    )

    if key not in seen:

        clean.append(
            s
        )

        seen.add(
            key
        )

with open(

    "data/services.json",

    "w",

    encoding="utf-8"

) as f:

    json.dump(

        clean,

        f,

        indent=2,

        ensure_ascii=False

    )

print(
f"\nFINAL SERVICES: {len(clean)}"
)