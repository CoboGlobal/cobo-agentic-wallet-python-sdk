class AuthHelper(object):
    @classmethod
    def generate_headers(
        cls,
        api_key: str,
    ):
        headers = {}
        if api_key is not None:
            headers["X-API-Key"] = api_key
        return headers
