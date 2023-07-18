from litestar import Request


def logged_in_user_key_builder(request: Request) -> str:
    return (
        request.url.path
        + str(request.user)
        + str(request.method)
        + ",".join(sorted(request.url.query_params))
    )
