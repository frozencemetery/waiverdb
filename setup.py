from setuptools import setup

version = '1.0.0'

setup(name='waiverdb',
      version=version,
      description='An engine for storing waivers against test results.',
      author='Red Hat, Inc.',
      author_email='qa-devel@lists.fedoraproject.org',
      license='GPLv2+',
      packages=['waiverdb'],
      package_dir={'waiverdb': 'waiverdb'},
      #entry_points={
      #    #TODO: register messaging plugins
      #},
)
