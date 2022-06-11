import requests
from requests.adapters import HTTPAdapter, Retry
from urllib3.poolmanager import PoolManager

import ssl


retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])

class NewHttpAdapter(HTTPAdapter):
    def init_poolmanager(self, *pool_args, **pool_kwargs):
        self.poolmanager = PoolManager(
            *pool_args, ssl_version=ssl.PROTOCOL_TLSv1_2, retries=retries, **pool_kwargs
        )


r_session = requests.session()
adapter = NewHttpAdapter()
r_session.mount("https://", adapter)

r = r_session.get("https://pokeapi.co/api/v2/pokemon/ditto")
print(r.status_code, r.json())
