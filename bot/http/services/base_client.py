import asyncio
import aiohttp

from ..models import BaseRequest

DEFAULT_TIMEOUT = 120

class BaseClient:
    BASE_URL = "https://api.localhost"

    def __init__(self, loop=None) -> None:
        if loop is None:
            loop = asyncio.get_event_loop()
        
        self.__loop = loop
        self.__headers = {
            'Authorization': "",
            'content_type': "application/json"
        }

    def _get_api_url(self, relative_path: str):
        if not relative_path.startswith("/"):
            raise ValueError(f"Relative url must start by a '/', got {relative_path}")

        return self.BASE_URL + relative_path

    def __merge_params(self, url: str, **params) -> str:
        url += "?"
        for key, value in params:
            url += f"{key}={value}&"
        url[:-1]

        return url

    async def get(self, url: str, timeout=DEFAULT_TIMEOUT, **params):
        if len(params.keys()) > 0:
            url = self.__merge_params(url, params)

        async with aiohttp.ClientSession(loop=self.__loop, timeout=timeout, headers=self.__headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()

                return response.json()

    async def post(self, url: str, data: BaseRequest, timeout=DEFAULT_TIMEOUT, **params):
        if len(params.keys()) > 0:
            url = self.__merge_params(url, params)
        
        async with aiohttp.ClientSession(loop=self.__loop, timeout=timeout, ) as session:
            async with session.post(url, data=data) as response:
                response.raise_for_status()

                return response.json()

    async def put(self, url: str, data: BaseRequest, timeout=DEFAULT_TIMEOUT, **params):
        if len(params.keys()) > 0:
            url = self.__merge_params(url, params)
        
        async with aiohttp.ClientSession(loop=self.__loop, timeout=timeout) as session:
            async with session.put(url, data=data) as response:
                response.raise_for_status()

                return response.json()

    async def delete(self, url: str, timeout=DEFAULT_TIMEOUT, **params):
        if len(params.keys()) > 0:
            url = self.__merge_params(url, params)
        
        async with aiohttp.ClientSession(loop=self.__loop, timeout=timeout) as session:
            async with session.delete(url) as response:
                response.raise_for_status()

                return response.json()