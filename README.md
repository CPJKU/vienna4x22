# Vienna 4x22 Piano Corpus -- Match, MusicXML, and PDF files

This repository contains the version 1.0.0 match files of the [Vienna 4x22 Piano Corpus](http://dx.doi.org/10.21939/4X22) as well as MusicXML and PDF files of the corresponding scores.

This repository was initially created for the Tutorial on Expressive Modeling of Music Performance presented at ISMIR 2019. Changes to the original data are specified in the [CHANGES.md](./CHANGES.md). The main differences of the data in this repository and the ones in the original repository involve mostly updating the version of the match files to the new version 1.0.0 and adding symbolic scores.

The `id` attributes of the `note` elements in the MusicXML files corresponds to the `Anchor` fields in the `snote` elements in the match files.

## Contents

This dataset includes 22 performances by professional pianists of 4 classical music excerpts.

1. Chopin, op. 38, measures 1-46
2. Chopin, op. 10, measures 1-22
3. Schubert, D783, 1st movement, measures 1-33
4. Mozart, K331, 1st movement, measures 1-36

## Quick Start

To use the dataset in python we recommend the [partitura package](github.com/CPJKU/partitura).
The current version of the match files is supported by partitura versions >=1.2.0

## Referencing this work

The dataset was collected and compiled by [Werner Goebl](https://iwk.mdw.ac.at/goebl/). If you use this work please cite.



```bibtex
@ELECTRONIC{vienna4x22,
  author = {Goebl, Werner},
  year = {1999},
  title = {The Vienna 4x22 Piano Corpus},
  language = {English},
  howpublished = {\url=http://dx.doi.org/10.21939/4X22},
  doi = {10.21939/4X22},
  owner = {mdw},
  timestamp = {2017.01.31}
}
```

## LICENSE

The files are distributed under the [CC BY 4.0 License](https://creativecommons.org/licenses/by/4.0/)