cd repos
for ITEM in $(cat ../interesting_repos.json | jq -r '.[].ssh_url')
do
  git clone $ITEM
done

for DIR in $(ls -1d */ | sed 's/\/$//')
do
  du -sh $DIR >> ../interesting_sizes.txt
  echo $DIR >> ../interesting_locs.txt
  echo $DIR >> ../interesting_locs.csv
  scc --no-cocomo $DIR >> ../interesting_locs.txt
  scc --no-cocomo --format=csv $DIR >> ../interesting_locs.csv
done
