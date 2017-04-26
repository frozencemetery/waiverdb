from setuptools import setup

version = '0.1.1'

setup(name='waiverdb',
      version=version,
      description='An engine for storing waivers against test results.',
      author='Red Hat, Inc.',
      author_email='qa-devel@lists.fedoraproject.org',
      license='GPLv2+',
      packages=['waiverdb', 'waiverdb.models'],
      package_dir={'waiverdb': 'waiverdb'},
)
