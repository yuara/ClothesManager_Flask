import json, requests, uuid
from flask_babel import _
from flask import current_app


def translate(text, source_language, dest_language):
    if (
        "MS_TRANSLATOR_KEY" not in current_app.config
        or not current_app.config["MS_TRANSLATOR_KEY"]
    ):
        return _("Error: the translation service is not configured.")

    endpoint = "https://api.cognitive.microsofttranslator.com"
    version = "translate?api-version=3.0"
    constructed_url = f"{endpoint}/{version}&from={source_language}&to={dest_language}"
    headers = {
        "Ocp-Apim-Subscription-Key": current_app.config["MS_TRANSLATOR_KEY"],
        "Ocp-Apim-Subscription-Region": "eastasia",
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    body = [{"text": text}]
    req = requests.post(constructed_url, headers=headers, json=body)
    res = req.json()

    if req.status_code != 200:
        return _("Error: the translation service failed.")
    return res[0]["translations"][0]["text"]
