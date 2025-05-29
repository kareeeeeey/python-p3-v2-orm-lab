from __init__ import CURSOR, CONN

class Employee:
    all = {}

    def __init__(self, name, position, department_id, id=None):
        self.id = id
        self.name = name
        self.position = position
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.position}, Dept {self.department_id}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str) and len(value.strip()) > 0:
            self._name = value.strip()
        else:
            raise ValueError("Name must be a non-empty string")

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if isinstance(value, str) and len(value.strip()) > 0:
            self._position = value.strip()
        else:
            raise ValueError("Position must be a non-empty string")

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if isinstance(value, int) or value is None:
            self._department_id = value
        else:
            raise ValueError("Department ID must be an integer or None")

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                position TEXT,
                department_id INTEGER,
                FOREIGN KEY(department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees;")
        CONN.commit()

    def save(self):
        sql = """
            INSERT INTO employees (name, position, department_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.position, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, position, department_id):
        employee = cls(name, position, department_id)
        employee.save()
        return employee

    def update(self):
        sql = """
            UPDATE employees
            SET name = ?, position = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.position, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in type(self).all:
            del type(self).all[self.id]
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        if row is None:
            return None
        employee = cls.all.get(row[0])
        if employee:
            employee.name = row[1]
            employee.position = row[2]
            employee.department_id = row[3]
        else:
            employee = cls(row[1], row[2], row[3], id=row[0])
            cls.all[employee.id] = employee
        return employee

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM employees").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM employees WHERE id = ?", (id,)).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute("SELECT * FROM employees WHERE name = ?", (name,)).fetchone()
        return cls.instance_from_db(row)

    def department(self):
        from department import Department
        return Department.find_by_id(self.department_id)

