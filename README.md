# spotify-artist-scraper
Goal: scrape all artists from the Spotify API.

## Setup
This project's dependencies are managed using `pipenv`.
First, [install pipenv](https://pipenv.pypa.io/en/latest/installation/#installing-pipenv),
and then run:

```bash
pipenv install
```

in the project directory.

Then, create a `.env` file to store the Spotify API
key and secret as environment variables:
```env
SPOTIPY_CLIENT_ID=<client-id>
SPOTIPY_CLIENT_SECRET=<secret>
```

## Running
The project's main file can be run with the command:

```bash
pipenv run python main.py > artists.csv
```
Debugging progress info will be printed to stderr, and
the artists scraped will be printed to stdout in CSV
format (and should be redirected to a file, like
`artists.csv` in the above command).

## Implementation
The Spotify API doesn't provide a direct way to list
all artists. After digging around the documentation,
the best option I found to get artists without already
knowing their ID was the search endpoint. My approach
attempts to extract all artists by recursively building
search terms, starting at single letter search terms
(`a`, `b`, `c`, etc) and recursively combining them
with all other letters until a configured maximum query
length is reached, or the results are below the maximum
search result size of 1000 (the latter indicating that
we have found all artists for that query, and no further
results will be found with subsequent combinations).

For example, if the search term `al` returns fewer than
1000 results, we can move on to `am` without attempting
any more queries that start with `al`.

### Rate limiting
The spotipy library handles automatic retries when it
receives an HTTP 429 (Too Many Requests) response,
and after running this continuously for some time,
I did not run into noticeable rate limiting.

The Spotify API doesn't provide a specific rate limit,
but if they did, my design would have included a
mechanism [such as this package](https://pypi.org/project/ratelimit/)
that would prevent the method which calls the API
from being called too often.

## Results
I was able to scrape over 100,000 unique artists
using this approach in about 15 minutes. According to
[this article](https://routenote.com/blog/how-many-artists-are-on-spotify/),
Spotify has 11,000,000 artists as of Q4 2021. We could
expect to complete this in under 2 days.

### Limitations
* We may miss artists using non-Latin characters in their
name.
* The configured maximum query length limits the depth,
so we may miss artists who do not appear for highly
populated shorter queries.
  * This may be overcome by iterating over smaller year ranges,
  returning only artists who have a release within that year
  range, and allowing iteration over the results with shorter
  queries

### Improvements
* Use a proper CSV writer, like Pandas, and write directly
to a file.
* Use smaller year ranges mentioned above, to allow using
smaller query strings and iterating over decades, for
example