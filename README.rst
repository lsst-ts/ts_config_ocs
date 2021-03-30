Configuration files for high-level LSST observatory control system CSCs

CSCs that are used for the entire observatory or are common to the Main and Auxiliary Telescopes (including configuration).

This code uses ``pre-commit`` to check yaml file syntax, maintain ``black`` formatting, and check ``flake8`` compliance.
To enable this, run the following commands once (the first removes the previous pre-commit hook)::

    git config --unset-all core.hooksPath
    pre-commit install
