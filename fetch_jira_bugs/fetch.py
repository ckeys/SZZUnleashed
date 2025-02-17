""" Fetch issues that match given jql query """
__author__ = "Kristian Berg"
__copyright__ = "Copyright (c) 2018 Axis Communications AB"
__license__ = "MIT"

from urllib.parse import quote
import urllib
import urllib.request as url
import json
import os
import argparse
import io
import sys

def fetch(project_issue_code, jira_project_name):
    """ Fetch issues that match given jql query """
    # Jira Query Language string which filters for resolved issues of type bug
    jql = 'project = ' + project_issue_code + ' ' \
        + 'AND issuetype = Bug '\
        + 'AND status in (Resolved, Closed) '\
        + 'AND resolution = Fixed '\
        + 'AND created <= "2025-01-01" '\
        + 'ORDER BY created DESC'
    jql = quote(jql, safe='')
    start_at = 0
    # max_results parameter is capped at 1000, specifying a higher value will
    # still return only the first 1000 results
    max_results = 1000
    os.makedirs('issues/', exist_ok=True)
    request = 'https://' + jira_project_name + '/rest/api/2/search?'\
        + 'jql={}&startAt={}&maxResults={}'
    
    # 1. Construct the JQL query
    jql = (
        f'project = "{project_issue_code}" '
        'AND issuetype = Bug '
        'AND status in (Resolved, Closed) '
        'AND resolution = Fixed '
        'AND created <= "2025-01-01" '
        'ORDER BY created DESC'
    )
    
    # 2. Define query parameters
    params = {
        'jql': jql,
        'startAt': start_at,
        'maxResults': 1,  # Maximum allowed by Jira API
    }
    
    # 3. Encode the query parameters
    encoded_params = urllib.parse.urlencode(params)
    
    # 4. Construct the full request URL
    request_url = f'https://{jira_project_name}/rest/api/2/search?{encoded_params}'

    print(request_url) 
    # Do small request to establish value of 'total'
    with url.urlopen(request_url) as conn:
        contents = json.loads(conn.read().decode('utf-8'))
        total = contents['total']

    # Fetch all matching issues and write to file(s)
    print('Total issue matches: ' + str(total))
    print('Progress: | = ' + str(max_results) + ' issues')
    while start_at < total:
        params['startAt'] = start_at
        params['maxResults'] = max_results
        encoded_params = urllib.parse.urlencode(params)
        request_url = f'https://{jira_project_name}/rest/api/2/search?{encoded_params}'
        with url.urlopen(request_url) as conn:
            with io.open('issues/res' + str(start_at) + '.json', 'w', encoding="utf-8") as f:
                f.write(conn.read().decode('utf-8', 'ignore'))
        print('|', end='', flush='True')
        start_at += max_results

    print('\nDone!')

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="""Convert a git log output to json.
                                                 """)
	parser.add_argument('--issue-code', type=str,
        	help="The code used for the project issues on JIRA: e.g., JENKINS-1123. Only JENKINS needs to be passed as parameter.")
	parser.add_argument('--jira-project', type=str,
            help="The name of the Jira repository of the project.")

	args = parser.parse_args()
	project_issue_code = args.issue_code
	jira_project_name = args.jira_project
	fetch(project_issue_code, jira_project_name)
