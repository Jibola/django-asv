from ..utils import QueryValuesForeignKeyRatioBase
from .models import LargeAuthor, LargeBook


TOTAL_BOOKS = 1_000_000


class QueryValuesForeignKey1MilTotalBooks(QueryValuesForeignKeyRatioBase):
    timeout = 600
    _author = LargeAuthor
    _book = LargeBook
    _total_books = TOTAL_BOOKS

    @classmethod
    def setup(cls, ratio):
        return cls._setup(ratio)

    def teardown(self, *args, **kwargs):
        return super()._teardown()

    def time_query_id_search(self, *args, **kwargs):
        return super()._time_query_id_search(*args, **kwargs)

    def time_query_name_search(self, *args, **kwargs):
        return super()._time_query_name_search(*args, **kwargs)

    setup.timeout = 600
