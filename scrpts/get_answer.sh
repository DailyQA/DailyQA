set -x
current_path=$(pwd)
export PYTHONPATH=$PYTHONPATH:$current_path


search_dates=(250104 250105 250106 250107 250108 250109 250110) #250111

#可以任意选择日期，获得对应日期的答案
for sd in ${search_dates[@]}
do
    python run/get_answer.py --query_name query_checked_classified --qa_name qa_${sd} --search_day ${sd}
done
