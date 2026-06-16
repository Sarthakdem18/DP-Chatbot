import json
import os
import csv

INPUT = "data/catalog"

rows = []

for file in os.listdir(
    INPUT
):

    if not file.endswith(
        ".json"
    ):
        continue

    path = os.path.join(
        INPUT,
        file
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(
            f
        )

    links = []

    for link in data.get(
        "internal_links",
        []
    ):

        title = link.get(
            "title",
            ""
        )

        url = link.get(
            "url",
            ""
        )

        links.append(
            f"{title} -> {url}"
        )

    rows.append({

        "tab":
        data.get(
            "tab",
            ""
        ),

        "service":
        data.get(
            "service",
            ""
        ),

        "url":
        data.get(
            "url",
            ""
        ),

        "description":
        data.get(
            "description",
            ""
        ),

        "use_cases":
        ", ".join(

            data.get(
                "use_cases",
                []
            )

        ),

        "requires_login":
        data.get(
            "requires_login",
            False
        ),

        "procedure_available":
        data.get(
            "procedure_available",
            False
        ),

        "internal_links":
        "\n".join(
            links
        )

    })

with open(

    "master_catalog.csv",

    "w",

    newline="",

    encoding="utf-8-sig"

) as f:

    writer = csv.DictWriter(

        f,

        fieldnames=[

            "tab",

            "service",

            "url",

            "description",

            "use_cases",

            "requires_login",

            "procedure_available",

            "internal_links"

        ]

    )

    writer.writeheader()

    writer.writerows(
        rows
    )

print(
"Detailed CSV exported"
)