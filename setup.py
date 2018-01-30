from setuptools import setup

setup(
  name = 'lessrpc_stub',
  packages = ['lessrpc_stub','lessrpc_stub.stubs'], # this must be the same as the name above
  version = '1.0.10',
  description = 'Less RPC stubs project',
  author = 'Salim Malakouti',
  author_email = 'salim.malakouti@gmail.com',
  license = 'MIT',
  url = 'https://github.com/LessRPC/lessrpc_stub_py2x/', # use the URL to the github repo
  download_url = 'https://github.com/LessRPC/lessrpc_stub_py2x/archive/1.0.10.tar.gz', # I'll explain this in a second
  keywords = ['python','serialization','deserialization','rpc','rmi','less rpc', 'client', 'server'], # arbitrary keywords
  classifiers = ['Programming Language :: Python :: 2.7'],
  install_requires=['pylods','pylods-json','httpoutputstream','cherrypy','enum34' ],
  python_requires='~=2.7'
)
