class Application():
    def __init__(self, app, name=None, **params):
        self.app = app
        self.name = name
        self.params = params

    def get_application_type(self):
        return self.app

    def get_name(self):
        return self.name

    def get_params(self):
        return self.params

    def get_param_value(self, key):
        return self.params.get(key, None)

    def check_application(self):
        pass

    def prepare_application(self):
        pass

    def run_application(self):
        pass
