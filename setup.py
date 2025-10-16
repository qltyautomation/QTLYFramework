import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='QLTYFramework',
    version='1.1.0',
    author='Eduardo Reynoso',
    author_email='eduardo@qltyautomation.com',
    description='Mobile automation testing framework built on Appium for iOS and Android platforms',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/yourusername/QLTYFramework',
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/QLTYFramework/issues"
    },
    license='MIT',
    packages=['qlty',
              'qlty.classes',
              'qlty.utilities',
              'qlty.classes.integrations',
              'qlty.classes.selenium',
              'qlty.classes.core'
              ],
    install_requires=['requests', 'Appium-Python-Client', 'colorlog', 'numpy',
                      'cython', 'pyjnius', 'slack-sdk', 'boto3', 'sphinx-rtd-theme'],
    package_data={'': ['*.jar']},
    include_package_data=True,
)
