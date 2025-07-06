import pytest

from api.neo4j import get_driver, get_db_name
from api.dao.ratings import RatingDAO

movie = '769'
user = '1185150b-9e81-46a2-a1d3-eb649544b9c4'
email = 'graphacademy.reviewer@neo4j.com'
rating = 5

@pytest.fixture(autouse=True)
def before_all(app):
    with app.app_context():
        driver = get_driver()
        db_name = get_db_name()

        def merge_data(tx):
            return tx.run("""
            MERGE (u:User {userId: $user})
            SET u.email = $email
            MERGE (m:Movie {tmdbId: $movie})
            """, user=user, movie=movie, email=email).consume()

        with driver.session(database=db_name) as session:
            session.execute_write(merge_data)
            session.close()

def test_store_integer(app):
    with app.app_context():
        driver = get_driver()
        db_name = get_db_name()

        dao = RatingDAO(driver, db_name)

        output = dao.add(user, movie, rating)

        assert output["tmdbId"] == movie
        assert output["rating"] is rating


