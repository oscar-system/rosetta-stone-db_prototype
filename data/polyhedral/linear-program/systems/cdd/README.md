Note that `cdd` is not an interactive program that serializes data. Instead it
reads data in its own format and transforms it according to commands provided
with the data.

The call to solve this linear program is
```
scdd data.ine
```
which will produce a file `data.lps` containing the solution.
