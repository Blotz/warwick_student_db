#/usr/bin/env python3
import datetime
import dataclasses
import argparse
import pathlib
import sys
import os

# Install these requirements:
import requests
import bs4
import xlsxwriter

@dataclasses.dataclass
class Student:
    firstname: str
    lastname: str
    id: int
    type: str
    year: int
    course: str

URL = "https://tabula.warwick.ac.uk/profiles/department/ma/students/"

def request_students(url):
    """
    Request all students from the MA department
    """
    payload={}
    headers = {
    'Cookie': ''
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


def parse_students(student_soup):
    """
    Parse the students from the soup
    """
    # find tbody
    tbody = student_soup.find('tbody')

    if tbody is None:
        print("couldn't find students. try setting a year earlier")
        sys.exit(1)

    # find all rows
    trs = tbody.find_all('tr')
    students = []
    for tr in trs:
        # find all columns
        tds = tr.find_all('td')

        firstname = tds[1].text
        lastname = tds[2].text
        id = tds[3].text
        type = tds[4].text
        year = tds[5].text
        course = tds[6].text

        # create student object
        student = Student(firstname, lastname, id, type, year, course)
        students.append(student)
    return students

def save_to_excel(output_file, students):
    """
    Save the students to an excel document
    """
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})

    # Write some simple text.
    worksheet.write('A1', 'First Name', bold)
    worksheet.write('B1', 'Last Name', bold)
    worksheet.write('C1', 'ID', bold)
    worksheet.write('D1', 'Type', bold)
    worksheet.write('E1', 'Year', bold)
    worksheet.write('F1', 'Course', bold)

    row = 1
    col = 0
    for student in students:
        worksheet.write(row, col, student.firstname)
        worksheet.write(row, col + 1, student.lastname)
        worksheet.write(row, col + 2, student.id)
        worksheet.write(row, col + 3, student.type)
        worksheet.write(row, col + 4, student.year)
        worksheet.write(row, col + 5, student.course)
        row += 1

    workbook.close()

def main():
    currentDate = datetime.date.today()
    current_year = currentDate.year

    argparser = argparse.ArgumentParser(description='Download students from the Warwick Student Database')
    argparser.add_argument('--year', type=int, help='Get all students from specific year', default=current_year)
    argparser.add_argument('--student-year', type=int, help='Get all students in a year')
    argparser.add_argument('--output','-o', type=str, help='Output file', default='./students.xlsx')
    args = argparser.parse_args()

    # parse output file
    # check if path ends in file
    path = pathlib.Path(args.output)
    dir_path = pathlib.Path(os.path.dirname(path))
    
    if not dir_path.exists():
        print("Output directory does not exist")
        sys.exit(1)
    
    if path.suffix != '.xlsx':
        print("Output file must be an excel file")
        sys.exit(1)
    
    # check if file exists
    if os.path.exists(args.output):
        # if it does, ask if we should overwrite
        print("File already exists. Overwrite? (y/n) ", end="")
        if input() != 'y':
            print("Exiting")
            sys.exit(0)

    # format request url
    url = URL + str(args.year) + "?studentsPerPage=10000"
    if args.student_year:
        url = url + "&yearsOfStudy=" + str(args.student_year)
    
    # print(url)
    # request students
    print("Requesting students from " + str(args.year))
    student_data = request_students(url)
    # search for students records
    print("loading students")
    student_soup = bs4.BeautifulSoup(student_data, 'html.parser')
    students = parse_students(student_soup)
    # save to excel documment
    print("Saving to " + args.output)
    save_to_excel(path, students)


if __name__=="__main__":
    main()
