import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from backend.models import Invite
from backend.tgbot.utils import logger


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

    def update_invites(self):
        existing_invite_count = len(Invite.objects.all())
        count = 0
        invites = self.get_data('EMAIL_CODES')
        iterrows = invites[['Адрес электронной почты', 'Ваше имя ', 'Ваша фамилия', 'Код для бота']].iterrows()
        # with transaction.atomic():
        for i, (email, name, surname, code) in iterrows:
            try:
                invite = Invite(email=email, name=name, surname=surname, code=code)
                invite.save()
                count += 1
            except:
                logger.debug('skipping email {}'.format(email))

        new_invite_count = len(Invite.objects.all())
        delta = new_invite_count - existing_invite_count
        assert delta == count, 'old {}, new {}, delta {}, count {}'.format(existing_invite_count, new_invite_count,
                                                                           delta, count)
        return delta
