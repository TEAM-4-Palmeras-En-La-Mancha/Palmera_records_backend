from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from controller.album_controller import (
    get_all,
    get_by_id,
    create_albums,
    update_album,
    delete_Album,
    get_by_record_label,
)
from model.album_model import Album
from model.artist_model import Artist
from model.genre_model import Genre
from model.record_labels_model import RecordLabel
from schema.album_schema import AlbumCreate, AlbumUpdate



def _db_query(album=None, label=None, genres=None, artists=None):

    def _query(entity):
        q = MagicMock()

        if entity is Album:
            q.filter.return_value.first.return_value = album
        elif entity is RecordLabel:
            q.filter.return_value.first.return_value = label
        elif entity is Genre:
            q.filter.return_value.all.return_value = [] if genres is None else genres
        elif entity is Artist:
            q.filter.return_value.all.return_value = [] if artists is None else artists

        return q

    return _query



def test_get_all_success_happy_path():

    db_mock = MagicMock()
    esperados = [
        Album(id=1, title="Dummy", release_year=2001, label_id=1),
        Album(id=2, title="Nonagon Infinity", release_year=2016, label_id=1),
    ]

    db_mock.query.return_value.offset.return_value.limit.return_value.all.return_value = esperados

    result = get_all(db=db_mock, skip=0, limit=100)

    assert result == esperados
    assert len(result) == 2
    db_mock.query.assert_called_once_with(Album)


def test_get_all_db_error_unhappy_path():

    db_mock = MagicMock()
    db_mock.query.side_effect = SQLAlchemyError("Disco corrupto")

    with pytest.raises(HTTPException) as exc_info:
        get_all(db=db_mock)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in getting albums" in exc_info.value.detail



def test_get_by_id_found_happy_path():

    db_mock = MagicMock()
    esperado = Album(id=1, title="Dummy", release_year=2001, label_id=1)

    db_mock.query.return_value.filter.return_value.first.return_value = esperado

    result = get_by_id(db=db_mock, album_id=1)

    assert result is esperado
    assert result.id == 1
    assert result.title == "Dummy"
    db_mock.query.assert_called_once_with(Album)


