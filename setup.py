from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='grade',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages('.', exclude=('test',)),
    url='https://github.com/thoward27/grade',
    license='AGPL',
    author='Tom Howard',
    author_email='info@tomhoward.codes',
    description='A package for easy autograding.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    install_requires=['Click']
)
