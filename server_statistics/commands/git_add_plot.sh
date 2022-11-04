echo "start git sh script. date:"
now=$(date)
echo "$now"


cd /home/pi/work/projects/api_transport/server_statistics/
python3 analysis.py

git config --global user.email "ident_green@posteo.de"
git config --global user.name "ixFelix"

git add plots/time_series*.png
git commit -m "auto add png"
sleep 30s
echo "push the script to github"
git push
echo "end of git sh script."
