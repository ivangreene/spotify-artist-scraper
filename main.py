from dotenv import load_dotenv
import spotipy
import sys
from itertools import chain
from spotipy.oauth2 import SpotifyClientCredentials

MAX_PAGE_LIMIT = 50
MAX_RESULTS = 1_000
START_CHAR = 'a'
END_CHAR = 'z'
MAX_QUERY_LENGTH = 6


load_dotenv()
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    traverse_from_seed()


def print_artists(artists):
    for artist in artists:
        print("{0},{1},{2},{3}".format(artist['id'], artist['name'], ";".join(artist['genres']), artist['popularity']))


def traverse_from_seed(seed=''):
    if seed:
        total, artists = get_artists_for_query(seed)
        if total < MAX_RESULTS:
            eprint("size for {0} ({1}) below max_result size ({2}), not continuing down tree"
                   .format(seed, total, MAX_RESULTS))
            print_artists(artists)
            return
        if len(seed) >= MAX_QUERY_LENGTH:
            eprint("seed {0} length at or equal to max query length ({1}), not continuing down tree"
                   .format(seed, MAX_QUERY_LENGTH))
            print_artists(artists)
            return
    for i in range(ord(START_CHAR), ord(END_CHAR) + 1):
        traverse_from_seed(seed + chr(i))


def get_artists_for_query(query):
    """
    Get artists for the given query. Eagerly loads the first page, and lazily loads the latter pages.
    :return a tuple of (total, artists)
    """
    eprint("getting artists for query {0}".format(query))
    total, first_page = get_artists_page(query, 0)
    if total < MAX_PAGE_LIMIT:
        return total, first_page
    return total,\
        chain(first_page,
              (item for page in
               (get_artists_page(query, offset)[1] for offset in range(MAX_PAGE_LIMIT, total, MAX_PAGE_LIMIT))
               for item in page))


def get_artists_page(query, offset):
    # Adding the year range seems to eliminate a lot of duplicates for certain
    # queries, allowing us to move across shorter queries more quickly.
    # TODO: Determine the significance of artists which do not fall within this year:1900-2050 filter
    result = sp.search(q=query + ' year:1900-2050', type='artist', limit=MAX_PAGE_LIMIT, offset=offset)
    return result['artists']['total'], result['artists']['items']


if __name__ == '__main__':
    main()
