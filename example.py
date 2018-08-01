#!/usr/bin/env python2

#Import the stuffs
import matplotlib.pyplot as plt
import numpy as np
import pandas as ps
import csv
from datetime import datetime as dt

def main():
    enrollments = read_csv('enrollments.csv')
    daily_engagement = read_csv('daily_engagement_full.csv')
    project_submissions = read_csv('project_submissions.csv')
    print("number of rows in enrollments, engagement and submissions" + "")
    print(len(enrollments), len(daily_engagement), len(project_submissions))

    # Clean up the data types in the enrollments table
    #dataCleanup(enrollments, daily_engagement, project_submissions)

    #cleanup the column name to account_key
    for dictionary in daily_engagement:
        dictionary['account_key'] = dictionary.pop('acct')

    #Get lists of unique students in the different files
    uniqueEnrollmentStudents = getUnique(enrollments, 'account_key')
    uniqueEngagementStudents = getUnique(daily_engagement, 'account_key')
    uniqueProjectStudents = getUnique(project_submissions, 'account_key')

    print("number of students in enrollments, daily engagement and project submission")
    print("")
    print(len(uniqueEnrollmentStudents), len(uniqueEngagementStudents), len(uniqueProjectStudents))


def getUnique(list, keyname):
    listOfUniqueNames = set()
    for item in list:
        listOfUniqueNames.add(item[keyname])
    return listOfUniqueNames

def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f)
        return list(reader)




# Takes a date as a string, and returns a Python datetime object.
# If there is no date given, returns None
def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')

# Takes a string which is either an empty string or represents an integer,
# and returns an int or None.
def parse_maybe_int(i):
    if i == '':
        return None
    else:
        return int(i)

def dataCleanup(enrollments, daily_engagement, project_submissions):
    for enrollment in enrollments:
        enrollment['cancel_date'] = parse_date(enrollment['cancel_date'])
        enrollment['days_to_cancel'] = parse_maybe_int(enrollment['days_to_cancel'])
        enrollment['is_canceled'] = enrollment['is_canceled'] == 'True'
        enrollment['is_udacity'] = enrollment['is_udacity'] == 'True'
        enrollment['join_date'] = parse_date(enrollment['join_date'])

    # Clean up the data types in the engagement table
    for engagement_record in daily_engagement:
        engagement_record['lessons_completed'] = int(float(engagement_record['lessons_completed']))
        engagement_record['num_courses_visited'] = int(float(engagement_record['has_visited']))
        engagement_record['projects_completed'] = int(float(engagement_record['projects_completed']))
        engagement_record['total_minutes_visited'] = float(engagement_record['total_minutes_visited'])
        engagement_record['utc_date'] = parse_date(engagement_record['utc_date'])
    # Clean up the data types in the submissions table
    for submission in project_submissions:
        submission['completion_date'] = parse_date(submission['completion_date'])
        submission['creation_date'] = parse_date(submission['creation_date'])

if __name__ == "__main__":
    main()
