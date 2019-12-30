.. _Jenkins: https://jenkins.io/
.. _Jenkinsfile: https://jenkins.io/doc/book/pipeline/jenkinsfile/

Quickstart
==========

Kirk is a tool that extends Jenkins_ functionalities, creating and building jobs
automatically, without thinking about their maintainance.

An example of a simple project file inside the ``projects`` folder:

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
branch:

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
documentation. Beware to understand the difference between scripted and declared
pipelines.

This approach has many pros:

  * there's no need to define Jenkins_ jobs manually anymore.
  * it's really simple to move from one Jenkins_ server to an another.
  * kirk permits to build Jenkins_ jobs for a particular user with the ``run --user``
    command, which create a Jenkins_ folder, where user can build jobs without
    affecting other users jobs.
  * kirk has its own user called **owner**, who's the one enabled to
    create/build jobs. This is **crucial**, because with this system it's
    possible to restrict the users privileges, avoiding jobs updates or bad
    maintainance.
  * project files are Yaml files supporting **environmental variables**. This
    makes really easy to integrate kirk with automation systems.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
