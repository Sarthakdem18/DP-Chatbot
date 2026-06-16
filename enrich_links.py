from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import json

INPUT = "data/pages"
OUTPUT = "data/procedures"

os.makedirs(
    OUTPUT,
    exist_ok=True
)

GOOD = [

"faq",

"guide",

"instruction",

"apply",

"register",

"procedure",

"form",

".pdf",

"download"

]

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    for file in os.listdir(
        INPUT
    ):

        with open(

            os.path.join(
                INPUT,
                file
            ),

            "r",

            encoding="utf-8"

        ) as f:

            data = json.load(
                f
            )

        procedures = []

        for link in data.get(
            "internal_links",
            []
        ):

            url = link.get(
                "url",
                ""
            )

            title = link.get(
                "title",
                ""
            )

            combined = (

                title
                +
                url

            ).lower()

            useful = any(

                x in combined

                for x in GOOD

            )

            if not useful:

                continue

            try:

                print(
                    f"Opening {url}"
                )

                page.goto(

                    url,

                    wait_until="domcontentloaded",

                    timeout=30000

                )

                page.wait_for_timeout(
                    2000
                )

                soup = BeautifulSoup(

                    page.content(),

                    "html.parser"

                )

                text = soup.get_text(

                    " ",

                    strip=True

                )

                procedures.append({

                    "title":
                    title,

                    "url":
                    url,

                    "content":
                    text[:15000]

                })

            except:

                pass

        save = {

            "service":
            data["service"],

            "procedures":
            procedures

        }

        with open(

            os.path.join(
                OUTPUT,
                file
            ),

            "w",

            encoding="utf-8"

        ) as out:

            json.dump(

                save,

                out,

                indent=2,

                ensure_ascii=False

            )

    browser.close()

print(
"Procedure enrichment complete"
)