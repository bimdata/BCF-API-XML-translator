from os import path
from lxml import etree, builder

SCHEMA_DIR = path.realpath(path.join(path.dirname(__file__), "../Schemas"))


class BcfXmlException(BaseException):
    pass


class JsonToXMLModel:
    def __init__(self, json):
        self.json = json
        self.maker = builder.ElementMaker()
        self.errors = None

    @property
    def xml(self):
        raise Exception("Unimplemented")

    def is_valid(self, raise_exception=False):
        if not hasattr(self, "SCHEMA_NAME"):
            raise Exception("This model can't be validated, set self.SCHEMA_NAME")

        schema_path = path.join(SCHEMA_DIR, self.SCHEMA_NAME)
        with open(schema_path, "r") as file:
            schema = etree.XMLSchema(file=file)

        if not schema.validate(self.xml):
            if raise_exception:
                raise BcfXmlException(schema.error_log)
            else:
                self.errors = schema.error_log
            return False
        return True
