import random
import re
import uuid


async def get_films_test_data(es_data):
    short_films_data = [{'uuid': film.get('uuid'),
                         'title': film.get('title'),
                         'imdb_rating': film.get('imdb_rating')}
                        for film in es_data]
    sorted_short_films_data = sorted(short_films_data, key=(lambda film: film.get('imdb_rating')))
    sorted_desc_short_films_data = sorted(short_films_data, key=(lambda film: -film.get('imdb_rating')))
    genre_to_filter = es_data[random.randint(0, len(es_data) - 1)].get('genre')[0].get('name')
    filtered_short_films_data = [{'uuid': film.get('uuid'),
                                  'title': film.get('title'),
                                  'imdb_rating': film.get('imdb_rating')}
                                 for film in
                                 list(filter(lambda film:
                                             genre_to_filter in [genre.get('name') for genre in
                                                                 film.get('genre')], es_data))]
    return (short_films_data, sorted_short_films_data, sorted_desc_short_films_data, genre_to_filter,
            filtered_short_films_data)


async def get_absent_genre():
    return 'g6nr6'


films_search_es_data = [
    {
        'uuid': str(uuid.uuid4()),
        'title': 'ANGRY BIRDS STAR WARS II',
        'imdb_rating': 7.7,
        'description': 'A retelling of Star Wars prequel trilogy with Angry Birds characters.',
        'genre': [
            {
                'uuid': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff',
                'name': 'Action'
            },
            {
                'uuid': '120a21cf-9097-479e-904a-13dd7198c1dd',
                'name': 'Adventure'
            },
            {
                'uuid': '6c162475-c7ed-4461-9184-001ef3d9f26e',
                'name': 'Sci-Fi'
            }
        ],
        'actors': [],
        'writers': [],
        'directors': []
    } for _ in range(random.randint(0, 10))]
films_search_es_data.extend(
    [{
        'uuid': str(uuid.uuid4()),
        'title': 'CHASING THE STAR',
        'imdb_rating': 3.1,
        'description': 'Three Magi Priests journey the unforgiving desert in search of the new born King.',
        'genre': [
          {
            'uuid': '120a21cf-9097-479e-904a-13dd7198c1dd',
            'name': 'Adventure'
          }
        ],
        'actors': [
          {
            'uuid': '079a361b-2574-4fc9-98e9-4107dc5b6a71',
            'full_name': 'Yancy Butler'
          },
          {
            'uuid': '3bb17a72-15b9-495d-afc9-b36512d99c48',
            'full_name': 'Johnny Rey Diaz'
          },
          {
            'uuid': '8e6051e5-8478-4090-8081-84fe3759fd23',
            'full_name': 'Terence Knox'
          },
          {
            'uuid': 'ef7c2589-fdd5-4410-a14e-b354989fa674',
            'full_name': 'Rance Howard'
          }
        ],
        'writers': [
          {
            'uuid': '606c74bd-ab92-4748-a5da-759f9cba91f8',
            'full_name': 'DJ Perry'
          }
        ],
        'directors': [
          {
            'uuid': '6ac5a43d-b7b5-4dba-adc2-0e48118c91be',
            'full_name': 'Bret Miller'
          }
        ],
        'actors_names': ['Yancy Butler', 'Johnny Rey Diaz', 'Terence Knox', 'Rance Howard'],
        'writers_names': ['DJ Perry', 'Bret Miller'],
    } for _ in range(random.randint(0, 10))])
films_search_es_data.extend([
    {
        'uuid': str(uuid.uuid4()),
        'title': 'CAPTAIN STAR',
        'imdb_rating': 7.6,
        'description': 'Captain Star, and his crew, Navigator Black, Atomic Engine Stoker',
        'genre': [
          {
            'uuid': '6a0a479b-cfec-41ac-b520-41b2b007b611',
            'name': 'Animation'
          },
          {
            'uuid': '5373d043-3f41-4ea8-9947-4b746c601bbd',
            'name': 'Comedy'
          },
          {
            'uuid': '6c162475-c7ed-4461-9184-001ef3d9f26e',
            'name': 'Sci-Fi'
          }
        ],
        'actors': [
          {
            'uuid': 'f957dc22-a84d-488d-96d6-5e88ce2e52f9',
            'full_name': 'Denica Fairman'
          }
        ],
        'writers': [
          {
            'uuid': '1cb8f48b-6f70-4c43-bf57-14704402ab2a',
            'full_name': 'Steven Appleby'
          },
          {
            'uuid': '412859f0-5f1e-4961-84ec-11ab919907d8',
            'full_name': 'Frank Cottrell Boyce'
          },
          {
            'uuid': '6b2cdfe9-484a-454f-a099-4766686dedee',
            'full_name': 'Geraldine Easter'
          },
          {
            'uuid': 'f08d49f5-1329-4eb3-9ac2-05a76235bc6b',
            'full_name': 'Pete Bishop'
          }
        ],
        'directors': [],
        'actors_names': ['Denica Fairman',],
        'writers_names': ['Steven Appleby', 'Frank Cottrell Boyce', 'Geraldine Easter', 'Pete Bishop'],
    } for _ in range(random.randint(0, 10))])
