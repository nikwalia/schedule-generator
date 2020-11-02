import urllib3
import xmltodict
import pandas as pd
import itertools
from collections import defaultdict
import csv

def getxml(url):
    """
    Retrives XML from a given url.

    :param url: url to retrive XML from
    :return: dictionary representing XML
    """
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    try:
        data = xmltodict.parse(response.data)
    except:
        print("Failed to parse xml")
    return data


def parse_course_info(years, semesters, majors):
    """
    Retrives XML from course explorer for a given list of years and semesters.
    Writes the data to an individual csv file.

    :param years: years to iterate over
    :param semesters: semesters to iterate over
    """
    for year, sem, major in list(itertools.product(years, semesters, majors)):

        url = 'https://courses.illinois.edu/cisapp/explorer/schedule/{}/{}/{}.xml'.format(year,sem, major)
        xml_doc = getxml(url)
        courses = []

        for course in xml_doc['ns2:subject']['courses']['course']:
            course_url = course['@href']
            course_xml_doc = getxml(course_url)['ns2:course']

            course_dict = {
                'courseId': course_xml_doc['@id'],
                'courseTitle': course_xml_doc['label'],
                'creditHours': course_xml_doc['creditHours'],
                'description': course_xml_doc['description'],
            }

            if 'courseSectionInformation' in course_xml_doc:
                course_dict['prereqs'] = course_xml_doc['courseSectionInformation']
            else:
                course_dict['prereqs'] = ""
        
            courses.append(course_dict)
        
        
        keys = courses[0].keys()
        with open('{}-{}-{}.csv'.format(year, sem, major), 'w', newline='')  as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(courses)

if __name__ == "__main__":
    years = ['2016','2017','2018','2019','2020']
    semesters = ['fall','spring']
    majors = ['CHEM']
    parse_course_info(years, semesters, majors)