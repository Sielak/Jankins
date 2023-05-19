from decimal import Decimal
import datetime


header = {
    "ftgnr": "92393",
    "kundbestnr": "PO00150958",
    "kundref2": "Miikka Koskinen",
    "OrdLevPlats1": None,
    "ordstat": 10,
    "salestype": "19",
    "kundfraktdeb": "0",
    "ordertextkod": "2",
    "godsmarke1": None,
    "godsmarke2": "PO00150958",
    "edit": None,
    "prislista": 30016,
    "q_hl_sendttlinkemail": "1",
    "lagstalle": "0",
    "ordtyp": 1,
    "momskod": 10,
    "q_salesmarket_code": "FI",
    "q_hl_emailtt": "Miikka.Koskinen@sok.fi"
}

rows = [
    {
        "artnr": "567683",
        "ordantal": Decimal("6.000000"),
        "vb_pris": Decimal("20.1100"),
        "fsgprisper": 1.0,
        "ordradst": 10,
        "artnrkund": None,
        "ordtyp": 1,
        "lagstalle": "0",
        "q_hl_ord_comefrom": 2,
        "momskod": 10,
        "altenhetkod": None,
        "ordantalaltenh": Decimal("0.000000"),
        "bestallas": "0"
    },
    {
        "artnr": "309023",
        "ordantal": Decimal("1.000000"),
        "vb_pris": Decimal("0.1200"),
        "fsgprisper": 1.0,
        "ordradst": 10,
        "artnrkund": '309023',
        "ordtyp": 1,
        "lagstalle": "0",
        "q_hl_ord_comefrom": 2,
        "momskod": 10,
        "altenhetkod": None,
        "ordantalaltenh": Decimal("0.000000"),
        "bestallas": "0"
    },
    {
        "artnr": "310969",
        "ordantal": Decimal("101.000000"),
        "vb_pris": Decimal("1.9400"),
        "fsgprisper": 1.0,
        "ordradst": 10,
        "artnrkund": "310969",
        "ordtyp": 1,
        "lagstalle": "0",
        "q_hl_ord_comefrom": 2,
        "momskod": 10,
        "altenhetkod": None,
        "ordantalaltenh": Decimal("0.000000"),
        "bestallas": "0"
    }
]