def test_get_by_id_not_found_unhappy_path():

    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_by_id(db=db_mock, album_id=999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Album not found"


def test_get_by_id_db_error_unhappy_path():

    db_mock = MagicMock()
    db_mock.query.side_effect = SQLAlchemyError("Error de lectura")

    with pytest.raises(HTTPException) as exc_info:
        get_by_id(db=db_mock, album_id=1)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in getting album" in exc_info.value.detail



def test_create_album_success_happy_path():

    db_mock = MagicMock()

    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    genero = Genre(id=1, name="Rock")
    artista = Artist(id=1, name="Black midi", bio="Banda británica")

    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[genero],
        artists=[artista],
    )

    album_data = AlbumCreate(
        title="Nonagon Infinity",
        release_year=2016,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    result = create_albums(db=db_mock, album_data=album_data)

    db_mock.add.assert_called_once_with(result)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(result)

    assert isinstance(result, Album)
    assert result.title == "Nonagon Infinity"
    assert result.release_year == 2016
    assert result.label_id == 1

    assert result.cover_image_url is None
    assert result.cover_image_public_id is None

    assert list(result.genres) == [genero]
    assert list(result.artists) == [artista]


@patch("controller.album_controller.cloudinary_service.upload_image")
def test_create_album_con_portada_happy_path(mock_upload):

    mock_upload.return_value = {
        "secure_url": "https://res.cloudinary.com/demo/cover.jpg",
        "public_id": "palmeras_records/albums/cover",
    }

    db_mock = MagicMock()
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    genero = Genre(id=1, name="Indie Rock")
    artista = Artist(id=1, name="Arctic Monkeys")

    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[genero],
        artists=[artista],
    )

    album_data = AlbumCreate(
        title="Tranquility Base",
        release_year=2018,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    cover = MagicMock()

    result = create_albums(db=db_mock, album_data=album_data, cover_image=cover)

    mock_upload.assert_called_once_with(
        cover.file,
        folder="palmeras_records/albums",
    )
    assert result.cover_image_url == "https://res.cloudinary.com/demo/cover.jpg"
    assert result.cover_image_public_id == "palmeras_records/albums/cover"
    db_mock.commit.assert_called_once()


def test_create_album_label_not_found_unhappy_path():

    db_mock = MagicMock()
    genero = Genre(id=1, name="Rock")
    artista = Artist(id=1, name="Black midi")

    db_mock.query.side_effect = _db_query(
        label=None,
        genres=[genero],
        artists=[artista],
    )

    album_data = AlbumCreate(
        title="Álbum sin sello",
        release_year=2020,
        label_id=999,
        genre_ids=[1],
        artist_ids=[1],
    )

    with pytest.raises(HTTPException) as exc_info:
        create_albums(db=db_mock, album_data=album_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Label not found"

    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


def test_create_album_genre_not_found_unhappy_path():

    db_mock = MagicMock()
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    artista = Artist(id=1, name="Black midi")

    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[],
        artists=[artista],
    )

    album_data = AlbumCreate(
        title="Álbum sin género",
        release_year=2020,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    with pytest.raises(HTTPException) as exc_info:
        create_albums(db=db_mock, album_data=album_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Genre not found"
    db_mock.commit.assert_not_called()


def test_create_album_artist_not_found_unhappy_path():

    db_mock = MagicMock()
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    genero = Genre(id=1, name="Rock")

    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[genero],
        artists=[],
    )

    album_data = AlbumCreate(
        title="Álbum sin artista",
        release_year=2020,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    with pytest.raises(HTTPException) as exc_info:
        create_albums(db=db_mock, album_data=album_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Artist not found"
    db_mock.commit.assert_not_called()


def test_create_album_db_error_unhappy_path():

    db_mock = MagicMock()
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    genero = Genre(id=1, name="Rock")
    artista = Artist(id=1, name="Black midi")

    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[genero],
        artists=[artista],
    )

    db_mock.commit.side_effect = SQLAlchemyError("Disco lleno")

    album_data = AlbumCreate(
        title="Álbum con fallo",
        release_year=2020,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    with pytest.raises(HTTPException) as exc_info:
        create_albums(db=db_mock, album_data=album_data)

    db_mock.rollback.assert_called_once()

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in creating album" in exc_info.value.detail



def test_update_album_success_happy_path():

    db_mock = MagicMock()
    existente = Album(id=1, title="Dummy", release_year=2001, label_id=1)
    db_mock.query.return_value.filter.return_value.first.return_value = existente

    update_data = AlbumUpdate(title="Dummy (Edición Expandida)", release_year=2004)

    result = update_album(db=db_mock, album_id=1, album_data=update_data)

    assert result is existente
    assert result.title == "Dummy (Edición Expandida)"
    assert result.release_year == 2004
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(existente)
    db_mock.rollback.assert_not_called()


def test_update_album_label_happy_path():

    db_mock = MagicMock()
    existente = Album(id=1, title="Dummy", release_year=2001, label_id=1)
    sello_nuevo = RecordLabel(id=2, name="4AD", country="United Kingdom")

    db_mock.query.side_effect = _db_query(album=existente, label=sello_nuevo)

    update_data = AlbumUpdate(label_id=2, title="Dummy (Reedición 4AD)")

    result = update_album(db=db_mock, album_id=1, album_data=update_data)

    assert result.label_id == 2
    assert result.title == "Dummy (Reedición 4AD)"
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(existente)


def test_update_album_not_found_unhappy_path():

    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    update_data = AlbumUpdate(title="Título Nuevo")

    with pytest.raises(HTTPException) as exc_info:
        update_album(db=db_mock, album_id=999, album_data=update_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Album not found"
    db_mock.commit.assert_not_called()


def test_update_album_label_not_found_unhappy_path():

    db_mock = MagicMock()
    existente = Album(id=1, title="Dummy", release_year=2001, label_id=1)

    db_mock.query.side_effect = _db_query(album=existente, label=None)

    update_data = AlbumUpdate(label_id=999)

    with pytest.raises(HTTPException) as exc_info:
        update_album(db=db_mock, album_id=1, album_data=update_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Record label not found"
    db_mock.commit.assert_not_called()


def test_update_album_db_error_unhappy_path():

    db_mock = MagicMock()
    existente = Album(id=1, title="Dummy", release_year=2001, label_id=1)
    db_mock.query.return_value.filter.return_value.first.return_value = existente

    db_mock.commit.side_effect = SQLAlchemyError("Conexión perdida")

    update_data = AlbumUpdate(title="Título Nuevo")

    with pytest.raises(HTTPException) as exc_info:
        update_album(db=db_mock, album_id=1, album_data=update_data)

    db_mock.rollback.assert_called_once()

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in updating album" in exc_info.value.detail



def test_delete_album_success_happy_path():

    db_mock = MagicMock()
    existente = Album(
        id=1,
        title="Álbum a borrar",
        release_year=2020,
        label_id=1,
        cover_image_public_id=None,
    )
    db_mock.query.return_value.filter.return_value.first.return_value = existente

    result = delete_Album(db=db_mock, album_id=1)

    assert result is None
    db_mock.delete.assert_called_once_with(existente)
    db_mock.commit.assert_called_once()
    db_mock.rollback.assert_not_called()


@patch("controller.album_controller.cloudinary_service.delete_image")
def test_delete_album_con_portada_happy_path(mock_delete):

    db_mock = MagicMock()
    existente = Album(
        id=1,
        title="Álbum con portada",
        release_year=2020,
        label_id=1,
        cover_image_public_id="palmeras_records/albums/cover",
    )
    db_mock.query.return_value.filter.return_value.first.return_value = existente

    result = delete_Album(db=db_mock, album_id=1)

    mock_delete.assert_called_once_with("palmeras_records/albums/cover")
    assert result is None
    db_mock.delete.assert_called_once_with(existente)
    db_mock.commit.assert_called_once()


def test_delete_album_not_found_unhappy_path():

    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_Album(db=db_mock, album_id=999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Album not found"
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_album_db_error_unhappy_path():

    db_mock = MagicMock()
    existente = Album(
        id=1,
        title="Álbum con fallo",
        release_year=2020,
        label_id=1,
        cover_image_public_id=None,
    )
    db_mock.query.return_value.filter.return_value.first.return_value = existente
    db_mock.commit.side_effect = SQLAlchemyError("Disco lleno")

    with pytest.raises(HTTPException) as exc_info:
        delete_Album(db=db_mock, album_id=1)

    db_mock.rollback.assert_called_once()

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in deleting album" in exc_info.value.detail



def test_get_by_record_label_success_happy_path():

    db_mock = MagicMock()
    esperados = [
        Album(id=1, title="Dummy", release_year=2001, label_id=1),
        Album(id=2, title="Nonagon Infinity", release_year=2016, label_id=1),
    ]
    db_mock.query.return_value.filter.return_value.all.return_value = esperados

    result = get_by_record_label(db=db_mock, label_id=1)

    assert result == esperados
    assert len(result) == 2
    db_mock.query.assert_called_once_with(Album)


def test_get_by_record_label_db_error_unhappy_path():

    db_mock = MagicMock()
    db_mock.query.side_effect = SQLAlchemyError("Error de red")

    with pytest.raises(HTTPException) as exc_info:
        get_by_record_label(db=db_mock, label_id=1)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in fetching albums" in exc_info.value.detail
