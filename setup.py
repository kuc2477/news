try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from news import VERSION


# describe readme and change logs
long_description = open('README.rst').read()

# test command
try:
    from setuptools.command.test import test
except ImportError:
    cmdclass = {}
else:
    class pytest(test):
        """cmdclass for test runner."""
        def finalize_options(self):
            self.test_args = ['--cov=news']
            self.test_suite = True

        def run_tests(self):
            from pytest import main
            errno = main(self.test_args)
            raise SystemExit(errno)
    cmdclass = {'test': pytest}


# dependencies
peer_dependencies = [
    'celery>=3.1.23',
    'redis>=2.10.5',
]
install_dependencies = [
    'aiohttp>=0.19.0',
    'schedule>=0.3.2',
    'feedparser>=5.2.1',
    'beautifulsoup4>=4.4.1',
    'extraction==0.2.1',
    'urltools>=0.3.2',
    'colorlog>=2.6.0',
    'django>=1.7,<1.10',
    'django-jsonfield>=0.9.16',
    'SQLAlchemy>=1.0.11',
    'sqlalchemy-utils>=0.31.6',
]
external_dependencies = [
    'https://github.com/kuc2477/extraction/archive/master.zip' +
    '#egg=extraction-0.2.1'
]
test_dependencies = [
    'pytest>=2.8.5',
    'pytest-asyncio>=0.3.0',
    'pytest-django>=2.9.1',
    'pytest-mock>=0.11.0',
    'pytest-cov>=2.2.1',
    'celery>=3.1.23',
    'redis>=2.10.5',
]


setup(
    name='news',
    packages=find_packages(exclude=['tests']),
    data_files=[('', ['README.rst'])],
    version=VERSION,
    description='Schedulable web subscription engine',
    long_description=long_description,
    license='MIT License',
    author='Ha Junsoo',
    author_email='kuc2477@gmail.com',
    maintainer='Ha Junsoo',
    maintainer_email='kuc2477@gmail.com',
    url='https://github.com/kuc2477/news',
    install_requires=(install_dependencies + peer_dependencies),
    dependency_links=external_dependencies,
    test_suite='tests',
    tests_require=test_dependencies,
    cmdclass=cmdclass,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5'
    ],
)
