from __init__ import CURSOR, CONN

class Review:

    all = {}

    def __init__(self, content, rating, employee_id, id=None):
        self.id = id
        self.content = content
        self.rating = rating
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: Rating {self.rating} for Employee {self.employee_id}>"

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str) and len(value.strip()) > 0:
            self._content = value.strip()
        else:
            raise ValueError("Content must be a non-empty string")

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if isinstance(value, (int, float)) and 1 <= value <= 5:
            self._rating = value
        else:
            raise ValueError("Rating must be a number between 1 and 5")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if isinstance(value, int) or value is None:
            self._employee_id = value
        else:
            raise ValueError("Employee ID must be an integer or None")

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                content TEXT,
                rating REAL,
                employee_id INTEGER,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        sql = """
            INSERT INTO reviews (content, rating, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.content, self.rating, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, content, rating, employee_id):
        review = cls(content, rating, employee_id)
        review.save()
        return review

    def update(self):
        sql = """
            UPDATE reviews
            SET content = ?, rating = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.content, self.rating, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in type(self).all:
            del type(self).all[self.id]
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        if row is None:
            return None
        review = cls.all.get(row[0])
        if review:
            review.content = row[1]
            review.rating = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3], id=row[0])
            cls.all[review.id] = review
        return review

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def find_by_employee_id(cls, employee_id):
        sql = "SELECT * FROM reviews WHERE employee_id = ?"
        rows = CURSOR.execute(sql, (employee_id,)).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def employee(self):
        from employee import Employee
        return Employee.find_by_id(self.employee_id)


