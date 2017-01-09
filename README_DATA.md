Several experiments were carried out with data sets from the shared task on MT quality estimation (QE) at the 2013, 2014 and 2016 editions of the Workshop on Statistical Machine Translation (WMT). Each data set consists of:
*  a set of source language segments;
* the corresponding raw translation produced by an unknown MT system, in some data sets not even the same system;
* an independent reference translations for every source segment, unrelated to the MT system being studied;
* the postedited version of the MT output; and
* the corresponding PE time in seconds.

Statistics of the corpora are provided in the following table:



| translation direction | training instances | test instances | mean source segment length | mean target segment length |
|-----------------------|--------------------|----------------|----------------------------|----------------------------|
| en --> es             | 803                | 284            | 24                         | 28                         |
| en --> es             | 650                | 208            | 22                         | 24                         |

The data sets were obtained from the data sets distributed as part of the shared task on MT QE for WMT'13 and WMT'14 (Bojar et al., 2013; Bojar et al., 2014), respectively. These data sets did not provide independent or PE references. Independent references were collected from the parallel data distributed for the shared MT task at the 2012 edition of WMT [http://www.statmt.org/wmt12/training-parallel.tgz]. PE references were provided by the shared-task organizers.

*Thanks to Prof. Lucia Specia for providing unavailable data.
