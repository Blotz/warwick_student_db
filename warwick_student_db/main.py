#/usr/bin/env python3
import asyncio
import dataclasses
import argparse
import pathlib
import sys
import os

# Install these requirements:
import requests
import bs4
import xlsxwriter
import aiohttp

@dataclasses.dataclass
class Student:
    firstname: str
    lastname: str
    id: int
    type: str
    year: int
    course: str
    # optional pronoun
    pronoun: str = ""

BASE_URL = "https://tabula.warwick.ac.uk/"
STUDENT_ENDPOINT = "profiles/department/ma/students/"
STUDENT_PROFILE_ENDPOINT = "profiles/view/"

def request_students(url, cookie):
    """
    Request all students from the MA department
    """
    payload={}
    headers = {
    'Cookie': cookie
    }
    response = requests.request("GET", BASE_URL + url, headers=headers, data=payload)
    return response.text

def parse_pronouns(student_soup):
    """
    Parse the pronouns from the soup
    """
    # find the pronouns
    pronouns_soup = student_soup.find('div', class_='col-xs-12 col-md-7 col-lg-8')

    if pronouns_soup is None:
        return "unknown"
    
    pronouns_text_list = pronouns_soup.text.split('\n')
    
    for pronoun_text in pronouns_text_list:
        if pronoun_text.startswith('Preferred pronouns'):
            return pronoun_text.split(':')[1].strip()
    else:
        return None

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
    worksheet.write('G1', 'Pronouns', bold)

    row = 1
    col = 0
    for student in students:
        worksheet.write(row, col, student.firstname)
        worksheet.write(row, col + 1, student.lastname)
        worksheet.write(row, col + 2, student.id)
        worksheet.write(row, col + 3, student.type)
        worksheet.write(row, col + 4, student.year)
        worksheet.write(row, col + 5, student.course)
        worksheet.write(row, col + 6, student.pronouns)
        row += 1

    workbook.close()

async def request_student_profile(session, student):
    """
    Get the student profile
    """
    url = BASE_URL + STUDENT_PROFILE_ENDPOINT + student.id
    async with session.get(url) as response:
        return await response.text()

async def main():
    argparser = argparse.ArgumentParser(description='Download students from the Warwick Student Database')
    argparser.add_argument('--year', type=int, help='Get all students from specific year', required=True)
    argparser.add_argument('--student-year', type=int, help='Get all students in a year')
    argparser.add_argument('--output','-o', type=str, help='Output file', default=None)
    args, file = argparser.parse_known_args()

    # parse output file
    # Check if file was supplied without the --output flag
    if args.output is None and len(file) > 0:
        args.output = file[0]
    elif args.output is None:
        args.output = "./students.xlsx"
    
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
    url = STUDENT_ENDPOINT + str(args.year) + "?studentsPerPage=10000"
    if args.student_year:
        url = url + "&yearsOfStudy=" + str(args.student_year)
    
    # enter cookie
    print("enter your browser cookie: ", end="")
    cookie = input()
    # print(url)
    # request students
    print("Requesting students from " + str(args.year))
    student_data = request_students(url, cookie)
    # search for students records
    print("loading students")
    student_soup = bs4.BeautifulSoup(student_data, 'html.parser')
    students = parse_students(student_soup)

    # async request student profiles with cookies
    print("requesting student profiles")
    async with aiohttp.ClientSession(headers={'Cookie': cookie}) as session:
        tasks = []
        for student in students:
            tasks.append(request_student_profile(session, student))
        student_profiles = await asyncio.gather(*tasks)
    
    # parse student profiles
    print("parsing student profiles")
    for i in range(len(students)):
        student_soup = bs4.BeautifulSoup(student_profiles[i], 'html.parser')
        students[i].pronouns = parse_pronouns(student_soup)
    
    # save to excel documment
    print("Saving to " + args.output)
    save_to_excel(path, students)



if __name__=="__main__":
    # run main
    asyncio.run(main())
    sys.exit(0)
