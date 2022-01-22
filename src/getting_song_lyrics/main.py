import json
import os
import pathlib
import typing

from bs4 import BeautifulSoup

import click

import numpy as np

import requests

from wordcloud import WordCloud

BEARER_ENV = "GENIUS_API_BEARER"


def write_lyrics_to_file(lyrics: str, file_out:pathlib.Path) -> None:
    """[recording the lyrics to the output_file.txt]

    Args:
        lyrics ([str]): [description]
        file_out (typing.Optional[pathlib.Path]): [description]
    """
    with open(file_out, "w") as file:
        file.write(lyrics)


def generate_word_cloud(lyrics: str, file_out: pathlib.Path) -> None:
    """[converting text to a word cloud,
        recording to the output_file.png]

    Args:
        lyrics ([str]): [description]
        file_out (typing.Optional[pathlib.Path]): [description]
    """
    x, y = np.ogrid[:400, :400]
    mask = (x - 200) ** 2 + (y - 200) ** 2 > 190 ** 2
    mask = mask.astype(int)
    wc = WordCloud(background_color="white", repeat=True, mask=255*mask)
    wc.generate(lyrics)
    wc.to_file(file_out)


def get_lyrics(
    search_str: str,
    bearer: str,
    output_path: pathlib.Path,
    callback: typing.Callable[[str, pathlib.Path], None],
) -> None:

    """[Authorization, requesting data, receiving and processing the server response,
        parsing a web page, recording the lyrics to a file]

    Raises:
        RuntimeError: [description]
        RuntimeError: [description]
    """

    header_authorization = {"Authorization": f"Bearer {bearer}"}
    genius_search_url = "http://api.genius.com/search"
    response = requests.get(
        genius_search_url,
        params={"q": search_str},
        headers=header_authorization,
    )
    if not response:
        raise RuntimeError(
            f"Cannot get response by request with reason {response.reason}"
        )

    data = response.json()
    hits = data["response"].get("hits")
    if hits is None:
        raise RuntimeError(f"Nothing found by '{search_str}'")

    url_lyrics = hits[0]["result"]["url"]

    # TODO explain why do we need it
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,\
         image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101\
         Firefox/94.0",
    }
    lyrics_response = requests.get(url_lyrics, headers=headers)
    soup = BeautifulSoup(lyrics_response.content, "html.parser")

    lyrics = "".join(
        tag.get_text(strip=True, separator="\n")
        for tag in soup.select('div[class^="Lyrics__Container"], .song_body-lyrics p')
    )
    callback(lyrics, output_path)


def retrieve_bearer_auth(config: typing.Optional[pathlib.Path]) -> str:
    """[Getting the authorization key from the file or from the command line option]

    Args:
        config (typing.Optional[pathlib.Path]): [file with authorization key]

    Raises:
        RuntimeError: [description]

    Returns:
        str: [authorization key]
    """
    if config:
        with open(config) as config_file:
            content = json.load(config_file)
            bearer = content["bearer_auth"]
    else:
        bearer = os.getenv(BEARER_ENV)
        if not bearer:
            raise RuntimeError("Unable to get bearer auth from environment")
    return bearer


@click.command()
@click.argument(
    "search_query",
)
@click.option(
    "-o",
    "--output-path",
    type=click.Path(writable=True, path_type=pathlib.Path),
    required=True,
    prompt="Enter the file to record result please",
)
@click.option(
    "-c",
    "--config-path",
    type=click.Path(exists=True, path_type=pathlib.Path),
)
def get_song_lyrics(
    search_query: str,
    output_path: pathlib.Path,
    config_path: typing.Optional[pathlib.Path],
) -> int:
    """[Generating the key for authorization on the site "Genius.com",
        checking the correct extension for the output file,
        ]

    Args:
        search_query (str): [The name of the song, the name of the artist, any words from the song]
        output_path (typing.Optional[pathlib.Path]): [The name of the file with the result]
        config_path (typing.Optional[pathlib.Path]): [The name of the file with the authorization key]

    Returns:
        [type]: [description]
    """
    try:
        bearer = retrieve_bearer_auth(config_path)
    except Exception as exc:
        msg = (
            "Genius API Bearer required. "
            f"Fill {BEARER_ENV} as environment variable or pass config option. "
            f"Exception caught: {exc}"
        )
        click.secho(msg, fg="red", bold=True)
        return 1

    process_by_extension = {
        ".png": generate_word_cloud,
        ".txt": write_lyrics_to_file,
    }
    callback = process_by_extension.get(output_path.suffix)
    if callback is None:
        click.secho(
            f"Unsupported extension {output_path.suffix}. Supported: {', '.join(process_by_extension.keys())}"
        )
        return 1

    get_lyrics(search_query, bearer, output_path, callback)
    return 0


if __name__ == "__main__":
    exit(get_song_lyrics())
