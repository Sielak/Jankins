from decimal import Decimal
import datetime


header = {
    "ftgnr": "57608", 
    "kundbestnr": "IO590110", 
    "kundref2": "Anders Palmlöf", 
    "OrdLevPlats1": "73435", 
    "ordstat": 10, 
    "salestype": "19", 
    "kundfraktdeb": "1", 
    "ordertextkod": None, 
    "godsmarke1": None, 
    "godsmarke2": "Test", 
    "edit": "HL Leveransdatum: 2020-11-25\nKommentar:\nHej! Vi önskar även 2 frp röda.", 
    "prislista": 1009, 
    "q_hl_sendttlinkemail": None, 
    "lagstalle": "0", 
    "ordtyp": 1, 
    "momskod": 0, 
    "q_salesmarket_code": "SE", 
    "q_hl_emailtt": None
}


rows = [
    {
        "artnr": "304203",
        "ordantal": Decimal("100.000000"),
        "vb_pris": Decimal("4.7100"),
        "fsgprisper": 1.0,
        "ordradst": 10,
        "artnrkund": "22",
        "ordtyp": 1,
        "lagstalle": "0",
        "q_hl_ord_comefrom": 2,
        "momskod": 0,
        "altenhetkod": None,
        "ordantalaltenh": Decimal("0.000000"),
        "bestallas": "0"
    },
    {
        "artnr": "304203",
        "ordantal": Decimal("150.000000"),
        "vb_pris": Decimal("4.7100"),
        "fsgprisper": 1.0,
        "ordradst": 10,
        "artnrkund": "22",
        "ordtyp": 1,
        "lagstalle": "0",
        "q_hl_ord_comefrom": 2,
        "momskod": 0,
        "altenhetkod": None,
        "ordantalaltenh": Decimal("0.000000"),
        "bestallas": "0"
    },
    {
        "artnr": "304203",
        "ordantal": Decimal("200.000000"),
        "vb_pris": Decimal("4.7100"),
        "fsgprisper": 1.0,
        "ordradst": 10,
        "artnrkund": "22",
        "ordtyp": 1,
        "lagstalle": "0",
        "q_hl_ord_comefrom": 2,
        "momskod": 0,
        "altenhetkod": None,
        "ordantalaltenh": Decimal("0.000000"),
        "bestallas": "0"
    }
]