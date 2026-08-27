import sys
import traceback

class CustomExceptions(Exception):
    def __init__(self, error_message, error_detail : sys):
        super().__init__(error_message)
        self.error_message = self.get_detailed_message(error_message, error_detail)
    
    @staticmethod
    def get_detailed_message(error_message, error_detail : sys):
        _, _, exc_tb = traceback.sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        error_message = f"Error occurred in python script [{file_name}] line number [{line_number}] error message [{error_message}]"
        return error_message
    
    def __str__(self):
        return self.error_message
   