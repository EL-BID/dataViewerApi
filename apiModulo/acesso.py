import psycopg2 

class Acesso:
    def __init__(self, host, user, database, p):
        self.host = host
        self.user = user
        self.database = database
        self.p = p

        self.connection = psycopg2.connect(user=self.user,
                                  password=self.p,
                                  host=self.host,
                                  port="5432",
                                  database=self.database)

    
    def getConnection(self):
        return self.connection



