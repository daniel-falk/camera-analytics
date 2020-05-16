from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

# These requirements are only needed for some of
# the code. Install using "pip install .[all]"
required_all = [
    "fastai",
    "tensorboardx",
]

setup(
    name='camera-analytics',
    description='Neural network based visual door state prediction',
    long_description='''
    AXIS network camera application for visual analytics
    to classify the state of a door (open/closed)''',
    version="0.0",
    packages=['camlytics'],
    url='https://github.com/daniel-falk/camera-analytics',
    author='Daniel Falk',
    author_email='daniel@da-robotteknik.se',
    license='MIT',
    install_requires=required,
    extras_require={
        'all': required_all
    },
    entry_points={
        'console_scripts': [
            'annotate=camlytics.annotation.annotate:do_annotate'
        ],
    }
)
