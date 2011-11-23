from setuptools import setup, find_packages

setup(
    name='txango',
    version= '0.1',
    install_requires = ['twisted', 'django'],
    packages=find_packages(),
    zip_safe=False
)
