ANNOTATED_DATA=/home/mlf/Escritorio/git-transit/gg/processed/
CODE=/home/mlf/Escritorio/git-transit/simpleqe/
ANNOTATOR=ann1

# Generate files from Carol's data

# code to factor
for ANNOTATOR in ann0 ann1 ann2 ann3 ann4
do
   printf "ANNOTATOR %s\n" $ANNOTATOR
   # TIME
   cat $ANNOTATED_DATA/dataset_$ANNOTATOR.filtered4 | awk 'BEGIN{FS="\t"} {print $7}' >/tmp/$ANNOTATOR.time
   # machine translated sentence
   cat $ANNOTATED_DATA/dataset_$ANNOTATOR.filtered4 | awk 'BEGIN{FS="\t"} {print $32}' >/tmp/$ANNOTATOR.sentences
   # reference TER
   cat $ANNOTATED_DATA/dataset_$ANNOTATOR.filtered4 | awk 'BEGIN{FS="\t"} {print "LABEL", NR, $38}' >/tmp/$ANNOTATOR.3ter
   printf "Reference TER:   " 
   python $CODE/ordering_merit_refactored.py --intensive /tmp/$ANNOTATOR.time /tmp/$ANNOTATOR.3ter /tmp/$ANNOTATOR.sentences | fgrep 'Q_simple(r,words)'| awk '{print $2}'
   # reference BLEU, reversed
   cat $ANNOTATED_DATA/dataset_$ANNOTATOR.filtered4 | awk 'BEGIN{FS="\t"} {print "LABEL", NR, -$39}' >/tmp/$ANNOTATOR.3bleui
   printf "Reference BLEU:  "   
   python $CODE/ordering_merit_refactored.py --intensive /tmp/$ANNOTATOR.time /tmp/$ANNOTATOR.3bleui /tmp/$ANNOTATOR.sentences | fgrep 'Q_simple(r,words)'| awk '{print $2}'
   # DIRECT ASSESSMENT, reversed
   printf "Direct assess.:  "
   cat $ANNOTATED_DATA/dataset_$ANNOTATOR.filtered4 | awk 'BEGIN{FS="\t"} {print "LABEL", NR, -$34}' >/tmp/$ANNOTATOR.3dai
   python $CODE/ordering_merit_refactored.py --intensive /tmp/$ANNOTATOR.time /tmp/$ANNOTATOR.3dai /tmp/$ANNOTATOR.sentences | fgrep 'Q_simple(r,words)'| awk '{print $2}'
   # HTER
   printf "Postedited TER:  "
   cat $ANNOTATED_DATA/dataset_$ANNOTATOR.filtered4 | awk 'BEGIN{FS="\t"} {print "LABEL", NR, $35}' >/tmp/$ANNOTATOR.3hter
   python $CODE/ordering_merit_refactored.py --intensive /tmp/$ANNOTATOR.time /tmp/$ANNOTATOR.3hter /tmp/$ANNOTATOR.sentences | fgrep 'Q_simple(r,words)'| awk '{print $2}'
   # HBLEU,reversed
   printf "Postedited BLEU: "
   cat $ANNOTATED_DATA/dataset_$ANNOTATOR.filtered4 | awk 'BEGIN{FS="\t"} {print "LABEL", NR, -$36}' >/tmp/$ANNOTATOR.3hbleui
   python $CODE/ordering_merit_refactored.py --intensive /tmp/$ANNOTATOR.time /tmp/$ANNOTATOR.3hbleui /tmp/$ANNOTATOR.sentences | fgrep 'Q_simple(r,words)'| awk '{print $2}'
   # use the actual time/mlen
   printf "Oracle1:         "   
   cat $ANNOTATED_DATA/dataset_$ANNOTATOR.filtered4 | awk 'BEGIN{FS="\t"} {print "LABEL", NR, $8}' >/tmp/$ANNOTATOR.3tau
   python $CODE/ordering_merit_refactored.py --intensive /tmp/$ANNOTATOR.time /tmp/$ANNOTATOR.3tau /tmp/$ANNOTATOR.sentences | fgrep 'Q_simple(r,words)'| awk '{print $2}'
   printf "Oracle2:         "
   python $CODE/ordering_merit_refactored.py --intensive /tmp/$ANNOTATOR.time /tmp/$ANNOTATOR.3tau /tmp/$ANNOTATOR.sentences | fgrep 'Q_simple(opt,words)'| awk '{print $2}'
   # clean up
   rm /tmp/$ANNOTATOR*

done


