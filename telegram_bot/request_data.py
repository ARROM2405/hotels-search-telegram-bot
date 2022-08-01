
class Request:
    """Class to handle all the information about the current request."""
    def __init__(self):
        self.lang: str = 'ru'
        self.last_message_id: int = None
        self.last_message_text: str = None
        self.last_message_keyboard: dict = None
        self.chat_id: int = None
        self.command: str = None
        self.city: str = None
        self.min_price: int = None
        self.max_price: int = None
        self.distance: int = None
        self.search_results: int = None
        self.destinationID: int = None


class ResponseError(BaseException):
    def __str__(self):
        return 'something went wrong'


"""requests dict keeps the list of all active requests."""
requests_dict: [str, Request] = dict()
