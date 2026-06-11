import httpx
from fastapi import Request, Response


class ProxyClient:
    def __init__(self, base_url: str):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=600.0)

    async def forward(self, request: Request, path: str) -> Response:
        # Собираем query string
        query = request.url.query
        full_path = f"{path}?{query}" if query else path

        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() != "host"
        }

        body = await request.body()

        upstream_response = await self._client.request(
            method=request.method,
            url=full_path,  # просто строка, base_url уже в клиенте
            headers=headers,
            content=body,
        )

        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=dict(upstream_response.headers),
            media_type=upstream_response.headers.get("content-type"),
        )

    async def aclose(self) -> None:
        await self._client.aclose()
