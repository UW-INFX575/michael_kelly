from lxml import html
import requests
import re
import pandas as pd
import csv

'''
This script scrapes faculty data from:
    Azusa Pacific University (http://www.apu.edu/clas/faculty)
    Georgian Court University (http://www.georgian.edu/faculty/list.htm)
    William & Mary University - Law School (http://law2.wm.edu/faculty/bios/fulltime/)

Produces a CSV file with the following fields for each professor:
            professors.append([firstname, lastname, grad_school, grad_school_code, highest_degree, grad_year,
                               university, university_code, title, department])
    firstname 
    lastname 
    grad_school = university where he/she earned highest degree
    grad_school_code = identifier code for grad school university
    highest_degree = highest degree earned (e.g. Ph.D.)
    grad_year = year that professor earned highest degree
    university = current university
    university_code = identifier code for current university
    title = title at current university (e.g. Assistant Professor)
    department = current department
'''

# Load schools data for reference and matching
schools_file = csv.DictReader(open('schools.csv'))
schools = []
for row in schools_file:
    school_id = int(row['id'])
    school_name = row['name']
    schools.append({'id':school_id, 'name':school_name})


def getFacultyAPU():
    professors = []

    # Faculty directory page
    rootURL = 'http://www.apu.edu'
    directoryPage = requests.get(rootURL + '/clas/faculty')
    directoryTree = html.fromstring(directoryPage.text)

    # Get links to all professors (exclude deans)
    links = directoryTree.xpath('//*[@id="template-page-content"]/ul[position() > 2]/li/a[2]/@href')
    titles = directoryTree.xpath('//*[@id="template-page-content"]/ul[position() > 2]/li/div[@class="title"]/text()')

    urls = map(lambda x: rootURL + x, links)

    # Go through each faculty page
    for i, url in enumerate(urls):
        facultyPage = requests.get(url)
        facultyTree = html.fromstring(facultyPage.text)
        
        # FIRSTNAME, LASTNAME
        fullTitle = facultyTree.xpath('//*[@id="template-page-content"]/div/div[1]/div[@class="contact"]/h2/text()')
        fullTitle = [x.strip() for x in fullTitle[0].split(',')]
        
        name = fullTitle.pop(0) # Remove degree from name
        name = re.sub('([A-Z]\.)+ ', '', name) # Remove intitials (middle name)
        name = re.sub('([\(\']\w*[\)\']) ', '', name)  # Remove word in parentheses or quotes (nickname)
        name = name.split(' ') # Split first and last name
        firstname = name[0]
        lastname = name[-1]
        
        # TITLE
        title = titles[i].split(',', 1)[0] # Faculty title comes before comma
        
        # UNVIVERSITY
        university = 'Azusa Pacific University'
        university_code = None # code for this university not yet created
        
        # DEPARTMENT
        department = facultyTree.xpath('//*[@id="template-page-content"]/div/div[1]/div[2]/text()')
        try:
            # Try to get department from below name
            department = '|'.join(department)
            department = re.search('Department of ([^\'\|]+)\|', department).group(1)
        except AttributeError:
            # If that didn't exist, look for the department section below bio
            department = facultyTree.xpath('//*[@id="template-page-content"]/div/div[2]/div[@class="sdepartment"]/ul/li/text()')
            department = department[0] if len(department) > 0 else ''
        
        # GRAD SCHOOL & DEGREE
        
        # Determine which line represents highest education
        # PhDs may list there education reverse chronologically or chronologically
        education_first = facultyTree.xpath('//*[@id="template-page-content"]/div/div[2]/ul[1]/li[1]/text()')
        education_last = facultyTree.xpath('//*[@id="template-page-content"]/div/div[2]/ul[1]/li[last()]/text()')

        # Initiate variables with default/null values
        highest_degree = None
        grad_school = None
        grad_school_code = None
        grad_year = ''
        
        # Degree might be in the Fulltitle text extracted above 
        highest_degree = ','.join(fullTitle) or None
        
        # Parse education items for faculty member
        # Most but not all faculty list education in reverse chronology
        # Check if highest degree is at bottom of list
        if len(education_first) > 0:
            if re.compile(r'(Ph.D.)').search(education_last[0]) is not None:
                education_highest = education_last[0]
            else:
                education_highest = education_first[0]
            
            # Split string and parse for degree and school
            # A few pages use dashes instead of commas to seperate degree. Replace with comma:
            education_highest = education_highest.replace('. - ', '. , ')
            # Split on comma to get main parts
            education_highest = [x.strip() for x in education_highest.split(',')]
            highest_degree = education_highest.pop(0) # Degree is always first
            highest_degree = highest_degree.split(' ')[0] # Take first degree title in case there are multiple

            # Get the school name NOT the year, deartment, or specialization
            temp_grad_school = None
            for text in education_highest:
                
                match_year = re.match('[0-9]{4}', text)
                grad_year = match_year.group(0) if match_year else ''
                
                # Look for school in the existing records
                for school in schools:
                    if school['name'].split(',', 1)[0] in text:
                        grad_school = school['name']
                        grad_school_code = int(school['id'])
                
                # Otherwise try to extract the school name from the line
                if grad_school == None:
                    if re.compile(r'([\d]+)').search(text) is None: # ensure not year
                        # If we already have the school and the next piece looks like a city, include it
                        if len(text.split()) < 3 and temp_grad_school is not None:
                            temp_grad_school = temp_grad_school + ', ' + text
                        # If it looks like a school name grab the text
                        if re.compile(r'University|College|School|Seminary|Institute').search(text) is not None:
                            temp_grad_school = text
                            # Specialization may be in front of the school name. Remove it
                            temp_grad_school = re.sub('(^.+\- )', '', temp_grad_school)
                    # Assign the grad school if it was found
                    grad_school = temp_grad_school or None
        
        # Insert into records only if degree and grad school were found
        if highest_degree != None and grad_school != None:
            professors.append([firstname, lastname, grad_school, grad_school_code, highest_degree, grad_year,
                            university, university_code, title, department])
    
    return professors



