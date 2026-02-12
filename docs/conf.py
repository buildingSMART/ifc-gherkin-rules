# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'buildingSMART Validation Service'
copyright = '2026, buildingSMART International'
author = 'buildingSMART International'
release = '0.8.4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.extlinks',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_favicon = '_static/favicon.ico'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

myst_links_external_new_tab = True

# -- Custom role for github links -------------------------------------------------
from docutils import nodes
from docutils.parsers.rst import roles

GITHUB_BASE = "https://github.com/buildingSMART/ifc-gherkin-rules"

def commit_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    sha = text.strip()
    url = f"{GITHUB_BASE}/commit/{sha}"
    node = nodes.reference(rawtext, sha[:8], refuri=url, **options)
    return [node], []

roles.register_local_role("commit", commit_role)

def tag_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    tag = text.strip()
    url = f"{GITHUB_BASE}/releases/tag/{tag}"
    node = nodes.reference(rawtext, tag, refuri=url, **options)
    return [node], []


roles.register_local_role("tag", tag_role)
