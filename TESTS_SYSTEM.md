# 1 General Description

<b>QaService</b> - a framework and a set of tests running in a docker container. 
All tests can be executed from a local machine as well, providing all the dependencies are installed (see requirements.txt file in 'QaService' folder).

The tests are not part of the Creditto project (since those aren't unit tests), but a set of 'black box' tests - 
each test generate an INPUT for Creditto project services and verifies the produced OUTPUT. 

INPUT can be HTTP request or SQL DB table modification.
Expected OUTPUT is HTTP response, SQL table modification or a Kafka message produced to one of the topics.

# 2 Tests Framework


# 3 Test Types


# 4 How To 
