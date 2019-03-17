import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

class Google_spread_sheet():
    def __init__(self, client_secret_path = './tgbot/client_secret.json', scope=SCOPE):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret_path, scope)
        gc = gspread.authorize(credentials)
        self.tab_1 = gc.open("ODS_Sheet_1").sheet1

    def get_data(self) -> pd.DataFrame:
        return pd.DataFrame(self.tab_1.get_all_records())
