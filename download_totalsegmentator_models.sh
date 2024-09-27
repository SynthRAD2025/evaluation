mkdir -p .totalsegmentator/nnunet/results
wget --directory-prefix=.totalsegmentator/nnunet/results https://github.com/wasserth/TotalSegmentator/releases/download/v2.0.0-weights/Dataset297_TotalSegmentator_total_3mm_1559subj.zip
wget --directory-prefix=.totalsegmentator/nnunet/results https://github.com/wasserth/TotalSegmentator/releases/download/v2.0.0-weights/Dataset295_TotalSegmentator_part5_ribs_1559subj.zip
wget --directory-prefix=.totalsegmentator/nnunet/results https://github.com/wasserth/TotalSegmentator/releases/download/v2.0.0-weights/Dataset294_TotalSegmentator_part4_muscles_1559subj.zip
wget --directory-prefix=.totalsegmentator/nnunet/results https://github.com/wasserth/TotalSegmentator/releases/download/v2.0.0-weights/Dataset293_TotalSegmentator_part3_cardiac_1559subj.zip
wget --directory-prefix=.totalsegmentator/nnunet/results https://github.com/wasserth/TotalSegmentator/releases/download/v2.0.0-weights/Dataset292_TotalSegmentator_part2_vertebrae_1532subj.zip
wget --directory-prefix=.totalsegmentator/nnunet/results https://github.com/wasserth/TotalSegmentator/releases/download/v2.0.0-weights/Dataset291_TotalSegmentator_part1_organs_1559subj.zip

original_dir=$(pwd)

cd .totalsegmentator/nnunet/results
for zipfile in *.zip; do
    unzip "$zipfile"
done
cd "$original_dir"
