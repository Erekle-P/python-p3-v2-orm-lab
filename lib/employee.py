from __init__ import CURSOR, CONN
from department import Department

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department ID: {self.department_id}>"

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Employee instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Employee instances."""
        sql = """
            DROP TABLE IF EXISTS employees;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def reviews(self):
        from review import Review  # Local import to avoid circular dependency
        CURSOR.execute("SELECT * FROM reviews WHERE employee_id = ?", (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]

    @classmethod
    def create(cls, name, job_title, department_id):
        """Create and return a new Employee instance."""
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def save(self):
        """Save the Employee instance to the database."""
        sql = """
            INSERT INTO employees (name, job_title, department_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        self.id = CURSOR.lastrowid
        CONN.commit()

    @classmethod
    def instance_from_db(cls, row):
        """Create an Employee instance from a database row."""
        employee = cls(row[1], row[2], row[3], row[0])
        return employee

    @classmethod
    def find_by_id(cls, id):
        """Find an Employee instance by its ID."""
        sql = """
            SELECT * FROM employees WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Find an Employee instance by its name."""
        sql = """
            SELECT * FROM employees WHERE name = ?
        """
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update an existing Employee instance in the database."""
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the Employee instance from the database."""
        sql = """
            DELETE FROM employees WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        # After deletion, clear object attributes to reflect the state of the deleted object
        self.id = None
        self.name = None
        self.job_title = None
        self.department_id = None

    @classmethod
    def get_all(cls):
        """Retrieve all Employee instances from the database."""
        sql = """
            SELECT * FROM employees
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Properties with validation

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str) or len(name) == 0:
            raise ValueError("Name must be a non-empty string")
        self._name = name

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, job_title):
        if not isinstance(job_title, str) or len(job_title) == 0:
            raise ValueError("Job title must be a non-empty string")
        self._job_title = job_title

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, department_id):
        from department import Department  # Local import to avoid circular dependency
        if not isinstance(department_id, int) or department_id <= 0 or not Department.find_by_id(department_id):
            raise ValueError("Department ID must be a valid positive integer referring to an existing department.")
        self._department_id = department_id
