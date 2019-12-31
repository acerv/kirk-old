.. _Jenkins: https://jenkins.io/
.. _Jenkinsfile: https://jenkins.io/doc/book/pipeline/jenkinsfile/

Quickstart
==========

Kirk is a tool that extends Jenkins_ functionalities, creating and building jobs
automatically, without thinking about their maintainance.

Kirk will communicate with Jenkins_ using a username which is called **owner**.
The owner is a user that communicates with Jenkins_ REST API and it has special
privileges into the server, such as:

  * reading installed plugins
  * creating a job
  * configuring a job
  * fetching job informations
  * building a job
  * deleting a job

First of all, check that the Jenkins_ server supports kirk. Run ``kirk-check``
command with server url, owner name and password in order to verify it:

.. code-block:: bash

  $ kirk-check http://localhost:8080 kirk 1116e370cb9c21990c23de3be450e015ea
  kirk-check session started

    url: http://localhost:8080
    user: kirk
    token: *******

    1/7   connection test  PASSED
    2/7   plugins installed  PASSED
    3/7   create job  PASSED
    4/7   configure job  PASSED
    5/7   fetching job info  PASSED
    6/7   build job  PASSED
    7/7   delete job  PASSED

Great! Our server supports kirk! 

Save your owner name credential with ``kirk-credential`` command. It will
store a ``credentials.cfg`` file inside the current folder that contains all
informations to read owner credentials:

.. code-block:: bash

  $ kirk-credential http://localhost:8080 kirk
  saving credential:
    url:  http://localhost:8080
    user: kirk
    password:

  credential saved

.. note::

  ``credentials.cfg`` is the default credentials file and it's always loaded
  from the current directory by ``kirk`` command.

Create your own ``projects`` folder where projects are saved.

.. code-block:: bash

  $ mkdir projects

And finally, create the first project file called ``projects/simple.yml``:

.. code-block:: yaml

    name: myproject
    description: my project 0
    author: pippo
    year: 2020
    version: 1.0
    location: MY_PROJECT
    defaults:
        server: http://localhost:8080
        scm:
            git:
                url: https://github.com/myuser/myrepo.git
    jobs:
        - name: fullbuild
          pipeline: ci/fullbuild_pipeline.groovy

        - name: run_unittest
          pipeline: ci/unittest_pipeline.groovy

To execute ``run_unittest`` job with latest modifications on ``development``
branch, use ``kirk run`` command:

.. parsed-literal::

    > kirk run myproject::run_unittest --change-id development

    kirk |version| session started

    owner: kirk
    rootdir: /home/sawk/kirk
    projects: projects
    credentials: credentials.cfg

    collected 5 jobs

    selected jobs
    myproject::run_unittest

    -> running myproject::run_unittest (user='')
    -> configured http://localhost:8080/job/MY_PROJECT/job/run_unittest/2/

As you can see, kirk is based on the concept that groovy pipelines are such a
powerful tool, that there's no need to define manually jobs statements anymore,
since they can be well defined inside the Jenkins_ pipelines.

For example, our ``ci/unittest_pipeline.groovy`` might be defined as following:

.. code-block:: groovy

  /* This is a scripted pipeline to run unittests on linux nodes */

  node("linux")
  {
    stage('Checkout')
    {
      scm checkout // fetch source code inside the node
    }
    stage('Unittest')
    {
      sh "pytest --junitxml=report.json" // run unittests
    }
    stage('Publish')
    {
      junit "report.json" // publish results
    }
  }

More complex pipelines examples are covered into the official Jenkinsfile_
documentation.

.. note::

  Beware to understand the difference between scripted and declared pipelines
  when reading the Jenkinsfile_ documentation.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
