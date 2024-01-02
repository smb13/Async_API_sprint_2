import random
import uuid

persons_search_es_data = [
   {
       'uuid': str(uuid.uuid4()),
       'full_name': 'Trevor Munson',
       'films': [
           {
               'uuid': 'a0451bbf-e64d-4756-8360-e10382f86dc9',
               'roles': [
                   'writer'
               ]
           }
       ]
   } for _ in range(random.randint(0, 10))]
persons_search_es_data.extend([
    {
        'uuid': str(uuid.uuid4()),
        'full_name': 'Marc Connelly',
        'films': [
            {
                'uuid': '66d7de47-16d7-40e9-9d08-6e1773bc0bc3',
                'roles': [
                    'writer'
                ]
            }
        ]
    } for _ in range(random.randint(0, 10))])
persons_search_es_data.extend([
    {
        'uuid': str(uuid.uuid4()),
        'full_name': 'Mat Lucas',
        'films': [
            {
                'uuid': '044beafe-fe25-4edc-95f4-adbb8979c35b',
                'roles': [
                    'actor'
                ]
            },
            {
                'uuid': 'fdfc8266-5ece-4d85-b614-3cfe9be97b71',
                'roles': [
                    'actor'
                ]
            }
        ]
    } for _ in range(random.randint(0, 10))])
persons_search_es_data.extend([
    {
        'uuid': str(uuid.uuid4()),
        'full_name': 'Risto Tuorila',
        'films': [
            {
                'uuid': '3c061ba9-49d2-4603-9ab8-d26954e29ef5',
                'roles': [
                    'actor'
                ]
            },
            {
                'uuid': '29106b0c-4374-443d-bce7-700b4121d144',
                'roles': [
                    'actor'
                ]
            }
        ]
    } for _ in range(random.randint(0, 10))])
persons_search_es_data.extend([
    {
        'uuid': str(uuid.uuid4()),
        'full_name': 'Adriana Maggs',
        'films': [
            {
                'uuid': 'dda2478e-b12e-4ac9-a0fb-815174073f96',
                'roles': [
                    'director',
                    'writer'
                ]
            }
        ]
    } for _ in range(random.randint(0, 10))])


async def get_persons_words_to_search(es_data):
    words_to_search = ['risto', 'trevor', 'lucas']
    word_to_search = words_to_search[random.randint(0, len(words_to_search) - 1)]
    absent_word = 'w0r1d'
    return word_to_search, absent_word


async def get_persons_search_test_data(es_data):
    word_to_search, absent_word = await get_persons_words_to_search(es_data)

    searched_persons_data = []
    for person in es_data:
        if word_to_search in person.get('full_name').lower().split():
            searched_persons_data.append(person)
    searched_persons_data = sorted(searched_persons_data, key=(lambda film: film.get('full_name')))

    return word_to_search, absent_word, searched_persons_data
