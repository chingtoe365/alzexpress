export PYTHONPATH=~/rebeccanomics:~/rebeccanomics/refinement

export LC_ALL=C

export EDITOR=nano

alias update_rn="cd ~/rebeccanomics && git pull -u && sudo service apache2 restart"

. /usr/share/virtualenvwrapper/virtualenvwrapper.sh
workon refinement
cd rebeccanomics/refinement
