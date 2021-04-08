class WikiFunction:
    def __init__(self, func_name: str, full_function_syntax: str, returning: str, description: str,
                 arg_descs: dict):
        self.function_name = func_name
        self.full_function_name_with_args = full_function_syntax
        self.returning_value = returning
        self.description = description
        self.arguments_descriptions = arg_descs

    def get_function_name(self):
        return self.function_name

    def get_full_function(self):
        return self.full_function_name_with_args

    def get_descriptions(self):
        return self.description

    def get_return_value(self):
        return self.returning_value

    def get_arguments_descriptions(self):
        return self.arguments_descriptions
