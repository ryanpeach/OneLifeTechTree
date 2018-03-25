git fetch upstream
git merge upstream/master
python3 batch_generate.py
git add -A
git commit -m "New Version"
git push
