# test/responsclass/responsclass.py

class Response:
    def __init__(self, response):
        self.response = response
        self.response_json = response.json()
        self.response_code = response.status_code

    def assert_status_code(self, status_code):
        if isinstance(status_code, list):
            assert self.response_code in status_code, self
        else:
            assert self.response_code == status_code, self
        return self

    # def validate(self, schema):
    #     if isinstance(self.response_json, list):
    #         for i, item in enumerate(self.response_json):
    #             try:
    #                 schema.model_validate(item)
    #             except ValidationError as e:
    #                 print(f"Element validation error {i}: {e}")
    #     else:
    #         try:
    #             schema.model_validate(self.response_json)
    #         except ValidationError as e:
    #             print(f"Element validation error: {e}")

    def __str__(self):
        return \
            f'Status code: {self.response_code} \n' \
            f'Request url: {self.response.url} \n' \
            f'Request data: {self.response_json}'
