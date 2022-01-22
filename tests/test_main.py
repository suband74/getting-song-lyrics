import json
from pathlib import Path

from click.testing import CliRunner
import pytest

from getting_song_lyrics.main import (
    get_lyrics,
    generate_word_cloud,
    get_song_lyrics,
    retrieve_bearer_auth,
)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def data_dir():
    """[Making the string with the full path to the file]"""
    test_data_dir = Path(__file__).resolve().parent
    return test_data_dir


@pytest.fixture
def sample_requests(requests_mock, data_dir):
    """[Make two "requests_mock"]"""
    data_dir = Path(__file__).resolve().parent
    with open(data_dir / "mock_file.json") as content:
        requests_mock.get("http://api.genius.com/search", json=json.load(content))
    with open(data_dir / "mock_file.html") as content:
        requests_mock.get(
            "https://genius.com/Sting-shape-of-my-heart-lyrics",
            content=content.read().encode(),
        )
    return requests_mock


def test_get_lyrics(sample_requests):
    """[Test of the function with the correct arguments]"""
    result = {}

    def write_to_local_variable(lyrics, ouput_path):
        result[ouput_path] = lyrics

    output_path = "some_file.txt"
    get_lyrics("sdkjbsdklfjg", "anything", output_path, write_to_local_variable)

    assert result[output_path] == "He deals the cards as a meditation"


def test_get_lyrics_2(requests_mock, data_dir):
    """[Test of the function with a non-existent song]"""
    with pytest.raises(RuntimeError) as exc:

        with open(data_dir / "response_without_hits.json") as content:
            requests_mock.get("http://api.genius.com/search", json=json.load(content))

        result = {}

        def write_to_local_variable(lyrics, ouput_path):
            result[ouput_path] = lyrics

        output_path = "some_file.txt"
        get_lyrics("sdkjbsdklfjg", "anything", output_path, write_to_local_variable)

    assert ("Nothing found by 'sdkjbsdklfjg'") == str(exc.value)


def test_get_lyrics_3(requests_mock, data_dir):
    """[Test of the function in case of a server error]"""
    with pytest.raises(RuntimeError) as exc:

        with open(data_dir / "response_without_hits.json"):
            requests_mock.get("http://api.genius.com/search", status_code=401)

        result = {}

        def write_to_local_variable(lyrics, ouput_path):
            result[ouput_path] = lyrics

        output_path = "some_file.txt"
        get_lyrics("sdkjbsdklfjg", "anything", output_path, write_to_local_variable)

    assert ("Cannot get response by request with reason None") == str(exc.value)


def test_generate_word_cloud(tmp_path):

    generate_word_cloud("a day in a life", tmp_path / "test.png")

    with open(tmp_path / "test.png", "rb") as file:
        d_content = file.read()

    assert d_content != None


def test_retrieve_bearer_auth_config(tmp_path):
    """[Test for generating an authorization key from a file]"""
    config_path = tmp_path / "cfg.json"
    bearer_expected = "anything"
    with open(config_path, "w") as config:
        json.dump({"bearer_auth": bearer_expected}, config)
    bearer_actual = retrieve_bearer_auth(config_path)
    assert bearer_actual == bearer_expected


def test_retrieve_bearer_auth_env(monkeypatch):
    """[Test for generating an authorization key from an environment variable]"""
    bearer_expected = "anything"
    monkeypatch.setenv("GENIUS_API_BEARER", bearer_expected)
    bearer_actual = retrieve_bearer_auth(None)
    assert bearer_actual == bearer_expected


def test_retrieve_bearer_auth_fail():
    """[Test in the absence of an authorization key]"""
    with pytest.raises(RuntimeError) as exc:
        retrieve_bearer_auth(None)
    assert ("Unable to get bearer auth from environment") == str(exc.value)


def test_main_succeeds(runner: CliRunner, sample_requests, data_dir):
    """[The test of the application with correct data]"""
    result = runner.invoke(
        get_song_lyrics,
        ["anything", "-o", "result.png", "-c", data_dir / "mock_key.json"],
    )

    assert result.exit_code == 0


def test_main_not_succeeds1(runner: CliRunner, data_dir):
    """[The test of the application with an incorrect authorization key]"""
    result = runner.invoke(
        get_song_lyrics, ["anything", "-o", "result.png", "-c", data_dir / "wrong_key.json"]
    )

    assert result.exit_code == 1


def test_main_fail_bearer2(runner: CliRunner):
    """[[The test of the application without an authorization key]"""
    result = runner.invoke(get_song_lyrics, ["anything", "-o", "result.png"])
    assert result.exit_code == 0


def test_main_succeeds(runner: CliRunner, sample_requests, data_dir):
    """[The test of the application with an incorrect output file extension]"""
    result = runner.invoke(
        get_song_lyrics,
        ["anything", "-o", "result.jpg", "-c", data_dir / "mock_key.json"],
    )

    assert result.exit_code == 0
