from setuptools import setup, find_packages

requires = [
    "flask",
    "spotipy",
    "requests",
    "beautifulsoup4",
    "pandas",
    "google-api-python-client",
    "google-auth",
    "google-auth-oauthlib",
    "google-auth-httplib2",
]

setup(
    name = 'SpotifyToYoutubeMP3',
    version = '1.0',
    description = 'An application that gets your Spotify songs and downloads the YoutubeMP3 version',
    author = 'Brandon Gaona',
    author_email = 'brandon.gaona@outlook.com',
    keywords = 'web flask',
    packages = find_packages(),
    include_package_data = True,
    install_requires = requires
)