# 1 General Description

<b>QaService</b> - a framework and a set of tests running in a docker container. 
All tests can be executed from a local machine as well, providing all the dependencies are installed (see requirements.txt file in 'QaService' folder).

The tests are not part of the Creditto project (since those aren't unit tests), but a set of 'black box' tests - 
each test generates an <b>INPUT</b> for Creditto project services and verifies the produced <b>OUTPUT</b>. 

INPUT can be HTTP request or SQL DB table modification.
Expected OUTPUT is HTTP response, SQL table modification or a Kafka message produced to one of the topics.

<img src="https://github.com/EvgeniyJeka/Creditto/blob/readme_updating/black_box_testing.jpg" alt="Screenshot" width="1000" />

# 2 Tests Framework

Set of tools used for effective test implementation. 
- Code responsible for work with MySQL, Kafka, and Docker can be found in 'Tools' folder under 'QaService'
- Code responsible for HTTP requests sending can be found in 'Requests' folder under 'QaService'
- Config can be found in 'Config' folder under 'QaService'

The framework uses PyTest tools - Pytest fixtures stored in <b>conftest.py</b> file

The framework uses the package 'credittomodels', the same package used by 'Creditto' project.


# 3 Test Groups

There are several groups of tests defined in <b>pytest.ini</b>:

  - sanity: sanity tests, verifying Bid and Offer placement, verifying other REST API methods
  
  - end2end: end to end tests, performing a full flow, verifying matching logic is applied correctly
  
  - functional: tests that verify a specific system functionality in each test 
  
  - kafka: tests that verify Kafka messages content, while messages are consumed directly from Kafka
  
  - negative: negative tests, verifying system behaviour on invalid input, verifying incoming HTTP requests are validated
  
  - container: all tests that can run in docker container
  
  - recovery: tests that verify services behaviour after docker container restart and recovery flow

All tests, except for 'recovery' can run in a Docker container. 
A test can be part of several groups - for example, the 'container' group includes all tests that can run in docker container, all except for 'recovery'. 
Each test is marked with a PyTest annotation, so the group of executed tests can be selected on each test run.


# 4 How To 
