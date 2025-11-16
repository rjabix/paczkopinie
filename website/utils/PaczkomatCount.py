from website.models import Paczkomats


class PaczkomatCount:

    def __init__(self, singleDbResponse: tuple[Paczkomats, int]):
        self.paczkomat: Paczkomats = singleDbResponse[0]
        self.count: int = singleDbResponse[1]
