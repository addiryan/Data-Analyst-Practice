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
    # Clean up the data types in the enrollments table
    dataCleanup(enrollments, daily_engagement, project_submissions)

    #cleanup the column name to account_key
    for dictionary in daily_engagement:
        dictionary['account_key'] = dictionary.pop('acct')

    #Get lists of unique students in the different files
    uniqueEnrollmentStudents = getUnique(enrollments, 'account_key')
    uniqueEngagementStudents = getUnique(daily_engagement, 'account_key')
    uniqueProjectStudents = getUnique(project_submissions, 'account_key')

    udacity_test_accounts = set()
    for data in enrollments:
            if data['is_udacity']:
                udacity_test_accounts.add(data['account_key'])

    non_udacity_enrollment = removeUdacityAccounts(enrollments, udacity_test_accounts)
    non_udacity_engagement = removeUdacityAccounts(daily_engagement, udacity_test_accounts)
    non_udacity_project_submissions = removeUdacityAccounts(project_submissions, udacity_test_accounts)

    paid_students = {}
    for data in non_udacity_enrollment:
        if not data['is_canceled'] or data['days_to_cancel'] > 7:
            account_key = data['account_key']
            enrollment_date = data['join_date']

            if account_key not in paid_students or \
                    enrollment_date > paid_students[account_key]:
                paid_students[account_key] = enrollment_date

    paid_enrollments = remove_free_trial_cancels(non_udacity_enrollment, paid_students)
    paid_engagement = remove_free_trial_cancels(non_udacity_engagement, paid_students)
    paid_submissions = remove_free_trial_cancels(non_udacity_project_submissions, paid_students)
    


    paid_engagement_in_first_week = []
    for engagement_record in paid_engagement:
        account_key = engagement_record['account_key']
        join_date = paid_students[account_key]
        engagement_record_date = engagement_record['utc_date']

        if within_one_week(join_date, engagement_record_date):
            paid_engagement_in_first_week.append(engagement_record)

    print(len(paid_engagement_in_first_week))

def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days >= 0 and time_delta.days < 7

def remove_free_trial_cancels(data, paid_students):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data

def removeUdacityAccounts(list, udacity_test_accounts):
    without_udacity_accounts = []
    for datapoint in list:
        if datapoint['account_key'] not in udacity_test_accounts:
            without_udacity_accounts.append(datapoint)
    return without_udacity_accounts

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
