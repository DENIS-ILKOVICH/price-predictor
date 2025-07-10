# test/test_dataframe.py
from tests.responsclass.responsclass import Response


def test_get_request_dataframe(get_request_dataframe):
    request = get_request_dataframe()

    response = Response(request)
    response.assert_status_code(200)
    assert 'error' not in response.response_json, f"Response should not contain error: {response.response_json}"
    print(response.__str__())

