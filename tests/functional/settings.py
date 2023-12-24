from pydantic import Field
from pydantic_settings import BaseSettings

from tests.functional.testdata.es_test_data import ES_MOVIES_NUMBER_OF_TEST_RECORDS


class SessionSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200')

    redis_host: str = Field('127.0.0.1')
    redis_port: int = Field(6379)


class BaseTestSettings(BaseSettings):
    es_index: str
    es_id_field: str = 'uuid'
    es_index_settings: dict = {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    }

    service_url: str = Field('http://127.0.0.1:8000')

    es_index_mapping: dict = {
        "movies": {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword"
                },
                "imdb_rating": {
                    "type": "float"
                },
                "genre": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },
                "description": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "directors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "actors_names": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "writers_names": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                }
            }
        }
    }


class GenreTestSettings(BaseTestSettings):
    es_index: str = 'genres'

    es_index_mapping: dict = {
        "genres": {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword"
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en"
                }
            }
        }
    }


class SearchTestSettings(BaseTestSettings):
    es_index: str = 'movies'


class FilmTestSettings(BaseTestSettings):
    es_index: str = 'movies'
    prefix: str = '/api/v1/films'
    page_size: int = ES_MOVIES_NUMBER_OF_TEST_RECORDS + 1


session_settings = SessionSettings()
search_test_settings = SearchTestSettings()
film_test_settings = FilmTestSettings()
genre_test_settings = GenreTestSettings()
