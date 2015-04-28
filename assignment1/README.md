# Overview
This script scrapes faculty data from:
- [Azusa Pacific University](http://www.apu.edu/clas/faculty)
- [Georgian Court University](http://www.georgian.edu/faculty/list.htm)
- [William & Mary University - Law School](http://law2.wm.edu/faculty/bios/fulltime/)

Produces a CSV file with the following fields for each professor:
- firstname: professor's first name
- lastname professors' last name
- grad_school: university where he/she earned highest degree
- grad_school_code: identifier code for grad school university
- highest_degree: highest degree earned (e.g. Ph.D.)
- grad_year: year that professor earned highest degree
- university: current university where teaching
- university_code: identifier code for current university
- title: title at current university (e.g. Assistant Professor)
- department: current department where teaching