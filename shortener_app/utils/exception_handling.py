from fastapi import HTTPException, Request


def handle_exception(status_code: int, message: str = "", request: Request = None):
    match status_code:
        case 400:
            raise_bad_request(message)
        case 404:
            raise_not_found(request)
        case 409:
            raise_entity_already_exists()


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)


def raise_entity_already_exists():
    message = "Custom URL already exists"
    raise HTTPException(status_code=409, detail=message)
