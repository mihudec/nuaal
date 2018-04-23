from setuptools import setup

setup(
    name='nuaal',
    version='0.1.0',
    packages=['nuaal', 'nuaal.tests', 'nuaal.utils', 'nuaal.Parsers', 'nuaal.Readers', 'nuaal.Writers', 'nuaal.examples', 'nuaal.Discovery',
              'nuaal.connections', 'nuaal.connections.api', 'nuaal.connections.api.epnm', 'nuaal.connections.api.apic-em', 'nuaal.connections.cli',
              'nuaal.connections.snmp'],
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