def getFacultyGCU():
    professors = []

    # Faculty directory page
    rootURL = 'http://www.georgian.edu'
    directoryPage = requests.get(rootURL + '/faculty/list.htm')
    directoryTree = html.fromstring(directoryPage.text)

    # Get links to all professors (exclude deans)
    links = directoryTree.xpath('//*[@id="ctl00_ContentPlaceHolder1_fac_list"]/div[@class="fac_item dontsplit"]/a[1]/@href')
    names = directoryTree.xpath('//*[@id="ctl00_ContentPlaceHolder1_fac_list"]/div[@class="fac_item dontsplit"]/a[1]/text()')
    titles = directoryTree.xpath('//*[@id="ctl00_ContentPlaceHolder1_fac_list"]/div[@class="fac_item dontsplit"]/text()[preceding-sibling::br][1]')

    urls = map(lambda x: rootURL + x, links)

    # Go through each faculty page
    for i, url in enumerate(urls):
        facultyPage = requests.get(url)
        facultyTree = html.fromstring(facultyPage.text)
        
        # FIRSTANAME, LASTNAME
        lastname, firstname = names[i].split(',')

        # TITLE
        title = titles[i]
        
        # UNIVERSITY
        university = 'Georgian Court University'
        university_code = None
        
        # DEPARTMENT
        department_text = facultyTree.xpath('//table[@class="tbl_staff_profile"]/tr/td[contains(., "Dept/School")]/text()[preceding-sibling::br]')
        # Department section may or may not exist
        if len(department_text) > 0:
            department = department_text[0]
        else:
            break

        # GRAD SCHOOL & DEGREE
        education_full = facultyTree.xpath('//*[@id="ctl00_ContentPlaceHolder1_ContentBlock1"]/div/ul[1]/li/text()')
        
        # Initiate variables with default/null values
        education_phd = None
        highest_degree = None
        grad_school = None
        grad_school_code = None
        
        # Check for variations in spelling and style for doctorate degree
        # Those without a doctorate will be ignored in order to exclude listed staff
        # who are not professsors
        regexp_phd = re.compile(r'Ph\.D\.|PhD|Doctor|Ed\.D')
        regexp_edd = re.compile(r'Ed\.D')
        for line in education_full:
            if regexp_phd.search(line) is not None:
                highest_degree = 'Ph.D.'
                education_phd = line
                break
            elif regexp_edd.search(line) is not None:
                highest_degree = 'Ed.D'
                education_phd = line
                break
        
        if education_phd != None:
            # Check for year of graduating
            match_year = re.match('[0-9]{4}', education_phd)
            grad_year = match_year.group(0) if match_year else ''
            
            # Look for school in the existing records
            for school in schools:
                if school['name'].split(',', 1)[0] in education_phd:
                    grad_school = school['name']
                    grad_school_code = int(school['id'])
            
            # Otherwise try to extract the school name from the line
            if grad_school == None:
                match_school = re.match('(?:,|^)(\D*(University|College|School|Seminary|Institute).*)(?:,|\n)', education_phd)
                grad_school = match_school.group(0) if match_school else None
        
        # Insert into records only if degree and grad school were found
        if highest_degree != None and grad_school != None:
            professors.append([firstname, lastname, grad_school, grad_school_code, highest_degree, grad_year,
                           university, university_code, title, department])
    return professors

