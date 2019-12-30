.. _Jenkins: https://jenkins.io/
.. _Jenkinsfile: https://jenkins.io/doc/book/pipeline/jenkinsfile/

==================
kirk documentation
==================

Kirk will push Jenkins_ into a professional environment, focusing more on
productivity rather than maintanance, helping to test source code modifications
before commit.

In the following example, Kirk will create and build a Jenkins_ job, according
with the project file, without the need to create it by hand.

.. note::
  Keep in mind that kirk is based on Jenkinsfile_ (also called 'groovy pipelines').

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

To execute ``fullbuild`` job with latest modifications on ``development``
branch:

.. parsed-literal::

    > kirk run myproject::fullbuild --change-id development

    kirk |version| session started

    owner: kirk
    rootdir: /home/sawk/kirk
    projects: projects
    credentials: credentials.cfg

    collected 5 jobs

    selected jobs
    myproject::fullbuild

    -> running myproject::fullbuild (user='')
    -> configured http://localhost:8080/job/MY_PROJECT/job/fullbuild/2/


Please take a look at this project and, if you are interested, let me know how
it can be improved.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
