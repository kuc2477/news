try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from news import VERSION


# describe readme and change logs
long_description = (
    open('README.rst').read() + '\n\n' +
    open('CHANGES.rst').read()
)

try:
    from setuptools.command.test import test
except ImportError:
    cmdclass = {}
else:
    class pytest(test):
        """cmdclass for test runner."""
        def finalize_options(self):
            self.test_args = []
            self.test_suite = True

        def run_tests(self):
            from pytest import main
            errno = main(self.test_args)
            raise SystemExit(errno)
    cmdclass = {'test': pytest}


setup(
    name='news',
    packages=find_packages(exclude=['tests']),
    entry_points='''
        [console_scripts]
        news = news.cli:main
    ''',
    data_files=[('', ['README.rst', 'CHANGES.rst'])],
    version=VERSION,
    description='Scheduled web post scrapper automated',
    long_description=long_description,
    license='MIT License',
    author='Ha Junsoo',
    author_email='kuc2477@gmail.com',
    maintainer='Ha Junsoo',
    maintainer_email='kuc2477@gmail.com',
    url='https://github.com/kuc2477/news',
    install_requires=[
        'aiohttp>=0.19.0',
        'schedule>=0.3.2',
        'beautifulsoup4>=4.4.1',
        'extraction==0.2.1',
        'urltools>=0.3.2',
        'click>=6.2',
        'colorlog>=2.6.0',
        'cached-property>=1.3.0',
        'django>=1.7',
        'django-jsonfield>=0.9.16',
        'SQLAlchemy>=1.0.11',
        'sqlalchemy-utils>=0.31.6',
    ],
    dependency_links=[
        'https://github.com/kuc2477/extraction/archive/master.zip' +
        '#egg=extraction-0.2.1'
    ],
    test_suite='tests',
    tests_require=[
        'pytest>=2.8.5',
        'pytest-asyncio>=0.3.0',
        'pytest-django>=2.9.1'
    ],
    cmdclass=cmdclass,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5'
    ],
)
