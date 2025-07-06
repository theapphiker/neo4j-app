import pytest

from api.neo4j import get_driver, get_db_name
from api.dao.genres import GenreDAO

def test_return_list_of_genres(app):
    with app.app_context():
        # Get Neo4j Driver
        driver = get_driver()
        db_name = get_db_name()

        # Create DAO
        dao = GenreDAO(driver, db_name)

        # Get all genres
        output = dao.all()

        assert len(output) is 19
        assert output[0]["name"] == "Action"
        assert output[18]["name"] == "Western"

        print("Here is the answer to the quiz question on the lesson:")
        print("Which genre has the highest movie count?")
        print("Copy and paste the following answer into the text box: \n\n")

        output.sort(key=lambda genre: genre["movies"], reverse=True)

        print(output[0]["name"])

