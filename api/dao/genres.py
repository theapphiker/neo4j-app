from api.data import genres
from api.exceptions.notfound import NotFoundException

class GenreDAO:
    """
    The constructor expects an instance of the Neo4j Driver, which will be
    used to interact with Neo4j.
    """
    def __init__(self, driver, db_name):
        self.driver=driver
        self.db_name=db_name

    # tag::all[]
    def all(self):
        # Define a unit of work to Get a list of Genres
        def get_movies(tx):
            result = tx.run("""
                MATCH (g:Genre)
                WHERE g.name <> '(no genres listed)'
                CALL {
                    WITH g
                    MATCH (g)<-[:IN_GENRE]-(m:Movie)
                    WHERE m.imdbRating IS NOT NULL AND m.poster IS NOT NULL
                    RETURN m.poster AS poster
                    ORDER BY m.imdbRating DESC LIMIT 1
                }
                RETURN g {
                    .*,
                    movies: count { (g)<-[:IN_GENRE]-(:Movie) },
                    poster: poster
                } AS genre
                ORDER BY g.name ASC
            """)

            return [ g.value(0) for g in result ]

        # Open a new session
        with self.driver.session(database=self.db_name) as session:
            # Execute within a Read Transaction
            return session.execute_read(get_movies)


    """
    This method should find a Genre node by its name and return a set of properties
    along with a `poster` image and `movies` count.

    If the genre is not found, a NotFoundError should be thrown.
    """
    # tag::find[]
    def find(self, name):
        # TODO: Open a new session
        # TODO: Define a unit of work to find the genre by it's name
        # TODO: Execute within a Read Transaction

        return [g for g in genres if g["name"] == name][0]
    # end::find[]