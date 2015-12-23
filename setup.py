try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

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
            errno = main(self.test_args)
            from pytest import main
            raise SystemExit(errno)
    cmdclass = {'test': pytest}


setup(
    name='news',
    packages=['news'],
    data_files=[('', ['README.rst', 'CHANGES.rst'])],
    version=VERSION,
    description='web readable scrapper and scheduluer automated',
    long_description=long_description,
    license='MIT License',
    author='Ha Junsoo',
    author_email='kuc2477@gmail.com',
    url='https://github.com/kuc2477/news',
    install_requires=['aiohttp>=0.19.0', 'beautifulsouip4>=4.4.1'],
    tests_require=['pytest>=2.8.5'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5'
    ],
    cmdclass=cmdclass
)
