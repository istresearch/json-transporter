from setuptools import find_packages
from setuptools import setup

setup(
    name='json-transporter',
    packages=find_packages(),
    package_data={},
    install_requires=[
        'urllib3',
        'elasticsearch>=1.6',
        'boto',
        'pymongo',
        'happybase',
        'pykafka',
        'docopt'
    ],
    entry_points={'console_scripts': ['tport=tport.tport:main']},
    version='0.5',
    description='A JSON data transporter',
    author='Jason Haas',
    author_email='jasonrhaas@gmail.com',
    license='MIT',
    url='https://github.com/istresearch/json-transporter',
    # download_url='https://github.com/istresearch/json-transporter/tarball/0.1',
    keywords='json elasticsearch s3 kafka mongo',
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
