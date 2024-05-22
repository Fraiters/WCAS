from typing import Dict, Tuple, Union

from db.base_db import BaseDb
from db.db_settings import DB_USERS_COMMANDS


class UserDb(BaseDb):
    """ Класс работы с таблицей 'users' """

    async def insert_record_user(self, data: Dict):
        """ Добавление записи в таблицу пользователей """
        command = DB_USERS_COMMANDS.get("insert_user")
        await self.insert_record(command=command, data=data)

    async def select_user_id_by_username(self, username: str) -> Union[str, None]:
        """ Выбор user_id по username """
        command = DB_USERS_COMMANDS.get("select_user_id_by_username")
        result = await self.select_one_by(command=command, data=username)  # type: Union[Tuple, None]

        if result is None:
            return None
            # msg = "uuid по данному title не существует"
            # raise Exception(msg)

        return result[0]

    async def select_uuid_by_username(self, username: str) -> Union[int, None]:
        """ Выбор user_id по username """
        command = DB_USERS_COMMANDS.get("select_uuid_by_username")
        result = await self.select_one_by(command=command, data=username)  # type: Union[Tuple, None]

        if result is None:
            return None
            # msg = "uuid по данному title не существует"
            # raise Exception(msg)

        return result[0]
