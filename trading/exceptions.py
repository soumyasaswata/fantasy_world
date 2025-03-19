from rest_framework.exceptions import APIException

class TradeValidationError(APIException):
    status_code = 400
    default_detail = "Invalid trade request."
    default_code = "trade_validation_error"