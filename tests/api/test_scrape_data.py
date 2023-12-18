from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from complex_frogs.api import scrape_data
from complex_frogs.database import get_db
from tests.dummy_data import (
    get_test_db,
    scrape_target1,
    scraped_data1,
)

app = FastAPI()
app.include_router(scrape_data.router)
app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)


def test_get_scrape_data():
    response = client.get("/scrape-data/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["title"] == scraped_data1["title"]
    assert data[0]["price"] == scraped_data1["price"]


def test_get_scrape_data_db_error(mocker):
    mocker.patch(
        "complex_frogs.database.crud.read_scrape_data",
        side_effect=SQLAlchemyError,
    )
    response = client.get("/scrape-data/")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["detail"] == "Database error"


def test_get_scrape_data_for_target():
    response = client.get(f"/scrape-data/target/{scrape_target1['id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["title"] == scraped_data1["title"]
    assert data[0]["price"] == scraped_data1["price"]


def test_get_scrape_data_for_target_not_found():
    response = client.get("/scrape-data/target/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Target not found"


def test_get_scrape_data_for_target_db_error(mocker):
    mocker.patch(
        "complex_frogs.database.crud.read_scrape_data_for_target",
        side_effect=SQLAlchemyError,
    )
    response = client.get(f"/scrape-data/target/{scrape_target1['id']}")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["detail"] == "Database error"


def test_get_scrape_data_by_id():
    response = client.get(f"/scrape-data/{scraped_data1['scrape_target_id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == scraped_data1["title"]
    assert data["price"] == scraped_data1["price"]


def test_get_scrape_data_by_id_not_found():
    response = client.get("/scrape-data/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Scrape data not found"


def test_get_scrape_data_by_id_db_error(mocker):
    mocker.patch(
        "complex_frogs.database.crud.read_scrape_data_by_id",
        side_effect=SQLAlchemyError,
    )
    response = client.get(f"/scrape-data/{scraped_data1['scrape_target_id']}")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["detail"] == "Database error"


def test_delete_scrape_data():
    response = client.delete(f"/scrape-data/{scraped_data1['scrape_target_id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_scrape_data_not_found():
    response = client.delete("/scrape-data/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Scrape data not found"


def test_delete_scrape_data_db_error(mocker):
    mocker.patch(
        "complex_frogs.database.crud.delete_scrape_data",
        side_effect=SQLAlchemyError,
    )
    response = client.delete(f"/scrape-data/{scraped_data1['scrape_target_id']}")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["detail"] == "Database error"
