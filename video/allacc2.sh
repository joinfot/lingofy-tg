#!/bin/bash
# Собирает всю партию. По три ролика разом — больше упирается в память.
cd /home/claude
export BATCH=${BATCH:-accdata3}
KEYS=$(python3 -c "
import importlib,os
D=importlib.import_module(os.environ['BATCH'])
print(' '.join(v['key'] for v in D.V))")
i=0
for K in $KEYS; do
  bash runacc2.sh "$K" &
  i=$((i+1))
  [ $((i % 3)) -eq 0 ] && wait
done
wait
echo "— партия собрана —"
ls -la /mnt/user-data/outputs/ | grep -E "$(echo $KEYS | tr ' ' '|')" | wc -l
