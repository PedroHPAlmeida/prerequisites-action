from unittest.mock import patch

from pytest import fixture


@fixture
def mock_requests():
    with patch('src.github.requests') as mock:
        yield mock


@fixture
def mock_response():
    class Response:
        def __init__(self) -> None:
            self.status_code = 200

        def json(self):
            return dict()

    return Response()


@fixture
def mock_json():
    with patch('src.github.json') as mock:
        yield mock


@fixture
def mock_get_branch_response_success():
    return ({'ref': 'any', 'object': {'sha': 'any', 'url': 'any-url'}}, 200)