films_search_es_data.extend([
    {
        'uuid': str(uuid.uuid4()),
        'title': 'STAR TREK: THE NEXT GENERATION COMPANION',
        'imdb_rating': 7.8,
        'description': '',
        'genre': [
          {
            'uuid': '6c162475-c7ed-4461-9184-001ef3d9f26e',
            'name': 'Sci-Fi'
          }
        ],
        'actors': [
          {
            'uuid': '1f53497b-6afa-4908-a981-04ebede30769',
            'full_name': 'Denise Crosby'
          },
          {
            'uuid': '9607e3fa-d667-45d0-abd1-a81709b67896',
            'full_name': 'Michael Dorn'
          },
          {
            'uuid': 'becda658-04ca-462a-ab95-9d62b6164431',
            'full_name': 'Michelle Forbes'
          },
          {
            'uuid': 'fc9f27d2-aaee-46e6-b263-40ec8d2dd355',
            'full_name': 'LeVar Burton'
          }
        ],
        'writers': [
          {
            'uuid': '6960e2ca-889f-41f5-b728-1e7313e54d6c',
            'full_name': 'Gene Roddenberry'
          }
        ],
        'directors': [],
        'actors_names': ['Denise Crosby', 'Michael Dorn', 'Michelle Forbes', 'LeVar Burton'],
        'writers_names': ['Gene Roddenberry'],
    } for _ in range(random.randint(0, 10))])
films_search_es_data.extend([
    {
        'uuid': str(uuid.uuid4()),
        'title': 'LEGO STAR WARS: THE YODA CHRONICLES - SECRET PLANS ARE REVEALED',
        'imdb_rating': 6.5,
        'description': 'The adventures of Skywalker and his friends whilst Luke is still in training, told in Lego.',
        'genre': [
          {
            'uuid': '6a0a479b-cfec-41ac-b520-41b2b007b611',
            'name': 'Animation'
          },
          {
            'uuid': 'a886d0ec-c3f3-4b16-b973-dedcf5bfa395',
            'name': 'Short'
          }
        ],
        'actors': [
          {
            'uuid': '233f4bab-2a85-4567-aacf-f47a0b1f5b65',
            'full_name': 'Michael Donovan'
          },
          {
            'uuid': '45c40980-7bce-4e18-a0f8-e01deb83e0fa',
            'full_name': 'Kirby Morrow'
          },
          {
            'uuid': '535fbcb6-2768-42c2-a3ab-878c7b2c42ab',
            'full_name': 'Trevor Devall'
          },
          {
            'uuid': 'f85e4336-828c-4228-ba7e-923348bb67a4',
            'full_name': 'Peter Kelamis'
          }
        ],
        'writers': [
          {
            'uuid': '7fb5cb86-4b5d-4f78-97e3-6295ce2c0403',
            'full_name': 'Martin Skov'
          },
          {
            'uuid': '80a599bd-80be-46f4-856c-8780f6694433',
            'full_name': 'Daniel Lipkowitz'
          },
          {
            'uuid': '95567187-6aec-4d29-8d48-ea32a1db38a1',
            'full_name': 'John McCormack'
          }
        ],
        'directors': [
          {
            'uuid': '7fb5cb86-4b5d-4f78-97e3-6295ce2c0403',
            'full_name': 'Martin Skov'
          }
        ],
        'actors_names': ['Michael Donovan', 'Kirby Morrow', 'Trevor Devall', 'Peter Kelamis'],
        'writers_names': ['John McCormack', 'Daniel Lipkowitz', 'Martin Skov'],
    } for _ in range(random.randint(0, 10))])


async def get_films_words_to_search(es_data):
    words_to_search = ['star', 'yoda', 'captain']
    word_to_search = words_to_search[random.randint(0, len(words_to_search) - 1)]
    absent_word = 'w0r1d'
    return word_to_search, absent_word


async def get_films_search_test_data(es_data):
    (short_films_data, sorted_short_films_data, sorted_desc_short_films_data, genre_to_filter,
     filtered_short_films_data) = await get_films_test_data(es_data)

    word_to_search, absent_word = await get_films_words_to_search(es_data)

    searched_short_films_data = []
    for film in es_data:
        if word_to_search in re.sub(r'[^\w\s]', '', film.get('title').lower()).split():
            searched_short_films_data.append(
                {'uuid': film.get('uuid'),
                 'title': film.get('title'),
                 'imdb_rating': film.get('imdb_rating')}
            )
    searched_short_films_data = sorted(searched_short_films_data, key=(lambda film: film.get('title')))
    searched_sorted_short_films_data = sorted(searched_short_films_data, key=(lambda film: film.get('imdb_rating')))
    searched_sorted_desc_short_films_data = sorted(searched_short_films_data,
                                                   key=(lambda film: -film.get('imdb_rating')))

    return (word_to_search, absent_word, short_films_data, searched_short_films_data, searched_sorted_short_films_data,
            searched_sorted_desc_short_films_data)
