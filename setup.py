from setuptools import setup

setup(
    name='nuaal',
    version='0.1.0',
    packages=['nuaal', 'nuaal.utils', 'nuaal.Parsers', 'nuaal.Readers', 'nuaal.Writers', 'nuaal.examples', 'nuaal.Discovery',
              'nuaal.connections.cli'],
    url='https://github.com/mijujda/nuaal',
    license='',
    author='Miroslav Hudec',
    author_email='mijujda@gmail.com',
    description='',
    install_requires=[
        "netmiko",
        "requests"
    ]
)