def getFacultyWM():
    professors = []

    # Faculty directory page
    rootURL = 'http://law2.wm.edu'
    directoryPage = requests.get(rootURL + '/faculty/bios/fulltime/?svr=1')
    directoryTree = html.fromstring(directoryPage.text)

    # Get links to all professors (exclude deans)
    urls = directoryTree.xpath('//*[@id="main"]/div/div[2]/div[@class="oneperson"]/div[2]/a/@href')
    names = directoryTree.xpath('//*[@id="main"]/div/div[2]/div[@class="oneperson"]/div[2]/a/h5/text()')
    
    # Go through each faculty page
    for i, url in enumerate(urls):
        
        # Deafult empty values
        firstname, lastname, grad_school, grad_school_code = ['']*4
        highest_degree, grad_year, university, university_code = ['']*4
        title, department = ['']*2
        
        facultyPage = requests.get(url)
        facultyTree = html.fromstring(facultyPage.text)
        
        # FIRSTANAME, LASTNAME
        fullname = names[i].split(',')[0]
        fullname = fullname.split()
        firstname = fullname[0]
        lastname = fullname[-1] 
        
        # UNIVERSITY
        university = 'William & Mary University'
        university_code = 359

        # DEPARTMENT
        department = 'Law School'
        
        # GRAD SCHOOL & DEGREE
        education_full = facultyTree.xpath('//*[@id="main"]/div/div/div[1]/div[2]/div/text()[following-sibling::br][2]')
        match = re.match('\: ([^,]+), ([^;]+);', education_full[0])
        highest_degree = match.group(1)
        university = match.group(2)
        
        # Insert into records
        professors.append([firstname, lastname, grad_school, grad_school_code, highest_degree, grad_year,
                           university, university_code, title, department])
    return professors

# Initiate sequence
print 'Scraping faculty data...'
professors = getFacultyGCU() + getFacultyAPU() + getFacultyWM()
print 'Complete'

# Add column headers
professors = pd.DataFrame(professors)
professors.columns = ['firstname', 'lastname', 'grad_school', 'grad_school_code', 'highest_degree', 'grad_year',
                      'university', 'university_code', 'title', 'department']

# Save to csv
professors.to_csv('faculty.csv', encoding = 'utf-8', index=False)
print 'Results saved in faculty.csv'