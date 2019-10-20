from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='grade',
    version='0.5.1',
    packages=['grade'],
    url='https://github.com/thoward27/grade',
    license='AGPL',
    author='Tom Howard',
    author_email='info@tomhoward.codes',
    description='An package for easy autograding.',
    long_description=long_description,
    python_requires='>=3.8',
)
