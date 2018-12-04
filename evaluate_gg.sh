if [ ! -d "gg" ]; then
  git clone https://gitlab.com/mlforcada/gg.git
fi

for f in $(ls gg/processed/dataset_ann?.filtered4); do
  echo "====================================== $f ======================================"
  ref=$(mktemp /tmp/ref.XXXX);
  pred=$(mktemp /tmp/prediction.XXXX);
  source=$(mktemp /tmp/source.XXXX);
  cut -f 8 $f > $ref;
  cut -f 1,10,34 $f | grep -n "." | sed 's/\([0-9]*\):/\1\t/g' | awk 'begin {fs=ofs="\t"} {print $2 "\t" $1 "\t" $4 "\t" $3}'  > $pred;
  cut -f 30 $f > $source;
  echo "************************************** DA **************************************"
  python ordering_merit_refactored.py $ref $pred $source;


  cut -f 1,10,35 $f | grep -n "." | sed 's/\([0-9]*\):/\1\t/g' | awk 'begin {fs=ofs="\t"} {print $2 "\t" $1 "\t" $4 "\t" $3}'  > $pred;
  echo "************************************** HTER **************************************"
  python ordering_merit_refactored.py $ref $pred $source;

  cut -f 1,10,36 $f | grep -n "." | sed 's/\([0-9]*\):/\1\t/g' | awk 'begin {fs=ofs="\t"} {print $2 "\t" $1 "\t" $4 "\t" $3}'  > $pred;
  echo "************************************** HBLEU **************************************"
  python ordering_merit_refactored.py $ref $pred $source;

  cut -f 1,10,37 $f | grep -n "." | sed 's/\([0-9]*\):/\1\t/g' | awk 'begin {fs=ofs="\t"} {print $2 "\t" $1 "\t" $4 "\t" $3}'  > $pred;
  echo "************************************** HMETEOR **************************************"
  python ordering_merit_refactored.py $ref $pred $source;

  cut -f 1,10,24 $f | grep -n "." | sed 's/\([0-9]*\):/\1\t/g' | awk 'begin {fs=ofs="\t"} {print $2 "\t" $1 "\t" $4 "\t" $3}'  > $pred;
  echo "************************************** KEYSTROKES **************************************"
  python ordering_merit_refactored.py $ref $pred $source;


  rm $ref $source $pred;
done
