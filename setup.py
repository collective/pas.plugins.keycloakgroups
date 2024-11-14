"""Installer for the pas.plugins.keycloakgroups package."""

from pathlib import Path
from setuptools import find_packages
from setuptools import setup


long_description = f"""
{Path("README.md").read_text()}\n
{Path("CONTRIBUTORS.md").read_text()}\n
{Path("CHANGES.md").read_text()}\n
"""


setup(
    name="pas.plugins.keycloakgroups",
    version="1.0.0b2.dev0",
    description="Use groups from Keycloak inside Plone portals.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS Keycloak Authentication Zope",
    author="Érico Andrei",
    author_email="ericof@plone.org",
    url="https://github.com/collective/pas.plugins.keycloakgroups",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/pas.plugins.keycloakgroups",
        "Source": "https://github.com/collective/pas.plugins.keycloakgroups",
        "Issue Tracker": "https://github.com/collective/pas.plugins.keycloakgroups/issues",
        "Documentation": "https://collective.github.io/pas.plugins.keycloakgroups",
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["pas", "pas.plugins"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "Plone",
        "plone.api",
        "plone.restapi",
        "python-keycloak",
    ],
    extras_require={
        "test": [
            "zest.releaser[recommended]",
            "zestreleaser.towncrier",
            "plone.app.testing",
            "plone.testing",
            "plone.restapi[test]",
            "pytest",
            "pytest-cov",
            "pytest-plone>=0.5.0",
            "pytest-docker",
            "pas.plugins.oidc>=2.0.0a1",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
