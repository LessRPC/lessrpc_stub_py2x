from org.lessrpc.stub.tests.test_simple_server_client import TestProvider
from org.lessrpc.stub.py.stubs.server import ServerStub
prov = TestProvider()
stub = ServerStub(prov)
stub.start()