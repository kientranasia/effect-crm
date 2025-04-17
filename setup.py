from setuptools import setup, find_packages

setup(
    name='effect-crm',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Login',
        'Flask-Migrate',
        'Flask-WTF',
        'python-dotenv',
    ],
) 