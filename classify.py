import json
import os

INPUT = "data/pages"
OUTPUT = "data/catalog"

os.makedirs(
    OUTPUT,
    exist_ok=True
)

RULES = {

"lost":[
"lost",
"misplaced",
"lost phone",
"lost wallet",
"lost document",
"missing"
],

"theft":[
"stolen",
"vehicle theft",
"mobile theft",
"robbery",
"theft"
],

"verification":[
"verification",
"certificate",
"tenant",
"character",
"clearance"
],

"complaint":[
"complaint",
"report",
"grievance"
],

"senior":[
"senior citizen",
"elderly"
],

"fir":[
"fir",
"case",
"police report"
],

"permission":[
"permission",
"license",
"approval",
"event"
],

"tracking":[
"track",
"search",
"status"
]

}


def detect_use_cases(
    service,
    content
):

    text = (

        service

        +

        " "

        +

        content

    ).lower()

    matches = []

    for category in RULES:

        words = RULES[
            category
        ]

        found = False

        for word in words:

            if word in text:

                matches.extend(
                    words
                )

                found = True

            if found:
                break

    if not matches:

        tokens = (

            service

            .lower()

            .replace(
                "/",
                " "
            )

            .split()

        )

        matches.extend(
            tokens
        )

    return list(
        set(
            matches
        )
    )


def describe(
    service,
    use_cases
):

    if use_cases:

        return (

            f"Service related to "

            +

            ", ".join(
                use_cases[:5]
            )

        )

    return (

        f"Police service: {service}"

    )


for file in os.listdir(
    INPUT
):

    if not file.endswith(
        ".json"
    ):
        continue

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

    service = data.get(
        "service",
        ""
    )

    content = data.get(
        "content",
        ""
    )

    use_cases = detect_use_cases(

        service,

        content

    )

    description = describe(

        service,

        use_cases

    )

    result = {

        "tab":
        data.get(
            "tab"
        ),

        "service":
        service,

        "url":
        data.get(
            "url"
        ),

        "description":
        description,

        "use_cases":
        use_cases,

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
        data.get(
            "internal_links",
            []
        )

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

            result,

            out,

            indent=2,

            ensure_ascii=False

        )

print(
"Improved catalog created"
)