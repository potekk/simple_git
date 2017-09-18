# simple_git

Simple git is a repository managing tool.
 
## Instalation
pip install simple_git
 
## Commands

* sgit init
* sgit add [files]+
* sgit commit
* sgit status


## Data layer

### Commit node structure
Commit node is a JSON which stores the information of:
* parent: filename to the parent node or null if not exists (eg. root node)
* files_meta - map from filename -> meta, meta are:
  * fobj_filename: filename where the gzip compressed files are stored
  * hash: hash of the tracked file
  * filename: orginal filename

### The .sgit directory structure

- .sgit/HEAD
  - the file stores to filepath to the last commit node
- .sgit/STAG
  - the file is JSON where the staging file index is stored
- .sgit/objects/files
  - directory where gzip compressed files are stored
- .sgit/object/tree
  - directory where commit nodes are stored
- .sgit/object/tree/root node
  - root of the commit node


