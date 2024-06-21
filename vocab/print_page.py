#!/usr/bin/env python
from typing import List
from google.cloud import translate_v2 as translate
import os

# Step 1: Read all lines from vocab.txt
with open("./vocab/vocab.txt", "r") as file:
    lines = file.readlines()


# Step 2: Translate each line using a web API
# https://cloud.google.com/translate/docs/basic/translating-text#translate_translate_text-python
def translate_text(target: str, text: List[str]) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(
        text, target_language=target, source_language="de"
    )

    for line in result:
        print("Text: {}".format(line["input"]))
        print("Translation: {}".format(line["translatedText"]))

    return result


translated_lines = translate_text("en", lines)

# Step 3: Convert translated results into a web page format
html_content = "<html><body>"
for line in translated_lines:
    html_content += f"<p>{line}</p>"
html_content += "</body></html>"

# Step 4: Print the web page as a PDF
# https://stackoverflow.com/a/75342366/6040478

# Save html_content to a file
with open("./vocab/printout.html", "w") as file:
    file.write(html_content)
os.system(
    'vivaldi-stable --print-to-pdf="./vocab/printout.pdf" --headless "./vocab/printout.html"'
)
