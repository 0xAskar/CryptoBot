import pathlib
from pycoingecko import CoinGeckoAPI
print(pathlib.Path().absolute())
cg = CoinGeckoAPI()
print(cg.get_coin_info_from_contract_address_by_id(id = "ethereum", contract_address = "0x34fba4fedac025547777975087707579746f305cd219c1645ea2a837e9e72d1a"))
