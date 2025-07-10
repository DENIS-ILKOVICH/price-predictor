# test/conftest.py
import pytest
import requests
from tests.config import ServiceUrl


@pytest.fixture(scope="session")
def test_session():

    session = requests.Session()
    return session


@pytest.fixture
def post_request_predict(test_session):

    def _post_request_predict():

        form_data = {
            'district': 'Kievsky',
            'rooms': 1,
            'floor': 1,
            'floors': 3,
            'area': 50,
            'type': 'Czech',
            'cond': 'Renovation',
            'walls': 'Monolith'
        }

        response = test_session.post(url=ServiceUrl.SERVICE_URL_PREDICT, data=form_data)
        return response

    return _post_request_predict



@pytest.fixture
def get_request_predictions(test_session):

    def _get_request_predictions():
        response = requests.get(url=ServiceUrl.SERVICE_URL_PREDICTIONS)
        return response

    return _get_request_predictions


@pytest.fixture
def get_request_dataframe(test_session):

    def _get_request_dataframe():
        response = requests.get(url=ServiceUrl.SERVICE_URL_DATAFRAME)
        return response

    return _get_request_dataframe