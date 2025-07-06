import os
from neo4j.exceptions import Neo4jError

import pytest

from api.dao.auth import AuthDAO
from api.neo4j import get_driver, get_db_name

email = "graphacademy@neo4j.com"
password = "letmein"
name = "Graph Academy"

@pytest.fixture(autouse=True)
def before_all(app):
    with app.app_context():
        driver = get_driver()
        db_name = get_db_name()

        def delete_user(tx):
            return tx.run("MATCH (u:User {email: $email}) DETACH DELETE u", email=email).consume()

        with driver.session() as session:
            session.execute_write(delete_user)
            session.close()

def test_register_user(app):
    with app.app_context():
        driver = get_driver()
        db_name = get_db_name()

        dao = AuthDAO(driver, os.environ.get('JWT_SECRET'), db_name)

        user = dao.register(email, password, name)

        assert user["userId"] is not None
        assert user["name"] == name
        assert "password" not in user
        assert user["userId"] is not None
        assert user["token"] is not None
