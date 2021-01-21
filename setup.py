from setuptools import setup, find_packages

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

setup(
    name='nuaal',
    version='0.1.19',
    packages=find_packages(exclude=["tests", "examples"]),
    url='https://github.com/mijujda/nuaal',
    license='',
    author='Miroslav Hudec',
    author_email='mijujda@gmail.com',
    description='Network Unified Abstraction API Library',
    install_requires=reqs,
    include_package_data=True
)
