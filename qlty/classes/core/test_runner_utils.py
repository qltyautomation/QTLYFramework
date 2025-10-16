# Native libraries
import pwd
import os
from pprint import pformat
from datetime import datetime
# Project libraries
from qlty.classes.integrations.slack_reporter import SlackReporter
from qlty.utilities.utils import setup_logger, get_unique_build_id
import qlty.config as config
import settings

logger = setup_logger(__name__, settings.DEBUG_LEVEL)


class TestRunnerUtils:
    """
    Utility class for configuration validation and test run lifecycle management
    """

    #: Console message for iOS-only test execution
    running_on_ios_message = 'iOS test cases only, skipping'
    #: Console message for Android-only test execution
    running_on_android_message = 'Android test cases only, skipping'
    #: Console message for Android web test execution
    running_on_android_web_message = 'Chrome mobile for Android only, skipping'
    #: Console message for iOS web test execution
    running_on_ios_web_message = 'Safari for iOS only, skipping'

    @staticmethod
    def report(test_results, test_run_id, test_run_elapsed_time):
        """
        Distributes results to enabled integration systems

        :param test_results: Collection of test execution results
        :type test_results: dict
        :param test_run_id: Unique test run identifier
        :type test_run_id: str
        :param test_run_elapsed_time: Total test run duration
        :type test_run_elapsed_time: datetime
        """

        # Dispatch Slack notification if enabled
        if config.SLACK_REPORTING:
            SlackReporter().report(TestRunnerUtils.get_testrun_totals(
                test_results), TestRunnerUtils.get_readable_run_time(test_run_elapsed_time))

        # Display Saucelabs results link if integration active
        if config.SAUCELABS_INTEGRATION:
            logger.info('Saucelabs results: {}\n Search for test cases with prefix: {}'.format(
                settings.SAUCELABS['URL'], get_unique_build_id()))

    @staticmethod
    def generate_test_run_id():
        """
        Generates unique identifier string for test run

        :return: Test run identifier string
        :rtype: str
        """
        return '[{}] {} - LOCAL | {} '.format(datetime.now().strftime('%H:%M'),
                                              config.CURRENT_PLATFORM, pwd.getpwuid(os.getuid())[0])

    @staticmethod
    def running_on_ios():
        """
        Checks if current test run targets iOS platform

        :return: True if iOS execution, False otherwise
        :rtype: bool
        """
        return config.CURRENT_PLATFORM == 'ios'

    @staticmethod
    def running_on_android():
        """
        Checks if current test run targets Android platform

        :return: True if Android execution, False otherwise
        :rtype: bool
        """
        return config.CURRENT_PLATFORM == 'android'

    @staticmethod
    def running_on_android_web():
        """
        Checks if current test run targets Chrome mobile for Android

        :return: True if Android web execution, False otherwise
        :rtype: bool
        """
        return config.CURRENT_PLATFORM == 'android_web'

    @staticmethod
    def running_on_ios_web():
        """
        Checks if current test run targets Safari mobile for iOS

        :return: True if iOS web execution, False otherwise
        :rtype: bool
        """
        return config.CURRENT_PLATFORM == 'ios_web'

    @staticmethod
    def get_testrun_totals(test_results):
        """
        Generates consolidated test case execution statistics

        Example output:

            .. code-block:: python

                results = {
                    'total_testcases': 0,
                    'passed_testcases': 0,
                    'failed_testcases': 0
                }

        :param test_results: Collection of executed test cases
        :type: Dictionary
        :return: Consolidated statistics dictionary
        :rtype: Dictionary
        """

        results = {
            'total_testcases': 0,
            'passed_testcases': 0,
            'failed_testcases': 0,
            'passed_percentage': '0.0%',
            'failed_percentage': '0.0%',
        }

        # Aggregate test result statistics
        for test_class, test_methods in test_results.items():
            for test_method, result in test_methods.items():
                if result['status'] == 'passed':
                    results['passed_testcases'] += 1
                elif result['status'] == 'failed':
                    results['failed_testcases'] += 1
                else:
                    logger.warning('Unrecognized result status: {}'.format(result['status']))

        # Calculate totals and percentages
        results['total_testcases'] = results['passed_testcases'] + results['failed_testcases']
        # Calculate pass/fail percentages
        results['passed_percentage'] = "{:.1f}%".format((results['passed_testcases'] / results['total_testcases']) * 100)
        results['failed_percentage'] = "{:.1f}%".format((results['failed_testcases'] / results['total_testcases']) * 100)

        return results

    @staticmethod
    def get_readable_run_time(test_run_time):
        """
        Converts test run duration to human-readable format (e.g., 1h 12m 34s)

        :param test_run_time: Test run duration in seconds
        :return: Formatted duration string
        :rtype: String
        """

        result = ''
        # Extract hours component (floor division)
        if test_run_time // 3600 > 0:
            result += '{}h '.format(int(test_run_time // 3600))
        # Remove hours from remaining time
        test_run_time %= 3600
        # Extract minutes component
        if test_run_time // 60 > 0:
            result += '{}m '.format(int(test_run_time // 60))
        # Remove minutes from remaining time
        test_run_time %= 60
        # Append remaining seconds
        result += '{}s'.format(int(test_run_time))

        return result
