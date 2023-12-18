from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

GET_PAGES_COUNT_URL = 'https://www.linkedin.com/jobs/search?keywords={}&location={}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'

VACANCIES_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={}&location={}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0&start={}'

SPECIFIC_VACANCY = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}?refId={}&trackingId={}'

WRONG_WORDS = ('youtube.com', 'linkedin.com', 'habr.com', 'github.com', 'languages.oup.com', 'wikipedia.org', 'support.google.com')
