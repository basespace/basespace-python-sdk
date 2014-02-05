This document is to help SDK developers update the BaseSpacePy documentation.

The documentation was auto-generated with sphinx version 1.1.3 (for BaseSpacePy 0.1.3). See http://sphinx-doc.org/.

To update the docs, install sphinx with:
apt-get install python-sphinx
apt-get install texlive-latex-base
apt-get install texlive-latex-recommended
apt-get install texlive-latex-extra
apt-get install texlive-fontx-recommended

Then edit 'Available Modules.txt' to add links to new modules, if needed. Since sphinx uses docstrings for its content, make sure that newly added classes/methods have properly written docstrings.

To generate new html (in ../html, run:
make html
(you may wish to delete the newly created directory ../doctrees).

To generate new latex and pdfs (in ../latex), run:
make latex
make latexpdf

To remove existing docs run:
make clean
