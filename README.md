# warwick_student_db
Python script to download maths student data from the Warwick Student Database

This isnt a public tool and requires you to pass your browser cookie from your valid account to access the data

use with caution

```bash
pip install https://github.com/Blotz/warwick_student_db.git
python -m warwick_student_db --help
```

```bash
$ python -m warwick_student_db --help
usage: __main__.py [-h] --year YEAR [--student-year STUDENT_YEAR] [--output OUTPUT]

Download students from the Warwick Student Database

options:
  -h, --help            show this help message and exit
  --year YEAR           Get all students from specific year
  --student-year STUDENT_YEAR
                        Get all students in a year
  --output OUTPUT, -o OUTPUT
                        Output file
```
```bash
$ python -m warwick_student_db --year 2021 
enter your browser cookie: COOKIE_FROM_BROWSER
Requesting students from 2021
loading students
requesting student profiles
parsing student profiles
Saving to ./students.xlsx
```
