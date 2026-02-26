# Rosetta stone DB (prototype)
This is a prototype of the Rosetta stone database for mathematical objects. Its
purpose is to store mathematical objects and their descriptions in different
mathematical software, to enable developers to deserialize such data in the
future. Furthermore it can be used to facilitate interoperability between
different mathematical softwares. As an added benefit, this database can be
used to showcase the serialization capabilities of mathematical software.


## Structure
At the top level there are folders
- **description** Containing a description of the examples
- **PROGRAM** Containing the examples for the given `PROGRAM`. Note that not
  every example will be available in every program.

An `example` from the folder `description` will then correspond to a folder
`PROGRAM/example` where you will find
- Code for producing this example in `PROGRAM` in `PROGRAM/example/generate.*`
- The example serialized by `PROGRAM` in `PROGRAM/example/data.*`
- Code for verifying the example by `PROGRAM` in `PROGRAM/example/check.*`
- A link for a MaPS runtime in `PROGRAM/example/maps` that contains the version
  of `PROGRAM` necessary to read the data or run the scripts. At the same time
  this script showcases how to read the data using `PROGRAM`.

Note that not all files will be available for all examples. Not all software
provides (de-)serialization. Proprietary software is not available in MaPS
runtimes. And not all data makes sense for all software, for example, almost
all mathematical software will have matrices implemented, but not every
mathematical software will have groups or number fields.

In case this structure is chosen differently for any reason, the corresponding
folder will come with a `README.md` file containing a detailed explanation.


## Guidelines for suitable entries
### Choose unique data entries
To uniquely map entries to each other between different data types, the entries
themselves should be unique and large enough, such that automated searching for
these becomes easy. For example, one digit numbers will often appear multiple
times, even in the metadata.

### Break symmetries
Take for example matrices. The worst example would be a quadratic zero matrix,
since in the data one would be unable to tell rows from columns and the entries
from each other. Instead choose a non-zero non-quadratic matrix.
