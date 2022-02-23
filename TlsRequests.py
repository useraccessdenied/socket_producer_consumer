import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

import ssl


class NewHttpAdapter(HTTPAdapter):
    def init_poolmanager(self, *pool_args, **pool_kwargs):
        self.poolmanager = PoolManager(
            *pool_args, ssl_version=ssl.PROTOCOL_TLSv1_1, **pool_kwargs
        )


r_session = requests.session()
adapter = NewHttpAdapter()
r_session.mount("https://", adapter)

r = r_session.get("https://pokeapi.co/api/v2/pokemon/ditto")
print(r.status_code, r.json())
