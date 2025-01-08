class Application():
    def __init__(self, app, name=None):
        self.app = app
        self.name = name

    def get_application_type(self):
        return self.app

    def get_name(self):
        return self.name

    def check_application(self):
        pass

    def prepare_application(self):
        pass

    def run_application(self):
        pass
