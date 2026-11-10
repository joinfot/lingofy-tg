#!/bin/bash
# Собирает всю партию. По три ролика разом — больше упирается в память.
cd /home/claude
export BATCH=${BATCH:-accdata4}
export FMTS=${FMTS:-fmts2}
KEYS=$(python3 -c "
import importlib,os
D=importlib.import_module(os.environ['BATCH'])
print(' '.join(v['key'] for v in D.V))")
i=0
FAIL=""
for K in $KEYS; do
  ( bash runacc2.sh "$K" || echo "УПАЛ $K" ) &
  i=$((i+1))
  [ $((i % 3)) -eq 0 ] && wait
done
wait

# Три параллельных рендера иногда дают битый кадр, и ролик выходит
# обрезанным. По одному то же самое собирается чисто, поэтому упавшие
# просто повторяются без параллели — это дешевле, чем гонять всю партию
# последовательно.
for K in $KEYS; do
  T=$(python3 -c "
import importlib, os
fmts=importlib.import_module(os.environ['FMTS'])
D=importlib.import_module(os.environ['BATCH'])
ph,sl,T=fmts.build(D.cfg('$K')); print(f'{T:.2f}')")
  G=$(ffprobe -v error -show_entries format=duration -of csv=p=0 \
    "/mnt/user-data/outputs/$K.mp4" 2>/dev/null || echo 0)
  OK=$(python3 -c "print(1 if abs($G - $T) <= 0.25 else 0)")
  [ "$OK" = "1" ] || FAIL="$FAIL $K"
done

if [ -n "$FAIL" ]; then
  echo "— перебираю по одному:$FAIL —"
  for K in $FAIL; do bash runacc2.sh "$K" || echo "УПАЛ СНОВА $K"; done
fi
echo "— партия собрана —"
ls -la /mnt/user-data/outputs/ | grep -E "$(echo $KEYS | tr ' ' '|')" | wc -l
