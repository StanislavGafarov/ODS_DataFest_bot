import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


class GoogleSpreadsheet():
    SCOPE = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    def __init__(self, client_secret_path):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret_path, self.SCOPE)
        gc = gspread.authorize(credentials)

        self.schedule = gc.open("ODS_Sheet_1").sheet1
        self.email_codes = gc.open("Data Fest⁶, регистрация (Ответы)").get_worksheet(1)

        self.table_map = {"SCHEDULE_TEST": self.schedule, "EMAIL_CODES": self.email_codes}

    def get_data(self, tab) -> pd.DataFrame:
        return pd.DataFrame(self.table_map[tab].get_all_records())
