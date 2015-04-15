from lxml import html
import requests
import re
import pandas as pd

# Faculty directory page
rootURL = 'http://www.apu.edu'
directoryPage = requests.get(rootURL + '/clas/faculty')
directoryTree = html.fromstring(directoryPage.text)

# Get links to all professors (exclude deans)
links = directoryTree.xpath('//*[@id="template-page-content"]/ul[position() > 2]/li/a[2]/@href')
urls = map(lambda x: rootURL + x, links)

professors = []

# Go through each faculty page
for url in urls:
    facultyPage = requests.get(url)
    facultyTree = html.fromstring(facultyPage.text)
    
    # Name
    fullTitle = facultyTree.xpath('//*[@id="template-page-content"]/div/div[1]/div[@class="contact"]/h2/text()')
    fullTitle = [x.strip() for x in fullTitle[0].split(',')]
    
    name = fullTitle.pop(0) # Remove degree from name
    name = re.sub('([A-Z]\.)+ ', '', name) # Remove intitials (middle name)
    name = re.sub('([\(\']\w*[\)\']) ', '', name)  # Remove word in parentheses or quotes (nickname)
    name = name.split(' ') # Split first and last name
    firstName = name[0]
    lastName = name[-1]
    
    # Degree From Name
    degree = ','.join(fullTitle)
    
    # University
    university = 'Azusa Pacific University'
    
    # Department
    dept = facultyTree.xpath('//*[@id="template-page-content"]/div/div[1]/div[2]/text()')
    try:
        # Try to get department from below name
        dept = '|'.join(dept)
        dept = re.search('Department of ([^\'\|]+)\|', dept).group(1)
    except AttributeError:
        # If that didn't exist, look for the department section below bio
        dept = facultyTree.xpath('//*[@id="template-page-content"]/div/div[2]/div[@class="sdepartment"]/ul/li/text()')
        dept = dept[0] if len(dept) > 0 else ''
    
    # Graduate School & Degree
    # Determine which line represents highest education
    # PhDs may list there education reverse chronologically or chronologically
    educationFirst = facultyTree.xpath('//*[@id="template-page-content"]/div/div[2]/ul[1]/li[1]/text()')
    educationLast = facultyTree.xpath('//*[@id="template-page-content"]/div/div[2]/ul[1]/li[last()]/text()')

    # Default Answers if no data
    gradSchool = ''
    gradDegree = degree # default to degree from name unless found in education
    
    # Most faculty use reverse chronology
    # Check if highest degree is at bottom of list
    if len(educationFirst) > 0:
        if re.compile(r'(Ph.D.)').search(educationLast[0]) is not None:
            educationHighest = educationLast[0]
        else:
            educationHighest = educationFirst[0]
        # Now split the string and parse for degree and school
        # A few pages use dashes instead of commas to seperate degree. Replace with comma:
        educationHighest = educationHighest.replace('. - ', '. , ')
        # Now split on comma to get main parts
        educationHighest = [x.strip() for x in educationHighest.split(',')]
        gradDegree = educationHighest.pop(0) # Degree is always first
        gradDegree = gradDegree.split(' ')[0] # Take first degree title in case there are multiple

        # Get the school name NOT the year, deartment, or specialization
        tempGradSchool = None
        for text in educationHighest:
            if re.compile(r'([\d]+)').search(text) is None: # ensure not year
                # If we already have the school and the next piece looks like a city, include it
                if len(text.split()) < 3 and tempGradSchool is not None:
                    tempGradSchool = tempGradSchool + ', ' + text
                # If it looks like a school name grab the text
                if re.compile(r'University|College|School|Seminary|Institute').search(text) is not None:
                    tempGradSchool = text
                    # Specialization may be in front of the school name. Remove it
                    tempGradSchool = re.sub('(^.+\- )', '', tempGradSchool)
        # Assign the grad school if it was found
        gradSchool = tempGradSchool or ''
    
    professors.append([firstName, lastName, university, dept, gradSchool, gradDegree])

professors