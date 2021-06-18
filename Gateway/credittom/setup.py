from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='credittomodels',
  version='0.0.2',
  description='Classes needed for Creditto project',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',
  author='Eugene Silverman',
  author_email='',
  license='MIT',
  classifiers=classifiers,
  keywords='credittomodels',
  packages=find_packages(),
  install_requires=['datetime', 'pymysql']
)