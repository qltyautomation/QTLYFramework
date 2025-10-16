# Third party libraries
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
# Project libraries
import qlty.utilities.utils as utils
import settings
import qlty.config as config
from qlty.utilities.utils import setup_logger

logger = setup_logger(__name__, settings.DEBUG_LEVEL)


class SaucelabsHelper:

    @staticmethod
    def get_saucelabs_appium_remote(test_case, platform):
        """
        Configures and returns a webdriver instance for Saucelabs remote execution with
        appropriate metadata for test organization
        :param test_case: A QLTY test case instance
        :type: QLTYTestcase
        :param platform: Platform identifier for webdriver configuration
        :type: String
        :return: Configured webdriver instance for saucelabs execution
        :rtype: Webdriver
        """
        logger.info('Configuring appium webdriver for saucelabs remote execution')
        try:
            capabilities = settings.SELENIUM['CAPABILITIES'][platform + '_saucelabs']
        except KeyError:
            logger.error('Saucelabs driver requested for {} but no capabilities defined '
                         'in settings.py\nPlease configure the required capabilities')
            exit(0)

        # Generate unique test case identifier with build and project info
        testcase_name = '{} - {}.{}'.format(
            utils.get_unique_build_id(),
            test_case.__class__.__qualname__,
            test_case._testMethodName)

        # Configure test case identifiers and metadata
        sauce_options = {
            'phoneOnly': True,
            'name': testcase_name,
            'build': settings.PROJECT_CONFIG['RELEASE'],
        }
        # Merge with saucelabs capabilities
        capabilities.update(settings.SELENIUM['CAPABILITIES'][platform + '_saucelabs'])
        # Add test-specific options for individual test reporting
        capabilities['sauce:options'] = sauce_options
        # Construct remote appium webdriver URL
        # Configure sauce labs remote URL
        appium_remote = 'https://{}:{}@{}'.format(settings.SAUCELABS['USERNAME'],
                                                  settings.SAUCELABS['ACCESS_KEY'],
                                                  settings.SAUCELABS['URL'])
        options = UiAutomator2Options()
        options.load_capabilities(capabilities)
        return webdriver.Remote(command_executor=appium_remote, options=options)

    @staticmethod
    def post_result(test_case, driver):
        """
        Submits test case result to the Saucelabs job record

        :param test_case: A QLTY test case for accessing webdriver
        :type test_case: QLTYTestCase
        :param driver: Webdriver for accessing script executor and posting result
        :type driver: Webdriver
        """
        test_case_name = '{}.{}'.format(test_case.__class__.__qualname__, test_case._testMethodName)
        if hasattr(test_case._outcome, 'errors'):
            # Python 3.4 through 3.10 compatibility
            result = test_case.defaultTestResult()
            test_case._feedErrorsToResult(result, test_case._outcome.errors)
        else:
            # Python 3.11 and later compatibility
            result = test_case._outcome.result

        job_result = 'passed' if all(test != test_case for test, text in result.errors + result.failures) else 'failed'
        logger.debug('Test case: {} has status [{}]'.format(test_case_name, job_result))
        # Submit result to Saucelabs test case record
        driver.execute_script("sauce:job-result={}".format(job_result))
