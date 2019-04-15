import pandas as pd
import pygsheets

from backend.models import Invite
from backend.tgbot.utils import logger


class GoogleSpreadsheet():
    SCOPE = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    def __init__(self, client_secret_path):
        self.client_secret_path = client_secret_path

        self.table_map = {"SCHEDULE_TEST": self.schedule_sheet, "EMAIL_CODES": self.email_sheet}

    def get_data(self, tab) -> pd.DataFrame:
        return pd.DataFrame(self.table_map[tab]().get_all_records())

    @property
    def _client(self):
        return pygsheets.authorize(service_account_file=self.client_secret_path)

    def email_sheet(self):
        return self._client.open('Data Fest⁶, регистрация (Ответы)').worksheet(value=1)

    def schedule_sheet(self):
        return self._client.open("ODS_Sheet_1").sheet1

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
