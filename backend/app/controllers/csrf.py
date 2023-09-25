from litestar import Router, get


@get(
    "/", description="Get a CSRF token to use in later requests", exclude_from_auth=True
)
async def csrf_get() -> None:
    return


router = Router(path="/csrf", route_handlers=[csrf_get])
