from __init__ import CURSOR, CONN

class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee ID: {self.employee_id}>"

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        from employee import Employee  # Local import to avoid circular dependency
        if not Employee.find_by_id(value):
            raise ValueError("Employee ID must reference a valid employee.")
        self._employee_id = value

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances."""
        sql = '''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        '''
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances."""
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        """Save the Review instance to the database."""
        if self.id is None:
            sql = '''
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            '''
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            self.update()
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create and return a new Review instance."""
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Create a Review instance from a database row."""
        review = cls(row[1], row[2], row[3], row[0])
        return review

    @classmethod
    def find_by_id(cls, id):
        """Find a Review instance by its ID."""
        sql = """
            SELECT * FROM reviews WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update an existing Review instance in the database."""
        sql = '''
            UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?
        '''
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the Review instance from the database."""
        sql = """
            DELETE FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Retrieve all Review instances from the database."""
        sql = """
            SELECT * FROM reviews
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Properties with validation

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if not isinstance(year, int) or year < 2000:
            raise ValueError("Year must be an integer and greater than or equal to 2000.")
        self._year = year

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        if not isinstance(summary, str) or len(summary) == 0:
            raise ValueError("Summary must be a non-empty string.")
        self._summary = summary
