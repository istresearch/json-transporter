import sys
import os
import shutil
from setuptools import setup, find_packages


def readme():
    ''' Returns README.rst contents as str '''
    with open('README.rst') as f:
        return f.read()

data_files = [
    (os.path.expanduser('~/.tport'), ['.tport'])
]

# Temporary hack to get around setup.py bombing on already existing files
if not os.path.isfile(os.path.expanduser('~/.tport')):
    shutil.copyfile('.tport', os.path.expanduser('~/.tport'))

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
extras_require = {
    'test': tests_require,
    'all': install_requires + tests_require,
    'docs': ['sphinx'] + tests_require,
    'lint': lint_requires
}

if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='json-transporter',
    version='0.2.1',
    description='A JSON data transporter',
    long_description=readme(),
    author='Jason Haas',
    author_email='jasonrhaas@gmail.com',
    license='MIT',
    url='https://github.com/istresearch/json-transporter',
    keywords=['json', 'elasticsearch', 's3', 'kafka', 'mongo'],
    packages=find_packages(),
    package_data={},
    # data_files=data_files,
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require=extras_require,
    dependency_links=dependency_links,
    zip_safe=True,
    test_suite='nose.collector',
    include_package_data=True,
    entry_points={'console_scripts': [
                                        'transporter=transporter.tport:main',
                                        'tport=transporter.tport:main'
                                        ]},
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
