# test/test_predictions.py
from tests.responsclass.responsclass import Response


def test_post_request_predict(post_request_predict):
    request = post_request_predict()

    response = Response(request)
    response.assert_status_code(201)
    assert 'error' not in response.response_json, f"Response should not contain error: {response.response_json}"
    print(response.__str__())


def test_get_request_predictions(get_request_predictions):
    request = get_request_predictions()

    response = Response(request)
    response.assert_status_code(200)
    assert 'error' not in response.response_json, f"Response should not contain error: {response.response_json}"
    print(response.__str__())

