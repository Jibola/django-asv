from ...utils import bench_setup
from .models import Author, Book


class QueryValuesForeignKey:
    def setup(self):
        bench_setup(migrate=True)
        authors = [Author.objects.create(author=str(y)) for y in range(10)]
        for x in range(10):
            Book(title="title", author=authors[x]).save()
        self.authors = authors

    def teardown(self):
        Book.objects.all().delete()
        Author.objects.all().delete()

    def time_query_foreign_key_author_author(self):
        for author in self.authors:
            list(Book.objects.filter(author__author=author.author))

    def time_query_foreign_key_author_id(self):
        for author in self.authors:
            list(Book.objects.filter(author=author))
