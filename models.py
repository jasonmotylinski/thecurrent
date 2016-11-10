from elasticsearch_dsl import Date, DocType, String


class Article(DocType):
    """Elasticsearch document."""
    artist = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    title = String(analyzer='snowball', fields={'raw': String(index='not_analyzed')})
    datetime = Date()

    class Meta:
        index = 'thecurrent'

    def save(self, ** kwargs):
        return super(Article, self).save(** kwargs)
