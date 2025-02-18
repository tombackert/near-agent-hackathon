import os.path
import json
import collections
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Wir verwenden hier nur den readonly-Scopes, da wir nur lesen.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Gib hier deine eigene Spreadsheet-ID und den Range an.
MY_SPREADSHEET_ID = "1vi8yPHNMTOBF6NtuqniwoN42juEfzgzF4M1i4N7NElA"
MY_RANGE_NAME = "Formularantworten 1!A:C"

def aggregate_responses(rows, title, description):
    """
    Aggregiert die Antworten aus den Sheet-Zeilen.
    Annahme: Die erste Zeile enthält Header, 
    wobei die erste Spalte (z.B. Zeitstempel) nicht ausgewertet wird.
    """
    if not rows or len(rows) < 2:
        return {"title": title, "description": description, "questions": []}
    
    header = rows[0]              # z.B. ["Spalte 1", "Question 1", "Question 2"]
    responses = rows[1:]          # Jede Zeile entspricht einer Antwort

    # Die Fragen stehen in den Spalten ab Index 1
    questions = header[1:]
    analysis_list = []

    # Für jede Frage sammeln wir die Antworten
    for i, question in enumerate(questions, start=1):
        counter = collections.Counter()
        for response in responses:
            if len(response) > i:
                answer = response[i]
                counter[answer] += 1

        total = sum(counter.values())
        distribution = []
        for option, count in counter.items():
            percentage = round((count / total) * 100, 2) if total > 0 else 0
            distribution.append({
                "option": option,
                "count": count,
                "percentage": percentage
            })
        
        # Bestimme die häufigste Antwort
        most_common_answer = counter.most_common(1)[0][0] if total > 0 else None

        analysis_list.append({
            "question": question,
            "analysis": {
                "most_common_answer": most_common_answer,
                "distribution": distribution
            }
        })

    return {
        "title": title,
        "description": description,
        "questions": analysis_list
    }

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=MY_SPREADSHEET_ID, range=MY_RANGE_NAME).execute()
        rows = result.get("values", [])

        if not rows:
            print("No data found.")
            return

        # Hier definieren wir den Titel und die Beschreibung der Umfrage
        survey_title = "Test Titel"
        survey_description = "Test description"

        # Aggregiere die Rohdaten
        aggregated_data = aggregate_responses(rows, survey_title, survey_description)
        
        # Ausgabe als JSON
        print(json.dumps(aggregated_data, indent=2))

    except HttpError as err:
        print(err)

if __name__ == "__main__":
    main()
