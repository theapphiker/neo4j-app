from api.data import popular, goodfellas
from api.exceptions.notfound import NotFoundException

class FavoriteDAO:
    """
    The constructor expects an instance of the Neo4j Driver, which will be
    used to interact with Neo4j.
    """
    def __init__(self, driver, db_name):
        self.driver=driver
        self.db_name=db_name


    """
    This method should retrieve a list of movies that have an incoming :HAS_FAVORITE
    relationship from a User node with the supplied `userId`.

    Results should be ordered by the `sort` parameter, and in the direction specified
    in the `order` parameter.

    Results should be limited to the number passed as `limit`.
    The `skip` variable should be used to skip a certain number of rows.
    """
    def all(self, user_id, sort = 'title', order = 'ASC', limit = 6, skip = 0):
        # Retrieve a list of movies favorited by the user
        with self.driver.session(database=self.db_name) as session:
            movies = session.execute_read(lambda tx: tx.run("""
                MATCH (u:User {{userId: $userId}})-[r:HAS_FAVORITE]->(m:Movie)
                RETURN m {{
                    .*,
                    favorite: true
                }} AS movie
                ORDER BY m.`{0}` {1}
                SKIP $skip
                LIMIT $limit
            """.format(sort, order), userId=user_id, limit=limit, skip=skip).value("movie"))

            return movies

    """
    This method should create a `:HAS_FAVORITE` relationship between
    the User and Movie ID nodes provided.
   *
    If either the user or movie cannot be found, a `NotFoundError` should be thrown.
    """
    def add(self, user_id, movie_id):
    # Define a new transaction function to create a HAS_FAVORITE relationship
        def add_to_favorites(tx, user_id, movie_id):
            row = tx.run("""
                MATCH (u:User {userId: $userId})
                MATCH (m:Movie {tmdbId: $movieId})
                MERGE (u)-[r:HAS_FAVORITE]->(m)
                ON CREATE SET u.createdAt = datetime()
                RETURN m {
                    .*,
                    favorite: true
                } AS movie
            """, userId=user_id, movieId=movie_id).single()

            # If no rows are returnedm throw a NotFoundException
            if row == None:
                raise NotFoundException()

            return row.get("movie")

        with self.driver.session(database=self.db_name) as session:
            return session.execute_write(add_to_favorites, user_id, movie_id)

    """
    This method should remove the `:HAS_FAVORITE` relationship between
    the User and Movie ID nodes provided.

    If either the user, movie or the relationship between them cannot be found,
    a `NotFoundError` should be thrown.
    """
    def remove(self, user_id, movie_id):
        def remove_from_favorites(tx, user_id, movie_id):
            row = tx.run("""
                MATCH (u:User {userId: $userId})-[r:HAS_FAVORITE]->(m:Movie {tmdbId: $movieId})
                DELETE r
                RETURN m {
                    .*,
                    favorite: false
                } AS movie
            """, userId=user_id, movieId=movie_id).single()

            # If no rows are returnedm throw a NotFoundException
            if row == None:
                raise NotFoundException()

            return row.get("movie")

        # Execute the transaction function within a Write Transaction
        with self.driver.session(database=self.db_name) as session:
            # Return movie details and `favorite` property
            return session.execute_write(remove_from_favorites, user_id, movie_id)