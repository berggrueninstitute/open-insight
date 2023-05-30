# open-insight

## Prototype Mockup — Open Insight

### ETL Code:

##### MongoDB: 

###### Docker Setup

https://docs.docker.com/engine/install/debian/

###### Run MongoDB with Docker

docker run --name mongo -p 27017:27017 -v ~/data/db:/data/db -d mongo:latest

#### Python Setup

Before running the script, make sure you have the following prerequisites installed:

* Python 3: Install Python 3 from the official website (https://www.python.org).

* PIP for Python 3: 
sudo apt install python3-pip

* NLTK: Install the NLTK package by running 
pip install nltk

* PyPDF2: Install the PyPDF2 package by running 
pip install PyPDF2

* pymongo: Install the pymongo package by running 
pip install pymongo

* pymongo: Install the objdict package by running 
pip install objdict



## Project Summary:

The Open Insight project aims to create a suite of software tools to create engagement between constituents and leaders in Democratic political processes. As a first step in launching the project, a prototype of the React-based applications that can be used to provide a user-friendly interface to interact with historical data on issues, voting and outside influence will be built both to demonstrate the application to generate interest and to assist with the iterative design of the application itself.

The application will be developed using the latest React frameworks and will have several components that can be customized based on User Interface requirements, including a non-React based WebGL View for rendering sophisticated Data Visualizations of search results. 

The project will involve creating a responsive and interactive UI that has been enabled to function in such a way as to demonstrate the look and feel and workflow of the application, but is not a full featured implementation of the application, which is out of scope at this stage and will not be executed until a more refined design has been reached at a future date.

Project Objectives:

- Develop prototypes of React UI based applications defined for Open Insight Suite
- Create a responsive and interactive UI for displaying user experience and workflow
- Implement Git repository to collect and share open source code
- Implement basic automation technology to continuously test and deploy project code

Project Scope:
The project will focus on creating a prototype of a JavaScript React UI application that can be used to interact with the proposed user interface design to understand the ideas and purpose involved in the application concept and evolve the user interface design itself.

Project Deliverables:

- Prototype of a JavaScript React UI application
- Git source code repository of the application code and history
- Online deployment of the application
- Automated deployment of latest code from Git
- Test cases and test results

Project Timeline:
The following is a breakdown of the project milestones:

- Milestone 1: Requirements gathering and UI design, basic infrastructure
- Milestone 2: Application development and automated deployment
- Week 3: Basic automated testing and bug fixing
- Week 4: UAT prototype for external testing
