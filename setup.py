from setuptools import setup
import grade

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='grade',
    version=grade.__version__,
    packages=['grade'],
    url='https://github.com/thoward27/grade',
    license='AGPL',
    author='Tom Howard',
    author_email='info@tomhoward.codes',
    description='A package for easy autograding.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
)
