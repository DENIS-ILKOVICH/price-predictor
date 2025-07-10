# app/controllers/real_estate_controllers.py
from ..controllers import REData, ValidationError
from ..utils.utils import Utils

class Controller:
    def __init__(self, req):
        self.req = req

    def filter_input_data_form(self, min_data, max_data):
        try:

            district = self.req.form.get("district")
            rooms = self.req.form.get("rooms")
            floor = self.req.form.get("floor")
            floors = self.req.form.get("floors")
            area = self.req.form.get("area")
            datatype = self.req.form.get("type")
            cond = self.req.form.get("cond")
            walls = self.req.form.get("walls")
            desc = self.req.form.get("desc")


            data_dict = {
                'district': district,
                'rooms': rooms,
                'floor': floor,
                'floors': floors,
                'area': area,
                'type': datatype,
                'cond': cond,
                'walls': walls,
            }

            try:
                data = REData(**data_dict)
                data_dict = data.dict()
            except ValidationError as e:
                return None

            data_dict['desc'] = desc

            utils = Utils()

            res = utils.validate_input_data_from_model(data_dict, min_data, max_data)

            if res is not None:
                return {'error_list': res}


            return data_dict

        except Exception as e:
            return None


    def filter_input_data_json(self, min_data, max_data):
        try:
            district = self.req.json.get("district")
            rooms = self.req.json.get("rooms")
            floor = self.req.json.get("floor")
            floors = self.req.json.get("floors")
            area = self.req.json.get("area")
            datatype = self.req.json.get("datatype")
            cond = self.req.json.get("cond")
            walls = self.req.json.get("walls")
            desc = self.req.json.get("desc")

            data_dict = {
                'district': district,
                'rooms': rooms,
                'floor': floor,
                'floors': floors,
                'area': area,
                'type': datatype,
                'cond': cond,
                'walls': walls,
            }

            try:
                data = REData(**data_dict)
                data_dict = data.dict()
            except ValidationError as e:
                return None

            data_dict['desc'] = desc

            utils = Utils()

            res = utils.validate_input_data_from_model(data_dict, min_data, max_data)

            if res is not None:
                return {'error_list': res}


            return data_dict

        except Exception as e:
            return None

