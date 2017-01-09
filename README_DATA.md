Several experiments were carried out with data sets from the shared task on MT quality estimation (QE) at the 2013, 2014 and 2016 editions of the Workshop on Statistical Machine Translation (WMT). Each data set consists of:
(a) a set of source language segments;
(b) the corresponding raw translation produced by an unknown MT system, in some data sets not even the same system;
(c) an independent reference translations for every source segment, unrelated to the MT system being studied;
(d) the postedited version of the MT output; and
(e) the corresponding PE time in seconds.
Statistics of the corpora are provided in the following table:

       | translation     training         test       mean segment length
       |   direction    instances    instances    source lang.   target lang.
-------+-------------------------------------------------------------------
WMT'13 |      en→es          803          284             24             28
WMT'14 |      en→es          650          208             22             24
WMT'16 |      de→en       13,000        2,000             17             18

Two of the data sets are for translation from English into Spanish (en→es) and were obtained from the data sets distributed as part of the shared task on MT QE for WMT'13 and WMT'14 (Bojar et al., 2013; Bojar et al., 2014), respectively. These data sets did not provide independent or PE references. Independent references were collected from the parallel data distributed for the shared MT task at the 2012 edition of WMT [http://www.statmt.org/wmt12/training-parallel.tgz]. PE references were provided by the shared-task organizers.*

The third data set focus is for English–German (en→de) translation and corresponds to WMT'16 MT QE shared task (Bojar et al., 2016). References and PE time were not publicly available and were provided by the organizers of the task.* In all the experiments, the training–test division is the same performed for the corresponding WMT shared tasks. WMT'16 also provides development data, which was added to the training corpus.

Each dataset is organised in a different directory. Each directory contains two sub-directories: one for the training data, and one for the test data.

*Thanks to Prof. Lucia Specia for providing unavailable data.
