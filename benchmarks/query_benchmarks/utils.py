from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
from random import randrange

from django.db import models

from ..utils import bench_setup
from ..models import Author, Book


class ForeignKeyQuery(Enum):
    BOOK_ID_FROM_AUTHOR = auto()
    BOOK_NAME_FROM_AUTHOR = auto()
    AUTHOR_ID_FROM_BOOK = auto()
    AUTOR_NAME_FROM_BOOK = auto()


class QueryValuesForeignKeyRatioBase:
    timeout = 200
    _author: models.Model = Author
    _book: models.Model = Book
    _total_books: int = 10
    _query_type: ForeignKeyQuery = ForeignKeyQuery.AUTHOR_ID_FROM_BOOK
    _previous_ratio = None
    authors = []
    params = [1, 10, 100, 1_000]
    param_names = ["book_to_author_ratio"]

    @classmethod
    def _setup(cls, ratio):
        if ratio == cls._previous_ratio:
            # database is already configured
            return
        else:
            cls._teardown(cls, final=True)

        bench_setup(migrate=True)
        num_authors = cls._total_books // ratio or 1
        authors = [
            cls._author.objects.create(author=f"author {y}") for y in range(num_authors)
        ]
        with ThreadPoolExecutor(max_workers=5) as exec:
            for book in range(cls._total_books):
                exec.submit(
                    cls._book(
                        title=f"title {book}",
                        author=authors[book % len(authors)],
                    ).save
                )
        cls._previous_ratio = ratio
        cls.authors = authors

    def _teardown(self, *args, **kwargs):
        # disable teardown for now will manually delete collection after runs
        if kwargs.get("final") is True:
            self._book.objects.all().delete()
            self._author.objects.all().delete()

    def _time_query_id_search(self, *args, **kwargs):
        self.__inner_query_foreign_key(ForeignKeyQuery.BOOK_ID_FROM_AUTHOR)

    def _time_query_name_search(self, *args, **kwargs):
        self.__inner_query_foreign_key(ForeignKeyQuery.AUTHOR_ID_FROM_BOOK)

    def __inner_query_foreign_key(self, query_type):
        # Select a value at random to bypass potential caching and ordering
        rand_author = self.authors[randrange(len(self.authors))]
        match query_type:
            case ForeignKeyQuery.BOOK_ID_FROM_AUTHOR:
                list(self._book.objects.filter(author__author=rand_author.author)[:100])
            case ForeignKeyQuery.BOOK_NAME_FROM_AUTHOR:
                list(self._book.objects.filter(author=rand_author)[:100])


def generate_foreign_key_benchmark(
    name, author, book, total_books, total_timeout=None, setup_timeout=None
):
    class QueryValueFactory(QueryValuesForeignKeyRatioBase):
        timeout = total_timeout or QueryValuesForeignKeyRatioBase.timeout
        benchmark_name = name
        pretty_name = name
        _author = author
        _book = book
        _total_books = total_books

        @classmethod
        def setup(cls, ratio):
            return cls._setup(ratio)

        def teardown(self, *args, **kwargs):
            return super()._teardown()

        def time_query_id_search(self, *args, **kwargs):
            return super()._time_query_id_search(*args, **kwargs)

        def time_query_name_search(self, *args, **kwargs):
            return super()._time_query_name_search(*args, **kwargs)

        setup.timeout = setup_timeout or QueryValuesForeignKeyRatioBase.timeout

    return QueryValueFactory
