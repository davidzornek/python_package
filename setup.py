# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='XXXXXXXXXXXXX',

    # Versions follow MAJOR.MINOR.MAINTENANCE
    # MAJOR: Changes incompatible with prior version
    # MINOR: Backwards-compatible additions to functionality
    # MAINTENANCE: Backwards-compatible bug fixes with no new functionality
    # See http://semver.org/ for more information.
    version='0.0.0',
    packages=['XXXXXXXXXXXXX],

    description='XXXXXXXXXXXXX',
    long_description=long_description,

    # The project's main homepage.
    url='XXXXXXXXXXXXX',

    # Author details
    author='XXXXXXXXXXXXX',
    author_email='XXXXXXXXXXXXX',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Project maturity allowed values:
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        # 7 - Inactive
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Data Scientists',
        'Topic :: Data Science :: Analysis ',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # Automatically discovers packages to be included.
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Minimal requirements to run
    install_requires=['pandas>=0.20.3',
                      'pymysql>=0.8.0',
                      'python-dotenv==0.6.5',
                      'requests>=2.18.4',
                      'pygeoj>=0.22',
                      'geojson>=2.3.0',
                      'geopandas>=0.3.0',
                      'deprecation>=2.0'
                      ],

    # Requires at least 3.6, but we do not commit to python 4 support.
    python_requires='~=3.6',

    # Include labels for mls data
    package_data={
        },

    include_package_data=True
)
