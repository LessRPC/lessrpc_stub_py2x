from setuptools import setup

setup(
  name = 'lessrpc-stub',
  packages = ['lessrpc'], # this must be the same as the name above
  version = '1.0.1',
  description = 'Less RPC stubs project',
  author = 'Salim Malakouti',
  author_email = 'salim.malakouti@gmail.com',
  license = 'MIT',
  url = 'https://github.com/LessRPC/lessrpc_stub_py2x', # use the URL to the github repo
  download_url = 'https://github.com/LessRPC/lessrpc_stub_py2x/archive/1.0.1.tar.gz', # I'll explain this in a second
  keywords = ['python','serialization','deserialization','rpc','rmi','less rpc', 'clinet', 'server'], # arbitrary keywords
  classifiers = ['Programming Language :: Python :: 2.7'],
  install_requires=[],
  python_requires='~=2.7',
)
