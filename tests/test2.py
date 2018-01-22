from tests.test_simple_server_client import TestProvider
from lessrpc_stub.stubs.server import ServerStub
prov = TestProvider()
stub = ServerStub(prov)
stub.start()