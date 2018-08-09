#!/usr/bin/env python2

#Import the stuffs
import matplotlib.pyplot as plt
import numpy as np
import pandas as ps
import csv
from datetime import datetime as dt
from collections import defaultdict

def main():
    enrollments = read_csv('enrollments.csv')
    daily_engagement = read_csv('daily_engagement_full.csv')
    project_submissions = read_csv('project_submissions.csv')
    # Clean up the data types in the enrollments table
    dataCleanup(enrollments, daily_engagement, project_submissions)
    for dictionary in daily_engagement:
        dictionary['account_key'] = dictionary.pop('acct')

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

    for engagement_record in paid_engagement:
        if engagement_record['num_courses_visited'] > 0:
            engagement_record['has_visited'] = 1
        else:
            engagement_record['has_visited'] = 0

    paid_engagement_in_first_week = []
    for engagement_record in paid_engagement:
        account_key = engagement_record['account_key']
        join_date = paid_students[account_key]
        engagement_record_date = engagement_record['utc_date']

        if within_one_week(join_date, engagement_record_date):
            paid_engagement_in_first_week.append(engagement_record)

    engagement_by_account = group_data(paid_engagement_in_first_week, 'account_key')

    '''
    total_minutes_by_account = {}

    for account_key, engagement_for_student in engagement_by_account.items():
        total_minutes = 0

        for engagement_record in engagement_for_student:
            total_minutes += engagement_record['total_minutes_visited']

        total_minutes_by_account[account_key] = total_minutes

    total_minutes = total_minutes_by_account.values()
    '''
    subway_project_lesson_keys = ['746169184', '3176718735']

    passing_students = find_passing_students(paid_submissions, subway_project_lesson_keys)
    passing_engagement, non_passing_engagement = find_passing_engagement(paid_engagement_in_first_week, passing_students)
    print(len(passing_engagement))
    print(len(non_passing_engagement))

    days_visited_by_account = sum_grouped_items(engagement_by_account, 'has_visited')
    describe_data(days_visited_by_account.values())

def find_passing_students(data, lesson_keys):
    passing_students = set()

    for data_point in data:
        if data_point['lesson_key'] in lesson_keys:
            if data_point['assigned_rating'] == 'PASSED' or data_point['assigned_rating'] == 'DISTINCTION':
                passing_students.add(data_point['account_key'])

    return passing_students

def find_passing_engagement(data, passing_students):
    passing_engagement = list()
    non_passing_engagement = list()
    for data_point in data:
        if data_point['account_key'] in passing_students:
            passing_engagement.append(data_point)
        else:
            non_passing_engagement.append(data_point)

    return passing_engagement, non_passing_engagement

def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days >= 0 and time_delta.days < 7

def remove_free_trial_cancels(data, paid_students):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data

def describe_data(data):
    print(np.mean(data))
    print(np.std(data))
    print(np.min(data))
    print(np.max(data))


def sum_grouped_items(grouped_data, field_name):
    summed_data = {}
    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            total += data_point[field_name]
        summed_data[key] = total
    return summed_data

def group_data(data, key_name):
    grouped_data = defaultdict(list)
    for data_point in data:
        key = data_point['account_key']
        grouped_data[key].append(data_point)
    return grouped_data

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
