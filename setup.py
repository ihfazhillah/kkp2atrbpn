from setuptools import setup

with open("requirements.txt", "r") as reqs:
    install_required = reqs.readlines()

setup(
    name='kkp2persil',
    version='0.1',
    packages=['kkpatrbpn.automate', 'kkpatrbpn.automate.pages'],
    url='https://github.com/ihfazhillah/kkp2atrbpn',
    license='',
    author='ihfazh',
    author_email='me@ihfazh.com',
    description='',
    install_required=install_required
)
