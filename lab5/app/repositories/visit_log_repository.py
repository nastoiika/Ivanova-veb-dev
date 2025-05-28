class VisitLogRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.page_size = 10

    def add(self, path, user_id=None):
        with self.db_connector.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO visit_logs (path, user_id, created_at) VALUES (%s, %s, NOW());",
                    (path, user_id)
                )
                connection.commit()

    def all(self):
        with self.db_connector.connect() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM visit_logs ORDER BY created_at DESC;")
                visits = cursor.fetchall()
        return visits

    def get_by_user_id(self, user_id):
        with self.db_connector.connect() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT * FROM visit_logs WHERE user_id = %s ORDER BY created_at DESC;",
                    (user_id,)
                )
                visits = cursor.fetchall()
        return visits

    def get_paginated(self, page):
        offset = (page - 1) * self.page_size
        with self.db_connector.connect() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT visit_logs.*, 
                        CONCAT(users.last_name, ' ', users.first_name, ' ', COALESCE(users.middle_name, '')) AS full_name
                    FROM visit_logs
                    LEFT JOIN users ON visit_logs.user_id = users.id
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s;
                """, (self.page_size, offset))
                return cursor.fetchall()

    def count_all(self):
        with self.db_connector.connect() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM visit_logs;")
                return cursor.fetchone()["total"]
    
    def count_by_pages(self):
        with self.db_connector.connect() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT path, COUNT(*) AS visit_count
                    FROM visit_logs
                    GROUP BY path
                    ORDER BY visit_count DESC;
                """)
                return cursor.fetchall()
            
    def count_by_users(self):
        with self.db_connector.connect() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT 
                        users.id,
                        CONCAT(users.last_name, ' ', users.first_name, ' ', COALESCE(users.middle_name, '')) AS full_name,
                        COUNT(visit_logs.id) AS visit_count
                    FROM visit_logs
                    LEFT JOIN users ON users.id = visit_logs.user_id
                    GROUP BY visit_logs.user_id
                    ORDER BY visit_count DESC;
                """)
                return cursor.fetchall()
