import sys
from setuptools import setup, find_packages


def readme():
    ''' Returns README contents as str '''
    with open('README.md') as f:
        return f.read()

install_requires = [
    'urllib3',
    'elasticsearch>=1.6',
    'boto',
    'pymongo',
    'happybase',
    'pykafka',
    'docopt'
]

lint_requires = [
    'pep8',
    'pyflakes'
]

tests_require = ['nose']
dependency_links = []
setup_requires = []
extras_require={
    'test': tests_require,
    'all': install_requires + tests_require,
    'docs': ['sphinx'] + tests_require,
    'lint': lint_requires
}

if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='json-transporter',
    version='0.1',
    description='A JSON data transporter',
    long_description=readme(),
    author='Jason Haas',
    author_email='jasonrhaas@gmail.com',
    license='MIT',
    url='https://github.com/istresearch/json-transporter',
    keywords=['json', 'elasticsearch', 's3', 'kafka', 'mongo'],
    packages=find_packages(),
    package_data={},
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require=extras_require,
    dependency_links=dependency_links,
    zip_safe=True,
    test_suite='nose.collector',
    include_package_data=True,
    entry_points={'console_scripts': ['tport=transporter.tport:main']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: General',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
