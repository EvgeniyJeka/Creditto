# 1 General Description

<b>QaService</b> - a framework and a set of tests running in a docker container. 
All tests can be executed from a local machine as well, providing all the dependencies are installed (see requirements.txt file in 'QaService' folder).

The tests are not part of the Creditto project (since those aren't unit tests), but a set of 'black box' tests - 
each test generates an <b>INPUT</b> for Creditto project services and verifies the produced <b>OUTPUT</b>. 

INPUT can be HTTP request or SQL DB table modification.
Expected OUTPUT is HTTP response, SQL table modification or a Kafka message produced to one of the topics.

<img src="https://github.com/EvgeniyJeka/Creditto/blob/main/black_box_testing.jpg" alt="Screenshot" width="1000" />

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

This section in docker-compose.yml file is responsible for QaService:


    sanity_tests_container:
 
    image: sanity_tests_container:latest
    
    command: ["pytest", "-v", "-m", "sanity"]
    
    build: ./QaService
    
    networks:
    
      - creditto_main
      
    environment:
    
      - BASE_URL=http://creditto_creditto_gateway_1:5000
      
      - SQL_HOST=cabin_db
      
      - SQL_PORT=3306
      
      - SQL_USER=root
      
      - SQL_PASSWORD=123456
      
      - WAIT_BEFORE_TIMEOUT=15
      
      - MYSQL_DB_WARMUP_DELAY=40 
      
  
 It contains the following line: <b>command: ["pytest", "-v", "-m", "sanity"]</b>
 
 This command is executed when docker container is started, it is used to run the selected test group.
 In given configuration all tests marked with <b>@pytest.mark.sanity</b> annotation will be executed.
 If you want to run another test group, replace the word 'sanity' with the selected test group name, for example:
 
 <b>command: ["pytest", "-v", "-m", "end2end"]</b>
 
 
