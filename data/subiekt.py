from app.config import AppConfig
from app.mssql import MSSQL
from app.helper import Helper

class Subiekt(object):

    def __init__(self):
        self.config = AppConfig()

    def get_products(self):
        database = MSSQL()

        query = """
            SELECT
                [id] = T.tw_Id,
                [symbol] = T.tw_Symbol,
                [rodzaj] = T.tw_Rodzaj,
                [vat] = T.tw_IdVatSp,
                [cena] = C.tc_""" + self.config.SUBIEKT_PRICE + """,
                [stok] = M.st_Stan,
                [rezerwacja] = M.st_StanRez,
                [dostepne] = M.st_Stan - M.st_StanRez
            FROM tw__Towar T
            JOIN tw_Cena C ON T.tw_Id = C.tc_IdTowar
            JOIN tw_Stan M ON tw_Id = M.st_TowId AND M.st_MagId IN(""" + self.config.SUBIEKT_WAREHOUSE + """)
            WHERE T.tw_Usuniety = 0 AND T.tw_Zablokowany = 0
        """

        results = database.fetch_data(query)

        results = Helper.create_dict_by_key(results, 'id', 'id_')

        return results
