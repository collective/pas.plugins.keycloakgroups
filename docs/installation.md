(index-label)=

# Installation

**This package supports sites running Plone version 6.0 and above.**

Add **pas.plugins.keycloakgroups** to the Plone installation using `pip`:

```bash
pip install pas.plugins.keycloakgroups
```

## Load the package

To make this package available to a Plone installation, you need to load its ZCML configuration.

If your project has a Python package with custom code, add the following line to your package's `dependencies.zcml` or `configure.zcml`:

```xml
   <include package="pas.plugins.keycloakgroups" />
```

An alternative to that is to use the `instance.yaml` configuration file provided by [`cookiecutter-zope-instance`](https://github.com/plone/cookiecutter-zope-instance).

Look for the `zcml_package_includes` configuration and add this package to the list of packages already listed there:

```yaml
   zcml_package_includes: ['my.package', 'pas.plugins.keycloakgroups']
```
