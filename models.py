from elasticsearch_dsl import Date, DocType, String


class Article(DocType):
    """Elasticsearch document."""
    artist = String(analyzer='snowball')
    title = String(analyzer='snowball')
    datetime = Date()

    class Meta:
        index = 'thecurrent'

    def save(self, ** kwargs):
        return super(Article, self).save(** kwargs)
